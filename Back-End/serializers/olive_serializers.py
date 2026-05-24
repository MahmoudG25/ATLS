from rest_framework import serializers
from apps.olive.models import OliveRecord


class OliveRecordSerializer(serializers.ModelSerializer):
    plot_name = serializers.CharField(source="plot.name", read_only=True)
    sector_name = serializers.CharField(source="plot.sector.name", read_only=True)

    class Meta:
        model = OliveRecord
        fields = "__all__"
