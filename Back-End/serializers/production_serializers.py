from rest_framework import serializers
from apps.production.models import AnnualYield

class AnnualYieldSerializer(serializers.ModelSerializer):
    plot_name = serializers.CharField(source='plot.name', read_only=True)
    sector_name = serializers.CharField(source='plot.sector.name', read_only=True)

    class Meta:
        model = AnnualYield
        fields = '__all__'
