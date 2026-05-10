from rest_framework import serializers
from .models import HarvestReport, SortingReport
from apps.reports.models import Season, Variety, Unit, QualityGrade, SortingCategory
from apps.farm.models import LocationNode


class HarvestReportSerializer(serializers.ModelSerializer):
    location_name = serializers.ReadOnlyField(source="location.name")
    season_name = serializers.ReadOnlyField(source="season.name")
    variety_name = serializers.ReadOnlyField(source="variety.name")
    unit_name = serializers.ReadOnlyField(source="unit.name")
    supervisor_name = serializers.ReadOnlyField(source="supervisor.get_full_name")

    class Meta:
        model = HarvestReport
        fields = "__all__"
        read_only_fields = ("company", "status", "variety_name_snapshot", "unit_label_snapshot")


class SortingReportSerializer(serializers.ModelSerializer):
    location_name = serializers.ReadOnlyField(source="harvest_report.location.name")
    
    class Meta:
        model = SortingReport
        fields = "__all__"
        read_only_fields = ("company", "status", "harvest_info_snapshot")

    def validate(self, data):
        """Quantity integrity check: Sorted + Rejected + Waste <= Incoming"""
        incoming = data.get("incoming_quantity")
        final = data.get("final_quantity")
        rejected = data.get("rejected_quantity", 0)
        waste = data.get("waste_quantity", 0)
        
        if (final + rejected + waste) > incoming:
            raise serializers.ValidationError("Total output exceeds incoming quantity.")
        return data
