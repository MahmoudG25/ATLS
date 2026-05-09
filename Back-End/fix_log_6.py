import os
import django
import sys
from django.db import transaction

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from apps.reports.models import DailyTaskReport, OperationLog

def fix_deterministic():
    print("=== Execution: Deterministic Repair ===")
    try:
        with transaction.atomic():
            # Log 6 fix
            r = DailyTaskReport.objects.get(id=12)
            log = OperationLog.objects.get(id=6)
            print(f"Repairing Report 12: Changing location {r.location_id} -> {log.location_id}")
            r.location_id = log.location_id
            r.save()
            print("Successfully updated Report 12.")
            
    except Exception as e:
        print(f"Failed to repair: {e}")
        raise

if __name__ == "__main__":
    fix_deterministic()
