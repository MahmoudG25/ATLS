# DYNAMIC FORM ENGINE

## Purpose
Define the dynamic form engine architecture for ATLS, enabling runtime-configurable, schema-driven forms for agricultural operations, harvest workflows, inspection reports, and tenant-specific workflows. This document establishes the rules for schema architecture, renderer pipeline, validation, offline behavior, and AI-safe constraints.

## Scope
Covers form engine philosophy, schema structure, field registry, renderer architecture, conditional logic, validation, offline persistence, tenant customization, versioning, permissions, analytics, and mobile-first UX.

## Current Status
- [x] Not Started
- [ ] In Progress
- [ ] Completed

## Dependencies
- `docs_v2/01_ARCHITECTURE/FRONTEND_ARCHITECTURE.md`
- `docs_v2/01_ARCHITECTURE/STATE_MANAGEMENT.md`
- `docs_v2/01_ARCHITECTURE/OFFLINE_STRATEGY.md`
- `docs_v2/01_ARCHITECTURE/API_ARCHITECTURE.md`
- `docs_v2/01_ARCHITECTURE/MEDIA_ARCHITECTURE.md`
- `docs_v2/01_ARCHITECTURE/EVENT_SYSTEM.md`
- `docs_v2/07_AI_AGENT/AI_DEVELOPMENT_RULES.md`

## Notes
This is the master dynamic form engine document for ATLS. Forms are runtime-generated from schemas, supporting offline-first workflows, tenant customization, and role-aware behavior. No hardcoded forms allowed.

## Last Updated
2026-05-12

---

## 1. Dynamic Form Philosophy
ATLS forms are runtime-configurable and schema-driven, eliminating hardcoded UI components. Forms adapt to agricultural workflows, tenant requirements, and user roles dynamically, ensuring flexibility for harvest logging, inspections, and maintenance tasks.

## 2. Why Schema-Driven Forms
Schema-driven forms enable runtime generation, reducing code duplication and supporting tenant-specific customizations. Schemas define fields, validation, and behavior declaratively, allowing forms to evolve without frontend redeployment.

## 3. Runtime Form Architecture
Forms are generated at runtime from JSON schemas fetched via API. The engine includes a field registry, renderer pipeline, validation engine, and persistence layer. Forms integrate with React Query for data loading and Zustand for lightweight state.

## 4. Form Schema Structure
Schemas are JSON objects with: fields array, layout rules, validation rules, conditional logic, and metadata. Schemas include version numbers and tenant identifiers for customization.

## 5. Field Definition Standards
Fields have type (text, select, media), label, validation rules, visibility conditions, and default values. Fields support nested structures and repeatable sections.

## 6. Field Registry Architecture
A centralized registry maps field types to renderers and validators. Registry entries include component factories, validation functions, and metadata. Registry is extensible for custom field types.

## 7. Dynamic Renderer Pipeline
Renderer pipeline processes schemas into React components: parse schema → resolve conditions → render fields → apply layout. Pipeline supports lazy rendering and performance optimizations.

## 8. Layout Schema Rules
Layout schemas define grid structures, tabs, and sections. Rules support responsive design, RTL layouts, and mobile-first rendering. Layouts are declarative and theme-aware.

## 9. Conditional Field Logic
Conditional logic uses expressions to show/hide fields based on form state. Logic is evaluated at runtime, supporting dependencies on other fields or external data.

## 10. Dynamic Visibility Rules
Visibility rules control field access based on user roles, tenant settings, and form context. Rules are enforced in the renderer and validated on submission.

## 11. Validation Architecture
Validation is schema-driven with runtime execution. Validators include built-in rules (required, format) and custom functions. Validation integrates with Zod for type safety.

## 12. Runtime Validation Pipeline
Validation pipeline runs on field changes and submission: parse rules → execute validators → aggregate errors → update UI. Pipeline supports async validation for lookups.

## 13. Zod Integration Strategy
Zod schemas are generated from form schemas for runtime validation. Integration ensures type safety and consistent error messages across client and server.

## 14. Nested Field Structures
Nested fields support object hierarchies and arrays. Renderer handles nesting with recursive components, maintaining form state integrity.

## 15. Repeatable Section Architecture
Repeatable sections allow dynamic addition/removal of field groups. Sections maintain state in arrays, with validation applied per instance.

## 16. Media Field Support
Media fields integrate with MEDIA_ARCHITECTURE.md, supporting uploads, previews, and offline queuing. Media fields link to domain entities and persist metadata.

## 17. Offline Form Behavior
Forms work offline with local persistence. Drafts survive restarts, and submissions queue for sync. Offline forms validate locally and merge on reconnect.

## 18. Draft Persistence Strategy
Drafts persist in local storage with tenant isolation. Persistence includes form state, schema version, and timestamps. Drafts auto-save on changes.

## 19. Form Versioning Rules
Schemas are versioned; forms check compatibility on load. Version mismatches trigger migrations or user notifications. Versions prevent stale form execution.

## 20. Schema Migration Strategy
Migrations update form data for schema changes. Migrations are automated where possible, with fallbacks for manual resolution.

## 21. Tenant-Specific Form Overrides
Tenants can override schemas via configuration. Overrides are merged at runtime, preserving base functionality while allowing customization.

## 22. White-Label Form Customization
White-label variants customize themes, labels, and layouts. Customizations are isolated and do not affect core logic.

## 23. Role-Aware Field Permissions
Fields have permission rules based on user roles. Renderer hides or disables fields accordingly. Permissions integrate with auth state.

## 24. Dynamic Workflow Integration
Forms integrate with workflows, showing/hiding fields based on process state. Integration uses event-driven updates.

## 25. Event-Driven Form Behavior
Forms respond to events (e.g., data changes) by re-evaluating conditions. Events trigger re-rendering and validation.

## 26. Form Analytics Integration
Forms track usage, completion rates, and errors. Analytics are tenant-scoped and privacy-compliant.

## 27. Mobile-First Form UX Rules
Forms prioritize mobile UX: touch-friendly inputs, progressive disclosure, and offline resilience. Layouts adapt to screen sizes.

## 28. RTL Form Rendering Rules
RTL layouts reverse field order and alignments. Rules apply automatically based on locale.

## 29. Performance Constraints
Forms limit rendered fields, use lazy loading, and optimize re-renders. Performance profiling ensures smooth mobile experience.

## 30. Lazy Field Rendering
Fields render on demand, reducing initial load. Lazy rendering uses intersection observers and virtual scrolling for large forms.

## 31. Dynamic Searchable Selects
Selects support async search and filtering. Options load dynamically from APIs, with caching via React Query.

## 32. Async Lookup Fields
Lookup fields fetch data asynchronously, integrating with server state. Lookups support debouncing and error handling.

## 33. Form Observability
Forms log rendering times, validation errors, and submission success. Observability aids debugging and optimization.

## 34. Form Error Recovery
Errors provide clear messages and recovery paths. Forms recover from validation failures and network issues.

## 35. Form Submission Lifecycle
Submission: validate → optimistic update → queue mutation → sync. Lifecycle handles offline and conflict resolution.

## 36. AI Safety Rules
AI must not:
- hardcode form logic in components
- create giant static forms
- inline validation rules
- mutate DOM directly
- branch on tenant in UI code
- duplicate field renderers
- store form blobs in Zustand

## 37. Forbidden Dynamic Form Anti-Patterns
- hardcoded field components
- static form definitions
- direct state mutations
- tenant-specific code paths
- unbounded nested structures
- synchronous validation blocks

## 38. Real-World Agricultural Form Scenarios
- **Harvest logging:** dynamic fields for crop types, yields, and media evidence, with conditional sections for different harvest methods.
- **Equipment inspection:** role-aware fields for technicians, with repeatable sections for multiple issues and media uploads.
- **Inventory adjustment:** tenant-customized fields for warehouse layouts, with offline persistence and sync.

## 39. Future Form Engine Evolution
- Advance AI-driven form generation from natural language.
- Implement advanced conditional logic with expressions.
- Expand media integration with real-time previews.
- Enhance offline collaboration for shared forms.
- Integrate with voice input for mobile workflows.

## 40. Example Runtime Form Flow
1. Fetch schema from API.
2. Initialize form state in Zustand.
3. Render fields based on conditions.
4. Validate on change.
5. Persist draft locally.
6. Submit with optimistic update.
7. Queue for offline sync if needed.
