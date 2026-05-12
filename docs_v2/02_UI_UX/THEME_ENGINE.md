# THEME ENGINE

## Purpose
Define the master runtime theme and white-label architecture for ATLS, enabling tenant-isolated branding, semantic theming, and runtime configurable appearance without code changes. This document establishes the rules for dynamic logos, app naming, theme modes, typography, spacing, and performance-safe theme injection.

## Scope
Covers theme philosophy, token architecture, runtime theme injection, tenant isolation, branding systems, dynamic rendering, performance constraints, accessibility, RTL compatibility, and future theme marketplace vision.

## Current Status
- [x] Not Started
- [ ] In Progress
- [ ] Completed

## Dependencies
- `docs_v2/02_UI_UX/DESIGN_SYSTEM.md`
- `docs_v2/02_UI_UX/MOBILE_FIRST_STRATEGY.md`
- `docs_v2/02_UI_UX/RTL_SYSTEM.md`
- `docs_v2/04_DYNAMIC_ENGINES/DYNAMIC_THEME_ENGINE.md`
- `docs_v2/04_DYNAMIC_ENGINES/ROLE_PERMISSION_ENGINE.md`
- `docs_v2/01_ARCHITECTURE/FRONTEND_ARCHITECTURE.md`
- `docs_v2/07_AI_AGENT/AI_DEVELOPMENT_RULES.md`

## Notes
This is the master theme engine document for ATLS. Themes are runtime-configurable, tenant-isolated, white-label capable, and semantic-token driven. No hardcoded branding or non-token styling is allowed.

## Last Updated
2026-05-12

---

## 1. Theme Philosophy
ATLS themes are runtime-first and tenant-aware. Branding and appearance are configurable by super admins and delivered dynamically to every tenant without code changes.

## 2. White-Label Architecture
White-label themes are separate tenant configurations that control logo, colors, typography, layout density, and dashboard appearance. White-label settings are isolated and applied at runtime.

## 3. Multi-Tenant Theme Isolation
Each tenant receives its own theme configuration. Isolation exists in storage, runtime resolution, and CSS variable application to prevent branding leaks.

## 4. Runtime Theme Injection
Themes inject CSS variables at runtime into the document root. Injection updates appearance immediately and avoids full reloads.

## 5. Theme Token Architecture
Tokens are semantic and hierarchical. The architecture separates semantic color tokens, typography tokens, spacing scales, and component-level overrides.

## 6. Semantic Color System
Colors are defined as semantic roles such as `surface-primary`, `text-primary`, `border-muted`, and `interactive-accent`. Use semantic tokens instead of hex literals.

## 7. Typography System
Typography is defined with scales for headings, body, captions, and numeric text. Tokens control font family, size, weight, line height, and letter spacing.

## 8. Arabic Typography Rules
Arabic typography uses locale-appropriate font stacks, direction-aware line heights, and clear glyph rendering. Text sizing and spacing are optimized for Arabic script readability.

## 9. Font Loading Strategy
Load fonts asynchronously and cache them per tenant. Use fallback font stacks until the configured tenant font is available.

## 10. Logo Management Rules
Logos are tenant-configurable media assets. The theme engine loads logos via CDN or secured assets and injects them through theme variables, never hardcoded.

## 11. Dynamic App Naming Rules
App names are configurable per tenant and injected at runtime in navigation, headers, and metadata. Names are not hardcoded in UI assets.

## 12. Theme Mode Architecture
Theme modes are runtime switches between dark, light, and high-contrast variants. Mode selection updates the same semantic token set with different values.

## 13. Dark Mode Rules
Dark mode uses semantic tokens optimized for nighttime and indoor use. Contrast ratios are validated and overlays remain legible.

## 14. Light Mode Rules
Light mode uses bright surfaces and strong outdoor readability. Ensure light backgrounds and dark text remain accessible in sunlight.

## 15. Runtime CSS Variable Strategy
CSS variables map theme tokens to runtime values. The engine uses variables for colors, spacing, radius, typography, and icon theming.

## 16. Tailwind Theme Integration
Tailwind classes resolve to CSS variables through semantic token bindings. Tailwind config avoids hardcoded colors and relies on runtime variables.

## 17. shadcn/ui Theme Rules
shadcn/ui components consume theme tokens through design-system adapters. Themes do not require modifying shadcn primitives.

## 18. Radix Theme Compatibility
Radix components use CSS variables and token mappings. Theme engine supports Radix theming through logical design tokens.

## 19. Dashboard Theme Rules
Dashboard appearance follows tenant theme settings and semantic tokens. Dashboard widgets align with the configured color system and spacing scale.

## 20. Navigation Theme Rules
Navigation components use semantic background, text, and interactive tokens. Runtime themes apply to bottom bars, drawers, and headers.

## 21. Form Theme Rules
Forms use theme-controlled input borders, field backgrounds, labels, and validation colors. Theme semantics drive focus and error states.

## 22. Chart Theme Rules
Charts align with the current theme through token-driven colors and contrast rules. Chart palettes remain coherent with dashboard and navigation themes.

## 23. Widget Theme Rules
Widgets respect tenant themes and use shared semantic tokens. Widgets do not define their own colors outside the theme contract.

## 24. Layout Density Rules
Layout density is configurable through theme tokens. Density settings adjust spacing, card padding, and component compactness in a controlled way.

## 25. Border Radius System
Radius tokens define consistent corner rounding across components. Radius values are controlled by theme and applied through CSS variables.

## 26. Spacing Scale System
Spacing uses a scale of semantic tokens such as `space-xs`, `space-md`, and `space-xl`. The scale is consistent across cards, forms, and layout gaps.

## 27. Iconography Theme Rules
Icons use semantic color tokens for fills and strokes. Directional icons mirror with RTL but remain theme-consistent.

## 28. Animation Theme Rules
Animation presets use theme-aware durations and easing. Motion values are controlled by tokens, with performance-aware limits for low-end devices.

## 29. Runtime Theme Persistence
Theme settings persist per tenant and user session. Persistence supports offline access and restores the configured theme state.

## 30. Offline Theme Behavior
Offline theme state remains visible and consistent. Theme rendering falls back to the last known configuration when connectivity is lost.

## 31. Theme Accessibility Rules
Themes enforce contrast standards, text legibility, and focus states. Token values are validated against accessibility metrics.

## 32. RTL Theme Compatibility
Theme tokens and layouts support RTL natively. Direction-aware styling uses logical properties and mirrored iconography.

## 33. Theme Performance Constraints
Themes minimize render impact by batching variable updates and avoiding excessive recalculations. Runtime injection is lightweight and optimized for low-end devices.

## 34. Theme Security Rules
Validate theme inputs server-side and sanitize configurable values. Prevent tenant themes from leaking across boundaries or introducing XSS through CSS values.

## 35. AI Safety Rules
AI must not:
- hardcode hex colors
- use inline styles
- duplicate tokens
- leak tenant branding
- override component colors directly
- use non-semantic color values
- hardcode logos
- hardcode typography
- hardcode spacing scales

## 36. Forbidden Theme Anti-Patterns
- hardcoded branding values
- inline theming in components
- duplicated theme tokens
- tenant-shared theme data
- component-specific color overrides
- static spacing systems
- hardcoded logos or app names
- theme reloads requiring code recompilation

## 37. Real-World White-Label Scenarios
- **Tenant launch:** a new brand configures logo, app name, and accent palette at runtime, with immediate effect across mobile dashboards.
- **Arabic-first client:** an Arabic tenant sets custom typography and RTL-aware theme values while preserving shared component structure.
- **Dark/light product:** a field operator toggles modes on the fly while the theme engine preserves semantic colors across charts, forms, and navigation.

## 38. Theme Migration Strategy
Theme migrations provide safe fallback values when token sets evolve. The strategy upgrades legacy theme configs without breaking existing tenants.

## 39. Future Theme Marketplace Vision
The theme engine can evolve to support marketplace themes, allowing tenants to select certified visual packages. Marketplace themes are still runtime-configurable and token-backed.

## 40. Final Theme Enforcement Checklist
- all themes are runtime-configurable
- branding is tenant isolated
- colors are semantic tokens only
- no hardcoded branding is used
- theme switching does not require reload
- typography is configurable through tokens
- spacing and radius use token scales
- runtime CSS variables drive appearance
- theme persistence supports offline use
- theme changes are validated and secure
