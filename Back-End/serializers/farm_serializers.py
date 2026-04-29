from rest_framework import serializers
from apps.farm.models import Farm, CropType, Sector, Plot, LocationNode, FarmSettings

class FarmSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FarmSettings
        fields = [
            'enable_sector', 'enable_stage', 'enable_enclosure',
            'allow_stage_without_sector', 'allow_enclosure_without_stage'
        ]

class FarmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farm
        fields = '__all__'

class CropTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CropType
        fields = '__all__'

class PlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plot
        fields = '__all__'

class SectorSerializer(serializers.ModelSerializer):
    plots = PlotSerializer(many=True, read_only=True)
    crop_type_name = serializers.CharField(source='crop_type.name', read_only=True)

    class Meta:
        model = Sector
        fields = ['id', 'name', 'farm', 'crop_type', 'crop_type_name', 'plots']


# ── LocationNode Serializers (new hierarchy system) ───────────────────────────

class LocationNodeSerializer(serializers.ModelSerializer):
    """Full read serializer — includes parent name and child count."""
    parent_name = serializers.CharField(source='parent.name', read_only=True, default=None)

    class Meta:
        model = LocationNode
        fields = ['id', 'name', 'type', 'parent', 'parent_id', 'parent_name', 'order', 'is_active', 'farm']
        read_only_fields = ['farm']


class LocationNodeCreateSerializer(serializers.ModelSerializer):
    """
    Write serializer for creating/updating LocationNodes.
    Enforces flexible hierarchy and 3-level depth limit.
    """

    class Meta:
        model = LocationNode
        fields = ['name', 'type', 'parent', 'order']

    def validate(self, data):
        parent = data.get('parent')
        node_type = data.get('type')

        if parent:
            # 1. Parent-Child Type Integrity
            if parent.type == LocationNode.TYPE_ENCLOSURE:
                raise serializers.ValidationError({'parent': 'لا يمكن إضافة عناصر تابعة للحوشة.'})

            if parent.type == LocationNode.TYPE_STAGE and node_type not in [LocationNode.TYPE_STAGE, LocationNode.TYPE_ENCLOSURE]:
                raise serializers.ValidationError({'type': 'المرحلة يمكن أن تحتوي على مراحل أو حوشات فقط.'})

            if parent.type == LocationNode.TYPE_SECTOR and node_type not in [LocationNode.TYPE_STAGE, LocationNode.TYPE_ENCLOSURE]:
                raise serializers.ValidationError({'type': 'القطاع يمكن أن يحتوي على مراحل أو حوشات فقط.'})

            # 2. Depth Control: Max 3 levels
            # parent.level is 0-indexed. If parent.level is 2, child would be level 3 (4th level).
            if parent.level >= 2:
                raise serializers.ValidationError({'parent': 'تم الوصول للحد الأقصى لعمق الهيكل (3 مستويات).'})

        return data


