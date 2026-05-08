# Warehouse Module — Backend Reference

---

## Models

### WarehouseItem
```python
class WarehouseItem(TenantAwareModel):
    company    = models.ForeignKey(Company, on_delete=models.CASCADE)
    name       = models.CharField(max_length=200)
    category   = models.CharField(max_length=100)   # tools, pesticides, fertilizers
    unit       = models.CharField(max_length=50)    # kg, liter, piece
    quantity   = models.FloatField(default=0)
    min_stock  = models.FloatField(default=0)       # low-stock threshold
    location   = models.CharField(max_length=200, blank=True)  # physical location
```

### WarehouseMovement
```python
class WarehouseMovement(TenantAwareModel):
    TYPES = [('IN', 'In'), ('OUT', 'Out')]
    company   = models.ForeignKey(Company, on_delete=models.CASCADE)
    item      = models.ForeignKey(WarehouseItem, on_delete=models.CASCADE,
                                   related_name='movements')
    type      = models.CharField(max_length=10, choices=TYPES)
    quantity  = models.FloatField()
    date      = models.DateField()
    notes     = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
```

**Rule**: Never update `quantity` directly. Always add a `WarehouseMovement` record.
The item quantity is computed from movements.

---

## API Endpoints

```
GET    /warehouse/items/              list all items (filter: category, low_stock)
POST   /warehouse/items/              create item
PATCH  /warehouse/items/{id}/         update item
GET    /warehouse/movements/          list movements (filter: item, date, type)
POST   /warehouse/movements/          add movement (IN or OUT)
GET    /warehouse/alerts/             items where quantity <= min_stock
GET    /warehouse/summary/            total value, item count, alert count
```

---

## Integration

- Fertilization reports → OUT movement for fertilizer items
- Low stock → Notification to MANAGER/OWNER
