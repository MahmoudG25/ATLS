import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.conf import settings
if "testserver" not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append("testserver")

from apps.users.models import User
from rest_framework.test import APIClient

# Get the admin user
user = User.objects.get(email="admin@example.com")
client = APIClient()
client.force_authenticate(user=user)

# Let's get the target user from the logs
target_user = User.objects.get(email="engineer@engineer.co")
print(f"Target User ID: {target_user.id}")

# Request: /api/users/<id>/permissions
url = f"/api/users/{target_user.id}/permissions"
response = client.get(url)
p_hash = response.headers.get("X-User-Permissions-Hash")
print(f"URL: {url} | Status: {response.status_code} | Hash: {p_hash}")

# Request /api/auth/me
response_me = client.get("/api/auth/me")
me_hash = response_me.headers.get("X-User-Permissions-Hash")
print(f"URL: /api/auth/me | Hash: {me_hash}")

print(f"Hashes match: {p_hash == me_hash}")
