from apps.reports.models import DailyTaskReport, OperationLog


def list_reports(engineer_id=None, location_id=None):
    qs = (
        DailyTaskReport.objects.select_related("engineer", "location")
        .all()
        .order_by("-report_date")
    )
    if engineer_id:
        qs = qs.filter(engineer_id=engineer_id)
    if location_id:
        qs = qs.filter(location_id=location_id)
    return qs


def create_report(user, data):
    data["engineer"] = user
    data["company"] = getattr(user, "company", None)
    return DailyTaskReport.objects.create(**data)


# -----------------------------------------------------------------------------
# Phase 2: Dual-Write Synchronization Bridge
# -----------------------------------------------------------------------------

def sync_operation_log(report_instance):
    """
    Phase 2 Dual-Write Bridge: Explicitly sync DailyTaskReport fields to a 1:1 OperationLog.
    This ensures all existing APIs continue to function normally while populating the new schema.
    """
    from apps.reports.models import Season
    report_date = report_instance.report_date
    season = None
    if report_date:
        season = Season.objects.filter(
            company_id=report_instance.company_id,
            start_date__lte=report_date,
            end_date__gte=report_date
        ).first()
    if not season:
        season = Season.objects.filter(company_id=report_instance.company_id, status="OPEN").first()

    op_log, created = OperationLog.objects.update_or_create(
        report=report_instance,
        defaults={
            "company_id": report_instance.company_id,
            "location_id": report_instance.location_id,
            "operation_id": report_instance.operation_id,
            "variety_id": report_instance.variety_id,
            "unit_id": report_instance.unit_id,
            "contractor_id": report_instance.contractor_id,
            "company_workers": report_instance.company_workers,
            "contractor_workers": report_instance.contractor_workers,
            "actual_productivity": report_instance.actual_productivity,
            "work_hours": report_instance.work_hours,
            "overtime_hours": report_instance.overtime_hours,
            "overtime_productivity": report_instance.overtime_productivity,
            "season": season,
        }
    )
    return op_log


def sync_child_operation_log(child_instance):
    """Ensure LaborEntry or Attachment gets attached to the OperationLog bridge if missing."""
    if child_instance.report_id and not child_instance.operation_log_id:
        op_log = OperationLog.objects.filter(report_id=child_instance.report_id).first()
        if op_log:
            child_instance.operation_log = op_log
            child_instance.save(update_fields=["operation_log"])
