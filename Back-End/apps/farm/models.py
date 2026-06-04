from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from core.tenant import TenantAwareModel
from django.core.exceptions import ValidationError


class Farm(TenantAwareModel):
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


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

    def get_tree_count(self):
        """
        Computes the effective tree count for this location node.
        - For ENCLOSURE: returns EnclosureProfile.tree_count.
        - For STAGE: returns StageProfile.tree_count if configured (> 0),
          otherwise rolls up tree counts of all descendant ENCLOSUREs.
        - For other node types (SECTOR, FARM): rolls up all descendant ENCLOSUREs.
        """
        if self.type == self.TYPE_ENCLOSURE:
            return getattr(self, "profile", None).tree_count if hasattr(self, "profile") and self.profile else 0
        
        if self.type == self.TYPE_STAGE:
            stage_tc = getattr(self, "stage_profile", None).tree_count if hasattr(self, "stage_profile") and self.stage_profile else 0
            if stage_tc > 0:
                return stage_tc
        
        # Rollup descendants
        descendants = self.get_descendants().filter(type=self.TYPE_ENCLOSURE, is_active=True)
        total = 0
        for desc in descendants:
            total += getattr(desc, "profile", None).tree_count if hasattr(desc, "profile") and desc.profile else 0
        return total


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

    def clean(self):
        super().clean()
        stage_node = self.location_node.parent
        while stage_node and stage_node.type != LocationNode.TYPE_STAGE:
            stage_node = stage_node.parent
            
        if stage_node:
            stage_profile = getattr(stage_node, 'stage_profile', None)
            if stage_profile:
                stage_limit = stage_profile.tree_count
                if stage_limit > 0:
                    sibling_enclosures = stage_node.get_descendants().filter(
                        type=LocationNode.TYPE_ENCLOSURE,
                        is_active=True
                    ).exclude(id=self.location_node_id)
                    
                    current_sum = EnclosureProfile.objects.filter(
                        location_node__in=sibling_enclosures
                    ).aggregate(total=models.Sum('tree_count'))['total'] or 0
                    
                    if current_sum + self.tree_count > stage_limit:
                        raise ValidationError(
                            f"إجمالي عدد الأشجار في الحوشات ({current_sum + self.tree_count}) لا يمكن أن يتجاوز الحد الأقصى للمرحلة ({stage_limit})."
                        )


class StageProfile(TenantAwareModel):
    """
    Operational metadata for a specific stage.
    Keeps LocationNode generic and holds stage-specific attributes.
    """
    location_node = models.OneToOneField(
        LocationNode,
        on_delete=models.CASCADE,
        related_name="stage_profile",
        limit_choices_to={"type": LocationNode.TYPE_STAGE}
    )
    tree_count = models.PositiveIntegerField(default=0)
    metadata = models.JSONField(default=dict, blank=True)
    general_notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات عامة")

    class Meta:
        verbose_name = "Stage Profile"
        verbose_name_plural = "Stage Profiles"

    def __str__(self):
        return f"Profile for Stage {self.location_node.name}"

    def clean(self):
        super().clean()
        sibling_enclosures = self.location_node.get_descendants().filter(
            type=LocationNode.TYPE_ENCLOSURE,
            is_active=True
        )
        current_sum = EnclosureProfile.objects.filter(
            location_node__in=sibling_enclosures
        ).aggregate(total=models.Sum('tree_count'))['total'] or 0
        
        if self.tree_count > 0 and self.tree_count < current_sum:
            raise ValidationError(
                f"عدد أشجار المرحلة لا يمكن أن يكون أقل من إجمالي الأشجار الموزعة في حوشاتها حالياً ({current_sum})."
            )
