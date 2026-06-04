import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from apps.users.models import FarmSystemConfig, Company

# Check database query
try:
    count = FarmSystemConfig.objects.count()
    print(f"Success! FarmSystemConfig table is accessible. Current config count: {count}")
    
    # Try fetching columns
    fields = [field.name for field in FarmSystemConfig._meta.get_fields()]
    print("Available fields in FarmSystemConfig:")
    for f in fields:
        print(f" - {f}")
except Exception as e:
    print(f"Error querying table: {e}")
