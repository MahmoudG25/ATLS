from rest_framework import serializers
from apps.equipment.models import Equipment, Maintenance, Usage, OilChangeLog, EquipmentLog, FleetMaintenanceAlert


class EquipmentSerializer(serializers.ModelSerializer):
    equipment_type_display = serializers.CharField(read_only=True)
    meter_delta = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    requires_maintenance = serializers.BooleanField(read_only=True)
    last_operation_date = serializers.DateField(read_only=True)

    class Meta:
        model = Equipment
        fields = "__all__"
        read_only_fields = ["company"]


class MaintenanceSerializer(serializers.ModelSerializer):
    equipment_name = serializers.CharField(source="equipment.name", read_only=True)

    class Meta:
        model = Maintenance
        fields = "__all__"
        read_only_fields = ["company"]


class UsageSerializer(serializers.ModelSerializer):
    equipment_name = serializers.CharField(source="equipment.name", read_only=True)

    class Meta:
        model = Usage
        fields = "__all__"
        read_only_fields = ["company"]


class OilChangeLogSerializer(serializers.ModelSerializer):
    equipment_name = serializers.CharField(source="equipment.name", read_only=True)

    class Meta:
        model = OilChangeLog
        fields = "__all__"
        read_only_fields = ["company"]


class EquipmentLogSerializer(serializers.ModelSerializer):
    equipment_name = serializers.CharField(source="equipment.name", read_only=True)
    log_type_display = serializers.CharField(read_only=True)
    operator_name = serializers.CharField(read_only=True)

    class Meta:
        model = EquipmentLog
        fields = "__all__"
        read_only_fields = ["company"]


class FleetMaintenanceAlertSerializer(serializers.ModelSerializer):
    equipment_name = serializers.CharField(source="equipment.name", read_only=True)
    meter_type = serializers.CharField(source="equipment.meter_type", read_only=True)

    class Meta:
        model = FleetMaintenanceAlert
        fields = "__all__"
        read_only_fields = ["company"]

