from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class Operation(models.Model):
    """قائمة العمليات الفنية الثابتة"""
    name = models.CharField(max_length=200, unique=True)
    category = models.CharField(max_length=50, choices=[
        ('harvest',      'حصاد'),
        ('planting',     'زراعة'),
        ('maintenance',  'صيانة'),
        ('pest_control', 'مكافحة'),
        ('transport',    'نقل وتحميل'),
        ('other',        'أخرى'),
    ])

    class Meta:
        verbose_name = "عملية فنية"
        verbose_name_plural = "العمليات الفنية"

    def __str__(self):
        return self.name

class ReportDropdownOption(models.Model):
    CATEGORY_CHOICES = [
        ('variety', 'Variety'),
        ('unit', 'Unit'),
        ('contractor', 'Contractor'),
        ('enclosure', 'Enclosure'),
        ('work_location', 'Work Location'),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('name', 'category')

    def __str__(self):
        return f"{self.category} - {self.name}"

class DailyTaskReport(models.Model):
    """تقرير المهام اليومي"""


    engineer        = models.ForeignKey(
                          settings.AUTH_USER_MODEL,
                          on_delete=models.PROTECT,
                          related_name='daily_reports',
                          verbose_name="المهندس"
                      )
    report_date     = models.DateField(verbose_name="تاريخ التقرير")
    crop            = models.ForeignKey('farm.Crop', on_delete=models.PROTECT, verbose_name="المحصول", null=True, blank=True)
    stage           = models.ForeignKey('farm.Stage', on_delete=models.PROTECT, null=True, blank=True, verbose_name="المرحلة")
    enclosure       = models.ForeignKey('farm.Enclosure', on_delete=models.PROTECT, related_name="reports_enclosure", verbose_name="الحوشة", null=True, blank=True)
    variety         = models.ForeignKey(ReportDropdownOption, on_delete=models.PROTECT, limit_choices_to={'category': 'variety'}, related_name="reports_variety", verbose_name="الصنف")
    work_location   = models.CharField(max_length=100, verbose_name="مكان العمل")
    company_workers = models.PositiveIntegerField(default=0, verbose_name="عمال الشركة")
    contractor_workers = models.PositiveIntegerField(default=0, verbose_name="عمال المقاول")
    contractor      = models.ForeignKey(ReportDropdownOption, on_delete=models.PROTECT, limit_choices_to={'category': 'contractor'}, related_name="reports_contractor", null=True, blank=True, verbose_name="كود المقاول")
    operation       = models.ForeignKey(Operation, on_delete=models.PROTECT, verbose_name="العملية الفنية")
    unit            = models.ForeignKey(ReportDropdownOption, on_delete=models.PROTECT, limit_choices_to={'category': 'unit'}, related_name="reports_unit", verbose_name="الوحدة")
    actual_productivity  = models.FloatField(null=True, blank=True, verbose_name="الانتاجية الفعلية")
    work_hours      = models.FloatField(verbose_name="ساعات العمل")
    overtime_hours  = models.FloatField(null=True, blank=True, verbose_name="ساعات الإضافي")
    overtime_productivity = models.FloatField(null=True, blank=True, verbose_name="انتاجية الإضافي")
    notes           = models.TextField(blank=True, verbose_name="ملاحظة")
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "تقرير مهام يومي"
        verbose_name_plural = "تقارير المهام اليومية"
        ordering = ['-report_date', 'engineer']
        indexes = [
            models.Index(fields=['report_date']),
            models.Index(fields=['engineer', 'report_date']),
            models.Index(fields=['crop', 'report_date']),
        ]

    def __str__(self):
        return f"{self.engineer} | {self.report_date} | {self.operation}"

class FertilizationReport(models.Model):
    """تقرير التسميد"""
    report_date         = models.DateField(verbose_name="تاريخ")
    variety             = models.CharField(max_length=30, verbose_name="الصنف")
    material_name       = models.CharField(max_length=100, verbose_name="المادة الفعالة")
    active_percentage   = models.FloatField(null=True, blank=True, verbose_name="النسبة %")
    rate_per_feddan     = models.FloatField(null=True, blank=True, verbose_name="معدل الفدان")
    transfer_number     = models.IntegerField(null=True, blank=True, verbose_name="رقم التحويلة")
    valves              = models.CharField(max_length=50, blank=True, verbose_name="المحابس")
    area_feddan         = models.FloatField(null=True, blank=True, verbose_name="المساحة (فدان)")
    tree_count          = models.IntegerField(null=True, blank=True, verbose_name="عدد الأشجار")
    total_quantity      = models.FloatField(null=True, blank=True, verbose_name="إجمالي الكمية")
    operator            = models.CharField(max_length=100, blank=True, verbose_name="القائم بالعمل")
    notes               = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "تقرير تسميد"
        verbose_name_plural = "تقارير التسميد"
        ordering = ['-report_date']

class IrrigationReport(models.Model):
    """تقرير الري"""
    report_date       = models.DateField(verbose_name="تاريخ")
    sector_number     = models.IntegerField(verbose_name="رقم القطاع")
    transfer_number   = models.IntegerField(verbose_name="رقم التحويلة")
    area_feddan       = models.FloatField(null=True, blank=True, verbose_name="المساحة (فدان)")
    tree_count        = models.IntegerField(null=True, blank=True, verbose_name="عدد النخيل")
    well_flow_m3      = models.FloatField(null=True, blank=True, verbose_name="تصرف البئر م³/ساعة")
    water_per_tree    = models.FloatField(null=True, blank=True, verbose_name="كمية المياه للنخلة")
    irrigation_hours  = models.FloatField(null=True, blank=True, verbose_name="ساعات الري")
    irrigation_cycles = models.IntegerField(null=True, blank=True, verbose_name="مرات الري")
    notes             = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "تقرير ري"
        verbose_name_plural = "تقارير الري"
        ordering = ['-report_date']

class CustomFieldDefinition(models.Model):
    FIELD_TYPES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('dropdown', 'Dropdown'),
        ('boolean', 'Boolean'),
    ]
    name = models.CharField(max_length=200, verbose_name="Field Name")
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES, verbose_name="Field Type")
    is_required = models.BooleanField(default=False, verbose_name="Is Required?")
    applies_to = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name="Applies to Model")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name="Created By")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Custom Field Definition"
        verbose_name_plural = "Custom Field Definitions"

    def __str__(self):
        return f"{self.name} ({self.applies_to.model})"

class CustomFieldValue(models.Model):
    field = models.ForeignKey(CustomFieldDefinition, on_delete=models.CASCADE, related_name='values')
    value = models.TextField(verbose_name="Value")
    
    # Generic relation to link to any report (DailyTaskReport, FertilizationReport, etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = "Custom Field Value"
        verbose_name_plural = "Custom Field Values"
        unique_together = ('field', 'content_type', 'object_id') # Each field has one value per record

    def __str__(self):
        return f"{self.field.name}: {self.value}"
