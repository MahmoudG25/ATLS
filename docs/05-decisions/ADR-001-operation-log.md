# ADR-001 — OperationLog as Core Entity

- **Status**: Accepted
- **Date**: 2026-05
- **Deciders**: System Architect

---

## Context

The original system modeled `DailyTaskReport` as the primary data entity.
Analytics were built from report-level fields (`company_workers`, `work_hours`, etc.).
This created coarse-grained data with limited analytical value.

The problem:
- One report per day per engineer mixed multiple operations into one record
- Analytics could not distinguish between pollination at Enclosure-12 vs. maintenance at Stage-A
- Labor costs could not be attributed to specific operations
- Location-based productivity could not be computed

---

## Decision

**OperationLog is now the atomic event record — the core of the system.**

`DailyTaskReport` becomes a container: it groups `OperationLog` entries for the same day and engineer. It does not hold operational data itself.

The event chain is:
```
Company → Farm → LocationNode → OperationLog ← DailyTaskReport (container)
                                    ↓
                               LaborEntry[]
                               Attachment[]
```

---

## Consequences

**Positive:**
- Analytics have full granularity: operation × location × date × engineer
- Labor costs are attributable to specific operations
- Future IoT sensors can emit `OperationLog` events directly
- The system supports multiple operations in one day at different locations

**Negative:**
- Existing code that queries `DailyTaskReport` fields must be updated to query `OperationLog`
- The UI form flow becomes two-step: create container → add events

**Migration note:**
- Existing `DailyTaskReport` records that have inline fields (workers, hours, operation) must be migrated to have those fields on `OperationLog` instead
- The `DailyTaskReport` model retains metadata only: date, engineer, farm, status

---

## Alternatives Considered

1. **Keep DailyTaskReport as core** — rejected because it cannot support operation-level analytics
2. **Multiple report types (irrigation, fertilization, daily)** — rejected because it creates duplicate logic; `OperationLog` with an operation type covers all cases

---

## References
- `00-core/EVENT_DRIVEN_ARCHITECTURE.md`
- `00-core/SYSTEM_ARCHITECTURE.md`
