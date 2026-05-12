# TAILWIND RULES

## Purpose
Define the authoritative Tailwind CSS governance framework for ATLS frontend, establishing utility-first constraints, design token enforcement, responsive architecture, and AI-safe class composition rules. This document ensures consistent, maintainable, scalable styling across all ATLS agricultural ERP interfaces while preventing utility explosion, responsive chaos, and dark mode inconsistency.

## Scope
Covers utility-first governance, design token architecture, spacing system rules, typography scales, responsive breakpoint discipline, RTL-safe utilities, class ordering conventions, component styling boundaries, dark mode strategy, theme token integration, white-label support, forbidden utility abuse patterns, responsive layout governance, mobile-first rules, Tailwind + shadcn integration, CSS variable architecture, state styling patterns, form styling consistency, table styling systems, z-index governance, elevation/shadow rules, animation utility usage, accessibility styling, performance constraints, and AI safety rules.

## Current Status
- [x] Not Started
- [ ] In Progress
- [x] Completed

## Dependencies
- `docs_v2/02_FRONTEND/DESIGN_SYSTEM.md`
- `docs_v2/02_FRONTEND/SHADCN_GUIDE.md`
- `docs_v2/05_FRONTEND/COMPONENT_ARCHITECTURE.md`
- `docs_v2/07_AI_AGENT/AI_DEVELOPMENT_RULES.md`

## Notes
Tailwind is the primary styling engine for ATLS. All styling must use utilities; inline styles and arbitrary values are forbidden. Responsive utilities must be mobile-first. Dark mode is explicit and RTL-aware. All custom utilities and theme extensions are governed.

## Last Updated
2026-05-12

---

## 1. Utility-First Governance

**RULE:** All ATLS styling uses Tailwind utilities exclusively. Inline styles are forbidden.

**Enforcement:**
- Linter rules detect and reject `style={{}}` in components
- CSS modules are permitted only for animations and global resets
- All component styling flows through design tokens
- Custom CSS must be reviewed by architecture team

**Application:**
```jsx
// GOOD: Utility-driven styling
<div className="p-4 bg-white rounded-lg shadow-md border border-gray-200">
  <h2 className="text-lg font-semibold text-gray-900">Title</h2>
</div>

// BAD: Inline styles
<div style={{padding: '16px', backgroundColor: 'white'}}>
```

**Agricultural Example:**
Field worker dashboard uses utilities for responsive card layouts, ensuring consistent spacing across tablet and mobile devices without inline style chaos.

---

## 2. Design Token-Driven Architecture

**RULE:** All spacing, sizing, colors, typography, and elevation use design tokens. Magic numbers are forbidden.

**Token System:**
- **Spacing:** `space-1` (4px) through `space-10` (40px) in 4px increments
- **Typography:** `text-xs`, `text-sm`, `text-base`, `text-lg`, `text-xl`, `text-2xl`
- **Colors:** Semantic names (primary, secondary, neutral, status colors)
- **Shadows:** `shadow-sm` through `shadow-lg` for elevation
- **Borders:** `border`, `border-2` with semantic colors
- **Radii:** `rounded-sm`, `rounded-md`, `rounded-lg`, `rounded-full`

**Enforcement:**
- Linter detects arbitrary values in tailwind config
- All tokens are centralized in `tailwind.config.js`
- Theme provider injects tokens as CSS variables
- AI agents must only use documented tokens

**CSS Variable Architecture:**
```css
:root {
  --color-primary: #1f2937;
  --color-primary-light: #3b82f6;
  --color-primary-dark: #0f172a;
  --color-neutral-bg: #ffffff;
  --color-neutral-text: #1f2937;
  --space-base: 4px;
}

@media (prefers-color-scheme: dark) {
  :root {
    --color-neutral-bg: #1f2937;
    --color-neutral-text: #f3f4f6;
  }
}
```

---

## 3. Spacing System Governance

**RULE:** Spacing must use consistent scales. No arbitrary pixel values allowed.

**Spacing Scale:**
- `space-1` = 4px
- `space-2` = 8px
- `space-3` = 12px
- `space-4` = 16px
- `space-6` = 24px
- `space-8` = 32px
- `space-10` = 40px

**Application Rules:**
- Section containers: `p-6` or `p-8`
- Card padding: `p-4` for mobile, `p-6` for desktop
- Field groups: `mb-4` (vertical) or `gap-4` (flex)
- Element margins: prefer `gap` over `margin` in flex/grid
- Touch targets: minimum `h-10` (40px) for buttons and inputs

**Grid Spacing:**
```jsx
// GOOD: Consistent spacing with gap
<div className="flex flex-col gap-4">
  <input className="px-4 py-2 rounded border" />
  <button className="px-6 py-3 bg-primary rounded">Submit</button>
</div>

// BAD: Inconsistent pixel values
<div>
  <input style={{padding: '8px 12px'}} />
  <button style={{marginTop: '16px', padding: '12px 20px'}}>
</div>
```

**Agricultural Example:**
Crop stage form uses `gap-4` between fields, `space-6` for section groups, ensuring consistent rhythm for field workers on mobile devices.

---

## 4. Typography Scale Rules

**RULE:** Typography must use predefined scales. Font sizes are non-negotiable tokens.

**Typography System:**
- `text-xs`: 12px (captions, metadata)
- `text-sm`: 14px (secondary text, labels)
- `text-base`: 16px (body text, default)
- `text-lg`: 18px (secondary headings, emphasis)
- `text-xl`: 20px (section headings)
- `text-2xl`: 24px (page headings)
- `text-3xl`: 30px (KPI values)

**Font Weight Rules:**
- `font-normal` (400): body text, secondary
- `font-medium` (500): labels, secondary headings
- `font-semibold` (600): headings, emphasis
- `font-bold` (700): primary headings, KPI labels

**Application:**
```jsx
// GOOD: Semantic typography
<div>
  <h1 className="text-2xl font-bold text-gray-900">Olive Farm Dashboard</h1>
  <p className="text-base font-normal text-gray-600 mt-2">Production overview</p>
  <span className="text-sm font-medium text-gray-700">Last updated: 2 hours ago</span>
</div>

// BAD: Arbitrary font sizes
<div>
  <h1 style={{fontSize: '28px', fontWeight: '700'}}>Dashboard</h1>
  <p style={{fontSize: '13px', color: '#666'}}>Overview</p>
</div>
```

**Readability Rules:**
- All text must meet WCAG AA contrast (4.5:1 for body, 3:1 for large)
- Outdoor readability: `text-lg` minimum for field views
- Low-end devices: avoid `text-3xl` for non-critical content
- RTL text: `text-right` for Arabic, auto-applied by direction utilities

**Agricultural Example:**
Supervisor KPI dashboard uses `text-3xl font-bold` for production numbers, `text-sm font-medium` for status labels, ensuring outdoor readability on low-end devices.

---

## 5. Responsive Breakpoint Discipline

**RULE:** All layouts must be mobile-first. Responsive utilities follow strict discipline.

**ATLS Breakpoints:**
- **Mobile (base):** 0px–639px
- **Tablet (md):** 640px–1023px
- **Desktop (lg):** 1024px+

**Mobile-First Rule:**
- Default styles target mobile
- Use `md:` prefix for tablet-and-up
- Use `lg:` prefix for desktop-and-up
- Never use `sm:` prefix (considered harmful)

**Responsive Application:**
```jsx
// GOOD: Mobile-first responsive
<div className="flex flex-col md:flex-row md:gap-6 lg:gap-8">
  <div className="w-full md:w-1/2 lg:w-2/3">Sidebar</div>
  <div className="w-full md:w-1/2 lg:w-1/3">Content</div>
</div>

// GOOD: Responsive padding
<section className="p-4 md:p-6 lg:p-8">Content</section>

// BAD: Desktop-first (reversed breakpoints)
<div className="flex flex-row lg:flex-col">

// BAD: Using sm: prefix
<div className="sm:flex">
```

**Grid Responsiveness:**
- Mobile: single column
- Tablet: 2-column grid
- Desktop: 3-4 column grid

**Example: Field Inventory Table**
```jsx
<table className="w-full">
  <thead className="hidden md:table-header-group bg-gray-100">
    <tr>
      <th className="text-left p-3">Field</th>
      <th className="hidden lg:table-cell">Area</th>
      <th>Status</th>
    </tr>
  </thead>
  <tbody className="flex flex-col md:table-row-group gap-2 md:gap-0">
    {fields.map(field => (
      <tr key={field.id} className="flex md:table-row flex-col gap-2">
        <td className="flex md:table-cell before:content-['Field:'] md:before:hidden">{field.name}</td>
        <td className="hidden lg:table-cell">{field.area}</td>
      </tr>
    ))}
  </tbody>
</table>
```

---

## 6. RTL-Safe Utility Usage

**RULE:** All horizontal utilities must be RTL-aware. Directional utilities are explicitly managed.

**RTL-Safe Utilities:**
- Use `start`/`end` instead of `left`/`right`
- Use `ps-` (padding-start) instead of `pl-` (padding-left)
- Use `pe-` (padding-end) instead of `pr-` (padding-right)
- Use `ms-` (margin-start) instead of `ml-` (margin-left)
- Use `me-` (margin-end) instead of `mr-` (margin-right)

**Application:**
```jsx
// GOOD: RTL-aware
<button className="px-4 py-2 bg-primary rounded">
  <span className="me-2">✓</span>
  <span>Accept</span>
</button>

// BAD: Direction-specific
<button className="pl-4 pr-4">
  <span style={{marginRight: '8px'}}>✓</span>
</button>
```

**Directional Content Flipping:**
- Icons in RTL: use `rtl:scale-x-[-1]` or `rtl:rotate-180`
- Navigation arrows: `rtl:rotate-180` for consistent direction
- Left-aligned text: `text-left rtl:text-right` (auto-managed by theme)

**Example: Sidebar Navigation**
```jsx
<nav className="flex flex-col gap-2">
  <a href="/farms" className="flex items-center gap-3 px-4 py-2">
    <MapIcon className="w-5 h-5 rtl:scale-x-[-1]" />
    <span>Farms</span>
  </a>
</nav>
```

---

## 7. Class Ordering Conventions

**RULE:** Tailwind classes must follow strict ordering. Automatic formatting is enforced.

**Class Order:**
1. **Layout:** `flex`, `grid`, `hidden`, `block`, `inline-block`
2. **Display:** `contents`, `flex-col`, `justify-center`, `items-start`
3. **Sizing:** `w-full`, `h-screen`, `min-h-10`, `max-w-md`
4. **Spacing:** `p-4`, `px-6`, `py-2`, `m-2`, `gap-3`
5. **Appearance:** `bg-white`, `text-gray-900`, `border-2`, `rounded-lg`
6. **Typography:** `font-semibold`, `text-lg`, `leading-relaxed`
7. **Effects:** `shadow-md`, `opacity-50`, `blur-sm`
8. **Transforms:** `scale-110`, `rotate-45`, `translate-x-4`
9. **Transitions:** `transition-all`, `duration-300`, `ease-in-out`
10. **Responsive:** `md:flex`, `lg:w-2/3`
11. **Dark mode:** `dark:bg-gray-900`, `dark:text-white`
12. **Group states:** `group-hover:bg-gray-100`
13. **Hover/Focus:** `hover:bg-blue-600`, `focus:outline-none`

**Tooling:**
- Use Prettier + `tailwindcss` plugin for automatic class sorting
- Configure `.prettierrc`:
```json
{
  "plugins": ["prettier-plugin-tailwindcss"],
  "tailwindConfig": "./tailwind.config.js"
}
```

**Example:**
```jsx
// CORRECT ordering (automatic via Prettier)
<button className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg shadow-md transition-all duration-200 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 md:px-8 dark:bg-blue-700 dark:hover:bg-blue-800">
  Submit
</button>
```

---

## 8. Component Styling Boundaries

**RULE:** Component styling boundaries are strict. Styles flow from utilities → shadcn components → domain wrappers.

**Styling Layers:**
1. **Utilities:** base Tailwind classes
2. **shadcn Components:** pre-styled from shadcn/ui
3. **Domain Wrappers:** agricultural domain extensions
4. **Pages:** composition and layout only

**Component Styling Contract:**
```jsx
// GOOD: Respecting boundaries
// Button.jsx (shadcn - do not modify)
export const Button = forwardRef(({ ...props }, ref) => (
  <button
    ref={ref}
    className={cn(
      "px-4 py-2 bg-primary text-white rounded-lg",
      props.className
    )}
  >
    {props.children}
  </button>
))

// PrimaryButton.jsx (domain wrapper)
export const PrimaryButton = ({ children, ...props }) => (
  <Button className="font-semibold uppercase" {...props}>
    {children}
  </Button>
)

// Usage: page.jsx
<PrimaryButton onClick={handleSubmit}>Save Field Data</PrimaryButton>
```

**Forbidden:**
- Modifying shadcn component internals
- Adding custom CSS alongside utilities
- Exporting components with hardcoded className overrides
- Component styling that breaks responsive behavior

---

## 9. Dark Mode Strategy

**RULE:** Dark mode is explicit, comprehensive, and token-driven. All components must support dark mode.

**Dark Mode Architecture:**
- Default: light mode
- Override: `dark:` prefix or `prefers-color-scheme: dark`
- Storage: user preference in localStorage + theme provider
- Application: root element `data-theme="dark"` or `class="dark"`

**Dark Mode Implementation:**
```jsx
// tailwind.config.js
export default {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        'neutral-bg': 'var(--color-neutral-bg)',
        'neutral-text': 'var(--color-neutral-text)',
      }
    }
  }
}

// ThemeProvider.jsx
export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState(() => 
    localStorage.getItem('theme') || 'light'
  )
  
  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark')
    localStorage.setItem('theme', theme)
  }, [theme])
  
  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}
```

**Dark Mode Color Rules:**
- Backgrounds: light mode `bg-white`, dark mode `bg-gray-900`
- Text: light mode `text-gray-900`, dark mode `text-white`
- Cards: light mode `bg-gray-50`, dark mode `bg-gray-800`
- Borders: light mode `border-gray-200`, dark mode `border-gray-700`
- Inputs: light mode `bg-white`, dark mode `bg-gray-800`

**Example:**
```jsx
<div className="bg-white dark:bg-gray-900 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-700 rounded-lg p-4">
  <h2 className="text-lg font-semibold">Field Data</h2>
  <input className="bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-600" />
</div>
```

**Enforcement:**
- All UI components must have dark mode utilities
- Dark mode is tested in CI/CD pipeline
- Missing dark mode classes fail PR review

---

## 10. Theme Token Integration

**RULE:** All theme customization flows through CSS variables and design tokens. Direct color usage is forbidden.

**Token Architecture:**
```jsx
// tailwind.config.js
const colors = {
  primary: 'var(--color-primary)',
  'primary-light': 'var(--color-primary-light)',
  'primary-dark': 'var(--color-primary-dark)',
  secondary: 'var(--color-secondary)',
  neutral: {
    'bg': 'var(--color-neutral-bg)',
    'text': 'var(--color-neutral-text)',
    '50': 'var(--color-neutral-50)',
    '100': 'var(--color-neutral-100)',
    '200': 'var(--color-neutral-200)',
  },
  status: {
    'success': 'var(--color-status-success)',
    'error': 'var(--color-status-error)',
    'warning': 'var(--color-status-warning)',
    'info': 'var(--color-status-info)',
  }
}

export default {
  theme: { colors }
}
```

**CSS Variable Storage:**
```css
:root {
  --color-primary: #2563eb;
  --color-primary-light: #3b82f6;
  --color-primary-dark: #1d4ed8;
  --color-secondary: #7c3aed;
  --color-neutral-bg: #ffffff;
  --color-neutral-text: #1f2937;
  --color-neutral-50: #f9fafb;
  --color-neutral-100: #f3f4f6;
  --color-neutral-200: #e5e7eb;
  --color-status-success: #10b981;
  --color-status-error: #ef4444;
  --color-status-warning: #f59e0b;
  --color-status-info: #0ea5e9;
}

@media (prefers-color-scheme: dark) {
  :root {
    --color-neutral-bg: #1f2937;
    --color-neutral-text: #f3f4f6;
    --color-neutral-50: #111827;
  }
}
```

**Theme Override for White-Label:**
```jsx
// WhiteLabelTheme.jsx
export const applyCustomTheme = (branding) => {
  const root = document.documentElement
  root.style.setProperty('--color-primary', branding.primaryColor)
  root.style.setProperty('--color-primary-light', branding.primaryLightColor)
  root.style.setProperty('--color-secondary', branding.secondaryColor)
}
```

---

## 11. White-Label Support Strategy

**RULE:** All customizable colors and branding elements use CSS variables. No hardcoded brand colors allowed.

**White-Label Customization Points:**
- Primary color (CTAs, accents)
- Secondary color (emphasis)
- Logo placement and sizing
- Typography brand
- Border radius (conservative vs. modern)
- Spacing density (compact vs. spacious)

**Implementation:**
```jsx
// BrandingConfig.js
export const getBrandingVariables = (tenant) => ({
  '--color-primary': tenant.brand.primaryColor || '#2563eb',
  '--color-secondary': tenant.brand.secondaryColor || '#7c3aed',
  '--color-neutral-bg': tenant.brand.backgroundColor || '#ffffff',
  '--border-radius': tenant.brand.borderRadius || '8px',
})

// App.jsx
useEffect(() => {
  const variables = getBrandingVariables(tenant)
  Object.entries(variables).forEach(([key, value]) => {
    document.documentElement.style.setProperty(key, value)
  })
}, [tenant])
```

**Forbidden:**
- Hardcoded brand colors (use variables)
- Inline styles for branding (use classes)
- Multiple CSS files per tenant (use CSS variables)

---

## 12. Forbidden Utility Abuse Patterns

**RULE:** Certain utility patterns are strictly forbidden to prevent chaos and performance degradation.

**Forbidden Patterns:**

### Random Spacing
```jsx
// BAD: arbitrary spacing values
<div className="mb-[17px] px-[23px] pt-[11px]">
```
**Fix:** Use spacing scale `space-1` through `space-10`

### Random Colors
```jsx
// BAD: arbitrary color values
<div className="bg-[#a4c639] text-[#2d5a3d]">
```
**Fix:** Use design tokens and CSS variables

### Inline Styles Alongside Classes
```jsx
// BAD: mixing utilities with inline styles
<button className="px-4 py-2 bg-blue-600" style={{marginRight: '12px'}}>
```
**Fix:** Use utility classes exclusively `me-3`

### Utility Explosion
```jsx
// BAD: 50+ classes on single element
<div className="flex items-center justify-between ... [20 more classes]">
```
**Fix:** Extract to components or use CSS modules for complex layouts

### Desktop-First Breakpoints
```jsx
// BAD: reversing mobile-first
<div className="hidden lg:block md:flex sm:flex">
```
**Fix:** Mobile-first only: default base, then `md:`, then `lg:`

### Uncontrolled Arbitrary Values
```jsx
// BAD: arbitrary values everywhere
<div className="w-[347px] h-[123px] p-[17px]">
```
**Fix:** Use predefined scales (w-full, h-screen, p-4, etc.)

---

## 13. State Styling Patterns

**RULE:** Component states (hover, focus, active, disabled) must be consistent and accessible.

**State Utilities:**
- `hover:` for mouse hover
- `focus:` for keyboard focus
- `active:` for button press
- `disabled:` for disabled state
- `group-hover:` for parent hover
- `aria-selected:` for accessibility state

**Example: Button States**
```jsx
<button className="
  px-4 py-2 bg-primary text-white rounded-lg
  transition-all duration-200
  hover:bg-primary-dark hover:shadow-lg
  focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2
  active:scale-95
  disabled:opacity-50 disabled:cursor-not-allowed
  dark:bg-primary-dark dark:hover:bg-primary
">
  Submit
</button>
```

**Form Input States:**
```jsx
<input
  className="
    w-full px-3 py-2 border rounded-lg
    border-neutral-300 bg-white text-gray-900
    placeholder-gray-500
    focus:outline-none focus:ring-2 focus:ring-primary
    focus:border-primary
    disabled:bg-gray-100 disabled:cursor-not-allowed
    aria-invalid:border-error aria-invalid:focus:ring-error
    dark:bg-gray-800 dark:border-gray-600 dark:text-white
  "
/>
```

**Accessible Focus Indicators:**
- `focus:outline-none` only if providing visible focus ring
- `focus:ring-2` for 2px focus ring
- `focus:ring-offset-2` for offset from element
- `focus-visible:` for keyboard-only focus (where supported)

---

## 14. Form Styling Consistency

**RULE:** All form elements use consistent styling patterns. Form styling is standardized across ATLS.

**Input Styling:**
```jsx
<input
  type="text"
  className="
    w-full px-4 py-2
    border border-neutral-300 rounded-lg
    bg-white text-gray-900
    placeholder-gray-500
    transition-colors
    focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent
    disabled:bg-gray-100 disabled:cursor-not-allowed
    dark:bg-gray-800 dark:border-gray-600 dark:text-white
  "
/>
```

**Label Styling:**
```jsx
<label className="block text-sm font-medium text-gray-900 mb-2 dark:text-gray-100">
  Field Name
</label>
```

**Select Styling:**
```jsx
<select
  className="
    w-full px-4 py-2
    border border-neutral-300 rounded-lg
    bg-white text-gray-900
    focus:outline-none focus:ring-2 focus:ring-primary
    dark:bg-gray-800 dark:border-gray-600
  "
>
  <option>Select an option</option>
</select>
```

**Checkbox/Radio Styling:**
```jsx
<label className="flex items-center gap-2">
  <input
    type="checkbox"
    className="
      w-4 h-4 rounded
      border-neutral-300
      focus:ring-2 focus:ring-primary
      cursor-pointer
    "
  />
  <span className="text-sm">Option</span>
</label>
```

**Error State Styling:**
```jsx
<div>
  <input
    aria-invalid="true"
    className="
      w-full px-4 py-2 border rounded-lg
      border-error focus:ring-error
    "
  />
  <p className="text-sm text-error mt-1">This field is required</p>
</div>
```

---

## 15. Table Styling System

**RULE:** Tables use consistent styling patterns for readability, mobile responsiveness, and data density.

**Table Architecture:**
```jsx
<div className="overflow-x-auto">
  <table className="w-full text-sm">
    <thead className="bg-gray-100 dark:bg-gray-800">
      <tr>
        <th className="px-4 py-3 text-left font-semibold text-gray-900 dark:text-white">
          Header
        </th>
      </tr>
    </thead>
    <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
      <tr className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
        <td className="px-4 py-3 text-gray-900 dark:text-white">Data</td>
      </tr>
    </tbody>
  </table>
</div>
```

**Mobile Card Variant:**
```jsx
<div className="flex flex-col md:hidden gap-4">
  {rows.map(row => (
    <div key={row.id} className="bg-white dark:bg-gray-800 border rounded-lg p-4">
      <div className="flex justify-between mb-2">
        <span className="font-medium text-gray-600 dark:text-gray-300">Field:</span>
        <span className="font-semibold text-gray-900 dark:text-white">{row.field}</span>
      </div>
      <div className="flex justify-between mb-2">
        <span className="font-medium text-gray-600 dark:text-gray-300">Area:</span>
        <span className="font-semibold text-gray-900 dark:text-white">{row.area}</span>
      </div>
    </div>
  ))}
</div>
```

**Sortable Column Styling:**
```jsx
<th className="
  px-4 py-3 text-left
  cursor-pointer
  hover:bg-gray-200 dark:hover:bg-gray-700
  select-none
">
  <div className="flex items-center gap-2">
    <span>Column</span>
    {isSorted && <ChevronIcon direction={sortDir} />}
  </div>
</th>
```

---

## 16. Z-Index Governance

**RULE:** Z-index hierarchy is centralized and enforced. No arbitrary z-index values allowed.

**Z-Index Scale:**
```jsx
// tailwind.config.js
const zIndex = {
  'dropdown': '50',
  'sticky': '100',
  'fixed': '200',
  'modal-backdrop': '300',
  'modal': '400',
  'popover': '500',
  'tooltip': '600',
}

export default {
  theme: { zIndex }
}
```

**Application:**
- **Base:** `z-0` (default)
- **Sticky Headers:** `sticky z-sticky`
- **Fixed Navigation:** `fixed z-fixed`
- **Modal Backdrop:** `z-modal-backdrop`
- **Modal Dialogs:** `z-modal`
- **Dropdowns:** `absolute z-dropdown`
- **Popovers:** `z-popover`
- **Tooltips:** `z-tooltip`

**Example:**
```jsx
<div className="fixed inset-0 bg-black/50 z-modal-backdrop" />
<div className="fixed inset-0 flex items-center justify-center z-modal">
  <dialog className="bg-white rounded-lg shadow-xl p-6">
    {/* Content */}
  </dialog>
</div>
```

---

## 17. Elevation & Shadow Rules

**RULE:** Shadows are semantic, responsive, and elevation-based. Shadow usage follows strict hierarchy.

**Shadow Scale:**
```jsx
// tailwind.config.js
const boxShadow = {
  'sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  'md': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
  'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
  'xl': '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
  'none': 'none',
}

export default {
  theme: { boxShadow }
}
```

**Elevation Application:**
- **Base elements:** `shadow-sm` for subtle depth
- **Cards:** `shadow-md` for content containers
- **Floating elements:** `shadow-lg` for dropdowns, modals
- **Focus states:** `shadow-xl` for emphasis

**Example:**
```jsx
<div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow">
  {/* Card content */}
</div>
```

**Dark Mode Shadow:**
```css
@media (prefers-color-scheme: dark) {
  .shadow-md {
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
  }
}
```

---

## 18. Animation Utility Usage

**RULE:** Animations use Tailwind utilities. Custom animations are governed and performance-tested.

**Built-in Animations:**
- `animate-spin`: loading spinners
- `animate-pulse`: skeleton loading
- `animate-bounce`: attention-seeking
- Transition utilities: `transition-all`, `duration-300`, `ease-in-out`

**Custom Animation Configuration:**
```jsx
// tailwind.config.js
export default {
  theme: {
    extend: {
      animation: {
        'slide-in': 'slideIn 0.3s ease-out',
        'fade-in': 'fadeIn 0.2s ease-in',
        'scale-bounce': 'scaleBounce 0.6s ease-in-out',
      },
      keyframes: {
        slideIn: {
          '0%': { transform: 'translateX(-100%)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        scaleBounce: {
          '0%, 100%': { transform: 'scale(1)' },
          '50%': { transform: 'scale(1.05)' },
        },
      },
    },
  },
}
```

**Reduced Motion Accessibility:**
```jsx
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## 19. Accessibility Styling

**RULE:** All styling must support WCAG 2.1 AA standards. Contrast, focus, and readability are mandatory.

**Contrast Rules:**
- Text on color: 4.5:1 minimum
- Large text: 3:1 minimum
- Non-text elements: 3:1 minimum

**Focus Styling:**
```jsx
// GOOD: visible focus indicator
<button className="
  focus:outline-none
  focus:ring-2 focus:ring-offset-2 focus:ring-primary
">

// BAD: invisible focus
<button className="focus:outline-none">
```

**Color Dependency:**
- Never use color alone to convey information
- Combine color with icons, patterns, or text
- Example: Error states use `border-error` + `text-error` + error icon

**Text Readability:**
- Minimum font size: `text-sm` (14px)
- Line height: `leading-relaxed` (1.625) for body text
- Maximum line length: 65-80 characters
- Letter spacing: `tracking-normal` (0.025em)

**Example: Accessible Form**
```jsx
<div>
  <label htmlFor="field-input" className="block text-sm font-medium mb-1">
    Field Name <span className="text-error" aria-label="required">*</span>
  </label>
  <input
    id="field-input"
    aria-invalid={hasError}
    aria-describedby={hasError ? 'error-msg' : undefined}
    className="w-full px-3 py-2 border rounded focus:ring-2 focus:ring-primary"
  />
  {hasError && (
    <p id="error-msg" className="mt-1 text-sm text-error" role="alert">
      This field is required
    </p>
  )}
</div>
```

---

## 20. Performance Constraints

**RULE:** Tailwind utilities must not cause performance degradation. CSS file size and runtime performance are monitored.

**Performance Rules:**
- Avoid unused utilities in production build
- Use PurgeCSS/Tailwind content configuration
- Monitor CSS file size: target < 50KB (gzipped)
- Avoid complex selectors that impact paint performance
- Test on low-end devices: target 60fps animations

**Build Configuration:**
```jsx
// tailwind.config.js
export default {
  content: [
    './src/**/*.{js,jsx,ts,tsx}',
    './public/*.html',
  ],
  // Optimize for production
  safelist: [],
  plugins: [],
}
```

**Performance Monitoring:**
- Run `tailwind build` and check output size
- Profile animations in DevTools Performance tab
- Test on Lighthouse CI
- Monitor bundle size in CI/CD

---

## 21. Tailwind + shadcn Integration

**RULE:** shadcn components use Tailwind utilities. No conflicting styling allowed.

**Integration Rules:**
- shadcn components export Tailwind classes
- Domain wrappers add utilities without conflicts
- Use `cn()` utility to merge classes safely

**Example:**
```jsx
// Using shadcn Button with Tailwind
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

export const SubmitButton = ({ className, ...props }) => (
  <Button
    className={cn(
      'uppercase font-semibold',
      className
    )}
    {...props}
  />
)
```

**Conflict Resolution:**
- Never override shadcn component base styles
- Use variant system for styling variations
- Extend through wrapper components

---

## 22. AI Safety Rules

**RULE:** AI agents must follow these constraints when generating Tailwind code.

**Forbidden Actions:**
- Use arbitrary values (e.g., `w-[347px]`, `mb-[23px]`)
- Generate inline styles
- Create new CSS beyond Tailwind utilities
- Use directional utilities (left/right) without RTL awareness
- Mix mobile and desktop breakpoints
- Create z-index values outside governance scale
- Add colors outside design tokens
- Use undocumented or deprecated utilities

**Required Actions:**
- Use predefined spacing scale
- Apply mobile-first breakpoints
- Use RTL-safe utilities (start/end)
- Reference design tokens and CSS variables
- Include dark mode utilities
- Add accessibility features (focus rings, ARIA attributes)
- Validate component responsiveness on mobile
- Test theme consistency

**Example: AI-Safe Component Generation**
```jsx
// GOOD: AI-safe pattern
<button className="
  px-4 py-2 bg-primary text-white rounded-lg font-medium
  hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-primary
  transition-colors duration-200
  dark:bg-primary-dark dark:hover:bg-primary
  disabled:opacity-50 disabled:cursor-not-allowed
">
  {children}
</button>

// BAD: AI-unsafe pattern
<button style={{padding: '8px 16px', backgroundColor: '#2563eb'}}>
```

---

## 23. Forbidden Anti-Patterns

**RULE:** These patterns are explicitly forbidden and enforced through linting.

**Anti-Pattern 1: Random Spacing**
```jsx
// FORBIDDEN
<div className="mb-[17px] p-[22px]">

// REQUIRED
<div className="mb-4 p-6">
```

**Anti-Pattern 2: Color Magic**
```jsx
// FORBIDDEN
<div className="text-[#a4c639] bg-[#2d5a3d]">

// REQUIRED
<div className="text-primary bg-secondary">
```

**Anti-Pattern 3: Desktop-First Responsiveness**
```jsx
// FORBIDDEN
<div className="hidden lg:flex md:flex sm:block">

// REQUIRED
<div className="flex md:hidden lg:flex">
```

**Anti-Pattern 4: Inline Styles**
```jsx
// FORBIDDEN
<div style={{padding: '16px', color: '#1f2937'}}>

// REQUIRED
<div className="p-4 text-gray-900">
```

**Anti-Pattern 5: Utility Explosion**
```jsx
// FORBIDDEN
<div className="flex items-center justify-between gap-2 rounded-lg border border-gray-200 bg-white p-4 shadow-md hover:shadow-lg transition-shadow ... [30 more classes]">

// REQUIRED
<div className="flex items-center justify-between gap-2 rounded-lg border border-gray-200 bg-white p-4 shadow-md hover:shadow-lg transition-shadow">
```

**Anti-Pattern 6: Uncontrolled Responsive Explosion**
```jsx
// FORBIDDEN
<div className="w-full md:w-1/2 lg:w-1/3 xl:w-1/4 2xl:w-1/5 sm:hidden">

// REQUIRED
<div className="w-full md:w-1/2 lg:w-1/3">
```

---

## 24. Real Agricultural ERP Examples

### Example 1: Olive Field Dashboard Card
```jsx
// Good: Semantic, responsive, accessible
<div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 md:p-6">
  <div className="flex justify-between items-start mb-4">
    <h3 className="text-lg md:text-xl font-semibold text-gray-900 dark:text-white">
      Olive Field #2
    </h3>
    <span className="px-3 py-1 bg-success/10 text-success text-sm font-medium rounded-lg">
      Healthy
    </span>
  </div>
  
  <div className="grid grid-cols-2 gap-4 mb-6">
    <div>
      <p className="text-sm text-gray-600 dark:text-gray-400">Area</p>
      <p className="text-2xl font-bold text-gray-900 dark:text-white">45.2 ha</p>
    </div>
    <div>
      <p className="text-sm text-gray-600 dark:text-gray-400">Soil Moisture</p>
      <p className="text-2xl font-bold text-gray-900 dark:text-white">68%</p>
    </div>
  </div>
  
  <button className="w-full px-4 py-2 bg-primary text-white font-medium rounded-lg hover:bg-primary-dark transition-colors dark:bg-primary-dark dark:hover:bg-primary">
    View Details
  </button>
</div>
```

### Example 2: Mobile Worker Form
```jsx
<form className="flex flex-col gap-4 p-4">
  <label className="flex flex-col gap-2">
    <span className="text-sm font-medium text-gray-900 dark:text-white">
      Harvest Date
    </span>
    <input
      type="date"
      className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary dark:bg-gray-800 dark:border-gray-600"
    />
  </label>
  
  <label className="flex flex-col gap-2">
    <span className="text-sm font-medium text-gray-900 dark:text-white">
      Quantity (kg)
    </span>
    <input
      type="number"
      inputMode="numeric"
      className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary dark:bg-gray-800 dark:border-gray-600"
    />
  </label>
  
  <button
    type="submit"
    className="mt-4 py-3 px-6 bg-primary text-white font-semibold rounded-lg hover:bg-primary-dark transition-colors"
  >
    Submit Report
  </button>
</form>
```

### Example 3: Supervisor Inventory Table
```jsx
<div className="overflow-x-auto">
  <table className="w-full text-sm">
    <thead className="bg-gray-100 dark:bg-gray-800">
      <tr>
        <th className="px-4 py-3 text-left font-semibold text-gray-900 dark:text-white">
          Product
        </th>
        <th className="px-4 py-3 text-right font-semibold text-gray-900 dark:text-white">
          Quantity
        </th>
        <th className="px-4 py-3 text-right font-semibold text-gray-900 dark:text-white">
          Status
        </th>
      </tr>
    </thead>
    <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
      {items.map(item => (
        <tr key={item.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
          <td className="px-4 py-3 text-gray-900 dark:text-white font-medium">
            {item.name}
          </td>
          <td className="px-4 py-3 text-right text-gray-900 dark:text-white">
            {item.qty}
          </td>
          <td className="px-4 py-3 text-right">
            <span className={cn(
              'px-3 py-1 rounded-lg text-sm font-medium',
              item.status === 'low' && 'bg-warning/10 text-warning',
              item.status === 'ok' && 'bg-success/10 text-success',
            )}>
              {item.status}
            </span>
          </td>
        </tr>
      ))}
    </tbody>
  </table>
</div>
```

---

## 25. Enforcement Checklist

**Before Merging PR:**
- [ ] No arbitrary Tailwind values detected (`w-[123px]`, `mb-[17px]`)
- [ ] All spacing uses design scale (`space-1` through `space-10`)
- [ ] All colors reference design tokens (not hardcoded hex)
- [ ] Mobile-first responsive utilities applied
- [ ] RTL utilities used (start/end, not left/right)
- [ ] Dark mode variants included on all components
- [ ] Focus indicators visible and accessible
- [ ] Contrast ratios meet WCAG AA standards
- [ ] No inline styles (style={} forbidden)
- [ ] Component renders correctly on mobile, tablet, desktop
- [ ] No z-index values outside governance scale
- [ ] Animation performance tested on low-end device

**Runtime Checks:**
```bash
# Check for arbitrary values
npx tailwind-enforce-tokens src/

# Check for inline styles
grep -r "style={{" src/

# Build and check CSS file size
npm run build
du -h dist/output.css  # Should be < 50KB gzipped
```

---

## Summary

ATLS Tailwind governance establishes utility-first, token-driven, mobile-first styling that prevents chaos, supports RTL and dark mode, and enables white-label customization. All styling must use predefined utilities and tokens. AI agents must follow strict constraints. Responsive behavior is mobile-first. Theme customization flows through CSS variables. Dark mode is comprehensive. Enforcement is automatic through linting and CI/CD. Agricultural field workers receive consistent, accessible, performant UX.

## Last Updated
2026-05-12
