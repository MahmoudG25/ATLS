from django.db import models

class Farm(models.Model):
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

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
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.crop_type.name})"

class Plot(models.Model):
    name = models.CharField(max_length=255)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, related_name="plots")
    is_general = models.BooleanField(default=False, help_text="True if sector does not have specific plots.")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

# --- New Hierarchical Models ---

class Crop(models.Model):
    CROP_TYPE_CHOICES = [
        ('palm', 'نخيل'),
        ('olive', 'زيتون'),
    ]
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="crops")
    name = models.CharField(max_length=100, verbose_name="المحصول")
    type = models.CharField(max_length=20, choices=CROP_TYPE_CHOICES, verbose_name="النوع")
    order = models.IntegerField(default=0, verbose_name="الترتيب")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.name

class Stage(models.Model):
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name="stages")
    name = models.CharField(max_length=100, verbose_name="المرحلة")
    order = models.IntegerField(default=0, verbose_name="الترتيب")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.crop.name} - {self.name}"

class Enclosure(models.Model):
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name="enclosures", verbose_name="المحصول")
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name="enclosures", null=True, blank=True, verbose_name="المرحلة")
    name = models.CharField(max_length=100, verbose_name="الحوشة / المنطقة")
    order = models.IntegerField(default=0, verbose_name="الترتيب")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        if self.stage:
            return f"{self.crop.name} - {self.stage.name} - {self.name}"
        return f"{self.crop.name} - {self.name}"

