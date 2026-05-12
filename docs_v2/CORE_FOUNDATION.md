# ATLS Platform: Core Foundation Architecture

> **Confidential & Proprietary**  
> **Target Audience:** Principal Architects, Engineering Leads, AI Implementation Agents  
> **Scope:** Foundational Architecture for ALL Domains and Infrastructure  

---

This document is the absolute root technical foundation for the ATLS agricultural ERP platform. It establishes the unalterable laws upon which all subsequent domains, services, and dynamic engines are built. 

If a domain violates the rules in this document, it is not part of the ATLS platform.

---

## 1. Shared Kernel
The Shared Kernel holds only the most fundamental primitives that exist below the domain boundary. 
*   **Allowed:** Canonical value objects (`Money`, `Coordinates`, `Dimensions`), global enums, base exceptions, and tenant context abstractions.
*   **Forbidden:** Business logic, domain-specific calculations, database queries, and repository implementations.

## 2. Base Entity Architecture
Every aggregate root and entity in the system inherits from a strict `BaseEntity` abstract class.
*   **Mandatory Fields:** `id` (UUIDv7), `tenant_id` (UUID), `created_at` (UTC), `updated_at` (UTC), `version` (Optimistic Locking).
*   **Behavior:** Entities must encapsulate their state. Properties must have private setters, mutating only via explicit behavioral methods.

## 3. UUID Strategy
The platform exclusively uses **UUIDv7**.
*   **Why UUIDv7:** It is time-ordered, providing natural chronological sorting and preventing database index fragmentation (B-Tree thrashing) typical of UUIDv4.
*   **Integers Forbidden:** Auto-incrementing integer IDs are strictly banned to prevent enumeration attacks and support offline-first distributed data generation.

## 4. Tenant Isolation Architecture
ATLS is a strictly multi-tenant SaaS platform.
*   **Tenant Scoping:** Every query, write, and background job MUST include the `tenant_id`. 
*   **Infrastructure Enforcement:** Repositories must transparently inject `WHERE tenant_id = ?` into every ORM call. Global query filters are mandatory. Cross-tenant access requires extreme `SUPER_ADMIN` authorization and is restricted to global analytics tools.

## 5. White Label Foundation
The system is built to be resold and branded.
*   **Tenant Configuration:** UI assets, logos, terminology (e.g., "Field" vs "Block"), and email templates are stored as configuration variables tied to the `tenant_id`.
*   **Hardcoding Banned:** No brand names or specific client terminology may be hardcoded in the UI or backend.

## 6. Feature Flag System
All major features, dynamic engines, and major API versions must be feature-flagged.
*   **Granularity:** Flags can be targeted globally, per-tenant, or per-user.
*   **Code Lifecycle:** Flags are temporary. Once a feature is 100% rolled out, the flag code MUST be ripped out during the next sprint.

## 7. Global Audit Base
Every state mutation is tracked.
*   **Requirements:** `user_id`, `device_id`, `correlation_id`, `timestamp`, `action`, `previous_state`, `new_state`.
*   **Immutability:** Audit tables are append-only. Updates or deletes to an audit record are physically prevented at the database level.

## 8. Timestamp Standards
*   **Storage:** ALL timestamps in the database are stored in **UTC**.
*   **Transport:** ALL API requests and responses use **ISO 8601 strings** (e.g., `2026-05-12T03:38:30Z`).
*   **Presentation:** Conversion to the tenant's or user's local timezone happens *exclusively* in the frontend UI or notification template.

## 9. Soft Delete Rules
Data in an ERP is never truly deleted.
*   **Mechanism:** `BaseEntity` includes an `is_active` boolean or `deleted_at` timestamp.
*   **Cascades:** Deleting a parent aggregate soft-deletes its owned children. Hard-deletes are restricted to GDPR compliance scripts executed by platform administrators.

## 10. Domain Exception System
*   **Base Class:** All exceptions inherit from `DomainException`.
*   **Categorization:** Exceptions are typed (e.g., `InvariantViolation`, `ConcurrencyConflict`, `ResourceNotFound`).
*   **No HTTP Leakage:** Domain exceptions do not know about HTTP 404 or 400. The API presentation layer maps Domain Exceptions to HTTP status codes.

## 11. Result Pattern
To prevent control-flow-via-exceptions for expected business logic branches, the Application layer uses a Result pattern.
*   **Signatures:** Methods return `Result<T, Error>`.
*   **Handling:** Consumers must explicitly check `.is_success()` before accessing `.value()`.

## 12. Event Base Classes
All Domain Events inherit from `BaseDomainEvent`.
*   **Payload Requirements:** `event_id` (UUIDv7), `correlation_id`, `timestamp`, `event_type`, `version`.
*   **Immutability:** Event properties are read-only upon instantiation.

## 13. Permission Foundation
Permissions are granular and dynamic, not hardcoded to roles.
*   **Action-Based:** Systems check if a user `can_harvest_enclosure`, not if they are a `Supervisor`.
*   **Ownership Boundaries:** Permissions evaluate the context (e.g., user can edit tasks *only* in Enclosures they manage).

## 14. Role System Foundation
Roles are mere templates that group Permissions.
*   **Dynamic Roles:** Tenants can create custom roles (e.g., `Night Shift Lead`) and assign specific permissions via the Permission Engine.
*   **No Hardcoded Roles:** Checking `user.role == 'ADMIN'` in business logic is forbidden.

## 15. Global Config Architecture
Configuration is hierarchical.
*   **Resolution Order:** Environment Variables -> Tenant Settings -> Default System Settings.
*   **Caching:** Configuration reads are heavily cached in Redis to prevent database saturation.

## 16. Environment Configuration Rules
*   **12-Factor App:** Configuration is strictly separated from code. Secrets, broker URLs, and database credentials exist only in the environment.
*   **Fail Fast:** If a required environment variable is missing on boot, the application must crash immediately.

## 17. Security Foundations
*   **Zero Trust:** Every API request is fully authenticated and authorized regardless of internal network placement.
*   **CORS & CSRF:** Strict domain whitelisting. CSRF tokens mandatory for state-changing browser requests.

## 18. Encryption Standards
*   **Data at Rest:** All databases and object storage buckets are encrypted at rest using AES-256.
*   **PII/Financial Data:** Sensitive fields (e.g., bank details, biometric signatures) are encrypted at the column level before hitting the database.
*   **Data in Transit:** TLS 1.3 is mandatory. Unencrypted HTTP traffic is rejected at the load balancer.

## 19. File Storage Foundation
*   **Abstraction:** The system depends on a `StorageProvider` interface, not a specific AWS S3 or Azure Blob SDK.
*   **Access:** Direct public URLs are forbidden. Files are accessed via presigned, time-expiring URLs to enforce tenant authorization.

## 20. Media Ownership Standards
*   **Aggregate Linkage:** Every file/image is owned by an Aggregate Root (e.g., an `EnclosureImage` belongs to an `EnclosureAggregate`).
*   **Lifecycle:** If an aggregate is archived, its media metadata is archived.

## 21. API Response Envelope
All APIs return a strict, predictable JSON envelope.
```json
{
  "data": { ... },
  "meta": { "pagination": { ... }, "correlation_id": "uuid" },
  "errors": null
}
```
*   **Consistency:** The frontend knows exactly how to parse successes and errors without writing custom try/catch logic per endpoint.

## 22. Pagination Standards
*   **Cursor Pagination:** Default for high-frequency data (like Event Streams or Operation Logs) to prevent offset lag and table scanning.
*   **Offset Pagination:** Allowed only for UI data grids where exact page numbers are a hard product requirement.

## 23. Global Validation Standards
*   **Fail Early:** Payload shape validation happens at the API boundary (Serializer/Pydantic).
*   **Domain Validation:** Business rule validation happens entirely inside the Aggregate Root. 

## 24. Localization Foundation
*   **Language Keys:** The backend only returns translation keys (e.g., `errors.invalid_crop_state`), never translated strings.
*   **Translation Engine:** The frontend resolves translation keys to the user's selected language using a localization engine (e.g., i18next).

## 25. RTL Foundation
The system is built to support languages like Arabic natively.
*   **Flexbox/Grid Logic:** Uses logical CSS properties (e.g., `margin-inline-start`, not `margin-left`).
*   **UI Components:** All components automatically mirror themselves when the HTML `dir` attribute is set to `rtl`.

## 26. Theme Engine Foundation
*   **CSS Variables:** All colors, spacing, and typography are defined as CSS variables (Custom Properties).
*   **Dark Mode Native:** Every component must support `prefers-color-scheme`.

## 27. Design Token Strategy
*   **Semantic Tokens:** Colors are referenced by intent (`color-surface-danger`), not value (`color-red-500`).
*   **White-Label Integration:** The Theme Engine overrides semantic tokens dynamically based on Tenant configuration.

## 28. Logging Foundation
*   **Structured Logging:** All logs are output as JSON.
*   **Required Context:** `timestamp`, `level`, `correlation_id`, `tenant_id`, `user_id`.
*   **No PII in Logs:** Scrubbing filters must execute before logs are flushed to stdout.

## 29. Correlation ID Standards
*   **Origin:** Generated at the API Gateway or edge layer.
*   **Propagation:** Travels through the HTTP headers (`X-Correlation-ID`), into the local thread context, attached to all Domain Events, and passed to background workers.
*   **Traceability:** A single ID connects an API request to a background calculation 5 minutes later.

## 30. Request Context Architecture
*   **Thread-Local Storage:** Information like `tenant_id` and `user_id` is securely placed in ContextVars (or equivalent thread-local storage) by middleware.
*   **Warning:** Must be explicitly cleared/reset to prevent data leakage in async or thread-pool environments.

## 31. Cache Foundation
*   **Strategic Caching:** Only immutable data, configuration, or high-read/low-write read models are cached.
*   **Invalidation:** Cache invalidation is triggered by Domain Events, never by manual UI triggers.

## 32. Redis Usage Rules
*   **Separation of Concerns:** Use separate Redis databases or instances for Caching, Sessions, and Message Queues (Celery).
*   **TTL Mandatory:** Every cache key must have a Time-To-Live. Infinite caching is banned.

## 33. Background Job Foundation
*   **Idempotency:** Every background job MUST be idempotent. It must be safe to run it 10 times consecutively.
*   **Granularity:** Jobs must be small and targeted. Instead of one job processing 10,000 tasks, enqueue 10,000 jobs processing 1 task each.

## 34. Celery Foundation
*   **Late Acknowledgment:** Tasks are only acknowledged after successful execution (`acks_late=True`) to prevent data loss if a worker crashes.
*   **Timeouts:** Every task must have a hard `soft_time_limit` and `time_limit` to prevent hung workers.

## 35. Transaction Standards
*   **Scope:** Transactions encapsulate a single Aggregate Root mutation.
*   **Isolation Levels:** Default to `READ COMMITTED`. Financial or critical inventory state updates must use `SERIALIZABLE` or explicit row-level locking (`SELECT FOR UPDATE`).

## 36. Outbox Foundation
*   **Transactional Guarantee:** Domain Events are inserted into an `outbox_events` table in the same database transaction that updates the domain entity.
*   **Relay Worker:** A separate process continually polls the outbox and publishes events to the message broker, guaranteeing At-Least-Once delivery.

## 37. CQRS Foundation
*   **Command/Query Split:** The API exposes Command endpoints (mutations) and Query endpoints (reads) using different models and serializers.
*   **Segregation:** Commands execute via the Domain layer. Queries bypass the Domain and hit Read Models directly.

## 38. Read Model Foundation
*   **Eventual Consistency:** Read models are updated by asynchronous event handlers. UIs must expect slight propagation delays.
*   **Flat Structures:** Read models are highly denormalized for extreme `SELECT` performance. No complex joins.

## 39. AI Agent Safety Rules
> [!CAUTION]
> **MANDATORY DIRECTIVES FOR AI IMPLEMENTATION AGENTS**
*   **Never Bypass Base Classes:** AI must inherit from `BaseEntity`, `DomainException`, and `BaseDomainEvent`.
*   **Never Bypass Tenant Context:** Queries generated by AI that lack explicit tenant filtering will be automatically rejected.
*   **Never Write Raw Datetimes:** AI must always use UTC utilities for timestamps.
*   **Never Hardcode Logic:** AI must utilize the feature flag and configuration engines for environmental behaviors.

## 40. Anti-Patterns & Forbidden Implementations
*   **Auto-Incrementing IDs:** Will leak business volume and break offline syncing.
*   **Hard-Deleting Data:** Destroys analytical integrity and audit trails.
*   **Synchronous External APIs:** Never call an external service (e.g., Weather API, Email Provider) inside a synchronous database transaction.
*   **Fat Views/Controllers:** Putting business logic in the UI or API router instead of the Domain layer.
*   **Shared Mutable State:** Relying on global variables or mutated singletons.

---

**Architecture Final Decree:**
This foundation is non-negotiable. Scalability, tenant security, and data integrity depend entirely on the unyielding enforcement of these 40 pillars. Build with discipline.
