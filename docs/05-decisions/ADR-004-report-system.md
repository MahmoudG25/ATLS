# ADR-004 — Report System Refactor Strategy

- **Status**: Accepted
- **Date**: 2026-05
- **Deciders**: System Architect

---

## Context

The early report system had several structural problems:
- Duplicate location fields (`sector` FK + `plot` FK + free-text fields)
- A generic dropdown table (`ReportDropdownOption`) used for operations, varieties, and units
- Separate `PalmRecord` and `OliveRecord` models — duplicated logic for different crop types
- `FertilizationReport` and `IrrigationReport` lacked `farm`, `location`, `operation` fields
- `CustomFieldDefinition` and `CustomFieldValue` models were unused but present

The system could not scale to new crop types without code changes.

---

## Decision

Refactor the report system gradually without breaking existing data:

### Step 1 — Unified Location
Remove `crop`, `stage`, `enclosure` text fields from reports.
Keep only `location = FK(LocationNode)`.

### Step 2 — Remove Legacy Tables (deprecate, not delete immediately)
- `Sector` → `LocationNode(type='SECTOR')`
- `Plot` → `LocationNode(type='ENCLOSURE')`
- `CropType` → `crop_type` CharField

### Step 3 — Fix Report Core Fields
Every report type must have: `company`, `farm`, `location`, `operation`, `engineer`.

### Step 4 — Replace Dropdown System
Delete `ReportDropdownOption`.
Replace with proper models:
- `Operation` (for operation types)
- `Variety` (for crop varieties)
- `Unit` (for measurement units)
- `Contractor` (for labor contractors)

### Step 5 — Merge Duplicate Crop Models
Create `CropRecord(crop_type='palm'|'olive'|...)`.
Delete `PalmRecord` and `OliveRecord`.

### Step 6 — Tenant Fix
Ensure `Equipment`, `Warehouse`, `Accounting` models all have `company = FK(Company)`.

### Step 7 — Fix Weak Reports
`FertilizationReport` and `IrrigationReport` must get `farm`, `location`, `operation` fields.

---

## Consequences

**Positive:**
- System is SaaS-ready: new crop types added from Admin, no code changes
- Analytics can now query by operation, location, date uniformly
- No more duplicate location logic

**Negative:**
- Existing data requires migration scripts
- Some legacy APIs change response shape (must be versioned or communicated to clients)

---

## Migration Safety Rules
- Never delete a migration — only add new ones
- Old fields kept as `null=True, blank=True` during transition period
- Legacy docs moved to `legacy/old-docs/` — not deleted

---

## References
- `00-core/DATABASE_RULES.md`
- `05-decisions/ADR-001-operation-log.md`
- `05-decisions/ADR-002-locationnode.md`
