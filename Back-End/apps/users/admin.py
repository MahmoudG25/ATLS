from django.contrib import admin
from .models import Company, User, LandingContent, Notification, ActivityLog


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "subscription_plan", "is_active", "created_at")

    def has_add_permission(self, request):
        # Single-Tenant: Disable add permission if a company already exists
        if Company.objects.exists():
            return False
        return super().has_add_permission(request)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "name", "role", "company", "is_approved", "is_active")
    list_filter = ("role", "is_approved", "is_active", "company")
    search_fields = ("email", "name")
    actions = ["approve_users"]

    def approve_users(self, request, queryset):
        queryset.update(is_approved=True)

    approve_users.short_description = "Approve selected users"


@admin.register(LandingContent)
class LandingContentAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        if LandingContent.objects.exists():
            return False
        return True


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("type", "recipient", "message_ar", "is_read", "created_at")
    list_filter = ("type", "is_read")


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("user", "action", "module", "created_at")
    list_filter = ("module", "created_at")
    readonly_fields = (
        "user",
        "action",
        "module",
        "description",
        "ip_address",
        "created_at",
    )
