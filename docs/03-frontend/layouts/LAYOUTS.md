# Layouts — Frontend Reference

> Dashboard shell: Sidebar + Topbar + Content area.

---

## DashboardLayout

Wraps every authenticated page. Structure:

```jsx
<DashboardLayout>
  <Sidebar />           {/* 260px left, permanent on desktop */}
  <Box className="flex flex-col flex-1">
    <DashboardTopbar /> {/* height: 64px */}
    <main className="flex-1 overflow-auto p-8 bg-slate-50">
      {children}        {/* page content */}
    </main>
  </Box>
</DashboardLayout>
```

**File**: `src/layouts/DashboardLayout.jsx`

---

## Sidebar

| Property | Value |
|----------|-------|
| Width | 260px (permanent desktop) |
| Background | `#0f172a` (slate-950) |
| Text | white |
| Active item | primary blue highlight |
| Collapse | hidden on mobile (bottom nav instead) |

```jsx
const MENU_ITEMS = [
  { path: '/dashboard',         label: 'dashboard',     icon: <DashboardIcon />, roles: ALL },
  { path: '/farm-structure',    label: 'farm',          icon: <ForestIcon />,    roles: ['SUPER_ADMIN','OWNER','MANAGER','ENGINEER'] },
  { path: '/reports',           label: 'reports',       icon: <AssignmentIcon />,roles: ['SUPER_ADMIN','OWNER','MANAGER','ENGINEER'] },
  { path: '/hr',                label: 'hr',             icon: <PeopleIcon />,    roles: ['SUPER_ADMIN','OWNER','MANAGER','HR'] },
  { path: '/warehouse',         label: 'warehouse',      icon: <WarehouseIcon />, roles: ['SUPER_ADMIN','OWNER','MANAGER','WAREHOUSE'] },
  { path: '/accounting',        label: 'accounting',     icon: <AccountIcon />,   roles: ['SUPER_ADMIN','OWNER','ACCOUNTANT'] },
  { path: '/equipment',         label: 'equipment',      icon: <BuildIcon />,     roles: ['SUPER_ADMIN','OWNER','MANAGER'] },
  { path: '/crop-records',      label: 'crop_records',   icon: <GrainIcon />,     roles: ['SUPER_ADMIN','OWNER','MANAGER','ENGINEER'] },
  { path: '/admin',             label: 'admin',          icon: <SettingsIcon />,  roles: ['SUPER_ADMIN','OWNER','MANAGER'] },
]

// Filter by role in render:
const visibleItems = MENU_ITEMS.filter(item =>
  item.roles === ALL || item.roles.includes(user.role)
)
```

---

## DashboardTopbar

| Element | Description |
|---------|-------------|
| Breadcrumb | Current page path |
| Language toggle | AR ↔ EN |
| Notifications bell | Badge with unread count |
| User avatar | Name + role chip + logout |

**File**: `src/layouts/DashboardTopbar.jsx`

---

## Mobile Layout

On screens < 768px:
- Sidebar hidden
- Bottom navigation bar (5 icon tabs, role-filtered)
- Content area: full width, no sidebar padding
- Topbar: logo only + hamburger

---

## Page Content Wrapper

```jsx
// Standard page padding — use on every page
<Box className="p-8">
  <Typography variant="h4" className="mb-6 font-bold">
    {t('page.title')}
  </Typography>
  {/* page content */}
</Box>
```

---

## RTL Adaptation

```javascript
// In DashboardLayout:
const dir = i18n.language === 'ar' ? 'rtl' : 'ltr'
// Sidebar: left on LTR, right on RTL (via CSS logical properties)
// All spacing via Tailwind logical: ps- pe- ms- me- (not pl- pr-)
```
