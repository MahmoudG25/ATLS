import os
import sys
import django

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from apps.reports.models import OperationLog

print("Operation Name | Source Type | Count | Sum of Productivity | Unique Units")
print("-" * 80)
from django.db.models import Count, Sum

logs = OperationLog.objects.values(
    'operation__name', 'source_type', 'unit__name'
).annotate(
    cnt=Count('id'),
    total_prod=Sum('actual_productivity')
).order_by('-cnt')

for log in logs:
    print(f"{log['operation__name']} | {log['source_type']} | {log['cnt']} | {log['total_prod']} | {log['unit__name']}")
