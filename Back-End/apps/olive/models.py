from django.db import models
from apps.farm.models import LocationNode
from core.models import BaseEntity


class OliveRecord(BaseEntity):
    location_node = models.ForeignKey(
        LocationNode, on_delete=models.CASCADE, related_name="olive_records"
    )
    trees_count = models.PositiveIntegerField()
    olive_type = models.CharField(max_length=100)
    trees_age = models.PositiveIntegerField(null=True, blank=True)
    last_year_production = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    expected_production = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    def __str__(self):
        return f"Olive Record - {self.location_node.name}"
