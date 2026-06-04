import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.conf import settings
if "testserver" not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append("testserver")

from apps.users.models import User
from rest_framework.test import APIClient

# Let's get the admin user
user = User.objects.get(email="admin@example.com")
print(f"User: {user.email}")
print(f"Role: {user.role}")

# Calculate expected hash
import hashlib
from django.core.cache import cache

cache_key = f"user_perms_hash_{user.id}"
cache.delete(cache_key)

codes = sorted(list(user.app_permissions.values_list("code", flat=True)))
content = f"{user.role}:{','.join(codes)}"
expected_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
print(f"Expected Hash: {expected_hash}")

# Simulate requests via APIClient
client = APIClient()
client.force_authenticate(user=user)

# Request 1: /api/auth/me
response1 = client.get("/api/auth/me")
hash1 = response1.headers.get("X-User-Permissions-Hash")
print(f"Response 1 (auth/me) Hash: {hash1}")

# Request 2: /api/notifications/
response2 = client.get("/api/notifications/")
hash2 = response2.headers.get("X-User-Permissions-Hash")
print(f"Response 2 (notifications) Hash: {hash2}")

# Request 3: /api/users
response3 = client.get("/api/users")
hash3 = response3.headers.get("X-User-Permissions-Hash")
print(f"Response 3 (users) Hash: {hash3}")

print(f"All hashes match expected: {hash1 == expected_hash and hash2 == expected_hash and hash3 == expected_hash}")
