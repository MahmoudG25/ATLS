# Permissions — ATLS Farm ERP

> **Authority**: Tier 2. Defines the full role permission matrix.

---

## 1. Role Definitions

| Role | Backend Value | Description |
|------|--------------|-------------|
| Super Admin | `SUPER_ADMIN` | Full access across ALL companies. System-level. |
| Owner | `OWNER` | Full access within their company. |
| Manager | `MANAGER` | Operational management. Partial admin. |
| Engineer | `ENGINEER` | Field operations. Create reports. |
| HR Officer | `HR` | HR module full access. |
| Accountant | `ACCOUNTANT` | Accounting module full access. |
| Warehouse Officer | `WAREHOUSE` | Warehouse module full access. |

Hierarchy: `SUPER_ADMIN > OWNER > MANAGER > ENGINEER > HR / ACCOUNTANT / WAREHOUSE`

---

## 2. Module Permission Matrix

| Feature | SUPER_ADMIN | OWNER | MANAGER | ENGINEER | HR | ACCOUNTANT | WAREHOUSE |
|---------|:-----------:|:-----:|:-------:|:--------:|:--:|:----------:|:---------:|
| Admin Dashboard | ✅ Full | ✅ Full | ✅ Partial | ❌ | ❌ | ❌ | ❌ |
| Farm Structure | ✅ | ✅ | ✅ | 👁️ Read | ❌ | ❌ | ❌ |
| Daily Reports | ✅ | ✅ | ✅ | ✅ Create | ❌ | 👁️ | ❌ |
| Operation Logs | ✅ | ✅ | ✅ | ✅ Create | ❌ | 👁️ | ❌ |
| HR Module | ✅ | ✅ | ✅ Partial | 👁️ Own file | ✅ Full | ❌ | ❌ |
| Warehouse | ✅ | ✅ | ✅ | ❌ | ❌ | 👁️ | ✅ Full |
| Accounting | ✅ | ✅ | 👁️ | ❌ | ❌ | ✅ Full | ❌ |
| Fleet/Equipment | ✅ | ✅ | ✅ | 👁️ | ❌ | ❌ | ❌ |
| Crop Records | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Production | ✅ | ✅ | ✅ | ✅ | ❌ | 👁️ | ❌ |
| Analytics | ✅ | ✅ | ✅ | 👁️ | ❌ | 👁️ | ❌ |
| Custom Fields | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |

---

## 3. Admin Dashboard Sub-Permissions

| Admin Section | SUPER_ADMIN | OWNER | MANAGER |
|---------------|:-----------:|:-----:|:-------:|
| Users | ✅ Full | ✅ Full | ✅ No delete |
| CMS | ✅ | ✅ | ❌ |
| Custom Fields | ✅ | ✅ | ✅ |
| Operations (types) | ✅ | ✅ | ✅ |
| Contractors | ✅ | ✅ | ✅ |
| Report Dropdowns | ✅ | ✅ | ✅ |
| Crop Types | ✅ | ✅ | ❌ |
| Company Settings | ✅ | ✅ | ❌ |

---

## 4. Backend Permission Classes

Location: `permissions/role_permissions.py`

```python
# Available permission classes
IsEngineerOrAbove    # ENGINEER, MANAGER, OWNER, SUPER_ADMIN
IsManagerOrAbove     # MANAGER, OWNER, SUPER_ADMIN
IsOwnerOrAbove       # OWNER, SUPER_ADMIN
IsSuperAdmin         # SUPER_ADMIN only
IsHROrAbove          # HR, MANAGER, OWNER, SUPER_ADMIN
IsAccountantOrAbove  # ACCOUNTANT, MANAGER, OWNER, SUPER_ADMIN
IsWarehouseOrAbove   # WAREHOUSE, MANAGER, OWNER, SUPER_ADMIN
```

Usage:
```python
class ReportCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsEngineerOrAbove]
```

---

## 5. Frontend Role Guards

```javascript
// Route-level guard
const ROLE_PERMISSIONS = {
  '/admin':     ['SUPER_ADMIN', 'OWNER', 'MANAGER'],
  '/hr':        ['SUPER_ADMIN', 'OWNER', 'MANAGER', 'HR'],
  '/warehouse': ['SUPER_ADMIN', 'OWNER', 'MANAGER', 'WAREHOUSE'],
  '/accounting':['SUPER_ADMIN', 'OWNER', 'ACCOUNTANT'],
  '/reports':   ['SUPER_ADMIN', 'OWNER', 'MANAGER', 'ENGINEER'],
  '/farm':      ['SUPER_ADMIN', 'OWNER', 'MANAGER', 'ENGINEER'],
}

// Component-level guard
const { user } = useAuth()
{['MANAGER', 'OWNER', 'SUPER_ADMIN'].includes(user.role) && (
  <Button>Delete</Button>
)}
```

---

## 6. Key Rules

1. **Never trust frontend** — all permission checks duplicated in backend
2. **SUPER_ADMIN** bypasses tenant isolation — sees all companies
3. **ENGINEER** can read farm structure but cannot modify it
4. **Unapproved users** (`is_approved=False`) cannot login at all
5. **Object-level permissions** — engineers can only edit their own reports
6. Permissions are **additive** — higher roles inherit lower role permissions
