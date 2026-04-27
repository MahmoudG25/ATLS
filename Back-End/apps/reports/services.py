from decimal import Decimal

from django.db.models import Avg, Count, DecimalField, ExpressionWrapper, F, Sum
from django.db.models.functions import Coalesce

from apps.reports.models import DailyTaskReport, LaborEntry
from apps.reports.selectors import kpi_metrics, tenant_reports, operations_over_time, worker_usage


def cost_analytics(company):
    cost_expr = ExpressionWrapper(
        (F("hours") + F("overtime")) * F("worker_rate"),
        output_field=DecimalField(max_digits=14, decimal_places=2),
    )
    labor = LaborEntry.objects.for_company(company)
    return {
        "per_operation": list(
            labor.values("report__operation__name")
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
            labor.values("report__farm__name")
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
        tenant_reports(company)
        .values("operation__name")
        .annotate(
            output=Coalesce(Sum("actual_productivity"), 0),
            workers=Coalesce(Sum("company_workers") + Sum("contractor_workers"), 0),
        )
        .annotate(productivity=ExpressionWrapper(F("output") / Coalesce(F("workers"), 1), output_field=DecimalField(max_digits=10, decimal_places=2)))
        .order_by("-productivity")
    )


def comparison_analytics(company):
    data = tenant_reports(company).aggregate(
        contractor=Avg("contractor_workers"),
        company_avg=Avg("company_workers"),
    )
    return {
        "contractor": round(float(data.get("contractor") or 0), 2),
        "company": round(float(data.get("company_avg") or 0), 2),
    }


def smart_alerts(company):
    reports = tenant_reports(company)
    low_prod = reports.filter(actual_productivity__lt=10).count()
    cost_expr = ExpressionWrapper(
        (F("hours") + F("overtime")) * F("worker_rate"),
        output_field=DecimalField(max_digits=14, decimal_places=2),
    )
    high_cost_reports = (
        LaborEntry.objects.for_company(company)
        .values("report")
        .annotate(entries=Count("id"), total=Sum(cost_expr))
        .filter(total__gt=5000)
        .count()
    )
    alerts = []
    if low_prod:
        alerts.append({"type": "low_productivity", "count": low_prod, "message": "Low productivity detected."})
    if high_cost_reports:
        alerts.append({"type": "high_cost", "count": high_cost_reports, "message": "High report cost detected."})
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
