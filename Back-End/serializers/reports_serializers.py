from rest_framework import serializers
from apps.reports.models import (
    Operation,
    Variety,
    Unit,
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
)
from apps.farm.models import LocationNode, FarmSettings


# ─── Helper: normalize any selected node → ENCLOSURE ────────────────────────
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
                raise serializers.ValidationError({"slug": "لا يمكن تغيير المعرف (slug) لعملية أساسية في النظام."})
            if "profile_type" in attrs and attrs["profile_type"] != self.instance.profile_type:
                raise serializers.ValidationError({"profile_type": "لا يمكن تغيير نوع القالب (profile_type) لعملية أساسية في النظام."})
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
    contractor_name = serializers.CharField(source="contractor.name", read_only=True)

    class Meta:
        model = OperationLog
        fields = "__all__"
        read_only_fields = ["company", "report"]

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
        profile_type = attrs.get("profile_type", "generic")
        profile_data = attrs.get("profile_data", {})
        
        if profile_type == "irrigation":
            required_keys = ["water_quantity", "irrigation_duration"]
            for key in required_keys:
                if key not in profile_data or profile_data[key] in [None, ""]:
                    raise serializers.ValidationError({"profile_data": f"Field '{key}' is required for irrigation."})
            try:
                float(profile_data["water_quantity"])
                float(profile_data["irrigation_duration"])
            except ValueError:
                raise serializers.ValidationError({"profile_data": "Irrigation fields must be numeric."})
                
        elif profile_type == "fertilization":
            required_keys = ["fertilizer_material", "fertilizer_dosage"]
            for key in required_keys:
                if key not in profile_data or profile_data[key] in [None, ""]:
                    raise serializers.ValidationError({"profile_data": f"Field '{key}' is required for fertilization."})
            try:
                float(profile_data["fertilizer_dosage"])
            except ValueError:
                raise serializers.ValidationError({"profile_data": "Dosage must be numeric."})

        elif profile_type == "spraying":
            required_keys = ["pesticide_material"]
            for key in required_keys:
                if key not in profile_data or profile_data[key] in [None, ""]:
                    raise serializers.ValidationError({"profile_data": f"Field '{key}' is required for spraying."})

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
    work_location_name = serializers.CharField(
        source="work_location.name", read_only=True
    )
    location_path = serializers.SerializerMethodField()
    operation_summary = serializers.SerializerMethodField()
    available_actions = serializers.SerializerMethodField()
    operation_logs = OperationLogSerializer(many=True, read_only=True)
    operations = serializers.ListField(child=serializers.DictField(), write_only=True, required=False)

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
        logs = obj.operation_logs.all()
        if not logs:
            return obj.operation.name if obj.operation else "بدون عمليات"
        # Gather unique operation names keeping sequence order mostly
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
            raise serializers.ValidationError({"location": "الموقع مطلوب."})

        # CRITICAL RULE: Normalize to ENCLOSURE
        resolved_node = _resolve_enclosure(location)
        if not resolved_node:
            raise serializers.ValidationError(
                {
                    "location": f"الموقع المختار ({location.name}) لا يحتوي على أي حوشة فعالة للتقرير عليها."
                }
            )

        # Update the data dictionary so it saves the ENCLOSURE ID
        data["location"] = resolved_node

        if company:
            # Validate tenant isolation for the resolved enclosure and other FKs
            tenant_checks = [
                (data["location"], "location", "الموقع لا ينتمي لهذه الشركة"),
                (
                    data.get("work_location"),
                    "work_location",
                    "مكان العمل لا ينتمي لهذه الشركة",
                ),
                (operation, "operation", "العملية لا تنتمي لهذه الشركة"),
                (variety, "variety", "الصنف لا ينتمي لهذه الشركة"),
                (unit, "unit", "الوحدة لا ينتمي لهذه الشركة"),
            ]
            for obj, field_name, msg in tenant_checks:
                if obj and getattr(obj, "company_id", None) != company.id:
                    raise serializers.ValidationError({field_name: msg})

            # Contractor is optional but must belong to same company if provided
            if contractor and getattr(contractor, "company_id", None) != company.id:
                raise serializers.ValidationError(
                    {"contractor": "المقاول لا ينتمي لهذه الشركة"}
                )

            # Engineer must belong to the same company (prevents cross-company assignment)
            if engineer and getattr(engineer, "company_id", None) != company.id:
                raise serializers.ValidationError(
                    {"engineer": "المهندس لا ينتمي لنفس الشركة"}
                )

        return data

    def create(self, validated_data):
        operations_data = validated_data.pop("operations", [])
        report = super().create(validated_data)
        if operations_data:
            self._sync_operations(report, operations_data)
        else:
            # Fallback for old API clients: Phase 2 bridge logic
            from services.reports_service import sync_operation_log
            sync_operation_log(report)
        return report

    def update(self, instance, validated_data):
        operations_data = validated_data.pop("operations", None)
        report = super().update(instance, validated_data)
        if operations_data is not None:
            self._sync_operations(report, operations_data)
        else:
            # Fallback for old API clients
            from services.reports_service import sync_operation_log
            sync_operation_log(report)
        return report

    def _sync_operations(self, report, operations_data):
        """
        Synchronizes the incoming operations array with the OperationLog model.
        Preserves ordering, handles creates, updates, and deletes.
        """
        existing_logs = {log.id: log for log in report.operation_logs.all()}
        seen_ids = set()

        for seq, op_data in enumerate(operations_data):
            op_id = op_data.get("id")
            
            # Resolve the enclosure location for this specific operation
            loc = op_data.get("location")
            if loc:
                from apps.farm.models import LocationNode
                if isinstance(loc, int):
                    loc_node = LocationNode.objects.filter(id=loc).first()
                    if loc_node:
                        op_data["location"] = _resolve_enclosure(loc_node) or loc_node

            if op_id and op_id in existing_logs:
                # Update existing
                log = existing_logs[op_id]
                for key, value in op_data.items():
                    if key not in ["id", "temp_id"] and hasattr(log, key):
                        # Ensure FKs are assigned correctly if they are IDs
                        if key in ["location", "operation", "variety", "unit", "contractor"] and isinstance(value, int):
                            setattr(log, f"{key}_id", value)
                        else:
                            setattr(log, key, value)
                log.sequence = seq
                log.save()
                seen_ids.add(op_id)
            else:
                # Create new
                # Remove non-model fields
                clean_data = {k: v for k, v in op_data.items() if k not in ["id", "temp_id"]}
                
                # Convert FK integers to _id fields
                for fk in ["location", "operation", "variety", "unit", "contractor"]:
                    if fk in clean_data and isinstance(clean_data[fk], int):
                        val = clean_data.pop(fk)
                        clean_data[f"{fk}_id"] = val
                        
                clean_data["report"] = report
                clean_data["company_id"] = report.company_id
                clean_data["sequence"] = seq
                OperationLog.objects.create(**clean_data)

        # Delete operations that were removed
        for old_id, old_log in existing_logs.items():
            if old_id not in seen_ids:
                old_log.delete()


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


class LaborEntrySerializer(serializers.ModelSerializer):
    contractor_name = serializers.CharField(source="contractor.name", read_only=True)
    line_cost = serializers.SerializerMethodField()

    def get_line_cost(self, obj):
        return (obj.hours + obj.overtime) * obj.worker_rate

    class Meta:
        model = LaborEntry
        fields = "__all__"


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = "__all__"


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
