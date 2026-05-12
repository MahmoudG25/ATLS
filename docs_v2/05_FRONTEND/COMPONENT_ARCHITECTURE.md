# COMPONENT ARCHITECTURE

## Purpose
Define the master frontend component execution architecture for ATLS, ensuring modular domains, reusable components, runtime theming, RTL support, offline-first UX, and scalable frontend growth.

## Scope
Covers frontend layering, component boundaries, feature architecture, domain isolation, hooks strategy, query and mutation architecture, optimistic updates, offline rendering, and AI-safe frontend constraints.

## Current Status
- [x] Not Started
- [ ] In Progress
- [ ] Completed

## Dependencies
- `docs_v2/02_UI_UX/COMPONENT_GUIDELINES.md`
- `docs_v2/02_UI_UX/THEME_ENGINE.md`
- `docs_v2/02_UI_UX/RTL_SYSTEM.md`
- `docs_v2/02_UI_UX/MOBILE_FIRST_STRATEGY.md`
- `docs_v2/01_ARCHITECTURE/STATE_MANAGEMENT.md`
- `docs_v2/01_ARCHITECTURE/FRONTEND_ARCHITECTURE.md`
- `docs_v2/07_AI_AGENT/AI_DEVELOPMENT_RULES.md`

## Notes
This is the master frontend component execution architecture document for ATLS. Frontend domains are isolated, state ownership is explicit, and React Query governs server state while components remain reusable and presentation-focused.

## Last Updated
2026-05-12

---

## 1. Frontend Architecture Philosophy
ATLS frontend architecture is modular, domain-oriented, and mobile-first. It balances reusable UI composition with strong domain isolation to support scalable agricultural workflows.

## 2. Modular Frontend Domain Strategy
Frontend domains are organized by business capabilities, not by technical layers. Each domain owns its components, hooks, routes, and state contracts.

## 3. Frontend Layering Architecture
Layering separates shared primitives, domain components, page composition, and feature orchestration. Clear boundaries prevent cross-domain dependencies.

## 4. Shared vs Domain Components
Shared components are generic UI primitives and theme-aware building blocks. Domain components encapsulate workflow-specific rendering and compose shared primitives.

## 5. Feature-Based Folder Structure
Use feature-based organization: `features/<domain>`, `components/ui`, `components/widgets`, `hooks`, `lib`, `pages`. Avoid massive shared folders.

## 6. Entity-Based Rendering Strategy
Render based on domain entities and scopes. Entity-based rendering ensures that farm, sector, stage, and enclosure contexts drive the UI structure.

## 7. Component Ownership Rules
Each component belongs to a single domain or shared module. Shared components must not import domain-specific code.

## 8. Page Composition Architecture
Pages coordinate data loading, state orchestration, and domain rendering. Page components compose domain widgets and shared UI without embedding business logic.

## 9. Smart vs Presentation Layering
Smart components manage state and side effects. Presentation components receive props and render UI only.

## 10. Hooks Architecture
Hooks are the primary abstraction for reusable behavior. Custom hooks encapsulate domain logic, state interaction, and data fetching without UI rendering.

## 11. Custom Hook Rules
Custom hooks are reusable and composable. They must not duplicate logic, perform direct fetches inside components, or mix business rules with UI presentation.

## 12. Query Hook Rules
Query hooks wrap React Query and expose typed query results. Query hooks should define keys, stale times, and cache behavior centrally.

## 13. Mutation Hook Rules
Mutation hooks wrap `useMutation`, handle optimistic updates, rollback logic, and invalidation. Mutation hooks keep side effects out of components.

## 14. Optimistic Update Strategy
Optimistic updates are applied through React Query lifecycle handlers. Use snapshot rollback, precise query patching, and only update affected query keys.

## 15. Form State Architecture
Form state is local or schema-driven, with server-backed defaults via React Query. Avoid storing full form payloads in global state.

## 16. Global UI State Rules
Global state is limited to auth, theme, navigation, and lightweight UI flags. Do not use global state to store server data or large entities.

## 17. Server State Rules
Server state is managed by React Query. All API-derived data belongs to query cache and is not duplicated in component state.

## 18. Local State Rules
Local state belongs to components or scoped hooks. Use local state for transient UI concerns only.

## 19. React Query Governance
React Query is the contract for server synchronization, caching, background refresh, optimistic updates, and offline query recovery.

## 20. Cache Invalidation Rules
Invalidate or refetch only affected query keys. Use hierarchical invalidation for related domain entities and avoid broad cache resets.

## 21. Error Boundary Architecture
Use error boundaries around domain pages and widget groups. Boundaries isolate failures and surface recovery actions.

## 22. Suspense & Lazy Loading Rules
Use lazy loading for non-critical components and routes. Suspense is applied to reduce initial load, with fallback skeletons for mobile UX.

## 23. Offline Rendering Strategy
Offline rendering uses cached queries, persisted themes, and local drafts. UI must remain functional with pending sync indicators and stale data warnings.

## 24. Skeleton Rendering Rules
Skeletons and placeholders are used during data loading. They preserve layout and avoid jarring jumps.

## 25. Empty State Rendering Rules
Empty states are meaningful and actionable. They explain the absence of data and suggest next steps.

## 26. Responsive Rendering Architecture
Responsive rendering is mobile-first. Use Tailwind responsive utilities and avoid fixed-width layouts.

## 27. Role-Aware Rendering Rules
Render based on role and permission data. UI should hide unauthorized features and avoid hardcoded role checks in presentation components.

## 28. Permission-Based Rendering Rules
Permission checks are enforced in hooks and higher-order components. Presentation components render only after permission resolution.

## 29. Runtime Theme Rendering
Theme values are injected at runtime and consumed by components through semantic tokens. Components must not hardcode theme values.

## 30. RTL Rendering Rules
Components support RTL natively through logical CSS and mirrored rendering. UI layouts and animations adapt to directionality.

## 31. Dashboard Widget Architecture
Dashboard widgets are isolated, configurable, and lazy-loaded. Widgets consume typed props and avoid global dependencies.

## 32. Dynamic Form Rendering
Forms render dynamically from schema definitions. Component architecture separates field renderers from form orchestration.

## 33. Navigation Rendering Strategy
Navigation components are domain-aware and runtime-configurable. Use contextual navigation hooks rather than hardcoded menu trees.

## 34. Search & Filtering Architecture
Search and filter UIs are composable components with lightweight state. Filtering interacts with query keys and avoids over-fetching.

## 35. Performance Constraints
Keep render cycles minimal, avoid deep component trees, and use memoization. Optimize for low-end mobile hardware.

## 36. Virtualization Rules
Use virtualization for long lists and tables. Avoid rendering large item sets in mobile contexts without virtualization.

## 37. AI Safety Rules
AI must not:
- create god components
- cross-domain import private modules
- duplicate hooks
- make direct fetch calls inside components
- rely on massive shared folders
- use uncontrolled global state
- put business logic inside UI
- deep prop drill state
- produce non-responsive rendering

## 38. Forbidden Frontend Anti-Patterns
- cross-domain imports for domain code
- god components handling UI and data
- direct API fetches in JSX
- huge shared folders with mixed concerns
- duplication of hooks or state logic
- uncontrolled global state stores
- hardcoded layout values
- deep component nesting without reason

## 39. Real-World Agricultural Frontend Scenarios
- **Harvest workflow:** a domain page composes query hooks for plot data, mutation hooks for yield submission, and reusable KPI widgets to display summary metrics.
- **Inspection flow:** a feature component uses dynamic form renderers, offline draft persistence, and permission-aware actions to support field operators.
- **Dashboard launch:** a tenant-specific dashboard loads runtime widget configs, theme tokens, and RTL-safe components for fast mobile access.

## 40. Final Frontend Enforcement Checklist
- frontend domains remain isolated
- components remain reusable
- state ownership is explicit
- React Query manages server state
- offline rendering is supported
- runtime theming is dynamic
- no god components are allowed
- no cross-domain private imports
- no direct fetches in components
- no deep prop drilling across domains
