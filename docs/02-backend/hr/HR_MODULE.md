# HR Module — Backend Reference

> Based on Phase 3 specification from the master plan.

---

## 1. Models

### Employee
```python
class Employee(TenantAwareModel):
    STATUS_CHOICES = [('active','Active'),('inactive','Inactive'),('terminated','Terminated')]

    company    = models.ForeignKey(Company, on_delete=models.CASCADE)
    user       = models.OneToOneField(settings.AUTH_USER_MODEL,
                                       on_delete=models.CASCADE, related_name='employee')
    hire_date  = models.DateField()
    department = models.CharField(max_length=100, blank=True)
    position   = models.CharField(max_length=100, blank=True)
    salary     = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    # Extended fields (Phase 3)
    address                = models.TextField(blank=True, default='')
    national_id            = models.CharField(max_length=20, blank=True)
    phone                  = models.CharField(max_length=20, blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone= models.CharField(max_length=20, blank=True)
    avatar_url             = models.URLField(max_length=500, blank=True)
```

### EmployeeAttachment
```python
class EmployeeAttachment(TenantAwareModel):
    FILE_TYPE_CHOICES = [('image','Image'),('pdf','PDF'),('other','Other')]
    company     = models.ForeignKey(Company, on_delete=models.CASCADE)
    employee    = models.ForeignKey(Employee, on_delete=models.CASCADE,
                                     related_name='attachments')
    name        = models.CharField(max_length=200)
    file_url    = models.URLField(max_length=1000)  # Cloudinary URL
    file_type   = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                     null=True)
```

### LeaveRequest
```python
class LeaveRequest(TenantAwareModel):
    LEAVE_TYPES = [('annual','Annual'),('sick','Sick'),('personal','Personal')]
    STATUS      = [('pending','Pending'),('approved','Approved'),('rejected','Rejected')]

    company     = models.ForeignKey(Company, on_delete=models.CASCADE)
    employee    = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leave_type  = models.CharField(max_length=20, choices=LEAVE_TYPES)
    start_date  = models.DateField()
    end_date    = models.DateField()
    reason      = models.TextField(blank=True)
    status      = models.CharField(max_length=20, choices=STATUS, default='pending')
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                     on_delete=models.SET_NULL)
```

### Attendance
```python
class Attendance(TenantAwareModel):
    STATUS = [('present','Present'),('absent','Absent'),('late','Late'),('half_day','Half Day')]
    company   = models.ForeignKey(Company, on_delete=models.CASCADE)
    employee  = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date      = models.DateField()
    check_in  = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    status    = models.CharField(max_length=20, choices=STATUS, default='present')

    class Meta:
        unique_together = ['employee', 'date']
```

---

## 2. API Endpoints

```
GET    /hr/employees/                   list (filter: status, department, search)
POST   /hr/employees/                   create employee record
GET    /hr/employees/{id}/              full detail
PATCH  /hr/employees/{id}/              update
DELETE /hr/employees/{id}/              soft delete (status=terminated)

GET    /hr/employees/{id}/attachments/  list files
POST   /hr/employees/{id}/attachments/  upload file (Cloudinary URL + metadata)
DELETE /hr/attachments/{id}/            delete file

GET    /hr/employees/search/?q=name     autocomplete for LaborEntry

GET    /hr/leaves/                      list (filter: status, employee, date)
POST   /hr/leaves/                      create leave request
PATCH  /hr/leaves/{id}/approve/         approve
PATCH  /hr/leaves/{id}/reject/          reject

GET    /hr/attendance/                  list (filter: date, employee)
POST   /hr/attendance/                  log attendance
PATCH  /hr/attendance/{id}/             update
```

---

## 3. Auto-Creation Rule

When a User registers with a field role, `Employee` is auto-created:
```python
FIELD_ROLES = ['ENGINEER', 'MANAGER', 'HR', 'ACCOUNTANT', 'WAREHOUSE']
```
See `02-backend/auth/AUTH_SYSTEM.md` for implementation.

---

## 4. File Storage

- Files stored on Cloudinary (no local storage)
- Only `file_url` (Cloudinary `secure_url`) is stored in DB
- Accepted formats: `jpg`, `jpeg`, `png`, `webp`, `pdf`
- Upload via unsigned preset from Frontend or via backend API
