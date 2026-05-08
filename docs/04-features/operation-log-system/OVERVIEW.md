# Operation Log System — Feature Overview

> Feature: Event-Driven Operation Recording
> Core ADRs: `ADR-001-operation-log.md`, `ADR-005-event-driven-farm-erp.md`

---

## What This Feature Does

Allows field engineers to record farm operations as atomic events, linked to specific locations, with full labor detail. Replaces the old single-operation-per-report model.

**Business value (Arabic):**
> المهندس يسجّل كل عملية قام بها في أي موقع بدقة كاملة:
> - إيه العملية؟ (تلقيح / صيانة / رش)
> - فين؟ (قطاع شمالي → مرحلة أ → حوشة ١٢)
> - كام عامل؟ كام ساعة؟ كام إنتاجية؟

---

## User Flow

```
1. Engineer opens Daily Report (DailyTaskReport — container)
2. Engineer adds Operation Log entries:
   - Selects location from tree (Sector → Stage → Enclosure)
   - Selects operation type (from company Operations list)
   - Enters: workers count, hours, productivity
   - Optionally adds LaborEntry details per worker
   - Optionally attaches photos
3. Engineer submits report
4. Manager reviews and approves
5. Analytics aggregate from OperationLog events
```

---

## Key Entities

| Entity | Role |
|--------|------|
| `DailyTaskReport` | Container (date + engineer + status) |
| `OperationLog` | Atomic event (the real data) |
| `LaborEntry` | Per-worker detail |
| `Attachment` | Photos linked to operation |
| `Operation` | Lookup: operation type |
| `LocationNode` | Lookup: where it happened |
| `Contractor` | Lookup: labor contractor |

---

## Backend Files

```
apps/reports/models.py              ← DailyTaskReport, OperationLog, LaborEntry
serializers/report_serializers.py   ← Nested serializers
services/report_service.py          ← Business logic
api/endpoints/report_views.py       ← API views
```

Reference: `02-backend/reports/OPERATION_LOG.md`

---

## Frontend Files

```
src/pages/reports/DailyTaskReport/
├── DailyTaskForm.jsx           ← Main form (report container)
├── OperationLogPanel.jsx       ← List + add operation logs
├── LaborEntryDrawer.jsx        ← Bottom drawer for worker details
└── AttachmentUpload.jsx        ← Photo upload via Cloudinary

src/features/reports/services.js ← All API calls
```

---

## Analytics Integration

Every `OperationLog` feeds directly into the analytics endpoints:
- `/analytics/kpi/` — overall KPIs
- `/analytics/productivity/` — by operation, location, date
- `/analytics/operations-summary/` — per-operation breakdown
- `/analytics/workers-by-location/` — location workforce map

Reference: `02-backend/reports/ANALYTICS_API.md`

---

## Current Status

- DailyTaskReport: ✅ Working
- OperationLog model: ⚠️ May be inline with DailyTaskReport — needs separation
- LaborEntry: ⚠️ Basic version exists — needs HR link
- Analytics: ✅ Working (querying from report fields — migrate to OperationLog)

**Next step**: Separate OperationLog into its own model per `ADR-001`.
