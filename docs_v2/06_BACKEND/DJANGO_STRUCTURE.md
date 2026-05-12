# Django Backend Structure & Governance

| Metadata | Details |
| :--- | :--- |
| **Document ID** | ATLS-BACK-01 |
| **Status** | AUTHORITATIVE |
| **Version** | 2.0.0 |
| **Owner** | Backend Architecture Team |
| **Applicability** | All ATLS Backend Services |

## 1. Backend Philosophy
The ATLS backend is a **Modular Monolith** built for high-scale agricultural operations. It prioritizes **Domain Integrity** over development speed. We follow a "DDD-Lite" approach where business logic is strictly decoupled from the web framework (Django). 
- **Database is an implementation detail**: Avoid leaking ORM logic into the service layer.
- **Explicit over Implicit**: No magic signals; use explicit event dispatching.
- **Tenant First**: Every query must be scoped by `tenant_id` at the lowest possible level.

## 2. Modular Monolith Rules
- **Encapsulation**: Each module (e.g., `farm`, `harvest`, `hr`) must own its models, services, and tests.
- **Communication**: Cross-module communication must happen via **Public Services** or **Domain Events**, never via direct ORM imports of another module's models.
- **Dependencies**: Circular dependencies between modules are strictly forbidden.

## 3. Django App Structure
Each bounded context is represented as a Django app. Standard internal structure:
```text
[app_name]/
├── api/                # DRF Views & Serializers (Web Layer)
├── services/           # Business Logic (Application Layer)
├── repositories/       # Data Access (Persistence Layer)
├── selectors/          # Query Logic (Read Layer)
├── models/             # DB Schema (Infrastructure Layer)
├── tasks/              # Celery Tasks (Async Layer)
├── events/             # Domain Event Definitions
├── tests/              # Multi-tier testing
└── migrations/         # DB Migrations
```

## 4. Domain Isolation
- Models in `Module A` must not have `ForeignKey` relations to `Module B`. Use "Soft Links" (UUID references) or a shared `core` ID if necessary.
- **Bounded Context**: Each module defines its own ubiquitous language.

## 5. Shared Kernel Rules
Common logic resides in `apps.core`. This includes:
- Base Model mixins (Audit, UUIDv7).
- Shared value objects (Currency, Weights).
- Global Exception Handlers.
- Tenant context middlewares.

## 6. Application Layer
The Application Layer (Services) coordinates the execution of business logic.
- It translates DTOs/Primitives into Domain actions.
- It manages transactions across multiple repositories.
- It dispatches events upon completion.

## 7. Infrastructure Layer
Includes Django Models, Database Migrations, and External Client implementations (e.g., Weather API, GPS Service).
- **Models**: Must only contain field definitions and basic `__str__`. Zero business logic.

## 8. Service Layer
- **Stateless**: Services should not hold state between calls.
- **Functional**: Aim for pure functions where possible.
- **Signature**: Prefer keyword arguments for clarity.

## 9. Repository Layer
- **Responsibility**: Encapsulate all ORM `QuerySet` logic.
- **Benefit**: Allows swapping the database or adding a caching layer without touching business logic.
- **Rule**: Views/Services must not call `.filter()` or `.exclude()` directly on models. Use repositories.

## 10. CQRS Separation
We separate "Write" operations (Commands) from "Read" operations (Queries/Selectors).
- **Commands**: Perform state changes, validate business rules, and save to DB.
- **Queries**: Optimize for data retrieval, pagination, and projection for the UI.

## 11. Commands & Queries
- **Command Name**: Verb-first (e.g., `CreateHarvestReport`, `UpdateEnclosureStatus`).
- **Query Name**: Descriptive (e.g., `GetEnclosureAnalytics`, `ListActiveWorkers`).

## 12. DTO Rules
- **Data Transfer Objects**: Use Pydantic models or `NamedTuples` to pass data between layers.
- **FORBIDDEN**: Passing `request.POST` or Raw QuerySets into service methods.

## 13. Domain Events
- **Mechanism**: Every significant change emits an event (e.g., `harvest_completed`).
- **Integration**: Events are persisted to an `Outbox` table within the same transaction to ensure reliability.

## 14. Celery Structure
- **Location**: Define tasks in `[app]/tasks/`.
- **Naming**: `[app].[task_name]` (e.g., `harvest.sync_yield_data`).
- **Retries**: Always implement exponential backoff for external integrations.

## 15. Async Execution
- **Offloading**: Any operation taking > 200ms must be offloaded to Celery.
- **Idempotency**: All tasks must be idempotent to handle retries safely.

## 16. API Boundaries
- **REST**: Follow standard HTTP verbs and status codes.
- **Versioning**: Header-based or URL-based (`/api/v1/`).
- **Documentation**: Mandatory OpenAPI (Swagger/Redoc) annotations for every endpoint.

## 17. Tenant Isolation
- **Row-Level**: Every model inherits from `TenantModel`.
- **Middleware**: Sets the current `tenant_id` in a thread-safe context.
- **Managers**: Models use a default manager that filters by the active `tenant_id`.

## 18. Permission Boundaries
- **Roles**: Use a fine-grained Permission system (e.g., `can_edit_harvest`).
- **Checks**: Perform checks at both the API (View) and Service layer.

## 19. Serializer Boundaries
- **Responsibility**: Transformation and basic field validation ONLY.
- **Cleanliness**: Serializers should call service methods, not save models directly.

## 20. Transaction Rules
- **Atomic**: Use `transaction.atomic` at the service level.
- **Duration**: Keep transactions as short as possible to prevent DB locking.
- **Events**: Only dispatch integration events *after* the transaction commits (`transaction.on_commit`).

## 21. Audit Integration
- **Tracking**: Every change records `created_by`, `updated_by`, and a JSON diff of the change.
- **Retention**: Audit logs are immutable and kept indefinitely in cold storage.

## 22. Config Structure
- **Django Environ**: Use `.env` files for all environment-specific variables.
- **Structure**: `settings/base.py`, `settings/dev.py`, `settings/prod.py`.

## 23. Environment Separation
- **Local**: SQLite/Docker-Postgres.
- **Staging**: Mirror of production.
- **Production**: High-availability RDS, dedicated Celery workers.

## 24. File Organization
- Follow the 2-character prefix rule for consistency (e.g., `01_CORE`, `02_FARM`).
- Keep module size manageable; split into sub-packages if an app exceeds 10 models.

## 25. Testing Structure
- **Unit**: Test service methods in isolation (mock repositories).
- **Integration**: Test API endpoints with a live test DB.
- **Coverage**: Minimum 80% coverage required for domain logic.

## 26. Migration Rules
- **Atomic Migrations**: One feature = one migration.
- **Safe Altering**: Never delete a column in the same release it's deprecated.
- **Data Migrations**: Use separate scripts, not standard `makemigrations` for large data changes.

## 27. Logging Structure
- **Levels**: `INFO` for operational flow, `ERROR` for exceptions, `CRITICAL` for system failure.
- **Format**: Structured JSON logging for easy parsing by ELK/CloudWatch.

## 28. Error Handling
- **Domain Exceptions**: Raise specific errors (e.g., `InsufficientStockError`).
- **API Mapping**: Global handler maps Domain Exceptions to correct HTTP codes (400, 404, 409).

## 29. Performance Constraints
- **N+1**: Strictly forbidden. Use `select_related` and `prefetch_related` in repositories.
- **Queries**: No query should take > 100ms.
- **Index**: Mandatory indexing on all foreign keys and frequently filtered fields.

## 30. AI Safety Rules
- **Validation**: AI agents MUST NOT bypass the service layer.
- **Views**: FORBID "fat views" (> 20 lines of logic).
- **Serializers**: FORBID "fat serializers" containing business logic.
- **Models**: FORBID business logic (methods that change state) in Django Models.
- **Utils**: FORBID giant `utils.py` files; use domain-specific logic containers.
- **ORM**: FORBID cross-domain ORM joins (joining `Module A` table with `Module B` in one query).
- **Transactions**: FORBID unmanaged transactions in async tasks.
- **Sync**: FORBID sync-heavy operations (file processing, external API calls) in the request-response cycle.

## 31. Forbidden Django Anti-Patterns
- **Signals**: Do not use `post_save` for business logic; use services.
- **Fat Models**: Avoid adding complex methods to models.
- **Global Imports**: Do not import from `apps.[module]` inside `apps.core`.

## 32. Real Agricultural Scenarios
- **Harvest Batch Creation**: Service `CreateBatch` validates seasonal quotas, creates the record, and triggers a Celery task to notify the quality control team.
- **Labor Assignment**: Command `AssignLabor` checks worker availability across different farm blocks before committing the link.

## 33. Future Microservice Extraction
- Modules are designed to be "Microservice Ready".
- By enforcing soft-links and event-driven communication, any Django app can be moved to a separate repository with minimal friction.

## 34. Enforcement Checklist
- [ ] Logic is in Services, not Views/Models.
- [ ] Data access is via Repositories/Selectors.
- [ ] Tenant isolation is enforced.
- [ ] Transaction boundaries are correct.
- [ ] Domain events are dispatched via Outbox.
- [ ] Tests cover happy and edge cases.
- [ ] N+1 queries checked with `django-silk` or similar.
- [ ] API is fully documented.
