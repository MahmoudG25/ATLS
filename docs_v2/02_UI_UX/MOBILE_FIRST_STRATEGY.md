# MOBILE FIRST STRATEGY

## Purpose
Define the ATLS mobile-first experience architecture, focusing on handheld agricultural workflows, offline resilience, RTL-native rendering, and low-end Android performance. This document establishes the rules for mobile navigation, onboarding, field data entry, camera-first workflows, and AI-safe mobile UX.

## Scope
Covers mobile-first philosophy, thumb-zone UX, bottom navigation, offline mobile workflows, performance optimization, mobile forms, field usability, sunlight readability, and AI safety constraints.

## Current Status
- [x] Not Started
- [ ] In Progress
- [ ] Completed

## Dependencies
- `docs_v2/02_UI_UX/DESIGN_SYSTEM.md`
- `docs_v2/01_ARCHITECTURE/FRONTEND_ARCHITECTURE.md`
- `docs_v2/01_ARCHITECTURE/OFFLINE_STRATEGY.md`
- `docs_v2/04_DYNAMIC_ENGINES/DYNAMIC_FORM_ENGINE.md`
- `docs_v2/04_DYNAMIC_ENGINES/DASHBOARD_CONFIGURATION_ENGINE.md`
- `docs_v2/04_DYNAMIC_ENGINES/ROLE_PERMISSION_ENGINE.md`
- `docs_v2/07_AI_AGENT/AI_DEVELOPMENT_RULES.md`

## Notes
This is the master mobile-first UX strategy for ATLS. Mobile usability is the primary experience, with offline state visibility, large touch targets, and lean workflows for field operators on low-end devices.

## Last Updated
2026-05-12

---

## 1. Mobile-First Philosophy
ATLS mobile-first design treats handheld devices as the primary experience. The platform is optimized for field operations, delivering fast entry, one-hand access, and dependable offline behavior.

## 2. Why Mobile-First ERP
Mobile-first ERP supports work in fields, warehouses, and remote locations where desktop access is unavailable. It enables real-time decision-making, reduces paper processes, and supports agricultural teams on the move.

## 3. Agricultural Field UX Principles
Principles: prioritize rapid workflows, minimize cognitive load, surface relevant operational context, keep interactions touch-friendly, and maintain readability in bright light.

## 4. One-Hand Usage Strategy
Design controls within thumb reach and keep primary actions near the bottom of the screen. Limit deep navigation and support back actions that are easy to execute with one hand.

## 5. Thumb-Zone Layout Rules
Place primary actions and frequently used controls in the lower two-thirds of the screen. Use large tap targets and avoid placing critical buttons at the top edge.

## 6. Bottom Navigation Architecture
Bottom navigation is the default pattern. Primary sections are accessible with a single tap and support immediate context switching without deep nesting.

## 7. Mobile Header Strategy
Headers are compact with clear titles, back controls, and context actions. Use sticky headers sparingly to preserve vertical space.

## 8. Floating Action Button Rules
FABs are reserved for the most important mobile actions, such as capture evidence, start inspection, or add a record. FABs are positioned for thumb access and hidden when not contextual.

## 9. Mobile Drawer Rules
Drawers and slide menus are secondary navigation. They must be shallow, accessible from the bottom or side, and avoid hiding essential workflow actions.

## 10. Drill-Down Navigation Strategy
Use hierarchical drill-down flows instead of wide menus. Present parent-to-child navigation as stacked screens with clear back affordances.

## 11. Mobile Dashboard UX
Mobile dashboards are vertical, card-based summaries with quick access to operational insights. Dashboards avoid dense tables and focus on scannable KPIs and action cards.

## 12. KPI Mobile Rendering Rules
KPI cards use large numbers, high-contrast labels, and minimal text. They must be legible outdoors and remain understandable at a glance.

## 13. Mobile Card Patterns
Cards are touch-friendly containers with ample padding, clear hierarchy, and single-tap affordances. Use cards for summaries, status, and navigation entry points.

## 14. Mobile Table Alternatives
Replace wide tables with stacked lists, expandable detail rows, and summary cards. Data grids are used only when screen width permits.

## 15. Mobile Form UX
Forms are narrow, single-column flows with clear labels and large inputs. Avoid side-by-side fields; use progressive disclosure for complex forms.

## 16. Multi-Step Form Strategy
Break long forms into small, contextual steps. Use progress indicators, save states, and allow users to complete portions offline.

## 17. Quick Data Entry UX
Provide presets, scan/capture shortcuts, autocomplete, and default values for fast entry. Minimize typing and favor tap-friendly controls.

## 18. Camera-First Workflow Rules
Support camera capture as a primary workflow for evidence, inspections, and maintenance logs. Provide immediate preview, retry, and annotation flows.

## 19. File Upload Mobile UX
File uploads use clear progress, resumable transfer, and retry controls. Present upload state prominently and keep uploads out of the critical path.

## 20. Offline Mobile UX
Offline mode is explicit and visible. Display offline badges, sync status, and data freshness indicators on every relevant screen.

## 21. Sync Status Indicators
Sync indicators show pending uploads, last sync time, and connectivity state. Status must be visible but not intrusive.

## 22. Background Sync UX
Background sync runs quietly with notifications only for failures or conflicts. Users should not be interrupted for routine sync events.

## 23. Conflict Resolution UX
Resolve conflicts with clear messaging, compare values side-by-side, and surface safe recovery choices. Avoid burying conflict details behind multiple taps.

## 24. Mobile Error Recovery UX
Present errors with actionable recovery paths. Use inline help, retry buttons, and contextual guidance for field-level failures.

## 25. Mobile Empty State UX
Empty states provide clear next steps, possible actions, and example data. Use concise copy and avoid dense visuals.

## 26. Gesture Interaction Rules
Use gestures for common mobile interactions (swipe-to-dismiss, pull-to-refresh), but keep core workflows accessible via buttons. Do not rely on hidden gestures.

## 27. Pull-To-Refresh Rules
Pull-to-refresh is supported for data refresh, with visible feedback and a clear refresh state. Use it only where users expect manual updates.

## 28. Mobile Search UX
Search is front-and-center for operational data. Provide filters, recent searches, and fast result rendering.

## 29. Mobile Filter UX
Filters are accessible via bottom sheets or inline collapsible panels. Keep filters simple and contextual.

## 30. Mobile Notification UX
Notifications are unobtrusive, toast-based, and dismissible. Use persistent banners only for critical sync or offline alerts.

## 31. Sunlight Readability Rules
Use high-contrast text, bold weights, and simple surfaces. Avoid low-contrast backgrounds and translucent overlays in bright environments.

## 32. Low-End Android Optimization Rules
Optimize layout complexity, reduce animation work, and minimize memory usage. Use lightweight rendering and avoid large asset payloads.

## 33. Mobile Performance Constraints
Limit component depth, lazy-load screens, and avoid expensive render cycles. Aim for smooth interactions on low-end hardware.

## 34. Battery Usage Constraints
Minimize background polling and heavy CPU work. Prefer event-based sync and defer noncritical tasks on low battery.

## 35. RTL Mobile Rendering Rules
RTL is native, with mirrored layouts, icons, and navigation patterns. Ensure Arabic text and UI flows feel natural and consistent.

## 36. Accessibility Rules
Support screen readers, large text, and reachable controls. Ensure all mobile interactions meet accessibility standards.

## 37. AI Safety Rules
AI must not:
- produce desktop-first layouts
- rely on hover interactions
- use tiny buttons
- create wide desktop-style tables
- use heavy animations
- build modal-heavy workflows
- design multi-column mobile forms
- hide offline state
- create complex nested navigation

## 38. Forbidden Mobile UX Anti-Patterns
- desktop-first pages
- hover-dependent controls
- tiny touch targets
- dense tables on phones
- excessive modal depth
- hidden offline status
- multi-column forms
- heavy animated transitions
- low-contrast text

## 39. Real-World Agricultural Mobile Scenarios
- **Harvest capture:** a field operator uses bottom navigation to open camera-first evidence capture, attaches photos, and submits offline while still seeing sync status.
- **Equipment repair:** a technician navigates drill-down maintenance tasks with one hand, uses large buttons for statuses, and records videos in low-bandwidth conditions.
- **Warehouse count:** a worker scans inventory, uses quick entry fields and toggle-driven workflows, and reviews KPI summaries on a mobile dashboard.

## 40. Future Mobile Evolution
- Evolve toward adaptive mobile layouts that learn common field workflows.
- Add voice-assisted data capture for hands-busy scenarios.
- Improve offline predictive sync and conflict avoidance.
- Expand gesture-based shortcuts for frequent actions.
- Enhance low-end device performance with progressive rendering and asset compression.
