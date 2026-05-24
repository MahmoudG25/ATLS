# Reporting Engine — Feature Overview

> Feature: Daily Report Creation, Review, and Approval Workflow

---

## What This Feature Does

Manages the full lifecycle of daily farm reports from creation to approval:
1. Engineer creates a `DailyTaskReport` (container)
2. Adds `OperationLog` entries per operation-location pair
3. Adds `LaborEntry` per worker (optionally linked to `Employee`)
4. Attaches photos via Cloudinary
5. Submits report for review
6. Manager reviews and approves or requests correction
7. Report data feeds into Analytics

---

## Report Lifecycle

```
DRAFT → SUBMITTED → APPROVED (or BACK_TO_DRAFT)
```

| Status | Who Sets It | Meaning |
|--------|-------------|---------|
| `draft` | System (on create) | Not yet submitted |
| `submitted` | Engineer | Ready for manager review |
| `approved` | Manager+ | Confirmed and locked |

---

## Key Frontend Pages

```
src/pages/reports/
├── ReportsList.jsx          ← List with filter (status, date, engineer, location)
├── DailyTaskReport/
│   ├── DailyTaskForm.jsx    ← Header: date, farm, notes
│   ├── OperationLogPanel.jsx ← List of OperationLogs + Add button
│   ├── LaborEntryDrawer.jsx  ← Per-worker detail drawer (Phase 2)
│   └── AttachmentUpload.jsx  ← Cloudinary photo upload
└── ReportDetail.jsx         ← Read-only view for manager
```

---

## Key Backend Files

```
apps/reports/models.py           ← DailyTaskReport, OperationLog, LaborEntry, Attachment
services/report_service.py       ← All business logic
api/endpoints/report_views.py    ← Thin API views
serializers/report_serializers.py ← Nested serializers
```

---

## Attachment Handling

All attachments stored on Cloudinary:
```python
class Attachment(TenantAwareModel):
    company      = models.ForeignKey(Company, on_delete=models.CASCADE)
    operation_log = models.ForeignKey(OperationLog, on_delete=models.CASCADE)
    file_url     = models.URLField(max_length=1000)   # Cloudinary secure_url
    file_type    = models.CharField(max_length=20, choices=[('image','Image'),('pdf','PDF')])
    uploaded_at  = models.DateTimeField(auto_now_add=True)
    uploaded_by  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
```

---

## Current Status

| Component | Status |
|-----------|--------|
| DailyTaskReport CRUD | ✅ Working |
| OperationLog model (separate) | ⚠️ May be inline — needs separation per ADR-001 |
| LaborEntry (basic) | ⚠️ Basic version, no HR link |
| Photo attachments | ⚠️ Basic upload |
| Report approval flow | ⚠️ Status field exists, no workflow UI |
| LaborEntry Drawer (Phase 2) | ⬜ Not built |
