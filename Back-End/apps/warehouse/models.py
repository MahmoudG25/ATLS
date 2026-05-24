from django.db import models
from django.contrib.auth import get_user_model
from core.tenant import TenantAwareModel

User = get_user_model()


class Warehouse(TenantAwareModel):
    """المستودعات / المخازن"""
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "مخزن"
        verbose_name_plural = "المخازن"
        unique_together = [("company", "name")]

    def __str__(self):
        return self.name


class Item(TenantAwareModel):
    CATEGORY_CHOICES = [
        ("tools", "Tools"),
        ("pesticides", "Pesticides"),
        ("fertilizers", "Fertilizers"),
        ("crops", "Crops"),
        ("other", "Other"),
    ]
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    warehouse = models.ForeignKey(
        Warehouse, on_delete=models.SET_NULL, null=True, blank=True, related_name="items"
    )
    unit = models.CharField(max_length=50, blank=True, null=True, verbose_name="الوحدة")
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_items",
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.category})"


class Movement(TenantAwareModel):
    TYPE_CHOICES = [
        ("IN", "In"),
        ("OUT", "Out"),
        ("RETURNED", "Returned"),
        ("DAMAGED", "Damaged"),
    ]
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="movements")
    movement_type = models.CharField(max_length=15, choices=TYPE_CHOICES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="movements"
    )
    location = models.ForeignKey(
        "farm.LocationNode", on_delete=models.SET_NULL, null=True, blank=True, related_name="warehouse_movements", verbose_name="الموقع / الحوشة"
    )
    other_location = models.CharField(max_length=255, blank=True, null=True, verbose_name="موقع آخر")
    responsible_user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="responsible_movements", verbose_name="المستخدم المسؤول"
    )
    date = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True, null=True, verbose_name="ملاحظات")

    def __str__(self):
        return f"{self.item.name} - {self.movement_type} - {self.quantity}"
