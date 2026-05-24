# Frontend Overview — ATLS Farm ERP

> Merged from: `front-end/project.md` + `front-end/dashboard.md` + `front-end/landing.md`

---

## Stack

| Component | Technology |
|-----------|-----------|
| Framework | React 19 + Vite |
| UI Library | Material UI v9 |
| Styling | Tailwind CSS v4 |
| i18n | i18next + react-i18next |
| Forms | react-hook-form + Zod |
| Charts | Recharts |
| HTTP Client | Axios (with JWT interceptor) |
| Export | xlsx + file-saver |

---

## Directory Structure

```
Front-End/src/
├── App.jsx              ← Root component, global bootstrap
├── main.jsx             ← Entry point
├── index.css            ← Global CSS resets
├── app/                 ← (if using app-router pattern)
├── assets/              ← Static assets
├── components/          ← Shared, reusable UI components
│   ├── Shared/
│   │   ├── TableToolbar.jsx
│   │   ├── TablePagination.jsx
│   │   └── Charts.jsx
│   └── <Module>/        ← Module-specific components
├── contexts/            ← React contexts
│   └── AuthContext.jsx
├── features/            ← Feature-scoped services + hooks
│   ├── auth/
│   │   └── services.js
│   ├── farm/
│   │   └── services.js
│   ├── reports/
│   │   └── services.js
│   ├── hr/
│   │   └── services.js
│   └── notifications/
│       └── services.js
├── i18n/                ← Translation files
│   └── locales/
│       ├── en.json
│       └── ar.json
├── i18n.js              ← i18next config
├── layouts/             ← Layout wrappers
│   ├── DashboardLayout.jsx
│   └── DashboardTopbar.jsx
├── pages/               ← Page-level components
│   ├── auth/
│   │   ├── Login.jsx
│   │   └── Register.jsx
│   ├── dashboard/
│   │   └── Dashboard.jsx
│   ├── farm/
│   │   └── FarmStructure.jsx
│   ├── reports/
│   │   └── DailyTaskReport/
│   ├── hr/
│   ├── warehouse/
│   ├── accounting/
│   ├── equipment/
│   └── admin/
├── routes/              ← Route definitions + guards
│   └── AppRoutes.jsx
├── services/            ← (legacy — moving to features/)
├── theme/               ← MUI theme customization
└── utils/
    └── export.js        ← Excel/CSV export utilities
```

---

## Architecture Pattern

```
User Interaction
  ↓
Page Component   (smart — manages state, calls hooks)
  ↓
UI Components    (dumb — receive props, render only)
  ↓
Custom Hooks     (useEmployees, useReports — data + state)
  ↓
Feature Services (features/<module>/services.js — API calls)
  ↓
Axios Instance   (JWT interceptor + base URL)
  ↓
Backend REST API
```

---

## Global Bootstrap (App.jsx)

On app load, before rendering:
1. Read `localStorage.atlas_lang` (default `en`)
2. `i18n.changeLanguage(lang)`
3. `document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr'`
4. `document.documentElement.lang = lang`

---

## Design System Summary

| Token | Value | Usage |
|-------|-------|-------|
| Primary | `#2563eb` | Buttons, links, active state |
| Success | `#10b981` | Farm, approve actions |
| Warning | `#f59e0b` | Pending, warehouse alerts |
| Danger | `#ef4444` | Delete, logout |
| Background | `#f8fafc` | Page background |
| Text Primary | `#0f172a` | Main text |

Fonts: `Outfit` (English) + `Cairo` (Arabic) from Google Fonts.

See `03-frontend/ui-system/UI_DESIGN_SYSTEM.md` for full design spec.

---

## Public Landing Page (`/`)

- Navbar: Logo + links + language toggle + auth-aware CTA
- Hero, Palm, Olive sections: content from CMS (`GET /api/auth/public/landing`)
- When authenticated: avatar + Dashboard button instead of Login/Register
- Full RTL support when Arabic is active

## Login & Register (`/login`, `/register`)

- Dark gradient background: `slate-950 → slate-900 → indigo-950`
- Glassmorphism card
- react-hook-form + Zod validation (all messages in Arabic)
- Post-register: "Awaiting admin approval" state

## Dashboard Layout (`/dashboard/*`)

- Sidebar: 260px permanent, role-filtered menu items
- Topbar: breadcrumb + notifications bell + user avatar
- Mobile: bottom navigation bar
- Content: page-specific
