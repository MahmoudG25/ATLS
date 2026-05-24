from apps.warehouse.models import Item, Movement
from django.db import transaction
from rest_framework.exceptions import ValidationError
from services.activity_service import log_activity


def list_items():
    return Item.objects.filter(is_active=True)


def get_movements(item_id=None, location_id=None):
    qs = Movement.objects.select_related("item", "location", "responsible_user").all().order_by("-date")
    if item_id:
        qs = qs.filter(item_id=item_id)
    if location_id:
        qs = qs.filter(location_id=location_id)
    return qs


def create_item(data, user=None):
    # Cannot set quantity initially, it computes from movements naturally
    data.pop("quantity", None)
    data.pop("updated_by", None)
    item = Item.objects.create(**data, updated_by=user)
    log_activity(user, f"Created Warehouse Item: {item.name}", "Warehouse")
    return item


def update_item(item_id, data, user=None):
    item = Item.objects.get(id=item_id)
    data.pop("quantity", None)  # Prevent direct quantity manipulation
    data.pop("updated_by", None)
    for attr, value in data.items():
        setattr(item, attr, value)
    item.updated_by = user
    item.save()
    log_activity(user, f"Updated Warehouse Item: {item.name}", "Warehouse")
    return item


def delete_item(item_id, user=None):
    item = Item.objects.get(id=item_id)
    item_name = item.name
    item.is_active = False
    item.save()
    if user:
        log_activity(user, f"Archived Warehouse Item: {item_name}", "Warehouse")


@transaction.atomic
def create_movement(data, user=None):
    if data["quantity"] <= 0:
        raise ValidationError({"quantity": "Quantity must be positive"})

    data.pop("user", None)
    movement = Movement.objects.create(**data, user=user)
    item = movement.item

    if movement.movement_type in ["IN", "RETURNED"]:
        item.quantity += movement.quantity
    elif movement.movement_type in ["OUT", "DAMAGED"]:
        if item.quantity < movement.quantity:
            raise ValidationError(
                {"quantity": "Insufficient stock for this movement."}
            )
        item.quantity -= movement.quantity

    item.save()
    log_activity(
        user,
        f"Warehouse Movement ({movement.movement_type}): {movement.quantity} {item.unit} of {item.name}",
        "Warehouse",
    )
