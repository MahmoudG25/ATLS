from django.db import models
from django.conf import settings
from core.tenant import TenantAwareModel


class HarvestReport(TenantAwareModel):
    """تقرير الحصاد - Core operational entity for enclosure-centric yields"""
    
    STATE_DRAFT = "DRAFT"
    STATE_SUBMITTED = "SUBMITTED"
    STATE_APPROVED = "APPROVED"
    STATE_FINALIZED = "FINALIZED"
    STATE_CHOICES = [
        (STATE_DRAFT, "مسودة"),
        (STATE_SUBMITTED, "مقدم"),
        (STATE_APPROVED, "معتمد"),
        (STATE_FINALIZED, "نهائي - مقفل"),
    ]

    # Enclosure-centric core
    location = models.ForeignKey(
        "farm.LocationNode", 
        on_delete=models.PROTECT, 
        related_name="harvest_reports",
        limit_choices_to={"type": "ENCLOSURE"}
    )
    season = models.ForeignKey(
        "reports.Season", 
        on_delete=models.PROTECT, 
        related_name="harvest_reports"
    )
    harvest_date = models.DateField(verbose_name="تاريخ الحصاد")
    variety = models.ForeignKey(
        "reports.Variety", 
        on_delete=models.PROTECT, 
        related_name="harvest_reports"
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="الكمية المحصودة")
    unit = models.ForeignKey(
        "reports.Unit", 
        on_delete=models.PROTECT, 
        related_name="harvest_reports"
    )

    # Workflow & Governance
    status = models.CharField(max_length=20, choices=STATE_CHOICES, default=STATE_DRAFT)
    is_partial = models.BooleanField(default=False, verbose_name="حصاد جزئي")
    
    # Labor & Logistics
    labor_count = models.PositiveIntegerField(default=0, verbose_name="عدد العمال")
    labor_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name="ساعات العمل")
    supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="supervised_harvests"
    )
    transportation_info = models.TextField(blank=True, verbose_name="معلومات النقل")
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="التكلفة التقديرية")
    
    # Historical Snapshots (Prevent Data Drift)
    variety_name_snapshot = models.CharField(max_length=200, blank=True)
    unit_label_snapshot = models.CharField(max_length=50, blank=True)
    
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "تقرير حصاد"
        verbose_name_plural = "تقارير الحصاد"
        ordering = ["-harvest_date", "-created_at"]
        indexes = [
            models.Index(fields=["company", "location", "season"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.location.name} | {self.season.name} | {self.harvest_date}"

    def save(self, *args, **kwargs):
        if self.pk:
            original = HarvestReport.objects.get(pk=self.pk)
            if original.status == self.STATE_FINALIZED and not kwargs.get("force_update", False):
                from django.core.exceptions import ValidationError
                raise ValidationError("Cannot modify a finalized harvest report.")
        super().save(*args, **kwargs)


class SortingReport(TenantAwareModel):
    """تقرير الفرز والنشارة - Chained operational processing step"""
    
    STATE_DRAFT = "DRAFT"
    STATE_SUBMITTED = "SUBMITTED"
    STATE_FINALIZED = "FINALIZED"
    STATE_CHOICES = [
        (STATE_DRAFT, "مسودة"),
        (STATE_SUBMITTED, "مقدم"),
        (STATE_FINALIZED, "نهائي - مقفل"),
    ]

    harvest_report = models.ForeignKey(
        HarvestReport, 
        on_delete=models.CASCADE, 
        related_name="sorting_reports",
        verbose_name="تقرير الحصاد المرتبط"
    )
    processing_date = models.DateField(verbose_name="تاريخ الفرز")
    
    # Quantity Integrity
    incoming_quantity = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="الكمية الواردة")
    final_quantity = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="الكمية المقبولة")
    rejected_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="الكمية المرفوضة")
    waste_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="هالك / فاقد")
    
    # Configuration (Master Data)
    sorting_category = models.ForeignKey(
        "reports.SortingCategory", on_delete=models.SET_NULL, null=True, blank=True
    )
    quality_grade = models.ForeignKey(
        "reports.QualityGrade", on_delete=models.SET_NULL, null=True, blank=True
    )
    
    # Workflow
    status = models.CharField(max_length=20, choices=STATE_CHOICES, default=STATE_DRAFT)
    
    # Snapshots
    harvest_info_snapshot = models.JSONField(default=dict, blank=True)
    
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "تقرير فرز"
        verbose_name_plural = "تقارير الفرز"
        ordering = ["-processing_date"]

    def __str__(self):
        return f"Sorting: {self.harvest_report.location.name} ({self.processing_date})"

    def save(self, *args, **kwargs):
        if self.pk:
            original = SortingReport.objects.get(pk=self.pk)
            if original.status == self.STATE_FINALIZED and not kwargs.get("force_update", False):
                from django.core.exceptions import ValidationError
                raise ValidationError("Cannot modify a finalized sorting report.")
        super().save(*args, **kwargs)


class AnnualYield(models.Model):
    """DEPRECATED: Will be replaced by SeasonalYield aggregation service"""
    plot = models.ForeignKey(
        "farm.LocationNode", on_delete=models.CASCADE, related_name="annual_yields", null=True
    )
    year = models.PositiveIntegerField()
    production_amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["plot", "year"], name="unique_plot_year_yield"
            )
        ]
