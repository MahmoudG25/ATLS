# Motion & Animation System Governance

| Metadata | Details |
| :--- | :--- |
| **Document ID** | ATLS-FRONT-06 |
| **Status** | AUTHORITATIVE |
| **Version** | 2.0.0 |
| **Owner** | Frontend Architecture Team |
| **Applicability** | All ATLS Web, PWA, and Mobile Interfaces |

## 1. Motion Philosophy
Motion in ATLS is **Functional, Subdued, and Informative**. We do not use animation for decoration. Motion exists to provide spatial orientation, confirm user actions, and reflect the real-time operational status of the farm.
- **Direct**: No bounce, no fluff.
- **Fast**: Transitions should never block a user from acting.
- **Contextual**: Motion should explain *where* an element came from and *where* it is going.

## 2. Operational UX Motion Principles
- **Clarity over Delight**: A farmer needs to know a report was saved, not see a complex animation.
- **Feedback Loop**: Every interaction (press, sync, error) must have a corresponding micro-motion.
- **Persistence of State**: Use motion to show that data is "travelling" to the offline queue.

## 3. Mobile-First Animation Rules
- **Viewport Constraints**: Avoid animations that exit the viewport boundaries (causes layout shifts).
- **Battery Preservation**: Use CSS animations over JS-heavy calculations where possible.
- **Interruptible**: Users must be able to click through or interrupt any transition.

## 4. RTL Motion Rules
- **Horizontal Mirroring**: Slide-ins from the "right" in LTR must slide in from the "left" in RTL.
- **Directional Icons**: Arrows and progress bars must reverse direction.
- **Spatial Logic**: The concept of "Forward" (Next) must move right-to-left in Arabic/Hebrew.

## 5. Motion Hierarchy Architecture
1. **Primary (Systemic)**: Page transitions, navigation.
2. **Secondary (Contextual)**: Modals, drawers, expandable sections.
3. **Tertiary (Micro)**: Button presses, toggles, success checks.

## 6. Animation Token System
Tokens are implemented via Tailwind and Framer Motion variants.
- `--motion-duration-fast`: 150ms
- `--motion-duration-base`: 250ms
- `--motion-duration-slow`: 400ms
- `--motion-easing-standard`: `[0.4, 0, 0.2, 1]`
- `--motion-easing-entrance`: `[0, 0, 0.2, 1]`
- `--motion-easing-exit`: `[0.4, 0, 1, 1]`

## 7. Duration Scale Rules
- **Micro-interactions**: <= 150ms.
- **Standard UI Transitions**: 200ms - 300ms.
- **Complex Page Changes**: Max 400ms.
- **Rule**: Never exceed 500ms for any UI animation.

## 8. Easing Rules
- **Standard**: For elements moving within the screen.
- **Decelerate**: For entering elements (fast start, slow end).
- **Accelerate**: For exiting elements (slow start, fast end).
- **Linear**: Reserved for background fades or progress bars.

## 9. Transition Standards
All transitions must use `opacity` and `transform` (scale, translate) only. 
- **FORBIDDEN**: Animating `height`, `width`, `top`, `left`, or `margin` (triggers layout thrashing).

## 10. Navigation Transition Rules
- **Shared Element Transitions**: Minimal use for high-context changes (e.g., clicking an Enclosure to see details).
- **Tab Switching**: Cross-fade or subtle slide with 200ms duration.

## 11. Page Transition Rules
- **Entrance**: Fade in with 20px vertical offset (slide up).
- **Exit**: Fade out with no offset to avoid distracting the eye from incoming content.

## 12. Modal Animation Rules
- **Entrance**: Scale from 95% to 100% + Fade.
- **Overlay**: Instant or 100ms fade.
- **Exit**: Scale down or simple fade.

## 13. Drawer & Bottom Sheet Motion
- **Entrance**: Slide from bottom (0% to 100% height).
- **Physics**: Use "spring" damping for a tactile, touch-first feel on mobile.
- **Gestures**: Must follow the finger during drag-to-close.

## 14. Bottom Navigation Motion
- **Active State**: Subtle scale up (1.1x) or indicator bar slide.
- **Haptic Sync**: Trigger haptic feedback (where available) with the animation.

## 15. Dashboard Animation Rules
- **Entrance**: Staggered children (max 5 items) with 0.05s delay between items.
- **Updates**: Use `framer-motion`'s `layout` prop for smooth re-ordering of KPI cards.

## 16. KPI Update Animations
- **Number Ticker**: Fast roll for numeric changes.
- **Color Pulse**: Subtle background flash (Green/Red) on value change to indicate "Live" update.

## 17. Loading Animation Standards
- **Progressive Disclosure**: Show text first, then skeleton, then data.
- **Indeterminate**: Use a horizontal progress bar (ATLS Emerald) at the top of the viewport.

## 18. Skeleton Animation Rules
- **Shimmer**: Linear gradient moving left-to-right (mirrored in RTL).
- **Cycle**: 1.5s duration.
- **Contrast**: Low-contrast gray (#F1F5F9 to #E2E8F0) to avoid "strobe" effect.

## 19. Error State Motion Rules
- **Shake**: Subtle horizontal shake (6px) on failed submission.
- **Entrance**: Slide down from the field or top of the screen.

## 20. Success Feedback Motion
- **Checkmark**: Draw-path animation for completion.
- **Scale**: Brief 1.05x scale of the successful card/button.

## 21. Toast & Notification Motion
- **Queueing**: New toasts push old ones up smoothly.
- **Positioning**: Slide in from top-center (mobile) or bottom-right (desktop).

## 22. Gesture Animation Rules
- **Swipe to Delete**: Immediate 1:1 response.
- **Spring Back**: If swipe is incomplete, element must snap back using a high-tension spring.

## 23. Press/Hover/Focus States
- **Press**: Scale down to 0.97x.
- **Hover**: (Desktop only) Subtle lift or brightness change.
- **Focus**: Border pulse or high-visibility outline.

## 24. Pull-To-Refresh Motion
- **Spinner**: Rotate based on pull distance.
- **Release**: Fast snap-to-position (60px from top) while loading.

## 25. Offline Sync Animation UX
- **Cloud Sync**: Rotating icon in the status bar.
- **Batch Success**: "Success" pulse on the offline queue counter.

## 26. Media Upload Progress Motion
- **Real-time**: Fluid progress bar (no jumps).
- **Completion**: Transition from progress bar to thumbnail fade-in.

## 27. Table Animation Rules
- **Re-ordering**: Animate row swaps with `layout` prop.
- **Filtering**: Fade out removed rows, slide up remaining rows.

## 28. List Virtualization Constraints
- **Rule**: Disable entry animations for virtualized lists to prevent CPU spikes.
- **Scroll**: Use `smooth` behavior for programmatic scrolls only if target is < 2 viewports away.

## 29. Accessibility Motion Reduction
- **User Preference**: Respect `prefers-reduced-motion: reduce`.
- **Implementation**: Replace slides/scales with simple `opacity: 0` to `1` transitions.

## 30. Reduced Motion Strategy
```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

## 31. GPU Acceleration Rules
- **Hardware**: Force GPU layer for complex items using `translateZ(0)` or `will-change: transform`.
- **Constraint**: Only use `will-change` on persistent elements to avoid memory leaks.

## 32. Performance Constraints
- **Frame Rate**: Maintain 60fps on mid-range devices.
- **Jank**: Zero layout shifts (CLS) during animation.

## 33. Low-End Device Constraints
- **Android 8+**: Limit to 2 concurrent animations.
- **Optimization**: Use `opacity` only if CPU usage > 80%.

## 34. Framer Motion Governance
- **Variants**: Always define variants outside the component for reusability and performance.
- **Layout**: Use `layoutId` sparingly for shared elements.
- **Exit**: Always wrap in `AnimatePresence`.

## 35. Tailwind Animation Usage Rules
- **Utility**: Use `animate-pulse`, `animate-spin`, `animate-bounce` for systemic states only.
- **Custom**: Define ATLS-specific durations/easings in `tailwind.config.js`.

## 36. AI Safety Rules
- **Validation**: AI agents MUST NOT add custom animations outside the token system.
- **Over-animation**: FORBID "animation spam" (multiple items moving simultaneously without relation).
- **Blocking**: FORBID animations that prevent user interaction (e.g., unskippable intros).
- **Complexity**: FORBID heavy parallax or 3D effects.
- **Feedback**: FORBID motion-only feedback; must always accompany a visual/textual state change.
- **Optimization**: FORBID dashboard animations that trigger re-renders of the entire data grid.

## 37. Forbidden Animation Anti-Patterns
- **The Bounce**: Never use "bouncy" or "elastic" easings for operational tools.
- **Infinite Spinners**: Avoid loaders that don't indicate progress for > 5 seconds.
- **Hidden Text**: Never animate text visibility via `letter-spacing` (performance killer).

## 38. Real Agricultural UX Motion Scenarios
- **Harvest Load**: Sliding a weight card into the ledger shows the data is "recorded".
- **Pesticide Warning**: Red border pulse on a field that exceeds safety thresholds.
- **GPS Lock**: Transition from "Searching" (pulse) to "Fixed" (solid check).

## 39. Future Motion Expansion
- **Lottie Support**: Reserved for onboarding or complex educational walkthroughs.
- **SVG Paths**: Advanced data visualization (growth charts) path animations.

## 40. Final Motion Enforcement Checklist
- [ ] `prefers-reduced-motion` is implemented.
- [ ] Only `opacity` and `transform` are animated.
- [ ] Durations follow the 150ms/250ms/400ms scale.
- [ ] RTL mirroring is verified for all slide animations.
- [ ] Low-end Android performance test passed.
- [ ] No unskippable/blocking transitions.
- [ ] Haptic feedback (if any) is synced with motion.
