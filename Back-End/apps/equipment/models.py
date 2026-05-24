from django.db import models
from core.tenant import TenantAwareModel


class Equipment(TenantAwareModel):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=100, blank=True, default="")
    model = models.CharField(max_length=100, blank=True, default="")
    serial_number = models.CharField(max_length=100, blank=True, default="")
    purchase_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50, default="active")
    specifications = models.TextField(blank=True, default="")
    current_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    
    # Oil Change Interval configuration and tracking
    oil_change_interval_hours = models.DecimalField(max_digits=8, decimal_places=2, default=250.0)
    oil_change_interval_days = models.IntegerField(default=180)
    last_oil_change_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    last_oil_change_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.type})"


class Maintenance(TenantAwareModel):
    equipment = models.ForeignKey(
        Equipment, on_delete=models.CASCADE, related_name="maintenances"
    )
    date = models.DateField()
    maintenance_type = models.CharField(max_length=100, default="scheduled")
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    notes = models.TextField(blank=True, default="")

    def __str__(self):
        return f"Maintenance: {self.equipment.name} on {self.date}"


class Usage(TenantAwareModel):
    equipment = models.ForeignKey(
        Equipment, on_delete=models.CASCADE, related_name="usages"
    )
    date = models.DateField()
    hours_used = models.DecimalField(max_digits=8, decimal_places=2)
    fuel_consumption = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    operator = models.CharField(max_length=255, blank=True, default="")

    def __str__(self):
        return f"Usage: {self.equipment.name} on {self.date}"


class OilChangeLog(TenantAwareModel):
    equipment = models.ForeignKey(
        Equipment, on_delete=models.CASCADE, related_name="oil_changes"
    )
    date = models.DateField()
    hours_at_change = models.DecimalField(max_digits=10, decimal_places=2)
    oil_type = models.CharField(max_length=100, blank=True, default="")
    filter_changed = models.BooleanField(default=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    notes = models.TextField(blank=True, default="")

    def __str__(self):
        return f"Oil Change: {self.equipment.name} on {self.date} at {self.hours_at_change} hrs"
