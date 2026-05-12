# AI DEVELOPMENT RULES

> **This is the highest-authority engineering document in the ATLS project.**
> Every AI agent MUST read this file in full before writing a single line of code.
> Violations of these rules constitute architecture corruption and are unacceptable.

---

## Last Updated
2026-05-12

## Status
- [x] Active — Enforced on all AI agents

---

## 1. Core Engineering Philosophy

1.1. ATLS is a **production-grade, white-label agricultural ERP**. Every decision must reflect enterprise standards.

1.2. Code is written **once and reused everywhere**. Duplication is a critical failure.

1.3. **Domain-Driven Architecture** governs all module boundaries. No domain bleeds into another.

1.4. The system is **Arabic-first, mobile-first, and AI-agent-driven**. Every feature must be designed with these three constraints from day one.

1.5. Every component, view, service, serializer, and model must be **independently replaceable** without cascading breakage.

1.6. **Correctness over cleverness.** Write the simplest, most readable solution that satisfies the requirement.

1.7. **No feature is complete without error handling, validation, loading states, and RTL support.**

---

## 2. AI Agent Responsibilities

2.1. The AI agent is a **senior engineer**, not a code monkey. It must challenge bad requirements and propose better alternatives.

2.2. Before writing code, the agent MUST:
- Identify the domain the task belongs to.
- Check if similar logic already exists anywhere in the codebase.
- Identify all files that will be affected.
- Confirm the UI pattern being followed.

2.3. The agent MUST NOT:
- Invent new patterns not established in this document.
- Write code outside the assigned task scope.
- Leave TODOs, stubs, or placeholder logic in production files.
- Skip validation, error handling, or RTL support.
- Rewrite working code without explicit instruction.

2.4. **Clarification Policy (anti-loop rule).** The agent MUST distinguish between uncertainty types:

| Uncertainty Type | Action |
|---|---|
| Low-risk (styling, naming, minor layout) | Proceed with best judgement. Document the decision. |
| Medium-risk (data shape, API param) | Apply safe default, flag assumption in a comment. |
| High-risk (architecture change, security, data loss, new dependency) | **STOP. Ask. Do not proceed.** |
| Business-critical (permission model, pricing logic, ownership rules) | **STOP. Ask. Do not proceed.** |

The agent must NEVER loop multiple clarifying questions in the same turn. Group all questions into a single, numbered list.

2.5. After completing a task, the agent MUST update `08_EXECUTION/CURRENT_PROGRESS.md` and `08_EXECUTION/CHANGELOG.md`.

---

## 3. Architecture Protection Rules

3.1. **Domain isolation is absolute.** A domain module must never import from another domain module directly. Cross-domain communication goes through shared services or API contracts only.

3.2. **No circular imports.** Ever. Structure imports to flow in one direction: `constants → utils → services → components → pages`.

3.3. **No God files.** No single file may contain more than one primary responsibility. A 500-line file is a red flag. A 1000-line file is a violation.

3.4. **No inline business logic in components.** Components render UI. Services handle logic. This boundary is sacred.

3.5. **No direct API calls from components.** All API communication goes through the service layer (`/services/`).

3.6. **No hardcoded data in UI files.** All static options, types, labels, and enumerations belong in `/constants/` or fetched from API.

3.7. **No global state for local concerns.** If a state is only needed inside one component tree, keep it local.

3.8. The `shared/` directory contains only **truly universal** utilities and components. Domain-specific code must never live in `shared/`.

---

## 4. Frontend Rules

4.1. **File structure per feature:**
```
features/{domain}/
  components/       # UI components for this domain
  pages/            # Route-level page components
  services/         # API calls and data transformation
  hooks/            # Custom React hooks
  constants/        # Static data, enums, labels
  types/            # TypeScript/JSDoc type definitions
  utils/            # Domain-specific helpers
```

4.2. Every page component must be a **thin orchestrator**: fetch data, handle loading/error states, pass props to child components. No logic inside page files.

4.3. All lists must implement **pagination or infinite scroll**. Never render an unbounded list.

4.4. All data-fetching must handle three states explicitly: `loading`, `error`, and `empty`.

4.5. Never use `index.js` as a component file. Every component file must be named after the component it exports.

4.6. **No anonymous default exports.** Every export must be a named function or class.

4.7. All user-facing strings must be stored in the i18n translation layer. No raw Arabic or English strings directly in JSX.

4.8. Components must not exceed **200 lines**. Extract sub-components aggressively.

4.9. Every interactive element must have a unique, descriptive `id` and `aria-label`.

---

## 5. Backend Rules

5.1. **Django apps map to domains.** One Django app per domain. No exceptions.

5.2. **Fat models, thin views.** Business logic lives in the service layer or model methods. ViewSets are routing controllers only.

5.3. **Service layer is mandatory.** All business logic that involves more than one model or any side effect must be encapsulated in a service function inside `services.py`.

5.4. **ViewSets must not contain business logic.** They call services, serialize results, and return responses.

5.5. All queryset filtering must be done in the service layer, not inline in views.

5.6. All write operations (create, update, delete) must go through services that enforce validation and business rules.

5.7. All API responses must follow the standard envelope:
```json
{
  "success": true,
  "data": {},
  "message": "Optional human-readable message",
  "errors": null
}
```

5.8. All list endpoints must support `page`, `page_size`, `search`, and `ordering` query parameters.

5.9. Never use `objects.all()` without explicit pagination in list views.

5.10. All database writes must be wrapped in `transaction.atomic()`.

---

## 6. Database Rules

6.1. Every model must have:
- `created_at` (auto timestamp)
- `updated_at` (auto timestamp)
- `is_active` (soft delete flag, default `True`)
- `created_by` (FK to User)

6.2. **No hard deletes.** All deletions are soft deletes via `is_active = False`.

6.3. All foreign keys must define `on_delete` explicitly. `CASCADE` requires written justification in a comment.

6.4. All models must define `__str__`, `Meta.verbose_name`, and `Meta.verbose_name_plural`.

6.5. All querysets must use `select_related` and `prefetch_related` to prevent N+1 queries.

6.6. Database indexes must be explicitly defined on all fields used in filtering, ordering, or joining.

6.7. All migrations must be reviewed before applying. Auto-generated migrations must be inspected for unintended drops.

6.8. Never write raw SQL unless ORM cannot express the query. Raw SQL must be documented with justification.

6.9. All numeric fields for money or area must use `DecimalField` with explicit `max_digits` and `decimal_places`.

---

## 7. Mobile-First Rules

7.1. Every UI component is designed for **mobile screen first** (320px minimum width), then scaled up.

7.2. Touch targets must be a minimum of **44×44px**.

7.3. Modals and drawers must be **full-screen or bottom-sheet** on mobile.

7.4. No hover-only interactions. All interactions must work with touch.

7.5. Tables must transform to **card layouts** on mobile. Never show a horizontal-scrolling table on mobile without explicit user intent.

7.6. All forms must use appropriate mobile keyboard types: `inputMode="numeric"`, `inputMode="tel"`, etc.

7.7. Font sizes must never be below **14px** on mobile.

7.8. Spacing must use the Tailwind responsive scale. Never hardcode pixel values.

---

## 8. RTL Rules

8.1. The application is **Arabic-first RTL**. All layouts must be designed in RTL by default.

8.2. Use `dir="rtl"` on the root HTML element. Never set direction per-component unless overriding for a specific reason (e.g., code blocks, numbers).

8.3. Use **logical CSS properties** only: `ms-`, `me-`, `ps-`, `pe-`, `start-`, `end-`. Never use `left`, `right`, `pl-`, `pr-`, `ml-`, `mr-` in Tailwind classes.

8.4. All flex containers must use `flex-row` in RTL context. Tailwind's RTL utilities (`rtl:`) must be used for directional overrides.

8.5. Icons that carry directional meaning (arrows, chevrons) must be **mirrored** in RTL. Use CSS `transform: scaleX(-1)` wrapped in an RTL utility class.

8.6. All animations and transitions must respect RTL direction (e.g., slide-in from the right in RTL).

8.7. All text alignment defaults to `text-start` (not `text-left`).

8.8. Number formatting must account for locale. Arabic numerals are used where appropriate.

8.9. **Framer Motion RTL Rules:**
- Slide animations that travel horizontally MUST invert their `x` values in RTL context.
- Use a custom `useRTLMotion()` hook that reads document direction and returns corrected variant values.
- Never hardcode `x: -300` or `x: 300` in motion variants. Always compute from RTL context.
- Example pattern:
```tsx
const { slideIn } = useRTLMotion(); // returns x: 300 in RTL, x: -300 in LTR
<motion.div variants={slideIn} />
```

8.10. **Radix UI RTL Rules:**
- All Radix primitives (`DropdownMenu`, `Popover`, `Tooltip`, `Select`) must have `dir="rtl"` passed explicitly when the app is in RTL mode.
- Wrap all Radix components in a `<DirectionProvider dir={dir}>` at the app root level.
- Never rely on Radix's auto-detection — always pass direction explicitly.

8.11. **Animation Direction Enforcement:**
- Page enter transitions: slide from `end` side (right in LTR, left in RTL).
- Drawer/Sheet open: slide from `end` in RTL.
- Delete/dismiss gestures: swipe toward `start` in RTL.
- Progress indicators: fill from `start` to `end`.
- Violation of this rule produces directionally inverted UX, which is a critical bug.

---

## 9. Tailwind Rules

9.1. **No arbitrary values** (`w-[347px]`) unless mathematically unavoidable and documented with a comment.

9.2. **No inline `style` attributes** on JSX elements. All styles go through Tailwind classes.

9.3. Use the **design token system**. Colors, spacing, and font sizes must reference the configured Tailwind theme, not raw values.

9.4. Class strings must be ordered: Layout → Box Model → Typography → Visual → Animation. Use `prettier-plugin-tailwindcss` to enforce order automatically.

9.5. Repeated class combinations of 4+ classes must be extracted into a component or a `@apply` utility in the CSS layer.

9.6. **Dark mode** must be considered for all color classes. Use `dark:` variants systematically.

9.7. Never use `!important` overrides (`!text-red-500`). Fix the specificity issue at the source.

---

## 10. shadcn/ui Rules

10.1. shadcn/ui components are the **only permitted UI primitives**. Do not introduce other component libraries.

10.2. shadcn components must **never be modified directly** in their source files inside `components/ui/`. Create wrapper components in the feature's `components/` folder.

10.3. All forms must use `shadcn/ui Form` with `react-hook-form` and `zod` validation. No custom form wiring.

10.4. All dialogs and sheets must use `shadcn/ui Dialog` or `Sheet`. No custom modal implementations.

10.5. All data tables must use `shadcn/ui Table` or `DataTable` pattern. No ad-hoc table markup.

10.6. All dropdowns must use `shadcn/ui Select` or `DropdownMenu`. No raw `<select>` elements.

10.7. All toast notifications must use `shadcn/ui Sonner` (or configured toaster). No custom notification systems.

10.8. When extending a shadcn component, create a new component file that wraps it: `components/{domain}/{ComponentName}.tsx`.

---

## 11. API Rules

11.1. All API routes follow REST conventions:
- `GET /api/{domain}/{resource}/` — List
- `POST /api/{domain}/{resource}/` — Create
- `GET /api/{domain}/{resource}/{id}/` — Retrieve
- `PUT /api/{domain}/{resource}/{id}/` — Full update
- `PATCH /api/{domain}/{resource}/{id}/` — Partial update
- `DELETE /api/{domain}/{resource}/{id}/` — Soft delete

11.2. All API endpoints must require authentication unless explicitly marked public.

11.3. All API endpoints must enforce **role-based permission classes**.

11.4. All endpoints must return appropriate HTTP status codes. `200` is not the default for all success responses.

11.5. All write endpoints must return the full serialized updated object, not just a success message.

11.6. API versioning prefix: `/api/v1/`. Never change this without a migration plan.

11.7. All filtering, searching, and ordering must be done server-side. Never ship full datasets to the frontend for client-side filtering.

11.8. Bulk operation endpoints must be purpose-built and explicitly named: `/api/{domain}/{resource}/bulk_update/`.

---

## 12. Service Layer Rules

12.1. Every domain must have a `services.py` file containing all business logic for that domain.

12.2. Service functions must be **pure and testable**: given the same inputs, they produce the same outputs and side effects.

12.3. Service functions must not call other services from different domains directly. Use events or shared utilities.

12.4. Every service function signature must be explicit. No `**kwargs` catch-alls without documentation.

12.5. All service functions that modify data must:
- Be wrapped in `transaction.atomic()`
- Create an audit log entry via the Audit domain service
- Return the modified object

12.6. Service functions must raise typed, descriptive exceptions. Use Django's `ValidationError` for business rule violations.

12.7. Service functions must never directly return ORM querysets. Return lists, dicts, or model instances only.

---

## 13. File Naming Rules

13.1. **Frontend:**
- Components: `PascalCase.tsx` (e.g., `HarvestForm.tsx`)
- Hooks: `camelCase.ts` prefixed with `use` (e.g., `useSeasonData.ts`)
- Services: `camelCase.ts` suffixed with `Service` (e.g., `harvestService.ts`)
- Pages: `PascalCase.tsx` suffixed with `Page` (e.g., `HarvestPage.tsx`)
- Constants: `SCREAMING_SNAKE_CASE.ts` (e.g., `OPERATION_TYPES.ts`)
- Types: `PascalCase.types.ts` (e.g., `Harvest.types.ts`)

13.2. **Backend:**
- Models: `models.py` (standard Django)
- Serializers: `{domain}_serializers.py`
- Views: `{domain}_views.py`
- Services: `{domain}_services.py`
- URLs: `{domain}_urls.py`
- Tests: `test_{domain}_{unit}.py`

13.3. **Documentation:**
- All caps with underscores: `DOMAIN_NAME.md`

13.4. Never use spaces or special characters in file names. Hyphens only in asset filenames (images, etc.).

---

## 14. Folder Structure Rules

14.1. **Frontend root structure:**
```
src/
  app/              # App-level config, routing, providers
  features/         # Domain feature modules
  shared/           # Truly universal components and utilities
  lib/              # Third-party library configurations
  assets/           # Static assets
  styles/           # Global CSS
  constants/        # App-wide constants
  types/            # App-wide type definitions
```

14.2. **Backend root structure:**
```
{project}/
  {domain}/
    models.py
    {domain}_serializers.py
    {domain}_views.py
    {domain}_services.py
    {domain}_urls.py
    admin.py
    apps.py
    migrations/
    tests/
```

14.3. Never place files at the root of `src/` or the Django project root. All files belong to a module.

14.4. Shared utilities that grow beyond 3 functions must be extracted into their own named file, not appended to `utils.ts`.

---

## 15. State Management Rules

15.1. **Local state first.** Only escalate to global state when genuinely needed across disconnected components.

15.2. **Server state** (API data) is managed by **React Query**. Do not use `useState` + `useEffect` for data fetching.

15.3. **UI state** (modals, drawers, tabs) is managed locally with `useState` or `useReducer`.

15.4. **Global app state** (user session, permissions, active farm) is managed by Zustand or Context API. Not Redux.

15.5. No state is derived on render. Computed values must be memoized with `useMemo`.

15.6. No state synchronization between global store and React Query cache. They serve different purposes.

15.7. Invalidate React Query cache after all mutations. Never manually update cached data unless performance-critical.

---

## 16. Error Handling Rules

16.1. Every API call must have a `.catch()` handler or `onError` callback. Silent failures are forbidden.

16.2. All backend exceptions must be caught at the view level and returned as structured error responses.

16.3. User-facing error messages must be:
- In Arabic (primary)
- Actionable ("Try again" or "Contact support" where appropriate)
- Specific (not "An error occurred")

16.4. All validation errors from the backend must be mapped to the corresponding form field. Global form errors are a last resort.

16.5. Network errors must show a retry option when possible.

16.6. All unhandled frontend exceptions must be caught by an Error Boundary and logged.

16.7. Never expose stack traces, internal server errors, or raw exception messages to the user.

16.8. All 404s must render the domain-appropriate empty state, not a generic error page.

---

## 17. Form Handling Rules

17.1. All forms use `react-hook-form` with `zodResolver`. No exceptions.

17.2. All forms must define a Zod schema in a separate `{FormName}.schema.ts` file.

17.3. All form fields must show:
- Label (in Arabic)
- Placeholder
- Validation error message (inline, below field)
- Required indicator

17.4. Forms must disable the submit button while submitting and show a loading indicator.

17.5. After a successful submit, the form must either:
- Navigate to the detail page of the created resource, OR
- Reset and show a success toast

17.6. Large forms (6+ fields) must be broken into logical sections with visual separators.

17.7. All select/dropdown fields must have a searchable interface when options exceed 8 items.

17.8. Date pickers must support Arabic locale and Hijri calendar display where required.

---

## 18. Validation Rules

18.1. **Frontend validation** is for user experience only (fast feedback). It must never be the only validation layer.

18.2. **Backend validation** is the authoritative layer. All business rules must be enforced in the service layer.

18.3. Zod schemas must mirror the backend serializer validation rules exactly.

18.4. All required fields must be explicitly marked `z.string().min(1)` or equivalent. Never rely on implicit required behavior.

18.5. Numeric fields must define min/max boundaries.

18.6. No regex validation without a clear comment explaining the pattern.

18.7. Custom Zod refinements must have descriptive error messages in Arabic.

18.8. Backend serializers must use `validate_{field}` and `validate` methods for cross-field validation, not view-level checks.

---

## 19. Dynamic Engine Rules

**Engine Authority Hierarchy (top = highest authority):**
```
[1] Role-Permission Engine      — controls WHO can do WHAT
[2] Configuration Engine        — controls WHAT features exist
[3] Theme Engine                — controls HOW things look
[4] Dynamic Hierarchy Engine    — controls structural DEPTH
[5] Dynamic Form Engine         — controls WHAT data is collected
[6] Dashboard Config Engine     — controls WHAT is displayed
```
No lower-ranked engine may override a higher-ranked engine's output.

19.1. The Dynamic Form Engine controls all configurable forms. No form that requires admin configuration may bypass this engine. The engine must support field ordering, conditional visibility, field type overrides, and required/optional toggles per tenant.

19.2. The Dynamic Hierarchy Engine controls all tree-structured data (farm → block → row → subunit). Never hardcode hierarchy levels. The number of hierarchy levels is a tenant configuration value, not a code constant.

19.3. The Role-Permission Engine is the **sole authority** for access control. Never check roles directly in component logic (`if user.role === 'ADMIN'`). Always use the `usePermission('action:resource')` hook on the frontend and `HasPermission` classes on the backend. Permission strings follow the pattern `{action}:{domain}:{resource}`.

19.4. The Theme Engine controls all white-label appearance. Never hardcode brand colors, logos, fonts, or tenant-specific copy. The Theme Engine must inject CSS custom properties at the `:root` level per tenant.

19.5. The Dashboard Configuration Engine controls all widget placement and visibility. Never render dashboard widgets outside this engine's control. Widget configuration (position, size, data source) is a per-role, per-tenant database record.

19.6. All engines must expose a configuration API that admins can control without code changes. Configuration APIs are protected behind the `SUPER_ADMIN` or `TENANT_ADMIN` role.

19.7. Engine configurations must be stored in the database, not in code constants. Engine defaults may be seeded via migrations but must be overridable.

19.8. **Engine Bypass is a Critical Violation.** Any code that renders, filters, or controls access without routing through the appropriate engine must be flagged as a P0 bug and corrected before merge.

---

## 20. Forbidden Actions

> These are absolute prohibitions. No exception. No override.

- ❌ NEVER hard-delete database records.
- ❌ NEVER write business logic inside a React component.
- ❌ NEVER call the API directly from a component. Use the service layer.
- ❌ NEVER import from another domain's internals.
- ❌ NEVER use `any` type in TypeScript without a documented exception.
- ❌ NEVER use `console.log` in production code.
- ❌ NEVER use `!important` in CSS/Tailwind.
- ❌ NEVER use directional CSS properties (`left`, `right`, `pl-`, `pr-`).
- ❌ NEVER modify shadcn/ui source files in `components/ui/`.
- ❌ NEVER ship a feature without loading, error, and empty states.
- ❌ NEVER ship a list without pagination.
- ❌ NEVER expose raw backend errors to the user.
- ❌ NEVER write a migration without reviewing it first.
- ❌ NEVER use `objects.all()` in production views without pagination.
- ❌ NEVER bypass the Role-Permission Engine for access checks.
- ❌ NEVER leave `TODO` comments in production files.
- ❌ NEVER hardcode user IDs, farm IDs, or any entity IDs in code.
- ❌ NEVER commit secrets, tokens, or environment-specific values to the repository.
- ❌ NEVER write raw SQL without documented justification and review.
- ❌ NEVER introduce a new third-party library without architectural review and documentation.

---

## 21. Anti-Patterns

> Patterns that have been observed and explicitly banned:

- **Prop drilling beyond 2 levels.** Extract to context or Zustand.
- **Monolithic page components.** Decompose into sub-components.
- **Copy-pasting logic between files.** Extract to a shared utility.
- **`useEffect` for data fetching.** Use React Query.
- **Conditional rendering of completely different UIs from one component.** Split into separate components.
- **`any` as a type escape hatch.** Define the proper type.
- **Optimistic updates without rollback.** Handle failure states.
- **Overloaded serializers.** A serializer for listing is different from one for creating.
- **ViewSets with `if request.method` branches.** Use separate actions or viewsets.
- **Putting migrations in git with unresolved conflicts.** Always squash before merge.
- **Using `pk` or `id` as a URL segment without validation.** Always validate entity ownership.

---

## 22. Performance Rules

22.1. All list views must use server-side pagination. Default page size: `20`. Maximum: `100`.

22.2. All images must be served in WebP format with responsive `srcset`.

22.3. All React components that accept complex props must be wrapped with `React.memo` if they appear in large lists.

22.4. All expensive computations must be wrapped in `useMemo`. All stable callbacks in `useCallback`.

22.5. Code splitting is mandatory for all domain feature modules. Use `React.lazy()` for page-level imports.

22.6. All database queries in list endpoints must be profiled. No query may exceed 100ms in production.

22.7. Django Debug Toolbar must be used during development to catch N+1 queries before merge.

22.8. All static assets must be compressed and served from CDN in production.

22.9. Core Web Vitals targets: LCP < 2.5s, FID < 100ms, CLS < 0.1.

---

## 23. Clean Code Rules

23.1. **One function, one responsibility.** A function that does more than one thing must be split.

23.2. **Functions must be named after what they do.** `getUserFarms`, not `getData`.

23.3. **Boolean variables must be named with `is`, `has`, `can`, `should` prefixes.**

23.4. **No magic numbers.** Extract all numeric constants to named constants.

23.5. **No nested ternaries.** Maximum one level of ternary. Use early returns or if/else for complex conditions.

23.6. **Function arguments beyond 3 should be an options object.**

23.7. **Comments explain WHY, not WHAT.** The code explains what. If you need to explain what, rewrite the code.

23.8. **Dead code is deleted immediately.** Commented-out code is a code smell. Use git history.

---

## 24. Documentation Rules

24.1. Every domain model must have a docstring explaining its purpose and key relationships.

24.2. Every service function must have a docstring specifying: purpose, parameters, return value, and exceptions raised.

24.3. Every custom hook must have a JSDoc comment explaining its purpose, parameters, and return shape.

24.4. Every API endpoint must be documented in `09_REFERENCE/API_REFERENCE.md`.

24.5. Every schema change must be reflected in `09_REFERENCE/DATABASE_REFERENCE.md`.

24.6. Every new domain or engine must have its corresponding document in `docs_v2/` updated.

24.7. All `docs_v2/` documents must have their `Last Updated` field maintained.

---

## 25. Progress Update Rules

25.1. After every completed task, update `08_EXECUTION/CURRENT_PROGRESS.md` with:
- Task name
- What was completed
- Files modified
- Known issues or blockers

25.2. After every completed task, append an entry to `08_EXECUTION/CHANGELOG.md`:
```
## [YYYY-MM-DD] {Task Name}
- Added: ...
- Modified: ...
- Fixed: ...
```

25.3. Tech debt discovered during a task must be logged in `08_EXECUTION/TECH_DEBT.md` immediately.

25.4. Phase completion triggers an update to `08_EXECUTION/MASTER_ROADMAP.md`.

---

## 26. Git Commit Rules

26.1. Commit messages follow Conventional Commits format:
```
{type}({scope}): {short description}

{optional body}
```

26.2. Types: `feat`, `fix`, `refactor`, `docs`, `style`, `test`, `chore`, `perf`.

26.3. Scope is the domain name: `feat(harvest): add yield bulk entry form`.

26.4. Every commit must represent a **single logical change**. No mixed commits.

26.5. No commit may break the build or fail existing tests.

26.6. Migration files must be committed in the same commit as the model change that triggered them.

26.7. Never force-push to `main` or `develop` branches.

---

## 27. Refactoring Rules

27.1. Refactoring requires explicit approval and a defined scope. Do not refactor while implementing a feature.

27.2. Every refactoring task must:
- Be documented in `08_EXECUTION/TECH_DEBT.md` before starting
- Have a defined before/after state
- Include test coverage before and after

27.3. Refactoring must not change external behavior. If behavior changes, it is a feature, not a refactor.

27.4. Incremental refactoring is preferred over big-bang rewrites.

27.5. When renaming a component or service, find ALL usages and update them in the same commit.

---

## 28. UI/UX Consistency Rules

28.1. All CRUD operations follow the same visual pattern:
- List → filterable, paginated table/card layout
- Detail → two-column layout (main content + metadata sidebar)
- Create/Edit → full-page form with sticky footer actions
- Delete → confirmation dialog, never an immediate action

28.2. All status badges follow the global color system:
- Active / Success: Green
- Warning / Pending: Amber
- Error / Inactive: Red
- Info / Draft: Blue
- Neutral / Archived: Slate

28.3. All icons come from a single icon library. No mixing libraries.

28.4. All page headers follow the same structure: breadcrumb → title → subtitle → action buttons.

28.5. All empty states must have: icon, descriptive message in Arabic, and a primary action button.

28.6. All loading states must use skeleton screens, not spinners, for content areas.

28.7. Destructive actions (delete, deactivate) must always be colored red and require confirmation.

28.8. All transitions must use consistent duration and easing from the Framer Motion config.

---

## 29. Domain Isolation Rules

29.1. Each domain owns its models, serializers, services, views, and URLs entirely.

29.2. Cross-domain data access goes through the service layer only — never by directly importing models from another domain's `models.py` into another domain's views or services.

29.3. Exception: Shared FK relationships to core models (`User`, `Farm`, `Season`) are permitted as they are infrastructure, not domain logic.

29.4. Each domain must have its own `permissions.py` defining domain-specific permission classes.

29.5. Each domain's API namespace is protected: `/api/v1/{domain}/`. No domain may respond on another's namespace.

29.6. When a domain is deactivated (white-label config), all its routes, components, and navigation entries must disappear without code changes.

---

## 30. AI Agent Final Checklist Before Writing Code

Before writing the first line of code for any task, the AI agent MUST answer YES to every question:

**Architecture:**
- [ ] Have I identified which domain this task belongs to?
- [ ] Does this task require changes to the architecture? If yes, have I documented the proposed change?
- [ ] Have I checked if similar logic already exists in the codebase?

**Implementation:**
- [ ] Is all business logic going into the service layer (not the view or component)?
- [ ] Is the API following REST conventions and the standard response envelope?
- [ ] Are all database writes wrapped in `transaction.atomic()`?
- [ ] Are all API calls going through the service layer (not directly from components)?

**Quality:**
- [ ] Are loading, error, and empty states handled?
- [ ] Is pagination implemented on all list views?
- [ ] Are all forms using `react-hook-form` + Zod?
- [ ] Is validation implemented on both frontend and backend?

**UI/UX:**
- [ ] Is the component designed mobile-first?
- [ ] Does the layout use logical CSS properties for RTL support?
- [ ] Are directional utilities (`start-`, `end-`, `ms-`, `me-`) used instead of `left`/`right`?
- [ ] Do all interactive elements have `id` and `aria-label` attributes?

**Standards:**
- [ ] Are file names following the naming conventions?
- [ ] Are files placed in the correct folder?
- [ ] Are all user-facing strings ready for i18n translation?
- [ ] Does the commit message follow Conventional Commits format?

**Documentation:**
- [ ] Will I update `CURRENT_PROGRESS.md` and `CHANGELOG.md` after this task?
- [ ] Is there any tech debt I discovered that needs logging in `TECH_DEBT.md`?

---

## 31. TypeScript Migration Strategy

> The project is currently JavaScript. Migration to TypeScript is **mandatory, gradual, and AI-controlled**.

31.1. **Migration Principle:** TypeScript adoption is incremental. No big-bang rewrites. Each task that touches a file should migrate that file if feasible.

31.2. **New files MUST be TypeScript.** Any new file created after 2026-05-12 must use `.ts` or `.tsx`. Creating `.js` or `.jsx` files is forbidden for new code.

31.3. **Migration Priority Order:**
```
1. types/          — type definitions first (no runtime impact)
2. constants/      — pure data, zero risk
3. utils/          — pure functions, easy to type
4. services/       — API layer, high value
5. hooks/          — custom hooks
6. components/     — UI layer last
7. pages/          — route-level components last
```

31.4. **JS Interoperability Rules:**
- TypeScript files may import from JavaScript files during migration.
- Add `// @ts-check` to JavaScript files being migrated incrementally.
- Use `declare module` stubs for JS modules lacking types.
- Never introduce `// @ts-ignore` without a comment explaining the exception and a linked TECH_DEBT entry.

31.5. **Typing Strategy:**
- All API response shapes must be typed in `src/types/api/{domain}.types.ts`.
- All component props must have explicit interfaces: `interface HarvestFormProps { ... }`.
- Use `unknown` instead of `any` for untyped third-party data, then narrow the type.
- Use `type` for unions/intersections, `interface` for object shapes.
- All event handlers must be typed: `React.ChangeEvent<HTMLInputElement>`, not `any`.

31.6. **Zod + TypeScript Integration:**
- All Zod schemas must export their inferred type:
```ts
export const HarvestSchema = z.object({ ... });
export type HarvestFormValues = z.infer<typeof HarvestSchema>;
```
- Never duplicate type definitions. If a Zod schema exists, infer the type from it.

31.7. **API Typing Rules:**
- All API response types must mirror the Django serializer output exactly.
- Shared response wrapper type:
```ts
interface ApiResponse<T> {
  success: boolean;
  data: T;
  message: string | null;
  errors: Record<string, string[]> | null;
}
```
- All service functions must be fully typed: input params and return type.

31.8. **Forbidden TypeScript Anti-Patterns:**
- ❌ `as unknown as TargetType` — double casting is a type system bypass.
- ❌ `any[]` on array parameters — always type the array element.
- ❌ Returning `void` from async functions that produce data — return the typed value.
- ❌ Non-null assertion `!` without a comment explaining why null is impossible.
- ❌ Type widening via `as` — narrow types, don't widen them.

---

## 32. AI Execution Protocol

> This section defines the exact procedure the AI agent follows for every task, in order.

**Phase 1 — Context Loading (before touching any file):**
- [ ] Read this document (`AI_DEVELOPMENT_RULES.md`) in full.
- [ ] Read `08_EXECUTION/CURRENT_PROGRESS.md` to understand current system state.
- [ ] Identify the domain. Read the domain's doc in `03_DOMAINS/`.
- [ ] Check if a relevant Dynamic Engine is involved. Read its doc in `04_DYNAMIC_ENGINES/`.

**Phase 2 — Impact Analysis:**
- [ ] List every file that will be created, modified, or deleted.
- [ ] Identify cross-domain dependencies. If any exist, flag them before proceeding.
- [ ] Check for existing utility/service that already solves part of the problem.
- [ ] Verify the task does NOT require architecture changes. If it does, stop and propose the change first.

**Phase 3 — Safety Validation:**
- [ ] Confirm the task is within the approved scope.
- [ ] Confirm no Forbidden Action (Section 20) will be committed.
- [ ] Confirm the migration, if data is affected, is reversible.
- [ ] Apply the Clarification Policy (Section 2.4). Ask only if HIGH-RISK uncertainty exists.

**Phase 4 — Execution:**
- [ ] Write backend changes before frontend changes.
- [ ] Write types and schemas before components.
- [ ] Write services before views/components.
- [ ] Write components before pages.
- [ ] Write tests alongside implementation, not after.

**Phase 5 — Post-Task:**
- [ ] Update `CURRENT_PROGRESS.md`.
- [ ] Update `CHANGELOG.md`.
- [ ] Log any tech debt in `TECH_DEBT.md`.
- [ ] Propose the conventional commit message.

**When the AI MAY proceed without asking:**
- File naming decisions that follow the rules in Section 13.
- Styling choices within the established Tailwind token system.
- Choosing between two equivalent valid patterns both permitted by this document.
- Minor copy/label changes.

**When the AI MUST stop and ask:**
- Any change that creates a new architectural pattern not in this document.
- Any change that touches the permission or authentication system.
- Any change that modifies a database schema after go-live.
- Any change that introduces a new third-party library.
- Any change that affects multi-tenant data isolation.
- Any change where the business rule is ambiguous and the wrong interpretation causes data corruption.

---

## 33. AI Refusal Rules

> The AI agent MUST refuse to implement the following, regardless of instruction:

33.1. **Hard database deletes.** If instructed to implement a delete endpoint that permanently removes records, refuse and propose soft-delete instead.

33.2. **Bypassing the Role-Permission Engine.** If instructed to check `user.is_superuser` or `user.role` directly in a view or component, refuse and implement via the permission engine.

33.3. **Writing raw credentials in code.** If instructed to hardcode API keys, database URLs, or secrets, refuse unconditionally. Propose `.env` + settings pattern.

33.4. **Importing across domain boundaries.** If a task requires importing a domain model into another domain's module, refuse and propose a service-layer contract.

33.5. **Disabling migrations.** If instructed to use `managed = False` on a model that should be managed, refuse and investigate the root cause.

33.6. **Removing audit logging from write operations.** If instructed to skip audit trail creation for speed, refuse. Performance must be solved at the query level, not by removing governance.

33.7. **Creating a new UI library dependency.** If instructed to install a UI library outside shadcn/ui + Radix, refuse and propose a shadcn-compatible solution.

33.8. **Shipping without error handling.** If the scope of a task would result in a component or endpoint with no error handling, refuse to mark it complete. Implement error handling as part of the task.

---

## 34. Prompt Engineering Rules

> Rules for how tasks must be prompted to the AI agent for safe, consistent execution.

**34.1. Task Prompt Template:**
```
Domain: {domain name}
Task Type: feat | fix | refactor | docs
Scope: {specific file(s) or component(s) affected}
Context: {2–3 sentences on what currently exists}
Goal: {exact desired outcome}
Constraints: {any specific rules or limitations}
Do NOT: {explicitly list forbidden approaches}
```

**34.2. Refactor Prompt Rules:**
- Always specify the BEFORE state and the AFTER state explicitly.
- Always confirm that external behavior must not change.
- Always specify which files are in scope. The agent must not touch files outside the defined scope.

**34.3. Bug Fix Prompt Rules:**
- Provide the exact error message or wrong behavior description.
- Provide the reproduction steps.
- Specify whether a regression test is required.
- Never prompt "just fix it" — always provide context.

**34.4. Architecture Prompt Rules:**
- Always reference this document and the relevant domain doc.
- Always specify the impact on other domains.
- Architecture tasks require a written proposal before implementation begins.

**34.5. Execution Prompt Rules:**
- Prompts must be self-contained. The agent must not need to search external sources to complete the task.
- All prompts for write operations must explicitly state: "Follow Section 12 (Service Layer Rules)."
- All prompts for UI work must explicitly state: "Follow Sections 7, 8, 9, 10 (Mobile, RTL, Tailwind, shadcn)."

---

## 35. White-Label Isolation Rules

35.1. **Branding Isolation.** All tenant-specific branding (logo, color palette, app name, favicon) must be stored in a `TenantConfiguration` database model. No branding value may appear in source code.

35.2. **CSS Custom Property Injection.** The Theme Engine injects tenant colors as CSS custom properties on `:root` at runtime after login. Components reference `var(--brand-primary)`, never a hardcoded hex value.

35.3. **Feature Toggles.** Every non-core module (Harvest, Equipment, HR, etc.) must be toggleable per tenant via the Configuration Engine. Disabled modules must:
- Remove their navigation entries.
- Return `403` on their API endpoints.
- Not render their components (lazy import never triggered).

35.4. **Configuration Isolation.** Tenant configuration records are partitioned by `tenant_id`. No API endpoint may return configuration data across tenant boundaries. Every configuration query must filter by the authenticated tenant.

35.5. **Deployment Separation.** White-label tenants share the codebase but have isolated:
- Database schemas (or row-level isolation with `tenant_id`).
- Media storage buckets.
- Configuration records.
- Domain/subdomain routing.

35.6. **No Tenant Bleed.** A request authenticated as Tenant A must never read, write, or infer data belonging to Tenant B. Every ORM query in a multi-tenant context must include a `tenant` filter. Missing tenant filter is a P0 security bug.

35.7. **Translation Isolation.** Each tenant may override translation strings. The i18n system must support a tenant-level override layer above the base translation files.

---

## 36. Legacy Migration Rules

> ATLS may contain legacy Material UI (MUI) components from earlier development phases. This section governs safe removal.

36.1. **No new MUI usage.** From this point forward, no MUI component may be introduced. Every new UI element uses shadcn/ui + Radix.

36.2. **Bridge Layer Strategy.** During migration, legacy MUI components are wrapped in a bridge component that presents a shadcn-compatible API surface:
```tsx
// components/bridge/LegacyTableBridge.tsx
// Wraps MUI DataGrid, exposes same props as shadcn DataTable
// TECH DEBT: Remove when shadcn DataTable migration is complete
```

36.3. **Migration Safety Rules:**
- Migrate one component at a time. Never migrate an entire page in a single commit.
- The bridge wrapper must be visually identical to the MUI original before switching.
- After each migration, delete the MUI import from the file. Never leave dead MUI imports.
- Log each migrated component in `08_EXECUTION/TECH_DEBT.md` under "MUI Migration Progress".

36.4. **MUI Dependency Removal Gate.** MUI may only be removed from `package.json` when zero MUI imports remain in the codebase. Run `grep -r "@mui"` before removing the dependency.

36.5. **Visual Regression Testing.** Before and after screenshots must be captured for every MUI → shadcn migration. The replacement must be pixel-comparable on both mobile and desktop.

---

## 37. Domain Event Rules

> Domain events enable decoupled cross-domain communication. This section governs their definition and usage.

37.1. **Event Naming Convention:**
```
{Domain}.{Entity}.{PastTenseVerb}

Examples:
  Harvest.Report.Submitted
  Inventory.Stock.Depleted
  HR.Worker.Deactivated
  Operations.Task.Approved
```

37.2. **Event Ownership.** Each event is owned by exactly one domain — the domain whose state change triggered the event. No other domain may publish an event on behalf of another domain's entity.

37.3. **Event Publishing Rules:**
- Events are published **after** the transaction that caused them commits. Never publish inside `transaction.atomic()` before commit.
- Use Django signals or a dedicated event bus (defined in `shared/events/`). Never publish via direct function calls into another domain's service.
- Events must be idempotent. Subscribers must handle duplicate delivery safely.

37.4. **Audit Integration.** Every domain event that represents a state change must trigger an audit log entry via the Audit domain. The Audit domain subscribes to all state-change events. Domain services must not duplicate audit logging — they publish the event; the Audit domain handles the record.

37.5. **Event Schema Versioning.** Event payloads must include a `version` field. When an event payload changes, increment the version and maintain backward-compatible handling for at least one previous version.

37.6. **Frontend Event Handling.** React Query cache invalidation triggered by real-time events (WebSocket, polling) must go through a centralized `EventBus` service in `src/lib/events/`. Components never subscribe to raw WebSocket messages directly.

---

## 38. API Typing & Contract Rules

38.1. Every Django serializer must have a corresponding TypeScript interface in `src/types/api/{domain}.types.ts`. The TS type and Django serializer must be kept in sync — they are a contract.

38.2. **Contract Drift is a Build Failure.** If the backend changes a serializer field (rename, type change, removal), the corresponding TS type must be updated in the same PR. Untypeed API surfaces that drift are a critical bug.

38.3. All TypeScript API types are generated from a **single source of truth** (either manually maintained or auto-generated from DRF schema). The decision must be documented in `01_ARCHITECTURE/API_ARCHITECTURE.md`.

38.4. API service functions on the frontend must return typed promises:
```ts
async function getHarvestReports(seasonId: string): Promise<ApiResponse<HarvestReport[]>> { ... }
```

38.5. Backend serializers must define `read_only_fields` and `write_only_fields` explicitly. No field may be both readable and writable without documented justification.

---

## 39. Security Rules

39.1. All endpoints must validate that the requesting user has ownership or access rights to the requested resource. `is_authenticated` alone is insufficient.

39.2. All user-uploaded files must be:
- Validated for file type (whitelist, not blacklist).
- Stored outside the web root.
- Served through a signed URL with expiry.
- Scanned for malware in production (integration documented in `06_BACKEND/FILE_STORAGE_SYSTEM.md`).

39.3. All API write endpoints must implement CSRF protection (Django's built-in) or explicit token validation for JWT-based APIs.

39.4. All sensitive fields (phone numbers, national IDs, financial data) must be encrypted at rest using Django's encrypted field utilities.

39.5. Rate limiting must be applied to: authentication endpoints, file upload endpoints, and any endpoint that sends external notifications (email, SMS).

39.6. SQL injection is prevented exclusively by the ORM. If raw SQL is ever used, it must use parameterized queries. String interpolation in SQL is a P0 security violation.

39.7. All authentication tokens expire. JWT access tokens: 15 minutes. Refresh tokens: 7 days. These values are configurable via environment variables, not hardcoded.

---

## 40. DDD Enforcement Rules

40.1. **Ubiquitous Language.** Every concept in the codebase must use the exact terminology defined in `09_REFERENCE/GLOSSARY.md`. When a new concept is introduced, add it to the glossary before writing code that uses it.

40.2. **Bounded Context Boundaries.** Each Django app represents one Bounded Context. The app's `models.py` defines its Aggregate Roots. No Aggregate Root from one context may be modified by another context's service.

40.3. **Aggregate Integrity.** All mutations to an Aggregate must go through the Aggregate Root. Never directly update a child entity without going through the root. Example: To update a `HarvestRow`, you must go through `HarvestReport` service, not a `HarvestRow` service.

40.4. **Value Objects.** Concepts with no identity (GPS coordinates, date ranges, measurement units) must be implemented as Value Objects (immutable Python dataclasses or TS readonly types), not as models with PKs.

40.5. **Repository Pattern.** The service layer functions as the Repository. ViewSets never query the ORM directly. All data access is mediated by `{domain}_services.py`.

40.6. **Anti-Corruption Layer.** When integrating with external APIs (weather, satellite, ERP connectors), an Anti-Corruption Layer (ACL) service in `shared/integrations/` translates external data models into ATLS domain models. External data shapes never leak into domain code.

40.7. **Domain Events over Direct Calls.** When Domain A needs to react to Domain B's state change, it subscribes to a Domain Event (Section 37). It never imports Domain B's service. This is the DDD enforcement mechanism for decoupling.

---

## 30. AI Agent Final Checklist Before Writing Code

Before writing the first line of code for any task, the AI agent MUST answer YES to every question:

**Context Loading:**
- [ ] Have I read `AI_DEVELOPMENT_RULES.md` for this session?
- [ ] Have I read `CURRENT_PROGRESS.md` to understand the current state?
- [ ] Have I identified the domain and read its domain doc?

**Architecture:**
- [ ] Have I identified which domain this task belongs to?
- [ ] Does this task require changes to the architecture? If yes, have I documented the proposed change?
- [ ] Have I checked if similar logic already exists in the codebase?
- [ ] Have I verified no Forbidden Action (Section 20) is required?

**Implementation:**
- [ ] Is all business logic going into the service layer (not the view or component)?
- [ ] Is the API following REST conventions and the standard response envelope?
- [ ] Are all database writes wrapped in `transaction.atomic()`?
- [ ] Are all API calls going through the service layer (not directly from components)?
- [ ] Is the new file `.ts` / `.tsx` (TypeScript)?

**Quality:**
- [ ] Are loading, error, and empty states handled?
- [ ] Is pagination implemented on all list views?
- [ ] Are all forms using `react-hook-form` + Zod?
- [ ] Is validation implemented on both frontend and backend?
- [ ] Is the Zod schema exported with an inferred TypeScript type?

**UI/UX:**
- [ ] Is the component designed mobile-first?
- [ ] Does the layout use logical CSS properties for RTL support?
- [ ] Are directional utilities (`start-`, `end-`, `ms-`, `me-`) used instead of `left`/`right`?
- [ ] Do all interactive elements have `id` and `aria-label` attributes?
- [ ] Are Framer Motion animations RTL-aware (Section 8.9)?
- [ ] Are Radix components using explicit `dir` prop (Section 8.10)?

**White-Label / Multi-Tenant:**
- [ ] Does this change include any hardcoded branding value? (Must be NO.)
- [ ] Does every ORM query in a multi-tenant context include a `tenant` filter?
- [ ] Is the feature toggleable via the Configuration Engine?

**Standards:**
- [ ] Are file names following the naming conventions?
- [ ] Are files placed in the correct folder?
- [ ] Are all user-facing strings ready for i18n translation?
- [ ] Does the commit message follow Conventional Commits format?

**Documentation:**
- [ ] Will I update `CURRENT_PROGRESS.md` and `CHANGELOG.md` after this task?
- [ ] Is there any tech debt I discovered that needs logging in `TECH_DEBT.md`?
- [ ] Is there a new concept that needs to be added to `GLOSSARY.md`?

---

> **This document is the law. When in doubt, do not proceed. Ask.**

---

## Last Updated
2026-05-12

## Version
v2.0 — Added: TypeScript strategy, AI execution protocol, refusal rules, prompt engineering rules, white-label isolation, legacy migration, domain events, API typing contracts, security rules, DDD enforcement. Strengthened: RTL (Framer Motion, Radix), Dynamic Engine hierarchy, clarification policy.
