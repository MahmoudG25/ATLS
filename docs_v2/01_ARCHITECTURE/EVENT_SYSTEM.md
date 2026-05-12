# ATLS Platform: Event-Driven Architecture System

## 1. Event-Driven Philosophy
The ATLS platform is fundamentally designed as an event-driven system. State mutations are treated as a series of indisputable, immutable historical facts. By making events first-class citizens, the platform decouples bounded contexts, enabling independent scaling, robust offline synchronization, and comprehensive auditability—essential traits for a high-availability agricultural ERP.

## 2. Why Event-Driven Architecture
Agricultural operations are highly distributed and often disconnected. A traditional synchronous monolith creates fragile temporal coupling. We adopt an Event-Driven Architecture (EDA) to achieve:
- **Resilience:** If the Reporting Domain is down, the Operations Domain can still record a harvest.
- **Traceability:** Every change is explicitly recorded as a domain event, yielding an inherent audit trail.
- **Asynchronous Workflows:** Heavy analytics, notifications, and ledger updates happen outside the critical user-facing HTTP request lifecycle.

## 3. Domain Event Definition
A **Domain Event** represents something meaningful that happened *within* a specific Bounded Context. 
- It captures a business fact (e.g., `HarvestReportSubmitted`).
- It is raised by an Aggregate Root.
- It is consumed *only* by handlers within the exact same Bounded Context (e.g., for updating internal read models or triggering internal side-effects).
- **Rule:** Domain Events MUST remain inside the originating bounded context.

## 4. Integration Event Definition
An **Integration Event** is a simplified, public contract broadcasted to the rest of the system when a Bounded Context completes a significant transaction.
- It is designed for consumption by *other* Bounded Contexts.
- It abstracts away internal domain complexities.
- **Rule:** Integration Events MUST be simplified external contracts, devoid of internal Aggregate implementation details.

## 5. Event Naming Convention
Events are historical facts and MUST be named using past-tense verbs.
- **Format:** `[Subject][Action][Fact]`
- **Good:** `CropPlanted`, `HarvestReportSubmitted`, `InventoryDeducted`
- **Bad:** `UpdateCrop`, `CreateHarvestReport` (These are Commands, not Events).

## 6. Event Ownership Rules
An event is wholly owned by the Bounded Context that generates it. The producer is responsible for defining the event schema and versioning. Consumers must adapt to the producer's published contract. A domain cannot publish an event on behalf of another domain.

## 7. Event Payload Rules
Every event (Domain or Integration) MUST contain the following standard metadata:
- `event_id`: UUIDv7 (ensures time-sortable uniqueness).
- `aggregate_id`: UUIDv7 of the entity mutated.
- `tenant_id`: UUIDv7 for strict data isolation.
- `occurred_at`: ISO 8601 UTC timestamp.
- `event_version`: Integer (starts at 1).

## 8. Event Immutability Rules
Events represent facts that have already occurred. Therefore, they are strictly immutable.
- Once created, an event's payload CANNOT be altered under any circumstances.
- If an erroneous event is published, a subsequent compensating event MUST be published (e.g., `HarvestReportCorrected`, `InventoryAdjustmentApplied`).

## 9. Transactional Outbox Pattern
To guarantee that business data and event data are written atomically without requiring distributed two-phase commits (2PC), ATLS mandates the Transactional Outbox Pattern.
- When an Aggregate is saved, its generated Domain and Integration Events are written to an `Outbox` table within the *same database transaction*.
- A separate background worker reads the `Outbox` and dispatches the events to the message broker or event bus.

## 10. Outbox Persistence Rules
- **Rule:** Outbox writes MUST occur in the same DB transaction as the aggregate state mutation. If the outbox write fails, the aggregate mutation rolls back.
- Once an event is successfully published to the bus, it is marked as processed or deleted from the Outbox.

## 11. Event Publishing Lifecycle
1. **Command Execution:** User triggers an action.
2. **Aggregate Mutation:** Business logic executes; Aggregate state changes.
3. **Event Generation:** Aggregate instantiates Domain/Integration Events.
4. **Local DB Transaction:** Aggregate state and Events (via Outbox) are saved atomically.
5. **Outbox Relay:** Background process polls Outbox and publishes to Event Bus.
6. **Dispatch:** Event Bus routes to subscribed queues.

## 12. Event Consumer Architecture
Consumers run as decoupled background workers or async Celery tasks. A consumer listens to a specific queue, receives the event payload, and executes its bounded context's logic (e.g., updating a read model, sending an email, or mutating its own aggregates).

## 13. Consumer Isolation Rules
- Consumers in Bounded Context B MUST NOT access the database of Bounded Context A.
- Consumers rely *solely* on the data provided within the Integration Event payload or must issue a defined API query (via ACL) if supplementary data is required.

## 14. Retry Strategy
Transient failures (network blips, DB deadlocks) are inevitable.
- **Rule:** Retries MUST use exponential backoff.
- Example: 1st retry at 5s, 2nd at 25s, 3rd at 125s, etc.
- A maximum retry limit MUST be established (e.g., 5 attempts) before an event is considered a "Poison Event".

## 15. Dead Letter Queue Strategy
- **Rule:** Poison events (events that exhaust retry limits or encounter unhandled exceptions) MUST move to a Dead Letter Queue (DLQ).
- Events in the DLQ trigger alerts to engineering for manual inspection, debugging, and eventual replay or discarding.

## 16. Idempotency Rules
Because message brokers guarantee "at-least-once" delivery, consumers may receive the same event multiple times.
- **Rule:** Consumers MUST be idempotent.
- Applying the same event twice MUST result in the exact same system state as applying it once. This is typically achieved by tracking processed `event_id`s in the consumer's database schema (e.g., an `ProcessedEvents` table).

## 17. Duplicate Event Handling
When an event arrives, the consumer checks if `event_id` exists in its `ProcessedEvents` ledger. If it exists, the consumer acknowledges the message and safely ignores it, taking no further action.

## 18. Event Ordering Rules
While UUIDv7 provides time-sortability, true strict ordering across distributed systems is challenging.
- Consumers should be designed to handle out-of-order events where possible (e.g., using `event_version` or timestamps to discard older updates if a newer one was already processed).

## 19. Event Versioning Strategy
When an event schema must change (e.g., adding a field), the `event_version` increments.
- Additive changes (new fields) are generally safe.
- Destructive changes (removing/renaming fields) require a new event type (e.g., `HarvestReportSubmittedV2`) or strict mapping layers in consumers to support both versions during transition.

## 20. Event Replay Philosophy
The system should support replaying Integration Events to rebuild read models (CQRS projections) or seed new services.
- This requires events to be retained in an Event Store for a determined retention period.
- Consumers must be robust against replaying historical events.

## 21. CQRS Projection Flow
Command and Query Responsibility Segregation (CQRS) uses events to synchronize optimized read models.
- **Rule:** CQRS projections MUST update asynchronously.
- The HTTP request that mutates data returns immediately after the Outbox write. A consumer subsequently processes the Domain Event and updates the Read-Optimized database tables or search indices.

## 22. Read Model Update Rules
Read models are tailored to specific UI views or API responses. They are entirely disposable and reconstructable from the event stream. They must not contain business logic; they only transform event data into projection formats.

## 23. Analytics Projection Events
- **Rule:** Analytics MUST NEVER compute heavy aggregations synchronously during HTTP requests.
- When operational events occur (`YieldRecorded`, `LaborLogged`), Integration Events are dispatched. The Analytics Domain consumes these asynchronously to increment/decrement pre-calculated counters and materialized views.

## 24. Notification Pipeline Events
Notifications (Emails, SMS, Push) are pure side-effects. They are handled by a dedicated Notification Consumer listening for specific Integration Events (e.g., `ThresholdExceeded`, `TaskAssigned`). This keeps the core domain logic completely free of notification delivery concerns.

## 25. Audit Trail Event Flow
Every state-mutating event inherently contributes to the Audit Trail. A dedicated Audit Consumer listens to all system Integration Events and writes them to a specialized, highly compressed, and tamper-evident Audit Log database.

## 26. Inventory Ledger Event Flow
- **Rule:** Inventory MUST rely on an append-only event-driven ledger flow.
- Inventory quantities are not simple `UPDATE inventory SET qty = qty - 1`. Instead, they are calculated by aggregating an append-only stream of `InventoryAdded` and `InventoryDeducted` events.

## 27. Offline Sync Event Handling
In agriculture, devices operate offline. When a mobile app syncs after being offline, it uploads a batch of commands.
- These commands are processed serially, generating events with historical `occurred_at` timestamps (from the device).
- Consumers must respect the `occurred_at` time to apply logic retrospectively if necessary.

## 28. Mobile Device Reconciliation
If an offline device submits an action that violates a business rule (e.g., deducting inventory that was already depleted by another user), the backend command fails. The backend generates a `SyncConflictDetected` event, which is pushed down to the mobile device for user resolution.

## 29. Saga / Process Manager Boundaries
For business processes spanning multiple bounded contexts (e.g., Planning a Crop -> Allocating Inventory -> Scheduling Labor), we use Sagas or Process Managers.
- A Saga listens to events from one context and dispatches commands to another.
- It manages state and triggers compensating transactions if a step fails.

## 30. Long Running Workflow Rules
Workflows taking hours or days rely entirely on event choreography or Saga orchestration. They must track timeouts and explicitly handle SLA breaches via `WorkflowTimeoutExpired` events.

## 31. Failure Recovery Strategy
- If a consumer fails repeatedly, it pauses and waits for DLQ resolution.
- If the Event Bus goes down, the Transactional Outbox ensures no events are lost; they will naturally pile up in the database and be dispatched once the bus recovers.

## 32. Event Monitoring & Observability
Every published event and consumer execution must be traced. OpenTelemetry trace IDs should be injected into Event Metadata. Alarms must trigger on DLQ depth, Outbox staleness (events taking too long to publish), and consumer lag.

## 33. AI Safety Rules
To ensure strict architectural integrity and system stability, the AI MUST adhere to the following rules:
- **FORBIDDEN:** Synchronous cross-domain mutations (e.g., HR Domain updating Farm Domain directly in the same request).
- **FORBIDDEN:** Direct analytics recalculation in HTTP requests.
- **FORBIDDEN:** Non-idempotent consumers.
- **FORBIDDEN:** Mutable event payloads.
- **FORBIDDEN:** Distributed DB transactions (2PC).
- **FORBIDDEN:** Event payloads containing ORM entities (payloads must be primitive serializable JSON/Dicts).

## 34. Forbidden Async Anti-Patterns
- **Event Pinball:** Where Event A triggers Event B, triggering Event C, triggering Event A, causing an infinite loop. Use correlation IDs to trace and break cycles.
- **Fat Events:** Including massive binary data (like images) in events. Pass a URL/reference instead.
- **Sync over Async:** Waiting synchronously on an HTTP thread for an async event to complete.

## 35. Real-World Agricultural Scenarios
- **Scenario:** A tractor breaks down (`EquipmentFailed`).
- **Flow:** Operations Domain consumes `EquipmentFailed` to halt tasks. HR Domain consumes it to reassign labor. Analytics consumes it to update downtime metrics. All happen asynchronously without the Equipment Domain knowing about HR or Analytics.

## 36. Future Evolution Strategy
As ATLS scales, the event bus may migrate from Redis/RabbitMQ to Kafka or AWS EventBridge. Because producers write to an Outbox and consumers are decoupled listeners, changing the transport layer requires zero changes to the core domain business logic.
