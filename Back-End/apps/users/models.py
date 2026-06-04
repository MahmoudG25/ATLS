from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


from core.models import BaseEntity
import uuid6

class Company(BaseEntity):
    name = models.CharField(max_length=255, unique=True)
    subscription_plan = models.CharField(max_length=100, default="starter")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_approved", True)
        extra_fields.setdefault("role", "SUPER_ADMIN")

        return self.create_user(email, password, **extra_fields)


class AppPermission(BaseEntity):
    code = models.CharField(max_length=100, unique=True, help_text="e.g. 'reports.override', 'reports.delete'")
    name = models.CharField(max_length=255, help_text="e.g. 'Can Override Reports'")
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "صلاحية مخصصة"
        verbose_name_plural = "صلاحيات مخصصة"

    def __str__(self):
        return f"{self.name} ({self.code})"


class RoleChoices(models.TextChoices):
    SUPER_ADMIN = "SUPER_ADMIN", _("Super Admin")
    OWNER = "OWNER", _("Owner")
    MANAGER = "MANAGER", _("Manager")
    ENGINEER = "ENGINEER", _("Engineer")
    ACCOUNTANT = "ACCOUNTANT", _("Accountant")
    HR = "HR", _("HR")
    WAREHOUSE = "WAREHOUSE", _("Warehouse")


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid6.uuid7, editable=False)
    username = None  # Remove username field
    email = models.EmailField(_("email address"), unique=True)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=RoleChoices.choices)
    phones = models.JSONField(default=list, blank=True)
    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )

    # Custom flags
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    avatar_url = models.URLField(max_length=1000, blank=True, default="")

    # Formal Relational Permission Architecture (Phase 4)
    app_permissions = models.ManyToManyField(
        AppPermission,
        blank=True,
        related_name="users",
        verbose_name="صلاحيات مخصصة"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "role"]

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email} ({self.role})"


class LandingContent(BaseEntity):
    """
    Singleton CMS Model defining the strings on the Public Facing UI
    in Enlish and Arabic natively.
    """

    hero_title_en = models.CharField(
        max_length=255, default="Precision Agriculture, Redefined."
    )
    hero_title_ar = models.CharField(
        max_length=255, default="الزراعة الدقيقة، أعيد تعريفها."
    )
    hero_text_en = models.TextField(
        default="Seamlessly manage Palm and Olive field structures."
    )
    hero_text_ar = models.TextField(default="إدارة مجالات النخيل والزيتون بسلاسة تامة.")

    palm_text_en = models.TextField(default="Track Every Mother Tree & Offshoot.")
    palm_text_ar = models.TextField(default="تتبع كل شجرة أم و فسيلة.")

    olive_text_en = models.TextField(default="Synchronized Harvest Operations.")
    olive_text_ar = models.TextField(default="عمليات حصاد متزامنة.")

    logo_text_en = models.CharField(max_length=100, default="Atlas Farm")
    logo_text_ar = models.CharField(max_length=100, default="أطلس سيوة")
    logo_url = models.TextField(default="", blank=True)

    # About Section
    about_title_en = models.CharField(
        max_length=255, default="Precision Farming Redefined"
    )
    about_title_ar = models.CharField(
        max_length=255, default="نظام أطلس لإدارة حقول النخيل والزيتون الدقيقة"
    )
    about_text_en = models.TextField(
        default="Atlas ERP empowers large-scale agricultural enterprises to register layout elements, tracks trees individually, structures daily engineer reporting sheets, and automates continuous yield metrics."
    )
    about_text_ar = models.TextField(
        default="تم تصميم نظام أطلس الزراعي الموحد ليقود ثورة تكنولوجية في أتمتة وتحليل بيانات المزارع الكبيرة. يساعدك محركنا الذكي على مراقبة الأشجار والإنتاجية وجدولة المهام والأسطول في مكان واحد."
    )

    # Features Section Title
    features_title_en = models.CharField(
        max_length=255, default="Why Choose Atlas ERP for Your Agriculture?"
    )
    features_title_ar = models.CharField(
        max_length=255, default="ما الذي يجعل أطلس الأفضل لإدارة مزارعك؟"
    )

    # Contact Section
    contact_title_en = models.CharField(
        max_length=255, default="Ready to Transform Your Operations?"
    )
    contact_title_ar = models.CharField(
        max_length=255, default="ابدأ في رقمنة وأتمتة مزارعك اليوم"
    )
    contact_text_en = models.TextField(
        default="Sign up today to configure your companies, isolate records, and launch dynamic daily reporting tools."
    )
    contact_text_ar = models.TextField(
        default="تواصل معنا الآن للحصول على استشارة كاملة لربط مزارعك وهيكلها وتجهيز لوحة التحكم المخصصة لشركتك."
    )
    contact_email = models.CharField(max_length=100, default="info@atlasfarm.dz")
    contact_phone = models.CharField(max_length=100, default="+213 (0) 5XX XXX XXX")

    def __str__(self):
        return "Atlas Global Layout Config"


class Notification(BaseEntity):
    """
    System notification for user alerts — new registrations, low stock, etc.
    """

    NOTIFICATION_TYPES = [
        ("user_pending", "User Pending Approval"),
        ("low_stock", "Low Stock Alert"),
        ("invoice", "New Invoice"),
        ("leave_request", "Leave Request"),
        ("system", "System Notification"),
    ]

    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    message_ar = models.CharField(max_length=255)
    message_en = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, default="system")
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=200, blank=True, default="")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.type}] → {self.recipient.email}"


class ActivityLog(BaseEntity):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="activity_logs"
    )
    action = models.CharField(max_length=255)
    module = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} - {self.action} ({self.created_at})"


class PasswordResetRequest(BaseEntity):
    email = models.EmailField()
    code = models.CharField(max_length=6)
    is_approved = models.BooleanField(default=False)
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.email} - Code: {self.code} - Approved: {self.is_approved}"


class Announcement(models.Model):
    """
    Company-wide bulletin board announcements.
    Published by admins/users with `can_post_announcement` permission.
    All company members can read them.
    """
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="announcements",
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    image_url = models.URLField(max_length=1000, blank=True)
    video_url = models.URLField(max_length=1000, blank=True)
    file_url = models.URLField(max_length=1000, blank=True)
    file_name = models.CharField(max_length=255, blank=True)
    is_pinned = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    category = models.CharField(max_length=50, default="general")
    is_active = models.BooleanField(default=True)
    published_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="announcements",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.company})"


from core.tenant import TenantAwareModel

class FarmSystemConfig(TenantAwareModel):
    # Branding Specs
    farm_name = models.CharField(max_length=255, default="مزرعة أطلس النموذجية")
    logo_url = models.URLField(blank=True, null=True)
    primary_color = models.CharField(max_length=50, default="#1E3A1E") # Deep Academic Green
    accent_color = models.CharField(max_length=50, default="#D4AF37")  # Wheat Gold
    currency = models.CharField(max_length=20, default="جنية مصري")
    active_font = models.CharField(max_length=50, default="Cairo")
    
    # Feature Toggles (Global Application Flags)
    feature_accounting = models.BooleanField(default=True, verbose_name="نظام المحاسبة")
    feature_hr = models.BooleanField(default=True, verbose_name="نظام الموارد البشرية HR")
    feature_fleet = models.BooleanField(default=True, verbose_name="منظومة الأسطول والمعدات")
    feature_warehouse = models.BooleanField(default=True, verbose_name="إدارة المخازن والمستودع")

    class Meta:
        db_table = 'farm_system_configs'
        verbose_name = 'إعدادات النظام والمزرعة'

    def __str__(self):
        return f"Config for {self.company.name if self.company else 'System'}"

