# UI/UX & I18N SPEC — Atlas Farm Management

## Goal

Define the exact UI/UX design system and bilingual (Arabic / English) behaviour for every surface of the Atlas ERP frontend.

---

## Design System

### Color Palette

| Token         | Value     | Usage                       |
|---------------|-----------|-----------------------------|
| `primary`     | `#2563eb` | Buttons, links, active state |
| `success`     | `#10b981` | Palm sector, approve actions |
| `accent`      | `#6366f1` | Fleet, indigo cards          |
| `warning`     | `#f59e0b` | Warehouse, pending chips     |
| `danger`      | `#ef4444` | Logout, deactivate           |
| `slate-900`   | `#0f172a` | Text primary                 |
| `slate-500`   | `#64748b` | Text muted                   |
| `slate-50`    | `#f8fafc` | Page background              |

### Typography

| Audience | Font           | Weights       |
|----------|----------------|---------------|
| English  | `Outfit`       | 400, 600, 700, 800 |
| Arabic   | `Cairo`        | 400, 600, 700, 800 |

* Load both fonts in `index.html` via Google Fonts.
* Apply `font-arabic` CSS class to `<body>` and `<html>` when `lang = ar`.
* Cairo renders Arabic beautifully at all weights. Never use a system fallback for Arabic.

### Spacing & Shape

* Page padding: `p-8` (32px)
* Card radius: `rounded-3xl` (24px)
* Button radius: `8px` (MUI override)
* Shadow level: `shadow-sm` / `elevation={0}` with `border border-slate-100`

---

## Internationalization (i18n)

### Engine

* Package: `i18next` + `react-i18next`
* Config file: `src/i18n.js`
* Default language: `en`
* Fallback language: `en`
* Persistence: `localStorage` key `atlas_lang`

### Language Toggle

* Shown in: Public Navbar (Landing), Dashboard Sidebar bottom
* Icon: `LanguageIcon` (MUI)
* Toggle switches between `en` ↔ `ar`
* On switch: update `i18n.language`, `localStorage.atlas_lang`, and `document.documentElement.dir`

### RTL Behaviour

* `dir="rtl"` is applied to `<html>` element when `lang = ar`
* `dir="ltr"` when `lang = en`
* This is set at app bootstrap (`App.jsx` or `main.jsx`) by reading `localStorage.atlas_lang`
* Not component-level — applies globally

### Translation Keys (Landing CMS)

These keys are fetched from Django API `GET /api/auth/public/landing` and injected into i18next at runtime:

```
hero_title    — Main landing headline
hero_text     — Landing sub-headline
palm_text     — Palm section header
olive_text    — Olive section header
```

Fallback values are hardcoded in `i18n.js` if the API is unreachable.

### Translation Keys (Dashboard / Static UI)

These are static and do not need CMS. They live in `i18n.js`:

```
nav_dashboard       — "Dashboard" / "لوحة التحكم"
nav_farm            — "Farm Structure" / "هيكل المزرعة"
nav_palm            — "Palm Fields" / "حقول النخيل"
nav_olive           — "Olive Fields" / "حقول الزيتون"
nav_warehouse       — "Ledger Matrix" / "مستودع"
nav_equipment       — "Fleet Networks" / "الأسطول"
nav_reports         — "Operation Feeds" / "السجلات اليومية"
nav_production      — "Yield Metrics" / "الإنتاج"
nav_accounting      — "Financial Backbone" / "المحاسبة"
nav_admin           — "Admin Controls" / "لوحة الإدارة"
nav_logout          — "Logout" / "تسجيل خروج"
```

---

## Page-Level Requirements

### Public Landing (`/`)

* Navbar: Logo + links + language toggle + auth-aware CTA
* Hero section: fetches `hero_title`, `hero_text` from CMS
* Palm section: fetches `palm_text` from CMS
* Olive section: fetches `olive_text` from CMS
* When authenticated: Show Avatar + Dashboard button instead of Login/Register
* All sections support RTL text direction when Arabic is active
* No hardcoded content strings

### Login & Register (`/login`, `/register`)

* Dark gradient background (`slate-950` → `slate-900` → `indigo-950`)
* Glassmorphism card (`bg-white/5 backdrop-blur-xl border border-white/10`)
* Atlas branding in header ("Atlas Farm" logo)
* English only (auth pages do not require bilingual support)
* Show "Awaiting admin approval" state post-register

### Dashboard Layout (Sidebar)

* Sidebar width: 260px, permanent variant
* Logo: "Atlas ERP" with gradient text `from-indigo-500 to-purple-600`
* Menu items grouped:
  - Operations: Dashboard, Farm, Palm, Olive, Warehouse, Equipment
  - Business Layer: Reports, Production, Accounting
  - Security Engine (SUPER_ADMIN only): Admin Controls
* Bottom of sidebar: User avatar + name/role + language toggle + Logout button
* Menu items respect role-based access (`roleMap`)

### Dashboard (`/dashboard`)

* Greeting: "Welcome back, {firstName}"
* KPI cards: Total Net Margin, Active Fleet Units, Ledger Commodities
* Placeholder for charts area (Phase 2)
* Cards use consistent design: white bg, `rounded-3xl`, `shadow-sm`

### Admin Controls (`/admin`)

* Tab 1 — Security Overview: User list with approve / deactivate actions
* Tab 2 — Bilingual CMS: Text fields for all landing page strings (EN + AR)
* CMS save pushes to `PATCH /api/admin/landing-content`
* SUPER_ADMIN access only (enforced by role-based routing)

---

## HTML & SEO

* `index.html` title: `Atlas Farm Management — ERP System`
* `<html lang>` attribute: updated dynamically when language changes
* Arabic font: `Cairo` loaded from Google Fonts
* English font: `Outfit` loaded from Google Fonts
* Meta description: "Atlas Farm Management — Precision agriculture ERP for Palm and Olive sectors."

---

## Global Bootstrap

In `App.jsx` or `main.jsx`, before rendering:

1. Read `localStorage.atlas_lang` (default `en`)
2. Call `i18n.changeLanguage(saved)`
3. Set `document.documentElement.dir = saved === 'ar' ? 'rtl' : 'ltr'`
4. Set `document.documentElement.lang = saved`

This ensures RTL and font direction are consistent on every page — not just the landing page.

---

## Do NOT

* Do not hardcode landing content strings in React
* Do not apply `dir` only to individual sections (apply globally to `<html>`)
* Do not use inline styles (use Tailwind classes or MUI `sx`)
* Do not duplicate i18n logic — use the shared `i18n.js` instance
* Do not mix modules — keep each feature isolated
