import os
import sys
import django

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.reports.selectors import get_location_analytics
from apps.farm.models import LocationNode
from apps.reports.models import OperationLog
from apps.production.models import HarvestReport

for node in LocationNode.objects.filter(type='STAGE'):
    analytics = get_location_analytics(node)
    descendants = node.get_descendants(include_self=True)
    logs_count = OperationLog.objects.filter(location__in=descendants).count()
    hr_count = HarvestReport.objects.filter(location__in=descendants).count()
    
    print(f"Stage ID: {node.id}")
    print(f"  Logs Count: {logs_count}")
    print(f"  Harvest Reports Count: {hr_count}")
    print(f"  Analytics Summary: {analytics['summary']}")
