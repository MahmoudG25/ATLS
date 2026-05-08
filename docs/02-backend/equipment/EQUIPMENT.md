# Equipment Module — Backend Reference

---

## Models

### Equipment
```python
class Equipment(TenantAwareModel):
    company           = models.ForeignKey(Company, on_delete=models.CASCADE)
    name              = models.CharField(max_length=200)
    type              = models.CharField(max_length=100)   # tractor, pump, vehicle
    serial_number     = models.CharField(max_length=100, blank=True)
    status            = models.CharField(max_length=20,
                        choices=[('active','Active'),('maintenance','In Maintenance'),('retired','Retired')],
                        default='active')
    assigned_location = models.ForeignKey(
        'farm.LocationNode', null=True, blank=True, on_delete=models.SET_NULL
    )
    notes             = models.TextField(blank=True)
```

### MaintenanceLog
```python
class MaintenanceLog(TenantAwareModel):
    company    = models.ForeignKey(Company, on_delete=models.CASCADE)
    equipment  = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='maintenance_logs')
    date       = models.DateField()
    description = models.TextField()
    cost       = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    performed_by = models.CharField(max_length=200, blank=True)
```

### EquipmentUsageLog
```python
class EquipmentUsageLog(TenantAwareModel):
    company    = models.ForeignKey(Company, on_delete=models.CASCADE)
    equipment  = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='usage_logs')
    report     = models.ForeignKey('reports.DailyTaskReport', null=True, blank=True,
                                    on_delete=models.SET_NULL)
    date       = models.DateField()
    hours      = models.FloatField()
    operator   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    notes      = models.TextField(blank=True)
```

---

## API Endpoints

```
GET    /equipment/                     list equipment
POST   /equipment/                     add equipment
PATCH  /equipment/{id}/                update
GET    /equipment/{id}/maintenance/    maintenance history
POST   /equipment/{id}/maintenance/    log maintenance
GET    /equipment/{id}/usage/          usage history
POST   /equipment/{id}/usage/          log usage (linked to report)
GET    /equipment/summary/             fleet status summary
```

---

## Integration

- `EquipmentUsageLog.report` → links to `DailyTaskReport`
- Equipment costs → `Accounting.Expense`
- `assigned_location` → `LocationNode` for location-based fleet tracking
