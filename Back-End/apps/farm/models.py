from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from core.tenant import TenantAwareModel


class Farm(TenantAwareModel):
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class CropType(models.Model):
    name = models.CharField(max_length=100, unique=True)  # e.g. 'Palm', 'Olive'

    def __str__(self):
        return self.name


class Sector(models.Model):
    """DEPRECATED: replaced by LocationNode tree structure"""

    name = models.CharField(max_length=255)
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="sectors")
    crop_type = models.ForeignKey(CropType, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.crop_type.name})"


class Plot(models.Model):
    """DEPRECATED: replaced by LocationNode tree structure"""

    name = models.CharField(max_length=255)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, related_name="plots")
    is_general = models.BooleanField(
        default=False, help_text="True if sector does not have specific plots."
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# --- New Hierarchical Models ---


class Crop(models.Model):
    """DEPRECATED: replaced by LocationNode tree structure"""

    CROP_TYPE_CHOICES = [
        ("palm", "نخيل"),
        ("olive", "زيتون"),
    ]
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="crops")
    name = models.CharField(max_length=100, verbose_name="المحصول")
    type = models.CharField(
        max_length=20, choices=CROP_TYPE_CHOICES, verbose_name="النوع"
    )
    order = models.IntegerField(default=0, verbose_name="الترتيب")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.name


class Stage(models.Model):
    """DEPRECATED: replaced by LocationNode tree structure"""

    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name="stages")
    name = models.CharField(max_length=100, verbose_name="المرحلة")
    order = models.IntegerField(default=0, verbose_name="الترتيب")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.crop.name} - {self.name}"


class Enclosure(models.Model):
    """DEPRECATED: replaced by LocationNode tree structure"""

    crop = models.ForeignKey(
        Crop,
        on_delete=models.CASCADE,
        related_name="enclosures",
        verbose_name="المحصول",
    )
    stage = models.ForeignKey(
        Stage,
        on_delete=models.CASCADE,
        related_name="enclosures",
        null=True,
        blank=True,
        verbose_name="المرحلة",
    )
    name = models.CharField(max_length=100, verbose_name="الحوشة / المنطقة")
    order = models.IntegerField(default=0, verbose_name="الترتيب")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        if self.stage:
            return f"{self.crop.name} - {self.stage.name} - {self.name}"
        return f"{self.crop.name} - {self.name}"


class LocationNode(MPTTModel, TenantAwareModel):
    TYPE_STAGE = "STAGE"
    TYPE_SECTOR = "SECTOR"
    TYPE_ENCLOSURE = "ENCLOSURE"
    TYPE_CHOICES = [
        (TYPE_STAGE, "Stage"),
        (TYPE_SECTOR, "Sector"),
        (TYPE_ENCLOSURE, "Enclosure"),
    ]

    farm = models.ForeignKey(
        Farm, on_delete=models.CASCADE, related_name="location_nodes"
    )
    parent = TreeForeignKey(
        "self", on_delete=models.CASCADE, related_name="children", null=True, blank=True
    )
    name = models.CharField(max_length=120)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "created_at", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "farm", "parent", "name", "type"],
                name="uniq_location_node_per_parent",
            ),
        ]
        indexes = [
            models.Index(fields=["company", "type", "is_active"]),
            models.Index(fields=["farm", "type", "is_active"]),
            models.Index(fields=["parent", "is_active"]),
        ]

    class MPTTMeta:
        parent_attr = "parent"
        order_insertion_by = ["order", "created_at"]

    def clean(self):
        super().clean()
        self.assert_same_company(self.farm, "farm")

        if self.parent:
            self.assert_same_company(self.parent, "parent")

            # 1. Parent-Child Type Integrity
            if self.parent.type == self.TYPE_ENCLOSURE:
                from django.core.exceptions import ValidationError

                raise ValidationError("لا يمكن إضافة عناصر تابعة للحوشة.")

            if self.parent.type == self.TYPE_STAGE and self.type not in [
                self.TYPE_STAGE,
                self.TYPE_ENCLOSURE,
            ]:
                from django.core.exceptions import ValidationError

                raise ValidationError(
                    "المرحلة يمكن أن تحتوي على مراحل أخرى أو حوشات فقط."
                )

            if self.parent.type == self.TYPE_SECTOR and self.type not in [
                self.TYPE_STAGE,
                self.TYPE_ENCLOSURE,
            ]:
                from django.core.exceptions import ValidationError

                raise ValidationError("القطاع يمكن أن يحتوي على مراحل أو حوشات فقط.")

            # 2. Depth Control: Max 3 levels
            # MPTT level is 0-indexed. Level 0 (Root), 1, 2.
            # If parent level is 2, child would be level 3 (4th level), which is forbidden.
            if self.parent.level >= 2:
                from django.core.exceptions import ValidationError

                raise ValidationError("تم الوصول للحد الأقصى لعمق الهيكل (3 مستويات).")

    def __str__(self):
        return f"{self.farm_id}:{self.type}:{self.name}"


class FarmSettings(TenantAwareModel):
    """
    Per-farm display settings for the location hierarchy.
    Controls which node types are shown in the Location picker.
    Auto-created with defaults when first accessed via get_or_create.
    """

    farm = models.OneToOneField(Farm, on_delete=models.CASCADE, related_name="settings")
    enable_sector = models.BooleanField(default=True)
    enable_stage = models.BooleanField(default=True)
    enable_enclosure = models.BooleanField(default=True)
    allow_stage_without_sector = models.BooleanField(default=False)
    allow_enclosure_without_stage = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Farm Settings"

    def __str__(self):
        return f"Settings for {self.farm}"


class EnclosureProfile(TenantAwareModel):
    """
    Operational metadata for a specific enclosure.
    Separates agricultural domain data from the structural hierarchy.
    """
    location_node = models.OneToOneField(
        LocationNode,
        on_delete=models.CASCADE,
        related_name="profile",
        limit_choices_to={"type": LocationNode.TYPE_ENCLOSURE}
    )
    crop_type = models.CharField(max_length=50, null=True, blank=True)  # e.g. 'palm', 'olive'
    planting_year = models.PositiveIntegerField(null=True, blank=True)
    tree_count = models.PositiveIntegerField(default=0)
    seedling_count = models.PositiveIntegerField(default=0)
    expected_yield = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    actual_yield = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Dynamic crop-specific metadata (e.g. variety, spacing)
    profile_data = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    general_notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات عامة")

    class Meta:
        verbose_name = "Enclosure Profile"
        verbose_name_plural = "Enclosure Profiles"

    def __str__(self):
        return f"Profile for {self.location_node.name}"
