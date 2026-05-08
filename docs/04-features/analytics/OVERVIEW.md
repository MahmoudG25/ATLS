# Analytics — Feature Overview

> Feature: Farm Performance Analytics Dashboard
> ADR: `ADR-001-operation-log.md` (analytics must query OperationLog, not DailyTaskReport)

---

## What This Feature Does

Provides real-time KPI dashboards and analytical reports for farm operations:
- Workers trend over time
- Productivity by operation type
- Workforce distribution by location
- Operation frequency analysis

**Business value (Arabic):**
> المدير يرى الصورة الكاملة: كام عامل شتغل إيه، فين، وبأد إيه إنتاجية —
> على مستوى كل عملية، كل موقع، كل فترة زمنية.

---

## Analytics API Endpoints (Active)

All 4 endpoints currently live — see `02-backend/reports/ANALYTICS_API.md` for full schemas.

| Endpoint | What It Returns |
|----------|----------------|
| `GET /analytics/kpi/` | Total workers, hours, reports, productivity (last 30 days + trend vs. previous period) |
| `GET /analytics/productivity/` | Daily productivity time series |
| `GET /analytics/operations-summary/` | Per-operation: workers, hours, report count, avg productivity |
| `GET /analytics/workers-by-location/` | Workers breakdown per LocationNode |

---

## Dashboard Components

```
KpiCard × 4         → Workers Total | Hours Total | Reports Count | Avg Productivity
ProductivityChart   → Line chart: daily trend
OperationsSummary   → Bar chart or table: per-operation breakdown
WorkersByLocation   → Horizontal bar: per-location
DateRangePicker     → Filter all charts by date range
```

---

## Data Source Rule

```
✅ ALWAYS query from: OperationLog
❌ NEVER query from: DailyTaskReport fields
```

This is the core architectural principle. See `ADR-001-operation-log.md`.

---

## Filters Available

- `?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`
- `?operation=<id>`
- `?location=<id>`
- `?engineer=<id>`

---

## Current Status

| Component | Status |
|-----------|--------|
| `/analytics/kpi/` endpoint | ✅ Live |
| `/analytics/productivity/` | ✅ Live |
| `/analytics/operations-summary/` | ✅ Live |
| `/analytics/workers-by-location/` | ✅ Live |
| Dashboard page (frontend) | ⚠️ Basic version exists |
| Date range filter | ⚠️ Partial |
| Location-based drill-down | ⬜ Not built |
| Export to Excel | ⚠️ Partial |
