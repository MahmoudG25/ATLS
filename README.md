# ATLS — Atlas Farm ERP

A comprehensive, bilingual (AR/EN, RTL/LTR) multi-tenant ERP platform for farm and agriculture management.

> **Stack**: Django 5 + PostgreSQL | React 19 + Vite | MUI v9 + Tailwind v4

---

## Quick Start

### Backend
```bash
cd Back-End
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend
```bash
cd Front-End
npm install
npm run dev
```

---

## Project Structure

```
ATLS/
├── Back-End/          ← Django REST API (PostgreSQL)
│   ├── apps/          ← Feature modules (farm, reports, hr, warehouse...)
│   ├── api/           ← URL routing + API views
│   ├── serializers/   ← DRF serializers
│   ├── services/      ← Business logic layer
│   └── permissions/   ← Role + tenant permission classes
│
├── Front-End/         ← React 19 + Vite SPA
│   └── src/
│       ├── pages/     ← Page-level components
│       ├── components/← Shared UI components
│       ├── features/  ← Feature services + hooks
│       ├── layouts/   ← DashboardLayout + Sidebar
│       ├── contexts/  ← AuthContext
│       └── i18n/      ← Translation files (ar/en)
│
├── docs/              ← Full documentation (see INDEX.md)
│   ├── 00-core/       ← Architecture rules (AI agents start here)
│   ├── 01-product/    ← Vision + Roadmap + Modules
│   ├── 02-backend/    ← Backend module references
│   ├── 03-frontend/   ← Frontend module references
│   ├── 04-features/   ← Feature implementation docs
│   ├── 05-decisions/  ← Architecture Decision Records (ADRs)
│   ├── 06-prompts/    ← AI agent system prompts
│   └── legacy/        ← Voided/archived docs (do not use)
│
└── CHANGELOG.md       ← Development history
```

---

## Documentation

**Start here**: [`docs/INDEX.md`](docs/INDEX.md)

### For AI Agents
```
1. docs/00-core/SOURCE_OF_TRUTH.md    → conflict resolution
2. docs/00-core/DOMAIN_LANGUAGE.md    → correct terminology
3. docs/00-core/SYSTEM_ARCHITECTURE.md → system design
4. docs/00-core/AI_AGENT_RULES.md     → all coding rules
5. docs/06-prompts/<role>-agent.md    → role-specific prompt
```

### Key References

| Doc | Purpose |
|-----|---------|
| [System Architecture](docs/00-core/SYSTEM_ARCHITECTURE.md) | Core entity chain, tech stack |
| [AI Agent Rules](docs/00-core/AI_AGENT_RULES.md) | **All rules — read first** |
| [Domain Language](docs/00-core/DOMAIN_LANGUAGE.md) | Canonical terminology |
| [Roadmap](docs/01-product/ROADMAP.md) | Implementation phases |
| [Backend Overview](docs/02-backend/BACKEND_OVERVIEW.md) | Django structure |
| [Frontend Overview](docs/03-frontend/FRONTEND_OVERVIEW.md) | React structure |
| [Analytics API](docs/02-backend/reports/ANALYTICS_API.md) | Live API reference |
| [Changelog](CHANGELOG.md) | Development history |

---

## Architecture in One Paragraph

ATLS is a **multi-tenant event-driven Farm ERP**. Every farm operation is recorded as an `OperationLog` — the atomic event at the heart of the system. A `DailyTaskReport` is just a container grouping these events by day and engineer. All farm locations (Sector → Stage → Enclosure) are unified under a single `LocationNode` model. Every model is tenant-scoped to a `Company`, and all business logic lives in the `services/` layer — never in views or components.
