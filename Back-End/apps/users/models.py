from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_approved', True)
        extra_fields.setdefault('role', 'SUPER_ADMIN')

        return self.create_user(email, password, **extra_fields)

class RoleChoices(models.TextChoices):
    SUPER_ADMIN = 'SUPER_ADMIN', _('Super Admin')
    OWNER = 'OWNER', _('Owner')
    MANAGER = 'MANAGER', _('Manager')
    ENGINEER = 'ENGINEER', _('Engineer')
    ACCOUNTANT = 'ACCOUNTANT', _('Accountant')
    HR = 'HR', _('HR')
    WAREHOUSE = 'WAREHOUSE', _('Warehouse')

class User(AbstractUser):
    username = None  # Remove username field
    email = models.EmailField(_('email address'), unique=True)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=RoleChoices.choices)
    phones = models.JSONField(default=list, blank=True)
    
    # Custom flags
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'role']

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email} ({self.role})"

class LandingContent(models.Model):
    """
    Singleton CMS Model defining the strings on the Public Facing UI
    in Enlish and Arabic natively.
    """
    hero_title_en = models.CharField(max_length=255, default="Precision Agriculture, Redefined.")
    hero_title_ar = models.CharField(max_length=255, default="الزراعة الدقيقة، أعيد تعريفها.")
    hero_text_en = models.TextField(default="Seamlessly manage Palm and Olive field structures.")
    hero_text_ar = models.TextField(default="إدارة مجالات النخيل والزيتون بسلاسة تامة.")
    
    palm_text_en = models.TextField(default="Track Every Mother Tree & Offshoot.")
    palm_text_ar = models.TextField(default="تتبع كل شجرة أم و فسيلة.")
    
    olive_text_en = models.TextField(default="Synchronized Harvest Operations.")
    olive_text_ar = models.TextField(default="عمليات حصاد متزامنة.")
    
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return "Atlas Global Layout Config"

class Notification(models.Model):
    """
    System notification for user alerts — new registrations, low stock, etc.
    """
    NOTIFICATION_TYPES = [
        ('user_pending', 'User Pending Approval'),
        ('low_stock', 'Low Stock Alert'),
        ('invoice', 'New Invoice'),
        ('leave_request', 'Leave Request'),
        ('system', 'System Notification'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message_ar = models.CharField(max_length=255)
    message_en = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, default='system')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    link = models.CharField(max_length=200, blank=True, default='')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.type}] → {self.recipient.email}"

