# AI Agent Rules — ATLS Farm ERP

> **Authority**: Tier 1. Every AI agent MUST read this file first. No exceptions.

---

## 0. Mandatory First Steps

Before writing ANY code:
1. Read `00-core/SOURCE_OF_TRUTH.md` — which doc wins on conflict
2. Read `00-core/DOMAIN_LANGUAGE.md` — correct terminology
3. Read `00-core/SYSTEM_ARCHITECTURE.md` — system boundaries
4. Read `00-core/DATABASE_RULES.md` — model rules
5. Identify the module being modified
6. Confirm no existing model/service covers the need

**Skipping these steps = invalid output.**

---

## 1. Django Rules

### App Structure (canonical)
```
apps/users, farm, reports, hr, warehouse, equipment, accounting, production
api/endpoints/<module>_views.py
serializers/<module>_serializers.py
services/<module>_service.py
permissions/role_permissions.py
```

### Model Rules
```python
# ✅ Every model inherits TenantAwareModel + has company FK
class MyModel(TenantAwareModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

# ❌ Never — model without company
class MyModel(models.Model):
    name = models.CharField(...)
```

- Use ForeignKey, not raw integer IDs
- Always use `select_related()` / `prefetch_related()`
- Add `Meta.indexes` on `company`, `date`, `status` fields
- No `GenericForeignKey` unless in CustomField system
- No duplicate models — check first

### Migration Rules
- Never delete migrations. Add new ones only.
- Name descriptively: `0004_add_employee_fk_to_laborentry`

---

## 2. DRF / API Rules

### Thin Views — Always
```python
# ✅ View calls service only
class ReportCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsEngineerOrAbove]
    def perform_create(self, serializer):
        report_service.create_report(serializer.validated_data, self.request.user)

# ❌ Business logic in view — VIOLATION
class ReportCreateView(APIView):
    def post(self, request):
        # 50 lines of logic here
```

### Serializer Rules
- One serializer per use-case (List / Detail / Create / Update)
- Serializers validate data only — no business logic
- Always validate tenant scoping in FK fields

### URL Naming
```python
# ✅ Correct
path('reports/', ReportListView.as_view())
path('reports/<int:pk>/labor-entries/', ...)
path('reports/<int:pk>/approve/', ...)

# ❌ Wrong
path('getReports/', ...)
path('reportDetail/', ...)
```

---

## 3. Services Layer Rules

### Architecture
```
View → Serializer (validate) → Service (business logic) → Model (data)
```

Every module MUST have `services/<module>_service.py` with:
- `create_<entity>()`
- `update_<entity>()`
- `delete_<entity>()`
- `get_<entity>()` / `list_<entities>()`

```python
# ✅ Service pattern
def create_report(validated_data, user) -> DailyTaskReport:
    location = validated_data.get('location')
    if location and location.company != user.company:
        raise ValidationError("Invalid location.")
    return DailyTaskReport.objects.create(company=user.company, engineer=user, **validated_data)

# ❌ Logic in view — VIOLATION
def post(self, request):
    if location.company != request.user.company:
        return Response({'error': '...'}, 400)
    DailyTaskReport.objects.create(...)
```

### Forbidden in Services
- No direct Django ORM calls in Views
- No Django ORM in Serializers (except validation)
- No business logic in `model.save()`
- No circular service imports

---

## 4. Multi-Tenant Rules

```python
# ❌ NEVER — unscoped (security breach)
reports = DailyTaskReport.objects.filter(date=today)

# ✅ ALWAYS — company-scoped
reports = DailyTaskReport.objects.for_company(request.user.company).filter(date=today)

# SUPER_ADMIN exception — must be explicit
if request.user.role == 'SUPER_ADMIN':
    queryset = DailyTaskReport.objects.all()
```

Every endpoint checklist:
- [ ] Filter by `company = request.user.company`
- [ ] Validate FK relationships are in same company
- [ ] Never expose cross-company data in nested serializers

---

## 5. Permissions Rules

```python
# ✅ Every view must declare permissions
class ReportCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsEngineerOrAbove]

# ❌ No permission class = open to all authenticated users
class ReportCreateView(generics.CreateAPIView):
    pass
```

All permission classes in `permissions/`:
- `role_permissions.py` → `IsEngineerOrAbove`, `IsManagerOrAbove`
- `tenant_permissions.py` → `IsSameCompany`
- `object_permissions.py` → `IsReportOwner`

Role hierarchy: `SUPER_ADMIN > OWNER > MANAGER > ENGINEER > HR/ACCOUNTANT/WAREHOUSE`

---

## 6. Anti-Spaghetti Code Rules

### The Size Limits
```
❌ React component > 300 lines → MUST split
❌ Service function > 80 lines → extract helpers
❌ View file > 200 lines → refactor

Exceptions require: # COMPLEXITY NOTE: [reason] | Refactor plan: [doc link]
```

### Forbidden Patterns (Backend)
```python
# ❌ Hardcoded role strings in logic
if user.role == 'ENGINEER': ...   # use permission class

# ❌ Raw SQL
cursor.execute("SELECT * FROM reports WHERE company_id = 1")

# ❌ Business logic in model.save()
def save(self): self.calculate_totals(); super().save()
```

### Forbidden Patterns (Frontend)
```javascript
// ❌ API call inside component
useEffect(() => { fetch('/api/reports/').then(...) }, [])

// ❌ Business logic in component
const total = workers.reduce((s, w) => s + w.hours * w.rate, 0)  // → extract to hook

// ❌ Inline styles
<div style={{ marginTop: 24 }}>  // → use sx or Tailwind
```

---

## 7. State Management Rules

```
Local state     → useState()   → UI state only (modal, loading, form)
Context state   → React Context → auth user, language, theme only
Server state    → Custom hooks + services.js → API data

❌ Redux / Zustand / MobX are NOT used in this project
❌ No global state for server data
```

Standard loading/error pattern:
```javascript
const [data, setData] = useState(null)
const [loading, setLoading] = useState(false)
const [error, setError] = useState(null)
```

---

## 8. Components Rules

| Category | Rules |
|----------|-------|
| Dumb/Presentational | Props only, no API, no logic, pure render |
| Smart/Container | Calls hooks/services, passes to dumb components |

```javascript
// ✅ Clear props interface
const EmployeeCard = ({ employee, onEdit, onDelete }) => { ... }

// ❌ Vague props
const EmployeeCard = ({ data }) => { ... }
const EmployeeCard = (props) => { ... }
```

MUI + Tailwind usage:
```javascript
// ✅
<Card sx={{ borderRadius: 4, p: 3 }}><div className="flex gap-4">

// ❌ Inline styles
<div style={{ marginTop: 24, display: 'flex' }}>
```

---

## 9. Forms Rules

```javascript
// ✅ react-hook-form + zod
const schema = z.object({ name: z.string().min(2) })
const { handleSubmit } = useForm({ resolver: zodResolver(schema) })

// ✅ Submission calls service
const onSubmit = async (data) => {
  await reportService.createReport(data)
}

// ❌ Manual state for form fields
const [name, setName] = useState('')

// ❌ fetch in form submit
const onSubmit = () => { fetch('/api/reports/', { method: 'POST' }) }
```

---

## 10. Querying Rules (Backend)

```python
# ✅ Always optimized
queryset = DailyTaskReport.objects \
    .for_company(company) \
    .select_related('engineer', 'operation', 'location', 'farm') \
    .prefetch_related('labor_entries', 'attachments')

# ❌ N+1 query
for report in DailyTaskReport.objects.filter(company=company):
    print(report.engineer.name)  # one query per report
```

Frontend loading pattern:
```javascript
if (loading) return <CircularProgress />
if (error) return <Alert severity="error">{error}</Alert>
if (!data) return null
return <DataTable rows={data} />
```

---

## 11. Naming Rules

### Backend
| Type | Convention | Example |
|------|-----------|---------|
| Models | PascalCase | `DailyTaskReport` |
| Fields | snake_case | `report_date`, `company_workers` |
| Services | verb_noun | `create_report()`, `update_employee()` |
| Views | NounActionView | `ReportCreateView` |
| Serializers | NounPurposeSerializer | `ReportCreateSerializer` |
| URLs | kebab-case | `/api/labor-entries/` |

### Frontend
| Type | Convention | Example |
|------|-----------|---------|
| Components | PascalCase.jsx | `EmployeeCard.jsx` |
| Hooks | use prefix | `useEmployees.js` |
| Services functions | camelCase | `getEmployees()` |
| Constants | UPPER_SNAKE | `ROLE_PERMISSIONS` |
| CSS classes | kebab-case | `tree-node-lg` |
| i18n keys | namespaced snake | `farm.add_sector` |

---

## 12. Business Logic Rules

### Where Logic Lives
```
✅ services/        ← ALL business logic
✅ Serializers      ← validation only
❌ Views            ← HTTP routing only
❌ model.save()     ← data persistence only
❌ Components       ← rendering only
❌ Hooks            ← data fetching + state only
```

### Core Non-Negotiable Business Rules
1. Every LocationNode belongs to a Company via its Farm
2. Every Report must have: `company`, `farm`, `location`, `operation`, `engineer`
3. Every LaborEntry must belong to a Report in the same company
4. OperationLog is the atomic event unit — DailyTaskReport is a container
5. No location FK is allowed outside `LocationNode`
6. Contractor must belong to same Company as the Report
7. Employee is 1:1 linked to User for staff roles

---

## 13. Documentation Update Rule (Mandatory)

Any AI-generated feature MUST update documentation:

| Change Type | Required Doc Update |
|-------------|---------------------|
| New model | `02-backend/<module>/<MODEL>.md` |
| New API endpoint | `02-backend/<module>/<MODULE>.md` |
| New feature | `04-features/<feature>/OVERVIEW.md` |
| Architecture change | `05-decisions/ADR-XXX.md` |
| New terminology | `00-core/DOMAIN_LANGUAGE.md` |

**No code without docs = Technical Debt.**

---

## 14. Absolute Forbidden List

```
❌ Delete migrations
❌ Break existing API response shapes
❌ Add GenericForeignKey without ADR justification
❌ Hardcode company/user IDs or role strings in business logic
❌ Create a model similar to an existing one
❌ Put business logic in views or models
❌ Call API directly in React components (always use services.js)
❌ Write React component over 300 lines without splitting
❌ Commit secrets, tokens, or credentials to repository
❌ Use old Sector/Plot/CropType table names — they are deprecated tables
❌ Override Tier 1 documentation without an ADR
```

---

## 15. Pre-Commit Safety Checklist

```
[ ] No unscoped querysets (objects.all() without company filter)
[ ] All new models have company FK and TenantAwareModel base
[ ] All new views have permission_classes declared
[ ] No business logic in views or model.save()
[ ] No API calls in React components (use services.js)
[ ] No hardcoded values (IDs, role strings, company names)
[ ] No credentials or tokens in any file
[ ] No React component over 300 lines without justification comment
[ ] Documentation updated for any new model/API/feature
[ ] Migrations created for any model changes
[ ] select_related/prefetch_related used in querysets returning FKs
[ ] Tenant scoping validated for all FK fields in serializers
```
