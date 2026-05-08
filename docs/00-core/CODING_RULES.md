# Coding Rules — ATLS Farm ERP

> **Authority**: Tier 2. Applies to all backend and frontend code.
> Merged from: `docs/back-end/rules.md` + `docs/front-end/rules.md`

---

## Backend Coding Rules (Django + DRF)

### Architecture

```
View Layer  →  Serializer  →  Service  →  Model
(HTTP only)    (validate)    (logic)     (data)
```

### Core Principles
- **Thin views** — views handle request/response routing only
- **Fat services** — all business logic lives in `services/<module>_service.py`
- **Clear module separation** — no cross-module logic without explicit import

### Module Structure (required per app)
```
apps/<module>/
├── models.py
├── apps.py
├── admin.py
└── migrations/

api/endpoints/<module>_views.py
serializers/<module>_serializers.py
services/<module>_service.py
```

### Layer Rules
```
Views:       handle request/response only — no DB, no logic
Serializers: validate + transform data only
Services:    all business logic, DB operations, external calls
Models:      data definition + manager methods only
```

### Naming Conventions
| Type | Convention | Example |
|------|-----------|---------|
| Models | PascalCase | `DailyTaskReport` |
| Fields | snake_case | `report_date` |
| Services | verb_noun | `create_report()` |
| Views | NounActionView | `ReportCreateView` |
| Serializers | NounPurposeSerializer | `ReportCreateSerializer` |
| URLs | kebab-case | `/api/labor-entries/` |

### Auth & Permissions
- JWT only — no session auth
- Block unapproved users at login
- Always declare `permission_classes` on every view
- Centralize permission logic in `permissions/` — no scattered checks

### Serializers
- One serializer per use-case: List, Detail, Create, Update
- No business logic in serializers — validation only
- Always scope FK validation to same company

### Error Handling
```python
# Consistent response format
{"error": "message"}        # 400 Bad Request
{"detail": "message"}       # 401/403/404
{"result": {...}}           # 200 OK
```

### Performance
- `select_related()` for FK fields
- `prefetch_related()` for reverse relations
- Paginate all list endpoints (PAGE_SIZE=25)
- No raw SQL — use Django ORM

### Do NOT (Backend)
```
❌ Put business logic in views
❌ Access DB directly in views
❌ Duplicate logic across modules
❌ Use print() for debugging (use logging)
❌ Delete migrations
❌ Hardcode IDs or role strings in logic
```

### AI Usage Note (Backend)
When modifying backend code:
- Do not change module structure
- Modify only the target module
- Reuse existing services before creating new ones
- Do not create duplicate models

---

## Frontend Coding Rules (React + Vite)

### Architecture

```
Page (smart) → Components (dumb) → Hooks → Services → API
```

### Core Principles
- **No business logic in components** — components render only
- **No API calls in UI** — all calls in `features/<module>/services.js`
- **Dumb components** — receive props, render, done
- **Smart pages** — call hooks, pass data to dumb components

### Module Structure (required per feature)
```
src/features/<module>/
├── services.js    ← ALL API calls
├── hooks.js       ← custom data hooks
└── index.js       ← public exports

src/pages/<module>/
├── ModuleListPage.jsx
└── ModuleDetailPage.jsx
```

### Naming
| Type | Convention | Example |
|------|-----------|---------|
| Components | PascalCase.jsx | `EmployeeCard.jsx` |
| Hooks | use prefix | `useEmployees.js` |
| Service functions | camelCase | `getEmployees()` |
| Constants | UPPER_SNAKE | `ROLE_PERMISSIONS` |

### API Usage
```javascript
// ✅ All API calls inside services.js
export const getReports = async (params) => {
  const { data } = await api.get('/reports/', { params })
  return data
}

// ❌ Never — fetch in component
useEffect(() => { fetch('/api/reports/').then(...) }, [])
```

### Auth Rules
- Store JWT once in context/localStorage
- Attach token automatically via Axios interceptor
- Redirect if not authenticated
- Block unapproved users (check `is_approved` from API)

### Role-Based UI
```javascript
// ✅ Read role from context
const { user } = useAuth()
if (user.role === 'MANAGER') { ... }

// ❌ Hardcode role in component tree
<Route path="/admin" element={<AdminPage />} />  // no role guard
```

### State Management
```
useState()     → local UI state (modal, loading, form)
React Context  → auth, language, theme only
Custom hooks   → server data (useEmployees, useReports)
```

### UI Rules
- MUI for components: `Button`, `TextField`, `Card`, `Dialog`
- Tailwind for layout/spacing: `flex`, `gap-4`, `p-6`
- No inline styles
- RTL support: `dir="rtl"` from `document.documentElement`

### Performance
- Lazy load all page-level components: `React.lazy()`
- `useMemo()` for expensive computations
- `useCallback()` for handler functions passed as props
- Avoid unnecessary re-renders

### Do NOT (Frontend)
```
❌ Mix modules together
❌ Duplicate logic across features
❌ Call API inside useEffect without a service
❌ Use inline styles
❌ Create a component over 300 lines without splitting
❌ Store sensitive data in localStorage (tokens only via secure pattern)
```

### AI Usage Note (Frontend)
When modifying frontend code:
- Touch only the relevant feature module
- Do not refactor unrelated code
- Keep folder structure unchanged
- Reuse existing components from `src/components/`
