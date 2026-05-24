from rest_framework import serializers
from apps.palm.models import PalmRecord


class PalmRecordSerializer(serializers.ModelSerializer):
    plot_name = serializers.CharField(source="plot.name", read_only=True)
    sector_name = serializers.CharField(source="plot.sector.name", read_only=True)

    class Meta:
        model = PalmRecord
        fields = "__all__"
