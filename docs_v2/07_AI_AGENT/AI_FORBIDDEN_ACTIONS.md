# AI Forbidden Actions & Operational Red Lines

| Metadata | Details |
| :--- | :--- |
| **Document ID** | ATLS-AI-02 |
| **Status** | AUTHORITATIVE |
| **Version** | 2.0.0 |
| **Owner** | AI Agent & Architecture Team |
| **Applicability** | All AI Agents & Automated Workflows |

## 1. Forbidden Philosophy
Safety, integrity, and tenant isolation are **non-negotiable** in the ATLS platform. Any AI-generated code or configuration that violates these "Red Lines" is considered a critical system risk and must be automatically rejected.
- **Integrity over Speed**: No shortcuts that compromise domain rules.
- **Safety by Default**: Every action must assume multi-tenant constraints.
- **Auditability**: No "silent" actions; everything must be traceable.

## 2. Architecture Violations
- **Circular Dependencies**: AI MUST NEVER create circular imports between modules (e.g., `farm` -> `harvest` -> `farm`).
- **God Services**: FORBID creating single service classes that handle logic for more than one bounded context.
- **Layer Bypassing**: FORBID views calling repositories directly or models containing service-level business logic.

## 3. Security Violations
- **Permission Bypassing**: AI MUST NEVER create endpoints without explicit permission checks (`HasPermission`).
- **Secret Exposure**: FORBID hardcoding API keys, passwords, or private IPs in source code or comments.
- **Public Admin**: FORBID exposing `/admin/` or internal metrics to the public internet.

## 4. Tenant Isolation Violations
- **Tenant Bypass**: AI MUST NEVER write queries that omit the `tenant_id` filter (unless via a verified system-admin manager).
- **Leakage**: FORBID joining tables from different tenants or allowing one tenant to see another's storage keys.

## 5. Database Violations
- **Hard Delete**: AI MUST NEVER implement `DELETE` SQL commands on production operational data; use soft deletes.
- **Schema Chaos**: FORBID creating database tables without a corresponding Django model and migration.

## 6. ORM Violations
- **N+1 Queries**: AI MUST NEVER generate code that triggers N+1 queries in loops.
- **Giant Joins**: FORBID queries joining more than 5 tables; use read models instead.

## 7. Frontend Violations
- **Base64 Storage**: AI MUST NEVER store images or files as Base64 strings in the database or frontend state.
- **Direct Store Mutation**: FORBID components mutating Zustand stores directly without an action.

## 8. Backend Violations
- **Fat Views**: AI MUST NEVER generate views exceeding 20 lines of logic.
- **Inventory Mutation**: FORBID direct database mutation of inventory counts; all changes must go through the `InventoryService`.

## 9. Async Violations
- **Sync Heavy Operations**: AI MUST NEVER perform synchronous video processing, heavy PDF generation, or bulk email sending in the request cycle.
- **Unmanaged Tasks**: FORBID triggering Celery tasks without idempotency protection.

## 10. Event System Violations
- **EDA Bypass**: AI MUST NEVER update critical status fields without emitting the corresponding domain event.
- **Magic Signals**: FORBID the use of Django Signals for business logic; use explicit event publishing.

## 11. Notification Violations
- **Notification Spam**: AI MUST NEVER implement loops that send notifications without a deduplication check.
- **Hardcoded Text**: FORBID hardcoding notification messages; must use the localized template system.

## 12. Media Violations
- **Public Buckets**: AI MUST NEVER enable public read access on operational media buckets.
- **Orphan Media**: FORBID deleting database records without a cleanup plan for the physical object storage.

## 13. Audit Violations
- **Log Deletion**: AI MUST NEVER implement any logic that allows the deletion or modification of `AuditEvent` logs.
- **Silent Mutations**: FORBID changing critical state (e.g., `Approved` status) without an audit trail.

## 14. UI/UX Violations
- **Non-Responsive**: AI MUST NEVER generate form layouts that are not mobile-first.
- **Blocking UX**: FORBID unskippable animations or transitions that block user interaction.

## 15. Offline Violations
- **Conflict Ignorance**: AI MUST NEVER implement sync logic that ignores or "silently overwrites" offline data conflicts.
- **Heavy Sync**: FORBID triggering full-data syncs on every app foreground; use delta-sync.

## 16. Performance Violations
- **Layout Thrashing**: AI MUST NEVER animate layout properties (`height`, `width`, `top`) in CSS; use `transform`.
- **Memory Leaks**: FORBID creating global event listeners or intervals without a cleanup function.

## 17. AI Shortcut Violations
- **Vague Naming**: AI MUST NEVER use single-letter variables or "magic" numbers.
- **TODO Pollution**: FORBID committing "TODO" or "FIXME" comments in final PRs.

## 18. Forbidden Refactor Patterns
- **Library Swapping**: AI MUST NEVER replace core libraries (e.g., swapping `Framer Motion` for `GSAP`) without explicit architecture approval.
- **Pattern Breaking**: FORBID introducing "Controller" patterns where "Service" patterns are mandated.

## 19. Forbidden Deployment Actions
- **Manual SSH**: AI MUST NEVER attempt to fix production issues via manual SSH/Terminal sessions.
- **Env Bypass**: FORBID bypassing the CI/CD pipeline for hotfixes.

## 20. Forbidden Production Actions
- **Direct SQL**: AI MUST NEVER execute raw `UPDATE` or `DELETE` SQL against the production database.
- **Config Injection**: FORBID injecting production environment variables outside the secret manager.

## 21. Critical Severity Matrix
| Action | Severity | Consequence |
| :--- | :--- | :--- |
| Tenant Leak | CRITICAL | Immediate account suspension + Rollback |
| Audit Deletion | CRITICAL | Hard Rejection + Security Audit |
| Unsafe Media Access | HIGH | PR Rejection + Security Review |
| Sync Heavy Operation | MEDIUM | Style Violation + Refactor Request |

## 22. Auto-Rejection Conditions
- Any code containing a `DELETE` SQL command on an operational table.
- Any query missing a `tenant_id` filter in a domain repository.
- Any service method > 100 lines.

## 23. Escalation Rules
- Any violation of "CRITICAL" level must be escalated to the Lead Architect.
- Recurrent violations by an AI agent must trigger a retraining or prompt-refinement cycle.

## 24. Agricultural Disaster Scenarios
- **Inventory Wipe**: An AI agent implements a "Cleanup" task that hard-deletes old inventory batches to save space, destroying the historical cost-basis for 5 years of reports.
- **Privacy Breach**: An AI agent optimizes a "Worker List" query by removing the tenant filter to "simplify the join," allowing a farm manager to see the payroll of a competitor farm.

## 25. Final Enforcement Checklist
- [ ] No `DELETE` commands found.
- [ ] No hardcoded secrets.
- [ ] Tenant filters present in all repositories.
- [ ] No sync-heavy tasks in views.
- [ ] No Django signals for logic.
- [ ] No public S3 buckets created.
- [ ] Audit logs are immutable.
- [ ] Inventory mutated via Service only.
- [ ] No circular dependencies.
- [ ] All forms are mobile-first.
