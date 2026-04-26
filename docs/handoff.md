# Atlas Farm Management — Session Handoff Document

> **Last updated:** 2026-04-20 · **Status:** Active Development  
> **Dev servers:** `npm run dev` (port 5173) · `python manage.py runserver` (port 8000)

---

## 1. What This Project Is

A bilingual (Arabic / English) **Farm ERP system** for managing Palm and Olive agricultural operations. It covers:

- Field structure (sectors, plots)
- Crop data (Palm + Olive records per plot)
- Warehouse inventory + movement ledger
- Fleet & equipment tracking (usage + maintenance)
- Daily operation reports
- Production yield tracking
- Financial accounting (expenses + revenues)
- Role-based user management + Admin CMS

---

## 2. Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + Vite |
| UI Library | Material UI (MUI) v5 |
| Styling | Tailwind CSS v4 |
| i18n | i18next + react-i18next |
| HTTP Client | Axios (singleton in `src/services/api.js`) |
| Auth | JWT (stored in `localStorage` as `token`) |
| Backend | Django + DRF |
| Database | PostgreSQL |
| Auth tokens | djangorestframework-simplejwt |

---

## 3. Project File Tree

```
e:\my project\
├── Front-End/
│   ├── index.html                  ← SEO title, Cairo + Outfit fonts, dir="ltr"
│   ├── RULES.md                    ← Frontend coding rules (READ FIRST)
│   ├── UI_UX_I18N.md               ← Design system + i18n spec (READ FIRST)
│   └── src/
│       ├── main.jsx                ← Entry — loads i18n BEFORE App
│       ├── App.jsx                 ← MUI Theme (green) + RTL bootstrap + AuthProvider
│       ├── index.css               ← Tailwind + RTL overrides + Arabic font rule
│       ├── i18n/
│       │   ├── index.js            ← i18next config (default = Arabic)
│       │   ├── ar.json             ← ALL Arabic strings (complete)
│       │   └── en.json             ← ALL English strings (complete)
│       ├── app/
│       │   └── AuthContext.jsx     ← Global auth state (user, login, logout)
│       ├── services/
│       │   └── api.js              ← Axios instance, baseURL=localhost:8000/api/
│       ├── layouts/
│       │   └── DashboardTopbar.jsx ← Topbar: page title + date + user/role chip
│       ├── routes/
│       │   └── AppRoutes.jsx       ← All routes (lazy-loaded) + DashboardLayout
│       ├── features/               ← API service calls only (NO UI here)
│       │   ├── auth/services.js
│       │   ├── farm/services.js
│       │   ├── palm/services.js
│       │   ├── olive/services.js
│       │   ├── warehouse/services.js
│       │   ├── equipment/services.js
│       │   ├── accounting/services.js
│       │   ├── production/services.js
│       │   └── reports/services.js
│       └── pages/
│           ├── public/Landing.jsx  ← 5-section landing (Hero/About/Palm/Olive/Contact)
│           ├── auth/
│           │   ├── Login.jsx
│           │   ├── Register.jsx
│           │   └── UserProfile.jsx
│           ├── dashboard/Dashboard.jsx
│           ├── farm/FarmStructure.jsx
│           ├── palm/PalmRecords.jsx
│           ├── olive/OliveRecords.jsx
│           ├── warehouse/InventoryLedger.jsx
│           ├── equipment/FleetManager.jsx
│           ├── accounting/FinanceDashboard.jsx
│           ├── production/YieldTracking.jsx
│           ├── reports/DailyLogs.jsx
│           └── admin/AdminControls.jsx
│
└── Back-End/
    ├── manage.py
    ├── apps/
    │   ├── users/       ← Custom User model
    │   ├── farm/        ← Farm, Sector, Plot, CropType
    │   ├── palm/        ← PalmRecord
    │   ├── olive/       ← OliveRecord
    │   ├── warehouse/   ← Item, Movement
    │   ├── equipment/   ← Equipment, MaintenanceLog, UsageLog
    │   ├── accounting/  ← Expense, Revenue
    │   └── reports/     ← DailyReport
    ├── api/             ← URL routers + ViewSets
    ├── services/        ← Business logic (one file per app)
    ├── serializers/     ← DRF serializers
    └── permissions/     ← Role-based DRF permission classes
```

---

## 4. i18n Architecture

### Key facts
- **Default language: Arabic (`ar`)**
- Stored in: `localStorage.atlas_lang`
- Toggle: sidebar footer button + landing navbar button
- Direction: set on `<html dir="rtl|ltr">` globally at bootstrap

### How it works
```
main.jsx → imports src/i18n/index.js first
App.jsx  → useEffect reads localStorage.atlas_lang, sets html.dir + html.lang + i18n.language
```

### Adding a new translation key
1. Add to `src/i18n/en.json` under the relevant namespace
2. Add to `src/i18n/ar.json` with the Arabic translation
3. Use `const { t } = useTranslation();` in the component, then `t('namespace.key')`

### CMS injection (landing page only)
Landing page fetches `GET /api/auth/public/landing` and injects the response into i18next via `injectCMSTranslations()` from `src/i18n/index.js`.

---

## 5. Auth & Role System

### User model fields
```
name, email, phones (JSON), role, is_approved, is_active
```

### Roles & access
| Role | Access |
|---|---|
| `SUPER_ADMIN` | Everything + Admin Controls |
| `OWNER` / `MANAGER` | All modules |
| `ENGINEER` | Reports, Farm, Palm, Olive, Equipment, Production |
| `ACCOUNTANT` | Accounting, Farm, Reports |
| `WAREHOUSE` | Warehouse, Farm, Reports |
| `HR` | (not yet mapped to sidebar) |

### Auth flow
```
Register → is_approved=False → Admin approves → User logs in → JWT returned
JWT stored in localStorage["token"] → Axios interceptor attaches to every request
```

### Key files
- `src/app/AuthContext.jsx` — provides `{ user, login, logout, loading }`
- `src/routes/AppRoutes.jsx` — `roleMap` object controls sidebar visibility per role
- `src/features/auth/services.js` — login, register, updateMe, getUsersList, approveUser, etc.

---

## 6. Design System

### Colors (MUI theme in `App.jsx`)
| Token | Hex | Usage |
|---|---|---|
| Primary | `#16a34a` | Buttons, active states, links |
| Secondary | `#4ade80` | Highlights |
| Warning/Accent | `#f97316` | Orange elements, Olive sector |
| Error | `#ef4444` | Delete, deactivate, logout |
| Background | `#f8fafc` | Page background |

### Typography
- **English** → `Outfit` (loaded from Google Fonts in `index.html`)
- **Arabic** → `Cairo` (loaded from Google Fonts in `index.html`)
- Arabic class applied via `html[lang="ar"]` CSS rule in `index.css`

### Shape & spacing
- Card radius: `rounded-2xl` / `rounded-3xl` (16–24px)
- Page padding: `p-8` (32px)
- No inline styles — use Tailwind or MUI `sx`

---

## 7. Routing Map

| Path | Component | Protected | Notes |
|---|---|---|---|
| `/` | `Landing` | No | 5 sections, CMS-driven |
| `/login` | `Login` | No | Dark glassmorphism |
| `/register` | `Register` | No | Dark glassmorphism |
| `/dashboard` | `Dashboard` | Yes | KPIs + quick actions |
| `/profile` | `UserProfile` | Yes | |
| `/farm` | `FarmStructure` | Yes | Tree view + plot stats |
| `/palm` | `PalmRecords` | Yes | Table + modal |
| `/olive` | `OliveRecords` | Yes | Table + modal |
| `/warehouse` | `InventoryLedger` | Yes | 2-panel: items + movements |
| `/equipment` | `FleetManager` | Yes | List + detail panel |
| `/reports` | `DailyLogs` | Yes | Card list + modal |
| `/production` | `YieldTracking` | Yes | Table + modal |
| `/accounting` | `FinanceDashboard` | Yes | KPIs + inflow/outflow |
| `/admin` | `AdminControls` | Yes | SUPER_ADMIN only |

All dashboard routes are **lazy-loaded** via `React.lazy()` + `<Suspense>`.

---

## 8. Dashboard Layout Structure

```
<DashboardLayout>
  <Drawer anchor="right|left" (RTL-aware)>
    Logo → Nav Groups (Operations / Business / Security) → User Card + Lang Toggle + Logout
  </Drawer>
  <Box main>
    <DashboardTopbar />     ← page title + date + user avatar/role chip
    <PageContent />
  </Box>
</DashboardLayout>
```

---

## 9. Backend API Endpoints (Known)

| Endpoint | Method | Description |
|---|---|---|
| `/api/auth/login/` | POST | JWT login |
| `/api/auth/register/` | POST | Register user |
| `/api/auth/me/` | GET/PATCH | Current user |
| `/api/auth/users/` | GET | User list (admin) |
| `/api/auth/users/{id}/approve/` | POST | Approve user |
| `/api/auth/users/{id}/deactivate/` | POST | Deactivate user |
| `/api/auth/public/landing` | GET | CMS landing content (no auth) |
| `/api/admin/landing-content` | PATCH | Update CMS (admin) |
| `/api/farm/farms/` | GET | Farm list |
| `/api/farm/sectors/` | GET/POST | Sectors |
| `/api/farm/plots/` | GET/POST | Plots |
| `/api/farm/crop-types/` | GET | Crop types |
| `/api/farm/structure/` | GET | Full tree (sectors + plots) |
| `/api/farm/plots/{id}/stats/` | GET | Plot stats (tree count, yield) |
| `/api/palm/records/` | GET/POST | Palm records |
| `/api/olive/records/` | GET/POST | Olive records |
| `/api/warehouse/items/` | GET/POST | Inventory items |
| `/api/warehouse/movements/` | GET/POST | Stock movements |
| `/api/equipment/` | GET/POST | Equipment list |
| `/api/equipment/{id}/` | GET | Equipment details |
| `/api/equipment/{id}/maintenance/` | POST | Log maintenance |
| `/api/equipment/{id}/usage/` | POST | Log usage |
| `/api/accounting/summary/` | GET | Financial summary |
| `/api/accounting/expenses/` | GET/POST | Expenses |
| `/api/accounting/revenues/` | GET/POST | Revenues |
| `/api/reports/` | GET/POST | Daily reports |
| `/api/production/yields/` | GET/POST | Yield records |

---

## 10. What Is Fully Done ✅

- [x] **i18n system** — `src/i18n/` folder, JSON files, default Arabic, CMS injection
- [x] **Global RTL bootstrap** — `App.jsx` sets `html.dir` + `html.lang` on every mount
- [x] **MUI theme** — green primary (#16a34a), orange accent (#f97316)
- [x] **Landing page** — 5 sections (Hero, About, Palm, Olive, Contact), farm green theme, fully bilingual
- [x] **Dashboard sidebar** — RTL-aware drawer anchor, role-based nav, lang toggle, all labels bilingual
- [x] **Dashboard topbar** — page title from route, date in locale, user avatar + role chip
- [x] **Lazy loading** — all pages via `React.lazy()` + `Suspense`
- [x] **FarmStructure** — bilingual (labels, modals, stats panel)
- [x] **PalmRecords** — bilingual (table headers, modal labels)
- [x] **OliveRecords** — bilingual (table headers, modal labels)
- [x] **InventoryLedger** — bilingual (both tables, both modals, category chips)
- [x] **FleetManager** — bilingual (list, detail panels, 3 modals)
- [x] **FinanceDashboard** — bilingual (KPI cards, inflow/outflow, modal)
- [x] **YieldTracking** — bilingual (table, modal)
- [x] **DailyLogs** — bilingual (cards, modal, signed-by label)
- [x] **AdminControls** — bilingual (tabs, chips, CMS field labels)
- [x] **UserProfile** — bilingual (headings, field labels, history)
- [x] **Dashboard** — bilingual greeting, KPI labels, quick-action grid

---

## 11. What Is NOT Done Yet ⚠️

- [ ] **Charts / Analytics** — Dashboard has a placeholder. Phase 2: use Recharts or D3
- [ ] **HR module** — `HR` role exists but has no dedicated page or sidebar item
- [ ] **Salary / Payroll** — `total_salaries` comes from API but no input UI exists
- [ ] **Notifications** — Topbar has no notification bell yet (placeholder space exists)
- [ ] **Form validation** — No client-side validation beyond `required` HTML attrs
- [ ] **Search / Filter** — No search bars on tables yet
- [ ] **Pagination** — API data is returned as flat lists; no pagination UI
- [ ] **Print / Export** — No PDF export (was planned for Daily Reports in a previous session)
- [ ] **Mobile responsive** — Sidebar is permanent drawer; no mobile hamburger menu
- [ ] **Production mode build** — Only tested with `npm run dev`
- [ ] **Error boundary** — No React error boundary around lazy routes

---

## 12. Known Issues / Watch Out ⚡

| Issue | Notes |
|---|---|
| `src/i18n.js` still exists | Old file, not used. The new system is `src/i18n/index.js`. Delete the old file when convenient. |
| `AuthProvider` wrapping | Is in `App.jsx`. `main.jsx` no longer has it — already fixed. |
| `UserProfile` missing `useEffect` import | Was fixed. Verify it's working when logged in. |
| Landing CMS fallback | If Django is offline, landing falls back to JSON strings in `ar.json`/`en.json` silently. |
| CORS | Django must have `localhost:5173` in `CORS_ALLOWED_ORIGINS`. Check `settings.py` if API calls fail. |

---

## 13. How to Start Tomorrow

### 1. Start servers
```powershell
# Terminal 1 — Frontend
cd "e:\my project\Front-End"
npm run dev

# Terminal 2 — Backend
cd "e:\my project\Back-End"
python manage.py runserver
```

### 2. Login as SUPER_ADMIN
- Go to `http://localhost:5173`
- Use the SUPER_ADMIN credentials
- All sidebar items + Admin Controls will be visible

### 3. Quick orientation
- **Landing page** → `src/pages/public/Landing.jsx`
- **Adding a translated string** → edit `src/i18n/ar.json` + `src/i18n/en.json`, then use `t('namespace.key')`
- **Adding a new route** → `src/routes/AppRoutes.jsx` (add lazy import + Route + roleMap entry)
- **Adding a new API call** → create/edit file in `src/features/<module>/services.js`

---

## 14. Session History (What We Built Today)

| Session | Work Done |
|---|---|
| Session 1 | Created `UI_UX_I18N.md` spec, global RTL bootstrap in `App.jsx`, Cairo/Outfit fonts in `index.html`, sidebar i18n in `AppRoutes.jsx` |
| Session 2 | Restructured i18n to `src/i18n/` folder, switched default to Arabic, green MUI theme, full Landing page redesign (5 sections), `DashboardTopbar`, lazy loading all pages, bilingual `Dashboard.jsx` |
| Session 3 | Translated ALL dashboard module pages — every table column heading, form label, modal title, button, badge, and stat card — across 10 pages |
