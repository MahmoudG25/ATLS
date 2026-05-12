# STATE MANAGEMENT

## Purpose
Define ATLS client and server state governance for a distributed agricultural ERP frontend. This document establishes the execution rules for React Query, Zustand, query keys, offline persistence, optimistic updates, and tenant-safe state management.

## Scope
Covers server state ownership, client state boundaries, React Query integration, Zustand governance, synchronization rules, cache hydration, offline recovery, form draft persistence, white-label isolation, and AI-safe state constraints.

## Current Status
- [x] Not Started
- [ ] In Progress
- [ ] Completed

## Dependencies
- `docs_v2/01_ARCHITECTURE/FRONTEND_ARCHITECTURE.md`
- `docs_v2/01_ARCHITECTURE/OFFLINE_STRATEGY.md`
- `docs_v2/01_ARCHITECTURE/API_ARCHITECTURE.md`
- `docs_v2/01_ARCHITECTURE/BACKEND_ARCHITECTURE.md`
- `docs_v2/01_ARCHITECTURE/EVENT_SYSTEM.md`
- `docs_v2/01_ARCHITECTURE/DOMAIN_DRIVEN_ARCHITECTURE.md`
- `docs_v2/07_AI_AGENT/AI_DEVELOPMENT_RULES.md`

## Notes
This is the master client/server state governance document for ATLS. It is the authoritative reference for state ownership, tenant-safe caches, offline replay, and UI resilience.

## Last Updated
2026-05-12

---

## 1. State Management Philosophy
ATLS treats state as either server-owned or client-scoped. Server state is authoritative, synchronized through React Query. Client state is intentionally minimal and limited to UI concerns, session metadata, theme, and navigation.

This approach preserves offline-first execution while avoiding duplicate caches, giant global stores, and tangled state dependencies.

## 2. Server State vs Client State
- **Server state:** owned exclusively by React Query, including lists, details, read models, filters, and server-derived results.
- **Client state:** auth/session metadata, theme branding, navigation preferences, lightweight UI toggles, and local draft placeholders.

Server state MUST not be duplicated in Zustand or other global stores. Client state MUST remain lightweight and isolated.

## 3. React Query Ownership Rules
- React Query owns all server-state fetching, caching, invalidation, background refresh, optimistic updates, and offline recovery integration.
- Use reusable query/mutation hooks and service wrappers.
- Direct fetch or axios calls inside components are forbidden.
- Keep React Query configuration centralized and domain-scoped.

## 4. Zustand Ownership Rules
- Zustand is confined to auth/session data, theme state, navigation preferences, and lightweight UI flags.
- Zustand MUST NOT store API response payloads, read models, or query data.
- Zustand is not a substitute for server-state caching.
- Use Zustand for state that is not part of server synchronization.
- Guard against state explosion by keeping slices specific and shallow.

## 5. Query Key Architecture
- Query keys must be array-based and deterministic.
- They must include domain, resource, tenant, and contextual qualifiers.
- Query keys are the primary contract for cache identity and invalidation.
- Tenant information must appear explicitly in every key where data is tenant-scoped.

## 6. Query Key Naming Convention
Use structured keys:
- ['farm', 'crop', cropId, 'details']
- ['inventory', 'stock', { tenantId, warehouseId, status }]
- ['reports', 'summary', { tenantId, range, type }]

Rules:
- Start with domain or bounded context.
- Follow with resource and scope.
- Append tenant-aware filters and settings.
- Avoid generic keys like ['data'], ['list'], or ['resource'].

## 7. Query Invalidation Rules
- Invalidate only the affected query keys.
- Prefer precise invalidation over broad cache resets.
- Invalidate related list queries after item mutations.
- Invalidate read models after write operations that affect their underlying data.
- Never assume staleTime alone will keep data consistent.

## 8. Query Cache Lifecycle
- Query lifecycle: fetch → cache → render → background refresh → invalidate.
- Use cache hydration for offline-aware startup and tenant-scoped recovery.
- Set staleTime and cacheTime according to volatility and mobile constraints.
- Remove unused keys proactively.
- Do not retain full payloads longer than necessary.

## 9. Optimistic Update Strategy
- Apply optimistic updates only when the user experience benefits and rollback is feasible.
- Patch the smallest affected query keys.
- Save pre-mutation snapshots in onMutate.
- Keep optimistic updates local to React Query cache, not global state.
- Rollback must be part of every optimistic mutation path.

## 10. Rollback Strategy
- Store the previous state before optimistic updates.
- Restore state in onError if the mutation fails.
- If rollback is incomplete, invalidate dependent queries in onSettled.
- Provide clear user feedback when optimistic state is rolled back.
- Avoid partial state retention after failed mutations.

## 11. Offline Mutation Queue Integration
- Offline mutation queues must persist locally and integrate with React Query on replay.
- Queue items should include tenant id, request id, payload, retry count, and dependencies.
- Replay queue items in order and update or invalidate affected queries afterward.
- Do not keep queue state exclusively in memory.
- Queue persistence must survive app restarts.

## 12. Sync-Aware State Behavior
- Components must reflect offline, syncing, and stale conditions.
- Use React Query statuses plus queue metadata for sync-aware UI.
- On reconnect, refresh affected server queries and replay pending mutations.
- Avoid showing stale or inconsistent data without clear indicators.

## 13. Draft Persistence Strategy
- Persist drafts locally for offline recovery and restart resilience.
- Draft records must contain tenant keys, form metadata, and timestamps.
- Rehydrate and merge drafts safely with server-loaded defaults.
- Expire or prune stale drafts to prevent cache bloat.
- Do not persist full server caches in draft storage.

## 14. Form State Rules
- Form input state is local to the form component or form engine instance.
- Load initial values from React Query and submit through mutation hooks.
- Keep form state isolated per instance, not in global stores.
- Use autosave for drafts, not for server-side state mutation.
- Keep validation logic in form libraries or domain hooks, not in plain UI markup.

## 15. Auth State Management
- Auth state is handled in Zustand and includes identity, token claims, tenant scope, and session validity.
- Auth state is separate from React Query caches and query data.
- Sign-in, sign-out, and refresh workflows must reset or invalidate auth-scoped queries.
- Persist auth credentials securely and tenant-isolated.

## 16. Session Rehydration
- Rehydrate session and tenant context at app startup.
- Validate rehydrated auth state before enabling protected features.
- Restore white-label and theme metadata alongside session state.
- Keep rehydration logic in the shell provider layer.

## 17. Theme State Management
- Theme and branding metadata are managed in Zustand.
- Theme state includes mode, palette keys, and white-label variant information.
- Persist theme preferences per tenant and brand.
- Theme state must not contain server entity data.

## 18. Navigation State Boundaries
- Navigation preferences and last-visited routes are client-only state.
- Store navigation metadata in route state, local storage, or Zustand if shared.
- Avoid placing domain navigation details in global stores.
- Keep navigation state lightweight and recoverable.

## 19. Table State Strategy
- Table state such as sorting, column visibility, selection, and page size can be stored locally or in route query params.
- Keep row and payload data in React Query caches only.
- Do not persist full table payloads in global client state.
- Use normalized query keys to reflect current table filters and pagination.

## 20. Filter State Strategy
- Filter definitions and active values belong to component or route state.
- Reflect filters explicitly in query keys when fetching server data.
- Do not store filter payloads as server data in Zustand.
- Use filter state for UI preferences and query parameter synchronization only.

## 21. URL State Synchronization
- Use URL parameters as the canonical representation of view state when appropriate.
- Keep URL synchronization separate from cache storage.
- Restore view state from the URL on page reload.
- Do not use the URL to store large datasets or server payloads.

## 22. Pagination State Rules
- Pagination parameters belong to query keys or route state.
- Prefer cursor or incremental pagination for large data sets.
- Keep page state local to paginated components or routes.
- Persist only the cursor or range metadata needed for recovery.

## 23. Cache Hydration Rules
- Hydrate cache metadata at startup for offline-aware views and tenant recovery.
- Use persisted keys, timestamps, and stale flags, not duplicate server payloads.
- Ensure cache hydration is tenant and white-label isolated.
- Rehydrate only what is necessary to resume offline workflows.

## 24. Prefetching Strategy
- Prefetch only when it improves UX and respects mobile constraints.
- Use prefetch for adjacent pages, likely next actions, or when the network is stable.
- Avoid aggressive prefetching on weak connections or low battery.
- Keep prefetch logic domain-scoped and conditional.

## 25. Background Refresh Rules
- Refresh queries in the background when connectivity returns.
- Target only the queries affected by writes or stale read models.
- Avoid global query refresh unless a full resync is explicitly required.
- Combine background refresh with event-driven invalidation.

## 26. Event-Driven Cache Updates
- React Query caches may be patched from backend events or websocket messages.
- Apply updates to the smallest affected keys.
- When event payloads are uncertain, invalidate rather than overwrite.
- Do not bypass React Query with manual caches or global stores.

## 27. Real-Time Readiness Strategy
- Design state to accept real-time patches through query patching, websocket listeners, and event subscriptions.
- Use query invalidation and patching for websocket-driven updates.
- Keep real-time state isolated from client-only stores.
- Ensure real-time updates remain tenant-aware.

## 28. Tenant Isolation Rules
- Tenant context must be explicit in query keys, persisted keys, and offline storage.
- Never mix tenant data in the same cache or store.
- Partition offline queues, drafts, theme preferences, and session state by tenant.
- Validate tenant identity on every persisted state load.

## 29. White-Label State Isolation
- White-label settings are runtime-configurable and isolated per brand.
- Store white-label metadata in tenant-aware client state.
- Avoid shared stores that mix brand variants.
- Keep persistence isolation for white-label and tenant metadata.

## 30. Offline State Recovery
- Recover offline state from persisted drafts, offline queue metadata, and cache hydration.
- Resume queued mutations and refresh affected queries after reconnect.
- Preserve local user intent through replay and rollback flows.
- Ensure recovery handles partial success and conflict outcomes gracefully.

## 31. State Persistence Rules
- Persist only the minimal state needed for restart recovery and offline continuation.
- Persist drafts, offline queue items, auth/session metadata, and theme preferences.
- Encrypt sensitive persisted state.
- Version persisted schemas and handle migrations safely.
- Do not persist raw API payloads unless required for offline view fallback.

## 32. Performance Constraints
- Avoid giant in-memory caches and duplicate data structures.
- Keep query retention modest on mobile.
- Use shallow state in Zustand and local component state for UI concerns.
- Profile query cache usage and prune stale entries.

## 33. Mobile Memory Constraints
- Limit in-memory cache size on mobile.
- Use shorter cache lifetimes for mobile-heavy features.
- Persist large state to disk rather than RAM when possible.
- Avoid storing media blobs in memory or Zustand.

## 34. Error State Management
- Keep error state in React Query and local form state.
- Expose errors contextually within the affected component.
- Do not persist raw server errors in long-lived state.
- Provide retry controls and clear failure messaging.

## 35. Loading State Management
- Loading indicators are component- or query-local.
- Use React Query status flags for server loading feedback.
- Reserve global loading overlays for app-wide transitions.
- Keep loading semantics predictable and consistent.

## 36. AI Safety Rules
AI must not:
- store API response data in Zustand or other global stores
- create giant global caches of server state
- execute fetch logic directly inside components
- invalidate all queries globally as a shortcut
- store media blobs in memory stores
- mix tenant data across cache boundaries
- allow uncontrolled optimistic mutations without rollback
- put mutation side effects inside render logic

## 37. Forbidden State Anti-Patterns
- using Zustand or Context as a server cache
- storing domain data in global client stores
- direct component fetch logic or useEffect fetch loops
- cross-domain entity imports to share state
- hardcoding tenant or white-label identifiers in state keys
- global query invalidation for every mutation

## 38. Real-World Agricultural State Scenarios
- **Offline harvest logging:** a worker records yield data offline, persists draft state, and replays the mutation queue in order once connectivity returns.
- **Mobile inventory adjustment:** a warehouse operator updates stock counts with optimistic feedback, then resolves conflicts if server counts changed.
- **White-label farm dashboard:** tenants see runtime branding with tenant-scoped theme state and isolated persisted preferences.
- **Field inspection form:** dynamic form draft state survives restarts and merges safely with server values after reconnect.
- **Remote maintenance task:** technicians continue task workflows offline while queue metadata and sync state preserve their progress.

## 39. State Observability
- Observe query lifecycle, mutation replay, offline queue state, and sync outcomes.
- Track invalidation events and tenant-scoped cache activity.
- Surface state health without exposing sensitive data.
- Use observability to identify stale caches and sync recovery issues.

## 40. Future State Evolution Strategy
- Strengthen offline-first persistence and tenant-aware recovery.
- Advance event-driven cache updates and real-time readiness.
- Improve mobile memory management and query pruning.
- Keep state governance minimal while expanding safe client-side resilience.
