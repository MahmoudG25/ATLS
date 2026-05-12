# RTL SYSTEM

## Purpose
Define the RTL/LTR rendering system architecture for ATLS, with Arabic-first native directionality and future bilingual support. This document establishes the rules for logical styling, runtime direction switching, mirrored layouts, RTL-aware animations, and AI-safe directionality.

## Scope
Covers RTL philosophy, bidirectional architecture, runtime direction switching, logical CSS rules, layout mirroring, typography alignment, chart behavior, gesture rules, accessibility, and theme integration.

## Current Status
- [x] Not Started
- [ ] In Progress
- [ ] Completed

## Dependencies
- `docs_v2/02_UI_UX/DESIGN_SYSTEM.md`
- `docs_v2/02_UI_UX/MOBILE_FIRST_STRATEGY.md`
- `docs_v2/04_DYNAMIC_ENGINES/DYNAMIC_THEME_ENGINE.md`
- `docs_v2/07_AI_AGENT/AI_DEVELOPMENT_RULES.md`

## Notes
This is the master RTL/LTR rendering system document for ATLS. Directionality is a first-class platform concern and must be handled with logical properties, mirrored animation, and runtime language switching.

## Last Updated
2026-05-12

---

## 1. RTL Philosophy
ATLS is Arabic-first and RTL-native. Directionality is core to UX, not a peripheral stylesheet switch. The platform supports LTR as a fully compatible secondary mode.

## 2. Arabic-First UX Principles
UX prioritizes Arabic typography, right-side primary actions, and native RTL readability. Interfaces are designed to feel natural for Arabic users while preserving bilingual consistency.

## 3. Bidirectional Architecture Strategy
The architecture uses a bidirectional direction resolver, logical CSS tokens, and isolated direction-aware components. It enables runtime switching without layout breaks.

## 4. Runtime Direction Switching
Direction switches at runtime with a single state change. The engine updates `html[dir]` and re-resolves tokenized layouts, avoiding full page reloads.

## 5. HTML dir Management Rules
Use the `dir` attribute on the `html` element as the authoritative source of truth. Do not manage direction with inline style hacks or component-specific overrides.

## 6. Logical CSS Property Rules
Use logical properties only: `margin-inline-start`, `padding-inline-end`, `inset-inline-start`, `text-align:start`, and `float:inline-start`. Logical properties ensure bidirectional compatibility.

## 7. Forbidden Physical CSS Rules
Physical properties are forbidden: `margin-left`, `margin-right`, `padding-left`, `padding-right`, `left`, `right`, `text-align:left`, `text-align:right`, and fixed directional transforms.

## 8. Layout Mirroring Rules
Layouts mirror automatically with logical properties. Alignment, spacing, and flow should adapt based on `dir`, not explicit left/right values.

## 9. Grid & Flex RTL Rules
Grid and flex containers use logical alignment: `justify-content:start`, `justify-items:end`, `place-self:start`, `padding-inline`. Avoid using physical direction modifiers.

## 10. Typography Alignment Rules
Typography alignment uses `text-align:start` and `text-align:end`. Heading and body text align naturally based on the active direction.

## 11. Arabic Typography Rendering Rules
Use Arabic-capable font stacks, support ligatures, and ensure character shaping. Arabic typography must render clearly at large and small sizes.

## 12. Icon Mirroring Rules
Icons with directional meaning mirror automatically in RTL. Use mirrored icon assets or logical flip utilities rather than duplicated icon sets.

## 13. Navigation RTL Rules
Navigation controls mirror to the opposite side in RTL. Primary navigation remains accessible and thumb-reachable in both directions.

## 14. Drawer Direction Rules
Drawers open from the inline-start edge and close to inline-end. Drawer direction depends on natural layout flow, not specific left/right rules.

## 15. Bottom Navigation RTL Rules
Bottom navigation retains the same order semantics in RTL, with the first tab on the right and the last tab on the left. Reverse layout only for directional meaning.

## 16. Bottom Sheet RTL Rules
Bottom sheets remain anchored to the bottom and mirror internal flow based on `dir`. Content ordering follows RTL semantics.

## 17. Form Rendering RTL Rules
Forms render in a single column with inline start labels and controls. Field order and validation icons follow RTL-friendly patterns.

## 18. Validation Message RTL Rules
Validation messages align to `start` and support right-to-left punctuation. Error text should remain adjacent to the related field in RTL.

## 19. Table RTL Rendering Rules
Tables use logical cell padding and natural reading order. Expanders, row actions, and sort icons mirror according to direction.

## 20. KPI Card RTL Rules
KPI cards position labels and values using logical placement. Directional trend indicators flip in RTL while preserving meaning.

## 21. Dashboard RTL Rules
Dashboard tiles and widgets mirror structural flow. Layouts adapt using logical grid and stack properties, not physical coordinates.

## 22. Chart RTL Rendering Rules
Charts support RTL reading direction in axis ordering, labels, and tooltips. X-axis progress and data series orientation mirror appropriately.

## 23. Animation Mirroring Rules
Animations mirror for slide-in/out and directional motion. Use logical motion definitions such as `translateInline` instead of hardcoded transforms.

## 24. Framer Motion RTL Rules
Framer Motion variants use direction-aware parameters. Mirror animation values by inspecting `dir` rather than hardcoding left/right movement.

## 25. Gesture Direction Rules
Gestures adapt to directionality. Swipe, drag, and carousel interactions reverse when the interface is RTL.

## 26. Swipe Interaction Rules
Swipe-to-dismiss and swipe-to-action use inline direction. RTL swipes behave opposite to LTR swipes in a predictable manner.

## 27. RTL Mobile UX Rules
Mobile RTL UX keeps action placement and navigation intuitive. Touch areas remain large and reachable regardless of direction.

## 28. Offline Indicator RTL Rules
Offline indicators align with UI directionality and remain visible in the same relative corner. Use logical positioning for badges and banners.

## 29. Notification RTL Rules
Notifications stack and align based on `dir`. Toasts and banners should respect RTL padding and text flow.

## 30. Accessibility RTL Rules
Accessibility announcements use the active direction. Screen readers and focus order must reflect bidirectional structure.

## 31. Runtime Language Switching
Language switching updates direction and localized content dynamically. The UI should switch languages without breaking layout or state.

## 32. Theme Engine RTL Integration
Theme tokens include direction-aware variants. RTL integration ensures runtime themes preserve mirrored layout and motion rules.

## 33. Performance Constraints
RTL rendering must not add significant runtime cost. Use cached direction state and avoid expensive DOM recalculations.

## 34. Testing Strategy
Test RTL and LTR in parallel. Include screenshot comparisons, keyboard navigation, and gesture direction verification.

## 35. AI Safety Rules
AI must not:
- use margin-left/right or padding-left/right
- use left/right positioning
- use text-align:left/right
- implement fixed directional transforms
- create non-mirrored animations
- assume LTR-only layouts
- hardcode directional icons
- ignore direction-aware charts

## 36. Forbidden RTL Anti-Patterns
- physical CSS directional properties
- static LTR-only layouts
- unmirrored slide animations
- mixed physical and logical alignment
- direction-specific icon duplication
- RTL broken push/pull gestures
- separate RTL-only components for common UI

## 37. Real-World Agricultural RTL Scenarios
- **Inspection flow:** an Arabic technician drills down from a right-aligned dashboard to RTL forms while gestures and charts mirror naturally.
- **Harvest checklist:** a field worker uses RTL cards and bottom navigation, with directional swipe actions reflecting local expectations.
- **Audit review:** an auditor switches to English and sees the layout flip cleanly to LTR, preserving widget order and gesture behavior.

## 38. Future Bilingual Evolution
Support future bilingual experiences with seamless RTL/LTR switching, shared token systems, and language-agnostic layout components. Expand direction-aware charting and motion presets for both directions.

## 39. Runtime Rendering Examples
Example flows: `html[dir='rtl']` enables logical inline-start spacing, mirrored icon animation, and RTL chart axes; switching to `dir='ltr'` reverses flow without replacing components.

## 40. Final RTL Enforcement Checklist
- `html[dir]` is authoritative
- only logical CSS properties are used
- layouts mirror with direction, not hardcoded values
- animations adapt to `dir`
- gestures respect directionality
- charts and tables support RTL
- runtime direction switching works without reload
- AI-generated UI follows RTL rules

## Notes
Important notes placeholder.

## Last Updated
2026-05-12
