# ATLS Platform: Database Architecture

> **Confidential & Proprietary**  
> **Target Audience:** Principal Architects, Engineering Leads, AI Implementation Agents  
> **Type:** Master Governance Document  

---

## 1. Database Philosophy
The database is the ultimate source of truth for the ATLS platform. Its architecture must prioritize data integrity, auditability, and multi-tenant isolation above all else. We treat the database not merely as a dumb storage layer for an ORM, but as a highly structured relational engine that enforces constraints, guarantees ACID properties, and supports complex CQRS read projections.

## 2. PostgreSQL Selection Rationale
PostgreSQL is the authoritative database for the ATLS platform. It was selected for its:
*   **ACID Compliance:** Unwavering transactional integrity for financial and agricultural ledger data.
*   **JSONB Support:** Allowing flexible schemaless attributes within strictly typed tables (e.g., dynamic equipment telemetry).
*   **Geospatial Capabilities:** PostGIS integration for future precision agriculture and mapping features.
*   **Robust Indexing:** B-Tree, GIN, and GiST indexes to handle complex querying and spatial bounding boxes.

## 3. Monolith Database Strategy
Currently, ATLS operates a Modular Monolith. All bounded contexts (Farm, HR, Operations, Inventory) share a single primary PostgreSQL cluster. This simplifies operational overhead, backups, and cross-domain event routing while the platform scales.

## 4. Future Service Extraction Strategy
While domains share a cluster, they **must not** share tables. A query from the HR Domain cannot `JOIN` directly against a table in the Operations Domain. By strictly separating tables by Bounded Context today, we ensure that if the Harvest Domain needs to become an independent microservice tomorrow, its tables can be lifted and shifted to a dedicated database without shattering the application.

## 5. Schema Separation Rules
*   Tables must be prefixed or grouped by their Bounded Context (e.g., `hr_worker`, `inv_transaction`, `ops_task`).
*   PostgreSQL Schemas (`CREATE SCHEMA`) may be utilized to further enforce physical separation between domains if required by future deployment architectures.

## 6. Tenant Isolation Rules
*   **MANDATORY:** Every table containing tenant-specific data MUST have a `tenant_id` column.
*   `tenant_id` must be part of composite indexes where appropriate to ensure lightning-fast tenant-scoped queries.
*   Application-level Row-Level Security (RLS) or strict ORM global filters must be applied to guarantee cross-tenant data leakage is mathematically impossible.

## 7. UUIDv7 Strategy
*   Platform-wide, all primary keys MUST utilize **UUIDv7**.
*   Unlike UUIDv4, UUIDv7 is time-sortable. This prevents index fragmentation and massive performance degradation in large B-Tree indexes as tables grow to hundreds of millions of rows.
*   UUIDv7 ensures offline mobile apps can generate unique keys without synchronous database coordination.

## 8. Primary Key Rules
*   Always use UUIDv7 for PKs.
*   Auto-incrementing Integers (`SERIAL`) are strictly forbidden for primary entity keys to prevent enumeration attacks and to support offline-first distributed data creation.

## 9. Foreign Key Rules
*   Foreign Keys MUST be explicitly defined at the database level to enforce referential integrity.
*   Every Foreign Key MUST be indexed. PostgreSQL does not automatically index FKs; failing to index them will result in catastrophic locking during `DELETE` or `UPDATE` operations.

## 10. Aggregate Persistence Rules
*   An Aggregate is saved as a single transactional unit.
*   The Root Entity and its child entities are persisted together. If the database transaction fails, the entire Aggregate state rolls back.

## 11. Transaction Rules
*   Keep transactions as short as possible.
*   Never perform external network calls (e.g., sending an email, calling Stripe API) inside an open database transaction.
*   Use `READ COMMITTED` isolation level as standard, elevating to `SERIALIZABLE` only for highly sensitive financial/inventory ledger operations where concurrent anomalies are unacceptable.

## 12. Soft Delete Architecture
*   **Hard deletes (`DELETE FROM...`) are strictly forbidden** for business entities (Workers, Sectors, Operations).
*   Every entity table MUST implement soft deletion via an `is_active` (boolean) or `deleted_at` (timestamp) column.
*   Soft-deleted records must cascade their inactive state to child relations logically or programmatically, maintaining historical integrity.

## 13. Audit Field Standards
Every operational table MUST include standard audit fields:
*   `created_at` (Timestamp, not null)
*   `updated_at` (Timestamp, not null)
*   `created_by` (UUID, reference to User/System)
*   `updated_by` (UUID, reference to User/System)

## 14. Audit Persistence Rules
*   Audit logs for critical actions (e.g., overriding a completed harvest) are immutable.
*   They are written to dedicated `audit_log` tables and cannot be updated or soft-deleted.

## 15. Event Outbox Architecture
*   To guarantee reliable Domain Event publishing, ATLS utilizes the Transactional Outbox pattern.
*   Domain Events are serialized to JSON and saved to an `outbox_events` table *within the same database transaction* as the Aggregate mutation.
*   A background worker reliably reads the Outbox table and publishes to the message broker (RabbitMQ/Kafka).

## 16. Event Store Philosophy
*   While not currently utilizing full Event Sourcing, critical domains (like Inventory) may persist a continuous ledger of events that can be replayed to reconstruct state.

## 17. CQRS Read Model Storage
*   The Analytics and Reporting domains rely on Read Models.
*   Read Models are separate, highly denormalized tables populated asynchronously.
*   They intentionally duplicate data to avoid expensive JOINs during synchronous HTTP reads.

## 18. Projection Tables
*   Tables specifically designed for the UI. (e.g., `dashboard_daily_yield_projection`).
*   If a projection table is corrupted, it can be entirely truncated and rebuilt by replaying historical Domain Events.

## 19. Materialized Views Strategy
*   PostgreSQL Materialized Views may be used for complex aggregations that do not require real-time accuracy (e.g., `monthly_farm_financial_summary`).
*   They must be refreshed concurrently via scheduled background workers (`REFRESH MATERIALIZED VIEW CONCURRENTLY`).

## 20. Indexing Philosophy
*   Index columns frequently used in `WHERE` clauses, `JOIN` conditions, and `ORDER BY` clauses.
*   Use GIN indexes for JSONB columns requiring fast key-value searches.
*   Over-indexing slows down `INSERT`/`UPDATE`. Only index proven query paths.

## 21. Query Optimization Rules
*   Beware of N+1 query problems. Use ORM capabilities (`select_related`, `prefetch_related`) to join data eagerly when required.
*   Use `EXPLAIN ANALYZE` to verify index usage on slow queries.

## 22. Partitioning Strategy
*   Tables expected to exceed 50 million rows (e.g., `ops_telemetry_log`, `hr_attendance_ping`) must be natively partitioned.
*   Time-based partitioning (by Month or Year) is the default strategy for immutable log data to enable efficient bulk archiving.

## 23. Time-Series Data Rules
*   High-frequency telemetry (e.g., tractor engine RPM every second) should be funneled into specialized time-series structures (like TimescaleDB extensions) rather than standard relational tables.

## 24. Media Persistence Strategy
*   **Media binaries (Images, Videos, PDFs) MUST NOT be stored in PostgreSQL `BYTEA` columns.**
*   PostgreSQL is for metadata only.

## 25. File Metadata Persistence
*   The database stores `MediaAsset` records containing: `file_url` (S3/Cloud path), `mime_type`, `size_bytes`, and `tenant_id`.

## 26. Offline Sync Persistence
*   Mobile apps sync using `updated_at` high-water marks.
*   The database must precisely track microsecond-level updates to ensure devices only pull records changed since their last sync.

## 27. Conflict Resolution Persistence
*   Data submitted by offline devices may conflict with server state.
*   The database utilizes Last-Write-Wins (LWW) based on device-originated timestamps for standard fields, but requires additive ledgers for critical data (Inventory, Runtimes).

## 28. Inventory Ledger Persistence
*   Inventory is strictly **Append-Only**.
*   You do not `UPDATE inv_stock SET quantity = 50`.
*   You `INSERT` an `InventoryTransaction` of `-10`. The current stock is a SUM of the ledger.

## 29. Historical Snapshot Rules
*   Transactional records (Operations, Harvests) must copy relevant hierarchy and context paths into their own tables at creation time.
*   If "Sector 4" is later renamed or moved, the historical Harvest record retains the snapshot of what Sector 4 was at the exact moment of the harvest.

## 30. Temporal Integrity Rules
*   Database constraints must prevent temporal paradoxes (e.g., an Operation cannot end before it started; a machinery breakdown cannot be logged before the machine was purchased).

## 31. Backup & Restore Philosophy
*   Continuous WAL (Write-Ahead Logging) archiving is mandatory.
*   Point-in-Time Recovery (PITR) must be supported to allow restoring the database to a specific minute before a catastrophic user error.

## 32. Disaster Recovery Rules
*   Read-replicas must be deployed in multi-AZ configurations for automatic failover.
*   Backups must be geo-redundant and tested quarterly.

## 33. Migration Rules
*   Schema migrations must be backward compatible.
*   Never drop a column or table in a single deployment. Phase 1: Ignore column in code. Phase 2: Drop column in DB.
*   Long-running migrations (e.g., adding an index to a 100M row table) MUST be executed `CONCURRENTLY` to avoid table locks.

## 34. AI Safety Rules
> [!CAUTION]
> **MANDATORY AI IMPLEMENTATION RULES**
> *   **No Direct Stock Mutation:** AI MUST NOT write SQL or ORM code that directly updates an inventory quantity field. Must use ledger insertions.
> *   **No Missing Tenant Filters:** AI MUST ensure every query against a tenant-aware table explicitly filters by `tenant_id`.
> *   **No Hard Deletes:** AI MUST NOT write `DELETE FROM` statements for domain entities. Use soft deletes.
> *   **Index Foreign Keys:** AI MUST explicitly declare indexes on all generated Foreign Key migrations.
> *   **No N+1 Queries:** AI MUST utilize eager loading in ORM queries returning lists of aggregates.
> *   **No ORM Lazy-Loading Abuse:** AI MUST NOT loop over ORM collections that trigger implicit database queries inside the loop.
> *   **No Giant Polymorphic Tables:** AI MUST avoid the "Entity-Attribute-Value" (EAV) anti-pattern or massive polymorphic tables without strict partitioning.

## 35. Forbidden Database Anti-Patterns
*   **The God Table:** A single `tasks` table trying to hold Harvesters, Mechanics, and HR Reviews via 50 nullable columns.
*   **String Primary Keys:** Using email addresses or names as Primary Keys.
*   **Business Logic in Triggers:** Hiding complex yield calculations inside PostgreSQL `BEFORE UPDATE` triggers where application developers cannot debug them.

## 36. Performance Constraints
*   OLTP (Transactional) queries must execute in < 50ms.
*   Any query taking > 500ms must be moved to an asynchronous background job or a pre-calculated CQRS Read Model.

## 37. Real-World Agricultural Scenarios
**Scenario:** A massive offline batch of Harvest Yields hits the API at 6:00 PM when all supervisors return to Wi-Fi.
*   **Database Impact:** The database receives 10,000 insertions in 10 seconds.
*   **Architecture Response:** Because PKs are UUIDv7, B-Tree insertion is sequential and blazingly fast. Records are inserted into the Harvest domain tables. Outbox events are written. The database is not bogged down trying to calculate analytics synchronously; it only handles the raw persistence, allowing the background workers to build the analytics dashboards overnight.

## 38. Future Evolution Strategy
*   Transitioning historical, immutable logs (e.g., sensor telemetry older than 1 year) out of PostgreSQL and into cold storage (S3/Parquet) queried via Amazon Athena or similar, keeping the primary PostgreSQL cluster lean and highly performant.
