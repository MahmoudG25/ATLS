# DYNAMIC THEME ENGINE

## Purpose
Define the runtime theme engine architecture for ATLS, enabling dynamic branding, tenant-specific theming, and white-label customization without frontend redeployment. This document establishes the rules for semantic tokens, runtime injection, tenant isolation, and AI-safe theming constraints.

## Scope
Covers theme engine philosophy, token system, runtime injection, tenant isolation, white-label branding, typography, dark mode, layout variants, dashboard theming, mobile-first rules, RTL support, versioning, performance, and observability.

## Current Status
- [x] Not Started
- [ ] In Progress
- [ ] Completed

## Dependencies
- `docs_v2/01_ARCHITECTURE/FRONTEND_ARCHITECTURE.md`
- `docs_v2/01_ARCHITECTURE/STATE_MANAGEMENT.md`
- `docs_v2/01_ARCHITECTURE/OFFLINE_STRATEGY.md`
- `docs_v2/01_ARCHITECTURE/API_ARCHITECTURE.md`
- `docs_v2/07_AI_AGENT/AI_DEVELOPMENT_RULES.md`

## Notes
This is the master runtime theme engine document for ATLS. Themes are runtime-configurable, tenant-isolated, and white-label capable. No hardcoded branding or colors allowed; all theming uses semantic tokens.

## Last Updated
2026-05-12

---

## 1. Theme Engine Philosophy
ATLS theming is runtime-driven and tenant-isolated, supporting white-label branding without code changes. Themes adapt dynamically to tenant preferences, ensuring consistent UX across agricultural workflows.

## 2. Why Runtime Theming
Runtime theming enables instant branding changes, multi-tenant isolation, and white-label flexibility. Themes load from server state, allowing super admins to customize without deployments.

## 3. Theme Engine Architecture
The engine includes semantic tokens, runtime injection, theme resolution pipeline, and persistence layer. Integrates with Tailwind, shadcn/ui, and Framer Motion for consistent application.

## 4. Semantic Token System
Tokens are semantic (e.g., primary-color, text-muted) mapped to design values. Tokens enable runtime overrides without hardcoded values.

## 5. Design Token Hierarchy
Hierarchy: global tokens → component tokens → semantic overrides. Hierarchy supports tenant customization while maintaining base consistency.

## 6. Runtime Theme Injection
Themes inject CSS variables at runtime via JavaScript. Injection updates DOM styles dynamically, supporting theme switching without reload.

## 7. Theme Resolution Pipeline
Pipeline: fetch tenant theme → merge with base → resolve tokens → inject CSS variables. Pipeline handles fallbacks and validation.

## 8. Tenant Theme Isolation
Themes are scoped by tenant; each tenant has isolated theme data. Isolation prevents cross-tenant leakage and ensures branding integrity.

## 9. White-Label Branding Strategy
White-label variants have dedicated theme configurations. Branding includes logos, colors, and layouts, isolated per variant.

## 10. Dynamic Logo Management
Logos are managed via media system, with runtime URLs injected into themes. Logos support multiple sizes and formats.

## 11. Typography Architecture
Typography uses semantic scales (heading, body, caption) with runtime font families and sizes. Supports tenant-specific fonts.

## 12. Color Palette Architecture
Palettes include primary, secondary, neutral, and accent colors. Palettes are runtime-configurable with contrast validation.

## 13. Spacing & Radius System
Spacing uses scale-based tokens (space-1 to space-10). Radius tokens for borders ensure consistent rounding.

## 14. Iconography Rules
Icons are theme-aware, with color and size tokens. Rules support RTL flipping and tenant-specific icon sets.

## 15. Dark Mode Architecture
Dark mode uses inverted palettes with semantic tokens. Mode switching toggles CSS variable sets.

## 16. Light Mode Architecture
Light mode is the default, with high-contrast palettes. Mode supports accessibility standards.

## 17. Theme Switching Lifecycle
Switching: update Zustand state → resolve new theme → inject variables → re-render components. Lifecycle is instant and reload-free.

## 18. Layout Variant System
Variants include compact, spacious, and mobile layouts. Variants adjust spacing and component sizes dynamically.

## 19. Dashboard Variant Architecture
Dashboards have theme variants for different agricultural contexts (e.g., farm overview, equipment monitoring). Variants customize widgets and layouts.

## 20. Navigation Theme Rules
Navigation themes control sidebar, tabs, and menus. Rules support collapsible states and theme-aware icons.

## 21. Mobile-First Theme Rules
Themes prioritize mobile: touch-friendly spacing, readable fonts, and adaptive layouts. Rules ensure responsive behavior.

## 22. RTL-Aware Theme Rendering
RTL themes reverse layouts, icons, and text alignment. Rendering detects locale and applies RTL tokens automatically.

## 23. Theme Persistence Strategy
Themes persist in server state and cache locally. Persistence survives offline usage with hydration on reconnect.

## 24. Theme Versioning Rules
Themes are versioned; clients check compatibility. Versioning prevents stale theme application.

## 25. Theme Migration Strategy
Migrations update theme data for new tokens. Migrations are automated with fallbacks.

## 26. Runtime CSS Variable Injection
Injection uses :root CSS variables updated via JavaScript. Variables map to Tailwind classes.

## 27. Tailwind Integration Rules
Tailwind uses semantic classes (e.g., bg-primary) resolved to CSS variables. No hardcoded colors in Tailwind config.

## 28. shadcn/ui Theme Integration
shadcn/ui components use theme tokens for styling. Integration ensures consistent theming across UI library.

## 29. Framer Motion Theme Presets
Motion uses theme-based easing and durations. Presets support animated transitions with theme colors.

## 30. Accessibility & Contrast Rules
Themes enforce WCAG contrast ratios. Rules validate color combinations and provide high-contrast modes.

## 31. Performance Constraints
Themes limit variable count and injection frequency. Lazy loading prevents initial bundle bloat.

## 32. Lazy Theme Loading
Themes load on demand, reducing startup time. Lazy loading uses dynamic imports for theme assets.

## 33. Offline Theme Behavior
Themes cache locally for offline use. Offline themes use persisted state without server fetches.

## 34. Theme Observability
Themes track loading times, switch events, and errors. Observability aids debugging and optimization.

## 35. Theme Security Constraints
Themes validate inputs to prevent XSS. Constraints ensure safe CSS variable injection.

## 36. AI Safety Rules
AI must not:
- hardcode colors or styles
- use inline styles
- create tenant-specific CSS
- duplicate theme objects
- modify shadcn primitives
- style without tokens

## 37. Forbidden Theme Anti-Patterns
- hardcoded branding
- inline CSS
- tenant-specific stylesheets
- non-semantic tokens
- reload-required switching
- non-isolated themes

## 38. Real-World White-Label Scenarios
- **Tenant branding:** a farm cooperative customizes colors and logos via admin panel, applied instantly across mobile apps.
- **White-label variant:** a regional brand overrides typography and layouts for local markets, isolated from other variants.
- **Dark mode toggle:** users switch modes dynamically, with themes persisting per tenant.

## 39. Future Theme Engine Evolution
- Advance AI-generated themes from branding guidelines.
- Implement real-time theme collaboration.
- Expand animation presets with physics-based motion.
- Integrate with design tools for live syncing.
- Enhance offline theme editing capabilities.

## 40. Example Runtime Theme Flow
1. Fetch tenant theme from API.
2. Merge with base tokens.
3. Inject CSS variables.
4. Update Tailwind classes.
5. Re-render with new theme.

## Notes
Important notes placeholder.

## Last Updated
2026-05-12
