# ATLS Platform: Farm Domain Services Architecture

> **Confidential & Proprietary**  
> **Target Audience:** Senior Engineering Team, AI Implementation Agents, Platform Architects  
> **Domain:** Agricultural ERP & Operations Platform  

---

## 1. Purpose Of Domain Services

Aggregates enforce transactional consistency around a specific boundary, but enterprise ERP operations frequently require coordinating changes across multiple aggregates. 

**Why Aggregates Alone Are Insufficient:**
Placing cross-aggregate coordination logic inside an aggregate leads to "God Aggregates" and massive transactional contention. Aggregates cannot and must not know about other aggregates' repositories.

**The Role of Domain Services:**
Domain Services represent the execution brain of the domain. They orchestrate complex business workflows, validate multi-aggregate states, and coordinate eventual consistency WITHOUT violating aggregate isolation. They exist to coordinate—not to own. They must never become "God Services" that bypass domain encapsulation.

---

## 2. Domain Service Philosophy

*   **Orchestration vs Ownership:** Services orchestrate workflows; Aggregates own the data and state transitions. Services do not mutate state directly; they call methods on Aggregates.
*   **Stateless Philosophy:** Domain services hold no intrinsic state. They are purely functional, receiving inputs and acting upon domain objects.
*   **Deterministic Execution:** Given the same inputs and aggregate states, a service must produce the exact same outcome.
*   **Idempotent Behavior:** Services must handle identical, repeated requests without corrupting the domain (crucial for mobile retries).
*   **Event-Driven Coordination:** Services prefer emitting Domain Events via the Outbox over executing synchronous cross-aggregate writes.

> [!CAUTION]
> **Explicitly Prohibited Behaviors:**
> *   **Hidden Writes:** Saving data via ORM queries instead of explicitly calling Repository methods.
> *   **Direct ORM Access:** Interacting with database models directly. Services use Repositories.
> *   **Logic Leakage:** Putting service orchestration logic into API controllers, views, or message consumers.

---

## 3. Service Classification Model

Domain Services in ATLS are strictly categorized by their behavioral archetype:

*   **Coordination Services:** Orchestrate complex workflows involving multiple steps and eventual consistency (e.g., closing a season).
*   **Validation Services:** Ensure business rules that require querying multiple aggregates (e.g., hierarchy structural validation).
*   **Propagation Services:** Manage the cascading effects of an operation up or down the hierarchy (e.g., rolling up task completion).
*   **Analytics Services:** Handle asynchronous computation and projection updates (eventually consistent read models).
*   **Synchronization Services:** Manage the resolution of offline mobile payloads, detecting conflicts and applying additive merges.
*   **Security Services:** Enforce domain-level authorization and escalate suspicious activities.

---

## 4. Core Domain Service Catalog

| Service Name | Purpose | Trigger Source | Owned Workflow | Transaction Scope | Emits Events | Retry Strategy | Failure Severity |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `OperationPropagationService` | Rolls up operational completion | Domain Event | Async Completion | Single Parent per Tx | `PropagationCompleted` | Exponential | High |
| `SeasonClosingService` | Locks financial/operational periods | Admin API | Sync State / Async Freeze | Single Season per Tx | `SeasonClosed` | Linear (3x) | Critical |
| `HierarchyValidationService` | Prevents cyclic trees / depth | API / Import | Sync Validation | Read-Only | None | None | Critical |
| `CompletionCalculationService` | Recalculates enclosure metrics | Domain Event | Async Recalculation | Single Enclosure per Tx | `MetricsUpdated` | Exponential | Medium |
| `OfflineMergeService` | Resolves mobile payload intents | Mobile API | Sync Merge | Single Enclosure per Tx | `OfflineSyncMerged` | None | High |
| `EnclosureMetricsService` | Updates eventual read models | Domain Event | Async Projection | Single Projection per Tx | None | Exponential | Medium |
| `AuditEscalationService` | Flags critical deviations | Domain Event | Async Escalation | Read-Only | `AuditEscalated` | Exponential | Critical |
| `SnapshotCompactionService` | Archives long event histories | Cron / Threshold | Async Compaction | Single Aggregate per Tx | `SnapshotCreated` | Exponential | Low |

---

## 5. Service Transaction Rules

**Transaction Boundaries & Ownership:**
A Domain Service must explicitly control the database transaction boundary. 
*   **Sync Execution:** Maximum scope is ONE aggregate write per transaction.
*   **Async Execution (Eventual Consistency):** If workflow requires updating three aggregates, the service updates the first, emits an event, and background handlers update the next two in independent transactions.

**Rules:**
*   **Forbidden Nested Transactions:** Opening a transaction within an already open transaction boundary is banned.
*   **Rollback Strategy:** If a service encounters an invariant violation, it raises a Domain Exception, instantly rolling back the current transaction.
*   **No Distributed Transactions:** Two-Phase Commits (2PC) are forbidden. Use Sagas or Eventual Consistency.

---

## 6. Event Emission Rules

**Outbox Requirements:**
When a Domain Service mutates an aggregate that other domains care about, it MUST emit a Domain Event. This event is saved to a Transactional Outbox table *inside* the same transaction as the aggregate mutation.

**Guarantees:**
*   **Ordering Guarantees:** Outbox relays guarantee at-least-once, strictly ordered delivery per aggregate instance.
*   **Deduplication Strategy:** Every event requires a unique `event_id`. Consumers must deduplicate based on this ID.
*   **Retry Policies:** If an event consumer fails, it backs off exponentially. Poison events go to a Dead Letter Queue (DLQ).
*   **Event Correlation:** Events emitted as a result of processing another event MUST carry forward the original `correlation_id`.

---

## 7. OperationPropagationService

> [!IMPORTANT]  
> **Critical Operational Engine:** This service manages the dynamic flow of data through the farm hierarchy.

*   **Propagation Orchestration:** Coordinates rolling up quantities (e.g., harvested kilos) from Plots to Sectors to Regions.
*   **Hierarchy Traversal:** Validates the path to the root before applying calculations.
*   **Async Worker Coordination:** Enqueues individual propagation steps to prevent synchronous timeouts.
*   **Propagation Thresholds & Recursion Protection:** Limits the depth of propagation to the tenant's max hierarchy depth to prevent infinite loops.
*   **Idempotency Locking:** Uses distributed locks (e.g., Redis `SETNX`) per hierarchy node to prevent race conditions when two siblings propagate simultaneously.

**Modes:**
*   **Eager Propagation:** Used only for critical financial locks.
*   **Async Propagation:** Standard mode; uses message broker.
*   **Virtual Propagation:** Calculates rollups on-the-fly for Read Models without mutating the source of truth.

---

## 8. SeasonClosingService

*   **Season Locking Flow:** Validates all pending offline operations have settled. Sets status to `CLOSING`.
*   **Async Closure Orchestration:** Emits events to freeze Enclosure metrics, lock timesheets, and prevent new task creation.
*   **Analytics Freezing:** Generates a hard snapshot of the read models for the season.
*   **Offline Sync Grace Periods:** Allows a configured window (e.g., 48 hours) for mobile devices to upload cached tasks before hard `CLOSED` state is applied.
*   **Rollback Prevention:** Once a season is `CLOSED`, the service prevents any reversion without a multi-signature executive override.

---

## 9. HierarchyValidationService

*   **Cycle Detection:** Executes topological sorts to guarantee the farm tree remains a Directed Acyclic Graph (DAG).
*   **Hierarchy Depth Validation:** Rejects any `MoveNode` command that would exceed the maximum depth limit (preventing recursion crashes).
*   **Structural Integrity Checks:** Validates that standard operational rules apply (e.g., an Enclosure cannot be the parent of a Region).
*   **Orphan Prevention:** Prevents the deletion of a parent node unless all children are explicitly reassigned or archived.

**Why Corruption is Catastrophic:**
A single cyclic reference in an ERP hierarchy will cause infinite loops in reporting engines, bringing down the entire analytics infrastructure.

---

## 10. CompletionCalculationService

*   **Weighted Completion:** Calculates task completion percentage based on the area of the enclosure vs total area.
*   **Quantity Completion:** Calculates progress based on expected vs actual yields.
*   **Tree-Based Completion:** Assesses progress based on the physical tree count involved in the operation.
*   **Manual Override Handling:** If a supervisor manually sets completion to 100%, the service halts formulaic recalculations.
*   **Recalculation Triggers:** Triggered asynchronously via `TaskUpdated` or `EnclosureAreaChanged` events. This is an eventually consistent process.

---

## 11. OfflineMergeService

*   **Mobile Sync Merge Logic:** Reconciles offline mobile intent payloads against the server's master state.
*   **Additive Merge Strategy:** Instead of overriding absolute values, applies additive deltas (e.g., `+50 trees planted`, not `total_trees = 500`).
*   **Optimistic Locking Handling:** Detects version mismatches. If non-additive, rejects the payload.
*   **Conflict Resolution:** Applies Last-Write-Wins (LWW) *only* for scalar settings (e.g., changing a task note). 
*   **Replay Handling & Duplicate Detection:** Validates the client-generated `sync_id`. If already processed, acknowledges success without mutating state (Idempotency).

---

## 12. EnclosureMetricsService

*   **Aggregate Metrics Calculation:** Computes complex historical data points (e.g., yield per hectare over 5 years).
*   **Cached Metrics & Read Model Sync:** Persists calculation results into CQRS Read Models for sub-millisecond API response times.
*   **Async Recalculation:** Re-runs calculations in the background when historical anomalies are corrected.

**Why Analytics Must Remain Eventually Consistent:**
Calculating 5 years of agronomic data synchronously during an Enclosure save will cause connection pool exhaustion. Analytics are decoupled from the transactional flow.

---

## 13. AuditEscalationService

*   **Severity Classification:** Determines if a domain event is Routine, Warning, or Critical.
*   **Suspicious Activity Detection:** Flags anomalies (e.g., deleting 10,000 trees offline and syncing at 3 AM).
*   **Escalation Workflows:** Dispatches alerts to Farm Managers or System Admins based on tenant policy.
*   **Immutable Audit Chains:** Secures critical events into write-only audit logs.

**CRITICAL Event Examples:**
*   Reopening a closed financial Season.
*   Hard-deleting a core Enclosure asset.
*   Cross-tenant data access attempts.

---

## 14. SnapshotCompactionService

*   **Snapshot Generation:** Reads the event stream for an aggregate and compiles it into a point-in-time state.
*   **Replay Compaction:** Truncates the active event stream, preventing memory exhaustion when loading old aggregates.
*   **Archival Coordination:** Moves compacted events to cold storage.
*   **Retention Policies:** Configures tenant-specific rules for how long raw transactional events remain in hot storage.

---

## 15. Service Failure Recovery

Distributed ERPs expect failure. Services must be resilient.
*   **Retry Orchestration:** Transient errors (network blips, DB locks) trigger exponential backoffs.
*   **Dead-Letter Queues (DLQ):** Messages that fail after max retries are sent to a DLQ for manual engineering inspection.
*   **Poison Message Handling:** If an event payload is structurally malformed, it bypasses retries and goes straight to DLQ.
*   **Compensation Workflows:** Sagas that encounter terminal errors must execute compensating transactions (e.g., reversing the tree count if the propagation fails).

---

## 16. Service Observability Rules

*   **Correlation IDs:** Every workflow MUST carry a `correlation_id` from the initial API request down through every async message and service call.
*   **Tracing:** Distributed tracing spans must encapsulate service method execution.
*   **Propagation Tracking:** Deep hierarchy rollups must log their path to detect infinite loops or processing bottlenecks.
*   **Distributed Workflow Visibility:** System administrators must be able to view the status of long-running workflows (e.g., Season Closure) via Audit logs.

---

## 17. Performance Protection Rules

*   **Execution Limits:** No service execution should block the main thread for more than 500ms.
*   **Propagation Caps:** Hard limits on how many child nodes can be processed synchronously before yielding to the message broker.
*   **Timeout Rules:** All distributed locks and HTTP calls must have absolute timeouts.
*   **Memory Protection:** Loading entire tables into a service is banned. Always use batching and pagination.

> [!WARNING]
> **Unbounded Recursion is BANNED.** Any service traversing a hierarchy MUST implement a depth counter and raise a `RecursionLimitExceeded` exception if it surpasses safety thresholds.

---

## 18. Multi-Tenant Isolation Rules

*   **Tenant-Safe Orchestration:** A service MUST NEVER orchestrate workflows involving aggregates from different tenants.
*   **Tenant-Scoped Events:** Every domain event placed into the outbox must include the `tenant_id`.
*   **Tenant-Safe Retries:** Background workers pulling from queues must implicitly filter or set their execution context to the `tenant_id` of the message payload.

---

## 19. Domain Service Anti-Patterns

If you implement any of the following, the architecture has failed.

*   **God Service:** A single `FarmManagerService` that knows how to create tasks, propagate yields, calculate completion, and send emails.
*   **Fat Application Service:** Putting all the business invariant logic into the Application Service instead of the Aggregate Root.
*   **Direct ORM Orchestration:** `Enclosure.objects.filter(tenant=x).update(status='ACTIVE')`. Bypasses domain logic.
*   **Hidden Event Emission:** Emitting events directly to RabbitMQ inside a service bypassing the Transactional Outbox (risks ghost events if the DB rolls back).
*   **Recursive Sync Propagation:** Calling the propagation service synchronously in a `while` loop.
*   **Cross-Tenant Orchestration:** Attempting to run global analytics across tenant boundaries inside a domain service.
*   **Blocking Async Workflows:** Waiting for a Celery task to finish inside a synchronous web request.

---

## 20. AI Agent Service Enforcement Rules

> [!CAUTION]
> **AI-AGENT ENGINEERING DIRECTIVES**  
> All autonomous agents, copilots, and AI engineering tools generating domain services are bound by the following unalterable laws:

1.  **Forbidden Implementation Shortcuts:** Agents MUST NOT inject ORM queries directly into Domain Services. Repositories ONLY.
2.  **Mandatory Transaction Scoping:** If a service method modifies an aggregate, the agent MUST wrap the repository call and the outbox event creation in a single `transaction.atomic()` block.
3.  **Mandatory Invariant Checks:** Agents MUST ensure the service checks domain invariants before attempting to orchestrate state changes.
4.  **Mandatory Outbox Emission:** Agents MUST NEVER use direct message broker calls (e.g., `celery.send_task`) inside a synchronous service transaction.
5.  **Forbidden Synchronous Cross-Aggregate Writes:** Agents MUST NOT write code that calls `.save()` on two different aggregates in the same method.

**Automatic Rejection Conditions:**
Any AI-generated service containing cross-aggregate synchronous saves, missing transaction scopes, or direct ORM `.filter()` calls MUST be automatically rejected.

---

## 21. Final Engineering Principles

**Orchestration Integrity**  
A Domain Service must coordinate failure as gracefully as it coordinates success. Always assume the next step in the workflow will fail.

**Resilience Over Convenience**  
It is easier to write a 300-line synchronous service. It is harder to write a 3-step event-driven Saga. Distributed ERPs demand the harder path to guarantee resilience.

**Deterministic Workflows**  
If a service is given the same state, it must produce the same result. Avoid implicit dependencies on system clocks or global variables.

**Auditability Over Speed**  
Every action orchestrated by a service must leave a trace. When an enclosure reports 10,000 dead trees, the service logs must prove exactly which mobile device synced the intent, and which worker executed the propagation.
