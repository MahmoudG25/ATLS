from rest_framework import serializers
from apps.equipment.models import Equipment, Maintenance, Usage, OilChangeLog


class EquipmentSerializer(serializers.ModelSerializer):
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
