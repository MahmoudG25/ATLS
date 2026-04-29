from rest_framework import serializers
from apps.reports.models import (
    Operation, Variety, Unit, Contractor, DailyTaskReport, FertilizationReport, IrrigationReport,
    CustomFieldDefinition, CustomFieldValue, ReportDropdownOption, LaborEntry, Attachment
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
        LocationNode.objects.filter(parent=node, is_active=True).order_by('order', 'name')
    )
    for child in children:
        result = _resolve_enclosure(child)
        if result:
            return result
    return None


class OperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operation
        fields = '__all__'

class VarietySerializer(serializers.ModelSerializer):
    class Meta:
        model = Variety
        fields = '__all__'
        read_only_fields = ['company']

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = '__all__'
        read_only_fields = ['company']

class ReportDropdownOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportDropdownOption
        fields = '__all__'
        read_only_fields = ['company']

class DailyTaskReportSerializer(serializers.ModelSerializer):
    engineer_name = serializers.CharField(source='engineer.name', read_only=True)
    operation_name = serializers.CharField(source='operation.name', read_only=True)
    variety_name = serializers.CharField(source='variety.name', read_only=True)
    unit_name = serializers.CharField(source='unit.name', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True)
    location_type = serializers.CharField(source='location.type', read_only=True)
    location_path = serializers.SerializerMethodField()
    attachments_count = serializers.IntegerField(source='attachments.count', read_only=True)
    labor_count = serializers.IntegerField(source='labor_entries.count', read_only=True)
    contractor_name = serializers.SerializerMethodField()
    # work_location is a deprecated legacy field — stored as empty string, hidden from all responses
    work_location = serializers.CharField(
        required=False, default='', allow_blank=True, write_only=True
    )

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
        fields = '__all__'
        read_only_fields = ['company']

    def validate(self, data):
        request = self.context.get("request")
        company = getattr(request, "company", None) if request else None
        location   = data.get('location')
        operation  = data.get('operation')
        variety    = data.get('variety')
        contractor = data.get('contractor')
        unit       = data.get('unit')
        engineer   = data.get('engineer')  # User FK instance

        # location is always required
        if not location:
            raise serializers.ValidationError({"location": "الموقع مطلوب."})

        # CRITICAL RULE: Normalize to ENCLOSURE
        resolved_node = _resolve_enclosure(location)
        if not resolved_node:
            raise serializers.ValidationError({"location": f"الموقع المختار ({location.name}) لا يحتوي على أي حوشة فعالة للتقرير عليها."})
        
        # Update the data dictionary so it saves the ENCLOSURE ID
        data['location'] = resolved_node

        if company:
            # Validate tenant isolation for the resolved enclosure and other FKs
            tenant_checks = [
                (data['location'], "location",  "الموقع لا ينتمي لهذه الشركة"),
                (operation,        "operation", "العملية لا تنتمي لهذه الشركة"),
                (variety,          "variety",   "الصنف لا ينتمي لهذه الشركة"),
                (unit,             "unit",      "الوحدة لا ينتمي لهذه الشركة"),
            ]
            for obj, field_name, msg in tenant_checks:
                if obj and getattr(obj, 'company_id', None) != company.id:
                    raise serializers.ValidationError({field_name: msg})

            # Contractor is optional but must belong to same company if provided
            if contractor and getattr(contractor, 'company_id', None) != company.id:
                raise serializers.ValidationError({"contractor": "المقاول لا ينتمي لهذه الشركة"})

            # Engineer must belong to the same company (prevents cross-company assignment)
            if engineer and getattr(engineer, 'company_id', None) != company.id:
                raise serializers.ValidationError({"engineer": "المهندس لا ينتمي لنفس الشركة"})

        return data


class FertilizationReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = FertilizationReport
        fields = '__all__'

class IrrigationReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = IrrigationReport
        fields = '__all__'

class CustomFieldDefinitionSerializer(serializers.ModelSerializer):
    applies_to_model = serializers.CharField(source='applies_to.model', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = CustomFieldDefinition
        fields = '__all__'
        read_only_fields = ['created_by']

class CustomFieldValueSerializer(serializers.ModelSerializer):
    field_name = serializers.CharField(source='field.name', read_only=True)
    field_type = serializers.CharField(source='field.field_type', read_only=True)

    class Meta:
        model = CustomFieldValue
        fields = '__all__'


class LaborEntrySerializer(serializers.ModelSerializer):
    contractor_name = serializers.CharField(source='contractor.name', read_only=True)
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
