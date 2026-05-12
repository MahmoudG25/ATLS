# AI Code Style & Governance

| Metadata | Details |
| :--- | :--- |
| **Document ID** | ATLS-AI-01 |
| **Status** | AUTHORITATIVE |
| **Version** | 2.0.0 |
| **Owner** | AI Agent & Engineering Team |
| **Applicability** | All AI-Generated & Human-Authored Code |

## 1. Code Style Philosophy
Code in ATLS must be **Self-Documenting, Modular, and Predictable**. Our style is designed to be easily parsed by both humans and AI agents, minimizing ambiguity and maximizing maintainability.
- **Explicit > Implicit**: Avoid "magic" and hidden logic.
- **Readability > Conciseness**: Choose clear names over short ones.
- **Consistency**: One way to do things across the entire platform.

## 2. Naming Conventions
| Context | Convention | Example |
| :--- | :--- | :--- |
| **React Components** | PascalCase | `HarvestReportTable` |
| **Functions/Variables** | camelCase | `calculateYieldWeight` |
| **Django Models/Classes** | PascalCase | `OperationalJournal` |
| **Database Fields/Python** | snake_case | `tenant_id`, `created_at` |
| **Constants/Enums** | SCREAMING_SNAKE_CASE | `MAX_UPLOAD_SIZE`, `ACTIVE` |
| **CSS Classes** | kebab-case | `btn-primary`, `nav-item` |

## 3. TypeScript Style Rules
- **Strict Mode**: Mandatory. No `any` types.
- **Interfaces**: Use `interface` for public APIs/Props, `type` for unions/aliases.
- **Explicit Returns**: Always define function return types.
- **Enums**: Use `as const` objects or standard `enum` for type safety.

## 4. React Component Style
- **Functional Components**: Use arrow functions.
- **Props**: Destructure props in the function signature.
- **Logic Placement**: Keep logic inside the component minimal; move complex logic to custom hooks.
- **Fragments**: Use `<> ... </>` instead of `<div>` where possible.

## 5. Hook Naming Rules
- **Standard**: Start with `use` (e.g., `useActiveSeason`).
- **Domain-Specific**: Prefix with domain name (e.g., `useHarvestData`, `usePersonnelList`).
- **Stateful**: Use `useStore[Entity]` for Zustand-connected hooks.

## 6. Zustand Store Rules
- **Naming**: `use[Domain]Store` (e.g., `useAuthStore`).
- **Atomic Actions**: Keep actions focused (e.g., `setLoading`, `addReport`).
- **Selectors**: Always use selectors to prevent unnecessary re-renders.

## 7. Tailwind Usage Rules
- **Utility First**: Use standard Tailwind classes.
- **Complexity**: If classes exceed 5+, use `cn()` utility or break into sub-components.
- **Arbitrary Values**: Avoid `top-[13px]`; use standard scale or design tokens.

## 8. Django Style Rules
- **PEP 8**: Mandatory. Use `black` and `isort` for formatting.
- **Docstrings**: Google Style docstrings for all classes and methods.
- **Type Hinting**: Mandatory for all service and repository methods.

## 9. Service Layer Naming
- **Suffix**: Always end with `Service` (e.g., `HarvestReportingService`).
- **Methods**: Verb-first (e.g., `execute_close_season`).

## 10. Repository Naming
- **Suffix**: Always end with `Repository` (e.g., `PersonnelRepository`).
- **Methods**: CRUD-focused (e.g., `get_by_id`, `create_record`).

## 11. DTO Naming
- **Input**: `[Action]Request` (e.g., `CreateHarvestRequest`).
- **Output**: `[Action]Response` or `[Entity]DTO`.

## 12. Event Naming
- **Format**: `domain.entity.action` (e.g., `harvest.load.completed`).
- **Past Tense**: Use past tense for events that have already occurred.

## 13. Enum Naming
- **Class**: PascalCase (e.g., `HarvestStatus`).
- **Members**: SCREAMING_SNAKE_CASE (e.g., `PENDING`, `APPROVED`).

## 14. File Naming Rules
- **Frontend**: `PascalCase.tsx` for components, `camelCase.ts` for logic.
- **Backend**: `snake_case.py`.
- **Assets**: `kebab-case.svg`.

## 15. Folder Naming Rules
- **Domain-based**: Group by bounded context (e.g., `features/harvesting/`).
- **Technical**: Group by layer (e.g., `services/`, `components/`).

## 16. Import Ordering
1. React/Framework imports.
2. Third-party library imports.
3. ATLS Core/Shared imports.
4. Relative domain imports (`../`).
5. Styles/Assets.

## 17. Function Design Rules
- **Single Responsibility**: One function = one job.
- **Max Lines**: Functions should not exceed 50 lines.
- **Arguments**: Prefer object destructuring for > 3 arguments.

## 18. Error Handling Style
- **Frontend**: Use `ErrorBoundary` for UI, `try/catch` with `toast.error()` for API calls.
- **Backend**: Use custom `DomainException` classes. Never return generic `500` for business logic errors.

## 19. Logging Style
- **Structured**: Log objects, not strings.
- **Context**: Always include `correlation_id` and `tenant_id`.

## 20. Commenting Standards
- **Why, not What**: Comments should explain the rationale for complex logic, not restate the code.
- **FORBIDDEN**: Commented-out code. Use Git history instead.

## 21. Documentation Standards
- **README**: Every major folder/app must have a `README.md`.
- **API**: Every endpoint must have OpenAPI (Swagger) annotations.

## 22. Testing Naming
- **Files**: `[filename].test.ts` or `test_[filename].py`.
- **Methods**: `test_should_[expected_behavior]_when_[context]`.

## 23. Async Code Style
- **Async/Await**: Preferred over Promises/Callbacks.
- **Parallel**: Use `Promise.all()` for independent async calls.
- **Loading**: Always handle loading and error states explicitly.

## 24. AI Safety Rules
- **Unclear Naming**: AI agents MUST NOT use single-letter variables (`x`, `y`) or vague names (`data`, `info`).
- **Giant Functions**: FORBID functions > 50 lines; break into sub-functions.
- **Nesting**: FORBID nesting logic > 3 levels deep (e.g., `if` inside `loop` inside `if`).
- **Abbreviations**: FORBID random abbreviations (e.g., `hrv_rpt`); use full names (`harvest_report`).
- **Magic Values**: FORBID hardcoded numbers or strings; use constants or enums.
- **Dead Code**: FORBID generating unreachable code or unused variables.
- **Comments**: FORBID leaving "TODO" comments or commented-out code in final output.
- **Inline Chaos**: FORBID mixing business logic, UI styles, and data fetching in a single component.

## 25. Forbidden Code Anti-Patterns
- **The God File**: Files exceeding 500 lines.
- **Deep Inheritance**: Class hierarchies > 2 levels.
- **Hidden Dependencies**: Using global variables or un-injected services.

## 26. Agricultural ERP Examples
- **Good**: `calculate_hectare_yield(area: Hectares, weight: Kilograms) -> Decimal`
- **Bad**: `calc(a, w)`

## 27. Final Enforcement Checklist
- [ ] Naming conventions followed (Pascal/camel/snake).
- [ ] No `any` types in TypeScript.
- [ ] Functions are < 50 lines.
- [ ] No magic values (Enums/Constants used).
- [ ] Error handling is explicit.
- [ ] Imports are sorted.
- [ ] No commented-out code.
- [ ] Documentation strings are present for core logic.
