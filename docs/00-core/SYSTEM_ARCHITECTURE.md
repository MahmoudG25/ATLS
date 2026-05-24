# System Architecture — ATLS Farm ERP

> **Authority**: Tier 1. The canonical description of system structure.
> See `SOURCE_OF_TRUTH.md` for conflict resolution rules.

---

## 1. System Type

**Event-Driven Multi-Tenant Farm Management SaaS**

- Designed to be sold to any farm (palm, olive, fruit, vegetables) without code changes
- All configuration driven from Admin Dashboard
- Full data isolation per company (tenant)

See `05-decisions/ADR-005-event-driven-farm-erp.md` for why we moved to event-driven.

---

## 2. Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend framework | Django 5+ + Django REST Framework |
| Database | PostgreSQL |
| Authentication | JWT (SimpleJWT) |
| File storage | Cloudinary |
| Frontend framework | React 19 + Vite |
| UI library | Material UI v9 |
| Styling | Tailwind CSS v4 |
| i18n | i18next + react-i18next |
| Forms | react-hook-form + Zod |
| Charts | Recharts |

---

## 3. Core Entity Chain

```
Company
└── Farm
    └── LocationNode (SECTOR → STAGE → ENCLOSURE)
        └── OperationLog  ← THE CORE EVENT ENTITY
            ├── LaborEntry[]
            └── Attachment[]
        └── DailyTaskReport  ← Container for OperationLogs
```

Full entity map:
```
Company
├── User (→ Employee 1:1 for field roles)
│   └── Employee
│       ├── EmployeeAttachment[]
│       ├── LeaveRequest[]
│       └── Attendance[]
├── Farm
│   └── LocationNode (MPTT tree)
│       ├── DailyTaskReport[]
│       │   ├── OperationLog[]  ← atomic events
│       │   │   ├── LaborEntry[] → Employee? (optional link)
│       │   │   └── Attachment[] (Cloudinary)
│       │   ├── FertilizationReport[]
│       │   └── IrrigationReport[]
│       └── CropRecord[] (unified palm + olive)
├── Operation[]             (reusable across system)
├── Contractor[]            (reusable across system)
├── Variety[]               (crop varieties)
├── Unit[]                  (measurement units)
├── WarehouseItem[]
│   └── WarehouseMovement[]
├── Equipment[]
│   └── EquipmentUsageLog[]
├── Expense[]
├── Revenue[]
└── YieldRecord[]
```

---

## 4. LocationNode Hierarchy

LocationNode is the ONLY location model. It unifies all location levels:

```
Farm
└── LocationNode (type=SECTOR)       # قطاع — e.g., "North Sector"
    └── LocationNode (type=STAGE)    # مرحلة — e.g., "Stage A"
        └── LocationNode (type=ENCLOSURE)  # حوشة — e.g., "Enclosure 12"
```

**Rules:**
- Stage is a valid, canonical level — NOT deprecated
- All levels (Sector, Stage, Enclosure) are stored in ONE table: `LocationNode`
- The `type` field (`SECTOR`, `STAGE`, `ENCLOSURE`) determines the level
- No separate `Sector`, `Stage`, or `Plot` tables exist
- See `02-backend/farm/FARM_STRUCTURE.md` for implementation details
- See `05-decisions/ADR-002-locationnode.md` for design rationale

---

## 5. OperationLog as System Core

> OperationLog is the atomic event record. It is the heart of the system.
> DailyTaskReport is a container — a grouping mechanism only.

This means:
- Analytics query `OperationLog`, not `DailyTaskReport`
- Labor costs flow from `OperationLog.LaborEntry`
- Location-based reporting is possible because every `OperationLog` has a `LocationNode`
- Historical audit trail is at the `OperationLog` level

See `00-core/EVENT_DRIVEN_ARCHITECTURE.md` and `05-decisions/ADR-001-operation-log.md`.

---

## 6. Multi-Tenant Architecture

Every piece of data is scoped to a Company:

```python
# Base pattern — every model
class TenantAwareModel(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    class Meta:
        abstract = True

# Base manager — every queryset
class TenantManager(models.Manager):
    def for_company(self, company):
        return self.filter(company=company)
```

See `00-core/TENANT_SYSTEM.md` for full multi-tenant rules.

---

## 7. Backend Architecture Layers

```
Request
  ↓
API View (routing + HTTP handling only)
  ↓
Permission Classes (role + tenant checks)
  ↓
Serializer (data validation + transformation)
  ↓
Service Layer (ALL business logic)
  ↓
Model / ORM (data access)
  ↓
Database (PostgreSQL)
```

Files:
```
api/endpoints/       ← Views
serializers/         ← Serializers
services/            ← Business logic
permissions/         ← Permission classes
apps/                ← Models
core/                ← Base models, settings, utilities
```

---

## 8. Frontend Architecture Layers

```
User Interaction
  ↓
Page Component (smart — orchestrates)
  ↓
UI Components (dumb — renders props)
  ↓
Custom Hooks (state + data fetching)
  ↓
Feature Services (API calls)
  ↓
Axios Instance (JWT + base URL)
  ↓
Backend API
```

Files:
```
src/pages/           ← Page-level components (smart)
src/components/      ← Reusable UI components (dumb)
src/features/        ← Feature-scoped services + hooks
src/contexts/        ← Auth, Theme, Language contexts
src/routes/          ← Route definitions + guards
src/i18n/            ← Translation files
src/theme/           ← MUI theme config
```

---

## 9. Removed / Deprecated Entities

These entities existed in early development and are now voided:

| Entity | Replaced By | Status |
|--------|-------------|--------|
| `Sector` (table) | `LocationNode(type=SECTOR)` | ❌ Deprecated table |
| `Plot` / `Hosh` (table) | `LocationNode(type=ENCLOSURE)` | ❌ Deprecated table |
| `CropType` (table) | `crop_type` field on `CropRecord` | ❌ Deprecated table |
| `PalmRecord` | `CropRecord(crop_type='palm')` | ❌ Deprecated model |
| `OliveRecord` | `CropRecord(crop_type='olive')` | ❌ Deprecated model |
| `ReportDropdownOption` | `Operation`, `Variety`, `Unit` models | ❌ Deprecated model |

> Do NOT use any of these. Do NOT create code that references them.
> Legacy docs in `legacy/old-docs/` describe the old structure for historical reference only.

---

## 10. Role System

| Role | Level | Key Capabilities |
|------|-------|-----------------|
| `SUPER_ADMIN` | 1 | Full access across all companies |
| `OWNER` | 2 | Full access within their company |
| `MANAGER` | 3 | Operational management, partial admin |
| `ENGINEER` | 4 | Create reports, read farm structure |
| `HR` | 5 | HR module full access |
| `ACCOUNTANT` | 5 | Accounting module full access |
| `WAREHOUSE` | 5 | Warehouse module full access |

For full permission matrix see `00-core/PERMISSIONS.md`.

---

## 11. Final Design Goals

The system must always be:
- **Scalable** — new modules without core changes
- **Clean** — logic in services, not scattered
- **Reusable** — entities shared across modules
- **Analytics-ready** — every model supports filtering/grouping/aggregation
- **Sellable** — SaaS-configurable per farm type without code changes
- **AI-safe** — documented enough for AI agents to work without confusion
