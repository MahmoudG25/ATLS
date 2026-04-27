from decimal import Decimal

from django.db.models import Avg, Count, DecimalField, ExpressionWrapper, F, IntegerField, Sum, Max, Min
from django.db.models.functions import Coalesce, TruncDate

from apps.reports.models import DailyTaskReport, LaborEntry


def tenant_reports(company):
    return (
        DailyTaskReport.objects.for_company(company)
        .select_related("operation", "farm", "engineer", "location", "location__farm")
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
    reports = tenant_reports(company)
    
    if start_date:
        reports = reports.filter(report_date__gte=start_date)
    if end_date:
        reports = reports.filter(report_date__lte=end_date)
    
    total_reports = reports.count()
    
    worker_stats = reports.aggregate(
        total_company_workers=Coalesce(Sum("company_workers"), 0, output_field=IntegerField()),
        total_contractor_workers=Coalesce(Sum("contractor_workers"), 0, output_field=IntegerField()),
        avg_workers_per_report=Avg(
            F("company_workers") + F("contractor_workers"),
            output_field=IntegerField()
        ),
    )
    
    operation_stats = reports.aggregate(
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
                worker_stats["total_company_workers"] + 
                worker_stats["total_contractor_workers"]
            ),
            "company_workers": worker_stats["total_company_workers"],
            "contractor_workers": worker_stats["total_contractor_workers"],
            "avg_workers_per_report": worker_stats["avg_workers_per_report"] or 0,
        },
        "operations": {
            "total_unique_operations": operation_stats["unique_operations"] or 0,
            "total_operation_records": operation_stats["total_operations"],
            "avg_productivity": round(float(operation_stats["avg_productivity"] or 0), 2),
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
    reports = tenant_reports(company)
    
    if start_date:
        reports = reports.filter(report_date__gte=start_date)
    if end_date:
        reports = reports.filter(report_date__lte=end_date)
    
    # By operation
    by_operation = list(
        reports
        .values("operation__id", "operation__name")
        .annotate(
            total_productivity=Coalesce(Sum("actual_productivity"), 0, output_field=IntegerField()),
            avg_productivity=Coalesce(Avg("actual_productivity"), 0),
            count_reports=Count("id"),
            min_productivity=Min("actual_productivity"),
            max_productivity=Max("actual_productivity"),
        )
        .order_by("-total_productivity")
    )
    
    # By location
    by_location = list(
        reports
        .values("location__id", "location__name", "location__type")
        .annotate(
            total_productivity=Coalesce(Sum("actual_productivity"), 0, output_field=IntegerField()),
            avg_productivity=Coalesce(Avg("actual_productivity"), 0),
            count_reports=Count("id"),
        )
        .order_by("-total_productivity")
    )
    
    # By date
    by_date = list(
        reports
        .values("report_date")
        .annotate(
            total_productivity=Coalesce(Sum("actual_productivity"), 0, output_field=IntegerField()),
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
    reports = tenant_reports(company)
    
    if start_date:
        reports = reports.filter(report_date__gte=start_date)
    if end_date:
        reports = reports.filter(report_date__lte=end_date)
    
    operations_data = list(
        reports
        .values("operation__id", "operation__name", "operation__category")
        .annotate(
            total_reports=Count("id"),
            total_company_workers=Coalesce(Sum("company_workers"), 0, output_field=IntegerField()),
            total_contractor_workers=Coalesce(Sum("contractor_workers"), 0, output_field=IntegerField()),
            total_workers=F("total_company_workers") + F("total_contractor_workers"),
            total_work_hours=Coalesce(Sum("work_hours"), 0),
            avg_work_hours=Avg("work_hours"),
            total_productivity=Coalesce(Sum("actual_productivity"), 0, output_field=IntegerField()),
            avg_productivity=Avg("actual_productivity"),
            unique_engineers=Count("engineer", distinct=True),
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
    reports = tenant_reports(company)
    
    if start_date:
        reports = reports.filter(report_date__gte=start_date)
    if end_date:
        reports = reports.filter(report_date__lte=end_date)
    
    locations_data = list(
        reports
        .values("location__id", "location__name", "location__type", "location__farm__id", "location__farm__name")
        .annotate(
            total_company_workers=Coalesce(Sum("company_workers"), 0, output_field=IntegerField()),
            total_contractor_workers=Coalesce(Sum("contractor_workers"), 0, output_field=IntegerField()),
            total_workers=F("total_company_workers") + F("total_contractor_workers"),
            total_reports=Count("id"),
            unique_engineers=Count("engineer", distinct=True),
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
    reports = tenant_reports(company)
    
    if start_date:
        reports = reports.filter(report_date__gte=start_date)
    if end_date:
        reports = reports.filter(report_date__lte=end_date)
    
    matrix = list(
        reports
        .values(
            "operation__id", "operation__name",
            "location__id", "location__name", "location__type"
        )
        .annotate(
            total_workers=Coalesce(
                F("company_workers") + F("contractor_workers"),
                0,
                output_field=IntegerField()
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
