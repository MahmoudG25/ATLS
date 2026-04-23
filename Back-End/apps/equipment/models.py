from django.db import models

class Equipment(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Maintenance(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='maintenances')
    date = models.DateField()
    notes = models.TextField()

    def __str__(self):
        return f"Maintenance: {self.equipment.name} on {self.date}"

class Usage(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='usages')
    date = models.DateField()
    hours_used = models.DecimalField(max_digits=8, decimal_places=2)
    fuel_consumption = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Usage: {self.equipment.name} on {self.date}"
