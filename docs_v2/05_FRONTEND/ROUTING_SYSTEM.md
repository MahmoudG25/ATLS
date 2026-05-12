# ROUTING SYSTEM

## Purpose
Define the master frontend routing and navigation execution architecture for ATLS, enabling mobile-first navigation, multi-tenant route isolation, role-aware guards, permission-aware rendering, lazy loading, and runtime navigation configuration.

## Scope
Covers route architecture, layout systems, auth and permission guards, mobile navigation routing, deep linking, offline route handling, white-label routing, RTL support, and AI-safe routing patterns.

## Current Status
- [x] Not Started
- [ ] In Progress
- [ ] Completed

## Dependencies
- `docs_v2/05_FRONTEND/COMPONENT_ARCHITECTURE.md`
- `docs_v2/02_UI_UX/NAVIGATION_SYSTEM.md`
- `docs_v2/02_UI_UX/RTL_SYSTEM.md`
- `docs_v2/02_UI_UX/MOBILE_FIRST_STRATEGY.md`
- `docs_v2/01_ARCHITECTURE/STATE_MANAGEMENT.md`
- `docs_v2/07_AI_AGENT/AI_DEVELOPMENT_RULES.md`

## Notes
This is the master frontend routing system document for ATLS. Routes are domain-isolated, mobile-first, runtime-configurable, and permission-aware.

## Last Updated
2026-05-12

---

## 1. Routing Philosophy
ATLS routing is domain-driven, mobile-first, and centered around hierarchy-aware workflows. Route composition serves navigation, not route tree complexity.

## 2. Route Architecture Strategy
Route architecture separates public, authenticated, tenant-scoped, and feature routes. Each domain hosts its own route definitions and lazy-loaded entrypoints.

## 3. Public Route Rules
Public routes are minimal and only provided for authentication, marketing, or onboarding. They should not expose tenant or role-specific UI.

## 4. Authenticated Route Rules
Authenticated routes are guarded at the router level. The router verifies auth before rendering domain layouts.

## 5. Tenant-Aware Routing
Tenant-aware routing uses tenant ID context in route params or state. Tenant scope is validated before rendering tenant-specific layouts and data.

## 6. Role-Aware Routing
Role-aware routing maps route access to user roles. Route fragments are enabled or hidden based on role metadata instead of in-component checks.

## 7. Permission-Based Routing
Permission guards evaluate authorization centrally. Routes render only when required permissions are present and fallback to unauthorized UX otherwise.

## 8. Feature Flag Routing
Feature flag routing hides disabled modules. Routes are registered dynamically based on enabled tenant features.

## 9. Layout Routing Architecture
Layout routes wrap domain pages with shared shells. Avoid duplicate layouts by reusing route-level layout components across domains.

## 10. Route Grouping Strategy
Group routes by domain and feature. Use nested routes for shared layout sections and domain-specific drill-down flows.

## 11. Domain Route Isolation
Each domain defines its own route tree. Shared routes are kept generic and do not import domain-private modules.

## 12. Lazy Route Loading
Enforce lazy-loading for domain chunks and heavy pages. Use route-based code splitting for initial-performance optimization.

## 13. Route-Based Code Splitting
Split code by route groups and page entrypoints. Keep route files small and declarative.

## 14. Mobile Navigation Routing
Mobile routing prioritizes bottom navigation and shallow stacks. Route transitions support one-handed navigation patterns.

## 15. Bottom Navigation Rules
Bottom navigation routes are primary mobile entrypoints. Keep tabs limited and accessible, with clear active state.

## 16. Sidebar Navigation Routing
Sidebar navigation is reserved for wider screens. Mobile routing does not depend on desktop sidebars.

## 17. Dashboard Navigation Routing
Dashboard routes are dynamic and configurable. Dashboards link to detail routes for drill-down analytics.

## 18. Hierarchy Drill-Down Routing
Drill-down routes represent hierarchy levels in the URL. The routing system preserves context and allows back traversal.

## 19. Breadcrumb Routing Strategy
Breadcrumbs reflect route hierarchy and current scope. They provide orientation without requiring deep menus.

## 20. Deep Linking Rules
Deep links resolve to the appropriate route and restore navigation context. They support tenant, role, and hierarchy parameters.

## 21. Dynamic Route Rules
Routes are generated dynamically from runtime configuration when needed. Route registration supports tenant-specific and feature-flagged paths.

## 22. URL Naming Conventions
Use clear, semantic URLs with domain context and entity IDs. Keep route names stable and human-readable.

## 23. Route Metadata Strategy
Route metadata includes title, permissions, layout, and analytics hooks. Metadata is consumed by guards, breadcrumbs, and navigation components.

## 24. Route Transition UX
Transitions are smooth and mobile-optimized. Use route-level animations sparingly and avoid jarring page changes.

## 25. Offline Route Handling
Offline route handling shows cached views and offline indicators. Routes remain accessible with fallback content when data is unavailable.

## 26. Error Route Handling
Use dedicated error routes and boundaries for failed render states. Errors should be contained and provide recovery options.

## 27. 404 & Recovery UX
404 routes offer clear guidance, search, and navigation back to safe entrypoints. Recovery UX helps users find relevant content quickly.

## 28. Unauthorized Access UX
Unauthorized routes display permission-aware messaging and redirect options. Do not expose underlying route structure to unauthorized users.

## 29. Search Navigation Rules
Search navigation links directly to route targets. Search results should include route context and actionable entrypoints.

## 30. Runtime Navigation Configuration
Runtime navigation configuration updates available routes without deployment. The routing system consumes configuration for route visibility and layout selection.

## 31. White-Label Navigation Rules
White-label navigation uses tenant-specific branding and route sets. Navigation remains isolated and does not leak across tenants.

## 32. RTL Navigation Rules
RTL navigation mirrors route flow and menu order. Routing components support direction-aware transitions and layout orientation.

## 33. Route Analytics Rules
Route analytics track route views, transitions, and permission denials. Analytics fire from route metadata and centralized route events.

## 34. Route Performance Constraints
Keep route files small and lazy-loaded. Avoid loading heavy pages on initial route resolution.

## 35. Route Prefetching Strategy
Prefetch routes judiciously for likely next screens. Use route prefetching on hover only on non-mobile contexts.

## 36. AI Safety Rules
AI must not:
- generate giant route files
- hardcode route trees
- duplicate layouts across routes
- scatter permission checks through components
- create deeply nested route chaos
- render heavy pages without lazy loading
- mutate routes directly in components
- tightly couple navigation systems

## 37. Forbidden Routing Anti-Patterns
- monolithic route files
- static hardcoded route trees
- duplicated layout components
- inline permission logic in many components
- deep nesting with no layout reuse
- non-lazy loaded heavy pages
- direct route mutation in UI
- tightly coupled domain navigation

## 38. Real-World Agricultural Routing Scenarios
- **Tenant dashboard:** a white-label tenant loads a dynamic dashboard route list that adapts to enabled modules and tenant branding.
- **Field drill-down:** an operator navigates from farm summary to sector and enclosure detail routes using shallow mobile stacks.
- **Unauthorized route:** a supervisor is redirected from a disabled feature route to a safe operations summary with permission-aware messaging.

## 39. Future Navigation Expansion
- Expand route configuration with AI-assisted navigation recommendations.
- Add smarter prefetching for likely drill-down paths.
- Support route-level theming and layout swaps.
- Improve offline route caching for faster recovery.
- Evolve runtime route registration with tenant marketplace modules.

## 40. Final Routing Enforcement Checklist
- routes remain domain isolated
- navigation remains mobile-first
- permissions remain centralized
- layout duplication is avoided
- lazy loading is enforced
- routing supports runtime configuration
- route files stay small and declarative
- route metadata governs guards and analytics
- no direct route mutation inside components
- no hardcoded navigation trees
