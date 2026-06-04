from django.contrib import admin
from .models import (
    Operation,
    DailyTaskReport,
    OperationLog,
    Season,
    Variety,
    Unit,
    Contractor,
    LaborCategory,
    QualityGrade,
    SortingCategory,
    PackagingType,
    ProductivityClassification,
    FertilizationReport,
    IrrigationReport,
    CustomFieldDefinition,
    CustomFieldValue,
    OperationalLocationAllocation,
    IrrigationDetail,
    AppliedFertilizer,
    PestControlReport,
    AppliedPesticide,
)


@admin.register(CustomFieldDefinition)
class CustomFieldDefinitionAdmin(admin.ModelAdmin):
    list_display = ("name", "field_type", "is_required", "applies_to", "created_by")
    list_filter = ("field_type", "is_required", "applies_to")


@admin.register(CustomFieldValue)
class CustomFieldValueAdmin(admin.ModelAdmin):
    list_display = ("field", "value", "content_type", "object_id")
    list_filter = ("field", "content_type")


@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    list_display = ("name", "category")
    search_fields = ("name",)
    list_filter = ("category",)


@admin.register(DailyTaskReport)
class DailyTaskReportAdmin(admin.ModelAdmin):
    list_display = (
        "engineer",
        "report_date",
        "farm_name",
        "location",
        "variety",
        "operation",
        "actual_productivity",
    )

    list_filter = ("report_date", "location", "variety", "engineer", "operation")

    search_fields = (
        "engineer__username",
        "engineer__first_name",
        "engineer__last_name",
        "notes",
    )

    date_hierarchy = "report_date"

    def farm_name(self, obj):
        return obj.location.farm.name if obj.location else "-"

    farm_name.short_description = "Farm"


@admin.register(FertilizationReport)
class FertilizationReportAdmin(admin.ModelAdmin):
    list_display = (
        "report_date",
        "variety",
        "material_name",
        "active_percentage",
        "rate_per_feddan",
    )
    list_filter = ("report_date", "variety")
    search_fields = ("material_name", "operator")
    date_hierarchy = "report_date"


@admin.register(IrrigationReport)
class IrrigationReportAdmin(admin.ModelAdmin):
    list_display = (
        "date",
        "engineer",
        "is_fertilized",
        "total_shifts",
        "total_hours",
    )
    list_filter = ("date", "engineer", "is_fertilized")
    date_hierarchy = "date"


@admin.register(OperationalLocationAllocation)
class OperationalLocationAllocationAdmin(admin.ModelAdmin):
    list_display = ("content_type", "object_id", "enclosure", "productivity_value")
    list_filter = ("enclosure",)


@admin.register(IrrigationDetail)
class IrrigationDetailAdmin(admin.ModelAdmin):
    list_display = ("report", "phase", "shifts_count", "hours_per_shift")
    list_filter = ("phase",)


@admin.register(AppliedFertilizer)
class AppliedFertilizerAdmin(admin.ModelAdmin):
    list_display = ("irrigation_detail", "fertilizer_item", "custom_material_name", "quantity", "unit")


class AppliedPesticideInline(admin.TabularInline):
    model = AppliedPesticide
    extra = 1


@admin.register(AppliedPesticide)
class AppliedPesticideAdmin(admin.ModelAdmin):
    list_display = ("report", "pesticide_item", "custom_pesticide_name", "quantity", "rate_per_feddan")


@admin.register(PestControlReport)
class PestControlReportAdmin(admin.ModelAdmin):
    list_display = ("date", "engineer", "pesticide_item", "custom_pesticide_name", "quantity")
    list_filter = ("date", "engineer")
    date_hierarchy = "date"
    inlines = [AppliedPesticideInline]



@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date", "end_date", "status", "is_active")
    list_filter = ("status", "is_active")


@admin.register(Variety)
class VarietyAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "is_active")
    list_filter = ("company", "is_active")


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "is_active")
    list_filter = ("company", "is_active")


@admin.register(Contractor)
class ContractorAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "rate_per_hour", "is_active")
    list_filter = ("company", "is_active")


@admin.register(OperationLog)
class OperationLogAdmin(admin.ModelAdmin):
    list_display = ("operation", "location", "season", "source_type", "status", "created_at")
    list_filter = ("operation", "season", "source_type", "status")
    search_fields = ("location__name", "profile_data")


admin.site.register([LaborCategory, QualityGrade, SortingCategory, PackagingType, ProductivityClassification])
