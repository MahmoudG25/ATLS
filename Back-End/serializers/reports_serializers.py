from rest_framework import serializers
from apps.reports.models import (
    Operation, DailyTaskReport, FertilizationReport, IrrigationReport,
    CustomFieldDefinition, CustomFieldValue, ReportDropdownOption
)

class OperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operation
        fields = '__all__'

class ReportDropdownOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportDropdownOption
        fields = '__all__'

class DailyTaskReportSerializer(serializers.ModelSerializer):
    engineer_name = serializers.CharField(source='engineer.username', read_only=True)
    operation_name = serializers.CharField(source='operation.name', read_only=True)
    sector_name = serializers.CharField(source='sector.name', read_only=True)
    variety_name = serializers.CharField(source='variety.name', read_only=True)
    unit_name = serializers.CharField(source='unit.name', read_only=True)
    contractor_name = serializers.CharField(source='contractor.name', read_only=True)
    enclosure_name = serializers.CharField(source='enclosure.name', read_only=True)

    class Meta:
        model = DailyTaskReport
        fields = '__all__'

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
