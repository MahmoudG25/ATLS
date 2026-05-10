import uuid
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.production.models import HarvestReport, SortingReport
from apps.reports.models import OperationLog, Operation
from apps.farm.models import EnclosureProfile


class ProductionWorkflowService:
    """Base service for production workflows with state management and auditing."""

    @staticmethod
    def validate_transition(report, new_status):
        """Enforces strict workflow state transitions."""
        allowed_transitions = {
            HarvestReport.STATE_DRAFT: [HarvestReport.STATE_SUBMITTED],
            HarvestReport.STATE_SUBMITTED: [HarvestReport.STATE_APPROVED, HarvestReport.STATE_DRAFT],
            HarvestReport.STATE_APPROVED: [HarvestReport.STATE_FINALIZED],
            HarvestReport.STATE_FINALIZED: [],  # Immutable
        }
        
        # Sorting states (simplified for now but following same logic)
        sorting_allowed = {
            SortingReport.STATE_DRAFT: [SortingReport.STATE_SUBMITTED],
            SortingReport.STATE_SUBMITTED: [SortingReport.STATE_FINALIZED, SortingReport.STATE_DRAFT],
            SortingReport.STATE_FINALIZED: [],
        }

        current_status = report.status
        
        if isinstance(report, HarvestReport):
            valid_next = allowed_transitions.get(current_status, [])
        else:
            valid_next = sorting_allowed.get(current_status, [])

        if new_status not in valid_next and current_status != new_status:
            raise ValidationError(
                f"Invalid transition from {current_status} to {new_status}."
            )

    @staticmethod
    def _create_operation_log(report, operation_type_slug, season, parent_log=None):
        """Generates a domain-agnostic OperationLog entry for the report."""
        try:
            operation = Operation.objects.get(slug=operation_type_slug, company=report.company)
        except Operation.DoesNotExist:
            # Fallback to system operation if available, or fail
            operation = Operation.objects.filter(slug="generic", company=report.company).first()
            if not operation:
                return None

        # Determine source metadata
        source_type = OperationLog.SOURCE_HARVEST if isinstance(report, HarvestReport) else OperationLog.SOURCE_SORTING
        
        # Use a consistent chain_id across related operations
        chain_id = getattr(report, "chain_id", uuid.uuid4())
        if not chain_id:
            chain_id = uuid.uuid4()

        log = OperationLog.objects.create(
            company=report.company,
            location=report.location if hasattr(report, "location") else report.harvest_report.location,
            operation=operation,
            season=season,
            source_type=source_type,
            source_id=report.id,
            parent_log=parent_log,
            chain_id=chain_id,
            variety=getattr(report, "variety", None),
            unit=getattr(report, "unit", None),
            actual_productivity=getattr(report, "quantity", 0) if isinstance(report, HarvestReport) else getattr(report, "final_quantity", 0),
            work_hours=getattr(report, "labor_hours", 0),
            status="COMPLETED"
        )
        return log


class HarvestWorkflowService(ProductionWorkflowService):
    """Orchestrates the Harvest lifecycle."""

    @classmethod
    @transaction.atomic
    def submit_report(cls, report_id):
        report = HarvestReport.objects.select_for_update().get(id=report_id)
        
        if report.status != HarvestReport.STATE_DRAFT:
            raise ValidationError("Only draft reports can be submitted.")

        # Capture snapshots
        report.variety_name_snapshot = report.variety.name if report.variety else ""
        report.unit_label_snapshot = report.unit.name if report.unit else ""
        
        report.status = HarvestReport.STATE_SUBMITTED
        report.save()
        return report

    @classmethod
    @transaction.atomic
    def finalize_report(cls, report_id, user):
        report = HarvestReport.objects.select_for_update().get(id=report_id)
        cls.validate_transition(report, HarvestReport.STATE_FINALIZED)

        # 1. Generate OperationLog for History
        cls._create_operation_log(report, "harvest", report.season)

        # 2. Update Enclosure Snapshot
        profile, _ = EnclosureProfile.objects.get_or_create(
            location_node=report.location,
            company=report.company
        )
        # Simple accumulation for actual yield in current season
        # (This is a simplified snapshot update; real analytics will derive from logs)
        if profile.actual_yield is None:
            profile.actual_yield = 0
        profile.actual_yield += report.quantity
        profile.save()

        report.status = HarvestReport.STATE_FINALIZED
        report.save()
        return report


class SortingWorkflowService(ProductionWorkflowService):
    """Orchestrates the Sorting lifecycle."""

    @classmethod
    def validate_quantities(cls, report):
        """Ensures Sorted + Rejected + Waste <= Incoming."""
        total_out = report.final_quantity + report.rejected_quantity + report.waste_quantity
        if total_out > report.incoming_quantity:
            raise ValidationError(
                f"Output quantity ({total_out}) exceeds incoming quantity ({report.incoming_quantity})."
            )

    @classmethod
    @transaction.atomic
    def finalize_report(cls, report_id, user):
        report = SortingReport.objects.select_for_update().get(id=report_id)
        cls.validate_transition(report, SortingReport.STATE_FINALIZED)
        cls.validate_quantities(report)

        # Find parent harvest log for lineage
        parent_log = OperationLog.objects.filter(
            source_type=OperationLog.SOURCE_HARVEST,
            source_id=report.harvest_report_id
        ).first()

        # 1. Generate OperationLog with Lineage
        cls._create_operation_log(report, "sorting", report.harvest_report.season, parent_log=parent_log)

        report.status = SortingReport.STATE_FINALIZED
        report.save()
        return report
