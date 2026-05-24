from django.db import models
from django.contrib.auth import get_user_model
from core.tenant import TenantAwareModel

User = get_user_model()


class Employee(TenantAwareModel):
    """
    HR Employee record linked to the system User.
    """

    STATUS_CHOICES = [
        ("active", "Active"),
        ("on_leave", "On Leave"),
        ("terminated", "Terminated"),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="employee_profile"
    )
    hire_date = models.DateField()
    department = models.CharField(max_length=100, blank=True, default="")
    position = models.CharField(max_length=100, blank=True, default="")
    salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    monthly_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="الراتب الشهري")
    standard_work_hours = models.PositiveIntegerField(default=8, verbose_name="ساعات العمل القياسية")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    notes = models.TextField(blank=True, default="")

    @property
    def hourly_rate(self):
        """
        احتساب الأجر الساعي للمهندس: (monthly_salary / 30) / standard_work_hours
        أو (salary / 30) / standard_work_hours كاحتياطي
        """
        sal = self.monthly_salary if self.monthly_salary > 0 else self.salary
        if sal > 0 and self.standard_work_hours > 0:
            return (sal / 30) / self.standard_work_hours
        return 0

    def __str__(self):
        return f"{self.user.name} — {self.position}"


class LeaveRequest(TenantAwareModel):
    """
    Employee leave/vacation requests.
    """

    LEAVE_TYPES = [
        ("annual", "Annual Leave"),
        ("sick", "Sick Leave"),
        ("personal", "Personal Leave"),
    ]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="leave_requests"
    )
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(blank=True, default="")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_leaves",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.employee.user.name} — {self.leave_type} ({self.start_date} → {self.end_date})"


class Attendance(TenantAwareModel):
    """
    Daily attendance log for employees.
    """

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="attendance_records"
    )
    date = models.DateField()
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("present", "Present"),
            ("absent", "Absent"),
            ("late", "Late"),
            ("half_day", "Half Day"),
        ],
        default="present",
    )
    notes = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-date"]
        unique_together = ["employee", "date"]

    def __str__(self):
        return f"{self.employee.user.name} — {self.date} ({self.status})"


class PayrollPeriod(TenantAwareModel):
    """
    فترات احتساب الرواتب للمزرعة
    """
    name = models.CharField(max_length=100, verbose_name="اسم الفترة")
    start_date = models.DateField(verbose_name="تاريخ البدء")
    end_date = models.DateField(verbose_name="تاريخ الانتهاء")
    is_closed = models.BooleanField(default=False, verbose_name="مغلقة")

    class Meta:
        ordering = ["-start_date"]
        verbose_name = "فترة الرواتب"
        verbose_name_plural = "فترات الرواتب"

    def __str__(self):
        status = "مغلقة" if self.is_closed else "مفتوحة"
        return f"{self.name} ({self.start_date} -> {self.end_date}) - {status}"


class Worker(TenantAwareModel):
    """
    سجل العامل التشغيلي الميداني في المزرعة (تابع للـ HR وليس له مستخدم بالضرورة)
    """
    STATUS_CHOICES = [
        ("active", "Active"),
        ("on_leave", "On Leave"),
        ("terminated", "Terminated"),
    ]
    WORKER_TYPE_CHOICES = [
        ("COMPANY", "عامل شركة"),
        ("CONTRACTOR", "عامل مقاول"),
    ]

    name = models.CharField(max_length=200, verbose_name="اسم العامل بالكامل")
    worker_type = models.CharField(max_length=20, choices=WORKER_TYPE_CHOICES, default="COMPANY")
    contractor = models.ForeignKey(
        "reports.Contractor", 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="hr_workers",
        verbose_name="المقاول التابع له"
    )
    badge_number = models.CharField(max_length=50, blank=True, default="", verbose_name="رقم البادج / الكود")
    national_id = models.CharField(max_length=50, blank=True, default="", verbose_name="الرقم القومي")
    address = models.CharField(max_length=255, blank=True, default="", verbose_name="العنوان")
    hire_date = models.DateField(null=True, blank=True, verbose_name="تاريخ بدء العمل")
    
    # حقول احتساب الأجر
    monthly_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="الراتب الشهري")
    standard_work_hours = models.PositiveIntegerField(default=8, verbose_name="ساعات العمل القياسية اليومية")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active", verbose_name="الحالة")
    notes = models.TextField(blank=True, default="", verbose_name="ملاحظات")
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def hourly_rate(self):
        """
        احتساب الأجر الساعي ديناميكياً: (الراتب الشهري / 30) / ساعات العمل القياسية
        """
        if self.monthly_salary > 0 and self.standard_work_hours > 0:
            return (self.monthly_salary / 30) / self.standard_work_hours
        return 0

    class Meta:
        ordering = ["name"]
        verbose_name = "عامل ميداني"
        verbose_name_plural = "العمال الميدانيون"

    def __str__(self):
        return f"{self.name} ({self.get_worker_type_display()})"


class PayrollTransaction(TenantAwareModel):
    """
    سجل الحركات المالية المرتبطة بالراتب (إضافي، خصم، إلخ)
    """
    TRANSACTION_TYPES = [
        ("OVERTIME", "عمل إضافي"),
        ("DEDUCTION", "خصم ساعات"),
    ]
    STATUS_CHOICES = [
        ("PENDING", "قيد المراجعة"),
        ("APPROVED", "معتمد"),
        ("REJECTED", "مرفوض"),
    ]

    worker = models.ForeignKey(
        Worker, 
        on_delete=models.CASCADE, 
        related_name="payroll_transactions",
        verbose_name="العامل"
    )
    period = models.ForeignKey(
        PayrollPeriod, 
        on_delete=models.PROTECT, 
        related_name="transactions",
        verbose_name="فترة الرواتب"
    )
    date = models.DateField(verbose_name="التاريخ")
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, verbose_name="نوع الحركة")
    
    # الساعات المدخلة
    hours = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name="عدد الساعات")
    # القيمة المالية المحتسبة
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="المبلغ المالي")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING", verbose_name="الحالة")
    notes = models.TextField(blank=True, default="", verbose_name="ملاحظات")
    
    # مرجع للحركة الأصلية في التقرير
    labor_entry = models.ForeignKey(
        "reports.LaborEntry",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payroll_transactions",
        verbose_name="بند العمالة المصدر"
    )

    class Meta:
        ordering = ["-date"]
        verbose_name = "حركة مالية للراتب"
        verbose_name_plural = "حركات مالية للرواتب"

    def __str__(self):
        return f"{self.worker.name} — {self.transaction_type} ({self.date}) — {self.amount}"


class PendingWorkerReview(TenantAwareModel):
    """
    سجل لمراجعة العمال المسجلين يدوياً من قبل المهندس ولم يتم ربطهم بعد بعامل HR
    """
    labor_entry = models.OneToOneField(
        "reports.LaborEntry",
        on_delete=models.CASCADE,
        related_name="pending_review",
        verbose_name="بند العمالة المرتبط"
    )
    worker_name_fallback = models.CharField(max_length=120, verbose_name="الاسم المكتوب يدوياً")
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False, verbose_name="تم حلها")
    resolved_worker = models.ForeignKey(
        Worker,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resolved_reviews",
        verbose_name="العامل الذي تم ربطه"
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "مراجعة عامل معلق"
        verbose_name_plural = "مراجعات العمال المعلقين"

    def __str__(self):
        return f"مراجعة: {self.worker_name_fallback} (حلّت: {self.resolved})"


class ContractorLedger(TenantAwareModel):
    """
    سجل الحركات المالية والأرصدة الخاصة بمقاولي العمالة
    """
    TRANSACTION_TYPES = [
        ("EARNING", "مستحقات عمل"),
        ("OVERTIME", "إضافي ساعات"),
        ("DEDUCTION", "خصومات ساعات"),
        ("PAYMENT", "دفعة مسددة للمقاول"),
    ]

    contractor = models.ForeignKey(
        "reports.Contractor",
        on_delete=models.CASCADE,
        related_name="ledger_entries",
        verbose_name="المقاول"
    )
    date = models.DateField(verbose_name="التاريخ")
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, verbose_name="نوع الحركة")
    
    # تفاصيل ساعات العمل إذا كانت الحركة متعلقة بالعمل الميداني
    hours = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name="عدد الساعات")
    rate = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="سعر الساعة")
    
    # القيمة المالية للمعاملة
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="المبلغ")
    
    # ربط اختياري ببند العمالة المصدر
    labor_entry = models.ForeignKey(
        "reports.LaborEntry",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contractor_ledger_entries",
        verbose_name="بند العمالة المصدر"
    )
    
    notes = models.TextField(blank=True, default="", verbose_name="ملاحظات")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        verbose_name = "دفتر أستاذ المقاول"
        verbose_name_plural = "دفاتر أستاذ المقاولين"

    def __str__(self):
        return f"{self.contractor.name} — {self.transaction_type} — {self.amount}"


class EmployeeDocument(TenantAwareModel):
    """
    وثائق ومستندات المهندسين والموظفين (البطاقات، شهادات التخرج، العقود، إلخ)
    """
    DOCUMENT_TYPES = [
        ("national_id", "بطاقة الرقم القومي"),
        ("academic_degree", "شهادة التخرج/الشهادة الأكاديمية"),
        ("training_cert", "شهادات الدورات والتدريب"),
        ("contract", "عقد العمل المبرم"),
    ]

    employee = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE, 
        related_name="documents",
        verbose_name="الموظف"
    )
    document_type = models.CharField(
        max_length=30, 
        choices=DOCUMENT_TYPES, 
        verbose_name="نوع المستند"
    )
    document_file = models.FileField(
        upload_to="hr/employee_docs/", 
        verbose_name="ملف المستند"
    )
    issue_date = models.DateField(null=True, blank=True, verbose_name="تاريخ الإصدار")
    expiry_date = models.DateField(null=True, blank=True, verbose_name="تاريخ الانتهاء")
    is_verified = models.BooleanField(default=False, verbose_name="معتمد من الإدارة")
    notes = models.TextField(blank=True, default="", verbose_name="ملاحظات")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "وثيقة موظف"
        verbose_name_plural = "وثائق الموظفين"

    def __str__(self):
        return f"{self.employee.user.name} — {self.get_document_type_display()}"


class PayrollComponent(TenantAwareModel):
    """
    عناصر الرواتب التفصيلية للموظفين (بدلات سكن، انتقالات، خصومات تأمين، إلخ)
    """
    COMPONENT_TYPES = [
        ("ALLOWANCE", "بدل إضافي"),
        ("DEDUCTION", "استقطاع / خصم ثابت"),
    ]

    employee = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE, 
        related_name="payroll_components",
        verbose_name="الموظف"
    )
    type = models.CharField(max_length=20, choices=COMPONENT_TYPES, verbose_name="نوع البند")
    name = models.CharField(max_length=100, verbose_name="اسم البند (مثال: بدل انتقالات)")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="القيمة المالية")
    is_recurring = models.BooleanField(default=True, verbose_name="يتكرر شهرياً تلقائياً")

    class Meta:
        verbose_name = "مكون مالي للراتب"
        verbose_name_plural = "مكونات الرواتب التفصيلية"

    def __str__(self):
        return f"{self.employee.user.name} — {self.name} ({self.amount})"

