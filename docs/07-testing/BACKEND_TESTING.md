# Backend Testing Strategy

## Philosophy
Our backend testing philosophy prioritizes stability and correctness for enterprise systems, with a strict focus on tenant isolation, permission boundaries, and data integrity.

## Tooling
- **Test Runner:** `pytest`
- **Django Integration:** `pytest-django`
- **Data Generation:** `factory_boy` and `faker`
- **Coverage Check:** `pytest-cov`

## Test Layers
1. **Model Tests:** Minimal. Only test custom model methods or complex properties.
2. **Selector Tests:** Verify that queries correctly filter by tenant and permissions.
3. **Service Layer Tests:** The core of our testing. Verify business logic, transaction safety, and error handling.
4. **API Endpoint Tests:** Validate request validation (serializers), response schemas, and HTTP status codes.

## Important Constraints
- **Tenant Isolation:** Every data access test MUST verify that Tenant A cannot access Tenant B's data.
- **No Production Refactoring:** Write tests that adapt to existing architecture, not the other way around.
- **Avoid Heavy Mocks:** Use factories to generate valid test data in the database rather than extensively mocking database calls.
