from django.db import models

class Farm(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class CropType(models.Model):
    name = models.CharField(max_length=100, unique=True) # e.g. 'Palm', 'Olive'

    def __str__(self):
        return self.name

class Sector(models.Model):
    name = models.CharField(max_length=255)
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="sectors")
    crop_type = models.ForeignKey(CropType, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name} ({self.crop_type.name})"

class Plot(models.Model):
    name = models.CharField(max_length=255)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, related_name="plots")
    is_general = models.BooleanField(default=False, help_text="True if sector does not have specific plots.")

    def __str__(self):
        return self.name
