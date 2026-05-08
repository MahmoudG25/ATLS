# Frontend Testing Strategy

## Philosophy
Frontend testing ensures reliable UI behavior and data formatting without becoming tightly coupled to DOM implementation details. We favor testing user interactions and application state over testing presentation.

## Tooling (Future Roadmap)
- **Test Runner:** `Vitest` or `Jest`
- **UI Testing:** React Testing Library (RTL)

## Test Layers
1. **Utility Tests:** Pure JavaScript functions (like formatters or access control) should be thoroughly unit tested.
2. **Component Tests:** Isolate complex UI components (e.g., recursive Tree views) and assert they render correct structures based on mock data.
3. **Integration Tests:** Test interactions between components and Context providers (e.g., Theme, Auth, Notifications).

## Important Constraints
- **Mock the Service Layer:** Never allow UI tests to make real network requests. Mock the API layer instead.
- **Focus on Behavior:** Test what the user sees and interacts with (roles, attributes, text) rather than internal state variables.
