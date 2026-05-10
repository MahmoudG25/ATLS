from django.contrib import admin
from .models import HarvestReport, SortingReport, AnnualYield


@admin.register(HarvestReport)
class HarvestReportAdmin(admin.ModelAdmin):
    list_display = (
        "location",
        "season",
        "harvest_date",
        "variety",
        "quantity",
        "unit",
        "status",
        "is_partial",
    )
    list_filter = ("status", "season", "variety", "is_partial")
    search_fields = ("location__name", "notes")
    date_hierarchy = "harvest_date"


@admin.register(SortingReport)
class SortingReportAdmin(admin.ModelAdmin):
    list_display = (
        "harvest_report",
        "processing_date",
        "incoming_quantity",
        "final_quantity",
        "status",
    )
    list_filter = ("status", "quality_grade")
    date_hierarchy = "processing_date"


@admin.register(AnnualYield)
class AnnualYieldAdmin(admin.ModelAdmin):
    list_display = ("plot", "year", "production_amount")
