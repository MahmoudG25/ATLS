# Backend Service Layer Governance

| Metadata | Details |
| :--- | :--- |
| **Document ID** | ATLS-BACK-02 |
| **Status** | AUTHORITATIVE |
| **Version** | 2.0.0 |
| **Owner** | Backend Architecture Team |
| **Applicability** | All ATLS Backend Service Implementations |

## 1. Service Philosophy
The Service Layer is the heart of the ATLS platform. It encapsulates all business logic, ensuring the domain remains independent of the delivery mechanism (Django/DRF).
- **Stateless**: Services do not store state; they process inputs and produce outputs/side-effects.
- **Explicit**: Every action is a clearly named function. No "magic" or hidden side-effects.
- **Atomic**: A service call should represent a single, atomic unit of work.

## 2. Thin Views / Fat Services
- **Views**: Responsible for HTTP-level concerns (authentication, rate limiting, request parsing). Views **must not** contain business logic or call `.save()` on models.
- **Services**: Responsible for business rules, data integrity, and cross-module coordination.

## 3. Service Types
We categorize services to prevent "God Services" and maintain clear responsibility.

| Type | Level | Responsibility |
| :--- | :--- | :--- |
| **Application Service** | Entry | Top-level entry points for use cases (e.g., `CreateHarvestReport`). |
| **Domain Service** | Core | Pure domain logic involving multiple aggregates within one module. |
| **Orchestration Service** | Cross-Module | Coordinates workflows involving multiple modules (e.g., `OnboardWorker`). |

## 4. Application Services
These services represent a single user intention.
- They accept DTOs (Pydantic/Dataclasses).
- They handle authorization and tenant enforcement.
- They coordinate between repositories and domain services.

## 5. Domain Services
Used when logic doesn't naturally belong to a single model or repository.
- Example: `YieldCalculationService` which calculates complex harvest weights based on moisture and grade.

## 6. Orchestration Services
Used for workflows that span across multiple bounded contexts.
- Example: `WorkerActivationService` which updates `HR` records, creates a `Security` badge, and notifies `Operations`.

## 7. Transaction Boundaries
- **Ownership**: The Service Layer owns the database transaction.
- **Atomic**: Use `@transaction.atomic` at the entry point of the Application Service.
- **Nesting**: Avoid nested `@transaction.atomic` blocks to prevent unexpected commit/rollback behavior.

## 8. Validation Flow
1. **Request Validation**: DRF Serializer checks data types and basic presence.
2. **Business Validation**: Service Layer checks domain rules (e.g., "Is the farm block already harvested?").
3. **Consistency Validation**: Repository/DB constraints (Unique, FK) as a final safety net.

## 9. Repository Usage
- Services **must** use Repositories for all state mutations.
- Services **must** use Selectors for all data retrieval.
- **Rule**: Never call `Model.objects.create()` or `Model.objects.get()` inside a service.

## 10. Event Publishing
ATLS uses the **Transactional Outbox Pattern**.
- Services create a `DomainEvent` record *within* the same transaction as the business change.
- Integration events are dispatched to external systems (Redis/RabbitMQ) only after the transaction commits successfully.

## 11. Celery Delegation
- Offload long-running tasks (PDF generation, bulk emails, data sync) immediately.
- Pass **IDs**, not full objects, to Celery tasks to prevent stale data issues.

## 12. Error Handling
- **Specific Exceptions**: Define custom exceptions (e.g., `InsufficientInventoryError`).
- **Standardization**: All service exceptions must inherit from a base `DomainError`.

## 13. Result Pattern
For complex operations, return a `Result` object.
```python
@dataclass
class ServiceResult:
    success: bool
    data: Optional[Any] = None
    error_code: Optional[str] = None
    message: Optional[str] = None
```

## 14. DTO Handling
- Convert `request.data` into a DTO before passing it to the service.
- **Benefit**: Decouples the service from DRF/Web framework types.

## 15. Permission Checks
- Perform fine-grained permission checks (e.g., `can_close_season`) inside the service layer, even if checked at the API level. This prevents "backdoor" logic errors.

## 16. Tenant Enforcement
- Every service call must pass a `tenant_id` or `tenant` context.
- **Rule**: All data operations must be scoped by this tenant to ensure absolute data isolation.

## 17. Audit Integration
- Services are responsible for logging who did what.
- Use the `AuditService` to record significant state transitions.

## 18. Rollback Rules
- If any part of a service fails, the entire transaction must roll back.
- **Exception**: "Non-critical" side effects (e.g., sending a non-essential notification) can be handled in a `try/except` block or as an async task.

## 19. Idempotency Rules
- Critical services (e.g., `SubmitPayment`, `CloseInventory`) must support idempotency keys.
- Store the key and the result in Redis/DB to prevent duplicate processing.

## 20. Performance Constraints
- Service execution time (excluding DB) should be < 50ms.
- **Looping**: Avoid DB queries inside loops. Use bulk operations via repositories.

## 21. Testing Strategy
- **Unit Tests**: Mock all external dependencies and repositories. Focus on branch coverage.
- **Component Tests**: Test the service with a real (test) database to verify repository integration.

## 22. AI Safety Rules
- **ORM**: FORBID ORM calls in Django Views; views must only call services.
- **Serializers**: FORBID business logic (calculations, state changes) in DRF Serializers.
- **Mutation**: FORBID direct cross-domain mutation; `Module A` must call a service in `Module B`.
- **Transactions**: FORBID nested transaction chaos; define a single clear entry point for transactions.
- **God Services**: FORBID creating "God Services" that handle multiple unrelated domains.
- **Sync**: FORBID sync-heavy workflows in the request cycle; use `Service -> Task` delegation.

## 23. Forbidden Service Anti-Patterns
- **The Wrapper**: Services that only wrap a single repository call with no logic. (Use a repository directly if it's a pure CRUD read, but write operations always need a service).
- **Import Hell**: Circular imports between services. Use interfaces or events to break cycles.
- **Model Leaks**: Returning raw Django models from services. Return DTOs or Serialized data.

## 24. Agricultural Workflows
- **Pesticide Application**: 
    1. Validate chemical safety data.
    2. Check weather conditions via `WeatherService`.
    3. Update `Field` status.
    4. Record inventory depletion.
    5. Emit `pesticide_applied` event.
- **Harvesting**:
    1. Verify block readiness.
    2. Create `HarvestRecord`.
    3. Update `SeasonalYield` projection.
    4. Trigger quality inspection task.

## 25. Final Checklist
- [ ] Logic is decoupled from `request` and `response` objects.
- [ ] Transaction boundaries are clearly defined.
- [ ] Event publishing follows the Outbox pattern.
- [ ] Tenant context is explicitly handled.
- [ ] DTOs are used for input/output.
- [ ] Exceptions are domain-specific.
- [ ] Performance (N+1) is checked at the repository level.
- [ ] Service is unit-testable without a running Django server.
