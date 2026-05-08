# Domain Language — Canonical Terminology

> **Authority**: Tier 1. This document is the single source of truth for naming.
> Any AI agent, developer, or documentation author MUST use the terms defined here.
> Deviating from this glossary constitutes a terminology drift violation.

---

## 1. Core Entity Names

| Canonical Term | Arabic | Context | Forbidden Alternatives |
|----------------|--------|---------|------------------------|
| `Company` | شركة | Root tenant entity | `Organization`, `Tenant`, `Client` |
| `Farm` | مزرعة | Belongs to Company | `Ranch`, `Site`, `Property` |
| `LocationNode` | عقدة الموقع | Universal location model | `Location`, `Place`, `Area`, `Node` |
| `Sector` | قطاع | LocationNode level 1 | `Zone`, `Region`, `Area` |
| `Stage` | مرحلة | LocationNode level 2 | `Phase`, `Block`, `Zone` |
| `Enclosure` | حوشة | LocationNode level 3 | `Plot`, `Hosh`, `Cell`, `Unit`, `Pen` |
| `OperationLog` | سجل العمليات | Atomic event record | `Task`, `Activity`, `Log`, `Entry` |
| `DailyTaskReport` | التقرير اليومي | Container grouping OperationLogs | `Report`, `DailyReport`, `WorkOrder` |
| `LaborEntry` | إدخال العمالة | Worker record per operation | `WorkerEntry`, `LabourRecord` |
| `Operation` | عملية | Business operation type | `Task`, `Activity`, `Job`, `Work` |
| `Contractor` | مقاول | External labor provider | `Vendor`, `Supplier`, `SubContractor` |
| `Employee` | موظف | Internal staff member | `Worker`, `Staff`, `User` (when HR context) |
| `User` | مستخدم | System auth identity | `Account`, `Member`, `Person` |
| `Variety` | صنف | Crop variety/cultivar | `Type`, `Kind`, `Species` |
| `CropRecord` | سجل المحصول | Unified crop model | `PalmRecord`, `OliveRecord` (deprecated) |
| `Attachment` | مرفق | File linked to report | `File`, `Document`, `Media` |

---

## 2. LocationNode Type System

LocationNode uses a `type` field with these exact values:

```python
class LocationNodeType(models.TextChoices):
    SECTOR    = 'SECTOR',    'Sector'     # Arabic: قطاع
    STAGE     = 'STAGE',     'Stage'      # Arabic: مرحلة
    ENCLOSURE = 'ENCLOSURE', 'Enclosure'  # Arabic: حوشة
```

**Hierarchy**:
```
Farm
└── LocationNode (type=SECTOR)       ← القطاع
    └── LocationNode (type=STAGE)    ← المرحلة
        └── LocationNode (type=ENCLOSURE)  ← الحوشة
```

> **IMPORTANT**: Stage is NOT deprecated. Stage is a valid, canonical level in the LocationNode hierarchy.
> Do NOT create separate `Stage` or `Sector` database tables. All levels live in `LocationNode`.

---

## 3. Module Names

| Module | Canonical Name | Arabic | Forbidden |
|--------|---------------|--------|-----------|
| Reports module | `reports` | التقارير | `logs`, `tasks` |
| Farm module | `farm` | المزرعة | `fields`, `sites` |
| HR module | `hr` | الموارد البشرية | `staff`, `personnel` |
| Accounting module | `accounting` | المحاسبة | `finance`, `billing` |
| Warehouse module | `warehouse` | المخازن | `inventory`, `stock` |
| Equipment module | `equipment` | الأسطول والمعدات | `fleet`, `assets` |
| Analytics module | `analytics` | التحليلات | `metrics`, `stats` |
| Production module | `production` | المحصول | `yield`, `harvest` |

---

## 4. Role Names

These must match exactly the backend enum values:

| Role | Display (EN) | Display (AR) | Backend Value |
|------|-------------|-------------|---------------|
| Super Admin | Super Admin | مدير النظام | `SUPER_ADMIN` |
| Owner | Owner | مالك | `OWNER` |
| Manager | Manager | مدير | `MANAGER` |
| Engineer | Engineer | مهندس | `ENGINEER` |
| HR | HR Officer | موارد بشرية | `HR` |
| Accountant | Accountant | محاسب | `ACCOUNTANT` |
| Warehouse | Warehouse Officer | أمين مخزن | `WAREHOUSE` |

---

## 5. Report Terminology

| Term | Meaning | Arabic |
|------|---------|--------|
| `report_date` | Date the work was performed | تاريخ العمل |
| `company_workers` | Number of internal company workers | عمال الشركة |
| `contractor_workers` | Number of contractor workers | عمال المقاول |
| `actual_productivity` | Measured output for the operation | الإنتاجية الفعلية |
| `work_hours` | Total hours worked | ساعات العمل |

---

## 6. API URL Conventions

| Pattern | Correct | Wrong |
|---------|---------|-------|
| Resource list | `/api/reports/` | `/api/get-reports/`, `/api/reportsList/` |
| Resource detail | `/api/reports/{id}/` | `/api/report/?id=1` |
| Nested resource | `/api/reports/{id}/labor-entries/` | `/api/labor-entries/?report=1` |
| Analytics | `/api/analytics/kpi/` | `/api/analytics/getKPI/` |
| Custom action | `/api/reports/{id}/approve/` | `/api/approveReport/{id}/` |

---

## 7. File & Folder Naming

### Backend (Python)
```
models.py          ← always singular, lowercase
views.py           ← always singular
serializers/       ← plural folder
services/          ← plural folder
user_service.py    ← module_service.py pattern
report_service.py
```

### Frontend (React)
```
components/        ← plural folder, PascalCase files
  EmployeeCard.jsx ← PascalCase
  LaborTable.jsx
services.js        ← singular, camelCase functions
hooks.js           ← singular, useSomething() convention
  useEmployees.js
pages/
  EmployeeList.jsx
  EmployeeDetail.jsx
```

---

## 8. Forbidden Terms — Never Use These

> These terms exist in legacy code/docs but must not appear in new code or documentation.

| Forbidden | Use Instead | Reason |
|-----------|-------------|--------|
| `Plot` | `Enclosure` (LocationNode type=ENCLOSURE) | Replaced by LocationNode |
| `Hosh` | `Enclosure` | Arabic transliteration — not canonical |
| `CropType` | `Variety` or `crop_type` field | Deprecated table |
| `Sector` (as table) | `LocationNode` with `type=SECTOR` | Unified in LocationNode |
| `Stage` (as table) | `LocationNode` with `type=STAGE` | Unified in LocationNode |
| `PalmRecord` | `CropRecord(crop_type='palm')` | Merged model |
| `OliveRecord` | `CropRecord(crop_type='olive')` | Merged model |
| `ReportDropdownOption` | `Operation`, `Variety`, `Unit` models | Replaced by proper entities |
| `DailyTask` | `DailyTaskReport` or `OperationLog` | Full name required |
| `task` | `operation` | Wrong domain term |
| `hardcoded` anything | Use DB-driven configuration | Anti-SaaS |

---

## 9. Arabic ↔ English Quick Reference

| English | Arabic | Notes |
|---------|--------|-------|
| Farm Structure | هيكل المزرعة | Navigation label |
| Daily Report | التقرير اليومي | Page title |
| Operation Log | سجل العمليات | Core entity |
| Farm Hierarchy | الهيكل الهرمي | Tree view title |
| Labor Entry | إدخال العمالة | Form label |
| Productivity | الإنتاجية | Analytics metric |
| Approve | موافقة | Action button |
| Reject | رفض | Action button |
| Pending | قيد الانتظار | Status badge |
| Active | نشط | Status badge |
| Terminated | منتهي | HR status |
