# Source of Truth — Documentation Authority Map

> **Purpose**: When two documents conflict, this file determines which one wins.
> Any AI agent or developer MUST consult this file before acting on conflicting information.

---

## 1. Authority Tiers

```
TIER 1 — ABSOLUTE AUTHORITY (never override without ADR)
├── 00-core/SYSTEM_ARCHITECTURE.md
├── 00-core/DATABASE_RULES.md
├── 00-core/AI_AGENT_RULES.md
├── 00-core/DOMAIN_LANGUAGE.md
└── 00-core/TENANT_SYSTEM.md

TIER 2 — AUTHORITATIVE REFERENCE (strong, can be overridden by Tier 1)
├── 05-decisions/ADR-*.md          ← All Architecture Decision Records
├── 00-core/PERMISSIONS.md
├── 00-core/CODING_RULES.md
└── 00-core/EVENT_DRIVEN_ARCHITECTURE.md

TIER 3 — MODULE REFERENCE (accurate for their domain, not cross-domain authority)
├── 02-backend/**/*.md
├── 03-frontend/**/*.md
├── 04-features/**/*.md
└── 01-product/*.md

TIER 4 — CONTEXTUAL ONLY (historical, informational, not binding)
├── CHANGELOG.md
└── legacy/old-docs/*.md
```

---

## 2. Conflict Resolution Rules

### Rule 1 — Tier Always Wins
If `00-core/SYSTEM_ARCHITECTURE.md` says `X` and `02-backend/farm/FARM_STRUCTURE.md` says `Y`, then `X` is correct.

### Rule 2 — ADR Overrides Old Design
An Architecture Decision Record in `05-decisions/` supersedes any older document that contradicts it.
Check ADR dates — the **most recent ADR** on a topic wins.

### Rule 3 — Legacy Docs Are Void
Any document in `legacy/old-docs/` is **explicitly invalidated**.
It exists only for historical reference. Never implement from it.

### Rule 4 — DOMAIN_LANGUAGE Is Final
If a term in `00-core/DOMAIN_LANGUAGE.md` says "use X, not Y" — that applies **everywhere**, including when generating code.

### Rule 5 — Code vs Docs Conflict
If implemented code contradicts a Tier 1 or Tier 2 document:
- The **document is correct** by default.
- The code should be flagged for refactor.
- Exception: if an ADR was written to match a proven production implementation.

---

## 3. Document Status Registry

| Document | Status | Authority | Last Reviewed |
|----------|--------|-----------|---------------|
| `00-core/SYSTEM_ARCHITECTURE.md` | ✅ Active | Tier 1 | 2026-05 |
| `00-core/DATABASE_RULES.md` | ✅ Active | Tier 1 | 2026-05 |
| `00-core/AI_AGENT_RULES.md` | ✅ Active | Tier 1 | 2026-05 |
| `00-core/DOMAIN_LANGUAGE.md` | ✅ Active | Tier 1 | 2026-05 |
| `00-core/TENANT_SYSTEM.md` | ✅ Active | Tier 1 | 2026-05 |
| `00-core/CODING_RULES.md` | ✅ Active | Tier 2 | 2026-05 |
| `00-core/PERMISSIONS.md` | ✅ Active | Tier 2 | 2026-05 |
| `00-core/EVENT_DRIVEN_ARCHITECTURE.md` | ✅ Active | Tier 2 | 2026-05 |
| `05-decisions/ADR-001-operation-log.md` | ✅ Active | Tier 2 | 2026-05 |
| `05-decisions/ADR-002-locationnode.md` | ✅ Active | Tier 2 | 2026-05 |
| `05-decisions/ADR-003-multi-tenant.md` | ✅ Active | Tier 2 | 2026-05 |
| `05-decisions/ADR-004-report-system.md` | ✅ Active | Tier 2 | 2026-05 |
| `05-decisions/ADR-005-event-driven-farm-erp.md` | ✅ Active | Tier 2 | 2026-05 |
| `02-backend/reports/ANALYTICS_API.md` | ✅ Active | Tier 3 | 2026-05 |
| `03-frontend/ui-system/UI_DESIGN_SYSTEM.md` | ✅ Active | Tier 3 | 2026-05 |
| `01-product/ROADMAP.md` | ✅ Active | Tier 3 | 2026-05 |
| `CHANGELOG.md` | ✅ Active | Tier 4 | — |
| `legacy/old-docs/*` | ❌ Voided | Tier 4 | — |

---

## 4. How to Update This Document

When adding a new authoritative document:
1. Add it to the registry table above with status `✅ Active`
2. Assign it a tier based on its scope (Tier 1 = global rules, Tier 3 = module-specific)
3. Update `docs/INDEX.md`

When deprecating a document:
1. Move it to `legacy/old-docs/`
2. Change its status to `❌ Voided` in this registry
3. Add a deprecation notice inside the file itself
4. Update any documents that referenced it

---

## 5. For AI Agents

Before making any architectural decision:

```
1. Check DOMAIN_LANGUAGE.md for correct terminology
2. Check SYSTEM_ARCHITECTURE.md for system boundaries
3. Check DATABASE_RULES.md before touching models
4. Check the relevant ADR for design rationale
5. Check AI_AGENT_RULES.md for what is forbidden
```

**If you are unsure which document to trust → always go up in tier number.**
