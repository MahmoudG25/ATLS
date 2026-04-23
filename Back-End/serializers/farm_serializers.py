from rest_framework import serializers
from apps.farm.models import Farm, CropType, Sector, Plot

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
