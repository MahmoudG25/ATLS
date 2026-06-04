from decimal import Decimal

import jsonschema
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Avg, Count, DecimalField, ExpressionWrapper, F, Sum, Case, When, IntegerField
from django.db.models.functions import Coalesce, Cast

from apps.reports.models import DailyTaskReport, LaborEntry

def validate_operation_profile(operation, profile_data):
    """
    Validates profile_data against the Operation's json_schema using jsonschema.
    If no schema is defined, it passes (allowing legacy/unstructured data).
    """
    if not operation or not operation.json_schema:
        return
    
    try:
        jsonschema.validate(instance=profile_data, schema=operation.json_schema)
    except jsonschema.exceptions.ValidationError as e:
        # Re-raise as Django ValidationError
        raise DjangoValidationError(f"بيانات العملية '{operation.name}' غير صالحة: {e.message}")

from apps.reports.selectors import (
    kpi_metrics,
    tenant_operation_logs,
    operations_over_time,
    worker_usage,
)


def cost_analytics(company):
    cost_expr = ExpressionWrapper(
        (F("hours") + F("overtime")) * F("worker_rate"),
        output_field=DecimalField(max_digits=14, decimal_places=2),
    )
    labor = LaborEntry.objects.for_company(company)
    return {
        "per_operation": list(
            labor.values("operation_log__operation__name")
            .annotate(
                total_cost=Coalesce(
                    Sum(cost_expr),
                    Decimal("0.00"),
                    output_field=DecimalField(max_digits=14, decimal_places=2),
                )
            )
            .order_by("-total_cost")
        ),
        "per_farm": list(
            labor.values("operation_log__location__farm__name")
            .annotate(
                total_cost=Coalesce(
                    Sum(cost_expr),
                    Decimal("0.00"),
                    output_field=DecimalField(max_digits=14, decimal_places=2),
                )
            )
            .order_by("-total_cost")
        ),
        "per_contractor": list(
            labor.values("contractor__name")
            .annotate(
                total_cost=Coalesce(
                    Sum(cost_expr),
                    Decimal("0.00"),
                    output_field=DecimalField(max_digits=14, decimal_places=2),
                )
            )
            .order_by("-total_cost")
        ),
    }


def productivity_analytics(company):
    return list(
        tenant_operation_logs(company)
        .values("operation__name")
        .annotate(
            output=Coalesce(Sum("actual_productivity"), 0.0, output_field=DecimalField(max_digits=12, decimal_places=2)),
            workers=Coalesce(Sum("company_workers") + Sum("contractor_workers"), 0),
        )
        .annotate(
            productivity=ExpressionWrapper(
                F("output") / Cast(Case(When(workers=0, then=1), default=F("workers"), output_field=IntegerField()), output_field=DecimalField(max_digits=12, decimal_places=2)),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            )
        )
        .order_by("-productivity")
    )


def comparison_analytics(company):
    data = tenant_operation_logs(company).aggregate(
        contractor=Avg("contractor_workers"),
        company_avg=Avg("company_workers"),
    )
    return {
        "contractor": round(float(data.get("contractor") or 0), 2),
        "company": round(float(data.get("company_avg") or 0), 2),
    }


def smart_alerts(company):
    reports = tenant_operation_logs(company)
    low_prod = reports.filter(actual_productivity__lt=10).count()
    cost_expr = ExpressionWrapper(
        (F("hours") + F("overtime")) * F("worker_rate"),
        output_field=DecimalField(max_digits=14, decimal_places=2),
    )
    high_cost_reports = (
        LaborEntry.objects.for_company(company)
        .values("operation_log")
        .annotate(entries=Count("id"), total=Sum(cost_expr))
        .filter(total__gt=5000)
        .count()
    )
    alerts = []
    if low_prod:
        alerts.append(
            {
                "type": "low_productivity",
                "count": low_prod,
                "message": "Low productivity detected.",
            }
        )
    if high_cost_reports:
        alerts.append(
            {
                "type": "high_cost",
                "count": high_cost_reports,
                "message": "High report cost detected.",
            }
        )
    return alerts


def smart_suggestions(company):
    comparison = comparison_analytics(company)
    suggestions = []
    if comparison["contractor"] > comparison["company"] * 1.2:
        suggestions.append("Reduce contractor workers by 20% for similar tasks.")
    suggestions.append("Benchmark top contractor performance weekly.")
    return suggestions


def dashboard_bundle(company):
    return {
        "kpi": kpi_metrics(company),
        "operations_over_time": operations_over_time(company),
        "workers_usage": worker_usage(company),
        "costs": cost_analytics(company),
        "productivity": productivity_analytics(company),
    }


def sync_allocation_costs(allocation):
    """
    سير العمل لحساب التكلفة المالية تلقائياً بناءً على بيانات الـ HR والمقاولين
    """
    from apps.hr.models import Worker
    from apps.reports.models import Contractor, LaborEntry, OperationLog
    from django.contrib.contenttypes.models import ContentType
    
    company = allocation.company
    enclosure = allocation.enclosure
    
    # 1. تحديد معدل أجر عمال الشركة من الـ HR
    active_company_workers = Worker.objects.filter(company=company, worker_type='COMPANY', status='active')
    if active_company_workers.exists():
        company_hourly_rates = [w.hourly_rate for w in active_company_workers if w.hourly_rate > 0]
        company_rate = sum(company_hourly_rates) / len(company_hourly_rates) if company_hourly_rates else Decimal("15.00")
    else:
        company_rate = Decimal("15.00") # معدل افتراضي
        
    # 2. تحديد المقاول ومعدله
    contractor = allocation.contractor
    parent_report = allocation.content_object
    if not contractor and parent_report and hasattr(parent_report, 'contractor'):
        contractor = getattr(parent_report, 'contractor', None)
        
    rate = contractor.rate_per_hour if contractor else Decimal("15.00")
    contractor_workers = allocation.contractor_workers
    if not contractor_workers and parent_report and hasattr(parent_report, 'contractor_workers'):
        contractor_workers = getattr(parent_report, 'contractor_workers', 0)

    # 3. محاولة العثور على OperationLog المقابل لتسجيل تفاصيل العمالة تحته
    # يمكن أن يكون التقرير المرتبط هو DailyTaskReport أو IrrigationReport أو PestControlReport
    if not parent_report:
        return

    source_type = "IRRIGATION" if parent_report.__class__.__name__ == 'IrrigationReport' else "PEST_CONTROL"
    
    # البحث عن أو إنشاء سجل العملية للـ Enclosure المستهدف
    op_log = OperationLog.objects.filter(
        company=company,
        location=enclosure,
        source_type=source_type,
        source_id=str(parent_report.id)
    ).first()
    
    if not op_log and hasattr(parent_report, 'operation'):
        # للمهام اليومية
        op_log = OperationLog.objects.filter(
            company=company,
            location=enclosure,
            report=parent_report
        ).first()
        
    if not op_log:
        # إنشاء OperationLog تلقائي للموقع إذا لم يوجد
        from apps.reports.models import Operation, Season
        season = Season.objects.filter(company=company, status="OPEN").first()
        
        # تحديد العملية الفنية المناسبة
        op_name = "توزيع عمالة ميداني"
        if parent_report.__class__.__name__ == 'IrrigationReport':
            op_name = "تشغيل وصيانة الري بالتنقيط"
        elif parent_report.__class__.__name__ == 'PestControlReport':
            op_name = "رش وقائي ضد سوسة النخيل"
            
        operation, _ = Operation.objects.get_or_create(
            name=op_name,
            company=company,
            defaults={"category": "maintenance"}
        )
        
        op_log = OperationLog.objects.create(
            company=company,
            location=enclosure,
            operation=operation,
            season=season,
            source_type=source_type,
            source_id=str(parent_report.id),
            company_workers=allocation.allocated_workers_company,
            contractor_workers=contractor_workers,
            actual_productivity=allocation.productivity_value,
            work_hours=Decimal("8.0")
        )
    else:
        # تحديث أعداد العمالة والإنتاجية في الـ Log الحالي
        op_log.company_workers = allocation.allocated_workers_company
        op_log.contractor_workers = contractor_workers
        op_log.actual_productivity = allocation.productivity_value
        op_log.save()

    # 4. تنظيف قيود العمالة التلقائية القديمة لهذا الـ Log وإعادة بنائها
    LaborEntry.objects.filter(operation_log=op_log, note__icontains="تلقائي").delete()
    
    # حقن عمال الشركة
    for i in range(allocation.allocated_workers_company):
        LaborEntry.objects.create(
            company=company,
            operation_log=op_log,
            worker_name=f"عامل شركة تلقائي {i+1}",
            worker_type=LaborEntry.WORKER_TYPE_COMPANY,
            worker_rate=company_rate,
            hours=Decimal("8.0"),
            note="توزيع عمالة شركة تلقائي"
        )
        
    # حقن عمال المقاول
    if contractor_workers:
        for i in range(contractor_workers):
            LaborEntry.objects.create(
                company=company,
                operation_log=op_log,
                worker_name=f"عامل مقاول تلقائي {i+1}",
                worker_type=LaborEntry.WORKER_TYPE_CONTRACTOR,
                contractor=contractor,
                worker_rate=rate,
                hours=Decimal("8.0"),
                note="توزيع عمال مقاول تلقائي"
            )

