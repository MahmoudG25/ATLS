from django.db import models
from apps.farm.models import Plot

class PalmRecord(models.Model):
    plot = models.ForeignKey(Plot, on_delete=models.CASCADE, related_name='palm_records')
    trees_count = models.PositiveIntegerField()
    palm_type = models.CharField(max_length=100)
    trees_age = models.PositiveIntegerField(null=True, blank=True)
    last_year_production = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    expected_production = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    offshoots_count = models.PositiveIntegerField(default=0)
    sold_offshoots = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Palm Record - {self.plot.name}"
