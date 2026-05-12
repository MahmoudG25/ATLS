# Audit & Compliance Domain

| Metadata | Details |
| :--- | :--- |
| **Document ID** | ATLS-DOM-AUD |
| **Status** | AUTHORITATIVE |
| **Version** | 2.0.0 |
| **Owner** | Architecture & Compliance Team |
| **Applicability** | Global System Audit & Operational Traceability |

## 1. Audit Domain Philosophy
The Audit Domain is the **"Black Box"** of the ATLS platform. It provides an incontrovertible, chronological record of every significant event that occurs within the system. In an agricultural ERP, auditability is not just about security; it is about food safety, chemical compliance, and financial accountability.
- **Incontrovertible**: Evidence that holds up in a court of law or a regulatory inspection.
- **Comprehensive**: Every state change must be traceable to a specific actor and context.
- **Passive Enforcement**: Audit tracking should happen automatically with zero friction for the end-user.

## 2. Immutable History Principles
- **Append-Only**: Data can only be written, never updated or deleted.
- **Cryptographic Chaining**: (Future) Hash-linking of audit blocks to detect tampering.
- **Indelible**: Once a record is committed to the audit store, it is permanent until the end of its retention lifecycle.

## 3. Audit Aggregate Structure
The core aggregate of this domain is the `AuditEvent`:
- **Actor**: `user_id`, `service_id`, `api_key_id`.
- **Action**: `CREATE`, `UPDATE`, `DELETE`, `EXECUTE`, `LOGIN`, `EXPORT`.
- **Target**: `entity_type` (e.g., `HarvestReport`), `entity_id` (UUID).
- **Context**: `tenant_id`, `ip_address`, `device_id`, `correlation_id`, `user_agent`.
- **Payload**: `before_state`, `after_state`, `diff`.

## 4. Audit Event Taxonomy
1. **SEC (Security)**: Authentication, Permission changes, API Key creation.
2. **OPS (Operational)**: Harvest logs, Labor assignments, Equipment usage.
3. **FIN (Financial)**: Invoicing, Payroll approval, Price changes.
4. **CHM (Chemical)**: Pesticide application, Fertilizer mixing, Safety threshold alerts.
5. **SYS (System)**: Configuration changes, Feature flag toggles, Migration execution.

## 5. Operational Audit Rules
- Every change to an operational entity (Farm, Enclosure, Crop) must record a "Before" and "After" snapshot.
- Changes to "Master Data" require reason codes (e.g., `DATA_CORRECTION`, `OPERATIONAL_RESTRUCTURING`).

## 6. Security Audit Rules
- Log all failed login attempts (including IP and User Agent).
- Log any elevation of privileges (e.g., adding an `Admin` role to a user).
- Log all access to "Sensitive Data" (e.g., Exporting worker payroll lists).

## 7. Financial Audit Rules
- **Non-Repudiation**: Every financial transaction must be signed (or traceable to a specific session token).
- **History**: Historical financial records must never be overwritten; use "Adjustment" records instead.

## 8. Inventory Audit Rules
- **Balance Integrity**: Every stock movement must link back to an audit record that explains the delta (Purchase, Usage, Waste, Correction).

## 9. Harvest Audit Rules
- **Traceability**: Every harvest load must be traceable to the specific supervisor and field worker who logged it, ensuring accountability for quality issues.

## 10. User Action Tracking
- Capture the exact UI interaction if it leads to a state change (e.g., "Clicked 'Confirm Harvest' from mobile app").
- Store the session lifetime alongside the audit trail.

## 11. Entity Change Snapshots
- For complex entities, store a full JSON snapshot of the aggregate state at the moment of change.
- **Rule**: Snapshots must not include transient fields (e.g., cached totals).

## 12. Diff Storage Strategy
- Store deltas using a standardized JSON Patch (RFC 6902) format.
- **Benefit**: Minimizes storage usage while allowing for easy "Undo" or "Replay" logic.

## 13. Before/After State Rules
- **Mandatory**: For any entity change in a `Closed` season or involving financial/chemical data.
- **Comparison**: The UI must be able to render a "Side-by-Side" diff of these states for auditors.

## 14. Soft Delete Audit Rules
- ATLS uses Soft Deletes (`is_deleted = True`). 
- The audit record must capture the state *before* deletion and the reason for the action.

## 15. Approval Workflow Auditing
- Capture who requested the approval, who granted it, the timestamp, and any comments attached to the decision.

## 16. Critical Event Classification
Events are tagged with a `SeverityLevel`:
- **LOW**: Standard CRUD on non-critical data.
- **MEDIUM**: Status changes, user management.
- **HIGH**: Financial commits, Chemical logs, Security breaches, Global configuration changes.

## 17. Multi-Tenant Audit Isolation
- Every audit record is strictly partitioned by `tenant_id`.
- **Safety**: Tenant A must never be able to query Audit logs from Tenant B.
- **Querying**: Use the global `TenantManager` for all audit lookups.

## 18. Compliance Retention Rules
- **Operational Logs**: 5 years.
- **Financial/Chemical Logs**: 10 years.
- **Security Logs**: 2 years.
- **Metadata**: Retained indefinitely.

## 19. Long-Term Archival Strategy
- Audit logs > 12 months old are moved to a **Compressed Cold Store** (e.g., S3 Glacier / BigQuery).
- **Retrieval**: Archives must be searchable within 4 hours.

## 20. Search & Filtering Architecture
- Use a dedicated **Search Index** (Elasticsearch/OpenSearch) for fast audit lookups.
- Support filtering by: `Actor`, `Target Entity`, `Date Range`, `Action Type`, and `Tenant`.

## 21. Timeline Reconstruction
- The system must provide a `GetTimeline(entity_id)` selector that returns the full history of an entity in chronological order.

## 22. Correlation ID Strategy
- A single `correlation_id` must follow a request from the Frontend, through the API, into the Service Layer, and into the Audit Log.
- **Benefit**: Link a UI action to multiple background database changes.

## 23. Event Source Tracking
- Log if the event originated from: `MOBILE_APP`, `WEB_DASHBOARD`, `CELERY_TASK`, `ADMIN_OVERRIDE`, `EXTERNAL_API`.

## 24. IP & Device Tracking
- Capture `ip_address` (IPv6 preferred) and `device_fingerprint` for every state-changing request.

## 25. Offline Audit Synchronization
- **Mobile Traceability**: For offline operations, capture the local device timestamp AND the server synchronization timestamp.
- **Conflict Audit**: Log when an offline conflict is resolved manually.

## 26. Read Model Strategy
- Avoid querying the primary Audit table for dashboards.
- Use a **Projection Read Model** (Materialized View) for "Recent Activity" feeds.

## 27. Alert Escalation Rules
- **SEV-HIGH** events (e.g., unauthorized access attempt) must trigger an immediate Slack/PagerDuty alert to the Security team.

## 28. Tamper Prevention Rules
- Audit logs are stored in a database with **Delete/Update permissions revoked** for the standard application user.
- **Storage**: Use "Object Lock" (WORM) storage for exported audit backups.

## 29. Audit Performance Constraints
- **Writing**: Audit record creation must add < 20ms to the transaction.
- **Latency**: Use an async `Outbox -> Celery` pipeline to offload heavy audit processing.

## 30. Async Audit Pipelines
1. **Sync**: Write minimal `Action` record in the primary transaction.
2. **Async**: Celery task populates the full `Snapshot` and `Diff` asynchronously.

## 31. Audit Compression Strategy
- Use Zstandard (zstd) for JSON payload compression to reduce storage footprint by up to 70%.

## 32. Audit API Exposure Rules
- **Internal**: Full access for SuperAdmins.
- **Tenant**: Access to "Operational Logs" only for TenantAdmins.
- **FORBIDDEN**: Exposing internal security/system audit logs to standard users.

## 33. GDPR/Privacy Constraints
- **Anonymization**: Support "Right to be Forgotten" by masking `user_id` and `ip_address` in historical audit logs without breaking the integrity of the action record itself.

## 34. AI Safety Rules
- **Deleting**: AI agents MUST NOT implement or trigger any logic that deletes or purges audit logs.
- **Modifying**: FORBID any logic that allows the modification of existing audit records.
- **Silent Mutation**: FORBID "Silent State Mutations" (changing database records without an accompanying audit log).
- **Actor Tracking**: FORBID anonymous state changes; every event must have a valid `actor_id`.
- **Bypasses**: FORBID creating "Service Accounts" or "Admin Bypasses" that circumvent audit tracking.
- **Heavy Writes**: FORBID synchronous heavy audit writes; use the Outbox/Celery pipeline for diff calculations.
- **Leakage**: FORBID any audit query that does not include a strict `tenant_id` filter.

## 35. Forbidden Audit Anti-Patterns
- **Logging to File**: Never store audit trails only in server log files; they must be in a structured, queryable database.
- **Storing PII**: Avoid storing raw PII (e.g., Credit Card numbers) in audit diffs; use masked values.
- **Ambiguous Actions**: Using generic action names like `EDIT`; use specific names like `UPDATE_WAGE_RATE`.

## 36. Real Agricultural Audit Scenarios
- **Pesticide Safety Violation**: An auditor investigates why a field was harvested before the safety period ended. The audit log shows who authorized the harvest, what time they did it, and that they bypassed a safety warning.
- **Inventory Discrepancy**: 500L of fertilizer is missing. Audit logs show the last 5 usages, identifying a specific tractor operator who failed to close a usage log.

## 37. Future Compliance Expansion
- **Blockchain Integration**: For high-value crops (Organic, Export-grade), hash-link audit trails to a public/private blockchain for immutable proof of origin.

## 38. Final Audit Enforcement Checklist
- [ ] Every state-changing service call has a corresponding audit log.
- [ ] Before/After snapshots are implemented for critical entities.
- [ ] Correlation IDs flow correctly through the stack.
- [ ] Tenant isolation is active at the DB query level.
- [ ] Critical events trigger real-time alerts.
- [ ] Retention policy is configured in the DB/Cloud store.
- [ ] Diff logic uses JSON Patch standard.
- [ ] Deletion of audit records is physically impossible for the app user.
