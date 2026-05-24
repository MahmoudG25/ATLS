from decimal import Decimal

from django.db.models import (
    Avg,
    Count,
    DecimalField,
    ExpressionWrapper,
    F,
    IntegerField,
    Sum,
    Max,
    Min,
    Q,
    Case,
    When,
)
from django.db.models.functions import Coalesce, TruncDate

from apps.reports.models import DailyTaskReport, LaborEntry, OperationLog


def tenant_operation_logs(company):
    """
    Phase 3: Source of truth for analytics is now OperationLog.
    """
    return (
        OperationLog.objects.for_company(company)
        .select_related("operation", "report", "report__engineer", "location", "location__farm")
    )


def tenant_reports(company):
    """Legacy container query, maintained for non-analytics endpoints"""
    return (
        DailyTaskReport.objects.for_company(company)
        .select_related("operation", "engineer", "location", "location__farm")
        .prefetch_related("labor_entries", "attachments")
    )


def operations_over_time(company):
    return list(
        tenant_operation_logs(company)
        .annotate(day=TruncDate(Coalesce("report__report_date", "created_at")))
        .values("day")
        .annotate(total=Count("id"))
        .order_by("day")
    )


def worker_usage(company):
    return list(
        tenant_operation_logs(company)
        .values("operation__name")
        .annotate(
            company_workers=Coalesce(
                Sum("company_workers"), 0, output_field=IntegerField()
            ),
            contractor_workers=Coalesce(
                Sum("contractor_workers"), 0, output_field=IntegerField()
            ),
        )
        .order_by("-company_workers", "-contractor_workers")
    )


def kpi_metrics(company):
    logs = tenant_operation_logs(company)
    labor = LaborEntry.objects.for_company(company)
    workers = logs.aggregate(
        company_workers=Coalesce(
            Sum("company_workers"), 0, output_field=IntegerField()
        ),
        contractor_workers=Coalesce(
            Sum("contractor_workers"), 0, output_field=IntegerField()
        ),
    )
    cost_expr = ExpressionWrapper(
        (F("hours") + F("overtime")) * F("worker_rate"),
        output_field=DecimalField(max_digits=14, decimal_places=2),
    )
    return {
        "total_operations": logs.aggregate(total=Count("operation", distinct=True))[
            "total"
        ]
        or 0,
        "total_workers": workers["company_workers"] + workers["contractor_workers"],
        "total_cost": labor.aggregate(
            total=Coalesce(
                Sum(cost_expr),
                Decimal("0.00"),
                output_field=DecimalField(max_digits=14, decimal_places=2),
            )
        )["total"],
        "avg_productivity": logs.aggregate(avg=Avg("actual_productivity"))["avg"]
        or 0,
    }


# ============================================================================
# ADVANCED ANALYTICS SELECTORS
# ============================================================================


def kpi_dashboard(company, start_date=None, end_date=None):
    """
    Comprehensive KPI metrics with date filtering.

    Computes:
    - Total workers (company + contractor)
    - Total operations
    - Average productivity per operation
    - Workers per location
    """
    logs = tenant_operation_logs(company)

    if start_date:
        logs = logs.filter(report__report_date__gte=start_date)
    if end_date:
        logs = logs.filter(report__report_date__lte=end_date)

    total_reports = logs.count()

    worker_stats = logs.aggregate(
        total_company_workers=Coalesce(
            Sum("company_workers"), 0, output_field=IntegerField()
        ),
        total_contractor_workers=Coalesce(
            Sum("contractor_workers"), 0, output_field=IntegerField()
        ),
        avg_workers_per_report=Avg(
            F("company_workers") + F("contractor_workers"), output_field=IntegerField()
        ),
    )

    operation_stats = logs.aggregate(
        unique_operations=Count("operation", distinct=True),
        total_operations=Count("id"),
        avg_productivity=Avg("actual_productivity"),
    )

    return {
        "period": {
            "start_date": start_date,
            "end_date": end_date,
        },
        "summary": {
            "total_reports": total_reports,
            "total_workers": (
                worker_stats["total_company_workers"]
                + worker_stats["total_contractor_workers"]
            ),
            "company_workers": worker_stats["total_company_workers"],
            "contractor_workers": worker_stats["total_contractor_workers"],
            "avg_workers_per_report": worker_stats["avg_workers_per_report"] or 0,
        },
        "operations": {
            "total_unique_operations": operation_stats["unique_operations"] or 0,
            "total_operation_records": operation_stats["total_operations"],
            "avg_productivity": round(
                float(operation_stats["avg_productivity"] or 0), 2
            ),
        },
    }


def productivity_analytics(company, start_date=None, end_date=None):
    """
    Productivity metrics grouped by operation, location, and date.

    Aggregations:
    - SUM(productivity), AVG(productivity), COUNT(reports)
    - GROUP BY operation, location, date
    - Sorted by productivity DESC
    """
    logs = tenant_operation_logs(company)

    if start_date:
        logs = logs.filter(report__report_date__gte=start_date)
    if end_date:
        logs = logs.filter(report__report_date__lte=end_date)

    # By operation
    by_operation = list(
        logs.values("operation__id", "operation__name")
        .annotate(
            total_productivity=Coalesce(
                Sum("actual_productivity"), 0, output_field=IntegerField()
            ),
            avg_productivity=Coalesce(Avg("actual_productivity"), 0),
            count_reports=Count("id"),
            min_productivity=Min("actual_productivity"),
            max_productivity=Max("actual_productivity"),
        )
        .order_by("-total_productivity")
    )

    # By location
    by_location = list(
        logs.values("location__id", "location__name", "location__type")
        .annotate(
            total_productivity=Coalesce(
                Sum("actual_productivity"), 0, output_field=IntegerField()
            ),
            avg_productivity=Coalesce(Avg("actual_productivity"), 0),
            count_reports=Count("id"),
        )
        .order_by("-total_productivity")
    )

    # By date
    by_date = list(
        logs.values(report_date=F("report__report_date"))
        .annotate(
            total_productivity=Coalesce(
                Sum("actual_productivity"), 0, output_field=IntegerField()
            ),
            avg_productivity=Coalesce(Avg("actual_productivity"), 0),
            count_reports=Count("id"),
        )
        .order_by("-report_date")
    )

    return {
        "by_operation": by_operation,
        "by_location": by_location,
        "by_date": by_date,
    }


def operations_summary(company, start_date=None, end_date=None):
    """
    Operations summary with detailed breakdown.

    Includes:
    - Workers per operation (company + contractor)
    - Work hours per operation
    - Reports count per operation
    - Location breakdown
    """
    logs = tenant_operation_logs(company)

    if start_date:
        logs = logs.filter(report__report_date__gte=start_date)
    if end_date:
        logs = logs.filter(report__report_date__lte=end_date)

    operations_data = list(
        logs.values("operation__id", "operation__name", "operation__category")
        .annotate(
            total_reports=Count("id"),
            total_company_workers=Coalesce(
                Sum("company_workers"), 0, output_field=IntegerField()
            ),
            total_contractor_workers=Coalesce(
                Sum("contractor_workers"), 0, output_field=IntegerField()
            ),
            total_workers=F("total_company_workers") + F("total_contractor_workers"),
            total_work_hours=Coalesce(Sum("work_hours"), 0),
            avg_work_hours=Avg("work_hours"),
            total_productivity=Coalesce(
                Sum("actual_productivity"), 0, output_field=IntegerField()
            ),
            avg_productivity=Avg("actual_productivity"),
            unique_engineers=Count("report__engineer", distinct=True),
            unique_locations=Count("location", distinct=True),
        )
        .order_by("-total_reports")
    )

    return {
        "total_operations": len(operations_data),
        "operations": operations_data,
    }


def workers_by_location(company, start_date=None, end_date=None):
    """
    Worker distribution grouped by location (LocationNode).

    Shows:
    - Total workers per location
    - Company vs contractor split
    - Reports count
    """
    logs = tenant_operation_logs(company)

    if start_date:
        logs = logs.filter(report__report_date__gte=start_date)
    if end_date:
        logs = logs.filter(report__report_date__lte=end_date)

    locations_data = list(
        logs.values(
            "location__id",
            "location__name",
            "location__type",
            "location__farm__id",
            "location__farm__name",
        )
        .annotate(
            total_company_workers=Coalesce(
                Sum("company_workers"), 0, output_field=IntegerField()
            ),
            total_contractor_workers=Coalesce(
                Sum("contractor_workers"), 0, output_field=IntegerField()
            ),
            total_workers=F("total_company_workers") + F("total_contractor_workers"),
            total_reports=Count("id"),
            unique_engineers=Count("report__engineer", distinct=True),
            unique_operations=Count("operation", distinct=True),
        )
        .order_by("-total_workers")
    )

    return {
        "total_locations": len(locations_data),
        "locations": locations_data,
    }


def operation_location_matrix(company, start_date=None, end_date=None):
    """
    Cross-tabulation of operations vs locations.

    Shows worker counts at intersection of operation x location.
    """
    logs = tenant_operation_logs(company)

    if start_date:
        logs = logs.filter(report__report_date__gte=start_date)
    if end_date:
        logs = logs.filter(report__report_date__lte=end_date)

    matrix = list(
        logs.values(
            "operation__id",
            "operation__name",
            "location__id",
            "location__name",
            "location__type",
        )
        .annotate(
            total_workers=Coalesce(
                F("company_workers") + F("contractor_workers"),
                0,
                output_field=IntegerField(),
            ),
            company_workers=Sum("company_workers"),
            contractor_workers=Sum("contractor_workers"),
            total_reports=Count("id"),
        )
        .order_by("operation__name", "-total_workers")
    )

    return {
        "matrix": matrix,
    }


# ─── Enclosure Profile Selectors ───────────────────────────────────────────


def get_location_timeline(location_node, profile_type=None, operation_id=None, search=None):
    """
    Returns a paginated-ready queryset of OperationLog records for a specific location.
    Optimized for the 'Enclosure Profile' timeline widget.
    """
    logs = OperationLog.objects.filter(
        location=location_node, 
        is_deleted=False
    ).select_related(
        "operation", "report", "report__engineer", "contractor", "unit", "variety", "location"
    ).prefetch_related("attachments", "labor_entries", "report__attachments")

    if profile_type:
        logs = logs.filter(profile_type=profile_type)
    
    if operation_id:
        logs = logs.filter(operation_id=operation_id)
        
    if search:
        logs = logs.filter(
            Q(operation__name__icontains=search) | 
            Q(report__engineer__first_name__icontains=search) |
            Q(report__engineer__last_name__icontains=search)
        )
        
    return logs.order_by("-report__report_date", "-created_at")

def get_location_full_timeline(location_node, limit=50):
    """
    Unified timeline combining OperationLog and HarvestReport.
    """
    from apps.production.models import HarvestReport
    from serializers.reports_serializers import OperationLogTimelineSerializer
    from serializers.production_serializers import HarvestReportSerializer
    
    logs = OperationLog.objects.filter(location=location_node, is_deleted=False).select_related(
        "operation", "report", "report__engineer"
    ).prefetch_related(
        "attachments", "labor_entries", "report__attachments"
    ).order_by("-report__report_date")[:limit]
    
    harvests = HarvestReport.objects.filter(location=location_node).order_by("-harvest_date")[:limit]
    
    # Merge and sort manually for the widget if needed, 
    # but for now we'll just keep the existing selectors.
    # Actually, the user wants 'productivity' to appear.
    return logs


def get_location_analytics(location_node):
    """
    Aggregated metrics for a specific LocationNode (Enclosure, Stage, or Sector).
    Uses recursive lookup to include all descendants.
    """
    # Use descendants to support Phase/Sector level analytics
    nodes = location_node.get_descendants(include_self=True)
    logs = OperationLog.objects.filter(location__in=nodes, is_deleted=False)
    
    # 1. Summary Metrics
    summary = logs.aggregate(
        total_ops=Coalesce(Count("id"), 0),
        total_hours=Coalesce(Sum("work_hours"), 0.0),
        total_productivity=Coalesce(Sum("actual_productivity"), 0.0),
        last_op_date=Max("report__report_date"),
        last_irrigation_date=Max("report__report_date", filter=Q(operation__category="irrigation") | Q(profile_type="irrigation")),
        last_fertilization_date=Max("report__report_date", filter=Q(operation__category="fertilization") | Q(profile_type="fertilization"))
    )

    # 2. Cost Distribution by Category
    cost_expr = ExpressionWrapper(
        (Coalesce(F("labor_entries__hours"), Decimal("0")) + Coalesce(F("labor_entries__overtime"), Decimal("0"))) * 
        Coalesce(F("labor_entries__worker_rate"), Decimal("0")),
        output_field=DecimalField(max_digits=14, decimal_places=2),
    )
    
    cost_trend = list(
        logs.annotate(period=TruncDate("report__report_date"))
        .values("period")
        .annotate(cost=Coalesce(Sum(cost_expr), Decimal("0")))
        .order_by("period")
    )
    
    # 3. Operation distribution
    distribution = list(
        logs.values(category=F("operation__category"))
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    
    # 4. Harvest Summary (Normalized to KG) - Recursive lookup
    from apps.production.models import HarvestReport
    harvest_sum = HarvestReport.objects.filter(
        location__in=nodes, 
        status__in=['SUBMITTED', 'APPROVED', 'FINALIZED']
    ).annotate(
        qty_kg=Case(
            When(unit__name__icontains='طن', then=F('quantity') * 1000),
            When(unit__name__icontains='ton', then=F('quantity') * 1000),
            default=F('quantity'),
            output_field=DecimalField()
        )
    ).aggregate(total=Sum('qty_kg'))['total'] or 0.0

    return {
        "summary": {
            **summary,
            "total_harvested_kg": float(harvest_sum)
        },
        "cost_trend": cost_trend,
        "operation_distribution": distribution
    }
