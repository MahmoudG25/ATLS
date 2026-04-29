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
    Enforces nesting rules:
      • SECTOR  → must have no parent (root level)
      • STAGE   → parent must be SECTOR
      • ENCLOSURE → parent must be SECTOR or STAGE (not another ENCLOSURE)
    """

    class Meta:
        model = LocationNode
        fields = ['name', 'type', 'parent', 'order']

    def validate(self, data):
        node_type = data.get('type')
        parent    = data.get('parent')

        if node_type == LocationNode.TYPE_SECTOR:
            if parent is not None:
                raise serializers.ValidationError({'parent': 'القطاع يجب أن يكون على مستوى المزرعة ولا يكون تابعاً لأي عنصر.'})

        elif node_type == LocationNode.TYPE_STAGE:
            # Stage can be at farm root (parent=None) OR under a Sector
            if parent is not None and parent.type != LocationNode.TYPE_SECTOR:
                raise serializers.ValidationError({'parent': 'المرحلة يمكن إضافتها فقط تحت قطاع أو مباشرة تحت المزرعة.'})

        elif node_type == LocationNode.TYPE_ENCLOSURE:
            if parent is None:
                raise serializers.ValidationError({'parent': 'الحوشة يجب أن تكون تابعة لقطاع أو مرحلة.'})
            if parent.type == LocationNode.TYPE_ENCLOSURE:
                raise serializers.ValidationError({'parent': 'الحوشة لا يمكن إضافتها تحت حوشة أخرى.'})

        return data

