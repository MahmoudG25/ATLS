# Query & ORM Governance

| Metadata | Details |
| :--- | :--- |
| **Document ID** | ATLS-BACK-03 |
| **Status** | AUTHORITATIVE |
| **Version** | 2.0.0 |
| **Owner** | Backend Architecture Team |
| **Applicability** | All Backend Database Interactions |

## 1. Query Philosophy
Database performance is the primary bottleneck for ATLS at scale. We treat the database as a precious resource.
- **Explicit over Implicit**: No hidden queries. Every query must be traceable to a specific intent.
- **Minimal Data Transfer**: Only fetch the columns and rows absolutely necessary for the current task.
- **Safety First**: Every query must be automatically scoped by the tenant context.

## 2. ORM Governance
- **Location**: All ORM logic must reside in `repositories/` (for writes) or `selectors/` (for reads).
- **Encapsulation**: Models and Views **must not** build complex QuerySets. 
- **Exclusivity**: Use the Django ORM for 99% of tasks. Only bypass for highly specialized reporting/analytics.

## 3. Read vs Write Queries
- **Write Path**: Handled by Services using Repositories. Focuses on data integrity and single-record precision.
- **Read Path**: Handled by Selectors. Focuses on performance, aggregation, and formatting for the UI.

## 4. QuerySet Standards
- **Lazy Evaluation**: Understand when a QuerySet is evaluated (looping, slicing, `repr()`).
- **Reuse**: Shared QuerySet logic should be defined in a `QuerySet` class on the model, not duplicated in multiple selectors.

## 5. select_related Rules
Use `select_related` for **1-to-1** and **Forward ForeignKey** relations.
- **Rule**: Always use `select_related` when accessing a related object's attribute (e.g., `harvest.block.name`).
- **Constraint**: Do not chain more than 3 levels deep without performance review.

## 6. prefetch_related Rules
Use `prefetch_related` for **1-to-Many** and **Many-to-Many** relations.
- **Rule**: Use `Prefetch()` objects to apply filtering or sorting to the related QuerySet, avoiding extra DB hits later.
- **Constraint**: Be mindful of the "Product of Fetches" memory usage for large datasets.

## 7. Pagination Rules
- **Operational Feeds**: Use **Cursor-based Pagination** (e.g., `django-filter` with `CreatedDate`) for high-frequency feeds to avoid "skipping" items when new data is inserted.
- **Admin/Search**: Use **Offset Pagination** (Standard DRF) for fixed datasets where jumping to a specific page is required.
- **Max Limit**: Every list endpoint must have a hard `PAGE_SIZE` limit (default 50, max 200).

## 8. Filtering Standards
- **Backend-Driven**: Use `django-filter` for declarative filtering.
- **Allowed Fields**: Explicitly define `filterset_fields`. Never allow arbitrary filtering on unindexed columns.

## 9. Sorting Standards
- **Default**: Every model must have a default `ordering` (usually `-created_at`).
- **User-Defined**: Allow sorting only on indexed columns.

## 10. Aggregation Rules
- **Database-Side**: Perform all sums, averages, and counts in PostgreSQL using `.aggregate()` or `.annotate()`.
- **FORBIDDEN**: Looping through records in Python to calculate totals.

## 11. Projection Queries
- **Values/Only**: Use `.only('field1', 'field2')` or `.values()` for high-volume list endpoints to reduce memory and transfer overhead.
- **Defer**: Use `.defer('large_json_field')` when the field is not needed for the current view.

## 12. CQRS Read Models
For complex dashboards (e.g., Seasonal Yield Summary), create dedicated **Read Models** (Materialized Views or dedicated tables) that are updated via Domain Events. 
- **Reason**: Complex joins across 5+ tables for every request will not scale.

## 13. Raw SQL Constraints
- **Approval**: Requires senior architecture approval.
- **Usage**: Only for complex CTEs or window functions not supported by the ORM.
- **Safety**: Always use parameterized queries to prevent SQL injection.

## 14. Tenant Scoping
- **Global Manager**: Every query must pass through a `TenantManager` that automatically injects `WHERE tenant_id = X`.
- **Bypass**: Bypassing tenant filters (e.g., for cross-tenant system reports) must be done via an explicit `.as_system_admin()` manager method.

## 15. Index Usage
- **Requirement**: Any field used in `filter()`, `exclude()`, or `order_by()` must be indexed.
- **Composite Indexes**: Use for frequent multi-field filters (e.g., `tenant_id` + `status`).

## 16. Async Query Constraints
- **Celery**: Use `.iterator()` when processing > 1000 records in a background task to keep memory usage constant.
- **Chunking**: Break massive updates into chunks of 500 records.

## 17. Reporting Queries
- **Read-Only Replica**: Route long-running reporting queries to a database replica to avoid locking the primary instance.
- **Timeout**: Set a hard 10-second timeout for any reporting query.

## 18. Analytics Queries
- **Pre-aggregation**: Perform hourly/daily pre-aggregations for KPIs.
- **Constraints**: Do not perform live analytics on the primary transactional tables for > 3 months of data.

## 19. Performance Monitoring
- **Silk/Debug Toolbar**: Use in development to count queries per request.
- **CloudWatch/RDS Insights**: Monitor for "Slow Queries" in production.
- **Alerting**: Alert when query count per request exceeds 30.

## 20. AI Safety Rules
- **N+1**: AI agents MUST NOT commit code that triggers N+1 queries (queries inside loops).
- **Unbounded**: FORBID queries without `.limit()` or pagination on large tables.
- **Select All**: FORBID `SELECT *` (default ORM behavior) on tables with large text/JSON blobs; use `.only()`.
- **Loops**: FORBID performing ORM mutations or fetches inside a `for` loop.
- **Tenant**: FORBID queries that do not explicitly include a `tenant_id` filter (unless via the global manager).
- **Blocking**: FORBID long-running analytics queries on the primary database thread.
- **Joins**: FORBID "Giant Joins" (> 5 tables); use pre-aggregated read models or subqueries.

## 21. Forbidden Query Anti-Patterns
- **Count in Loop**: Calling `.count()` inside a loop.
- **Existence via Fetch**: Using `if len(qs) > 0` instead of `if qs.exists()`.
- **Full Table Scan**: Filtering on unindexed text fields.

## 22. Agricultural Data Scenarios
- **Worker Timeline**: Fetching attendance for 500 workers. Use `prefetch_related` for worker details and `select_related` for farm block info.
- **Pesticide Inventory**: Calculating current stock. Use `.aggregate(Sum('quantity'))` in the database.

## 23. Enforcement Checklist
- [ ] No N+1 queries (verified with logs).
- [ ] All filters use indexed columns.
- [ ] Tenant scoping is active.
- [ ] Pagination is implemented for all list endpoints.
- [ ] Large fields are deferred or projected via `.only()`.
- [ ] No DB queries in loops.
- [ ] Complexity < 3 joins per query.
- [ ] Default ordering is defined.
