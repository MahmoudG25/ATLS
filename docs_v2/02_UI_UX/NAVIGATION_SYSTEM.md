# NAVIGATION SYSTEM

## Purpose
Define the master navigation experience architecture for ATLS, enabling mobile-first, hierarchical, role-aware, and runtime-configurable navigation across agricultural workflows. This document establishes the rules for bottom navigation, drill-down hierarchy, contextual actions, offline-aware routing, and RTL-native directionality.

## Scope
Covers navigation philosophy, hierarchy architecture, mobile navigation, drill-down UX, runtime rendering, search-driven entry points, permission-aware visibility, and navigation performance.

## Current Status
- [x] Not Started
- [ ] In Progress
- [ ] Completed

## Dependencies
- `docs_v2/02_UI_UX/DESIGN_SYSTEM.md`
- `docs_v2/02_UI_UX/MOBILE_FIRST_STRATEGY.md`
- `docs_v2/02_UI_UX/RTL_SYSTEM.md`
- `docs_v2/04_DYNAMIC_ENGINES/ROLE_PERMISSION_ENGINE.md`
- `docs_v2/04_DYNAMIC_ENGINES/DASHBOARD_CONFIGURATION_ENGINE.md`
- `docs_v2/01_ARCHITECTURE/FRONTEND_ARCHITECTURE.md`
- `docs_v2/01_ARCHITECTURE/OFFLINE_STRATEGY.md`
- `docs_v2/07_AI_AGENT/AI_DEVELOPMENT_RULES.md`

## Notes
This is the master navigation experience document for ATLS. Navigation is designed for mobile field operations, hierarchical domain traversal, permission-aware rendering, and runtime configuration.

## Last Updated
2026-05-12

---

## 1. Navigation Philosophy
ATLS navigation is mobile-first, context-driven, and hierarchy-aware. The system surfaces the right workflows quickly and keeps users oriented through drill-down paths.

## 2. Mobile-First Navigation Principles
Navigation prioritizes bottom navigation, large touch targets, and shallow interaction depth. Primary actions are reachable with one hand.

## 3. Agricultural Operational Navigation UX
Operational UX maps to farm workflows. Navigation reflects farm, sector, stage, and enclosure relationships and supports rapid task switching.

## 4. Navigation Hierarchy Architecture
Use a clear hierarchy with primary sections, secondary drill-downs, and contextual actions. The hierarchy is modeled on domain scope, not fixed menus.

## 5. Route Structure Philosophy
Routes mirror domain topology and remain stable. Route structure supports deep linking, breadcrumb paths, and predictable drill-down behavior.

## 6. Bottom Navigation Architecture
Bottom navigation is the primary mobile navigation pattern. It exposes core sections and adapts to tenant-specific modules.

## 7. Mobile Drawer Architecture
Drawers are secondary entry points for less-frequent workflows and settings. They are shallow, contextual, and accessible from the mobile chrome.

## 8. Sidebar Usage Rules
Sidebars are reserved for wider screens only. Mobile navigation does not rely on desktop sidebars.

## 9. Breadcrumb Navigation Rules
Breadcrumbs provide orientation in drill-down flows. They appear on mobile in compact form and maintain hierarchy context.

## 10. Drill-Down Navigation Strategy
Drill-down uses stacked screens and back affordances. Users move from summary to detail without losing their path.

## 11. Hierarchy Traversal UX
Hierarchy traversal is explicit and scoped. Users navigate farm → sector → stage → enclosure with clear parent references.

## 12. Farm/Sector/Stage/Enclosure Navigation
Navigation paths reflect farm-level, sector-level, stage-level, and enclosure-level workflows. Each level provides contextual actions and data entry points.

## 13. Contextual Navigation Rules
Contextual navigation surfaces actions related to the current object. Context menus and FABs adapt to the active domain scope.

## 14. Contextual FAB Navigation
FABs provide quick entry to the most important action in context, such as adding evidence or starting an inspection. They change with the current screen context.

## 15. Global Search Navigation
Global search is a primary navigation path. Search results link to domains, entities, and workflows directly.

## 16. Quick Access Navigation
Quick access cards and shortcuts surface frequent workflows. They are personalized based on role and recent activity.

## 17. Recently Visited Navigation
Recently visited screens are available for fast return. The system encourages quick re-entry to active workflows.

## 18. Favorites & Pinned Navigation
Favorites and pinned items provide shortcuts to important entities. They are tenant-specific and configurable.

## 19. Role-Based Navigation Visibility
Navigation items respect roles and permissions. Only authorized options render, preventing hidden-critical-action issues.

## 20. Feature Toggle Navigation Rules
Navigation adapts to enabled modules and feature toggles. Disabled modules are hidden from menus.

## 21. Tenant-Specific Navigation Rules
Tenant-specific navigation configurations load at runtime. Flows remain isolated and reflect tenant-enabled capabilities.

## 22. Dynamic Navigation Rendering
Navigation renders dynamically from configuration. The system supports runtime updates without redeploy.

## 23. Navigation State Persistence
Navigation state persists across sessions and offline restarts. Breadcrumbs, selected tabs, and last screens are restored.

## 24. Offline Navigation Behavior
Offline navigation still exposes cached routes and workflows. Users can traverse cached screens and data while offline.

## 25. Empty Navigation State UX
Empty navigation states provide clear guidance and actions. They explain why items are absent and how to enable modules or permissions.

## 26. Navigation Error Recovery
Navigation errors show friendly recovery options, such as reload, retry, or return to home. They avoid trapping users in dead ends.

## 27. Mobile Back Navigation Rules
Back navigation follows platform conventions and preserves history. The back stack is explicit for drill-down workflows.

## 28. Gesture Navigation Rules
Gestures complement buttons but never replace them. Swipes and edge gestures are optional and consistent with directionality.

## 29. Deep-Linking Rules
Deep links map to domain entities and workflows. They load the correct drill-down context and persist navigation state.

## 30. Notification-To-Screen Navigation
Notifications link directly to relevant screens. The transition is direct and preserves workflow context.

## 31. Dashboard Navigation UX
Dashboard navigation surfaces key workflows and KPI entry points. Dashboards link to detailed operational screens.

## 32. Cross-Domain Navigation Rules
Cross-domain navigation is unified and consistent. Users can move between farms, inventory, HR, and equipment without duplicated trees.

## 33. Runtime Navigation Configuration
Navigation configuration is loaded at runtime, allowing super admins to adjust available screens and modules dynamically.

## 34. RTL Navigation Rules
RTL navigation mirrors layout direction and menu ordering. Navigation components use logical properties and respond to `dir`.

## 35. Navigation Accessibility Rules
Navigation supports screen readers, focus management, and large touch targets. It adheres to accessibility best practices.

## 36. Navigation Performance Constraints
Navigation is optimized for low-end devices with minimal render overhead, lazy route loading, and light-weight menus.

## 37. AI Safety Rules
AI must not:
- build desktop-only sidebars
- use hover-dependent navigation
- bury critical actions
- duplicate navigation trees
- hardcode visibility based on roles
- create deep nested menus
- assume unlimited hierarchy depth
- render non-performant navigation paths

## 38. Forbidden Navigation Anti-Patterns
- desktop-first sidebars
- hidden critical actions
- hover-only menus
- hardcoded role visibility
- duplicated trees across domains
- unbounded recursive navigation
- stale cached navigation state

## 39. Real-World Agricultural Navigation Scenarios
- **Field inspection:** a technician uses bottom navigation to jump to inspections, drills down from farm to enclosure, and uses contextual FABs for evidence capture.
- **Warehouse transfer:** a manager switches quickly between inventory, harvest, and equipment screens using runtime navigation configuration and quick access shortcuts.
- **Audit review:** an auditor accesses tenant-specific reports and workflows through role-filtered navigation and recent items.

## 40. Future Navigation Evolution
- Evolve toward predictive navigation shortcuts.
- Add voice-triggered workflow entry.
- Support adaptive navigation based on field context.
- Expand cross-domain quick switchers.
- Improve offline-first route caching and prefetching.
