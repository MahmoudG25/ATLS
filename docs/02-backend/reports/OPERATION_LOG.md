# OperationLog — Core Event Entity

> The atomic event record at the heart of ATLS.
> See `ADR-001-operation-log.md` and `00-core/EVENT_DRIVEN_ARCHITECTURE.md`.

---

## 1. What Is OperationLog?

An `OperationLog` represents a single farm operation performed at a specific location on a specific date. It is the atomic unit of work recorded in the system.

**Business meaning (Arabic):**
> سجل العمليات هو الوحدة الأساسية لتسجيل أي عمل يتم في المزرعة.
> كل عملية في موقع محدد تُسجَّل كـ OperationLog منفصل.

---

## 2. Model Definition

```python
class OperationLog(TenantAwareModel):
    # Parent container
    report    = models.ForeignKey(
        'DailyTaskReport', on_delete=models.CASCADE,
        related_name='operation_logs'
    )
    # Event context
    company   = models.ForeignKey(Company, on_delete=models.CASCADE)
    date      = models.DateField()
    location  = models.ForeignKey(LocationNode, on_delete=models.CASCADE,
                                   related_name='operation_logs')
    operation = models.ForeignKey(Operation, on_delete=models.CASCADE,
                                   related_name='operation_logs')
    # Labor
    company_workers    = models.IntegerField(default=0)
    contractor_workers = models.IntegerField(default=0)
    contractor         = models.ForeignKey(
        Contractor, null=True, blank=True, on_delete=models.SET_NULL
    )
    work_hours         = models.FloatField(default=8.0)
    # Output
    actual_productivity = models.FloatField(null=True, blank=True)
    notes               = models.TextField(blank=True, default='')

    class Meta:
        indexes = [
            models.Index(fields=['company', 'date']),
            models.Index(fields=['company', 'operation', 'date']),
            models.Index(fields=['location', 'date']),
        ]
```

---

## 3. DailyTaskReport — Container Only

```python
class DailyTaskReport(TenantAwareModel):
    company   = models.ForeignKey(Company, on_delete=models.CASCADE)
    farm      = models.ForeignKey(Farm, on_delete=models.CASCADE)
    engineer  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    report_date = models.DateField()
    status    = models.CharField(
        max_length=20,
        choices=[('draft','Draft'),('submitted','Submitted'),('approved','Approved')],
        default='draft'
    )
    notes     = models.TextField(blank=True, default='')
    # operation_logs → reverse FK from OperationLog
```

The `DailyTaskReport` holds **metadata only** — date, engineer, status.
All operational data lives in `OperationLog` children.

---

## 4. LaborEntry

```python
class LaborEntry(TenantAwareModel):
    company       = models.ForeignKey(Company, on_delete=models.CASCADE)
    operation_log = models.ForeignKey(OperationLog, on_delete=models.CASCADE,
                                       related_name='labor_entries')
    # Worker identification
    worker_name   = models.CharField(max_length=200)
    employee      = models.ForeignKey(
        'hr.Employee', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='labor_entries'
    )
    worker_type   = models.CharField(
        max_length=20, choices=[('company','Company'),('contractor','Contractor')]
    )
    contractor    = models.ForeignKey(
        Contractor, null=True, blank=True, on_delete=models.SET_NULL
    )
    # Work detail
    hours_worked  = models.FloatField(default=8.0)
    overtime_hours = models.FloatField(default=0.0)
    hourly_rate   = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    notes         = models.TextField(blank=True, default='')
```

---

## 5. API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| `GET` | `/reports/` | List DailyTaskReports for company |
| `POST` | `/reports/` | Create new report (container) |
| `GET` | `/reports/{id}/` | Report detail with nested OperationLogs |
| `POST` | `/reports/{id}/operation-logs/` | Add OperationLog to report |
| `PATCH` | `/reports/{id}/operation-logs/{log_id}/` | Update OperationLog |
| `DELETE` | `/reports/{id}/operation-logs/{log_id}/` | Remove OperationLog |
| `POST` | `/reports/{id}/operation-logs/{log_id}/labor-entries/` | Add LaborEntry |
| `PATCH` | `/reports/{id}/approve/` | Approve report (MANAGER+) |

---

## 6. Analytics Queries

Always query from `OperationLog` — not `DailyTaskReport`:

```python
# Workers by operation
OperationLog.objects.for_company(company) \
    .values('operation__name') \
    .annotate(
        total_workers=Sum(F('company_workers') + F('contractor_workers')),
        avg_productivity=Avg('actual_productivity'),
        total_reports=Count('id'),
    ).order_by('-total_workers')

# Workers by location
OperationLog.objects.for_company(company) \
    .values('location__id', 'location__name', 'location__type') \
    .annotate(total_workers=Sum(F('company_workers') + F('contractor_workers')))

# Daily trend
OperationLog.objects.for_company(company) \
    .values('date') \
    .annotate(total=Sum(F('company_workers') + F('contractor_workers'))) \
    .order_by('-date')
```

See `02-backend/reports/ANALYTICS_API.md` for all analytics endpoints.
