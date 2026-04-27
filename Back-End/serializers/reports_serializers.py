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
    crop_name = serializers.CharField(source='crop.name', read_only=True)
    stage_name = serializers.CharField(source='stage.name', read_only=True)
    variety_name = serializers.CharField(source='variety.name', read_only=True)
    unit_name = serializers.CharField(source='unit.name', read_only=True)
    contractor_name = serializers.SerializerMethodField()
    enclosure_name = serializers.SerializerMethodField()

    def get_contractor_name(self, obj):
        return obj.contractor.name if obj.contractor else None

    def get_enclosure_name(self, obj):
        if obj.enclosure:
            if obj.enclosure.stage:
                return f"{obj.enclosure.crop.name} / {obj.enclosure.stage.name} / {obj.enclosure.name}"
            return f"{obj.enclosure.crop.name} / {obj.enclosure.name}"
        return None

    class Meta:
        model = DailyTaskReport
        fields = '__all__'

    def validate(self, data):
        crop = data.get('crop')
        stage = data.get('stage')
        enclosure = data.get('enclosure')

        if not crop:
            raise serializers.ValidationError({"crop": "المحصول مطلوب."})
        
        if not enclosure:
            raise serializers.ValidationError({"enclosure": "الحوشة / المنطقة مطلوبة."})

        if crop.type == 'palm':
            if not stage:
                raise serializers.ValidationError({"stage": "المرحلة مطلوبة لنخيل."})
            # Ensure enclosure belongs to the stage
            if enclosure.stage != stage:
                raise serializers.ValidationError({"enclosure": "الحوشة المختارة لا تنتمي للمرحلة المحددة."})
        elif crop.type == 'olive':
            if stage:
                raise serializers.ValidationError({"stage": "الزيتون لا يحتوي على مراحل."})
            # Ensure enclosure belongs to the crop
            if enclosure.crop != crop:
                raise serializers.ValidationError({"enclosure": "المنطقة المختارة لا تنتمي لمحصول الزيتون."})

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
