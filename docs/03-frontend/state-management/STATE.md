# State Management — Frontend Reference

---

## State Layers

```
Local state     →  useState()          →  Component-level UI only
Context state   →  React Context       →  Auth, language, theme
Server state    →  Custom hooks        →  API data (no Redux)
```

---

## 1. Local State — useState()

Use for UI-only state that does not need to be shared:

```javascript
// ✅ Correct uses
const [open, setOpen] = useState(false)         // dialog/drawer open state
const [loading, setLoading] = useState(false)   // local loading indicator
const [error, setError] = useState(null)        // local error message

// ❌ Wrong — server data should NOT be in local useState
const [employees, setEmployees] = useState([])  // use a hook instead
```

---

## 2. Context State — React Context

Three global contexts only:

### AuthContext
```javascript
// Provider: src/contexts/AuthContext.jsx
const AuthContext = createContext()

export const AuthProvider = ({ children }) => {
  const [user, setUser]         = useState(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  const login = (userData, tokens) => {
    localStorage.setItem('access_token', tokens.access)
    localStorage.setItem('refresh_token', tokens.refresh)
    setUser(userData)
    setIsAuthenticated(true)
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setUser(null)
    setIsAuthenticated(false)
  }

  return (
    <AuthContext.Provider value={{ user, isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

// Hook
export const useAuth = () => useContext(AuthContext)
```

### Usage pattern
```javascript
const { user, isAuthenticated, logout } = useAuth()

// Role check
if (!['MANAGER', 'OWNER'].includes(user.role)) return null

// Never do this:
const user = JSON.parse(localStorage.getItem('user'))  // ❌ WRONG
```

---

## 3. Server State — Custom Hooks

All API data is managed through custom hooks in `src/features/<module>/hooks.js`:

```javascript
// src/features/reports/hooks.js
export const useReports = (filters = {}) => {
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState(null)

  const fetchReports = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await reportService.getReports(filters)
      setReports(data)
    } catch (err) {
      setError(err.response?.data?.detail || 'خطأ في تحميل البيانات')
    } finally {
      setLoading(false)
    }
  }, [JSON.stringify(filters)])

  useEffect(() => { fetchReports() }, [fetchReports])

  return { reports, loading, error, refetch: fetchReports }
}

// Usage in page component:
const { reports, loading, error, refetch } = useReports({ status: 'submitted' })
```

---

## 4. Standard Loading Pattern

Every component that shows data MUST handle loading + error:

```jsx
// ✅ Full pattern
const { data, loading, error } = useMyHook()

if (loading) return <CircularProgress sx={{ display: 'block', mx: 'auto', mt: 4 }} />
if (error)   return <Alert severity="error">{error}</Alert>
if (!data || data.length === 0) return <EmptyState message={t('common.no_data')} />

return <MyDataComponent data={data} />

// ❌ Wrong — no loading handling
return <DataTable rows={data} />  // crashes if data is null/undefined
```

---

## 5. Mutation Pattern (Create/Update/Delete)

```javascript
// Mutations stay in the component — they are not hooks
const handleCreate = async (formData) => {
  setSubmitting(true)
  try {
    await reportService.createReport(formData)
    refetch()          // refresh the list
    setDialogOpen(false)
  } catch (err) {
    setError(err.response?.data?.detail || 'خطأ في الحفظ')
  } finally {
    setSubmitting(false)
  }
}
```

---

## 6. Forbidden Patterns

```
❌ Redux / Zustand / MobX — not in this project
❌ Global state for server data (use hooks)
❌ useEffect with API calls without cleanup
❌ Prop drilling more than 2 levels (use context or pass via parent)
❌ Storing tokens outside AuthContext (except localStorage for persistence)
❌ Reading localStorage directly in components (use useAuth() hook)
```
