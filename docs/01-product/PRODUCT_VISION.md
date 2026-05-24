# Product Vision — ATLS Farm ERP

> The business vision for what ATLS is and who it's for.

---

## What Is ATLS?

ATLS (Atlas Farm Management System) is a **Multi-Tenant Farm Management SaaS** platform designed for agricultural enterprises of any type — palm, olive, fruit, vegetable, or mixed farms.

**Core value proposition:**
> Any farm can configure and use ATLS without a single line of code change.
> The system adapts to the farm — not the other way around.

---

## Who Is It For?

| User | Role | Primary Need |
|------|------|-------------|
| Farm Owner | `OWNER` | Visibility into all operations, costs, productivity |
| Farm Manager | `MANAGER` | Daily operational oversight, report review |
| Field Engineer | `ENGINEER` | Quick report entry from the field |
| HR Officer | `HR` | Employee management, leaves, attendance |
| Accountant | `ACCOUNTANT` | Labor costs, payroll, financial reporting |
| Warehouse Officer | `WAREHOUSE` | Inventory tracking, low-stock alerts |

---

## Core Capabilities

### Operational Management
- Field engineers create daily operation logs from mobile/desktop
- Each log captures: location, operation type, workers, hours, productivity
- Manager reviews and approves reports
- Full audit trail of all farm activities

### Farm Structure Management
- Dynamic hierarchical farm layout: Sector → Stage → Enclosure
- Admin configures the hierarchy — no code changes
- Location-based analytics and cost attribution

### Human Resources
- Employee database with linked User accounts
- Leave request and approval workflow
- Daily attendance tracking
- Cloudinary-stored documents and ID scans

### Financial Intelligence
- Labor cost calculation from operation logs
- Payroll linked to HR employee records
- Warehouse cost tracking
- Location-based cost analysis

### Analytics & Reporting
- KPI dashboard: workers, hours, productivity by period
- Operation-level analysis: which operations consume most resources
- Location-level analysis: which areas are most productive
- Engineer performance tracking

---

## SaaS Configuration Model

Everything that makes one farm different from another is configurable from Admin:

| Configuration | Where |
|---------------|-------|
| Farm name and type | Company Settings |
| Location hierarchy | Farm Structure UI |
| Operation types | Operations Admin |
| Crop varieties | Crop Types Admin |
| Contractor list | Contractors Admin |
| Custom report fields | Custom Fields Admin |
| Bilingual CMS content | CMS Admin |

---

## Non-Goals

- ATLS does not manage financial accounting at the ledger level (no double-entry bookkeeping)
- ATLS does not replace a dedicated payroll system (it tracks labor costs, not full payroll)
- ATLS does not manage supply chain or procurement beyond basic warehouse tracking

---

## Technology Principles

1. **Clean data** — every metric is queryable, aggregatable, attributable
2. **Tenant isolation** — zero data leakage between companies
3. **Arabic-first UX** — RTL, Cairo font, bilingual throughout
4. **Mobile-aware** — engineers use it in the field on phones
5. **AI-safe codebase** — documented well enough for AI agents to work safely

---

## Related Documents

- `01-product/ROADMAP.md` — implementation phases
- `01-product/MODULES_OVERVIEW.md` — module status
- `00-core/SYSTEM_ARCHITECTURE.md` — technical architecture
