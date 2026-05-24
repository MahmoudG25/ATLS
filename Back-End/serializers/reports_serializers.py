from rest_framework import serializers
from apps.reports.models import (
    Operation,
    Variety,
    Unit,
    ApplicationMethod,
    Contractor,
    DailyTaskReport,
    FertilizationReport,
    IrrigationReport,
    CustomFieldDefinition,
    CustomFieldValue,
    ReportDropdownOption,
    LaborEntry,
    Attachment,
    OperationLog,
    Season,
    GalleryMedia,
)
from apps.farm.models import LocationNode, FarmSettings


# ΓöÇΓöÇΓöÇ Helper: normalize any selected node ΓåÆ ENCLOSURE ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
def _resolve_enclosure(node):
    """
    CRITICAL RULE: location must always be stored as an ENCLOSURE node.
    If the user selected a SECTOR or STAGE, recursively search children
    for the first active ENCLOSURE. Returns the ENCLOSURE node or None.
    """
    if node.type == LocationNode.TYPE_ENCLOSURE:
        return node
    # BFS over active children
    children = list(
        LocationNode.objects.filter(parent=node, is_active=True).order_by(
            "order", "name"
        )
    )
    for child in children:
        result = _resolve_enclosure(child)
        if result:
            return result
    return None


class OperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operation
        fields = "__all__"
        read_only_fields = ["company"]

    def validate(self, attrs):
        # Restrict changing system operations structure
        if self.instance and self.instance.is_system:
            if "slug" in attrs and attrs["slug"] != self.instance.slug:
                raise serializers.ValidationError({"slug": "┘ä╪º ┘è┘à┘â┘å ╪¬╪║┘è┘è╪▒ ╪º┘ä┘à╪╣╪▒┘ü (slug) ┘ä╪╣┘à┘ä┘è╪⌐ ╪ú╪│╪º╪│┘è╪⌐ ┘ü┘è ╪º┘ä┘å╪╕╪º┘à."})
            if "profile_type" in attrs and attrs["profile_type"] != self.instance.profile_type:
                raise serializers.ValidationError({"profile_type": "┘ä╪º ┘è┘à┘â┘å ╪¬╪║┘è┘è╪▒ ┘å┘ê╪╣ ╪º┘ä┘é╪º┘ä╪¿ (profile_type) ┘ä╪╣┘à┘ä┘è╪⌐ ╪ú╪│╪º╪│┘è╪⌐ ┘ü┘è ╪º┘ä┘å╪╕╪º┘à."})
        return super().validate(attrs)


class VarietySerializer(serializers.ModelSerializer):
    class Meta:
        model = Variety
        fields = "__all__"
        read_only_fields = ["company"]


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = "__all__"
        read_only_fields = ["company"]


class OperationLogSerializer(serializers.ModelSerializer):
    operation_name = serializers.CharField(source="operation.name", read_only=True)
    location_name = serializers.CharField(source="location.name", read_only=True)
    location_path = serializers.SerializerMethodField()
    variety_name = serializers.CharField(source="variety.name", read_only=True)
    unit_name = serializers.CharField(source="unit.name", read_only=True)
    contractor_name = serializers.SerializerMethodField()
    contractors = serializers.PrimaryKeyRelatedField(many=True, queryset=Contractor.objects.all(), required=False)

    class Meta:
        model = OperationLog
        fields = "__all__"
        read_only_fields = ["company", "report"]

    def get_contractor_name(self, obj):
        names = [c.name for c in obj.contractors.all()]
        if names:
            return " + ".join(names)
        return obj.contractor.name if obj.contractor else None

    def get_location_path(self, obj):
        node = obj.location
        if not node:
            return None
        parts = [node.name]
        while node.parent_id:
            node = node.parent
            parts.append(node.name)
        return " / ".join(reversed(parts))

    def validate(self, attrs):
        # 1. Fetch operation to get its schema
        operation = attrs.get("operation")
        profile_data = attrs.get("profile_data", {})

        # 2. Dynamic Schema Validation (JSON Schema Governance)
        if operation:
            from apps.reports.services import validate_operation_profile
            from django.core.exceptions import ValidationError as DjangoValidationError
            try:
                validate_operation_profile(operation, profile_data)
            except DjangoValidationError as e:
                raise serializers.ValidationError({"profile_data": e.message})

        return attrs




class ContractorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contractor
        fields = "__all__"
        read_only_fields = ["company"]


class ReportDropdownOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportDropdownOption
        fields = "__all__"
        read_only_fields = ["company"]


class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = "__all__"
        read_only_fields = ["company"]


from django.db import transaction
from django.utils import timezone


class AttachmentSerializer(serializers.ModelSerializer):
    report_title = serializers.SerializerMethodField()
    engineer_name = serializers.SerializerMethodField()
    location_name = serializers.SerializerMethodField()

    class Meta:
        model = Attachment
        fields = "__all__"
        read_only_fields = ["company"]


    def get_report_title(self, obj):
        if obj.report:
            op_name = obj.report.operation.name if obj.report.operation else "بدون عملية"
            loc_name = obj.report.location.name if obj.report.location else ""
            date_str = obj.report.report_date.strftime("%Y-%m-%d") if obj.report.report_date else ""
            return f"{op_name} - {loc_name} ({date_str})".strip(" - ")
        return None

    def get_engineer_name(self, obj):
        if obj.report and obj.report.engineer:
            return obj.report.engineer.name
        return None

    def get_location_name(self, obj):
        if obj.report and obj.report.location:
            return obj.report.location.name
        return None

    def to_internal_value(self, data):
        data = data.copy() if hasattr(data, "copy") else dict(data)
        if "url" in data and "file_url" not in data:
            data["file_url"] = data["url"]
        if "type" in data and "file_type" not in data:
            data["file_type"] = data["type"]
        return super().to_internal_value(data)

    def to_representation(self, instance):
        import mimetypes
        url = instance.file_url or ""
        file_type = instance.file_type or "FILE"
        
        thumbnail_url = url
        if file_type == "IMAGE" and "cloudinary.com" in url:
            thumbnail_url = url.replace("/upload/", "/upload/c_thumb,w_200/")
            
        filename = url.split('/')[-1] if url else ""
        mime, _ = mimetypes.guess_type(filename)
        if not mime:
            if file_type == "IMAGE":
                mime = "image/jpeg"
            elif file_type == "VIDEO":
                mime = "video/mp4"
            else:
                mime = "application/octet-stream"
                
        uploaded_by_name = None
        if hasattr(instance, "report") and instance.report:
            if hasattr(instance.report, "engineer") and instance.report.engineer:
                uploaded_by_name = instance.report.engineer.name or instance.report.engineer.username
            elif hasattr(instance.report, "supervisor") and instance.report.supervisor:
                uploaded_by_name = instance.report.supervisor.name or instance.report.supervisor.username
            elif hasattr(instance.report, "created_by") and instance.report.created_by:
                uploaded_by_name = instance.report.created_by.name or instance.report.created_by.username

        rep = {
            "id": instance.id,
            "type": file_type,
            "url": url,
            "thumbnail_url": thumbnail_url,
            "mime_type": mime,
            "file_name": filename or "attachment",
            "file_size": None,
            "source": "daily_task",
            "uploaded_by": uploaded_by_name,
            "created_at": instance.uploaded_at.isoformat() if instance.uploaded_at else None,
            "file_url": url,
            "file_type": file_type,
            "uploaded_at": instance.uploaded_at.isoformat() if instance.uploaded_at else None,
            "report_title": self.get_report_title(instance),
            "engineer_name": self.get_engineer_name(instance),
            "location_name": self.get_location_name(instance),
            "report": instance.report_id,
        }
        return rep


class LaborEntrySerializer(serializers.ModelSerializer):
    contractor_name = serializers.CharField(source="contractor.name", read_only=True)
    line_cost = serializers.SerializerMethodField()

    def get_line_cost(self, obj):
        return (obj.hours + obj.overtime) * obj.worker_rate

    class Meta:
        model = LaborEntry
        fields = "__all__"


class DailyTaskReportListSerializer(serializers.ModelSerializer):
    engineer_name = serializers.CharField(source="engineer.name", read_only=True)
    operation_name = serializers.CharField(source="operation.name", read_only=True)
    variety_name = serializers.CharField(source="variety.name", read_only=True)
    unit_name = serializers.CharField(source="unit.name", read_only=True)
    location_name = serializers.CharField(source="location.name", read_only=True)
    location_type = serializers.CharField(source="location.type", read_only=True)
    location_path = serializers.SerializerMethodField()
    attachments_count = serializers.IntegerField(
        source="attachments.count", read_only=True
    )
    labor_count = serializers.IntegerField(source="labor_entries.count", read_only=True)
    contractor_name = serializers.SerializerMethodField()
    contractors = serializers.PrimaryKeyRelatedField(many=True, queryset=Contractor.objects.all(), required=False)
    work_location_name = serializers.CharField(
        source="work_location.name", read_only=True
    )
    operation_summary = serializers.SerializerMethodField()
    available_actions = serializers.SerializerMethodField()
    attachments = AttachmentSerializer(many=True, read_only=True)
    operation_logs = serializers.SerializerMethodField()
    # Computed aggregated metrics from operation_logs (fallback from direct report fields)
    company_workers = serializers.SerializerMethodField()
    contractor_workers = serializers.SerializerMethodField()
    actual_productivity = serializers.SerializerMethodField()

    class Meta:
        model = DailyTaskReport
        fields = [
            "id", "report_date", "status", "engineer", "engineer_name",
            "operation", "operation_name", "operation_summary",
            "variety", "variety_name", "unit", "unit_name",
            "location", "location_name", "location_type", "location_path",
            "attachments_count", "labor_count", "contractor", "contractor_name",
            "contractors", "work_location", "work_location_name", "available_actions",
            "created_at", "updated_at",
            "company_workers", "contractor_workers", "actual_productivity",
            "attachments", "operation_logs"
        ]

    def _get_active_logs(self, obj):
        """Return active (non-deleted) operation logs, cached per object."""
        return obj.operation_logs.filter(is_deleted=False)

    def get_company_workers(self, obj):
        """Aggregate company_workers from operation_logs; fall back to report field."""
        direct = obj.company_workers or 0
        logs = self._get_active_logs(obj)
        if logs.exists():
            from django.db.models import Sum
            agg = logs.aggregate(total=Sum("company_workers"))["total"] or 0
            return agg if agg > 0 else direct
        return direct

    def get_contractor_workers(self, obj):
        """Aggregate contractor_workers from operation_logs; fall back to report field."""
        direct = obj.contractor_workers or 0
        logs = self._get_active_logs(obj)
        if logs.exists():
            from django.db.models import Sum
            agg = logs.aggregate(total=Sum("contractor_workers"))["total"] or 0
            return agg if agg > 0 else direct
        return direct

    def get_actual_productivity(self, obj):
        """Aggregate actual_productivity from operation_logs; fall back to report field."""
        direct = obj.actual_productivity
        logs = self._get_active_logs(obj)
        if logs.exists():
            from django.db.models import Sum
            agg = logs.aggregate(total=Sum("actual_productivity"))["total"]
            if agg is not None and agg > 0:
                return agg
        return direct

    def get_location_path(self, obj):
        node = obj.location
        if not node:
            return None
        parts = [node.name]
        while node.parent_id:
            node = node.parent
            parts.append(node.name)
        return " / ".join(reversed(parts))

    def get_operation_summary(self, obj):
        logs = self._get_active_logs(obj)
        if not logs.exists():
            return obj.operation.name if obj.operation else "بدون عمليات"
        op_names = []
        for log in logs:
            if log.operation and log.operation.name not in op_names:
                op_names.append(log.operation.name)
        if not op_names:
            return obj.operation.name if obj.operation else "بدون عمليات"
        return " + ".join(op_names)

    def get_available_actions(self, obj):
        request = self.context.get("request")
        if not request:
            return []
        user = request.user
        user_role = getattr(user, "role", "ENGINEER")
        is_manager = user_role in ["MANAGER", "SUPER_ADMIN", "OWNER"]
        
        actions = []
        if obj.status in ["draft", "rejected"]:
            if obj.engineer == user or is_manager:
                actions.append("submit")
        
        if is_manager:
            if obj.status == "submitted":
                actions.append("review")
            if obj.status in ["submitted", "under_review"]:
                actions.append("approve")
                actions.append("reject")
        
        return actions

    def get_contractor_name(self, obj):
        names = [c.name for c in obj.contractors.all()]
        if names:
            return " + ".join(names)
        return obj.contractor.name if obj.contractor else None

    def get_operation_logs(self, obj):
        logs = obj.operation_logs.filter(is_deleted=False).order_by('sequence')
        return OperationLogSerializer(logs, many=True, context=self.context).data


class DailyTaskReportSerializer(serializers.ModelSerializer):

    engineer_name = serializers.CharField(source="engineer.name", read_only=True)
    operation_name = serializers.CharField(source="operation.name", read_only=True)
    variety_name = serializers.CharField(source="variety.name", read_only=True)
    unit_name = serializers.CharField(source="unit.name", read_only=True)
    location_name = serializers.CharField(source="location.name", read_only=True)
    location_type = serializers.CharField(source="location.type", read_only=True)
    location_path = serializers.SerializerMethodField()
    attachments_count = serializers.IntegerField(
        source="attachments.count", read_only=True
    )
    labor_count = serializers.IntegerField(source="labor_entries.count", read_only=True)
    contractor_name = serializers.SerializerMethodField()
    contractors = serializers.PrimaryKeyRelatedField(many=True, queryset=Contractor.objects.all(), required=False)
    work_location_name = serializers.CharField(
        source="work_location.name", read_only=True
    )
    location_path = serializers.SerializerMethodField()
    operation_summary = serializers.SerializerMethodField()
    available_actions = serializers.SerializerMethodField()
    operation_logs = serializers.SerializerMethodField()
    labor_entries = LaborEntrySerializer(many=True, read_only=True)
    operations = serializers.ListField(child=serializers.DictField(), write_only=True, required=False)
    attachments = serializers.SerializerMethodField()

    def get_attachments(self, obj):
        try:
            qs = obj.attachments.all()
            return AttachmentSerializer(qs, many=True, context=self.context).data
        except Exception as exc:
            import logging
            logging.getLogger(__name__).error(
                "get_attachments failed for DailyTaskReport pk=%s: %s", obj.pk, exc, exc_info=True
            )
            return []


    def get_location_path(self, obj):
        node = obj.location
        if not node:
            return None
        parts = [node.name]
        while node.parent_id:
            node = node.parent
            parts.append(node.name)
        return " / ".join(reversed(parts))


    def get_operation_summary(self, obj):
        logs = obj.operation_logs.filter(is_deleted=False)
        if not logs:
            return obj.operation.name if obj.operation else "╪¿╪»┘ê┘å ╪╣┘à┘ä┘è╪º╪¬"
        # Gather unique operation names keeping sequence order mostly
        op_names = []
        for log in logs:
            if log.operation and log.operation.name not in op_names:
                op_names.append(log.operation.name)
        if not op_names:
            return obj.operation.name if obj.operation else "╪¿╪»┘ê┘å ╪╣┘à┘ä┘è╪º╪¬"
        return " + ".join(op_names)

    def get_available_actions(self, obj):
        request = self.context.get("request")
        if not request:
            return []
        user = request.user
        user_role = getattr(user, "role", "ENGINEER")
        is_manager = user_role in ["MANAGER", "SUPER_ADMIN", "OWNER"]
        
        actions = []
        if obj.status in ["draft", "rejected"]:
            if obj.engineer == user or is_manager:
                actions.append("submit")
        
        if is_manager:
            if obj.status == "submitted":
                actions.append("review")
            if obj.status in ["submitted", "under_review"]:
                actions.append("approve")
                actions.append("reject")
        
        return actions

    def get_contractor_name(self, obj):
        names = [c.name for c in obj.contractors.all()]
        if names:
            return " + ".join(names)
        return obj.contractor.name if obj.contractor else None

    def get_operation_logs(self, obj):
        logs = obj.operation_logs.filter(is_deleted=False).order_by('sequence')
        return OperationLogSerializer(logs, many=True, context=self.context).data

    def get_location_path(self, obj):
        node = obj.location
        if not node:
            return None
        parts = [node.name]
        while node.parent_id:
            node = node.parent
            parts.append(node.name)
        return " / ".join(reversed(parts))

    class Meta:
        model = DailyTaskReport
        fields = "__all__"
        read_only_fields = [
            "company", "status", "rejection_reason", 
            "override_by", "override_at", "was_overridden", 
            "is_deleted", "deleted_at", "deleted_by",
            "created_at", "updated_at", "submitted_at", "approved_at", "rejected_at"
        ]

    def validate(self, data):
        request = self.context.get("request")
        company = getattr(request, "company", None) if request else None
        location = data.get("location")
        operation = data.get("operation")
        variety = data.get("variety")
        contractor = data.get("contractor")
        unit = data.get("unit")
        engineer = data.get("engineer")  # User FK instance

        # location is always required
        if not location:
            raise serializers.ValidationError({"location": "╪º┘ä┘à┘ê┘é╪╣ ┘à╪╖┘ä┘ê╪¿."})

        if location.type not in [LocationNode.TYPE_ENCLOSURE, LocationNode.TYPE_STAGE, LocationNode.TYPE_SECTOR]:
            raise serializers.ValidationError({"location": "Invalid location type"})
        data["location"] = location

        if company:
            # Validate tenant isolation for the resolved enclosure and other FKs
            tenant_checks = [
                (data["location"], "location", "╪º┘ä┘à┘ê┘é╪╣ ┘ä╪º ┘è┘å╪¬┘à┘è ┘ä┘ç╪░┘ç ╪º┘ä╪┤╪▒┘â╪⌐"),
                (
                    data.get("work_location"),
                    "work_location",
                    "┘à┘â╪º┘å ╪º┘ä╪╣┘à┘ä ┘ä╪º ┘è┘å╪¬┘à┘è ┘ä┘ç╪░┘ç ╪º┘ä╪┤╪▒┘â╪⌐",
                ),
                (operation, "operation", "╪º┘ä╪╣┘à┘ä┘è╪⌐ ┘ä╪º ╪¬┘å╪¬┘à┘è ┘ä┘ç╪░┘ç ╪º┘ä╪┤╪▒┘â╪⌐"),
                (variety, "variety", "╪º┘ä╪╡┘å┘ü ┘ä╪º ┘è┘å╪¬┘à┘è ┘ä┘ç╪░┘ç ╪º┘ä╪┤╪▒┘â╪⌐"),
                (unit, "unit", "╪º┘ä┘ê╪¡╪»╪⌐ ┘ä╪º ┘è┘å╪¬┘à┘è ┘ä┘ç╪░┘ç ╪º┘ä╪┤╪▒┘â╪⌐"),
            ]
            for obj, field_name, msg in tenant_checks:
                if obj and getattr(obj, "company_id", None) != company.id:
                    raise serializers.ValidationError({field_name: msg})

            # Contractor is optional but must belong to same company if provided
            if contractor and getattr(contractor, "company_id", None) != company.id:
                raise serializers.ValidationError(
                    {"contractor": "╪º┘ä┘à┘é╪º┘ê┘ä ┘ä╪º ┘è┘å╪¬┘à┘è ┘ä┘ç╪░┘ç ╪º┘ä╪┤╪▒┘â╪⌐"}
                )

            # Engineer must belong to the same company (prevents cross-company assignment)
            if engineer and getattr(engineer, "company_id", None) != company.id:
                raise serializers.ValidationError(
                    {"engineer": "╪º┘ä┘à┘ç┘å╪»╪│ ┘ä╪º ┘è┘å╪¬┘à┘è ┘ä┘å┘ü╪│ ╪º┘ä╪┤╪▒┘â╪⌐"}
                )

        return data

    @transaction.atomic
    def create(self, validated_data):
        operations_data = validated_data.pop("operations", [])
        contractors_data = validated_data.pop("contractors", None)
        
        # Set legacy contractor to the first one for backwards compatibility
        if contractors_data:
            validated_data["contractor"] = contractors_data[0]
            
        report = super().create(validated_data)
        
        if contractors_data is not None:
            report.contractors.set(contractors_data)
        
        # Unified Pipeline
        if operations_data:
            self._sync_operations(report, operations_data)
        elif validated_data.get("operation"):
            from services.reports_service import sync_operation_log
            sync_operation_log(report)
            
        return report

    @transaction.atomic
    def update(self, instance, validated_data):
        operations_data = validated_data.pop("operations", None)
        contractors_data = validated_data.pop("contractors", None)
        
        if contractors_data is not None:
            if contractors_data:
                validated_data["contractor"] = contractors_data[0]
            else:
                validated_data["contractor"] = None
                
        report = super().update(instance, validated_data)
        
        if contractors_data is not None:
            report.contractors.set(contractors_data)
            
        if operations_data is not None:
            self._sync_operations(report, operations_data)
        elif report.operation_id:
            from services.reports_service import sync_operation_log
            sync_operation_log(report)
            
        return report

    def _sync_operations(self, report, operations_data):
        """
        Synchronizes incoming operations with OperationLog model.
        Supports Expansion: STAGE/SECTOR -> Multiple ENCLOSURE events.
        """
        import uuid
        from apps.farm.models import LocationNode
        from django.utils import timezone

        existing_logs = {log.id: log for log in report.operation_logs.filter(is_deleted=False)}
        seen_ids = set()
        seen_bulk_ids = set()
        
        request = self.context.get("request")
        user = request.user if request else None

        for seq, op_data in enumerate(operations_data):
            op_id = op_data.get("id")
            bulk_id = op_data.get("bulk_operation_id")
            
            # 1. Resolve Location & Determine Scope
            loc_id = op_data.get("location")
            if not loc_id:
                continue
                
            loc_node = LocationNode.objects.filter(id=loc_id).first()
            if not loc_node:
                continue

            # Determine Target Enclosures
            if loc_node.type == LocationNode.TYPE_ENCLOSURE:
                targets = [loc_node]
            else:
                # Expansion Logic: Get all active descendant enclosures
                targets = list(loc_node.get_descendants().filter(type=LocationNode.TYPE_ENCLOSURE, is_active=True))
            
            if not targets:
                continue

            # 2. Update or Create
            if op_id and op_id in existing_logs:
                # Individual Update
                log = existing_logs[op_id]
                contractors_data = op_data.get("contractors", [])
                self._apply_op_data(log, op_data, seq)
                # Set contractors
                log.contractors.set(contractors_data)
                # Legacy compatibility: set single contractor to the first selected
                if contractors_data:
                    log.contractor_id = contractors_data[0]
                else:
                    log.contractor_id = None
                log.save()
                
                # Sync nested labor entries
                self._sync_labor_entries(log, op_data.get("labor_entries", []), report)
                seen_ids.add(op_id)
            elif bulk_id:
                # Bulk Update: Update all logs belonging to this bulk group
                bulk_logs = report.operation_logs.filter(bulk_operation_id=bulk_id, is_deleted=False)
                contractors_data = op_data.get("contractors", [])
                for log in bulk_logs:
                    self._apply_op_data(log, op_data, seq)
                    # Set contractors
                    log.contractors.set(contractors_data)
                    # Legacy compatibility: set single contractor to the first selected
                    if contractors_data:
                        log.contractor_id = contractors_data[0]
                    else:
                        log.contractor_id = None
                    log.save()
                    
                    self._sync_labor_entries(log, op_data.get("labor_entries", []), report)
                    seen_ids.add(log.id)
                seen_bulk_ids.add(bulk_id)
            else:
                # NEW Operation (could be single or bulk)
                new_bulk_id = uuid.uuid4() if len(targets) > 1 else None
                for target in targets:
                    clean_data, labor_entries_data, contractors_data = self._prepare_clean_data(op_data, report, target, seq)
                    clean_data["bulk_operation_id"] = new_bulk_id
                    new_log = OperationLog.objects.create(**clean_data)
                    # Set many-to-many contractors
                    if contractors_data:
                        new_log.contractors.set(contractors_data)
                    # Create nested labor entries after the log is saved
                    self._create_labor_entries(new_log, labor_entries_data, report)
                    seen_ids.add(new_log.id)

        # 3. Soft-delete removed operations
        for old_id, old_log in existing_logs.items():
            if old_id not in seen_ids:
                old_log.is_deleted = True
                old_log.deleted_at = timezone.now()
                old_log.deleted_by = user
                old_log.save(update_fields=["is_deleted", "deleted_at", "deleted_by"])

    # Reverse-relation / M2M fields that must NOT be passed to create()
    REVERSE_FIELDS = {"labor_entries", "attachments", "custom_field_values", "operation_logs"}

    def _prepare_clean_data(self, op_data, report, location_node, sequence):
        """Return (clean_data_dict, labor_entries_list, contractors_list) – reverse relations are stripped out."""
        labor_entries_data = op_data.get("labor_entries", [])
        contractors_data = op_data.get("contractors", [])

        clean_data = {
            k: v for k, v in op_data.items()
            if k not in {"id", "temp_id", "bulk_operation_id", "location", "contractors"} | self.REVERSE_FIELDS
        }

        # Convert FK primitives (int or UUID string) to _id fields so Django doesn't
        # try to assign a raw string/int as a model instance.
        for fk in ["operation", "variety", "unit", "contractor"]:
            if fk in clean_data and not hasattr(clean_data[fk], 'pk'):
                val = clean_data.pop(fk)
                if val is not None:
                    clean_data[f"{fk}_id"] = val

        clean_data["location"] = location_node
        clean_data["report"] = report
        clean_data["company_id"] = report.company_id
        clean_data["sequence"] = sequence

        # Set legacy contractor field
        if contractors_data:
            clean_data["contractor_id"] = contractors_data[0]
        else:
            clean_data["contractor_id"] = None

        return clean_data, labor_entries_data, contractors_data

    def _create_labor_entries(self, log, labor_entries_data, report):
        """Create LaborEntry rows linked to a freshly-created OperationLog."""
        if not labor_entries_data:
            return
        from apps.reports.models import LaborEntry
        for entry in labor_entries_data:
            if not isinstance(entry, dict):
                continue
            contractor_id = entry.get("contractor")
            if hasattr(contractor_id, 'pk'):
                contractor_id = contractor_id.pk
            LaborEntry.objects.create(
                report=report,
                operation_log=log,
                company=report.company,
                worker_name=entry.get("worker_name", ""),
                worker_type=entry.get("worker_type", "COMPANY"),
                contractor_id=contractor_id,
                worker_rate=entry.get("worker_rate", 0),
                hours=entry.get("hours", 0),
                overtime=entry.get("overtime", 0),
                note=entry.get("note", ""),
            )

    def _sync_labor_entries(self, log, labor_entries_data, report):
        """Sync labor entries for an existing OperationLog (create, update, delete)."""
        from apps.reports.models import LaborEntry
        
        # Get existing active labor entries for this log
        existing_entries = {entry.id: entry for entry in log.labor_entries.all()}
        seen_ids = set()
        
        for entry_data in labor_entries_data:
            if not isinstance(entry_data, dict):
                continue
            
            entry_id = entry_data.get("id")
            contractor_id = entry_data.get("contractor")
            if hasattr(contractor_id, 'pk'):
                contractor_id = contractor_id.pk
                
            clean_fields = {
                "worker_name": entry_data.get("worker_name", ""),
                "worker_type": entry_data.get("worker_type", "COMPANY"),
                "contractor_id": contractor_id,
                "worker_rate": entry_data.get("worker_rate", 0),
                "hours": entry_data.get("hours", 0),
                "overtime": entry_data.get("overtime", 0),
                "note": entry_data.get("note", ""),
            }
            
            if entry_id and entry_id in existing_entries:
                # Update existing
                entry_obj = existing_entries[entry_id]
                for k, v in clean_fields.items():
                    setattr(entry_obj, k, v)
                entry_obj.save()
                seen_ids.add(entry_id)
            else:
                # Create new
                new_entry = LaborEntry.objects.create(
                    report=report,
                    operation_log=log,
                    company=report.company,
                    **clean_fields
                )
                seen_ids.add(new_entry.id)
                
        # Delete removed entries
        for old_id, old_entry in existing_entries.items():
            if old_id not in seen_ids:
                old_entry.delete()

    def _apply_op_data(self, log, op_data, sequence):
        for key, value in op_data.items():
            if key in {"id", "temp_id", "bulk_operation_id", "location", "contractors"} | self.REVERSE_FIELDS:
                continue
            if not hasattr(log, key):
                continue
            # Convert FK primitives
            if key in ["operation", "variety", "unit", "contractor"] and not hasattr(value, 'pk'):
                if value is not None:
                    setattr(log, f"{key}_id", value)
            else:
                setattr(log, key, value)
        log.sequence = sequence
        log.save()


class FertilizationReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = FertilizationReport
        fields = "__all__"


class IrrigationReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = IrrigationReport
        fields = "__all__"


class CustomFieldDefinitionSerializer(serializers.ModelSerializer):
    applies_to_model = serializers.CharField(source="applies_to.model", read_only=True)
    created_by_name = serializers.CharField(
        source="created_by.username", read_only=True
    )

    class Meta:
        model = CustomFieldDefinition
        fields = "__all__"
        read_only_fields = ["created_by"]


class CustomFieldValueSerializer(serializers.ModelSerializer):
    field_name = serializers.CharField(source="field.name", read_only=True)
    field_type = serializers.CharField(source="field.field_type", read_only=True)

    class Meta:
        model = CustomFieldValue
        fields = "__all__"


class OperationLogTimelineSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for the Enclosure Timeline feed.
    Includes full operation metadata and summary metrics.
    """
    operation_name = serializers.CharField(source="operation.name", read_only=True)
    operation_category = serializers.CharField(source="operation.category", read_only=True)
    ui_schema = serializers.JSONField(source="operation.ui_schema", read_only=True)
    engineer_name = serializers.SerializerMethodField()
    report_date = serializers.SerializerMethodField()
    
    metrics = serializers.SerializerMethodField()
    attachments_count = serializers.SerializerMethodField()
    attachments = serializers.SerializerMethodField()
    labor_entries = LaborEntrySerializer(many=True, read_only=True)
    report_status = serializers.SerializerMethodField()
    execution_status = serializers.CharField(source="status", read_only=True)

    location_name = serializers.CharField(source="location.name", read_only=True)
    unit_name = serializers.CharField(source="unit.name", read_only=True)
    variety_name = serializers.CharField(source="variety.name", read_only=True)
    contractor_name = serializers.SerializerMethodField()
    contractors = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = OperationLog
        fields = [
            "id", "operation_name", "operation_category", "ui_schema",
            "engineer_name", "report_date", "profile_type", "profile_version", 
            "profile_data", "metrics", "attachments_count", "attachments", "created_at",
            "labor_entries", "report_status", "execution_status", "status",
            "source_type", "source_id", "report_id",
            "company_workers", "contractor_workers", "actual_productivity", "work_hours",
            "overtime_hours", "overtime_productivity", "location_name", "unit_name",
            "variety_name", "contractor_name", "contractors"
        ]

    def get_contractor_name(self, obj):
        names = [c.name for c in obj.contractors.all()]
        if names:
            return " + ".join(names)
        return obj.contractor.name if obj.contractor else None

    def get_engineer_name(self, obj):
        if obj.source_type == "HARVEST":
            from apps.production.models import HarvestReport
            report = HarvestReport.objects.filter(id=obj.source_id).first()
            if report:
                user = report.supervisor or report.created_by
                if user:
                    return user.name or user.username or user.email
        elif obj.source_type == "SORTING":
            from apps.production.models import SortingReport
            report = SortingReport.objects.filter(id=obj.source_id).first()
            if report and report.harvest_report:
                user = report.harvest_report.supervisor or report.harvest_report.created_by
                if user:
                    return user.name or user.username or user.email
        # Default fallback to obj.report (DAILY_TASK)
        if obj.report and obj.report.engineer:
            return obj.report.engineer.name or obj.report.engineer.username
        return None

    def get_report_date(self, obj):
        if obj.source_type == "HARVEST":
            from apps.production.models import HarvestReport
            report = HarvestReport.objects.filter(id=obj.source_id).first()
            if report:
                return report.harvest_date
        elif obj.source_type == "SORTING":
            from apps.production.models import SortingReport
            report = SortingReport.objects.filter(id=obj.source_id).first()
            if report:
                return report.processing_date
        if obj.report:
            return obj.report.report_date
        return None

    def get_report_status(self, obj):
        if obj.source_type == "HARVEST":
            from apps.production.models import HarvestReport
            report = HarvestReport.objects.filter(id=obj.source_id).first()
            if report:
                return report.status
        elif obj.source_type == "SORTING":
            from apps.production.models import SortingReport
            report = SortingReport.objects.filter(id=obj.source_id).first()
            if report:
                return report.status
        if obj.report:
            return obj.report.status
        return None

    def get_metrics(self, obj):
        # Calculate summary metrics for this specific log entry with safety defaults
        labor = obj.labor_entries.all()
        total_cost = sum(
            ((l.hours or 0) + (l.overtime or 0)) * (l.worker_rate or 0) 
            for l in labor
        )
        return {
            "total_cost": float(total_cost),
            "total_hours": float(sum(l.hours or 0 for l in labor)),
            "worker_count": labor.count() or ((obj.company_workers or 0) + (obj.contractor_workers or 0))
        }

    def get_attachments_count(self, obj):
        return len(self.get_attachments(obj))

    def get_attachments(self, obj):
        attachments_data = []
        # 1. Direct log attachments
        log_atts = obj.attachments.all()
        log_atts_serialized = AttachmentSerializer(log_atts, many=True).data
        
        # 2. Source/Report-level attachments
        source_atts_serialized = []
        if obj.source_type == "HARVEST":
            from apps.production.models import HarvestAttachment
            from apps.production.serializers import HarvestAttachmentSerializer
            harvest_atts = HarvestAttachment.objects.filter(report_id=obj.source_id)
            source_atts_serialized = HarvestAttachmentSerializer(harvest_atts, many=True).data
        elif obj.report:
            # Daily task report level attachments
            report_atts = obj.report.attachments.all()
            source_atts_serialized = AttachmentSerializer(report_atts, many=True).data
            
        # Merge them based on unique URL to avoid duplicates.
        seen_urls = set()
        merged = []
        for att in log_atts_serialized:
            url = att.get("url") or att.get("file_url")
            if url and url not in seen_urls:
                seen_urls.add(url)
                merged.append(att)
        for att in source_atts_serialized:
            url = att.get("url") or att.get("file_url")
            if url and url not in seen_urls:
                seen_urls.add(url)
                merged.append(att)
                
        # Sort merged attachments by created_at descending if present
        def parse_date(date_str):
            if not date_str:
                return timezone.now()
            from django.utils.dateparse import parse_datetime
            parsed = parse_datetime(date_str)
            return parsed if parsed else timezone.now()
            
        merged.sort(key=lambda x: parse_date(x.get("created_at")), reverse=True)
        return merged


class GalleryMediaSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source="uploaded_by.name", read_only=True)

    class Meta:
        model = GalleryMedia
        fields = ["id", "file_url", "file_type", "uploaded_at", "uploaded_by_name"]
        read_only_fields = ["id", "uploaded_at"]

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['uploaded_by'] = user
        company = getattr(user, 'company', None)
        if not company:
            from apps.users.models import Company
            company = Company.objects.first()
        validated_data['company'] = company
        return super().create(validated_data)

    def to_internal_value(self, data):
        data = data.copy() if hasattr(data, "copy") else dict(data)
        if "url" in data and "file_url" not in data:
            data["file_url"] = data["url"]
        if "type" in data and "file_type" not in data:
            data["file_type"] = data["type"]
        return super().to_internal_value(data)

    def to_representation(self, instance):
        import mimetypes
        url = instance.file_url or ""
        file_type = instance.file_type or "FILE"
        
        thumbnail_url = url
        if file_type == "IMAGE" and "cloudinary.com" in url:
            thumbnail_url = url.replace("/upload/", "/upload/c_thumb,w_200/")
            
        filename = url.split('/')[-1] if url else ""
        mime, _ = mimetypes.guess_type(filename)
        if not mime:
            if file_type == "IMAGE":
                mime = "image/jpeg"
            elif file_type == "VIDEO":
                mime = "video/mp4"
            else:
                mime = "application/octet-stream"
                
        uploaded_by_name = instance.uploaded_by.name or instance.uploaded_by.username if instance.uploaded_by else None

        rep = {
            "id": instance.id,
            "type": file_type,
            "url": url,
            "thumbnail_url": thumbnail_url,
            "mime_type": mime,
            "file_name": filename or "gallery_media",
            "file_size": None,
            "source": "gallery",
            "uploaded_by": uploaded_by_name,
            "created_at": instance.uploaded_at.isoformat() if instance.uploaded_at else None,
            "file_url": url,
            "file_type": file_type,
            "uploaded_at": instance.uploaded_at.isoformat() if instance.uploaded_at else None,
            "uploaded_by_name": uploaded_by_name,
        }
        return rep
# ============================================================================
# ANALYTICS SERIALIZERS
# ============================================================================


class KPIDashboardSerializer(serializers.Serializer):
    """KPI Dashboard metrics serializer"""

    class PeriodSerializer(serializers.Serializer):
        start_date = serializers.DateField(allow_null=True)
        end_date = serializers.DateField(allow_null=True)

    class SummarySerializer(serializers.Serializer):
        total_reports = serializers.IntegerField()
        total_workers = serializers.IntegerField()
        company_workers = serializers.IntegerField()
        contractor_workers = serializers.IntegerField()
        avg_workers_per_report = serializers.FloatField()

    class OperationsSerializer(serializers.Serializer):
        total_unique_operations = serializers.IntegerField()
        total_operation_records = serializers.IntegerField()
        avg_productivity = serializers.FloatField()

    period = PeriodSerializer()
    summary = SummarySerializer()
    operations = OperationsSerializer()


class ProductivityMetricSerializer(serializers.Serializer):
    """Individual productivity metric"""

    operation__id = serializers.IntegerField(required=False, allow_null=True)
    operation__name = serializers.CharField(required=False, allow_null=True)
    location__id = serializers.IntegerField(required=False, allow_null=True)
    location__name = serializers.CharField(required=False, allow_null=True)
    location__type = serializers.CharField(required=False, allow_null=True)
    location__farm__id = serializers.IntegerField(required=False, allow_null=True)
    location__farm__name = serializers.CharField(required=False, allow_null=True)
    report_date = serializers.DateField(required=False, allow_null=True)
    total_productivity = serializers.IntegerField()
    avg_productivity = serializers.FloatField()
    count_reports = serializers.IntegerField()
    min_productivity = serializers.IntegerField(required=False, allow_null=True)
    max_productivity = serializers.IntegerField(required=False, allow_null=True)


class ProductivityAnalyticsSerializer(serializers.Serializer):
    """Productivity analytics grouped by operation, location, and date"""

    by_operation = ProductivityMetricSerializer(many=True)
    by_location = ProductivityMetricSerializer(many=True)
    by_date = ProductivityMetricSerializer(many=True)


class OperationDetailSerializer(serializers.Serializer):
    """Operation summary detail"""

    operation__id = serializers.IntegerField()
    operation__name = serializers.CharField()
    operation__category = serializers.CharField()
    total_reports = serializers.IntegerField()
    total_company_workers = serializers.IntegerField()
    total_contractor_workers = serializers.IntegerField()
    total_workers = serializers.IntegerField()
    total_work_hours = serializers.FloatField()
    avg_work_hours = serializers.FloatField()
    total_productivity = serializers.IntegerField()
    avg_productivity = serializers.FloatField()
    unique_engineers = serializers.IntegerField()
    unique_locations = serializers.IntegerField()


class OperationsSummarySerializer(serializers.Serializer):
    """Operations summary"""

    total_operations = serializers.IntegerField()
    operations = OperationDetailSerializer(many=True)


class LocationWorkerSerializer(serializers.Serializer):
    """Worker distribution by location"""

    location__id = serializers.IntegerField()
    location__name = serializers.CharField()
    location__type = serializers.CharField()
    location__farm__id = serializers.IntegerField()
    location__farm__name = serializers.CharField()
    total_company_workers = serializers.IntegerField()
    total_contractor_workers = serializers.IntegerField()
    total_workers = serializers.IntegerField()
    total_reports = serializers.IntegerField()
    unique_engineers = serializers.IntegerField()
    unique_operations = serializers.IntegerField()


class WorkersByLocationSerializer(serializers.Serializer):
    """Workers by location distribution"""

    total_locations = serializers.IntegerField()
    locations = LocationWorkerSerializer(many=True)


class OperationLocationMatrixItemSerializer(serializers.Serializer):
    """Operation-Location cross-tabulation item"""

    operation__id = serializers.IntegerField()
    operation__name = serializers.CharField()
    location__id = serializers.IntegerField()
    location__name = serializers.CharField()
    location__type = serializers.CharField()
    total_workers = serializers.IntegerField()
    company_workers = serializers.IntegerField()
    contractor_workers = serializers.IntegerField()
    total_reports = serializers.IntegerField()


class OperationLocationMatrixSerializer(serializers.Serializer):
    """Operation-Location cross-tabulation"""

    matrix = OperationLocationMatrixItemSerializer(many=True)

class ApplicationMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationMethod
        fields = "__all__"
        read_only_fields = ["company"]
