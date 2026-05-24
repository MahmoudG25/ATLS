# ATLS Documentation — Master Index

> Navigation hub for all project documentation.
> Always start here. See `00-core/SOURCE_OF_TRUTH.md` for conflict resolution.

---

## Quick Start for AI Agents

```
Before writing any code, read in this order:
1. 00-core/SOURCE_OF_TRUTH.md    → which doc wins
2. 00-core/DOMAIN_LANGUAGE.md    → correct terms
3. 00-core/SYSTEM_ARCHITECTURE.md → system design
4. 00-core/AI_AGENT_RULES.md     → all rules
5. 06-prompts/<role>-agent.md    → your specific prompt
```

---

## 📁 00-core/ — Absolute Authority (Tier 1 & 2)

| File | What It Contains |
|------|-----------------|
| [SOURCE_OF_TRUTH.md](00-core/SOURCE_OF_TRUTH.md) | Document authority hierarchy + conflict resolution |
| [SYSTEM_ARCHITECTURE.md](00-core/SYSTEM_ARCHITECTURE.md) | System design, entity chain, tech stack |
| [DATABASE_RULES.md](00-core/DATABASE_RULES.md) | Model design rules, query patterns |
| [AI_AGENT_RULES.md](00-core/AI_AGENT_RULES.md) | **ALL rules for AI agents — read this first** |
| [DOMAIN_LANGUAGE.md](00-core/DOMAIN_LANGUAGE.md) | Canonical terminology, Arabic↔English mapping |
| [CODING_RULES.md](00-core/CODING_RULES.md) | Backend + frontend coding standards |
| [PERMISSIONS.md](00-core/PERMISSIONS.md) | Role definitions + permission matrix |
| [TENANT_SYSTEM.md](00-core/TENANT_SYSTEM.md) | Multi-tenant isolation rules |
| [EVENT_DRIVEN_ARCHITECTURE.md](00-core/EVENT_DRIVEN_ARCHITECTURE.md) | OperationLog as core event |

---

## 📁 01-product/ — Product Context

| File | What It Contains |
|------|-----------------|
| [PRODUCT_VISION.md](01-product/PRODUCT_VISION.md) | What ATLS is, who it's for, core capabilities |
| [ROADMAP.md](01-product/ROADMAP.md) | Phases 1–11 with status and deliverables |
| [MODULES_OVERVIEW.md](01-product/MODULES_OVERVIEW.md) | Module status table + ownership map |

---

## 📁 02-backend/ — Backend Reference

| File | What It Contains |
|------|-----------------|
| [BACKEND_OVERVIEW.md](02-backend/BACKEND_OVERVIEW.md) | Stack, directory structure, patterns |
| [auth/AUTH_SYSTEM.md](02-backend/auth/AUTH_SYSTEM.md) | User model, JWT, approval flow, notifications |
| [farm/FARM_STRUCTURE.md](02-backend/farm/FARM_STRUCTURE.md) | LocationNode model + API endpoints |
| [reports/OPERATION_LOG.md](02-backend/reports/OPERATION_LOG.md) | OperationLog + DailyTaskReport + LaborEntry |
| [reports/ANALYTICS_API.md](02-backend/reports/ANALYTICS_API.md) | All analytics endpoints with schemas |
| [hr/HR_MODULE.md](02-backend/hr/HR_MODULE.md) | Employee, LeaveRequest, Attendance models |
| [warehouse/WAREHOUSE.md](02-backend/warehouse/WAREHOUSE.md) | Warehouse models and endpoints |
| [accounting/ACCOUNTING.md](02-backend/accounting/ACCOUNTING.md) | Accounting models and endpoints |
| [equipment/EQUIPMENT.md](02-backend/equipment/EQUIPMENT.md) | Equipment models and endpoints |

---

## 📁 03-frontend/ — Frontend Reference

| File | What It Contains |
|------|-----------------|
| [FRONTEND_OVERVIEW.md](03-frontend/FRONTEND_OVERVIEW.md) | Stack, directory structure, architecture |
| [ui-system/UI_DESIGN_SYSTEM.md](03-frontend/ui-system/UI_DESIGN_SYSTEM.md) | Colors, typography, spacing, i18n |
| [pages/AUTH_PAGES.md](03-frontend/pages/AUTH_PAGES.md) | Login, register, approval flow |
| [pages/DASHBOARD.md](03-frontend/pages/DASHBOARD.md) | Dashboard layout and KPI cards |

---

## 📁 04-features/ — Feature Documentation

| File | What It Contains |
|------|-----------------|
| [operation-log-system/OVERVIEW.md](04-features/operation-log-system/OVERVIEW.md) | Event recording feature |
| [farm-structure/OVERVIEW.md](04-features/farm-structure/OVERVIEW.md) | Farm tree UI feature |
| [farm-structure/PHASE_01.md](04-features/farm-structure/PHASE_01.md) | Full adaptive UI implementation |
| [hr-system/OVERVIEW.md](04-features/hr-system/OVERVIEW.md) | HR feature overview |
| [analytics/OVERVIEW.md](04-features/analytics/OVERVIEW.md) | Analytics feature overview |
| [reporting-engine/OVERVIEW.md](04-features/reporting-engine/OVERVIEW.md) | Report engine overview |

---

## 📁 05-decisions/ — Architecture Decision Records

| File | Decision |
|------|---------|
| [ADR-001-operation-log.md](05-decisions/ADR-001-operation-log.md) | OperationLog as core entity |
| [ADR-002-locationnode.md](05-decisions/ADR-002-locationnode.md) | LocationNode as universal location model |
| [ADR-003-multi-tenant.md](05-decisions/ADR-003-multi-tenant.md) | Row-level tenant isolation |
| [ADR-004-report-system.md](05-decisions/ADR-004-report-system.md) | Report system refactor strategy |
| [ADR-005-event-driven-farm-erp.md](05-decisions/ADR-005-event-driven-farm-erp.md) | Event-driven architecture decision |

---

## 📁 06-prompts/ — AI Agent Prompts

| File | Use When |
|------|---------|
| [backend-agent.md](06-prompts/backend-agent.md) | Working on Django/DRF backend |
| [frontend-agent.md](06-prompts/frontend-agent.md) | Working on React frontend |
| [review-agent.md](06-prompts/review-agent.md) | Reviewing code for quality/security |
| [refactor-agent.md](06-prompts/refactor-agent.md) | Refactoring without changing behavior |
| [architecture-agent.md](06-prompts/architecture-agent.md) | Planning new features or system design |

---

## 📁 legacy/old-docs/ — Voided Documents

> ⚠️ These documents are INVALIDATED. Historical reference only.
> See [legacy/old-docs/ARCHIVE_NOTICE.md](legacy/old-docs/ARCHIVE_NOTICE.md) for details.

---

## 📄 Root Level

| File | What It Contains |
|------|-----------------|
| [CHANGELOG.md](../CHANGELOG.md) | Development history |
| [README.md](../README.md) | Project setup and overview |

---

## Documentation Dependency Map

```
SOURCE_OF_TRUTH.md          ← resolves conflicts between all docs
    ↓
DOMAIN_LANGUAGE.md          ← terminology used by all docs
SYSTEM_ARCHITECTURE.md      ← design used by all docs
    ↓
DATABASE_RULES.md           ← used by: 02-backend/ docs
AI_AGENT_RULES.md           ← used by: 06-prompts/ docs
CODING_RULES.md             ← used by: 02-backend/, 03-frontend/ docs
PERMISSIONS.md              ← used by: 02-backend/, 03-frontend/ docs
TENANT_SYSTEM.md            ← used by: 02-backend/ docs
EVENT_DRIVEN_ARCHITECTURE.md ← used by: 04-features/, 05-decisions/ docs
    ↓
05-decisions/ADR-*.md       ← design rationale for: 02-backend/, 04-features/
    ↓
02-backend/**, 03-frontend/** ← module-level implementation docs
    ↓
04-features/**              ← feature-level implementation docs
    ↓
06-prompts/**               ← aggregates all above for AI agents
```
