import os
import django
import sys

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from apps.reports.models import DailyTaskReport, OperationLog, LaborEntry
from django.db.models import Count

def verify():
    print("=== Operational Integrity Verification ===")
    
    # 1. Total Counts
    total_reports = DailyTaskReport.objects.count()
    total_logs = OperationLog.objects.count()
    print(f"Total Reports: {total_reports}")
    print(f"Total Operation Logs: {total_logs}")
    
    # 2. Orphaned Reports (Reports without any OperationLog)
    orphaned_reports = DailyTaskReport.objects.annotate(log_count=Count('operation_logs')).filter(log_count=0)
    print(f"Orphaned Reports (0 logs): {orphaned_reports.count()}")
    if orphaned_reports.count() > 0:
        for r in orphaned_reports[:5]:
            print(f"  - Report ID: {r.id}, Date: {r.report_date}, Location: {r.location}")
            
    # 3. Mismatched Locations
    # Check if any OperationLog has a different location than its parent report (for single-op reports)
    mismatched = OperationLog.objects.exclude(location=django.db.models.F('report__location'))
    print(f"Mismatched Locations (Log vs Report): {mismatched.count()}")
    
    # 4. Labor Entry Linkage
    # Every LaborEntry should be linked to an OperationLog
    unlinked_labor = LaborEntry.objects.filter(operation_log__isnull=True)
    print(f"Unlinked Labor Entries: {unlinked_labor.count()}")
    
    # 5. Null Checks on critical fields
    null_op = OperationLog.objects.filter(operation__isnull=True).count()
    null_loc = OperationLog.objects.filter(location__isnull=True).count()
    print(f"Logs with Null Operation: {null_op}")
    print(f"Logs with Null Location: {null_loc}")
    
    # 6. Tenant Consistency
    tenant_mismatch = OperationLog.objects.exclude(company=django.db.models.F('report__company')).count()
    print(f"Tenant Mismatches (Log vs Report): {tenant_mismatch}")

    print("\n=== Summary ===")
    if orphaned_reports.count() == 0 and unlinked_labor.count() == 0:
        print("STATUS: GREEN (Integrity OK)")
    else:
        print("STATUS: RED (Action Required)")

if __name__ == "__main__":
    verify()
