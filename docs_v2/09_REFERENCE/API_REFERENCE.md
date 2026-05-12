# API Standards & Reference

| Metadata | Details |
| :--- | :--- |
| **Document ID** | ATLS-REF-API |
| **Status** | AUTHORITATIVE |
| **Version** | 2.0.0 |
| **Owner** | API Architecture Team |
| **Applicability** | Global Backend API Governance |

## 1. API Philosophy
The ATLS API is a **Stateless Contract**. It must be consistent, secure, and highly predictable for both frontend developers and AI agents. We prioritize machine-readability and tenant safety over "concise" responses.
- **Contract-First**: Every change must be reflected in the schema/documentation.
- **Tenant-Locked**: Every request must be validated against the caller's tenant context.
- **Fail-Fast**: Provide descriptive, machine-readable errors for all failures.

## 2. REST Architecture Standards
- **Protocol**: HTTPS only.
- **Format**: JSON (Request and Response).
- **Stateless**: No server-side sessions; all state in the JWT.

## 3. Base URL Structure
- Production: `https://api.atls.ai/api/v2/`
- Staging: `https://api.staging.atls.ai/api/v2/`

## 4. Versioning Rules
- **Strategy**: URL-based versioning (e.g., `/v2/`).
- **Breaking Changes**: Increments the version number.
- **Non-Breaking Changes**: Additions to existing models do not increment version.

## 5. Authentication Rules
- **Method**: Bearer Token (JWT).
- **Header**: `Authorization: Bearer <token>`.

## 6. JWT Usage Rules
- Tokens must contain: `user_id`, `tenant_id`, and `exp`.
- **FORBIDDEN**: Storing sensitive business data or permissions directly in the JWT payload.

## 7. Tenant Context Rules
- The `tenant_id` MUST be extracted from the JWT and used to scope every database query.
- **Cross-Tenant**: Any attempt to access a resource not belonging to the `tenant_id` must return a `404 Not Found` (to prevent ID enumeration) or `403 Forbidden`.

## 8. Endpoint Naming Rules
- Use plural nouns: `/farms/`, `/harvest-loads/`, `/inventory-items/`.
- Use `kebab-case` for multi-word resources.

## 9. CRUD Endpoint Standards
- `GET /resource/`: List (paginated).
- `GET /resource/{id}/`: Retrieve single.
- `POST /resource/`: Create.
- `PUT /resource/{id}/`: Full update.
- `PATCH /resource/{id}/`: Partial update.
- `DELETE /resource/{id}/`: Soft delete.

## 10. Query Parameter Standards
- Boolean: `?is_active=true`.
- Date range: `?created_at__gte=2026-01-01&created_at__lte=2026-01-31`.

## 11. Filtering Standards
- Use `django-filter` style naming: `?field__lookup=value` (e.g., `?name__icontains=farm`).

## 12. Pagination Standards
- **Mandatory**: All list endpoints must be paginated.
- **Method**: Limit-Offset or Cursor-based.
- **Params**: `?limit=100&offset=0`.

## 13. Sorting Standards
- Param: `?ordering=-created_at,name`.

## 14. Response Envelope Standards
```json
{
  "status": "success",
  "data": { ... },
  "meta": {
    "count": 100,
    "limit": 10,
    "offset": 0
  },
  "correlation_id": "uuid-v7-value"
}
```

## 15. Error Response Standards
```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "The provided data is invalid.",
    "details": { ... }
  },
  "correlation_id": "uuid-v7-value"
}
```

## 16. Validation Error Format
```json
{
  "details": {
    "field_name": ["This field is required.", "Value must be positive."]
  }
}
```

## 17. File Upload Endpoints
- Use `multipart/form-data` for direct uploads or Signed-URL patterns for large files.
- Return the `media_id` and the S3 URI.

## 18. Media URL Standards
- Return signed, temporary URLs for private media assets.

## 19. Async Job Endpoints
- Return `202 Accepted` with a `job_id`.
- Provide a `GET /jobs/{id}/` endpoint to poll status.

## 20. Offline Sync Endpoints
- `POST /sync/`: Batch upload of offline operations.
- `GET /sync/delta/`: Fetch only changes since `last_sync_timestamp`.

## 21. Bulk Operation Endpoints
- `POST /resource/bulk-create/`: Array of items.
- Atomic by default (all succeed or all fail).

## 22. Idempotency Rules
- Use `Idempotency-Key` header for non-safe methods (POST, PATCH).
- Required for high-value operations (e.g., financial transactions, harvest completion).

## 23. Permission Error Rules
- Return `403 Forbidden` for authenticated users with insufficient permissions.

## 24. Audit Exposure Rules
- The API must allow querying an entity's history via `GET /resource/{id}/history/`.

## 25. Notification Endpoints
- `GET /notifications/unread-count/`
- `PATCH /notifications/{id}/read/`

## 26. Reporting Endpoints
- `POST /reports/generate/`: Triggers async generation.

## 27. Analytics Endpoints
- Scoped to read-only projections.
- **FORBIDDEN**: Running heavy analytical queries against operational tables.

## 28. Rate Limiting Standards
- Tiered by user role.
- Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`.

## 29. Performance Constraints
- Response time target: < 200ms for 90% of requests.
- Max payload size: 5MB for JSON.

## 30. API Deprecation Rules
- Header: `Warning: 299 - "This version is deprecated. Please migrate to v3."`.
- Minimum 6 months notice before removal.

## 31. API Documentation Standards
- **Standard**: OpenAPI (Swagger) 3.0.
- Mandatory descriptions for every field and parameter.

## 32. AI Safety Rules
- **Consistency**: AI agents MUST NOT return inconsistent response structures between endpoints.
- **Undocumented**: FORBID creating or using undocumented endpoints.
- **Internal IDs**: FORBID exposing internal DB IDs; use UUIDv7 exclusively.
- **Permissions**: AI MUST NOT implement endpoints that bypass the `tenant_id` or permission checks.
- **Heavy Analytics**: FORBID synchronous heavy analytical queries in operational endpoints.
- **Giant Payloads**: FORBID returning > 1000 items in a single non-paginated response.
- **Pagination**: FORBID list endpoints without mandatory pagination parameters.

## 33. Forbidden API Anti-Patterns
- **The "God" Endpoint**: One endpoint that does everything based on a `type` parameter.
- **HTML in JSON**: Returning pre-formatted HTML inside a JSON response.
- **200 OK Errors**: Returning `200 OK` when the payload contains an error message.

## 34. Agricultural ERP API Scenarios
- **Syncing 50 Harvest Loads**: Using the `/sync/` endpoint to upload 50 harvest load records captured offline during a 12-hour shift without connectivity.
- **Report Export**: Requesting a PDF export of the monthly inventory movement via the async `/reports/` engine.

## 35. Future API Expansion
- GraphQL support for the Analytics domain.
- Webhook subscriptions for external agricultural integrations.

## 36. Final API Checklist
- [ ] Endpoint uses plural kebab-case nouns.
- [ ] Versioning included in URL.
- [ ] JWT authentication enforced.
- [ ] Tenant context injected and verified.
- [ ] Mandatory pagination on list endpoints.
- [ ] Standardized error response format used.
- [ ] Performance targets met (< 200ms).
- [ ] OpenAPI documentation updated.
- [ ] No internal IDs exposed.
