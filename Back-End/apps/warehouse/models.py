from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Item(models.Model):
    CATEGORY_CHOICES = [
        ("tools", "Tools"),
        ("pesticides", "Pesticides"),
        ("fertilizers", "Fertilizers"),
    ]
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
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


class Movement(models.Model):
    TYPE_CHOICES = [
        ("IN", "In"),
        ("OUT", "Out"),
    ]
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="movements")
    movement_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="movements"
    )
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item.name} - {self.movement_type} - {self.quantity}"
