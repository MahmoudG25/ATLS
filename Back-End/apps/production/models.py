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
    labor_count = models.PositiveIntegerField(default=0, verbose_name="إجمالي عدد العمال")
    company_workers = models.PositiveIntegerField(default=0, verbose_name="عمال الشركة")
    contractor_workers = models.PositiveIntegerField(default=0, verbose_name="عمال المقاول")
    contractor_name = models.CharField(max_length=200, blank=True, verbose_name="اسم المقاول")
    labor_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name="ساعات العمل")
    supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="supervised_harvests"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="authored_harvests"
    )
    transport_method = models.TextField(blank=True, verbose_name="طريقة النقل / معلومات النقل")
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="التكلفة التقديرية")
    
    # Historical Snapshots (Prevent Data Drift)
    variety_name_snapshot = models.CharField(max_length=200, blank=True)
    unit_label_snapshot = models.CharField(max_length=50, blank=True)
    
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    
    # Super Admin overrides tracker
    override_reason = models.TextField(blank=True, verbose_name="سبب التعديل الاستثنائي")
    override_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="overridden_harvests"
    )
    override_at = models.DateTimeField(null=True, blank=True)
    was_overridden = models.BooleanField(default=False)

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
        # Since we use UUID7 defaults, self.pk is populated even for new records.
        # We must check if the record exists in the DB to determine if it's an update.
        if self.pk and not getattr(self, "_state", None).adding:
            try:
                original = HarvestReport.objects.get(pk=self.pk)
                if original.status == self.STATE_FINALIZED and not kwargs.get("force_update", False) and not getattr(self, "force_update", False):
                    from django.core.exceptions import ValidationError
                    raise ValidationError("Cannot modify a finalized harvest report.")
            except HarvestReport.DoesNotExist:
                pass
        super().save(*args, **kwargs)


class HarvestAttachment(TenantAwareModel):
    """مرفقات تقرير الحصاد - Images, PDFs, etc."""
    FILE_TYPE_IMAGE = "IMAGE"
    FILE_TYPE_VIDEO = "VIDEO"
    FILE_TYPE_FILE = "FILE"
    FILE_TYPE_CHOICES = [
        (FILE_TYPE_IMAGE, "Image"),
        (FILE_TYPE_VIDEO, "Video"),
        (FILE_TYPE_FILE, "File"),
    ]

    report = models.ForeignKey(
        HarvestReport, 
        on_delete=models.CASCADE, 
        related_name="attachments"
    )
    file_url = models.URLField(max_length=1000, null=True, blank=True)
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES, default=FILE_TYPE_IMAGE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for {self.report.id} - {self.file_type}"


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
        # Same check for UUID7 populated PKs
        if self.pk and not getattr(self, "_state", None).adding:
            try:
                original = SortingReport.objects.get(pk=self.pk)
                if original.status == self.STATE_FINALIZED and not kwargs.get("force_update", False):
                    from django.core.exceptions import ValidationError
                    raise ValidationError("Cannot modify a finalized sorting report.")
            except SortingReport.DoesNotExist:
                pass
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
