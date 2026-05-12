# FRONTEND ARCHITECTURE

## Purpose
Define the ATLS master frontend execution architecture for the enterprise agricultural platform. This document establishes the frontend philosophy, modular domain structure, styling and UI governance, state boundaries, offline-aware behavior, and performance rules.

## Scope
Covers React + TypeScript execution, app shell design, routing, component ownership, dynamic engines, PWA behavior, offline UX, white-label theming, RTL support, and observability for the ATLS frontend stack.

## Current Status
- [x] Not Started
- [ ] In Progress
- [ ] Completed

## Dependencies
- `docs_v2/01_ARCHITECTURE/STATE_MANAGEMENT.md`
- `docs_v2/01_ARCHITECTURE/OFFLINE_STRATEGY.md`
- `docs_v2/01_ARCHITECTURE/API_ARCHITECTURE.md`
- `docs_v2/01_ARCHITECTURE/EVENT_SYSTEM.md`
- `docs_v2/01_ARCHITECTURE/BACKEND_ARCHITECTURE.md`
- `docs_v2/07_AI_AGENT/AI_DEVELOPMENT_RULES.md`

## Notes
The frontend architecture is the execution contract for ATLS UI teams; it must preserve modularity, domain isolation, and platform resilience.

## Last Updated
2026-05-12

---

## 1. Frontend Philosophy
ATLS frontend architecture is designed around resilient, user-centric delivery in agricultural environments. It prioritizes domain-oriented modularity, mobile-first usability, offline awareness, and a clear separation between presentation, state, and business intent.
- UI components are composition-first and domain-local.
- Server state is owned by React Query.
- Client state is minimal and managed only where necessary.
- The frontend must support dynamic engine-driven behavior without sacrificing predictability.

## 2. Mobile-First Architecture
- Design must begin with mobile screens and progressively enhance for desktop dashboards.
- Touch interactions, screen space economy, and offline operation must be first-class concerns.
- Layouts use responsive breakpoints that emphasize field workflows and mobile form ergonomics.
- Mobile performance constraints dictate lower memory use, lighter bundles, and reduced prefetching.

## 3. Offline-Aware Frontend Design
- Offline awareness is built into the app shell, routing, and data components.
- The UI must provide explicit offline indicators, retry affordances, and graceful degradation.
- All write operations must support queued execution and optimistic local state.
- Offline behavior is not an afterthought; it is required for core workflows and field usability.

## 4. Application Shell Architecture
- The app shell is the root execution layer and manages shared providers, routing, theme, auth, and offline state.
- It should remain thin, delegating domain rendering to feature modules.
- The shell initializes React Query, Zustand, theme engine, internationalization, and PWA runtime support.
- Global providers must not contain business logic or domain-specific render decisions.

## 5. Domain-Oriented Frontend Structure
- The frontend is organized by domain/feature boundaries, not by technical layers alone.
- Each domain folder contains its own pages, components, hooks, and service adapters.
- Cross-domain imports are restricted to shared utilities and interface contracts.
- Domain modules communicate through API hooks, query keys, and event-driven UI actions.

## 6. Feature-Based Modular Architecture
- Features are self-contained and own their presentation, data access, and UI composition.
- Shared components are generic and reusable, not domain-specific.
- Feature modules should expose clear public hooks and abstractions for integration.
- Avoid feature-level god components that render unrelated domain concerns.

## 7. Route Architecture
- Routing is feature-scoped and reflects domain structure.
- Use nested routes for layout inheritance and feature shells.
- Route definitions should be declarative and kept close to the domain module.
- Avoid monolithic route files that mix unrelated feature paths.

## 8. Protected Route Strategy
- Protected routes are enforced at the routing layer using auth state from Zustand and permission metadata.
- Redirects and guard logic belong in route wrappers or route provider modules, not in page components.
- Protected route failures should render meaningful access-denied or sign-in flows, not blank pages.
- Auth state drives route availability, while server state remains in React Query.

## 9. Layout System Architecture
- Layouts are composed from generic structural primitives and domain-specific content slots.
- Base layouts handle scaffolding, navigation, top bars, and footers.
- Feature layouts provide context-specific framing without duplicating base shell logic.
- Layouts must support both mobile and dashboard form factors seamlessly.

## 10. Navigation Architecture
- Navigation state is lightweight and managed through route parameters, React Router state, and limited Zustand preferences.
- The navigation system must support mobile drawers, breadcrumb paths, and white-label menu variants.
- Do not store domain navigation state in global stores.
- Navigation should adapt to RTL automatically and preserve active route semantics.

## 11. Responsive Architecture
- Responsive behavior is implemented through Tailwind utility classes, semantic design tokens, and layout components.
- UI should adapt fluidly to phone, tablet, and large-screen dashboard breakpoints.
- Hide or collapse non-essential UI on mobile.
- Responsive rules must preserve input accessibility and offline affordances.

## 12. Component Ownership Rules
- Components belong to the domain or shared library where they are authored.
- Domain components may consume shared primitives; shared components must never depend on specific domains.
- Ownership is expressed through folder boundaries, naming, and public exports.
- Components should not import from other feature domains except through approved shared interfaces.

## 13. Shared Component Rules
- Shared components are generic building blocks with no domain behavior.
- They implement design system primitives, layout utilities, and accessibility wrappers.
- Avoid embedding business logic inside shared components.
- Shared components may use shadcn/ui and Radix primitives but not modify them directly.

## 14. shadcn/ui Governance
- `shadcn/ui` components are treated as design system primitives and consumed, not altered.
- Customization occurs through wrappers, theming, and composition.
- Do not modify upstream shadcn source files; preserve upgradeability.
- Use shadcn components for consistent interface patterns, not as a replacement for domain-specific logic.

## 15. Radix Primitive Governance
- Radix primitives are the accessibility foundation for complex interactions.
- Use Radix for modals, tooltips, dropdowns, tabs, and other interactive patterns.
- Wrap Radix primitives in domain-safe components to encapsulate behavior and styling.
- Do not bypass Radix APIs with custom DOM hacks or hidden imperative state.

## 16. TailwindCSS Governance
- Tailwind is the styling engine, but use semantic tokens and design tokens whenever possible.
- Avoid hardcoded colors, direct utility duplication, and inline styles for themeable values.
- Encapsulate utility patterns in reusable classes and component wrappers.
- Respect white-label theming by using token-based values instead of fixed palette references.

## 17. Framer Motion Governance
- Use Framer Motion for motion that enhances usability and clarifies state transitions.
- Motion should support RTL by reversing directional animations where appropriate.
- Keep animation definitions declarative and avoid motion inside business logic.
- Motion should be additive and not required for core functionality.

## 18. React Query Integration
- React Query owns all server-state synchronization.
- Use React Query hooks for fetching, caching, background refresh, invalidation, and optimistic mutation.
- Do not use direct fetch logic inside components.
- Keep query key definitions consistent and feature-scoped.

## 19. Zustand Boundaries
- Zustand is limited to auth/session metadata, theme preferences, navigation settings, and lightweight UI flags.
- It must not contain server-side data, read model caches, or large lists.
- Zustand state should remain minimal and isolated from React Query caches.
- Use Zustand for transient client state that is not appropriate for query management.

## 20. Form Architecture
- Forms use controlled inputs and form libraries for validation and state management.
- Load initial values from React Query and submit through mutation hooks.
- Form state is local to the form instance, with draft persistence handled separately.
- Avoid storing full form payloads in global state.

## 21. Dynamic Form Rendering
- Dynamic forms are driven by runtime schema data and field metadata.
- Use a form engine to render fields, validations, and conditional blocks.
- Dynamic field definitions must be normalized and tenant-aware.
- Offline dynamic forms must continue to render and validate using persisted schema and draft state.

## 22. Table & Data Grid Strategy
- Data grids are feature-specific components built on shared, generic table primitives.
- Use virtualization for large dataset rendering.
- Data grids should load rows through cursor/paginated React Query queries.
- Avoid giant monolithic grid components; keep each grid composable and domain-scoped.

## 23. Dashboard Widget Architecture
- Dashboards are composed from independent widgets and panels.
- Widgets fetch their own server state and remain self-contained.
- Dashboard layout provides orchestration without embedding domain data logic.
- Avoid large dashboard pages with unbounded render trees.

## 24. Theme Engine Integration
- Theme engine is runtime-configurable and drives colors, spacing, and typography through Tailwind tokens.
- White-label themes are applied dynamically and isolated per tenant or brand.
- Theme state is stored in Zustand and read by the shell provider.
- Do not hardcode theme values in components; use semantic tokens.

## 25. White-Label Frontend Isolation
- White-label customization is managed as a runtime theme and configuration layer.
- UI branding, logos, palettes, and layout variants are isolated by tenant context.
- White-label data must not leak across deployments or tenant instances.
- The shell applies branding without altering domain logic.

## 26. RTL Architecture
- RTL support is native and built into layout, navigation, and motion.
- UI components should mirror direction-sensitive behavior based on locale.
- Use CSS logical properties and RTL-aware variants for layout.
- Validate RTL rendering in automated regression suites.

## 27. Accessibility Rules
- Accessibility is mandatory for all UI components and pages.
- Follow WCAG standards for keyboard navigation, focus management, labels, and contrast.
- Use Radix primitives and semantic markup to support assistive technologies.
- Accessibility should be enforced at the component and route level.

## 28. Offline UI Rules
- The UI must indicate offline status and queued operations clearly.
- Offline actions should be possible without blocking navigation or data entry.
- Provide users with retry controls and sync progress feedback.
- Offline UI behavior must remain consistent across mobile and desktop.

## 29. Error Boundary Strategy
- Use error boundaries around feature modules and the application shell.
- Errors should degrade gracefully and preserve unaffected UI.
- Error boundaries should report diagnostic context and allow user recovery.
- Avoid burying errors inside generic fallback screens.

## 30. Loading State Architecture
- Loading state is local to queries and components.
- Use React Query status flags for server data loading.
- Reserve global loading indicators for app-wide transitions only.
- Keep loading feedback informative and unobtrusive.

## 31. Lazy Loading Strategy
- Lazy load feature modules and heavy UI dependencies.
- Use route-based code splitting for large dashboards and admin sections.
- Keep the initial bundle small to improve mobile startup performance.
- Load non-critical UI assets only when needed.

## 32. Bundle Splitting Strategy
- Apply meaningful bundle boundaries around domain features and widget collections.
- Avoid single-file route components that import the entire app.
- Use shared chunking for common utilities and design system primitives.
- Monitor bundle size growth and prioritize critical path assets.

## 33. Frontend Performance Rules
- Prioritize time-to-interactive, input responsiveness, and visual stability.
- Minimize render passes and avoid expensive synchronous layout work.
- Use virtualization for large lists and dashboards.
- Reduce unnecessary re-renders by isolating component state.

## 34. PWA Frontend Rules
- PWA support is required for offline capability and mobile resilience.
- Ensure service worker registration is controlled and tenant-safe.
- Cache shell assets, offline fallbacks, and critical static resources.
- Keep PWA behavior consistent with offline architecture and sync rules.

## 35. Media Rendering Rules
- Media rendering should support lazy loading, low-bandwidth fallbacks, and thumbnails.
- Avoid rendering large media assets until needed.
- Keep media previews lightweight and tenant-isolated.
- Do not store media blobs in Zustand or global stores.

## 36. Frontend Security Rules
- Do not expose sensitive tenant or auth information in client-side logs.
- Protect runtime configuration and theme data from cross-tenant leakage.
- Use secure storage for auth tokens and offline session state.
- Avoid direct DOM access or insecure third-party UI hacks.

## 37. Frontend Observability
- Capture page load, route transitions, query failures, and performance metrics.
- Use structured telemetry for errors and slow UI pathways.
- Ensure observability respects tenant privacy and white-label isolation.
- Make frontend health visible to platform operations teams.

## 38. AI Safety Rules
AI-assisted frontend development must forbid:
- giant global stores with server data
- cross-domain component imports outside approved shared contracts
- direct fetch logic in components or effects
- inline business logic in UI components
- hardcoded color values or themes
- modifying shadcn source primitives directly
- route-level god pages that render unrelated domains
- giant dashboard components that break modular ownership

## 39. Forbidden Frontend Anti-Patterns
- fat UI components that manage business rules and server calls
- shared components with domain-specific knowledge
- global state stores containing query data
- direct styling hacks that bypass Tailwind tokens
- using shadcn primitives as a custom component library rather than composition base
- ignoring RTL in layout and motion

## 40. Real-World Agricultural UX Scenarios
- **Field inspection on mobile:** a technician records crop observations in a compact form that works offline, syncs when connectivity returns, and stays responsive throughout.
- **Remote dashboard review:** a supervisor accesses cached summary panels over weak networks, with widgets loading independently and visually indicating stale data.
- **White-label farm portal:** a tenant sees runtime branding and theming applied consistently across pages without changing domain feature behavior.
- **Seasonal planning flow:** planners use dynamic forms and conditional fields to adapt to crop cycles, with offline draft persistence and schema-driven rendering.
- **Equipment dispatch:** operators navigate task flows with responsive layout, offline-aware route guards, and minimal component state.

## 41. Future Frontend Evolution Strategy
- Continue evolving runtime theming and white-label capabilities.
- Expand dynamic engine support for form, dashboard, and workflow generation.
- Improve PWA resilience and background sync integration.
- Explore native mobile bridge patterns for deeper offline and hardware integration.
- Refine frontend observability to support large-scale agricultural operations.
