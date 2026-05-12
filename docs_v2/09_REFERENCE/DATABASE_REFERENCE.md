# Database Reference & Schema Standards

| Metadata | Details |
| :--- | :--- |
| **Document ID** | ATLS-REF-DAT |
| **Status** | AUTHORITATIVE |
| **Version** | 2.0.0 |
| **Owner** | Database Architecture Team |
| **Applicability** | Global Persistence & Schema Governance |

## 1. Database Philosophy
The database is the **Platform's Memory**. In ATLS, data integrity, multi-tenant isolation, and chronological accuracy are prioritized over developer convenience. We treat our PostgreSQL schema as a high-fidelity record of agricultural history.
- **Strictly Isolated**: Tenant data must never bleed.
- **Immutable History**: Soft deletes and audit trails are standard.
- **AI-Optimized**: Schema design must be clear and predictable for automated agents.

## 2. PostgreSQL Standards
- **Version**: PostgreSQL 15+ (LTS).
- **Extensions**: `pgcrypto`, `uuid-ossp`, `postgis` (for GeoJSON).
- **Encoding**: `UTF-8`.
- **Timezone**: `UTC` (All timestamps).

## 3. UUIDv7 Rules
- **Standard**: UUIDv7 is the MANDATORY primary key format for all tables.
- **Benefit**: Time-ordered UUIDs provide high insert performance and natural chronological sorting.
- **FORBIDDEN**: Auto-incrementing integer primary keys.

## 4. Tenant Isolation Columns
- Every table (with rare system exceptions) MUST include a `tenant_id` column.
- **Type**: `UUID`.
- **Constraint**: `NOT NULL`.
- **Indexing**: Always included in the primary index or a dedicated B-tree index.

## 5. Base Entity Fields
All tables must inherit from a `BaseEntity` with:
- `id`: `UUIDv7` (PK).
- `tenant_id`: `UUID` (FK).
- `is_deleted`: `Boolean` (Default: `False`).
- `created_at`: `DateTime`.
- `updated_at`: `DateTime`.
- `created_by_id`: `UUID` (FK).
- `updated_by_id`: `UUID` (FK).

## 6. Timestamp Standards
- Use `TIMESTAMPTZ` for all date-time fields.
- Use `DATE` for agricultural events that do not require time-of-day precision (e.g., `planting_date`).

## 7. Soft Delete Standards
- **Implementation**: `is_deleted` column.
- **Filtering**: All managers must default to `is_deleted=False`.
- **Auditing**: Deletion actions must record a reason in the audit log.

## 8. Audit Field Standards
- `correlation_id`: `UUID` (Optional but recommended for linking operations).
- `version`: `Integer` (For optimistic locking).

## 9. Naming Conventions
- **Casing**: `snake_case` for everything.
- **Singular**: Use singular table names (e.g., `harvest_load`, not `harvest_loads`).

## 10. Table Naming Rules
- Format: `[app_name]_[entity_name]` (e.g., `harvest_load`, `inventory_batch`).

## 11. Column Naming Rules
- Foreign keys: `[entity]_id` (e.g., `enclosure_id`).
- Booleans: `is_[state]` or `has_[property]` (e.g., `is_active`, `has_media`).

## 12. Foreign Key Rules
- **Constraints**: Mandatory `ON DELETE PROTECT` or `ON DELETE SET NULL` for operational data.
- **Cross-Domain**: Avoid hard FKs between bounded contexts; use UUID pointers and Event-Driven consistency.

## 13. Indexing Standards
- **Mandatory**: All Foreign Keys must be indexed.
- **Type**: `B-tree` for IDs/Dates; `GIN` for JSONB.

## 14. Composite Index Rules
- Use for multi-column lookups (e.g., `tenant_id` + `is_deleted` + `created_at`).

## 15. Unique Constraint Rules
- Must include `tenant_id` (e.g., `unique(tenant_id, batch_number)`).

## 16. Enum Storage Rules
- Use `TextChoices` or `IntegerChoices` at the application level.
- Store as `VARCHAR` or `SMALLINT` in DB for flexibility; avoid native PostgreSQL `ENUM` types.

## 17. JSONB Usage Rules
- Use only for unstructured metadata or highly dynamic form data.
- **FORBIDDEN**: Storing primary relational data inside JSONB.

## 18. Materialized Path Rules
- For hierarchies (e.g., Farm -> Block -> Enclosure), use a `path` field (e.g., `001.002.005`) for high-speed recursive queries.

## 19. Read Model Tables
- Suffix: `_projection` or `_summary` (e.g., `harvest_yield_summary`).
- Populated asynchronously via events.

## 20. Outbox Table Reference
- Table: `core_outbox`.
- Fields: `id`, `event_type`, `payload`, `processed_at`.

## 21. Audit Table Reference
- Table: `audit_event`.
- Fields: `id`, `actor_id`, `action`, `target_entity`, `before_state`, `after_state`.

## 22. Inventory Ledger Tables
- Table: `inventory_ledger`.
- Stores every stock delta (In/Out) to ensure 100% balance integrity.

## 23. Harvest Batch Tables
- Table: `harvest_batch`.
- Links multiple `harvest_load` records to a single seasonal lot.

## 24. Reporting Tables
- Dedicated tables for pre-aggregated seasonal reports to speed up dashboard loads.

## 25. Media Tables
- Table: `media_asset`.
- Stores metadata, S3 keys, and GPS coordinates for evidence files.

## 26. Notification Tables
- Table: `notification_log`.
- Tracks delivery status across multiple channels.

## 27. Analytics Projection Tables
- Wide tables optimized for read-heavy analytical dashboards.

## 28. Migration Standards
- Use Django Migrations.
- **Non-Blocking**: Large schema changes must use a 3-step rollout (Add -> Populate -> Constraint).

## 29. Performance Constraints
- **Table Size**: Partition tables exceeding 50 million rows (e.g., `audit_event`).
- **Join Limit**: Avoid joins > 5 tables in a single query.

## 30. AI Safety Rules
- **Auto-Increment**: AI agents MUST NOT use auto-incrementing integer primary keys.
- **Direct Mutation**: FORBID direct database mutation of inventory counts; use the ledger system.
- **Missing Indexes**: FORBID creating tables without indexing foreign keys and `tenant_id`.
- **Tenant ID**: FORBID any schema change that removes or makes `tenant_id` optional.
- **Nullable**: FORBID "Giant Nullable Schemas"; use proper normalization or JSONB for sparse data.
- **JSON Usage**: FORBID using JSONB for core relational identifiers or status flags.
- **Cross-Domain**: FORBID hard Foreign Keys that cross bounded context boundaries (e.g., `Harvest` to `Personnel`).

## 31. Forbidden Database Anti-Patterns
- **The EAV Pattern**: (Entity-Attribute-Value) Use JSONB or dynamic engine instead.
- **Database Logic**: No Triggers or Stored Procedures for business logic.
- **Shared PKs**: Reusing IDs across tenants.

## 32. Agricultural ERP Database Scenarios
- **Seasonal Rollover**: How the database handles the transition from Season 2025 to 2026 without losing historical enclosure data.
- **Harvest Spike**: Handling 500+ writes per second during the peak harvest hour.

## 33. Future Scaling Notes
- Sharding by `tenant_id` or `region_id`.
- Read replicas for the Analytics domain.

## 34. Final Database Checklist
- [ ] UUIDv7 used for all PKs.
- [ ] `tenant_id` present on all tables.
- [ ] `is_deleted` and timestamps present.
- [ ] Foreign keys indexed.
- [ ] JSONB used appropriately.
- [ ] Naming conventions followed (snake_case).
- [ ] No hard-deletes implemented.
- [ ] No database-level triggers for business logic.
