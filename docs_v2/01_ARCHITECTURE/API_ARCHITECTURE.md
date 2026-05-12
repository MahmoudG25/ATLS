# ATLS Platform: Master API Governance Architecture

## 1. API Philosophy
The ATLS API acts as the primary external contract for the platform. It is designed to be mobile-first, offline-capable, and strictly separated into Command (Write) and Query (Read) operations following CQRS principles. The API serves as a thin presentation layer, delegating all business logic to the underlying Application and Domain layers.

## 2. API Architectural Style
We adhere to Pragmatic REST. Resources are exposed as predictable URLs, utilizing standard HTTP methods to signify intent. However, we deviate from pure REST where necessary for performance or domain expressiveness (e.g., using explicit verb endpoints for complex actions like `/api/v1/harvests/{id}/submit`).

## 3. REST Resource Design
Endpoints must represent domain aggregates or read models. 
- Nouns are used for resources: `/api/v1/farms`, `/api/v1/workers`.
- Nested resources should only be used when the child cannot exist without the parent and the boundary is small: `/api/v1/farms/{id}/fields`.
- Deeply nested resources (more than two levels) are forbidden; use query parameters instead.

## 4. API Versioning Strategy
APIs are strictly versioned in the URL path (e.g., `/api/v1/`).
- Minor, non-breaking changes (adding fields) do not require a version bump.
- Major, breaking changes (removing fields, changing payload structures) require creating `/api/v2/`.
- Both versions must be supported concurrently during the deprecation window.

## 5. URL Naming Rules
- Use kebab-case for URL segments: `/api/v1/task-reports`.
- Use plural nouns for collections: `/api/v1/users`.
- Use snake_case for query parameters: `?start_date=2026-05-12`.

## 6. Request Envelope Standards
POST, PUT, and PATCH requests should accept a flat JSON body representing the Command or DTO. We avoid wrapping request bodies in redundant outer keys like `{"data": {...}}` to keep client payloads clean.

## 7. Response Envelope Standards
All successful API responses MUST follow a standardized envelope to provide predictable parsing for frontend and mobile clients:
```json
{
  "success": true,
  "data": { ... }, 
  "meta": {
    "pagination": { ... },
    "timestamp": "2026-05-12T05:00:00Z"
  }
}
```

## 8. Error Response Standards
Error responses MUST provide actionable information without leaking internal stack traces or ORM details:
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "The provided data is invalid.",
    "details": [
      { "field": "yield_amount", "issue": "Must be greater than zero." }
    ]
  },
  "meta": { "trace_id": "req_123abc" }
}
```

## 9. HTTP Status Code Rules
- `200 OK`: Successful read or update.
- `201 Created`: Resource successfully created.
- `202 Accepted`: Async operation queued.
- `400 Bad Request`: Validation failure or business rule violation.
- `401 Unauthorized`: Missing or invalid authentication.
- `403 Forbidden`: Authenticated, but lacks permission.
- `404 Not Found`: Resource does not exist.
- `409 Conflict`: Resource state conflict (e.g., offline sync collision).
- `500 Internal Server Error`: Unexpected system failure.

## 10. Authentication Architecture
The API relies on token-based authentication. The primary mechanism is JSON Web Tokens (JWT) passed in the `Authorization: Bearer <token>` header. Session cookies are avoided for API calls to ensure cross-platform (mobile/web) compatibility.

## 11. JWT Lifecycle Rules
- Access tokens are short-lived (e.g., 15-30 minutes).
- They contain minimal payload data: `user_id`, `tenant_id`, and `role_id`.
- They MUST NOT contain sensitive PII or massive permission arrays.

## 12. Refresh Token Strategy
- Refresh tokens are long-lived (e.g., 7 days) and stored securely on the client.
- They are rotated upon use (Refresh Token Rotation) to detect and prevent replay attacks.
- The server maintains a revocation list or tracks token families to instantly invalidate compromised sessions.

## 13. Permission Evaluation Flow
Permissions are evaluated at the API/Application boundary before domain logic executes. 
1. `IsAuthenticated` check (Token validity).
2. `HasTenantAccess` check (Context validity).
3. `HasRolePermission` check (Action validity).

## 14. Tenant Isolation Enforcement
ATLS is a multi-tenant platform. 
- The `tenant_id` MUST be resolved from the authenticated user's token or context.
- APIs MUST NEVER accept `tenant_id` as an untrusted client input in the request body for data manipulation.
- All ORM queries backing the API MUST automatically filter by the resolved `tenant_id`.

## 15. Request Context Injection
The current user, tenant, and request metadata (IP, user-agent) are injected into a Request Context object. This object is passed down to Application Services, preventing the Domain Layer from importing Django HTTP request objects.

## 16. Pagination Standards
All list endpoints MUST be paginated. Returning unpaginated collections is forbidden.
The response envelope `meta.pagination` object must include:
- `current_page`, `page_size`, `total_items`, `total_pages`.

## 17. Cursor vs Offset Pagination Rules
- **Offset Pagination** (`?page=2&size=50`): Used for admin dashboards, tables, and standard web views where users jump between pages.
- **Cursor Pagination** (`?cursor=xyz123`): MUST be used for high-velocity feeds, infinite scrolling on mobile devices, and offline sync endpoints to prevent data duplication/skipping when records are inserted during pagination.

## 18. Filtering Architecture
Filters are passed as query parameters. 
- Use standard operators: `?status=active&created_after=2026-01-01`.
- For complex OR conditions, utilize dedicated search endpoints or specialized query syntax (e.g., `?filter[status]=active,pending`).

## 19. Global Search Architecture
Search operations that span multiple fields or require fuzzy matching MUST NOT use heavy SQL `LIKE` queries against transactional tables. They must be routed to a dedicated search endpoint backed by a Read Model or Search Index (e.g., Elasticsearch, Typesense).

## 20. Sorting Rules
Sorting is defined via the `sort` query parameter.
- Ascending: `?sort=created_at`
- Descending: `?sort=-created_at`
- Multiple fields: `?sort=-created_at,status`

## 21. CQRS Query Endpoint Strategy
Write operations (POST, PUT, PATCH) target Command APIs, which update Aggregates.
Read operations (GET) target Query APIs, which bypass Aggregates and fetch data directly from Read Models. The API layer maps the Read Model directly to the Response Envelope.

## 22. Bulk Operation APIs
Endpoints handling bulk inserts or updates (e.g., `/api/v1/inventory/bulk-deduct`) must accept arrays of commands. They must be transactional, applying either entirely or not at all, and should return detailed error structures indicating which specific items failed.

## 23. Offline Synchronization APIs
Mobile clients sync data using a pull/push model.
- **Pull:** `GET /api/v1/sync?last_sync_at=...` returns all events or read models updated since the provided timestamp.
- **Push:** `POST /api/v1/sync` accepts an array of offline commands stored locally by the device.

## 24. Conflict Resolution APIs
When an offline push encounters a conflict (e.g., trying to complete a task already marked completed), the API returns a `409 Conflict` with the current server state. The client is responsible for presenting the conflict to the user for resolution.

## 25. File Upload Architecture
- **Rule:** Direct file uploads through the backend application server's memory are forbidden for large files.
- Small files (avatars) may use `multipart/form-data`.
- Large files (videos, heavy PDFs) must use Pre-Signed URLs.

## 26. Chunk Upload Rules
If Pre-Signed URLs are not feasible, large uploads must use chunked upload APIs, where the client sends the file in smaller byte ranges, and the server reconstructs the file locally before moving it to cold storage.

## 27. Pre-Signed URL Strategy
1. Client requests an upload URL: `POST /api/v1/uploads/request`.
2. API generates a secure, time-limited pre-signed URL (e.g., AWS S3).
3. Client uploads directly to cloud storage.
4. Client notifies API of completion: `POST /api/v1/uploads/confirm`.

## 28. Async Operation APIs
For heavy processing (e.g., generating massive reports), the API MUST NOT block the HTTP thread.
1. Client issues `POST /api/v1/reports/generate`.
2. API returns `202 Accepted` with a `task_id`.
3. Client polls `GET /api/v1/tasks/{task_id}` or listens to WebSockets for completion status.

## 29. Idempotency Key Rules
All state-mutating API endpoints (POST, PUT, PATCH) should accept an `Idempotency-Key` header. If a client retries a request due to a network timeout, the server must recognize the key and return the cached original response without re-executing the transaction.

## 30. Rate Limiting Strategy
APIs must enforce rate limits by IP or User ID to prevent abuse. Rate limit headers (`X-RateLimit-Limit`, `X-RateLimit-Remaining`) should be returned to the client.

## 31. API Caching Rules
- Use `ETag` and `If-None-Match` headers to allow clients to cache Read Models efficiently.
- Cache control headers must be explicitly set to prevent sensitive data from caching in intermediary proxies.

## 32. Read Model API Rules
Endpoints serving read models must return flattened, presentation-ready JSON. The API layer should not force the client to stitch together multiple relationships by making subsequent requests (avoid N+1 API calls).

## 33. API Performance Constraints
- API response times for 95% of requests must be < 200ms.
- Payloads must be strictly minimized; do not return fields the client does not need.
- Database N+1 queries during serialization are forbidden.

## 34. OpenAPI/Swagger Governance
The API contract is the ultimate source of truth. OpenAPI (Swagger) documentation must be auto-generated from code annotations and schema definitions to ensure it never drifts from the actual implementation.

## 35. API Observability & Tracing
Every request generates a `trace_id` returned in the response meta tag. This ID ties together HTTP logs, application logs, DB queries, and background tasks, allowing rapid debugging of cross-system issues.

## 36. AI Safety Rules
To ensure structural integrity and security, AI agents MUST abide by:
- **FORBIDDEN:** Returning raw ORM objects from the API layer.
- **FORBIDDEN:** Inconsistent response/error envelopes.
- **FORBIDDEN:** Creating unpaginated list endpoints.
- **FORBIDDEN:** Synchronous analytics calculations blocking the API thread.
- **FORBIDDEN:** Exposing internal database structures or foreign keys to the client.
- **FORBIDDEN:** Giant nested payloads that impact serialization performance.
- **FORBIDDEN:** Tenant leaks (failing to scope queries by `tenant_id`).
- **FORBIDDEN:** Direct file uploads through backend memory.

## 37. Forbidden API Anti-Patterns
- **Chatty APIs:** Forcing the client to make 10 requests to render one screen.
- **Leaky Abstractions:** Exposing Django's internal field names or error messages directly to the client.
- **Stateful APIs:** Relying on server-side session state for subsequent API calls.

## 38. Real-World Agricultural Scenarios
- **Scenario:** A tractor operator in a low-connectivity zone submits 5 completed tasks.
- **Execution:** The mobile app stores them locally. Upon gaining a signal, it hits the `POST /api/v1/sync` bulk endpoint. The API uses Idempotency keys to ensure that if the network drops during the response, a retry doesn't duplicate the tasks.

## 39. Future Public API Strategy
As the platform matures, a subset of the internal APIs will be exposed as a Public API for external integrations (e.g., John Deere systems). Internal APIs must be designed with strict validation and contracts now, ensuring they are "public-ready" when the time comes.

## 40. Mobile-first API Considerations
Mobile clients suffer from packet loss, high latency, and battery constraints. APIs must be designed to minimize payload size (using aggressive compression and sparse fieldsets), support background sync, and handle aggressive retries gracefully.
