import sys

content = """
## 31. Farm Aggregate Boundaries

**Aggregate Roots:**
The Farm Domain is strictly divided into four Aggregate Roots. No transaction may modify entities across two Aggregate Roots simultaneously without using eventual consistency (Domain Events).

1. **Farm Aggregate**
   - **Root Entity:** `Farm`
   - **Child Entities:** `HierarchyConfiguration`, `Equipment`
   - **Invariants:** A Farm must have exactly one active `HierarchyConfiguration`. Deactivating a Farm disables all operational access.
   - **Consistency:** Strong. Changes to config depth immediately block incompatible node creation.

2. **Season Aggregate**
   - **Root Entity:** `Season`
   - **Child Entities:** `SeasonSnapshot`
   - **Invariants:** Only one Season can be OPEN per Farm. Start date must precede end date.
   - **Consistency:** Strong. Closing a season synchronously computes the SeasonSnapshot (if < 500 enclosures) or transitions state to CLOSING until async job finishes.

3. **Hierarchy Aggregate**
   - **Root Entity:** `HierarchyNode`
   - **Child Entities:** `HierarchyNode` (self-referential)
   - **Invariants:** Tree depth cannot exceed `HierarchyConfiguration.depth`. Cycles are forbidden.
   - **Consistency:** Strong. Deactivating a node hides its descendants in the same transaction.

4. **Enclosure Aggregate**
   - **Root Entity:** `Enclosure`
   - **Child Entities:** None directly (history is aggregated via views).
   - **Invariants:** Must belong to a valid leaf node if depth > 0. Must have one `CropType`.
   - **Consistency:** Strong. `tree_count` mutations are atomic.

**Aggregate Ownership:**
External domains (Harvest, Operations) hold references (IDs) to Farm Aggregates but cannot mutate them. To mutate a Farm Aggregate, external domains must emit a Domain Event that the Farm Domain consumes.

---

## 32. Farm Domain Services

Business logic is encapsulated in stateless, pure Domain Services located in `services.py`.

### `SeasonClosingService`
- **Responsibilities:** Validates season close conditions, computes final completion percentages, freezes yield data into `SeasonSnapshot`, archives pending operations.
- **Inputs:** `season_id`, `tenant_id`, `user_id`
- **Outputs:** `SeasonSnapshot` object
- **Transaction Behavior:** `transaction.atomic()`. Fails entirely if snapshot generation fails.
- **Events Published:** `Farm.Season.Closed`

### `OperationPropagationService`
- **Responsibilities:** Expands a node-targeted operation into individual enclosure operations.
- **Inputs:** `operation_id`, `target_node_id`, `tenant_id`
- **Outputs:** Count of propagated records.
- **Transaction Behavior:** Batch inserts inside `transaction.atomic()`. Dispatches to Celery if enclosures > 200.
- **Events Published:** None directly (Operations Domain owns the operation events).

### `HierarchyMigrationService`
- **Responsibilities:** Safely processes structural changes (e.g., depth changes or moving nodes).
- **Inputs:** `farm_id`, `new_config`, `node_mapping`
- **Outputs:** Updated `HierarchyConfiguration`.
- **Transaction Behavior:** Atomic. Requires Super Admin approval.
- **Events Published:** `Farm.HierarchyConfig.Changed`

### `EnclosureLifecycleService`
- **Responsibilities:** Handles Enclosure creation, deactivation, and crop changes.
- **Inputs:** `enclosure_data`, `tenant_id`, `user_id`
- **Outputs:** `Enclosure` instance.
- **Transaction Behavior:** Atomic. Checks season locks before mutation.
- **Events Published:** `Farm.Enclosure.Created`, `Farm.Enclosure.Deactivated`, `Farm.Enclosure.CropChanged`

### `CompletionCalculationService`
- **Responsibilities:** Computes realtime completion % for an enclosure or node.
- **Inputs:** `entity_id`, `season_id`
- **Outputs:** `{ "planned": int, "completed": int, "percentage": float }`
- **Transaction Behavior:** Read-only. No transaction.
- **Events Published:** None.

---

## 33. Farm Read Models (CQRS Strategy)

ATLS separates the write model (Aggregates) from the read model (Views) to handle complex analytics without locking tables.

33.1. **CQRS Strategy:** The write database handles pure transactions. Denormalized Read Models are built via database Views (for real-time) or async Celery tasks (for complex aggregations).

33.2. **`FarmHierarchyReadModel`**
- **Purpose:** Fast delivery of the full tree structure for mobile navigation.
- **Mechanism:** Materialized View updated asynchronously via Celery on `Farm.Node.*` events.
- **Invalidation:** Redis cache key `farm:{id}:tree` cleared on structural changes.

33.3. **`EnclosureDashboardReadModel`**
- **Purpose:** Serves the main operational table (Enclosures + Current Status + Completion %).
- **Mechanism:** Denormalized table `enclosure_dashboard_read` updated via Django signals on Operation/Harvest events.
- **Invalidation:** Eventual consistency (target: < 2 seconds delay).

33.4. **`EnclosureHistoryReadModel`**
- **Purpose:** Chronological timeline of everything that happened to an enclosure.
- **Mechanism:** Database View performing `UNION ALL` across Operations, Reports, and Harvests, indexed by `(enclosure_id, date)`.
- **Invalidation:** Real-time via View.

33.5. **`SeasonAnalyticsReadModel`**
- **Purpose:** Aggregate statistics for the current season.
- **Mechanism:** Computed nightly or on-demand via Redis. Frozen into `SeasonSnapshot` on close.

---

## 34. Operation Propagation Strategy

Current propagation is enhanced with a distributed, scalable strategy to prevent write amplification.

34.1. **Thresholds:**
- **< 50 enclosures:** Synchronous Eager Propagation. Immediate response.
- **50 – 500 enclosures:** Asynchronous Eager Propagation (Celery). UI shows "Propagation in progress".
- **> 500 enclosures:** Virtual Propagation.

34.2. **Virtual Propagation (Large Scale):**
- Does not create individual database rows immediately.
- Creates a single `VirtualOperation` record linked to the target node.
- When an enclosure is fetched, the API dynamically merges virtual operations with explicit enclosure operations.
- Explicit actions on a virtual operation for a specific enclosure (e.g., marking it complete) "materializes" that single record into the DB as an explicit override.

34.3. **Idempotency & Duplicate Prevention:**
- Propagation jobs are keyed by `hash(operation_id, target_node_id)`. Redis prevents duplicate identical propagation tasks from running simultaneously.

34.4. **Failure Recovery:**
- Celery tasks use `acks_late=True` and transaction boundaries. If a propagation task fails mid-batch, it retries and uses `get_or_create` to prevent duplicate row creation.

---

## 35. Offline Synchronization & Conflict Resolution

ATLS is a mobile-first field system. Network loss is expected.

35.1. **Optimistic Locking:** Every Enclosure and Operation record includes a `_version` field. Updates must include the version. If the server version > client version, an `HTTP 409 Conflict` is returned.

35.2. **Queueing Mobile Writes:**
- Write operations performed offline are stored in IndexedDB (frontend) in a Sync Queue.
- The queue stores the exact API payload and timestamp.

35.3. **Sync Strategy:**
- Upon reconnection, the frontend dispatches the Sync Queue sequentially.
- Transient errors (500, network) trigger exponential backoff retries.
- Persistent errors (400, 409) move the item to a "Conflict UI" state.

35.4. **Conflict Resolution Rules:**
- **Last-Write-Wins (LWW):** Applied to simple fields (notes, status) if `_version` matches.
- **Additive Merge:** Applied to collections (adding photos, logging harvest weight). Offline additions are always accepted.
- **Hard Conflict:** If a field worker tries to update an operation that a manager has locked or deleted, the worker receives a conflict notification. The local change is discarded.

---

## 36. Audit Severity & Security Escalation

Every domain event is logged by the Audit Domain with an explicit severity level.

| Severity | Triggers | Escalation & Alerts |
|---|---|---|
| **LOW** | Enclosure created, media uploaded, operation marked complete. | Stored in audit log only. No alerts. |
| **MEDIUM** | Crop type changed, tree count adjusted, season opened. | Highlighted in Farm Manager's daily digest. |
| **HIGH** | Season closed without 100% completion, Hierarchy node deleted. | In-app notification to Tenant Admin. Requires explicit confirmation reason. |
| **CRITICAL** | Hierarchy depth changed, Farm deactivated, mass-deletion. | SMS/Email alert to Super Admin. Blocked until Super Admin enters OTP / confirmation code. |

---

## 37. Domain Ownership Matrix

To prevent circular dependencies, ATLS strictly enforces the Source of Truth.

| Concept / Data | Authoritative Owner (Write) | Consumers (Read-Only) |
|---|---|---|
| Farm Hierarchy & Enclosures | **Farm Domain** | All Domains |
| Season State | **Farm Domain** | All Domains |
| Operation Records | **Operations Domain** | Farm (History), Analytics |
| Completion % | **Operations Domain** | Farm (Dashboard), Analytics |
| Daily Reports | **Reporting Domain** | Farm (History), HR (Payroll) |
| Harvest Yield | **Harvest Domain** | Farm (History), Analytics, Inventory |
| Inventory Consumption | **Inventory Domain** | Operations, Farm, Analytics |
| Season Snapshot | **Farm Domain** (Assembler) | Analytics |
| Worker Productivity | **Analytics Domain** | HR |

**Rule:** A domain may query another domain's Read Model, but may never write to another domain's database tables.

---

## 38. Farm Domain Performance Rules

38.1. **Query Complexity Limits:** No query may exceed 3 table joins (`select_related`). Complex queries must be routed to a denormalized Read Model.

38.2. **Maximum Recursion Depth:** Hierarchy tree fetching uses PostgreSQL CTEs (Common Table Expressions) limited strictly to the configured `HierarchyConfiguration.depth` (max 4). Infinite recursion is impossible by design.

38.3. **Mobile Payload Size:** The `/api/v1/farm/{id}/sync` endpoint must compress its payload. The maximum allowed payload size for the offline hierarchy initialization is 5MB. Above 5MB, enclosures must be lazy-loaded per sector.

38.4. **Pagination Strictness:** Endpoints returning Enclosures or Operations MUST enforce pagination. `limit` parameter is capped at 100. Bypassing pagination (`limit=0`) is forbidden.

38.5. **Analytics Caching:** Analytics endpoint queries spanning > 10,000 rows must hit a Redis cache (TTL: 1 hour) or a pre-computed projection. They must never execute raw aggregation against the transactional tables during business hours.

---

## 39. Farm Domain State Machines

Explicit state machines govern critical entities to prevent invalid transitions.

39.1. **Season State Machine**
- `PENDING` → `OPEN` (Trigger: Manager Action)
- `OPEN` → `CLOSING_ASYNC` (Trigger: Manager Action, if > 500 enclosures)
- `OPEN` / `CLOSING_ASYNC` → `CLOSED` (Trigger: Snapshot Complete)
- `CLOSED` → `ARCHIVED` (Trigger: Admin Action)
- *Forbidden:* `CLOSED` → `OPEN`.

39.2. **Enclosure Operational Status (Computed)**
- `DORMANT` (No season)
- `ACTIVE` (Season open, operations exist)
- `COMPLETED` (100% planned ops done)
- `OVERDUE` (Current date > planned op date & status != completed)

39.3. **Propagation Job State Machine**
- `QUEUED` → `PROCESSING` → `COMPLETED`
- `PROCESSING` → `FAILED_RETRY` → `PROCESSING`
- `FAILED_RETRY` → `DEAD_LETTER` (after 3 retries, requires manual intervention)

---

## 40. AI Implementation Safety Guards

> **CRITICAL DIRECTIVES FOR AI AGENTS WORKING IN THE FARM DOMAIN**

40.1. **Forbidden Direct DB Writes:** Never use `Enclosure.objects.filter(...).update(...)` to bypass the `EnclosureLifecycleService`. All writes must route through the Domain Services.

40.2. **Forbidden Cross-Aggregate Mutations:** Never write a function that saves a `Farm` and a `Season` in the same direct ORM block without using the appropriate services and emitting events.

40.3. **Mandatory Tenant Filtering:** EVERY single ORM query written by the AI MUST include a `tenant_id` check.
- ❌ `Enclosure.objects.get(code=code)`
- ✅ `Enclosure.objects.get(code=code, farm__tenant_id=tenant_id)`

40.4. **Forbidden N+1 Loops:** Never iterate over a queryset of Enclosures and execute a related query inside the loop.
- ❌ `for enc in enclosures: ops = enc.operations.all()`
- ✅ `enclosures.prefetch_related('operations')`

40.5. **Event Emission Mandate:** If an AI implements a feature that changes the state of a Farm, Season, Node, or Enclosure, it MUST include the corresponding `EventBus.publish(...)` call in the service layer.

40.6. **No "Magic" Deletes:** Never implement a `.delete()` method call. Always use `is_active = False` (soft delete) and append a timestamp to the unique code if necessary to free up the unique constraint.

---
"""

file_path = "e:\my project\docs_v2\\03_DOMAINS\FARM_DOMAIN.md"
with open(file_path, "r", encoding="utf-8") as f:
    original_content = f.read()

# Remove the final blockquote
footer_marker = "> **This document is the law for the Farm Domain. Any implementation that contradicts these rules constitutes a domain violation and must be corrected before merge.**"
if footer_marker in original_content:
    original_content = original_content.replace(footer_marker, "")

new_content = original_content.strip() + "\n\n" + content.strip() + "\n\n> **This document is the law for the Farm Domain. Any implementation that contradicts these rules constitutes a domain violation and must be corrected before merge.**\n"

with open(file_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print("Successfully appended 10 new sections to FARM_DOMAIN.md")
