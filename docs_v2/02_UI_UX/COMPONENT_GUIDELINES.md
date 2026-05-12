# COMPONENT GUIDELINES

## Purpose
Define the master component governance architecture for ATLS, ensuring reusable, composable, mobile-first, RTL-native, and theme-aware UI components built with React, TailwindCSS, shadcn/ui, Radix UI, and Framer Motion.

## Scope
Covers component philosophy, hierarchy, reusable patterns, separation of concerns, form and dashboard component architecture, animation standards, accessibility, AI safety, and enforcement rules.

## Current Status
- [x] Not Started
- [ ] In Progress
- [ ] Completed

## Dependencies
- `docs_v2/02_UI_UX/DESIGN_SYSTEM.md`
- `docs_v2/02_UI_UX/THEME_ENGINE.md`
- `docs_v2/02_UI_UX/MOBILE_FIRST_STRATEGY.md`
- `docs_v2/02_UI_UX/RTL_SYSTEM.md`
- `docs_v2/04_DYNAMIC_ENGINES/DYNAMIC_THEME_ENGINE.md`
- `docs_v2/04_DYNAMIC_ENGINES/ROLE_PERMISSION_ENGINE.md`
- `docs_v2/01_ARCHITECTURE/FRONTEND_ARCHITECTURE.md`
- `docs_v2/07_AI_AGENT/AI_DEVELOPMENT_RULES.md`

## Notes
This is the master UI component governance document for ATLS. Components must support runtime theming, RTL, mobile-first rendering, composability, and separation of UI from business logic.

## Last Updated
2026-05-12

---

## 1. Component Philosophy
ATLS components are built for reuse, composition, and clarity. Components should be predictable, theme-aware, and free of business logic.

## 2. Mobile-First Component Principles
Design components for touch-first mobile usage. Components must render responsively and prioritize large tap targets.

## 3. Component Hierarchy Architecture
Organize components into atomic, composite, and page-level layers. Maintain clear boundaries between low-level UI primitives and domain-specific widgets.

## 4. Atomic vs Composite Components
Atomic components expose small, reusable primitives. Composite components assemble atomics into richer UI patterns without embedding business rules.

## 5. Base UI Component Rules
Base UI components use semantic props, Tailwind utility composition, and theme tokens. They should be small, stateless, and generic.

## 6. Business Component Rules
Business components encapsulate domain display logic and compose lower-level UI elements. They should remain free of direct data fetching and API calls.

## 7. Domain Widget Rules
Domain widgets are reusable across features and support tenant-aware rendering. Widgets accept data via props and emit events rather than own business workflows.

## 8. Page Composition Rules
Pages compose components and orchestrate state. Page components coordinate data loading, layout, and event handlers while delegating rendering to reusable UI components.

## 9. Smart vs Dumb Component Strategy
Smart components manage state and orchestration. Dumb components focus on rendering and are reusable across contexts.

## 10. Separation of Concerns Rules
UI layers remain separate from business logic and domain services. Components should not contain domain decisions or fetch side effects.

## 11. State Ownership Rules
State belongs to feature containers, pages, or hooks. Presentational components receive state via props and callbacks.

## 12. Props Design Rules
Props should be explicit, minimal, and semantic. Avoid prop drilling by using context only for cross-cutting UI concerns, not business data.

## 13. Component Reusability Rules
Build components to be reusable in multiple domains. Avoid hardcoding labels, colors, and layouts within reusable components.

## 14. Composition Over Inheritance Rules
Favor component composition over inheritance. Compose smaller primitives into richer UI patterns rather than extending component behavior.

## 15. Component Naming Rules
Use descriptive names aligned with function and responsibility. Name primitives clearly (e.g., `Button`, `InputField`, `KpiCard`) and domain composites with context.

## 16. Folder Structure Rules
Organize components by layer: `components/ui`, `components/widgets`, `components/pages`, `components/domain`. Keep shared primitives separate from domain-specific widgets.

## 17. Form Component Architecture
Form components are built from atomic inputs, validation messages, and layout primitives. Forms use schema-driven patterns and do not embed business logic.

## 18. Input Component Standards
Input components support labels, helper text, validation states, and theme tokens. They use semantic spacing and are accessible by default.

## 19. Validation Rendering Rules
Validation errors are displayed inline and adjacent to the affected input. Validation UI is handled by form components, not business components.

## 20. Modal & Sheet Component Rules
Modals and sheets are used for transient tasks. They are theme-aware, accessible, and avoid blocking primary navigation flows.

## 21. Table Component Rules
Tables are used only when necessary. For mobile, prefer responsive lists, expandable cards, or simplified table alternatives.

## 22. Card Component Rules
Cards are consistent containers with theme-driven padding, radius, and shadows. Use cards to group related information and actions.

## 23. Dashboard Widget Standards
Dashboard widgets are isolated, lazy-loaded, and configurable. Widgets should not assume global state beyond explicit props or UI context.

## 24. Empty State Component Rules
Empty states provide clear messages, actions, and optional guidance. They should be reusable across domains.

## 25. Loading State Component Rules
Loading states use skeletons or lightweight spinners. Loading components should not obscure the entire screen unnecessarily.

## 26. Error State Component Rules
Error states are recoverable and actionable. Components should isolate failures so one widget does not break the whole view.

## 27. Offline State Component Rules
Offline-aware components display connectivity and sync status clearly. They adapt behavior based on offline mode and persist input where appropriate.

## 28. Responsive Rendering Rules
Components must render across screen sizes using mobile-first breakpoints. Avoid hardcoded pixel values and prefer responsive utility classes.

## 29. RTL Component Rules
Components support RTL natively. Use logical CSS utilities, mirrored icons, and direction-aware layout patterns.

## 30. Theme-Aware Component Rules
Components consume theme tokens through CSS variables or semantic class mappings. Avoid inline style overrides and hardcoded design values.

## 31. Accessibility Rules
Components support keyboard navigation, ARIA attributes, focus management, and contrast requirements. Accessibility is built into component defaults.

## 32. Framer Motion Component Rules
Motion components use performance-safe presets and theme-aware easing. Animate only meaningful transitions and avoid layout jank.

## 33. Animation Boundaries
Animation belongs in UI components, not business logic. Keep motion confined to visual feedback and transitions, not state changes.

## 34. Performance Constraints
Keep component trees shallow and avoid expensive rendering. Use memoization, lazy loading, and virtualization where needed.

## 35. Lazy Loading Rules
Lazy load non-critical components and widgets. Defer heavy visuals until needed and prioritize initial mobile render speed.

## 36. Virtualization Rules
Use virtualization for long lists and tables. Avoid rendering large item sets in mobile views without virtualization.

## 37. AI Safety Rules
AI must not:
- create giant components
- use inline styles
- duplicate components
- drive prop drilling hell
- place business logic inside UI
- call APIs directly inside UI widgets
- hardcode layouts
- produce non-responsive rendering
- build deeply nested component trees

## 38. Forbidden Component Anti-Patterns
- huge monolithic components
- inline styling in reusable UI
- repeated component copies
- data fetching inside presentational components
- UI controlling business decisions
- fixed desktop-only layouts
- deep nested render trees
- theme-specific hardcoded styles

## 39. Real-World Agricultural UI Scenarios
- **Inspection widget:** a reusable media card shows evidence and status in mobile-friendly form, driven by props and lightweight UI state.
- **Harvest form:** a schema-driven input flow uses atomic fields, validation components, and progress steps for fast field entry.
- **Dashboard summary:** a composable KPI widget assembles small primitives into a role-aware card that updates on tenant theme changes.

## 40. Final Component Enforcement Checklist
- components are reusable and composable
- UI is separated from business logic
- components support runtime theming
- components support RTL natively
- mobile rendering is prioritized
- no inline styles in reusable components
- no duplicated component logic
- no direct API calls inside UI widgets
- component trees remain manageable
- theme and accessibility rules are enforced
