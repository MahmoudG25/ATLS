import os
import django
import sys
from django.db import transaction
from django.utils import timezone

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from apps.reports.models import DailyTaskReport, OperationLog, LaborEntry
from services.reports_service import sync_operation_log

def backfill(dry_run=True):
    print(f"=== Operational Backfill Script ({'DRY RUN' if dry_run else 'LIVE EXECUTION'}) ===")
    
    reports = DailyTaskReport.objects.all().order_by('id')
    stats = {
        "processed": 0,
        "orphans_fixed": 0,
        "mismatches_detected": 0,
        "mismatches_fixed": 0,
        "skipped": 0,
        "errors": 0
    }

    try:
        with transaction.atomic():
            for report in reports:
                stats["processed"] += 1
                logs = report.operation_logs.filter(is_deleted=False)
                
                # 1. Handle Orphans
                if logs.count() == 0:
                    if report.operation_id:
                        print(f"[ORPHAN] Report {report.id} has no logs. Syncing from legacy fields...")
                        if not dry_run:
                            sync_operation_log(report)
                        stats["orphans_fixed"] += 1
                    else:
                        print(f"[SKIP] Report {report.id} has no operation selected and no logs. Skipping.")
                        stats["skipped"] += 1
                        continue

                # 2. Handle Location Mismatches
                # Refresh logs after possible sync
                logs = report.operation_logs.filter(is_deleted=False)
                for log in logs:
                    if log.location_id != report.location_id:
                        stats["mismatches_detected"] += 1
                        print(f"[MISMATCH] Log {log.id} (Loc: {log.location_id}) != Report {report.id} (Loc: {report.location_id})")
                        
                        # Fix: Update log location to match report enclosure
                        if not dry_run:
                            old_loc = log.location_id
                            log.location_id = report.location_id
                            log.save(update_fields=['location'])
                            print(f"   -> FIXED: Log {log.id} location updated {old_loc} -> {log.location_id}")
                            stats["mismatches_fixed"] += 1

            if dry_run:
                print("\n[DRY RUN] Rolling back changes...")
                transaction.set_rollback(True)
            else:
                print("\n[LIVE] Committing changes...")

    except Exception as e:
        print(f"\n[ERROR] Script failed: {e}")
        stats["errors"] += 1
        raise

    print("\n=== Final Report ===")
    for key, val in stats.items():
        print(f"{key.replace('_', ' ').title()}: {val}")

if __name__ == "__main__":
    is_dry = "--live" not in sys.argv
    backfill(dry_run=is_dry)
    if is_dry:
        print("\nNOTE: Run with '--live' to apply changes.")
