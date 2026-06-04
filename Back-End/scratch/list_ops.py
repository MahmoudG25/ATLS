import os
import sys
import django

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from apps.reports.models import Operation

print("ID | Name | Category | Profile Type | Active")
print("-" * 60)
for op in Operation.objects.all().order_by('category', 'name'):
    print(f"{op.id} | {op.name} | {op.category} | {op.profile_type} | {op.is_active}")
