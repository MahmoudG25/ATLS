# Event-Driven Architecture — ATLS Farm ERP

> **Authority**: Tier 2. Explains the event-driven operational model.
> See also: `05-decisions/ADR-001-operation-log.md` and `ADR-005-event-driven-farm-erp.md`

---

## 1. Core Concept

ATLS is an **Event-Driven Farm ERP**.

Every farm activity is recorded as an atomic event (`OperationLog`).
These events are the true source of operational data.

```
Traditional (report-centric):    Event-Driven (what we use):
  DailyTaskReport = core           OperationLog = core
  Analytics from reports           Analytics from events
  One report per day               Many events per day
  Coarse-grained data              Fine-grained data
```

---

## 2. Entity Roles

### OperationLog — The Heart
```
OperationLog is the atomic event record.
It captures a single operation performed at a specific location on a specific date.
It is the source of truth for:
  - labor costs
  - productivity metrics
  - location-based analytics
  - operation frequency analysis
```

### DailyTaskReport — The Container
```
DailyTaskReport is a grouping container only.
It groups OperationLogs for the same day and engineer.
It does NOT contain operational data directly.
Analytics should NOT be built from DailyTaskReport fields.
```

---

## 3. Event Flow

```
Engineer in the field
    ↓
Creates DailyTaskReport (container for the day)
    ↓
Adds OperationLog entries:
    - Location: Enclosure 12, Stage A, North Sector
    - Operation: Pollination
    - Workers: 8 company + 2 contractor
    - Hours: 6
    - Productivity: 150 palms
    ↓
Attaches LaborEntry details (names, hours, rates)
    ↓
Optionally attaches photos (Attachment → Cloudinary)
    ↓
Manager reviews the DailyTaskReport
    ↓
Analytics aggregates from OperationLog events
```

---

## 4. OperationLog Model (Conceptual)

```python
class OperationLog(TenantAwareModel):
    # Container
    report   = models.ForeignKey(DailyTaskReport, on_delete=models.CASCADE,
                                  related_name='operation_logs')
    # Event context
    date      = models.DateField()
    location  = models.ForeignKey(LocationNode, on_delete=models.CASCADE)
    operation = models.ForeignKey(Operation, on_delete=models.CASCADE)
    # Labor
    company_workers    = models.IntegerField(default=0)
    contractor_workers = models.IntegerField(default=0)
    contractor         = models.ForeignKey(Contractor, null=True, blank=True, ...)
    work_hours         = models.FloatField(default=8.0)
    # Output
    actual_productivity = models.FloatField(null=True, blank=True)
    notes               = models.TextField(blank=True)
    # Related
    labor_entries = (reverse FK to LaborEntry)
    attachments   = (reverse FK to Attachment)
```

---

## 5. Analytics Pattern

```python
# ✅ Correct — analytics from OperationLog events
from apps.reports.models import OperationLog

events = OperationLog.objects \
    .for_company(company) \
    .filter(date__range=(start, end)) \
    .select_related('operation', 'location') \
    .values('operation__name', 'location__name') \
    .annotate(
        total_workers=Sum(F('company_workers') + F('contractor_workers')),
        total_hours=Sum('work_hours'),
        avg_productivity=Avg('actual_productivity'),
    )

# ❌ Wrong — analytics from DailyTaskReport (coarse, limited)
reports = DailyTaskReport.objects.for_company(company).values('date').annotate(...)
```

---

## 6. Benefits of Event-Driven Approach

| Benefit | How |
|---------|-----|
| **Granular analytics** | Each operation-location pair is a separate event |
| **Cost attribution** | Labor costs tied to specific operation + location |
| **Audit trail** | Every field action is a timestamped event |
| **Flexible reporting** | Group by date, operation, location, engineer, contractor |
| **Future IoT ready** | Events can be triggered by sensors, not just humans |
| **Scalable** | New event types add without changing report structure |

---

## 7. What This Means for Development

### When adding a new data field:
- If it's per-operation → add to `OperationLog`
- If it's per-day per-engineer → add to `DailyTaskReport`
- If it's per-worker → add to `LaborEntry`

### When building analytics:
- Always query `OperationLog` — not `DailyTaskReport`
- Use `location`, `operation`, `date` as primary group-by dimensions

### When building reports UI:
- The form creates a `DailyTaskReport` shell first
- Then the engineer adds `OperationLog` entries to it
- The UI should make it clear: report = container, logs = the actual data
