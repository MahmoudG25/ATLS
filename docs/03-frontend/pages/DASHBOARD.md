# Dashboard — Frontend Reference

> Main dashboard page — first page after login.

---

## Layout

```
DashboardLayout
├── Sidebar (260px, permanent, role-filtered)
└── Main content area
    ├── DashboardTopbar (breadcrumb + notifications + avatar)
    └── Page content
        ├── KPI Cards row (4 cards)
        ├── Charts row
        │   ├── ProductivityChart (line, 2/3 width)
        │   └── OperationsSummary (bar, 1/3 width)
        └── WorkersByLocation (horizontal bar, full width)
```

---

## KPI Cards

| Card | Metric | Source |
|------|--------|--------|
| Total Workers | Sum of company + contractor workers | `OperationLog` |
| Total Work Hours | Sum of work_hours | `OperationLog` |
| Total Reports | Count of DailyTaskReports | `DailyTaskReport` |
| Avg Productivity | Average actual_productivity | `OperationLog` |

Each card also shows: trend vs previous period (↑ green / ↓ red).

---

## Filters

- Date range picker (default: last 30 days)
- Applied to all dashboard data simultaneously

---

## Role-Based Content

| Role | What They See |
|------|--------------|
| OWNER | All metrics for company |
| MANAGER | All metrics for company |
| ENGINEER | Their own reports only |
| HR | HR-related KPIs instead |
| ACCOUNTANT | Cost-focused KPIs |
| WAREHOUSE | Stock level KPIs |

---

## Service

```javascript
// features/reports/services.js
export const getKpiData = (params) => api.get('/analytics/kpi/', { params })
export const getProductivityData = (params) => api.get('/analytics/productivity/', { params })
export const getOperationsSummary = (params) => api.get('/analytics/operations-summary/', { params })
export const getWorkersByLocation = (params) => api.get('/analytics/workers-by-location/', { params })
```

---

## Components Used

```
KpiCard              → src/components/Shared/KpiCard.jsx
ProductivityChart    → src/components/Shared/Charts.jsx
OperationsSummary    → src/components/Shared/Charts.jsx
WorkersByLocation    → src/components/Shared/Charts.jsx
DateRangePicker      → MUI DatePicker
NotificationsBell    → src/components/Shared/NotificationsBell.jsx
```
