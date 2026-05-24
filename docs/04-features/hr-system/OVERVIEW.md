# HR System — Feature Overview

> Feature: Employee Management, Leaves, and Attendance
> Phase: 3 (Backend) + Phase 4 (Frontend) — see `01-product/ROADMAP.md`

---

## What This Feature Does

Manages all human resources within the farm company:
- Employee records with personal/professional details
- File attachments (ID scans, contracts, certificates) via Cloudinary
- Leave request and approval workflow
- Daily attendance tracking
- Integration with LaborEntry (field workers linked to Employee records)

**Business value (Arabic):**
> إدارة كاملة للموظفين: بياناتهم، إجازاتهم، حضورهم،
> ومستنداتهم — كلها في مكان واحد، مربوطة بتقارير العمل الميداني.

---

## User Flows

### HR Officer Flow
1. View employee list (search, filter by status/department)
2. Open employee detail: 4 tabs (Info, Attachments, Attendance, Leaves)
3. Upload employee document → stored on Cloudinary
4. Review and approve/reject leave requests
5. Log daily attendance

### Manager Flow
1. View HR dashboard: KPI cards (active employees, pending leaves, absences)
2. Approve leave requests
3. View employee profiles (read-only)

### Engineer Flow
1. View their own profile (read-only)
2. Submit leave request

---

## Key Entities

| Entity | Role |
|--------|------|
| `Employee` | Core HR record (linked 1:1 to User for field roles) |
| `EmployeeAttachment` | Cloudinary-stored file linked to employee |
| `LeaveRequest` | Leave approval workflow |
| `Attendance` | Daily check-in/check-out record |

---

## Backend Files
```
apps/hr/models.py                   ← Employee, Attachment, Leave, Attendance
serializers/hr_serializers.py       ← CRUD serializers
services/hr_service.py              ← Business logic
api/endpoints/hr_views.py           ← API views
```
Reference: `02-backend/hr/HR_MODULE.md`

---

## Frontend Files (Planned)
```
src/pages/hr/
├── HRDashboard.jsx         ← KPI cards
├── EmployeeList.jsx        ← Table with search/filter
├── EmployeeDetail.jsx      ← 4-tab detail page
└── LeaveManagement.jsx     ← Approve/reject flow
src/features/hr/services.js ← API calls
```

---

## Cloudinary File Upload

Files are uploaded directly from the frontend to Cloudinary using an unsigned preset.
The frontend receives the `secure_url` and sends it to the backend via `EmployeeAttachment` API.

```javascript
// Frontend upload flow
const result = await cloudinary.upload(file, { upload_preset: 'REDACTED_PRESET' })
await hrService.addAttachment(employeeId, { file_url: result.secure_url, name: file.name })
```

---

## Current Status

| Component | Status |
|-----------|--------|
| Employee model (base) | ✅ |
| Extended fields (Phase 3) | ⬜ Not added |
| EmployeeAttachment model | ⬜ Not added |
| LeaveRequest model | ⬜ Not added |
| Attendance model | ⬜ Not added |
| Full CRUD endpoints | ⬜ Not built |
| Frontend pages | ⬜ Not built |
