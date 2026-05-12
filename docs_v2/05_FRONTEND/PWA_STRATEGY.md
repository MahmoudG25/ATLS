# PWA STRATEGY

## Purpose
Define the ATLS master Progressive Web App architecture and offline mobile execution strategy for remote farm operations, weak network zones, intermittent connectivity, low-end Android devices, and field-ready installable experiences.

## Scope
Covers PWA shell architecture, installability, service worker design, cache strategies, offline workflows, sync orchestration, media upload recovery, persistent queueing, IndexedDB architecture, mobile performance constraints, and AI-safe PWA execution rules.

## Current Status
- [x] Not Started
- [ ] In Progress
- [ ] Completed

## Dependencies
- `docs_v2/02_UI_UX/MOBILE_FIRST_STRATEGY.md`
- `docs_v2/02_UI_UX/THEME_ENGINE.md`
- `docs_v2/01_ARCHITECTURE/STATE_MANAGEMENT.md`
- `docs_v2/05_FRONTEND/COMPONENT_ARCHITECTURE.md`
- `docs_v2/05_FRONTEND/ROUTING_SYSTEM.md`
- `docs_v2/04_DYNAMIC_ENGINES/CONFIGURATION_ENGINE.md`

## Notes
This is the master ATLS PWA strategy document. It must be consistent with offline-first, mobile-first, tenant-aware, and app-like execution patterns without duplicating existing architecture logic.

## Last Updated
2026-05-12

---

## 1. PWA Philosophy
ATLS PWA philosophy is to provide a resilient, installable app experience for field operations that gracefully tolerates connectivity loss while preserving data integrity and performance. The PWA must behave like a mobile app on low-end Android devices and remote farm environments, with offline-first workflows and strong recovery guarantees.

## 2. Mobile-First Execution Strategy
The PWA prioritizes mobile execution through responsive shell rendering, touch-optimized navigation, minimal initial payloads, and adaptive resources. The strategy avoids desktop-first assumptions, relying instead on app-like routing and fast page start times under constrained CPU, memory, and connectivity.

## 3. Installable App Strategy
Installability is achieved through a well-defined manifest, scoped service worker, HTTPS delivery, and prompt-friendly install UX. The PWA should support a homescreen launch, full-screen or standalone display modes, proper icons, and theme colors that match tenant branding without compromising shell stability.

## 4. App Shell Architecture
The app shell is the minimal runtime UI that loads immediately and contains navigation, offline indicators, tenant header, and primary route container. Shell assets are cached aggressively while application data loads asynchronously, ensuring the PWA remains interactive with minimal network dependence.

## 5. Service Worker Architecture
The service worker is a thin, purpose-driven worker scoped to the application root. It orchestrates caching, request routing, background sync, and update delivery. The worker should avoid giant monoliths, keep logic modular, and delegate complex state persistence to IndexedDB and the app runtime.

## 6. Cache Layer Strategy
Cache layer strategy separates static shell assets, runtime data, API responses, and media payloads. Each cache tier has explicit versioning and lifespan rules. Cache corruption is prevented through atomic writes, cache namespace isolation, and validation checks.

## 7. Static Asset Caching
Static asset caching uses a dedicated shell cache for HTML, JS, CSS, fonts, and manifest assets. The shell cache is updated only through controlled service worker activation and skipWaiting flows to prevent stale shell persistence. Static assets are immutable and follow a content-hash versioning scheme.

## 8. API Cache Rules
API cache rules distinguish between read-mostly resources and transient operational data. Read resources such as configuration metadata and product lists may be cached with stale-while-revalidate semantics, while transactional endpoints use network-first with cache fallback for offline viewability.

## 9. Runtime Cache Strategy
Runtime cache strategy caches API payloads and computed state selectively in IndexedDB and a response cache. Cache entries are tagged by tenant, route, and entity type. The strategy prioritizes freshness for active workflows and persistence for offline continuity.

## 10. Offline Shell Rules
The offline shell must always be available and never rely on a network load to render core navigation. Shell rules include: render skeleton UI from local cache, show offline indicators immediately, hydrate with cached route state, and delay heavy data until network or sync is available.

## 11. Offline Navigation Strategy
Offline navigation uses a route graph that is decoupled from live data. Navigation targets should load cached route pages, fall back to safe summary screens, and preserve context for queued operations. Deep links should resolve to the last known good route or a safe recovery route.

## 12. IndexedDB Architecture
IndexedDB is the authoritative offline persistence layer for queued operations, drafts, media metadata, sync checkpoints, and tenant-scoped caches. The schema is versioned, namespaced by tenant and user, and designed with granular object stores for operation queues, media uploads, and local state snapshots.

## 13. Offline Queue Persistence
Offline queue persistence stores every offline operation in an atomic queue. Each queued record includes request metadata, payload hash, timestamp, tenant context, permission identity, and retry metadata. Queue persistence survives app restarts and service worker updates.

## 14. Draft Persistence Rules
Draft persistence preserves user draft state locally for forms, reports, notes, and field entries. Drafts are saved at meaningful interaction points, batched during idle time, and retained until successful sync or explicit discard. Draft data must never be lost due to cache eviction alone.

## 15. Background Sync Architecture
Background sync architecture uses service-worker-driven sync events, periodic sync when supported, and app runtime wake-up strategies. Sync jobs are orchestrated in stages: queue hydration, dependency resolution, upload execution, and conflict reconciliation.

## 16. Sync Replay Strategy
Sync replay is deterministic and ordered. Offline operations are replayed in the same sequence they were queued, honoring dependency relationships and preventing duplicates. Each replay step is idempotent and records success codes to avoid reprocessing completed operations.

## 17. Media Upload Recovery
Media upload recovery stores upload metadata, current chunk status, and retry state in IndexedDB. Recovery supports resumed uploads after app restarts, service worker restarts, connection loss, or low battery events. Media chunks are uploaded incrementally, and partial progress is preserved.

## 18. Deferred Upload Strategy
Deferred upload strategy caches media locally and defers large payloads until connectivity meets policy thresholds. Small operational attachments may upload immediately when weak but available networks are detected; large images or video are queued for recovery and user confirmation.

## 19. Connectivity Detection Rules
Connectivity detection uses navigator.onLine and active probe checks against trusted endpoints. The app maintains connection state categories: online, slow, intermittent, and offline. Detection rules favor actual network reachability over browser-reported status.

## 20. Sync Conflict UX
Sync conflict UX surfaces conflicts clearly and safely. When remote changes conflict with offline edits, users see concise context, suggested resolutions, and a safe undo path. Conflicts must never be auto-resolved without explicit user or domain logic consent.

## 21. Offline Indicators UX
Offline indicators are persistent, visible, and non-blocking. Indicators include banner status, sync progress markers, queued operation counts, and retry state. They communicate resilience rather than failure, avoiding alarmism.

## 22. Mobile Memory Constraints
Mobile memory constraints require small cache footprints, paged IndexedDB access, and limited concurrent uploads. The PWA avoids storing massive blobs in memory by streaming files and using on-disk caching via IndexedDB or the service worker.

## 23. Battery Optimization Rules
Battery optimization rules throttle background sync, defer non-essential work, and avoid CPU-heavy tasks on low power. The PWA honors battery status APIs and reduces polling or prefetching when the device reports low battery.

## 24. Weak Network Optimization
Weak network optimization uses adaptive request strategies, low-bandwidth asset delivery, and incremental sync. The PWA detects slow connections and switches to compressed payloads, lightweight UI, and offline-friendly workflows.

## 25. App Startup Performance
App startup performance is achieved by loading the shell first, deferring heavy route data, and prewarming IndexedDB only when needed. The initial render should be sub-second on low-end Android devices, with non-blocking hydration of cached state.

## 26. Lazy Loading Strategy
Lazy loading strategy applies to route bundles, feature modules, media viewers, and non-critical components. The PWA loads only what is needed for the current task, deferring diagnostics, analytics, and large charting modules until the user navigates there.

## 27. Offline Authentication Strategy
Offline authentication strategy caches a validated session token and minimal identity claims securely in IndexedDB. It avoids storing raw credentials, expires offline sessions based on policy, and requires network revalidation for sensitive operations.

## 28. Push Notification Readiness
Push notification readiness is architected for eventual support while keeping the core PWA functional without it. The service worker remains capable of receiving push messages if enabled, but the offline model does not depend on push for core sync or recovery.

## 29. Device Storage Constraints
Device storage constraints are respected by limiting caches, pruning stale entries, and prioritizing critical operational data. The PWA uses eviction policies that retain queue data and drafts before less essential assets.

## 30. PWA Security Rules
PWA security rules enforce HTTPS, service worker scope control, CSP headers, safe offline auth persistence, and secure IndexedDB access patterns. The service worker must never expose sensitive payloads in public caches or leak tenant data across scopes.

## 31. White-Label PWA Isolation
White-label PWA isolation keeps tenant branding, theme assets, and feature sets siloed at runtime. Offline storage, cache namespaces, and service worker routing are tenant-aware to prevent cross-tenant data leakage.

## 32. Tenant-Aware Offline Storage
Tenant-aware offline storage namespaces caches and IndexedDB stores by tenant and user. Each tenant gets isolated persisted queues, media recovery metadata, and shell configuration to ensure safe multi-tenant operation on shared devices.

## 33. Update Delivery Strategy
Update delivery strategy uses service worker lifecycle hooks to install new shell versions in the background and prompt users when stable. Updates are applied safely without discarding queued offline operations or corrupting cached state.

## 34. PWA Observability Rules
PWA observability rules capture offline state transitions, sync success/failure, cache invalidation, and recovery workflows. Observability events are emitted without exposing private data, enabling diagnosis of weak-network and offline failures.

## 35. Failure Recovery Strategy
Failure recovery strategy isolates failures to individual route or sync tasks, recovers shell availability, and provides explicit recovery actions. It avoids global cache wipes by repairing only affected entries and preserving queued offline work.

## 36. AI Safety Rules
AI safety rules forbid giant service workers, uncontrolled caching, storing massive blobs in memory, blocking UI during sync, infinite retry loops, stale shell persistence, global cache wipes, and unsafe offline auth persistence. AI-generated PWA logic must remain modular, predictable, and aligned with deterministic offline workflows.

## 37. Forbidden PWA Anti-Patterns
- monolithic service worker scripts
- caching all network traffic indiscriminately
- loading large media into memory instead of streaming
- blocking UI while sync runs
- retrying forever without backoff or user control
- persisting stale shell state indefinitely
- clearing all caches on failure
- storing credentials in localStorage or exposed caches
- allowing tenant data to cross service worker scope boundaries

## 38. Real-World Agricultural Offline Scenarios
- a field technician captures crop observations and continues working while connectivity drops, with the draft saved locally and later synced when the network returns
- a remote farm worker installs the PWA, opens the shell offline, and navigates to cached operational summaries and job assignment pages
- an inspector uploads images of equipment damage; the media payload is queued and resumed after reconnecting, preserving progress across app restarts
- a multi-tenant support device retains tenant-specific offline queues and avoids leaking another tenant's farm data

## 39. Future Mobile Expansion Strategy
Future expansion includes smarter offline AI guidance, predictive prefetching for likely next tasks, deeper low-bandwidth media compression, preloaded tenant workflows, and expanded background sync policies that respect device health and field conditions.

## 40. Final PWA Enforcement Checklist
- app shell is always available offline
- service worker scope is controlled and thin
- caches are versioned and isolated
- runtime data is stored in IndexedDB, not memory
- queued operations survive restarts
- media upload recovery supports resumed uploads
- offline auth is secure and limited
- sync replay is deterministic and ordered
- stale shell persistence is prevented
- weak network and battery rules are enforced
- tenant and white-label isolation are preserved
- updates are delivered safely
- forbidden PWA anti-patterns are avoided
- AI safety constraints are explicitly enforced
