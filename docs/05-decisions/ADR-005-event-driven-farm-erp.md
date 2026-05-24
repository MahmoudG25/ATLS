# ADR-005 — Event-Driven Farm ERP Architecture

- **Status**: Accepted
- **Date**: 2026-05
- **Deciders**: System Architect

---

## Context

### The Old Architecture (Report-Centric)

The system originally modeled farm operations as daily reports:
- An engineer fills one `DailyTaskReport` per day
- The report has fields: `company_workers`, `contractor_workers`, `work_hours`, `operation`
- Analytics were built from these report-level aggregates

**Problems with this approach:**
1. **Coarse granularity** — one operation per report; multiple operations on the same day required multiple reports with confusing structure
2. **Lost context** — no way to distinguish "who did what at which enclosure with what result"
3. **Analytics blind spots** — could not answer: "How many hours were spent on pollination at Enclosure-12 last month?"
4. **Rigid structure** — adding a new operation type meant UI changes, not just data changes
5. **No event stream** — impossible to build real-time monitoring or IoT integration

---

## Decision

**Move to an Event-Driven architecture where `OperationLog` is the atomic event.**

```
OLD (Report-Centric):
  DailyTaskReport {
    operation: "Pollination"
    company_workers: 10
    work_hours: 8
    location: "North Sector"    ← single location for whole report
  }

NEW (Event-Driven):
  DailyTaskReport {             ← container only (metadata)
    date: "2026-05-08"
    engineer: User
    farm: Farm
    status: "submitted"
  }
  OperationLog {                ← atomic event (the real data)
    report: DailyTaskReport
    location: LocationNode      ← specific enclosure
    operation: Operation        ← specific operation
    company_workers: 8
    contractor_workers: 2
    work_hours: 6.5
    actual_productivity: 150
  }
  LaborEntry {                  ← per-worker detail
    operation_log: OperationLog
    worker_name: "Ahmad Ali"
    hours: 8
    rate: 50
  }
```

---

## Rationale

| Requirement | Report-Centric | Event-Driven |
|-------------|---------------|--------------|
| Multiple ops in one day | ❌ Requires multiple reports | ✅ Multiple OperationLogs |
| Location-level analytics | ❌ Only farm-level | ✅ Enclosure-level |
| Labor cost attribution | ❌ Day-level only | ✅ Operation-level |
| IoT sensor events | ❌ Manual forms only | ✅ Direct event emission |
| Real-time dashboards | ❌ Aggregates too coarse | ✅ Event stream |
| Audit trail | ❌ Report-level | ✅ Event-level |

---

## Consequences

**Positive:**
- Full operational granularity: which enclosure, which operation, which workers, what result
- Analytics answer business questions that were impossible before
- System ready for IoT integration (sensors emit OperationLogs)
- Labor costs are correctly attributed to specific work

**Negative:**
- More complex data model than a simple daily form
- Existing `DailyTaskReport` code must be updated to add `OperationLog` child records
- Frontend form becomes a two-step process: create header → add operation logs

**UI Business Explanation (Arabic):**

> المهندس الآن يفتح "تقرير يومي" كـ wrapper لليوم،
> ثم يُضيف "سجلات عمليات" لكل عملية قام بها في أماكن مختلفة.
> هذا يعطي المدير صورة كاملة: مين عمل إيه، فين، وبأد إيه إنتاجية.

---

## Implementation Notes

- `DailyTaskReport` retains: `date`, `engineer`, `farm`, `company`, `status`, `notes`
- `OperationLog` holds: `location`, `operation`, `workers`, `hours`, `productivity`
- `LaborEntry` holds: `worker_name`, `employee FK (optional)`, `hours`, `rate`
- Analytics ALWAYS query from `OperationLog`, never from `DailyTaskReport` fields

---

## References
- `00-core/EVENT_DRIVEN_ARCHITECTURE.md`
- `05-decisions/ADR-001-operation-log.md`
- `04-features/operation-log-system/OVERVIEW.md`
