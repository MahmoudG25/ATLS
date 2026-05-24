# Accounting Module — Backend Reference

---

## Models

### Expense
```python
class Expense(TenantAwareModel):
    company  = models.ForeignKey(Company, on_delete=models.CASCADE)
    amount   = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.CharField(max_length=100)
    date     = models.DateField()
    notes    = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
```

### Revenue
```python
class Revenue(TenantAwareModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    amount  = models.DecimalField(max_digits=12, decimal_places=2)
    source  = models.CharField(max_length=200)
    date    = models.DateField()
    notes   = models.TextField(blank=True)
```

### Invoice
```python
class Invoice(TenantAwareModel):
    TYPES  = [('purchase','Purchase'),('sales','Sales')]
    STATUS = [('draft','Draft'),('sent','Sent'),('paid','Paid'),('cancelled','Cancelled')]
    company        = models.ForeignKey(Company, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=50, unique=True)
    type           = models.CharField(max_length=20, choices=TYPES)
    status         = models.CharField(max_length=20, choices=STATUS, default='draft')
    party_name     = models.CharField(max_length=200)
    issue_date     = models.DateField()
    due_date       = models.DateField(null=True, blank=True)
    total_amount   = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes          = models.TextField(blank=True)
    created_by     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
```

### Salary
```python
class Salary(TenantAwareModel):
    company  = models.ForeignKey(Company, on_delete=models.CASCADE)
    employee = models.ForeignKey('hr.Employee', on_delete=models.CASCADE)
    amount   = models.DecimalField(max_digits=10, decimal_places=2)
    date     = models.DateField()
    notes    = models.TextField(blank=True)
```

---

## API Endpoints (Planned)

```
GET /accounting/expenses/             list + filter by category, date
POST /accounting/expenses/            create
GET /accounting/revenues/             list + filter
POST /accounting/revenues/            create
GET /accounting/invoices/             list + filter by status, type
POST /accounting/invoices/            create
GET /accounting/payroll/              salaries from HR employees
GET /accounting/labor-costs/          cost from OperationLog × LaborEntry
GET /accounting/location-costs/       cost breakdown per LocationNode
GET /accounting/monthly-summary/      revenue - expenses by month
```

---

## Integration

- `HR.Employee.salary` → `Accounting.payroll`
- `OperationLog.LaborEntry (hours × rate)` → `Accounting.labor_cost`
- `WarehouseMovement (OUT)` → `Accounting.material_cost`
