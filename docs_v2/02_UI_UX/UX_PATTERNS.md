# UX PATTERNS

## Purpose
Define the master UX interaction patterns for ATLS, delivering mobile-first, Arabic-first, operational, and offline-aware workflows. This document establishes rules for fast field interactions, low-friction reporting, hierarchy drill-down, and AI-safe UX.

## Scope
Covers UX philosophy, workflow standards, mobile interaction rules, offline patterns, form UX, reporting UX, hierarchy navigation, and accessibility.

## Current Status
- [x] Not Started
- [ ] In Progress
- [ ] Completed

## Dependencies
- `docs_v2/02_UI_UX/MOBILE_FIRST_STRATEGY.md`
- `docs_v2/02_UI_UX/RTL_SYSTEM.md`
- `docs_v2/02_UI_UX/NAVIGATION_SYSTEM.md`
- `docs_v2/02_UI_UX/DASHBOARD_SYSTEM.md`
- `docs_v2/02_UI_UX/COMPONENT_GUIDELINES.md`
- `docs_v2/02_UI_UX/DESIGN_SYSTEM.md`
- `docs_v2/01_ARCHITECTURE/OFFLINE_STRATEGY.md`
- `docs_v2/07_AI_AGENT/AI_DEVELOPMENT_RULES.md`

## Notes
This is the master UX patterns document for ATLS. UX is designed for fast operational workflows, one-handed mobile usage, weak networks, and hierarchy-aware farming operations.

## Last Updated
2026-05-12

---

## 1. UX Philosophy
ATLS UX is field-first and speed-oriented. It minimizes taps, reduces cognitive load, and keeps workflows simple for mobile agricultural teams.

## 2. Mobile-First UX Principles
Design for handheld screens, large tap targets, single-column flows, and fast access to the next action. Mobile usage is the primary experience.

## 3. Agricultural Operational UX
Operational UX aligns with farm, sector, stage, and enclosure workflows. It surfaces the right data and actions for field work without unnecessary navigation.

## 4. Touch-First Interaction Rules
Touch is primary. Controls are sized for fingers, spaced to prevent mis-taps, and avoid hover-only interactions.

## 5. One-Handed Usage Rules
Place primary actions within thumb reach and keep important controls near the bottom of the screen. Strive for short interaction paths and reachable navigation.

## 6. Outdoor Visibility UX
Use high contrast, bold typography, and clear visual hierarchy for outdoor readability. Avoid low-contrast or translucent surfaces that fail in bright light.

## 7. Low-End Device UX Rules
Keep animations subtle, reduce render complexity, and minimize large asset usage. UX must remain responsive on low-end Android hardware.

## 8. Offline UX Principles
Make offline state explicit and usable. Provide local data access, save drafts automatically, and surface sync readiness clearly.

## 9. Offline Sync UX
Sync UX shows pending changes, last successful sync, and offline duration. Background sync is seamless and only surfaces issues when intervention is needed.

## 10. Quick Action UX
Offer immediate actions through FABs, quick cards, and contextual buttons. Reduce the number of taps required to complete common tasks.

## 11. Contextual Action UX
Actions are tied to the current context and entity. Avoid global action menus for workflow-specific tasks.

## 12. Floating Action Button UX
FABs are used sparingly for primary workflows like capture, add, or start inspection. They are context-sensitive and placed for easy thumb access.

## 13. Bottom Sheet UX
Bottom sheets surface secondary details and actions without navigating away. They remain shallow and avoid hiding essential workflow controls.

## 14. Modal Usage Rules
Use modals only for brief confirmations or critical interruptions. Avoid modal-heavy workflows and never nest modals on mobile.

## 15. Drawer UX Rules
Drawers are secondary navigation and settings containers. They should be accessible but not required for primary workflows.

## 16. Reporting Workflow UX
Reporting workflows are streamlined with guided steps, presets, and quick capture modes. Reports focus on entering the minimum required evidence.

## 17. Daily Report UX
Daily reports are presented as short, repeatable flows with clear progress markers. They support offline drafting and quick submission.

## 18. Harvest Reporting UX
Harvest reports emphasize yield, quality, and evidence capture. UX supports camera-first workflows and conditional inputs.

## 19. Inventory Operation UX
Inventory workflows use fast counting, scanning, and status updates. Operations favor cards or list views over dense tables.

## 20. Equipment Workflow UX
Equipment workflows highlight maintenance status, issue logging, and inspection capture. UX provides direct access to equipment history and actions.

## 21. HR Workflow UX
HR workflows are focused on personnel tasks, approvals, and attendance. UX reduces form complexity and supports role-specific actions.

## 22. Dashboard Interaction UX
Dashboards present scannable KPIs, trends, and quick entry points. They serve as operational launch pads rather than static reports.

## 23. Drill-Down UX Patterns
Drill-down flows move users from summary cards to detail screens. Preserve context with clear breadcrumbs or back affordances.

## 24. Hierarchy Navigation UX
Hierarchy navigation reflects domain levels clearly. Users should understand farm → sector → stage → enclosure progression at a glance.

## 25. Search UX Patterns
Search is immediate and suggestion-driven. Results highlight matching entities and actionable workflows.

## 26. Filtering UX Patterns
Filters are compact, visible, and context-aware. Use chips, bottom sheets, and inline controls for mobile filtering.

## 27. Empty State UX
Empty states explain why content is missing and what to do next. They offer meaningful actions and avoid blank screens.

## 28. Loading State UX
Loading states use skeletons and placeholders to keep interfaces visible. Avoid full-screen loading on every transition.

## 29. Error Recovery UX
Errors are clear, actionable, and non-technical. Provide retry options and explain how to recover from failed operations.

## 30. Success Feedback UX
Provide immediate confirmation for completed actions. Use brief success messages and clear next steps.

## 31. Progressive Disclosure Rules
Show only necessary fields and actions. Reveal additional options as the user progresses to reduce overwhelm.

## 32. Form UX Standards
Forms are grouped, single-column, and broken into manageable sections. Use clear labels, required indicators, and inline help.

## 33. Validation UX Rules
Validation feedback is immediate, contextual, and easy to understand. Avoid vague errors and display them near the relevant field.

## 34. Media Upload UX
Media upload UX supports capture, preview, and retry. Upload state is visible and does not block the rest of the workflow.

## 35. Notification UX
Notifications are transient, informative, and dismissible. Use persistent banners only for ongoing offline or sync status.

## 36. Accessibility UX Rules
UX supports screen readers, large touch targets, focus visibility, and high contrast. Accessibility is integral, not optional.

## 37. RTL UX Rules
RTL UX is native with mirrored layouts, iconography, and navigation flow. All mobile patterns work seamlessly in RTL mode.

## 38. AI Safety Rules
AI must not:
- design desktop-first workflows
- generate modal spam
- overload users with multi-step tasks
- hide actions behind obscure gestures
- create tiny touch targets
- rely on hover-only interactions
- build deeply nested workflows
- create complex forms without grouping
- produce unclear error messaging

## 39. Forbidden UX Anti-Patterns
- desktop-only flows
- hidden critical actions
- modal-heavy UX
- deep nested menus
- tiny buttons
- hover-dependent interactions
- dense unreadable forms
- ambiguous status feedback
- non-visible offline state

## 40. Real-World Agricultural UX Scenarios
- **Field survey:** a field worker completes a harvest report with one-handed camera capture, quick toggles, and offline draft persistence.
- **Maintenance check:** an operator drills down from a sector dashboard to enclosure tasks, logs equipment issues, and uses large action buttons to mark completion.
- **Audit review:** an auditor navigates a role-aware dashboard, accesses recent activity, and switches language direction seamlessly.

## 41. Future UX Evolution
- Improve predictive task shortcuts based on user behavior.
- Expand voice-assisted entry for hands-busy workflows.
- Add smarter offline indicators and prefetching.
- Continue refining hierarchy-aware drill-down UX.
- Enhance adaptive flows for bilingual and white-label experiences.
