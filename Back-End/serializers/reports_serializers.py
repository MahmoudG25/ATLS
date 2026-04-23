from rest_framework import serializers
from apps.reports.models import DailyReport

class DailyReportSerializer(serializers.ModelSerializer):
    engineer_name = serializers.CharField(source='engineer.name', read_only=True)
    sector_name = serializers.CharField(source='sector.name', read_only=True)
    plot_name = serializers.CharField(source='plot.name', read_only=True, allow_null=True)

    class Meta:
        model = DailyReport
        fields = '__all__'
        read_only_fields = ['engineer']
