from rest_framework import serializers
from apps.reports.models import (
    Operation, Variety, Unit, Contractor, DailyTaskReport, FertilizationReport, IrrigationReport,
    CustomFieldDefinition, CustomFieldValue, ReportDropdownOption, LaborEntry, Attachment
)

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

    def validate(self, data):
        request = self.context.get("request")
        company = getattr(request, "company", None) if request else None
        variety = data.get('variety')
        contractor = data.get('contractor')
        unit = data.get('unit')
        location = data.get('location')
        operation = data.get('operation')

        if company:
            if location and location.company_id != company.id:
                raise serializers.ValidationError({"location": "Invalid tenant relation"})
            if operation and operation.company_id != company.id:
                raise serializers.ValidationError({"operation": "Invalid tenant relation"})
            if variety and variety.company_id != company.id:
                raise serializers.ValidationError({"variety": "Invalid tenant relation"})
            if contractor and contractor.company_id != company.id:
                raise serializers.ValidationError({"contractor": "Invalid tenant relation"})
            if unit and unit.company_id != company.id:
                raise serializers.ValidationError({"unit": "Invalid tenant relation"})

        if not location:
            raise serializers.ValidationError({"location": "Location is required."})

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
