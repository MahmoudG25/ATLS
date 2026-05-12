# DESIGN SYSTEM

## Purpose
Define the master visual design system for ATLS, establishing mobile-first, RTL-native, and white-label capable UI/UX principles for agricultural ERP operations. This document establishes the rules for semantic tokens, component patterns, accessibility, and AI-safe design constraints.

## Scope
Covers design philosophy, semantic tokens, typography, spacing, color system, component patterns, mobile-first behavior, RTL rendering, accessibility, dark/light mode, white-label constraints, and animation rules.

## Current Status
- [x] Not Started
- [ ] In Progress
- [ ] Completed

## Dependencies
- `docs_v2/01_ARCHITECTURE/FRONTEND_ARCHITECTURE.md`
- `docs_v2/04_DYNAMIC_ENGINES/DYNAMIC_THEME_ENGINE.md`
- `docs_v2/07_AI_AGENT/AI_DEVELOPMENT_RULES.md`

## Notes
This is the master visual design system document for ATLS. Design prioritizes mobile-first UX, RTL-native rendering, and semantic tokens. No arbitrary styling allowed; all design uses token-driven consistency.

## Last Updated
2026-05-12

---

## 1. Design Philosophy
ATLS design delivers mobile-app feeling with enterprise reliability, prioritizing field usability, RTL-native rendering, and white-label adaptability for agricultural workflows.

## 2. Agricultural ERP UX Principles
Principles: operational efficiency, field-readability, touch-first interactions, offline resilience, and hierarchy-aware information display.

## 3. Mobile-App Feeling Strategy
Strategy: app-like navigation, gesture support, bottom sheets, and immersive experiences optimized for handheld devices.

## 4. Semantic Design Token System
Tokens: semantic names (primary-color, text-heading) mapped to values. Tokens enable runtime theming and consistency.

## 5. Color System Architecture
Colors: primary, secondary, neutral, status. System supports contrast ratios and accessibility.

## 6. Status Color Rules
Rules: success (green), error (red), warning (yellow), info (blue). Rules ensure consistent status communication.

## 7. Typography System
Typography: scales for headings, body, captions. System supports readability in sunlight and on low-end devices.

## 8. Arabic Typography Rules
Rules: proper Arabic font stacks, ligature support, RTL alignment. Rules ensure perfect Arabic rendering.

## 9. Spacing System
Spacing: scale-based (space-1 to space-10). System ensures consistent margins and padding.

## 10. Radius System
Radius: scale for borders (radius-sm, radius-lg). System supports rounded corners for touch-friendly UI.

## 11. Shadow System
Shadows: elevation levels (shadow-1 to shadow-5). System indicates depth and hierarchy.

## 12. Elevation Hierarchy
Hierarchy: base, raised, overlay. Hierarchy uses shadows for layered UI.

## 13. Iconography Rules
Icons: consistent style, RTL-aware flipping. Rules support touch targets and readability.

## 14. Button System
Buttons: primary, secondary, ghost variants. System ensures large touch targets.

## 15. Input System
Inputs: text, select, checkbox. System supports validation states and accessibility.

## 16. Form Visual Standards
Standards: grouped fields, clear labels, error states. Standards prioritize usability.

## 17. Card System
Cards: content containers with shadows. System supports KPI and data display.

## 18. KPI Card Architecture
KPI cards: large numbers, trends, icons. Architecture ensures scannability.

## 19. Dashboard Visual Rules
Rules: grid layouts, widget consistency. Rules support mobile stacks.

## 20. Table & Data Grid Visual Rules
Rules: zebra stripes, sortable headers. Rules ensure data readability.

## 21. Modal & Dialog Rules
Rules: centered, overlay backgrounds. Rules support mobile bottom sheets.

## 22. Drawer & Bottom Sheet Rules
Rules: slide-in animations, swipe gestures. Rules optimize mobile UX.

## 23. Navigation Visual Rules
Rules: bottom tabs, clear icons. Rules support field navigation.

## 24. Bottom Navigation UX
UX: 4-5 tabs, large targets. UX ensures quick access.

## 25. Mobile Header System
Headers: title, actions, back button. System supports RTL.

## 26. Empty State UX
UX: illustrations, clear messages. UX guides users.

## 27. Loading State UX
UX: skeletons, progress indicators. UX prevents confusion.

## 28. Error State UX
UX: clear errors, recovery actions. UX ensures usability.

## 29. Notification & Toast UX
UX: non-intrusive, swipe-dismiss. UX supports alerts.

## 30. RTL Visual Rendering Rules
Rules: right-aligned text, mirrored icons. Rules ensure native RTL.

## 31. Accessibility & Contrast Rules
Rules: WCAG compliance, keyboard navigation. Rules ensure inclusivity.

## 32. Dark Mode Visual Rules
Rules: dark backgrounds, light text. Rules support low-light usage.

## 33. Light Mode Visual Rules
Rules: light backgrounds, dark text. Rules support sunlight readability.

## 34. White-Label Design Constraints
Constraints: logo placement, brand colors. Constraints maintain consistency.

## 35. Animation & Motion UX Rules
Rules: subtle transitions, performance-aware. Rules avoid heavy animations on low-end devices.

## 36. Offline UX Indicators
Indicators: offline badges, sync status. Indicators ensure awareness.

## 37. AI Safety Rules
AI must not:
- use random spacing
- apply arbitrary colors
- create desktop-first layouts
- make tiny touch targets
- design inconsistent cards
- structure forms poorly
- choose unreadable typography
- ignore contrast
- add heavy animations

## 38. Forbidden UI/UX Anti-Patterns
- small buttons
- low contrast
- desktop layouts
- inconsistent spacing
- arbitrary colors
- unreadable text
- heavy animations
- non-RTL aware
- inaccessible components

## 39. Real-World Agricultural UX Scenarios
- **Field engineer:** large touch targets for gloves, sunlight-readable text, offline indicators.
- **Supervisor:** KPI cards for quick scanning, bottom navigation for workflows.
- **Warehouse worker:** tables for inventory, error states for corrections.

## 40. Future Design System Evolution
- Advance AI-driven design recommendations.
- Implement adaptive layouts.
- Expand accessibility features.
- Integrate voice UI.
- Enhance offline UX.

## Notes
Important notes placeholder.

## Last Updated
2026-05-12
