from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from core.tenant import TenantAwareModel
import uuid


class Operation(TenantAwareModel):
    """قائمة العمليات الفنية الثابتة"""

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, null=True, blank=True)
    profile_type = models.CharField(max_length=50, default="generic")
    is_system = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    CATEGORY_CHOICES = [
        ("pollination", "تلقيح ومشاتل"),
        ("planting", "زراعة وفسائل"),
        ("maintenance", "صيانة ونظافة"),
        ("fertilization", "تسميد"),
        ("protection", "مكافحة"),
        ("monitoring", "متابعة وإشراف"),
        ("transport", "نقل وتحميل"),
        ("other", "أخرى"),
    ]
    category = models.CharField(
        max_length=50, choices=CATEGORY_CHOICES, default="other"
    )
    
    # JSON Schema Governance
    json_schema = models.JSONField(
        null=True, blank=True, 
        help_text="JSON Schema (Draft-7) rules for validating profile_data"
    )
    ui_schema = models.JSONField(
        null=True, blank=True, 
        help_text="UI definitions for rendering forms and timeline fields"
    )
    schema_version = models.IntegerField(default=1)

    class Meta:
        verbose_name = "عملية فنية"
        verbose_name_plural = "العمليات الفنية"
        unique_together = [("company", "name")]

    def __str__(self):
        return self.name


class Season(TenantAwareModel):
    """الموسم الزراعي - First-class domain for governing reporting periods"""
    STATUS_CHOICES = [
        ("OPEN", "مفتوح"),
        ("CLOSED", "مغلق"),
        ("ARCHIVED", "مؤرشف"),
    ]
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="OPEN")
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "موسم"
        verbose_name_plural = "المواسم"
        ordering = ["-start_date"]
        unique_together = [("company", "name")]

    def __str__(self):
        return self.name


class Variety(TenantAwareModel):
    name = models.CharField(max_length=100)
    company = models.ForeignKey(
        "users.Company", on_delete=models.CASCADE, related_name="varieties"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Variety"
        verbose_name_plural = "Varieties"
        unique_together = ("company", "name")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Unit(TenantAwareModel):
    name = models.CharField(max_length=100)
    company = models.ForeignKey(
        "users.Company", on_delete=models.CASCADE, related_name="units"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Unit"
        verbose_name_plural = "Units"
        unique_together = ("company", "name")
        ordering = ["name"]

    def __str__(self):
        return self.name


class LaborCategory(TenantAwareModel):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Labor Category"
        verbose_name_plural = "Labor Categories"
        unique_together = [("company", "name")]

    def __str__(self):
        return self.name


class QualityGrade(TenantAwareModel):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Quality Grade"
        verbose_name_plural = "Quality Grades"
        unique_together = [("company", "name")]

    def __str__(self):
        return self.name


class SortingCategory(TenantAwareModel):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Sorting Category"
        verbose_name_plural = "Sorting Categories"
        unique_together = [("company", "name")]

    def __str__(self):
        return self.name


class PackagingType(TenantAwareModel):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Packaging Type"
        verbose_name_plural = "Packaging Types"
        unique_together = [("company", "name")]

    def __str__(self):
        return self.name


class ProductivityClassification(TenantAwareModel):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Productivity Classification"
        verbose_name_plural = "Productivity Classifications"
        unique_together = [("company", "name")]

    def __str__(self):
        return self.name


class ReportDropdownOption(TenantAwareModel):
    CATEGORY_CHOICES = [
        ("variety", "Variety"),
        ("unit", "Unit"),
        ("contractor", "Contractor"),
        ("enclosure", "Enclosure"),
        ("work_location", "Work Location"),
    ]

    name = models.CharField(max_length=100)
    company = models.ForeignKey(
        "users.Company",
        on_delete=models.CASCADE,
        related_name="report_options",
        null=True,
        blank=True,
    )
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("company", "name", "category")

    def __str__(self):
        return f"{self.category} - {self.name}"


class DailyTaskReport(TenantAwareModel):
    """تقرير المهام اليومي"""

    STATUS_CHOICES = [
        ("draft", "مسودة"),
        ("submitted", "مقدم"),
        ("under_review", "قيد المراجعة"),
        ("approved", "معتمد"),
        ("rejected", "مرفوض"),
    ]
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="draft", verbose_name="حالة التقرير"
    )
    rejection_reason = models.TextField(blank=True, verbose_name="سبب الرفض")

    engineer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="daily_reports",
        verbose_name="المهندس",
    )
    report_date = models.DateField(verbose_name="تاريخ التقرير")
    location = models.ForeignKey(
        "farm.LocationNode", on_delete=models.PROTECT, related_name="daily_task_reports"
    )
    variety = models.ForeignKey(
        "reports.Variety",
        on_delete=models.PROTECT,
        related_name="daily_task_reports",
        verbose_name="الصنف",
    )
    work_location = models.ForeignKey(
        "farm.LocationNode",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="daily_task_work_reports",
        verbose_name="مكان العمل",
    )
    company_workers = models.PositiveIntegerField(default=0, verbose_name="عمال الشركة")
    contractor_workers = models.PositiveIntegerField(
        default=0, verbose_name="عمال المقاول"
    )
    contractor = models.ForeignKey(
        "reports.Contractor",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="daily_task_reports",
        verbose_name="كود المقاول",
    )
    contractors = models.ManyToManyField(
        "reports.Contractor",
        blank=True,
        related_name="daily_task_reports_m2m",
        verbose_name="المقاولون"
    )
    operation = models.ForeignKey(
        Operation, on_delete=models.PROTECT, verbose_name="العملية الفنية"
    )
    unit = models.ForeignKey(
        "reports.Unit",
        on_delete=models.PROTECT,
        related_name="daily_task_reports",
        verbose_name="الوحدة",
    )
    actual_productivity = models.FloatField(
        null=True, blank=True, verbose_name="الانتاجية الفعلية"
    )
    work_hours = models.FloatField(verbose_name="ساعات العمل")
    overtime_hours = models.FloatField(
        null=True, blank=True, verbose_name="ساعات الإضافي"
    )
    overtime_productivity = models.FloatField(
        null=True, blank=True, verbose_name="انتاجية الإضافي"
    )
    notes = models.TextField(blank=True, verbose_name="ملاحظة")
    
    # Override fields
    override_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="overridden_reports",
        verbose_name="المعدل الاستثنائي"
    )
    override_at = models.DateTimeField(null=True, blank=True, verbose_name="وقت التعديل الاستثنائي")
    override_reason = models.TextField(null=True, blank=True, verbose_name="سبب التعديل")
    was_overridden = models.BooleanField(default=False, verbose_name="تم تعديله استثنائياً")
    
    # Soft Delete fields for auditability
    is_deleted = models.BooleanField(default=False, verbose_name="محذوف")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الحذف")
    deleted_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deleted_reports",
        verbose_name="تم الحذف بواسطة"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ التقديم")
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الاعتماد")
    rejected_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الرفض")

    class Meta:
        verbose_name = "تقرير مهام يومي"
        verbose_name_plural = "تقارير المهام اليومية"
        ordering = ["-updated_at", "-created_at"]
        indexes = [
            models.Index(fields=["company", "report_date"]),
            models.Index(fields=["company", "operation", "report_date"]),
            models.Index(fields=["report_date"]),
            models.Index(fields=["engineer", "report_date"]),
        ]

    def __str__(self):
        return f"{self.engineer} | {self.report_date} | {self.operation}"

    @property
    def farm(self):
        """Derived from location. LocationNode always has a farm."""
        return self.location.farm if self.location else None

    @property
    def total_cost(self):
        return sum(
            (line.hours + line.overtime) * line.worker_rate
            for line in self.labor_entries.all()
        )

    def clean(self):
        super().clean()
        if not self.location:
            raise ValidationError({"location": "Location is required."})
        self.assert_same_company(self.location, "location")
        if self.location.farm.company_id != self.company_id:
            raise ValidationError({"location": "Invalid tenant relation"})
        if self.variety and self.variety.company_id != self.company_id:
            raise ValidationError({"variety": "Invalid tenant relation"})
        if self.contractor and self.contractor.company_id != self.company_id:
            raise ValidationError({"contractor": "Invalid tenant relation"})
        if self.unit and self.unit.company_id != self.company_id:
            raise ValidationError({"unit": "Invalid tenant relation"})
        if self.operation and self.operation.company_id != self.company_id:
            raise ValidationError({"operation": "Invalid tenant relation"})


class OperationLog(TenantAwareModel):
    """سجل العمليات (Atomic Event) - Optimized for timeline and traceability"""

    # Core Indexed Relationships (Operational Performance)
    location = models.ForeignKey(
        "farm.LocationNode", on_delete=models.PROTECT, related_name="operation_logs", db_index=True
    )
    operation = models.ForeignKey(
        Operation, on_delete=models.PROTECT, verbose_name="العملية الفنية", db_index=True
    )
    season = models.ForeignKey(
        Season, on_delete=models.PROTECT, null=True, blank=True, related_name="operation_logs"
    )
    
    # Generic Source Tracking (Flexible but structured)
    SOURCE_DAILY_TASK = "DAILY_TASK"
    SOURCE_HARVEST = "HARVEST"
    SOURCE_SORTING = "SORTING"
    SOURCE_IRRIGATION = "IRRIGATION"
    SOURCE_PEST_CONTROL = "PEST_CONTROL"
    SOURCE_CHOICES = [
        (SOURCE_DAILY_TASK, "Daily Task Report"),
        (SOURCE_HARVEST, "Harvest Report"),
        (SOURCE_SORTING, "Sorting Report"),
        (SOURCE_IRRIGATION, "Irrigation Report"),
        (SOURCE_PEST_CONTROL, "Pest Control Report"),
    ]
    source_type = models.CharField(max_length=50, choices=SOURCE_CHOICES, db_index=True, null=True, blank=True)
    source_id = models.CharField(max_length=255, db_index=True, null=True, blank=True)
    
    # Backward compatibility / legacy link (will be deprecated once all domains use generic source)
    report = models.ForeignKey(
        DailyTaskReport, on_delete=models.CASCADE, related_name="operation_logs", 
        verbose_name="التقرير الحاوي", null=True, blank=True
    )

    # Lineage & Traceability
    parent_log = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="child_logs",
        verbose_name="العملية الأب"
    )
    chain_id = models.UUIDField(null=True, blank=True, db_index=True, verbose_name="كود السلسلة")

    # Operational Data
    variety = models.ForeignKey(
        "reports.Variety", on_delete=models.PROTECT, null=True, blank=True,
        related_name="operation_logs", verbose_name="الصنف"
    )
    unit = models.ForeignKey(
        "reports.Unit", on_delete=models.PROTECT, null=True, blank=True,
        related_name="operation_logs", verbose_name="الوحدة"
    )
    contractor = models.ForeignKey(
        "reports.Contractor", on_delete=models.PROTECT, null=True, blank=True,
        related_name="operation_logs", verbose_name="كود المقاول"
    )
    contractors = models.ManyToManyField(
        "reports.Contractor",
        blank=True,
        related_name="operation_logs_m2m",
        verbose_name="المقاولون"
    )
    
    company_workers = models.PositiveIntegerField(default=0, verbose_name="عمال الشركة")
    contractor_workers = models.PositiveIntegerField(default=0, verbose_name="عمال المقاول")
    actual_productivity = models.FloatField(null=True, blank=True, verbose_name="الانتاجية الفعلية")
    work_hours = models.FloatField(default=0.0, verbose_name="ساعات العمل")
    overtime_hours = models.FloatField(null=True, blank=True, verbose_name="ساعات الإضافي")
    overtime_productivity = models.FloatField(null=True, blank=True, verbose_name="انتاجية الإضافي")
    sequence = models.PositiveSmallIntegerField(default=0, verbose_name="الترتيب")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # Dynamic Profiles
    profile_type = models.CharField(max_length=50, default="generic")
    profile_version = models.IntegerField(default=1)
    profile_data = models.JSONField(default=dict, blank=True)

    # Soft Delete / Archival metadata
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deleted_operation_logs",
    )

    # Bulk Operations & Scoping
    bulk_operation_id = models.UUIDField(null=True, blank=True, db_index=True)
    
    # Status
    EXECUTION_STATUS_CHOICES = [
        ("PENDING", "قيد الانتظار"),
        ("COMPLETED", "تم التنفيذ"),
        ("FAILED", "فشل التنفيذ"),
        ("SKIPPED", "تم التخطي"),
    ]
    status = models.CharField(max_length=20, choices=EXECUTION_STATUS_CHOICES, default="COMPLETED")

    class Meta:
        verbose_name = "سجل عملية"
        verbose_name_plural = "سجلات العمليات"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["company", "operation", "created_at"]),
            models.Index(fields=["company", "location", "created_at"]),
            models.Index(fields=["source_type", "source_id"]),
        ]

    def __str__(self):
        return f"{self.operation} @ {self.location} ({self.created_at.date()})"

    def clean(self):
        super().clean()
        if not self.location:
            raise ValidationError({"location": "Location is required."})
        
        # 1. Enforce Enclosure-only for operations
        from apps.farm.models import LocationNode
        if self.location.type != LocationNode.TYPE_ENCLOSURE:
            raise ValidationError({"location": "يجب أن تستهدف العمليات التشغيلية 'حوشة' فقط لضمان دقة البيانات."})

        if self.report:
            self.assert_same_company(self.report, "report")
        self.assert_same_company(self.location, "location")
        
        # 2. Hierarchy Branch Consistency
        # The operation location MUST be the same as or a descendant of the report location
        if self.report and self.report.location_id and self.location_id:
            report_loc = self.report.location
            if self.location != report_loc and not self.location.is_descendant_of(report_loc):
                # Audit log the attempt (simple implementation)
                print(f"[AUDIT] Location Drift Attempt: Operation {self.operation} tried to link to {self.location} while Report {self.report.id} is at {report_loc}")
                raise ValidationError({
                    "location": f"الموقع المختارة ({self.location.name}) لا يقع ضمن نطاق التقرير الحالي ({report_loc.name})."
                })

        if self.location.farm.company_id != self.company_id:
            raise ValidationError({"location": "Invalid tenant relation"})
        if self.operation and self.operation.company_id != self.company_id:
            raise ValidationError({"operation": "Invalid tenant relation"})
        if self.variety and self.variety.company_id != self.company_id:
            raise ValidationError({"variety": "Invalid tenant relation"})
        if self.unit and self.unit.company_id != self.company_id:
            raise ValidationError({"unit": "Invalid tenant relation"})
        if self.contractor and self.contractor.company_id != self.company_id:
            raise ValidationError({"contractor": "Invalid tenant relation"})


class FertilizationReport(TenantAwareModel):
    """تقرير التسميد"""

    report_date = models.DateField(verbose_name="تاريخ")
    company = models.ForeignKey(
        "users.Company",
        on_delete=models.CASCADE,
        related_name="fertilization_reports",
        null=True,
        blank=True,
    )
    enclosure = models.ForeignKey(
        "farm.LocationNode",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fertilization_reports",
        verbose_name="الحوشة",
    )
    variety = models.CharField(max_length=30, verbose_name="الصنف")
    material_name = models.CharField(max_length=100, verbose_name="المادة الفعالة")
    active_percentage = models.FloatField(
        null=True, blank=True, verbose_name="النسبة %"
    )
    rate_per_feddan = models.FloatField(
        null=True, blank=True, verbose_name="معدل الفدان"
    )
    transfer_number = models.IntegerField(
        null=True, blank=True, verbose_name="رقم التحويلة"
    )
    valves = models.CharField(max_length=50, blank=True, verbose_name="المحابس")
    area_feddan = models.FloatField(
        null=True, blank=True, verbose_name="المساحة (فدان)"
    )
    tree_count = models.IntegerField(null=True, blank=True, verbose_name="عدد الأشجار")
    total_quantity = models.FloatField(
        null=True, blank=True, verbose_name="إجمالي الكمية"
    )
    operator = models.CharField(
        max_length=100, blank=True, verbose_name="القائم بالعمل"
    )
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "تقرير تسميد"
        verbose_name_plural = "تقارير التسميد"
        ordering = ["-report_date"]


class IrrigationReport(TenantAwareModel):
    """تقرير الري المحدث"""

    date = models.DateField(verbose_name="التاريخ")
    engineer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="irrigation_reports_v2",
        verbose_name="المهندس المسؤول"
    )
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")
    attachments = models.JSONField(default=list, blank=True, verbose_name="المرفقات")
    is_fertilized = models.BooleanField(default=False, verbose_name="مع تسميد")
    
    total_shifts = models.IntegerField(default=0, verbose_name="إجمالي التحويلات")
    total_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0.0, verbose_name="إجمالي الساعات")
    company_workers = models.PositiveIntegerField(default=0, verbose_name="عمال الشركة")
    contractor_workers_a = models.PositiveIntegerField(default=0, verbose_name="عمال مقاول أ")
    contractor_workers_b = models.PositiveIntegerField(default=0, verbose_name="عمال مقاول ب")
    contractor = models.ForeignKey(
        "reports.Contractor",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="irrigation_reports_v2_linked",
        verbose_name="المقاول"
    )
    contractor_workers = models.PositiveIntegerField(default=0, verbose_name="عمال المقاول")

    class Meta:
        verbose_name = "تقرير ري"
        verbose_name_plural = "تقارير الري"
        ordering = ["-date"]


class CustomFieldDefinition(TenantAwareModel):
    FIELD_TYPES = [
        ("text", "Text"),
        ("number", "Number"),
        ("date", "Date"),
        ("dropdown", "Dropdown"),
        ("boolean", "Boolean"),
    ]
    name = models.CharField(max_length=200, verbose_name="Field Name")
    field_type = models.CharField(
        max_length=20, choices=FIELD_TYPES, verbose_name="Field Type"
    )
    is_required = models.BooleanField(default=False, verbose_name="Is Required?")
    company = models.ForeignKey(
        "users.Company",
        on_delete=models.CASCADE,
        related_name="custom_field_definitions",
        null=True,
        blank=True,
    )
    applies_to = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, verbose_name="Applies to Model"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Created By",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Custom Field Definition"
        verbose_name_plural = "Custom Field Definitions"

    def __str__(self):
        return f"{self.name} ({self.applies_to.model})"


class CustomFieldValue(TenantAwareModel):
    field = models.ForeignKey(
        CustomFieldDefinition, on_delete=models.CASCADE, related_name="values"
    )
    value = models.TextField(verbose_name="Value")

    # Generic relation to link to any report (DailyTaskReport, FertilizationReport, etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        verbose_name = "Custom Field Value"
        verbose_name_plural = "Custom Field Values"
        unique_together = (
            "field",
            "content_type",
            "object_id",
        )  # Each field has one value per record

    def __str__(self):
        return f"{self.field.name}: {self.value}"


class Contractor(TenantAwareModel):
    ACTIVITY_TYPE_CHOICES = [
        ("labor_supply", "توريد عمالة"),
        ("equipment_rental", "تأجير معدات"),
        ("general_contracting", "مقاولات عامة"),
        ("specialized_services", "خدمات متخصصة"),
        ("other", "أخرى"),
    ]

    name = models.CharField(max_length=120)
    rate_per_hour = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    phone_number = models.CharField(max_length=50, blank=True, default="", verbose_name="رقم الهاتف")
    email = models.EmailField(blank=True, default="", verbose_name="البريد الإلكتروني")
    address = models.CharField(max_length=255, blank=True, default="", verbose_name="العنوان")
    commercial_registry = models.CharField(max_length=100, blank=True, default="", verbose_name="السجل التجاري")
    tax_card = models.CharField(max_length=100, blank=True, default="", verbose_name="البطاقة الضريبية")
    contract_date = models.DateField(null=True, blank=True, verbose_name="تاريخ التعاقد")
    activity_type = models.CharField(
        max_length=50,
        choices=ACTIVITY_TYPE_CHOICES,
        blank=True,
        default="",
        verbose_name="نوع النشاط"
    )
    notes = models.TextField(blank=True, default="", verbose_name="ملاحظات")

    class Meta:
        unique_together = ("company", "name")
        ordering = ["name"]

    def __str__(self):
        return self.name


class LaborEntry(TenantAwareModel):
    WORKER_TYPE_COMPANY = "COMPANY"
    WORKER_TYPE_CONTRACTOR = "CONTRACTOR"
    WORKER_TYPE_CHOICES = [
        (WORKER_TYPE_COMPANY, "Company"),
        (WORKER_TYPE_CONTRACTOR, "Contractor"),
    ]

    report = models.ForeignKey(
        DailyTaskReport, on_delete=models.CASCADE, related_name="labor_entries",
        null=True, blank=True
    )
    harvest_report = models.ForeignKey(
        "production.HarvestReport", on_delete=models.CASCADE, related_name="labor_entries",
        null=True, blank=True
    )
    operation_log = models.ForeignKey(
        "reports.OperationLog",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="labor_entries",
    )
    worker_name = models.CharField(max_length=120)
    worker_type = models.CharField(max_length=20, choices=WORKER_TYPE_CHOICES)
    contractor = models.ForeignKey(
        Contractor,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="labor_entries",
    )
    worker_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    overtime = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["company", "report"]),
            models.Index(fields=["report", "worker_type"]),
        ]

    def clean(self):
        if (
            self.report_id
            and self.company_id
            and self.report.company_id != self.company_id
        ):
            raise ValidationError({"report": "Invalid tenant relation"})
        if self.contractor and self.contractor.company_id != self.company_id:
            raise ValidationError({"contractor": "Invalid tenant relation"})
        if (
            self.operation_log_id
            and self.company_id
            and self.operation_log.company_id != self.company_id
        ):
            raise ValidationError({"operation_log": "Invalid tenant relation"})


class Attachment(TenantAwareModel):
    FILE_TYPE_IMAGE = "IMAGE"
    FILE_TYPE_VIDEO = "VIDEO"
    FILE_TYPE_FILE = "FILE"
    FILE_TYPE_CHOICES = [
        (FILE_TYPE_IMAGE, "Image"),
        (FILE_TYPE_VIDEO, "Video"),
        (FILE_TYPE_FILE, "File"),
    ]

    report = models.ForeignKey(
        DailyTaskReport, on_delete=models.CASCADE, related_name="attachments"
    )
    operation_log = models.ForeignKey(
        "reports.OperationLog",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="attachments",
    )
    file_url = models.URLField(max_length=1000)
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["company", "uploaded_at"]),
        ]

    def clean(self):
        if (
            self.report_id
            and self.company_id
            and self.report.company_id != self.company_id
        ):
            raise ValidationError({"report": "Invalid tenant relation"})
        if (
            self.operation_log_id
            and self.company_id
            and self.operation_log.company_id != self.company_id
        ):
            raise ValidationError({"operation_log": "Invalid tenant relation"})


class ApplicationMethod(TenantAwareModel):
    """طريقة الإضافة (مثال: رش ورقي، حقن في التربة، الخ)"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class GalleryMedia(TenantAwareModel):
    """Media explicitly uploaded for the gallery / slider outside of reports"""
    
    FILE_TYPE_CHOICES = Attachment.FILE_TYPE_CHOICES
    
    file_url = models.URLField(max_length=1000)
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES, default=Attachment.FILE_TYPE_IMAGE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"GalleryMedia {self.id} ({self.file_type})"


class OperationalLocationAllocation(TenantAwareModel):
    """توزيع العمليات التشغيلية والموارد على الأحواش الفردية"""
    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    enclosure = models.ForeignKey('farm.LocationNode', on_delete=models.CASCADE, verbose_name="الحوشة")
    
    # توزيع عمالة مخصص
    allocated_workers_company = models.IntegerField(default=0, verbose_name="عمال شركة")
    allocated_workers_contractor_a = models.IntegerField(default=0, verbose_name="عمال مقاول أ")
    allocated_workers_contractor_b = models.IntegerField(default=0, verbose_name="عمال مقاول ب")
    
    # الإنتاجية والملاحظات
    productivity_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name="الإنتاجية للموقع")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات الموقع")

    class Meta:
        db_table = 'operational_location_allocations'
        verbose_name = 'توزيع العمليات على المواقع'
        verbose_name_plural = 'توزيع العمليات على المواقع'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            from apps.reports.services import sync_allocation_costs
            sync_allocation_costs(self)
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Error syncing allocation costs: {e}", exc_info=True)


class IrrigationDetail(TenantAwareModel):
    """تفاصيل الري لكل مرحلة"""
    report = models.ForeignKey(IrrigationReport, on_delete=models.CASCADE, related_name='details')
    phase = models.ForeignKey('farm.LocationNode', on_delete=models.CASCADE, verbose_name="المرحلة")
    shifts_count = models.IntegerField(verbose_name="عدد التحويلات")
    hours_per_shift = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="عدد الساعات للتحويلة")

    class Meta:
        verbose_name = "تفاصيل الري"
        verbose_name_plural = "تفاصيل الري"


class AppliedFertilizer(TenantAwareModel):
    """الأسمدة المضافة خلال دورة الري"""
    irrigation_detail = models.ForeignKey(IrrigationDetail, on_delete=models.CASCADE, related_name='fertilizers')
    fertilizer_item = models.ForeignKey('warehouse.Item', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="السماد")
    custom_material_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="اسم السماد الخارجي")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="الكمية")
    unit = models.CharField(max_length=50, default="كجم", verbose_name="الوحدة")

    class Meta:
        verbose_name = "السماد المضاف"
        verbose_name_plural = "الأسمدة المضافة"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new and self.custom_material_name:
            try:
                from apps.warehouse.models import MaterialVerificationAlert
                requested_by = self.irrigation_detail.report.engineer if self.irrigation_detail and self.irrigation_detail.report else None
                MaterialVerificationAlert.objects.create(
                    company=self.company,
                    source_report_type='irrigation',
                    source_report_id=self.irrigation_detail.report_id,
                    requested_by=requested_by,
                    suggested_name=self.custom_material_name
                )
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"Error creating material alert: {e}", exc_info=True)


class PestControlReport(TenantAwareModel):
    """تقرير وقاية النبات والمكافحة"""
    date = models.DateField(verbose_name="التاريخ")
    engineer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name="المهندس المسؤول")
    pesticide_item = models.ForeignKey('warehouse.Item', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="المبيد")
    custom_pesticide_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="اسم المبيد الخارجي")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="الكمية المستخدمة")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")
    attachments = models.JSONField(default=list, blank=True, verbose_name="المرفقات")

    class Meta:
        verbose_name = "تقرير مكافحة"
        verbose_name_plural = "تقارير المكافحة"
        ordering = ["-date"]

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new and self.custom_pesticide_name:
            try:
                from apps.warehouse.models import MaterialVerificationAlert
                MaterialVerificationAlert.objects.create(
                    company=self.company,
                    source_report_type='pest_control',
                    source_report_id=self.id,
                    requested_by=self.engineer,
                    suggested_name=self.custom_pesticide_name
                )
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"Error creating material alert: {e}", exc_info=True)


