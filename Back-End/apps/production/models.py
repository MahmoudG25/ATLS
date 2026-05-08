from django.db import models
from apps.farm.models import Plot


class AnnualYield(models.Model):
    plot = models.ForeignKey(
        Plot, on_delete=models.CASCADE, related_name="annual_yields"
    )
    year = models.PositiveIntegerField()
    production_amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["plot", "year"], name="unique_plot_year_yield"
            )
        ]
