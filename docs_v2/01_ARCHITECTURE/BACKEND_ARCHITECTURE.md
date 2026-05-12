# ATLS Platform: Master Backend Execution Architecture

## 1. Backend Philosophy
The ATLS backend is built to model the complex, real-world reality of agricultural operations. It prioritizes data integrity, deep domain expressiveness, and long-term maintainability over rapid initial development. The backend enforces strict boundaries to prevent "big ball of mud" degradation while leveraging the robust ecosystem of Django.

## 2. Modular Monolith Strategy
We employ a Modular Monolith architecture. While deployed as a single application, the codebase is logically partitioned into strict Bounded Contexts. This provides the deployment simplicity of a monolith with the organizational scalability of microservices, allowing future extraction if necessary.

## 3. Bounded Context Backend Isolation
Each bounded context (e.g., Farm, HR, Inventory, Operations) must operate as an independent subsystem. Contexts communicate via defined APIs or asynchronous events. A module in one context cannot arbitrarily reach into the database or internal classes of another context.

## 4. Django App Structure
Django "apps" map to Bounded Contexts or sub-domains, not technical layers. A typical Django app structure enforces Clean Architecture:
- `models/` (Infrastructure / Persistence)
- `services/` (Application & Domain Layers)
- `repositories/` (Infrastructure)
- `views/` & `serializers/` (Presentation)
- `events/` (Domain / Integration Events)

## 5. Domain Layer Definition
The core of the system. It contains enterprise business rules, Aggregates, Entities, and Value Objects. It must have ZERO dependencies on external frameworks, databases, or infrastructure concerns.

## 6. Application Layer Definition
Orchestrates use cases. It receives commands from the Presentation layer, fetches Aggregates via Repositories, invokes Domain logic, handles transaction boundaries, and dispatches events. It does not contain pure business rules.

## 7. Infrastructure Layer Definition
Contains implementation details: Django ORM models, database migrations, 3rd-party API integrations, and message broker publishers. It implements interfaces defined by the Application/Domain layers.

## 8. Presentation Layer Definition
The entry point (API endpoints, WebSockets, CLI commands). It maps external requests to internal DTOs/Commands, delegates to the Application layer, and formats responses. Views/ViewSets must remain extremely thin.

## 9. Dependency Direction Rules
Dependencies must point INWARD toward the Domain Layer. 
- Presentation depends on Application.
- Application depends on Domain and Interfaces.
- Infrastructure depends on Interfaces defined by Application/Domain.
- Domain depends on NOTHING.

## 10. Request Lifecycle
1. Request arrives at Django URL Router.
2. View/ViewSet receives request.
3. Serializer validates payload format.
4. View calls an Application Service.
5. Application Service executes business logic within a transaction.
6. Results/Errors bubble back up to View.
7. Serializer formats response for client.

## 11. Command Execution Flow
Commands mutate state. They are handled by Application Services which:
- Start a Unit of Work (Transaction).
- Load an Aggregate from a Repository.
- Execute a method on the Aggregate.
- Save the Aggregate via Repository.
- Write Domain/Integration events to the Outbox.
- Commit the Transaction.

## 12. Query Execution Flow
Queries read state. They bypass the Domain layer and Application Services for performance, often reading directly from Read Models, search indices, or lightweight ORM queries designed specifically for the Presentation layer.

## 13. CQRS Backend Separation
Command and Query Responsibility Segregation is enforced. Write paths (Commands) go through strict Domain logic and Aggregates. Read paths (Queries) are optimized for data retrieval, returning flattened DTOs without loading heavy Aggregate roots.

## 14. Application Services Rules
- Must orchestrate, not calculate.
- Must coordinate transaction boundaries.
- Must handle authorization checks before execution.
- Must return primitive DTOs or Result objects, never ORM models.

## 15. Domain Services Rules
- House business logic that doesn't naturally fit inside a single Entity/Aggregate.
- Must remain pure and free of side-effects (no direct DB writes).
- Rely on data passed into them or injected abstractions.

## 16. Repository Pattern Rules
- Abstract away the Django ORM from the Domain/Application layers.
- Implement methods that return/save Aggregates.
- Hide complex filtering and join logic.
- Prevent the leaking of Django `QuerySet` objects into the Application layer.

## 17. ORM Usage Rules
- `models.Model` classes belong purely to the Infrastructure layer.
- They are persistence models, NOT domain models.
- **Rule:** Cross-domain ORM imports are strictly forbidden. If HR needs Farm data, it must query the Farm module's public Application Service or API.

## 18. Serializer Architecture
Django REST Framework (DRF) serializers are strictly for data mapping and structural validation (e.g., "is this a valid email format?").
- **Rule:** Business logic MUST NOT exist inside serializers. No `create()` or `update()` overrides containing domain rules.

## 19. Validation Pipeline
1. **Presentation Validation:** Format checks (Serializers/Pydantic).
2. **Application Validation:** Use-case specific rules (e.g., "User has permission to do this task").
3. **Domain Validation:** Invariant enforcement (e.g., "Cannot harvest a crop that isn't planted").

## 20. Transaction Management
- Transactions MUST remain short-lived.
- Confined to the Application Service layer handling a Command.
- External network calls (e.g., Stripe, sending an email) inside DB transactions are strictly forbidden to prevent database lock exhaustion.

## 21. Unit of Work Strategy
The Unit of Work pattern coordinates atomic changes. In Django, this is typically managed using `transaction.atomic()` wrapped around the Application Service execute method, ensuring aggregate state and outbox events commit together.

## 22. Event Publishing Lifecycle
Application Services do not publish events directly to the broker. They persist events to the Outbox table within the Unit of Work. A separate async worker reliably publishes them.

## 23. Async Task Architecture
Long-running workflows, heavy computations, and integrations must be offloaded to background tasks (e.g., Celery). Async workflows MUST rely on domain/integration events or explicit task delegation, never synchronous HTTP blocking.

## 24. Background Worker Rules
Workers must be idempotent. They should anticipate transient failures and rely on the Retry/DLQ strategies defined in the Event System architecture.

## 25. File Upload Processing
File uploads (images, PDFs) must be handled asynchronously. The synchronous HTTP request returns a signed URL or upload confirmation. Background workers process resizing, virus scanning, or data extraction.

## 26. Permission Evaluation Flow
Permissions are evaluated at the Presentation or Application layer *before* domain logic executes. Use a policy-based approach rather than scattering `if user.is_admin` checks throughout the code.

## 27. Tenant Isolation Enforcement
ATLS is multi-tenant. Tenant isolation must be enforced at the lowest possible infrastructure level (e.g., custom ORM managers automatically filtering by `tenant_id`). Application code should rarely need explicit tenant filtering logic.

## 28. API Error Handling Strategy
Use standardized exception handling to map Domain exceptions to HTTP status codes. The client should receive predictable error payloads (e.g., `code`, `message`, `details`), never stack traces.

## 29. Result Pattern Strategy
Application Services should return `Result` objects (Success/Failure wrappers) rather than throwing generic exceptions for expected business rule violations. Exceptions are for exceptional circumstances.

## 30. Read Model Query Rules
Queries against read models should avoid complex joins where possible. Data should be pre-computed by event handlers.

## 31. Caching Philosophy
Cache at the edges (Presentation layer or Read Models). Do not cache Domain logic or Aggregate state, as it introduces complexity and eventual consistency issues in the write path.

## 32. Observability & Logging
Every request must be assigned a correlation ID. Logs, metrics, and traces (OpenTelemetry) must be generated at the Application Service boundary.

## 33. Testing Architecture
- **Unit Tests:** Focus on Domain Models and Domain Services. Fast, no DB.
- **Integration Tests:** Focus on Repositories and Application Services with a real DB.
- **E2E Tests:** Focus on API endpoints.

## 34. AI Safety Rules
To ensure strict architectural integrity, AI agents MUST abide by:
- **FORBIDDEN:** Fat services that mix orchestration and domain logic.
- **FORBIDDEN:** God repositories handling multiple aggregates.
- **FORBIDDEN:** Direct cross-domain mutations (e.g., HR updating Farm DB directly).
- **FORBIDDEN:** Business logic inside serializers or views.
- **FORBIDDEN:** Direct ORM access from UI-facing or Presentation layers.
- **FORBIDDEN:** Giant transactional workflows spanning multiple requests.
- **FORBIDDEN:** Synchronous analytics calculations during state mutation.

## 35. Forbidden Backend Anti-Patterns
- **Anemic Domain Model:** Entities that are just bags of getters/setters while all logic lives in services.
- **Smart UI / Fat Controllers:** Views that handle validation, business rules, and DB saving.
- **Hidden Side Effects:** Updating related entities directly instead of using domain events.

## 36. Real-World Agricultural Scenarios
- **Scenario:** Processing a massive harvest yield.
- **Execution:** 
  1. UI sends POST request.
  2. View calls `RecordYieldService`.
  3. Service loads `HarvestAggregate`, updates state, generates `YieldRecorded` event.
  4. Repository saves state and outbox event in one transaction.
  5. HTTP returns 200 OK.
  6. Worker pushes event. Inventory context consumes event and updates quantities async.

## 37. Future Service Extraction Strategy
Because boundaries are strictly maintained within the modular monolith, extracting a bounded context into a standalone microservice requires only routing API requests and re-configuring event bus connections, not rewriting business logic.

## 38. Performance Constraints
- N+1 queries must be strictly eliminated in Read paths.
- Aggregate boundaries must be kept small to reduce memory overhead and DB lock contention.
- Paginate all list responses by default.
