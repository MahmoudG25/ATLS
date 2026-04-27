from decimal import Decimal

from django.db.models import Avg, Count, DecimalField, ExpressionWrapper, F, IntegerField, Sum
from django.db.models.functions import Coalesce, TruncDate

from apps.reports.models import DailyTaskReport, LaborEntry


def tenant_reports(company):
    return (
        DailyTaskReport.objects.for_company(company)
        .select_related("operation", "farm", "engineer")
        .prefetch_related("labor_entries", "attachments")
    )


def operations_over_time(company):
    return list(
        tenant_reports(company)
        .annotate(day=TruncDate("report_date"))
        .values("day")
        .annotate(total=Count("id"))
        .order_by("day")
    )


def worker_usage(company):
    return list(
        tenant_reports(company)
        .values("operation__name")
        .annotate(
            company_workers=Coalesce(Sum("company_workers"), 0, output_field=IntegerField()),
            contractor_workers=Coalesce(Sum("contractor_workers"), 0, output_field=IntegerField()),
        )
        .order_by("-company_workers", "-contractor_workers")
    )


def kpi_metrics(company):
    reports = tenant_reports(company)
    labor = LaborEntry.objects.for_company(company)
    workers = reports.aggregate(
        company_workers=Coalesce(Sum("company_workers"), 0, output_field=IntegerField()),
        contractor_workers=Coalesce(Sum("contractor_workers"), 0, output_field=IntegerField()),
    )
    cost_expr = ExpressionWrapper(
        (F("hours") + F("overtime")) * F("worker_rate"),
        output_field=DecimalField(max_digits=14, decimal_places=2),
    )
    return {
        "total_operations": reports.aggregate(total=Count("operation", distinct=True))["total"] or 0,
        "total_workers": workers["company_workers"] + workers["contractor_workers"],
        "total_cost": labor.aggregate(
            total=Coalesce(
                Sum(cost_expr),
                Decimal("0.00"),
                output_field=DecimalField(max_digits=14, decimal_places=2),
            )
        )["total"],
        "avg_productivity": reports.aggregate(avg=Avg("actual_productivity"))["avg"] or 0,
    }
