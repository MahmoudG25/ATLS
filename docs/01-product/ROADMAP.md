# Roadmap — ATLS Farm ERP

> Implementation phases ordered by priority. Updated: 2026-05.

---

## Phase Status Key

| Symbol | Meaning |
|--------|---------|
| ✅ | Complete |
| ⚠️ | Exists but needs improvement |
| 🔴 | In progress / high priority |
| 🟡 | Medium priority |
| 🟢 | Lower priority |
| ❌ | Not started |

---

## 🔴 PHASE 1 — Farm Structure Adaptive UI

**Goal**: Transform the static farm tree into an adaptive, dynamic UI.

**Deliverables:**
- `FarmStructure.jsx` — adaptive node sizing based on sibling count
- `FarmStructure.css` — size classes (lg/md/sm/xs)
- Collapse/Expand per branch
- Search/filter by name
- Count badges on parent nodes
- Horizontal scroll for wide trees

**Status**: ⚠️ Partially implemented — see `04-features/farm-structure/PHASE_01.md`

**Rules:**
- No backend changes — API exists and works
- Node size scales with sibling count: 1-3 → lg, 4-6 → md, 7-12 → sm, 13+ → xs
- Enclosure grid: 1-4 → 2 cols, 5-8 → 3 cols, 9-12 → 4 cols, 13+ → 5 cols

---

## 🔴 PHASE 2 — LaborEntry Inline Panel

**Goal**: Engineers can add per-worker detail directly in the daily report form.

**Deliverables:**
- `LaborEntryDrawer.jsx` — bottom drawer with worker table
- HR search integration — autocomplete from `Employee` model
- `LaborEntry.employee` FK (optional, links to HR)
- `/hr/employees/search/?q=` endpoint

**Status**: ❌ Not started

---

## 🔴 PHASE 3 — HR Module (Backend)

**Goal**: Complete HR backend.

**Deliverables:**
- `Employee` model extended: `address`, `national_id`, `phone`, `emergency_contact_*`, `avatar_url`
- `EmployeeAttachment` model (Cloudinary URLs)
- Auto-create `Employee` when `ENGINEER`/`MANAGER`/`HR`/`ACCOUNTANT`/`WAREHOUSE` user registers
- Full CRUD endpoints: `/hr/employees/`, `/hr/leaves/`, `/hr/attendance/`

**Status**: ⚠️ Base models exist — endpoints and extensions needed

---

## 🔴 PHASE 4 — HR Module (Frontend)

**Goal**: Full HR management UI.

**Deliverables:**
- `HRDashboard.jsx` — KPI cards
- `EmployeeList.jsx` — table with search/filter
- `EmployeeDetail.jsx` — 4 tabs: Info, Attachments, Attendance, Leaves
- `LeaveManagement.jsx` — approve/reject flow

**Status**: ❌ Not started

---

## 🔴 PHASE 5 — Sidebar + Navigation

**Goal**: Role-based sidebar navigation.

**Deliverables:**
- `Sidebar.jsx` — permanent 260px sidebar, role-filtered menu items
- `DashboardLayout.jsx` — updated to use sidebar
- `AppRoutes.jsx` — all routes with role guards

**Status**: ⚠️ Basic sidebar exists — role filtering incomplete

---

## 🔴 PHASE 6 — Admin Dashboard

**Goal**: Full configurable admin panel.

**Deliverables:**
- Operations Admin, Contractors Admin, Dropdowns Admin
- Custom Fields Admin (Drag & Drop field ordering)
- Crop Types Admin (for SaaS multi-crop support)
- Company Settings

**Status**: ⚠️ Basic user management exists — full admin not complete

---

## 🟡 PHASE 7 — Warehouse

**Goal**: Complete warehouse with low-stock alerts.

**Deliverables:**
- `category`, `unit`, `min_stock`, `location` fields on `WarehouseItem`
- `/warehouse/alerts/` and `/warehouse/summary/` endpoints
- `LowStockAlerts.jsx`, `WarehouseSummary.jsx`

**Status**: ⚠️ Basic inventory exists

---

## 🟡 PHASE 8 — Accounting

**Goal**: Real financial data integration.

**Deliverables:**
- `/accounting/payroll/` — salaries from HR
- `/accounting/labor-costs/` — from OperationLog × LaborEntry
- `/accounting/location-costs/` — cost per LocationNode
- `PayrollPage.jsx`, `CostAnalysis.jsx`

**Status**: ⚠️ Basic Expense/Revenue models exist

---

## 🟡 PHASE 9 — Fleet & Equipment

**Goal**: Tie equipment usage to reports.

**Deliverables:**
- `EquipmentUsageLog` model (links equipment to OperationLog)
- `assigned_location` FK on Equipment
- `UsageAnalytics.jsx`, `MaintenanceLog.jsx`

**Status**: ⚠️ Basic fleet UI exists

---

## 🟢 PHASE 10 — CropRecord Unification

**Goal**: Replace PalmRecord + OliveRecord with unified CropRecord.

**Deliverables:**
- `CropRecord(crop_type='palm'|'olive'|...)` model
- `CropRecords.jsx` — unified page with type filter
- Migration from old models

**Status**: ❌ Not started (PalmRecord + OliveRecord still exist)

---

## 🟢 PHASE 11 — Production

**Goal**: Link yield records to locations and crop records.

**Deliverables:**
- `location`, `crop_type`, `variety`, `season` fields on `YieldRecord`
- `HarvestCalendar.jsx`, `YieldAnalytics.jsx`

**Status**: ⚠️ Basic YieldTracking exists
