# Backend Overview — ATLS Farm ERP

> Merged from: `back-end/project.md` + `back-end/rules.md`

---

## Stack

| Component | Technology |
|-----------|-----------|
| Framework | Django 5+ |
| API | Django REST Framework |
| Database | PostgreSQL |
| Auth | JWT (SimpleJWT) |
| File Storage | Cloudinary |
| Task Queue | — (planned: Celery) |

---

## Directory Structure

```
Back-End/
├── apps/                    ← Django applications
│   ├── users/               ← Auth, roles, notifications
│   ├── farm/                ← Farm, LocationNode
│   ├── reports/             ← DailyTaskReport, OperationLog, LaborEntry
│   ├── hr/                  ← Employee, LeaveRequest, Attendance
│   ├── warehouse/           ← WarehouseItem, WarehouseMovement
│   ├── equipment/           ← Equipment, MaintenanceLog, UsageLog
│   ├── accounting/          ← Expense, Revenue, Invoice, Salary
│   └── production/          ← YieldRecord, CropRecord
├── core/                    ← Base models, settings, utilities
│   ├── settings.py
│   └── base_models.py       ← TenantAwareModel, TenantManager
├── api/                     ← URL routing
│   ├── urls.py
│   └── endpoints/           ← All API views
│       ├── farm_views.py
│       ├── report_views.py
│       ├── hr_views.py
│       ├── analytics_views.py
│       └── ...
├── serializers/             ← All serializers
│   ├── report_serializers.py
│   ├── hr_serializers.py
│   └── ...
├── services/                ← All business logic
│   ├── user_service.py
│   ├── farm_service.py
│   ├── report_service.py
│   ├── hr_service.py
│   ├── warehouse_service.py
│   ├── accounting_service.py
│   └── notification_service.py
└── permissions/             ← Custom permission classes
    ├── role_permissions.py
    └── tenant_permissions.py
```

---

## Architecture Pattern

```
Request
  ↓
api/endpoints/<module>_views.py  (thin view — HTTP only)
  ↓
permissions/<class>.py           (role + tenant check)
  ↓
serializers/<module>_serializers.py  (validate + transform)
  ↓
services/<module>_service.py     (ALL business logic)
  ↓
apps/<module>/models.py          (data access)
  ↓
PostgreSQL
```

---

## Key Patterns

### TenantAwareModel
Every model inherits this — see `00-core/TENANT_SYSTEM.md`.

### Service Layer
Every module has a service file. Views call services — they never access ORM directly.
See `00-core/CODING_RULES.md`.

### Permission Classes
Every view declares permission_classes. No open endpoints.
See `00-core/PERMISSIONS.md`.

---

## API Base URL

```
Development:  http://localhost:8000/api/
Production:   https://your-domain.com/api/
```

All endpoints require JWT:
```
Authorization: Bearer <access_token>
```

---

## Seeding & Utilities

| File | Purpose |
|------|---------|
| `seed_report_options.py` | Seeds Operation, Variety, Unit records |
| `seed_wl.py` | Seeds sample LocationNode data |
| `check_db.py` | Basic DB connectivity check |
