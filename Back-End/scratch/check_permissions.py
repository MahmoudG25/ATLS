import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from apps.users.models import User, AppPermission

print("--- APP PERMISSIONS IN DATABASE ---")
for perm in AppPermission.objects.all().order_by("code"):
    print(f"ID: {perm.id} | Code: {perm.code} | Name: {perm.name}")

print("\n--- USER PERMISSIONS ---")
for user in User.objects.all().order_by("email"):
    perms = list(user.app_permissions.values_list("code", flat=True))
    print(f"User: {user.email} | Role: {user.role} | Permissions: {perms}")
