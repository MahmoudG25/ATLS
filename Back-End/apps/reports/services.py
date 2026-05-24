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
