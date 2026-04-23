# Atlas Farm ERP — Changelog & Accomplishments

> **Date**: April 23, 2026  
> **Scope**: Full implementation of the 16-point Development Plan

---

## 🔴 Phase 1 — Critical / Blocking

### 1.1 Fixed Admin Route RBAC Bug
- **Problem**: The `/admin` route used `requireModule="all"`, but `hasAccess(user, 'all')` always returned `false` for non-SUPER_ADMIN roles — making it impossible for OWNER and MANAGER to access the admin panel.
- **Solution**: Added a new `requireRoles` prop to `ProtectedRoute` and switched the admin route to use explicit role-based checking: `['SUPER_ADMIN', 'OWNER', 'MANAGER']`.
- **File changed**: `Front-End/src/routes/AppRoutes.jsx`

### 1.2 Backend `.env` Security Hardening
- **Problem**: `settings.py` had hardcoded fallback values for `SECRET_KEY` (`'django-insecure-fallback-key'`) and `DB_PASSWORD` (`'123'`), creating a security risk in production.
- **Solution**: Introduced a `get_env_variable()` helper that raises `ImproperlyConfigured` if critical environment variables are missing. Added `ALLOWED_HOSTS` to `.env` and `.env.example`.
- **Files changed**: `Back-End/core/settings.py`, `Back-End/.env`, `Back-End/.env.example`

### 1.3 Error Boundary — Per-Route Wrapping & Production Safety
- **Problem**: Error details (`error.toString()`) were leaked to end-users in production. The `ErrorBoundary` was a single wrapper in `DashboardLayout`, meaning any crash brought down the whole shell.
- **Solution**: 
  - Error details are now hidden in production (`import.meta.env.PROD`).
  - Added a **"إعادة المحاولة" (Retry)** button alongside the home button.
  - Every route is now individually wrapped with `<ErrorBoundary>`, so a crash in one page doesn't affect the sidebar or other routes.
- **Files changed**: `Front-End/src/components/ErrorBoundary.jsx`, `Front-End/src/routes/AppRoutes.jsx`

### 1.4 Admin Controls — Search, Filter & Delete Confirmation
- Added a **search bar** (name/email), **role filter**, and **status filter** (Pending / Active / Deactivated) to the user management tab.
- Replaced the browser-native `window.confirm()` with a professional **MUI Dialog** for delete confirmation.
- Added empty state UI when no users match the search.
- **File changed**: `Front-End/src/pages/admin/AdminControls.jsx`

---

## 🟠 Phase 2 — High Priority

### 2.1 User Profile — Enhanced Identity & Password Strength
- Backend: Exposed `last_login` and `date_joined` fields in `UserSerializer`.
- Frontend: 
  - Profile header now displays **joined date** and **last login** with `CalendarToday` / `AccessTime` icons.
  - Identity tab shows read-only fields (email, role, joined, last login) in a styled card.
  - Security tab now includes a **real-time password strength meter** (5 levels: ضعيفة جداً → قوية جداً) using `LinearProgress`.
  - Fixed a CSS class typo (`flexitems-center` → `flex items-center`) in the settings tab.
- **Files changed**: `Back-End/serializers/user_serializers.py`, `Front-End/src/pages/auth/UserProfile.jsx`

### 2.2 Navbar Dropdown — Enhanced Menu
- Added a **mini profile header** (avatar + name + role) at the top of the dropdown.
- Added **Account Settings** menu item linking to `/profile`.
- Added **Language toggle** (عربي / English) directly in the dropdown.
- Integrated Escape key handler for accessibility.
- **File changed**: `Front-End/src/layouts/DashboardTopbar.jsx`

### 2.3 Mobile PWA Support
- Created `public/manifest.json` with app name, theme color (`#16a34a`), and display mode.
- Added `<meta>` tags to `index.html`: `theme-color`, `apple-mobile-web-app-capable`, `apple-mobile-web-app-status-bar-style`, `apple-mobile-web-app-title`, and `<link rel="manifest">`.
- **Files created**: `Front-End/public/manifest.json`  
- **Files changed**: `Front-End/index.html`

### 2.4 Notifications System (Full Stack)
- **Backend**:
  - New `Notification` model in `apps/users/models.py` with types: `user_pending`, `low_stock`, `invoice`, `leave_request`, `system`.
  - Service layer in `services/notification_service.py` with: `get_user_notifications`, `get_unread_count`, `mark_notification_read`, `mark_all_read`, `create_notification`, `notify_admins_new_user`.
  - API endpoints in `api/endpoints/notification_views.py`: `GET /notifications/`, `PATCH /notifications/{id}/read/`, `PATCH /notifications/read-all/`.
  - Auto-triggers: admins are notified when a new user registers.
- **Frontend**:
  - API service in `features/notifications/services.js`.
  - `NotificationBell` component with unread badge, dropdown list, mark-as-read, mark-all-read, 60-second polling, and relative time display.
  - Integrated into `DashboardTopbar.jsx`.
- **Migration**: `users.0003_notification`

### 2.5 Reusable Search, Filter & Pagination Components
- Created `TableToolbar.jsx` — configurable search input + dynamic filter dropdowns + clear button.
- Created `TablePagination.jsx` — result range display, rows-per-page selector (10/25/50), page navigation.
- Both components are translation-ready and designed for use across all module tables.
- **Files created**: `Front-End/src/components/TableToolbar.jsx`, `Front-End/src/components/TablePagination.jsx`

---

## 🟡 Phase 3 — Medium Priority

### 3.1 Form Validation (React Hook Form + Zod)
- Installed `react-hook-form`, `zod`, and `@hookform/resolvers`.
- Migrated **Register** page to use `Controller` components with `zodResolver`. Validation rules:
  - Name: min 2 characters
  - Email: valid email format
  - Role: required
  - Password: min 8 characters
- Migrated **Login** page with the same pattern.
- All validation messages are in Arabic by default.
- Submit buttons auto-disable during submission via `isSubmitting`.
- **Files changed**: `Front-End/src/pages/auth/Register.jsx`, `Front-End/src/pages/auth/Login.jsx`

### 3.2 Accounting Module — Invoices & Salary
- Added `Invoice` model with fields: `invoice_number`, `type` (purchase/sales), `status` (draft/sent/paid/cancelled), `party_name`, `issue_date`, `due_date`, `total_amount`, `notes`, `created_by`.
- Added `InvoiceItem` model with auto-calculated `total` (`quantity × unit_price`).
- Added `__str__` method to `Salary` model.
- **Migration**: `accounting.0002_invoice_invoiceitem`
- **File changed**: `Back-End/apps/accounting/models.py`

### 3.3 HR Module (New)
- Created new Django app: `apps/hr`
- **Models**:
  - `Employee` — linked to `User` via `OneToOneField`, with `hire_date`, `department`, `position`, `salary`, `status`.
  - `LeaveRequest` — with `leave_type` (annual/sick/personal), approval workflow (`pending/approved/rejected`), `reviewed_by`.
  - `Attendance` — daily log with `check_in`, `check_out`, `status` (present/absent/late/half_day), unique constraint on `[employee, date]`.
- **Service layer**: `services/hr_service.py` with CRUD for employees, leave requests, and attendance.
- **Migration**: `hr.0001_initial`
- **Files created**: `Back-End/apps/hr/models.py`, `Back-End/apps/hr/apps.py`, `Back-End/services/hr_service.py`

---

## 🟢 Phase 4 — Lower Priority

### 4.1 Charts & Analytics
- Installed `recharts`.
- Created reusable chart components in `Front-End/src/components/Charts.jsx`:
  - `AreaChartCard` — gradient fill area chart for trends
  - `BarChartCard` — rounded bar chart for comparisons
  - `PieChartCard` — donut chart with legend for categories
- All charts are responsive, RTL-compatible, and use consistent color palette.

### 4.2 Print & Export
- Installed `xlsx` and `file-saver`.
- Created `Front-End/src/utils/export.js` with:
  - `exportToExcel(data, filename)` — generates `.xlsx` file
  - `exportToCSV(data, filename)` — generates `.csv` with BOM for Excel Arabic support
  - `printPage(elementId)` — opens print dialog for specific element or whole page

### 4.3 Production Readiness
- Added `DEFAULT_PAGINATION_CLASS` and `PAGE_SIZE: 25` to DRF settings.
- Configured `STATIC_ROOT` and `MEDIA_ROOT` for deployment.
- **File changed**: `Back-End/core/settings.py`

---

## Database Migrations Summary

| Migration | Description |
|-----------|-------------|
| `users.0003_notification` | Notification model for alerts |
| `accounting.0002_invoice_invoiceitem` | Invoice + InvoiceItem models |
| `hr.0001_initial` | Employee, LeaveRequest, Attendance |

## New Dependencies

### Frontend (`npm`)
| Package | Purpose |
|---------|---------|
| `react-hook-form` | Form state management |
| `zod` | Schema validation |
| `@hookform/resolvers` | Zod ↔ RHF bridge |
| `recharts` | Chart components |
| `xlsx` | Excel/CSV generation |
| `file-saver` | File download trigger |

### Backend
No new pip packages — all features use Django/DRF built-ins.

---

## Architecture Rules Compliance

| Rule | Status |
|------|--------|
| Thin views, fat services | ✅ All new logic in service files |
| No API calls in UI components | ✅ All calls in `features/*/services.js` |
| No inline styles | ✅ MUI `sx` + Tailwind |
| Module isolation | ✅ Each feature in its own directory |
| JWT authentication | ✅ Existing interceptor reused |
| `select_related` for queries | ✅ Used in all service queries |
| Role-based permissions | ✅ Backend + frontend enforced |
