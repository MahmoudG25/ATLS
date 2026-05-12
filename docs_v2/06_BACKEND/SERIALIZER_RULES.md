# DRF Serializer Governance

| Metadata | Details |
| :--- | :--- |
| **Document ID** | ATLS-BACK-04 |
| **Status** | AUTHORITATIVE |
| **Version** | 2.0.0 |
| **Owner** | Backend Architecture Team |
| **Applicability** | All DRF API Serializers |

## 1. Serializer Philosophy
In ATLS, serializers are **Data Gateways**, not business logic containers. Their role is strictly limited to:
- **Transformation**: Converting Python types to JSON (and vice-versa).
- **Format Validation**: Ensuring inputs match expected types and structures.
- **Contract Enforcement**: Guaranteeing a stable API response for the frontend.

## 2. DTO Boundaries
- **Input Flow**: `Request` -> `Serializer` -> `DTO` -> `Service`.
- **Output Flow**: `Service` -> `Domain Object` -> `Serializer` -> `Response`.
- **Rule**: Serializers must never pass raw `validated_data` to a service. Always map to a typed DTO first.

## 3. Validation Responsibilities
- **Serializer**: Validates field presence, format (e.g., Email, UUID), and basic range checks.
- **Service**: Validates business state (e.g., "Is this harvest season still open?").
- **Rule**: If validation requires a database query, it belongs in the Service or a specialized Validator called by the Service.

## 4. Read vs Write Serializers
- **Separation**: Always use separate classes for Reading (List/Detail) and Writing (Create/Update).
- **Naming**: `[Model]ReadSerializer` and `[Model]WriteSerializer`.
- **Rationale**: Read serializers often need nested data and computed fields, while write serializers must be flat and strict.

## 5. Nested Serializer Rules
- **Reads**: Allowed up to 2 levels deep for high-context views. For deeper requirements, use flat IDs and the frontend will fetch details.
- **Writes**: **STRICTLY FORBIDDEN**. Write serializers must be flat. Handling nested writes (e.g., creating a parent and 10 children in one request) leads to "Nested Write Chaos." Use separate API calls or a specialized Service for bulk operations.

## 6. Response Envelopes
Every ATLS response follows a standard envelope:
```json
{
  "status": "success",
  "data": { ... },
  "metadata": {
    "timestamp": "2024-05-12T10:00:00Z",
    "version": "v1"
  }
}
```

## 7. Pagination Contracts
Standardized pagination metadata:
```json
{
  "count": 1050,
  "next": "url?cursor=abc",
  "previous": null,
  "results": [ ... ]
}
```

## 8. Error Contracts
Standardized error format for frontend parsing:
```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input provided",
    "details": {
      "field_name": ["Specific error message"]
    }
  }
}
```

## 9. Field Naming Rules
- **JSON**: `snake_case` (standard for ATLS frontend/backend alignment).
- **IDs**: Always use `id` for primary keys (UUIDs). Use `[entity]_id` for foreign keys in write serializers.

## 10. Enum Serialization
- **Input**: Accept both the key (integer/string) and the human-readable label.
- **Output**: Return an object: `{"id": "ACTIVE", "label": "Active"}` to prevent frontend-side mapping.

## 11. Media Serialization
- **Format**: Return absolute URLs for images/files.
- **Optimization**: Include `thumbnail_url` and `blur_hash` for operational images (e.g., harvest evidence).

## 12. Audit Serialization
- Standard `AuditSerializer` mixin for all operational entities:
```python
class AuditSerializer(serializers.Serializer):
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)
```

## 13. Performance Constraints
- **N+1**: Never use `SerializerMethodField` to perform a database query. This is the #1 cause of API performance failure.
- **Logic**: If you need related data, use `select_related` in the selector and map the field directly.

## 14. Serializer Composition
- Use **Mixins** for shared field groups (e.g., `LocationMixin` for GPS fields).
- Avoid deep inheritance hierarchies (> 2 levels).

## 15. AI Safety Rules
- **Business Logic**: AI agents MUST NOT place business logic (calculations, complex IF statements) in serializers.
- **Nested Writes**: FORBID nested write implementations in `create()` or `update()`.
- **ORM**: FORBID ORM queries inside serializer fields or `validate()` methods.
- **Inheritance**: FORBID "Giant Serializers" that inherit from multiple complex parents.
- **Side Effects**: FORBID hidden side effects (sending emails, triggering tasks) inside serializers; use services.

## 16. Forbidden Serializer Anti-Patterns
- **The Query in Field**: Using `SerializerMethodField` to fetch related records.
- **The Fat validate()**: Putting 50 lines of business validation in `validate()`.
- **Direct Save**: Calling `serializer.save()` inside the serializer itself (should be done in the view/service context, though ATLS prefers `service.execute(dto)`).

## 17. Agricultural API Scenarios
- **Harvest Batch**: Read serializer includes nested `enclosure` and `crew` summary. Write serializer accepts `enclosure_id`, `crew_id`, and `weight`.
- **Worker List**: Uses `only()` fields in the selector to populate a lightweight `WorkerListSerializer` for high-speed mobile loading.

## 18. Enforcement Checklist
- [ ] Separate Read/Write serializers are used.
- [ ] No DB queries in `SerializerMethodField`.
- [ ] Input data is mapped to a DTO before being passed to a service.
- [ ] Field names use `snake_case`.
- [ ] No nested writes are implemented.
- [ ] Error format follows the standard contract.
- [ ] Enums return `{id, label}` objects.
- [ ] Audit fields are included for operational entities.
