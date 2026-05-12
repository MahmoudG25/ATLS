# ATLS Platform: Farm Domain Aggregate Architecture

> **Confidential & Proprietary**  
> **Target Audience:** Senior Engineering Team, AI Implementation Agents, Platform Architects  
> **Domain:** Agricultural ERP & Operations Platform  

---

## 1. Purpose Of This Document

This document defines the strict Domain-Driven Design (DDD) aggregate boundaries for the ATLS Farm Domain. In an enterprise ERP environment dealing with offline field operations, dynamic hierarchies, and millions of transactional records, failure to respect transactional boundaries leads to race conditions, orphaned data, and total system collapse.

Aggregates exist to enforce **transactional consistency boundaries**. They are not mere data containers or ORM relations. They are impenetrable barriers that guarantee domain invariants are never violated, regardless of concurrent operations, offline synchronizations, or distributed processing lags. 

Without absolute transactional discipline, scalable distributed ERP systems cannot function. 

---

## 2. Farm Domain Aggregate Philosophy

The ATLS Farm Domain strictly adheres to the principle of **Aggregate Isolation**. 

*   **Strong Consistency:** Guaranteed *only* within a single aggregate boundary during a single transaction.
*   **Eventual Consistency:** Mandated for all cross-aggregate side effects and read-model updates.
*   **Transactional Ownership:** An aggregate root absolutely owns its internal entities and value objects. No external system may modify an aggregate's internals without routing through the root.
*   **Domain Invariants:** The absolute business rules that must hold true at the commit of any transaction. 

> [!CAUTION]
> **CROSS-AGGREGATE WRITES ARE STRICTLY FORBIDDEN.**  
> A single database transaction MUST NOT modify more than one aggregate instance. If two aggregates must change, modify one, emit a domain event, and modify the second via an eventual consistency handler.

---

## 3. Aggregate Communication Rules

Aggregates in ATLS operate as distributed, isolated state machines.

**Allowed Communication:**
1.  **Application Services:** Orchestrate workflows by loading an aggregate via a repository, invoking a domain method on the root, and saving it back.
2.  **Domain Events:** The *only* mechanism for inter-aggregate communication. Aggregates generate events (e.g., `EnclosureTreesPlanted`), which are dispatched after the transaction commits.
3.  **Read Models (CQRS):** Queries must bypass aggregates entirely and read from dedicated, eventually consistent Read Models or projection tables.

**Explicitly Prohibited:**
*   **Direct Aggregate Mutation:** Do not alter properties of an aggregate without using its defined behavioral methods.
*   **Cross-Repository Mutations:** A service method must never call `.save()` on two different repositories.
*   **Nested Aggregate Persistence:** Passing one aggregate root into the method of another, and expecting both to persist.

---

## 4. Aggregate Root Catalog

The Farm Domain is partitioned into the following highly-cohesive Aggregate Roots:

| Aggregate Root | Purpose | Consistency Type | Scale Risk |
| :--- | :--- | :--- | :--- |
| **FarmAggregate** | Global farm configuration, branding, tenant policies, and timezone logic. | Strong (Infrequent Updates) | Low |
| **HierarchyAggregate** | Dynamic structural mapping of regions, zones, and custom operational sectors. | Strong (Structural Integrity) | High (Recursion/Cyclic limits) |
| **EnclosureAggregate** | The primary operational unit. Owns tree counts, crops, area metrics, and planting history. | Strong (High Concurrency) | Extreme (Offline sync collisions) |
| **SeasonAggregate** | Temporal bounds locking financial and operational reporting. | Strong (State transitions) | Medium (Lock contention) |

---

## 5. FarmAggregate

**Responsibilities:**
The `FarmAggregate` is the configuration root of the tenant's physical operation. It owns structural policies but NOT the structure itself.

**Owned Entities & Value Objects:**
*   Farm Settings (Timezone, Units of Measure)
*   White-label Branding Configuration
*   Operational Configuration (Allowed crop types, default shift hours)
*   Hierarchy Policy Ownership (Rules governing how deep hierarchies can go)

**Invariants:**
*   A farm must have an explicitly defined timezone.
*   A farm's operational currency and unit system (Metric/Imperial) cannot change once transactional data exists.

**Forbidden Responsibilities:**
*   *DOES NOT* own Enclosures.
*   *DOES NOT* own Seasons or tasks. Loading the Farm must never load the physical assets.

---

## 6. HierarchyAggregate

**Responsibilities:**
Manages the dynamic, infinite-depth (up to system limits) parent-child structure of the physical farm (e.g., Region -> Sector -> Plot).

**Dynamic Node Structures:**
Nodes are manipulated via explicit domain methods (`MoveNode`, `DeactivateBranch`), not by changing a `parent_id` foreign key.

**Invariants & Structural Validation:**
*   **Cycle Prevention:** A node can never become a child of itself or its descendants.
*   **Depth Rules:** Hierarchy depth cannot exceed the configured tenant maximum (prevents stack overflows in recursive CTEs).

> [!WARNING]
> **Recursive Corruption Risk**  
> Arbitrary re-parenting without aggregate validation can detach millions of child records from tenant visibility policies. Hierarchy re-parenting is an expensive, isolated transaction.

---

## 7. EnclosureAggregate

**Responsibilities:**
The absolute source of truth for physical, trackable asset boundaries. This is the most heavily mutated aggregate in the system due to mobile field operations.

**Operational Ownership:**
*   **Tree Count Rules:** Strict accounting of living, dead, and planted trees.
*   **Crop Ownership:** Cultivar and rootstock historical tracking.
*   **Media Ownership:** Geospatial polygons, images, and attachments belonging strictly to the enclosure.
*   *Note:* It owns the *definition* of analytics targets, but the *calculated aggregations* live in Read Models.

**Strict Invariants:**
*   `TotalLivingTrees` MUST NEVER be negative.
*   `PlantedArea` MUST NEVER exceed `TotalEnclosureArea`.
*   Planting histories are **immutable**. Corrections require additive compensation records, not updates to historical rows.
*   **Seasonal Locking:** If the active season is closed, Enclosure asset metrics cannot be altered without a `SUPER_ADMIN` audit override.

---

## 8. SeasonAggregate

**Responsibilities:**
Defines the financial and operational temporal boundaries of the farm. 

**Lifecycle & State Machine:**
*   `DRAFT` -> `ACTIVE` -> `CLOSING` -> `CLOSED` -> `ARCHIVED`

**Locking Behavior:**
*   When `CLOSING`, the season accepts no new operations but allows pending offline syncs to resolve.
*   When `CLOSED`, all historical records tied to this season become cryptographically immutable.
*   Reopening a `CLOSED` season requires a break-glass protocol and generates an executive audit trail.

**Async Closing Strategy:**
Closing a season fires an event triggering async calculation finalizations across all related Enclosures. The season state drives read-model freezes.

---

## 9. Aggregate Invariants

| Aggregate | Business Invariants | Forbidden Mutations | Data Integrity Rules |
| :--- | :--- | :--- | :--- |
| **FarmAggregate** | Base currency is immutable post-setup | No mutating `tenant_id` | Must have >= 1 active admin |
| **HierarchyAggregate**| Strict acyclic directed graph (DAG) | No raw SQL `parent_id` updates | Orphaned nodes immediately tombstoned |
| **EnclosureAggregate**| `active_trees >= 0`, `area > 0` | No overriding history logs | Geospatial polygon must be valid and closed |
| **SeasonAggregate** | Dates cannot overlap active seasons | No standard user can reopen | End date must be > Start date |

---

## 10. Transaction Boundary Rules

**Inside a Single Transaction (Synchronous):**
*   Loading the aggregate root.
*   Executing business logic and invariant checks.
*   Updating the aggregate's internal state.
*   Saving the aggregate.
*   Dispatching Domain Events to an Outbox table (Transactional Outbox pattern).

**Outside the Transaction (Asynchronous/Eventual):**
*   Sending push notifications.
*   Updating ElasticSearch/Read Models.
*   Recalculating parent hierarchy rollups.

**Max Transaction Scope:**
One HTTP Request = One Aggregate Instance = One Database Transaction.

> [!IMPORTANT]
> **Idempotency is Mandatory:**  
> All aggregate mutating methods must be idempotent to support mobile client retries during poor network connectivity. 

---

## 11. Cross Aggregate Event Flow

When a field operation occurs, it triggers an enterprise event flow that respects boundaries:

1.  **[Sync] Operation Created:** Mobile client posts a task. `OperationAggregate` validates and saves.
2.  **[Sync] Event Emitted:** `OperationCompletedEvent` written to Transactional Outbox.
3.  **[Async] Propagation Job Created:** Message broker picks up the event.
4.  **[Async] Child Operations / Enclosures Updated:** The handler loads the `EnclosureAggregate`, applies the tree count delta, and saves.
5.  **[Async] Read Models Updated:** A separate handler listens to `EnclosureTreesUpdatedEvent` to update analytical dashboards.

**Failure Handling:** Dead-letter queues (DLQs) handle failures. Event handlers MUST be idempotent (e.g., using `event_id` tracking).

---

## 12. Aggregate Versioning Strategy

To support massive concurrent offline operations, aggregates utilize strict **Optimistic Locking**.

*   **Version Fields:** Every aggregate root contains a `version` (integer) or `updated_at` (timestamp with microsecond precision).
*   **Stale Write Prevention:** If an offline mobile client attempts to sync an `EnclosureAggregate` with version `4`, but the server is at version `6`, the transaction aborts with a `ConcurrencyException`.
*   **Conflict Resolution:** The client must fetch version `6`, perform a local merge (or additive delta), and re-submit.

---

## 13. Aggregate Persistence Rules

**Repositories:**
Repositories are the *only* gateway to the database. They deal exclusively in Aggregate Roots. You cannot have an `EnclosureImageRepository`; images are saved when the `EnclosureAggregate` is saved.

**Zero ORM Bypass:**
*   NO use of `.update()` or `.bulk_update()` queries that bypass the aggregate lifecycle.
*   NO hidden database triggers. All state changes must occur in the Domain layer code.

Repositories exist to translate pure domain objects into database rows, completely decoupling the business logic from the infrastructure.

---

## 14. Performance Constraints

*   **Aggregate Size Limits:** Aggregates must remain small. An `EnclosureAggregate` should not eagerly load 10 years of historical logs. Use pagination and lazy loading for internal collections.
*   **Payload Limits:** Mobile synchronization payloads are strictly bounded (e.g., max 500 queued operations per sync batch).
*   **Query Limits:** Repositories must never return unbounded lists. 

---

## 15. Multi-Tenant Isolation Rules

ATLS is a multi-tenant platform. Tenant isolation is a zero-tolerance security boundary.

*   **Tenant Ownership:** EVERY aggregate root must contain a `tenant_id`.
*   **Validation:** Repositories must transparently append `WHERE tenant_id = ?` to every single read and write.
*   **Forbidden Access:** No service may ever process aggregates from two different tenants simultaneously.

---

## 16. Offline Synchronization Rules

Mobile-first ERP requires robust offline handling.

*   **Additive Merge Strategy:** Instead of mobile clients submitting absolute states (`trees = 400`), they submit additive intents (`Operation: Plant 50 trees`). This prevents last-write-wins data destruction.
*   **Queued Operations:** Offline writes are stamped with a client-side timestamp and a UUID.
*   **Duplicate Prevention:** The backend checks the UUID against an `OperationLog` intent table. If the UUID exists, the sync request is ignored (Idempotency).

---

## 17. Aggregate Security Rules

*   **Audit Requirements:** Every aggregate mutation must be traceable to a `user_id`, `device_id`, and `timestamp`.
*   **Soft Delete Philosophy:** Data is NEVER hard-deleted in an ERP. Aggregates use an `is_active` or `deleted_at` flag. Hard deletes destroy historical analytical integrity.
*   **Escalation Rules:** Only users with explicit `ROLE_SYSTEM_ADMIN` can modify aggregate invariants or override version locks.

---

## 18. Aggregate Anti-Patterns

If you implement any of the following, the architecture has failed.

*   **The God Aggregate:** Making `FarmAggregate` hold every `Enclosure`, `Worker`, and `Task` inside it. *Why it's dangerous:* A single user updating their profile locks the entire farm for all other users.
*   **Cross Aggregate Transactions:** Updating an `Enclosure` and a `Worker` in the same `transaction.atomic()` block. *Why it's dangerous:* Destroys scalability and prevents sharding.
*   **Direct ORM Mutation:** `Enclosure.objects.filter(id=1).update(trees=500)`. *Why it's dangerous:* Bypasses all domain invariants, version bumping, and event emission.
*   **Circular Ownership:** Aggregate A requires B to be valid, and B requires A to be valid. *Why it's dangerous:* Impossible to create or delete either without database constraint violations.
*   **Hidden Side Effects:** Updating an aggregate silently triggers an API call to an external billing system inside the model's `save()` method. *Why it's dangerous:* Unpredictable performance and untestable code.

---

## 19. AI Agent Safety Rules

> [!CAUTION]
> **AI-AGENT ENGINEERING DIRECTIVES**  
> All autonomous agents, copilots, and AI engineering tools modifying this codebase are bound by the following unalterable laws:

1.  **NEVER bypass repositories.** You must not write raw SQL or ORM updates that skip the repository layer.
2.  **NEVER mutate aggregates directly.** Do not set `enclosure.trees = 50`. You must call `enclosure.plant_trees(50)`.
3.  **NEVER create hidden writes.** No signals, no DB triggers, no hidden hooks.
4.  **NEVER add business logic to views/controllers.** Views only parse HTTP, call the Application Service, and return JSON.
5.  **NEVER bypass tenant filters.** Every query you write must explicitly account for `tenant_id`.
6.  **NEVER use mass delete/update shortcuts.** You must load the aggregates, apply the domain logic, and save them.

**Service Layer Enforcement:** AI agents must write code that relies purely on the Domain layer to protect itself.

---

## 20. Final Engineering Principles

**Architecture Integrity > Delivery Speed**  
A feature delivered quickly that corrupts the aggregate boundary is a net negative to the enterprise.

**Domain Ownership > Convenience**  
It is always more convenient to update three tables in a single script. In a distributed ERP, convenience causes data anomalies. Respect the domain.

**Scalability > Shortcuts**  
Design every aggregate assuming it will be concurrently edited by 50 offline mobile devices syncing the moment they hit a cellular tower.

**Maintainability > Rapid Hacks**  
The code you write today will be audited by agriculture regulatory bodies in five years. Build it with unshakeable integrity.

---

## 21. Aggregate Event Catalog

| Event Name | Trigger | Producer Aggregate | Consumer Domains | Delivery Type | Idempotency Requirements | Retry Policy | Ordering Requirements |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `EnclosureTreesPlanted` | New planting op synced | `EnclosureAggregate` | Analytics, Inventory | Outbox / At-least-once | Event ID deduplication | Exponential backoff | Strict chronological |
| `EnclosureTreesRemoved` | Removal op synced | `EnclosureAggregate` | Analytics | Outbox / At-least-once | Event ID deduplication | Exponential backoff | Strict chronological |
| `SeasonClosed` | Season status changed to CLOSED | `SeasonAggregate` | Operations, Finance | Outbox / At-least-once | State transition guard | 3 retries -> DLQ | Independent |
| `HierarchyNodeMoved` | Node re-parented | `HierarchyAggregate` | Enclosure, Analytics | Outbox / At-least-once | Revision tracking | Infinite until success | Strict hierarchical |
| `PropagationStarted` | Rollup job initiated | `HierarchyAggregate` | Operations | Broker direct | Execution lock | None (re-triggered) | None |
| `PropagationCompleted` | Rollup job finished | `HierarchyAggregate` | Operations | Broker direct | Execution lock | None | None |
| `PropagationFailed` | Rollup job errored | `HierarchyAggregate` | Notifications | Broker direct | Execution lock | 3 retries -> DLQ | None |
| `OfflineSyncMerged` | Mobile payload resolved | `EnclosureAggregate` | Audit | Outbox / At-least-once | Sync UUID deduplication | None | Strict chronological |

**Event Naming Convention:**
*   **Past-Tense Naming:** Events represent things that have *already happened*. (e.g., `TreesPlanted`, not `PlantTrees`).
*   **Immutable Payloads:** Event payloads represent a point in time and must NEVER change once emitted.
*   **Event Versioning:** Payload schemas must be versioned (e.g., `v1`, `v2`). Consumers must be capable of routing obsolete event structures.

> [!CAUTION]
> **Explicitly Prohibited:**  
> *   **Command-Style Event Naming:** Naming events `UpdateTrees` implies a command, not a fact.
> *   **Mutable Events:** Events must contain all context needed; they should not rely on later queries that might return different state.
> *   **Hidden Side-Effect Events:** Triggering DB hooks instead of explicit Domain Events.

---

## 22. Aggregate Snapshot Strategy

**Snapshot Creation Rules:**
For aggregates with long lifespans and massive operational logs (e.g., `EnclosureAggregate`), loading thousands of domain events to rebuild state becomes a performance bottleneck.
*   **Aggregate Compaction:** A snapshot is generated every N events (e.g., every 100 offline sync operations).
*   **Historical Archival Boundaries:** Events prior to a compacted snapshot are moved to cold storage (e.g., S3 or Glacier).
*   **Replay Limits:** Systems MUST NOT replay more than the maximum snapshot threshold (e.g., 100 events) during a single request. 

**Replay Optimization & Dangers:**
Unlimited replay is strictly dangerous. Replaying a 10-year history of planting and harvesting logs for a single enclosure inside a synchronous request will cause memory exhaustion and connection timeouts.
*   **Enclosure History Protection:** Ensure enclosures rely on point-in-time snapshots for active metrics.
*   **Mobile Replay Constraints:** Mobile devices pull snapshots, not raw event logs.
*   **Snapshot Invalidation:** If a critical historical correction occurs, the snapshot is explicitly invalidated, and a background worker rebuilds it.

---

## 23. Aggregate Loading Strategy

Aggregates must be lightweight and fast to load.

**Loading Rules:**
*   **Lazy Loading:** Internal collections (e.g., `OperationLog`) must NOT be eagerly loaded unless explicitly required for an invariant check.
*   **Projection-First Querying:** UI lists and dashboards MUST query Read Models, never the Aggregate repositories.
*   **Pagination Requirements:** Any internal collection loaded for validation must be paginated or bounded by a hard limit.
*   **Recursive Loading Protections:** A `HierarchyAggregate` must rely on materialized paths (e.g., `ltree`) or closure tables, avoiding recursive `parent.parent.parent` queries.

**Explicitly Banned:**
*   **Eagerly loading entire hierarchy trees** into memory.
*   **Loading 10-year histories** into an `EnclosureAggregate` instance.
*   **Recursive nested aggregate loading:** Loading `Farm` -> `Season` -> `Enclosure` in a single ORM call.

**Maximum Safe Collection Sizes:**
Collections within an aggregate must be strictly bounded (e.g., maximum 50 active tasks per sync payload).

---

## 24. Distributed Locking & Concurrency Rules

In a distributed environment with asynchronous workers (e.g., Celery), explicit locking is required for specific contention scenarios.

**Distributed Lock Scenarios:**
*   **Propagation Execution Locks:** Calculating hierarchy rollups requires a distributed lock (e.g., Redis `SETNX`) to prevent overlapping workers from deadlocking on the same tree branch.
*   **Season Closing Locks:** Only one process can execute the transition to `CLOSED`.
*   **Sync Conflict Locks:** Concurrent mobile syncs for the same enclosure UUID require lock acquisition.

**Concurrency Strategy:**
*   **Deadlock Prevention:** Locks must always be acquired in a deterministic order (e.g., alphabetical by aggregate ID).
*   **Lock Timeout Strategy:** Every distributed lock MUST have an absolute TTL (Time-To-Live). Infinite locks are banned.
*   **Retry Backoff:** Failed lock acquisitions trigger an exponential backoff retry.
*   **Optimistic Locking Interaction:** Distributed locks protect async workers; optimistic locking (`version` checks) protects synchronous HTTP requests.

> [!WARNING]
> Distributed locks are strictly FORBIDDEN for standard CRUD operations. They are reserved exclusively for long-running async background tasks and critical state transitions.

---

## 25. Aggregate Decomposition Strategy

As the platform scales, aggregates that grow too large (God Aggregates) must be decomposed.

**Future Scalability Extraction Strategy:**
*   **Splitting Analytics:** `EnclosureAggregate` currently tracks tree counts. In the future, complex yield projections must be extracted to a separate `YieldAggregate`.
*   **Extracting Media Ownership:** Geospatial polygons and media attachments should be migrated to a dedicated `AssetMediaAggregate` linked by `enclosure_id`.
*   **Operational Boundaries:** Separating `TaskAggregate` from `EnclosureAggregate` ensures operations can scale independently of physical asset data.

**Preventing God Aggregate Evolution:**
*   **Safe Decomposition Indicators:** If an aggregate routinely exceeds 100KB in JSON serialized size, or if locking contention affects >5% of transactions, it must be decomposed.

---

## 26. Domain Event Naming Conventions

Strict naming standards ensure predictability across the event-driven architecture.

**Standards:**
*   **Event Naming:** `{Aggregate}{Noun}{PastTenseVerb}`
*   **Command Naming:** `{Verb}{Aggregate}{Noun}`
*   **Queue Naming:** `{domain}.{aggregate}.{event}`
*   **Retry Event Naming:** `{EventName}.retry`
*   **Failure Event Naming:** `{EventName}.failed`

**Examples:**
*   ✅ **GOOD:** `TreesPlanted`, `SeasonClosed`, `PropagationFailed`
*   ❌ **BAD:** `UpdateTrees`, `ProcessSeason`, `HandlePropagation`

Domain language must always reflect an immutable historical fact (past tense).

---

## 27. Aggregate Observability Rules

Distributed ERPs require absolute transparency into cross-aggregate workflows.

**Observability Requirements:**
*   **Correlation IDs:** Every synchronous HTTP request generates a `correlation_id`. This ID MUST be passed to all outbox events, background jobs, and logs.
*   **Event Tracing:** Event brokers must log the delivery, processing time, and outcome of every domain event.
*   **Propagation Tracing:** Hierarchy rollups must log their depth and execution time to detect N+1 anomalies.
*   **Audit Correlation:** All aggregate mutations must be auditable back to the exact `correlation_id` and originating user/device.

---

## 28. AI Agent Enforcement Expansion

> [!CAUTION]
> **ENHANCED AI-AGENT GOVERNANCE**  
> AI implementation agents are strictly bound by the following expanded enterprise rules:

*   **Forbidden Repository Shortcuts:** Agents MUST NOT inject ORM queries directly into Application Services. Use Repository interfaces.
*   **Forbidden Direct ORM Filtering:** `Enclosure.objects.filter(...)` inside a domain method is banned. The aggregate root must already contain the loaded state.
*   **Mandatory Invariant Assertions:** Every mutating method written by an AI MUST include explicit `if` checks enforcing business invariants before modifying state.
*   **Mandatory Transaction Scoping:** AI agents MUST wrap aggregate save operations in explicit transaction blocks (e.g., `with transaction.atomic():`).
*   **Mandatory Event Emission Validation:** Any AI-generated code that mutates state MUST dispatch a corresponding Domain Event to the Outbox.

**Automatic Rejection Conditions:**
Any AI-generated pull request or code block containing raw ORM `.update()`, missing transaction boundaries, or cross-aggregate synchronous writes MUST be automatically rejected.
