from django.contrib import admin
from .models import Operation, DailyTaskReport, FertilizationReport, IrrigationReport, CustomFieldDefinition, CustomFieldValue

@admin.register(CustomFieldDefinition)
class CustomFieldDefinitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'field_type', 'is_required', 'applies_to', 'created_by')
    list_filter = ('field_type', 'is_required', 'applies_to')

@admin.register(CustomFieldValue)
class CustomFieldValueAdmin(admin.ModelAdmin):
    list_display = ('field', 'value', 'content_type', 'object_id')
    list_filter = ('field', 'content_type')

@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    search_fields = ('name',)
    list_filter = ('category',)

@admin.register(DailyTaskReport)
class DailyTaskReportAdmin(admin.ModelAdmin):
    list_display = ('engineer', 'report_date', 'sector', 'variety', 'operation', 'actual_productivity')
    list_filter = ('report_date', 'sector', 'variety', 'engineer', 'operation')
    search_fields = ('engineer__username', 'engineer__first_name', 'engineer__last_name', 'notes')
    date_hierarchy = 'report_date'

@admin.register(FertilizationReport)
class FertilizationReportAdmin(admin.ModelAdmin):
    list_display = ('report_date', 'variety', 'material_name', 'active_percentage', 'rate_per_feddan')
    list_filter = ('report_date', 'variety')
    search_fields = ('material_name', 'operator')
    date_hierarchy = 'report_date'

@admin.register(IrrigationReport)
class IrrigationReportAdmin(admin.ModelAdmin):
    list_display = ('report_date', 'sector_number', 'transfer_number', 'area_feddan', 'irrigation_hours')
    list_filter = ('report_date', 'sector_number')
    date_hierarchy = 'report_date'
