# Modules Overview — ATLS Farm ERP

> Quick-reference table of all modules, their status, and documentation links.

---

## Module Status Table

| # | Module | Backend | Frontend | Priority | Docs |
|---|--------|---------|----------|----------|------|
| 1 | Farm Structure | ✅ API ready | ⚠️ Needs adaptive UI | 🔴 P1 | `02-backend/farm/`, `04-features/farm-structure/` |
| 2 | Daily Reports / OperationLog | ⚠️ Needs OperationLog refactor | ⚠️ Needs LaborEntry panel | 🔴 P1 | `02-backend/reports/`, `04-features/operation-log-system/` |
| 3 | HR Module | ⚠️ Base models only | ❌ Not built | 🔴 P2 | `02-backend/hr/`, `04-features/hr-system/` |
| 4 | Admin Dashboard | ⚠️ Basic only | ⚠️ Incomplete | 🔴 P2 | `02-backend/auth/` |
| 5 | Warehouse | ⚠️ Basic inventory | ⚠️ Needs alerts UI | 🟡 P3 | `02-backend/warehouse/` |
| 6 | Accounting | ⚠️ Models exist | ⚠️ No real data | 🟡 P3 | `02-backend/accounting/` |
| 7 | Fleet & Equipment | ⚠️ Basic fleet | ⚠️ Needs report link | 🟡 P3 | `02-backend/equipment/` |
| 8 | Crop Records | ❌ Split (Palm+Olive) | ⚠️ Separate pages | 🟢 P4 | `02-backend/` |
| 9 | Production | ⚠️ Basic yield | ⚠️ Needs location link | 🟢 P4 | — |
| 10 | Analytics | ✅ 4 endpoints live | ⚠️ Dashboard exists | 🟡 P3 | `02-backend/reports/ANALYTICS_API.md`, `04-features/analytics/` |

---

## Module Ownership Map

Each module has a designated backend app and frontend feature:

| Module | Backend App | Frontend Feature | Service File |
|--------|-------------|-----------------|--------------|
| Auth & Users | `apps/users` | `features/auth` | `services/user_service.py` |
| Farm & Locations | `apps/farm` | `features/farm` | `services/farm_service.py` |
| Reports / Ops | `apps/reports` | `features/reports` | `services/report_service.py` |
| HR | `apps/hr` | `features/hr` | `services/hr_service.py` |
| Warehouse | `apps/warehouse` | `features/warehouse` | `services/warehouse_service.py` |
| Equipment | `apps/equipment` | `features/equipment` | — |
| Accounting | `apps/accounting` | `features/accounting` | `services/accounting_service.py` |
| Production | `apps/production` | `features/production` | — |

---

## Shared / Cross-Module Entities

These entities are used by multiple modules — they are NOT owned by any single module:

| Entity | Used By |
|--------|---------|
| `LocationNode` | Reports, Analytics, HR, Equipment, Warehouse |
| `Operation` | Reports, Analytics, Accounting |
| `Contractor` | Reports, Accounting, Analytics |
| `Variety` | Reports, CropRecord, Production |
| `Unit` | Reports, Warehouse |
| `Attachment` | Reports, HR |
| `Employee` | HR, Reports (via LaborEntry), Accounting |

---

## Navigation Structure (Sidebar)

```
SIDEBAR
├── Dashboard               (All roles)
├── Farm Structure          (SUPER_ADMIN, OWNER, MANAGER, ENGINEER[read])
├── Daily Reports           (SUPER_ADMIN, OWNER, MANAGER, ENGINEER)
│   ├── Daily Report Form
│   └── Reports List
├── HR                      (SUPER_ADMIN, OWNER, MANAGER, HR)
│   ├── Employees
│   └── Leave Management
├── Warehouse               (SUPER_ADMIN, OWNER, MANAGER, WAREHOUSE)
├── Accounting              (SUPER_ADMIN, OWNER, ACCOUNTANT)
├── Fleet & Equipment       (SUPER_ADMIN, OWNER, MANAGER)
├── Crop Records            (SUPER_ADMIN, OWNER, MANAGER, ENGINEER)
├── Production              (SUPER_ADMIN, OWNER, MANAGER, ENGINEER)
├── Analytics               (SUPER_ADMIN, OWNER, MANAGER)
└── Admin Controls          (SUPER_ADMIN, OWNER, MANAGER[partial])
```
