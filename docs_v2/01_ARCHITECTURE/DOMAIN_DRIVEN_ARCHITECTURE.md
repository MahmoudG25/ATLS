# ATLS Platform: Domain Driven Architecture

> **Confidential & Proprietary**  
> **Target Audience:** Principal Architects, Engineering Leads, AI Implementation Agents  
> **Type:** Master Governance Document  

---

## 1. DDD Philosophy
ATLS employs Domain-Driven Design (DDD) to align software architecture directly with the complex, physical realities of agricultural operations. Our code speaks the language of the farm. We isolate complexity by breaking the massive ERP system into strictly bounded contexts, ensuring that a change in how a tractor is maintained does not break how a harvest is compensated.

## 2. Strategic Design Principles
*   **Business Alignment:** The architecture must reflect the organizational structure and operational reality of our agricultural tenants.
*   **Explicit Boundaries:** Code must never casually leak across domains. If the HR domain needs Operations data, it must ask formally, not query the Operations database tables directly.
*   **Continuous Evolution:** Domains are not static. As the business understanding of farming operations deepens, the domain boundaries and models must refactor to reflect that new knowledge.

## 3. Tactical Design Principles
*   **Rich Domain Models:** Logic belongs in the Aggregate, not in massive procedural service scripts.
*   **Framework Agnosticism:** Core business logic must be isolated from the specific ORM, HTTP framework, or database vendor.
*   **Event-First Mentality:** Domains communicate state changes via Domain Events, promoting decoupling and eventual consistency.

## 4. Bounded Context Philosophy
A Bounded Context is a linguistic and architectural boundary. A "Worker" in the HR Context is an entity with a salary and attendance. A "Worker" (Operator) in the Equipment Context is simply a reference ID validated for a driving license. The definitions are context-specific and must not be forced into a single, monolithic "God Model."

## 5. Context Mapping Strategy
*   We utilize **Partnership** where domains heavily co-evolve (e.g., Operations and Harvest).
*   We utilize **Customer/Supplier** (via APIs and Events) for downstream dependencies (e.g., Analytics consuming Operations).
*   We utilize **Anti-Corruption Layers (ACL)** when integrating with legacy systems or third-party external services.

## 6. Domain Classification
To focus engineering effort, domains are classified by their strategic value to the ATLS platform.

## 7. Core Domains
The primary differentiators of ATLS.
*   **Farm Domain:** The spatial and structural representation of the land.
*   **Operations Domain:** The execution engine for all agricultural activities.
*   **Harvest Domain:** The yield tracking and origin mapping system.

## 8. Supporting Domains
Necessary for the platform to function, but not the primary selling point.
*   **Equipment Domain:** Asset management and maintenance.
*   **HR Domain:** Labor tracking and piece-rate compensation.
*   **Inventory Domain:** Inputs, chemicals, and spare parts management.

## 9. Generic Domains
Commodity functionalities that could theoretically be replaced by off-the-shelf software.
*   **Notification Domain:** Email, SMS, and Push notifications.
*   **Audit Domain:** System logging and compliance tracking.
*   **Analytics Domain:** Projections and dashboard rendering (Read-Only).

## 10. Aggregate Philosophy
Aggregates are transactional boundaries. They represent a cluster of domain objects that can be treated as a single unit. They exist to protect business invariants (rules that must always be true).

## 11. Aggregate Root Rules
*   Every Aggregate has one and only one Root Entity.
*   External objects must hold references only to the Root Entity (via ID), never to internal entities.
*   Only the Root Entity is permitted to be obtained directly via database queries. All internal entities are loaded through the Root.

## 12. Entity Rules
*   Entities have an identity (`id`) that persists over time, even if their attributes change.
*   Equality is determined by the identity, not the attributes.

## 13. Value Object Rules
*   Value Objects have no identity. They are defined solely by their attributes (e.g., `Money`, `GPSCoordinate`, `Temperature`).
*   They MUST be immutable. If a value changes, a new Value Object is instantiated and replaces the old one.

## 14. Repository Rules
*   Repositories mediate between the domain and data mapping layers using a collection-like interface.
*   **One Repository per Aggregate Root.**
*   Repositories strictly return Domain Entities, not ORM models or raw database dictionaries.
*   **NO FAT REPOSITORIES:** Repositories only handle persistence and retrieval; they do not contain business validation logic.

## 15. Domain Service Rules
*   Used for business logic that spans multiple Aggregates within the *same* Bounded Context, or logic that doesn't naturally fit on a single Entity.
*   Must be stateless.
*   Example: A `PreventiveMaintenanceSchedulingService` that analyzes an `Equipment` aggregate and an `OperationsSchedule` aggregate.

## 16. Application Service Rules
*   The orchestrator layer. Also known as Use Cases or Command Handlers.
*   They fetch the Aggregate from the Repository, execute a method on the Aggregate, and save it back to the Repository.
*   They do *not* contain business logic. They handle transactions, security, and orchestrating external dependencies.

## 17. Command Handler Architecture
*   Commands are intent-based instructions to mutate state (e.g., `AssignWorkerToCrewCommand`).
*   Handled by Application Services. They mutate the domain and publish Domain Events.
*   Commands return success/failure or the new aggregate ID, not complex data structures.

## 18. Query Handler Architecture
*   Queries are requests for data without mutating state (e.g., `GetDailyHarvestYieldQuery`).
*   Queries completely bypass the Domain Model and Repositories. They hit Read Models or raw SQL directly for maximum performance.

## 19. CQRS Philosophy
*   Command Query Responsibility Segregation (CQRS) is an **architectural separation**, not necessarily a mandate for dual databases or microservices.
*   In ATLS, we implement CQRS at the application layer: different classes/handlers for Writes (Domain/Aggregates) vs. Reads (Projections/SQL Views).

## 20. Event-Driven Philosophy
*   Changes in state are communicated via Events.
*   "Event" means something that *has already happened* (e.g., `HarvestYieldLoggedEvent`).
*   Promotes high decoupling. The Harvest Domain doesn't need to know the Analytics Domain exists; it just broadcasts the event.

## 21. Domain Event Ownership
*   Domain Events are owned by the Bounded Context that generated them.
*   They are published synchronously within the same transaction to trigger internal side-effects (e.g., updating a Read Model in the same database).

## 22. Integration Event Rules
*   Integration Events are simplified Domain Events broadcast over a message broker (e.g., Kafka/RabbitMQ) to *other* Bounded Contexts.
*   They only contain primitives (IDs, timestamps), never complex serialized Domain Objects, to prevent tight coupling to the producer's internal structures.

## 23. Transactional Boundaries
*   A single HTTP Request or Command must mutate **ONE and ONLY ONE** Aggregate synchronously.
*   If multiple Aggregates must be updated, the first is updated synchronously, and the others are updated asynchronously via Domain Events.

## 24. Eventual Consistency Rules
*   Because we mutate one Aggregate per transaction, cross-aggregate and cross-domain updates are eventually consistent.
*   The UI must be designed to handle this (e.g., optimistic UI updates, polling, or websockets) instead of forcing the backend to use massive, blocking distributed transactions.

## 25. Read Model Philosophy
*   Projections tailored exactly for UI screens.
*   Built asynchronously by listening to Domain Events.
*   Stored in denormalized tables or fast document stores to eliminate complex `JOIN` operations on read.

## 26. Anti-Corruption Layer Rules
*   When consuming data from an external system (or a poorly bounded legacy module), the ACL translates the external model into the ATLS Domain Model.
*   Ensures that external changes don't infect our core business logic.

## 27. Inter-Domain Communication Rules
*   **Rule 1:** Synchronous cross-domain database queries (ORM imports) are strictly FORBIDDEN.
*   **Rule 2:** Prefer Asynchronous Events (Integration Events).
*   **Rule 3:** If synchronous data is strictly required, use cross-domain Application Services/APIs that return Data Transfer Objects (DTOs), never Domain Entities.

## 28. Shared Kernel Rules
*   A shared library of primitive types used across all domains (e.g., `TenantId`, `Money`, `BaseDomainEvent`).
*   Must be kept extremely small. Modifying the Shared Kernel requires coordination across all domain teams.

## 29. Domain Isolation Rules
*   Each domain must be structured as if it were an independent service, even if housed within a modular monolith repository.
*   No sharing of database tables between domains. If domains share a Postgres instance, they use separate schemas.

## 30. Dependency Direction Rules
*   Dependencies always point inwards.
*   Infrastructure (Databases, APIs, UI) depends on Application Services.
*   Application Services depend on Domain Models.
*   Domain Models depend on nothing outside themselves.

## 31. Multi-Tenant Domain Isolation
*   Tenant isolation is enforced at the Repository and Read Model levels.
*   Domain Entities intrinsically belong to a `TenantId`. Any Command interacting with an aggregate must implicitly validate the acting user's tenant context.

## 32. White-Label Domain Isolation
*   Domain Logic must remain agnostic to UI branding.
*   Business rules cannot rely on "Client A's specific UI configuration." All white-label variations must be driven by explicit Tenant Configuration injected into Domain Services.

## 33. Offline Domain Considerations
*   Domain logic must support conflict resolution (Last-Write-Wins or Additive Merges) because Commands generated by offline mobile apps may be executed hours or days after they were intended.

## 34. AI Safety Rules
> [!CAUTION]
> **MANDATORY AI IMPLEMENTATION RULES**
> *   **No God Services:** AI MUST NOT create `FarmOperationsHarvestManager` services. Keep services scoped strictly to their context.
> *   **No Cross-Domain Imports:** AI MUST NOT import models from `hr.models` inside `operations.services`. Use the defined API or Event bus.
> *   **No Direct Aggregate Mutation:** AI MUST NOT bypass Application Services to mutate an Aggregate state directly within a View or API Controller.
> *   **Protect Invariants:** AI MUST ensure all state mutations occur via explicit methods on the Aggregate Root, never via public property setters.

## 35. Anti-Patterns
*   **Anemic Domain Model:** Aggregates that are just bags of getters and setters with no business logic.
*   **Fat Application Services:** Putting all the `if/else` business rules in the orchestrator instead of the Domain Model.
*   **Synchronous Distributed Transactions:** Trying to save a `Harvest`, deduct `Inventory`, and update `Analytics` in a single monolithic database transaction.

## 36. Real-World Scenarios
**Scenario:** A Worker completes a Pruning Operation.
*   **Bad DDD:** The `OperationController` fetches the Operation, updates it, fetches the Worker, updates their hours, fetches the Analytics table, updates the dashboard, and calls `save()` on all three.
*   **ATLS DDD:** The `OperationController` dispatches `CompleteOperationCommand`. The `Operations` Application Service loads the `OperationAggregate`, calls `operation.complete()`, saves it, and publishes `OperationCompletedEvent`. The `HR Domain` listens to this event to log labor hours asynchronously. The `Analytics Domain` listens to update the dashboard asynchronously.

## 37. Architectural Tradeoffs
*   We accept eventual consistency (and the UI complexity it brings) in exchange for high availability, decoupling, and horizontal scalability.
*   We accept the boilerplate of defining DTOs, Commands, and Queries to prevent the tight coupling caused by passing ORM models directly to the presentation layer.

## 38. Future Evolution Strategy
*   This Modular Monolith architecture is explicitly designed for future extraction. By enforcing strict domain boundaries today, we guarantee that if the `Harvest Domain` needs to scale independently during peak season, it can be seamlessly extracted into a true microservice without rewriting its core business logic.
