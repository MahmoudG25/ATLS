# OFFLINE STRATEGY

## Purpose
Define the ATLS master offline-first architecture for the agricultural platform. This document establishes the rules and patterns for resilient synchronization, persistence, conflict recovery, media upload handling, and tenant-safe offline behavior.

## Scope
Covers offline-first philosophy, sync engine architecture, queue persistence, mutation replay, background sync, offline UX, local storage strategies, mobile network awareness, and production-safe AI restrictions.

## Current Status
- [x] Not Started
- [ ] In Progress
- [ ] Completed

## Dependencies
- `docs_v2/01_ARCHITECTURE/STATE_MANAGEMENT.md`
- `docs_v2/01_ARCHITECTURE/FRONTEND_ARCHITECTURE.md`
- `docs_v2/01_ARCHITECTURE/API_ARCHITECTURE.md`
- `docs_v2/01_ARCHITECTURE/EVENT_SYSTEM.md`
- `docs_v2/01_ARCHITECTURE/DATABASE_ARCHITECTURE.md`
- `docs_v2/01_ARCHITECTURE/BACKEND_ARCHITECTURE.md`
- `docs_v2/07_AI_AGENT/AI_DEVELOPMENT_RULES.md`

## Notes
Offline-first is a core system requirement for ATLS. Offline capability must be designed, tested, and treated as a first-class architectural concern.

## Last Updated
2026-05-12

---

## 1. Offline-First Philosophy
ATLS treats offline-first as a platform guarantee, not an optional feature. The system is designed for farms, remote desert sites, and unstable mobile networks where connectivity is intermittent, expensive, or nonexistent.
- Local persistence and queueing are mandatory.
- The UX remains responsive while server synchronization happens asynchronously.
- The platform accepts eventual consistency in favor of uninterrupted field operations.

## 2. Why Offline Matters
Offline capability preserves productivity in real agricultural workflows:
- farmers and technicians can continue logging operations without waiting for connectivity
- remote sensors and media-heavy inspections can be recorded and synchronized later
- field teams avoid lost work in areas with weak or intermittent signal
- business-critical inventory and dispatch workflows remain available during outages

## 3. Connectivity Assumptions
ATLS assumes:
- connectivity is occasionally available and may be slow
- networks can be highly variable across geographic regions
- mobile data may be metered and expensive
- sync should function under intermittent windows and resume after drops
- connectivity state must be detected accurately and gracefully handled

## 4. Offline Capability Matrix
Offline support must be evaluated across the following dimensions:
- read operations: cached dashboards, last-known values, and reference data
- write operations: queued commands and optimistic updates
- media capture: offline staging of images and video metadata
- authentication: offline token refresh and session rehydration
- UI availability: navigation, forms, and critical workflows
- recovery: replay, conflict handling, and data integrity

## 5. Sync Engine Architecture
The sync engine is the core offline orchestration layer. It consists of:
- a persistent offline mutation queue
- retry and backoff policies
- network awareness and battery-aware scheduling
- background sync orchestrator
- queue replay and conflict detection
- audit-safe commit markers

React Query remains the authoritative server-state engine, while the sync engine manages offline persistence and replay semantics.

## 6. Offline Mutation Queue
All offline write operations must be enqueued. The queue:
- stores commands and payloads, not derived data snapshots
- preserves original intent and ordering
- isolates tenant context per item
- remains accessible to sync and recovery workflows

In-memory-only queues are forbidden.

## 7. Queue Persistence Strategy
- Persist queue items locally using secure storage such as IndexedDB or platform-native storage.
- Use structured adapters to abstract storage differences across web and mobile.
- Store metadata with each item: tenant id, request id, timestamp, retry count, and dependencies.
- Ensure persisted queue state survives app restarts and process termination.

## 8. Queue Replay Lifecycle
Queue replay must follow a defined lifecycle:
1. load persisted queue items on startup
2. validate item order and tenant context
3. execute replay against the server in sequence
4. apply optimistic state where safe
5. handle success, conflict, and failure explicitly
6. persist replay progress and item state

## 9. Idempotent Replay Rules
- Every queued action must be idempotent or safely retryable.
- Include server-generated ids or request fingerprints to detect duplicates.
- Avoid retrying non-idempotent side effects without a safe server-side guard.
- If the server returns a duplicate error, treat it as success for replay semantics.

## 10. Sync Ordering Rules
- Maintain original user intent order for dependent operations.
- Preserve prioritization for critical operational commands.
- Allow independent actions to execute in parallel only when they affect distinct resources.
- Use causal ordering for commands that depend on previous state changes.

## 11. Conflict Resolution Philosophy
Conflicts are expected in offline-first operation. The system must:
- preserve user intent where possible
- favor server truth for authoritative state
- surface conflicts for user intervention when automatic merge is unsafe
- recover with minimal data loss

## 12. Last-Write-Wins Rules
- Last-write-wins may be applied only for low-risk metadata updates and simple toggles.
- For core domain state such as inventory counts, crop data, or asset status, last-write-wins is a fallback, not the default.
- Always prefer explicit conflict metadata and merge logic over blind overwrite.

## 13. Additive Merge Rules
- Use additive merge for appending logs, comments, and non-destructive updates.
- Merge operations must preserve history and prevent accidental deletion of existing values.
- Additive merge is appropriate for field notes, attachments lists, and status timelines.

## 14. Human Conflict Resolution Workflows
- When automatic resolution is unsafe, provide clear user workflows to resolve conflicts.
- Present conflicting values, timestamps, and source context.
- Allow the user to accept server state, keep local edits, or merge fields manually.
- Record the chosen resolution in audit logs and replay metadata.

## 15. Optimistic Offline Execution
- Support optimistic execution for responsive field workflows.
- Optimistic updates must use React Query and localized query patching.
- Capture rollback snapshots before applying optimistic state.
- Do not block UI while waiting for offline queue persistence or eventual server confirmation.

## 16. Background Sync Architecture
- Background sync is a first-class component of offline architecture.
- It runs outside the user action thread when possible and resumes work on reconnect.
- It manages queue replay, media upload progression, and read model refresh.
- It coordinates with battery/network policies and app lifecycle events.

## 17. Service Worker Strategy
- Use service workers on web to enable background sync and offline caching.
- Service workers should manage fetch fallback for cached resources, queue replay triggers, and periodic sync when supported.
- Do not use service workers as the sole source of truth for mutation persistence.
- Ensure service worker behavior is tenant-isolated and safe for white-label deployments.

## 18. Network Awareness Rules
- Detect connection quality and type accurately.
- Use conservative sync behavior on weak or expensive networks.
- Avoid aggressive retries when the network is offline or unstable.
- Provide clear UI state for offline, limited connectivity, and sync progress.

## 19. Battery-Aware Synchronization
- Pause non-critical background sync when the device is low on battery.
- Defer large uploads or non-essential polling to charging or stable connectivity windows.
- Allow critical operational sync to continue with explicit user consent if necessary.
- Respect platform power-saving modes and low-power settings.

## 20. Media Upload Strategy
- Separate media uploads from critical operational mutations.
- Stage media metadata and references in the command queue, while uploads occur in a dedicated media queue.
- Avoid blocking mission-critical commands on large media transfer completion.
- Keep media upload progress and retry state independent from core business command replay.

## 21. Chunk Upload Recovery
- Upload media in resumable chunks when available.
- Track upload progress, completed chunks, and retry headers.
- Recover from partial failures by resuming rather than restarting uploads where supported.
- Persist chunk state locally until the full asset is confirmed by the server.

## 22. Large Video Upload Rules
- Treat large video uploads as low-priority background sync tasks unless explicitly required for immediate operations.
- Throttle video transfer on weak networks and defer until better conditions are available.
- Use metadata-only queue items while the raw media upload proceeds in the background.
- Avoid storing large blobs in RAM or global state.

## 23. Offline Media Metadata
- Persist only media metadata, thumbnails, and references in the offline queue, not full binary blobs in global state.
- Keep media metadata tenant-safe and isolated per farm or brand.
- Use local storage for lightweight preview assets and persist actual files through platform file storage APIs.

## 24. Draft Persistence Strategy
- Persist form drafts locally for offline recovery.
- Store draft metadata, field values, and context keys in indexed storage.
- Version drafts to detect schema changes and prevent stale submission.
- Expire or prune old drafts to avoid stale cache bloat.

## 25. Offline Form Recovery
- Rehydrate offline forms automatically when connectivity is unavailable.
- Preserve unsaved changes across navigation and app restarts.
- Merge server-loaded defaults with local draft state safely on reconnect.
- Provide users with conflict-aware prompts when draft content differs from fresh server values.

## 26. Read Model Caching Strategy
- Cache read models locally to support offline dashboards and lookup screens.
- Use explicit invalidation on reconnection and after successful mutations.
- Treat cached read models as stale-by-default until refreshed on reconnect.
- Avoid storing large, full-domain read model snapshots indefinitely.

## 27. Offline Search Strategy
- Provide lightweight offline search over cached indexes and reference data.
- Limit offline search to locally persisted content and metadata.
- Use server-side search for wide queries when connectivity resumes.
- Indicate when search results are offline and may not be complete.

## 28. Offline Navigation Strategy
- Maintain navigation state locally so users can move through core workflows offline.
- Persist the current route context and form state for recovery.
- Avoid deep linking to server-only screens when offline unless cached fallback data is available.
- Use navigation state to guide users to recoverable offline workflows.

## 29. Offline Authentication Rules
- Persist auth tokens and session state securely for offline access.
- Rehydrate auth state on startup and validate it before replay.
- Avoid storing sensitive credentials in unencrypted storage.
- Invalidate offline session state on logout and propagate logout across active sessions.

## 30. Tenant Isolation Offline
- Partition offline storage by tenant identifier.
- Ensure offline queues, drafts, and caches never mix tenant data.
- Enforce tenant-scoped keys in every persisted store.
- Prevent cross-tenant reads or writes in offline modes.

## 31. White-Label Offline Isolation
- Keep white-label branding and configuration isolated per deployment instance.
- Persist offline assets and preferences separately for each brand or customer variant.
- Do not share offline queue or draft state across brand contexts.
- Ensure offline UI behavior respects the active white-label theme and tenant security.

## 32. Sync Failure Recovery
- Detect sync failures explicitly and keep failed items in the queue.
- Expose failure reasons to users and support retry or defer actions.
- Do not drop failed queue items silently.
- Use backoff and retry policies tuned for unstable connectivity.

## 33. Corrupted Queue Recovery
- Validate persisted queue integrity at load time.
- If corruption is detected, isolate and discard only the affected queue shard.
- Preserve unaffected queue items and recover gracefully.
- Log corruption events for diagnostics without disrupting the entire offline store.

## 34. Partial Sync Recovery
- Handle partial sync success by marking items individually and continuing replay for the rest.
- Validate final server state with follow-up queries if some items succeed and others fail.
- Use transactional semantics only when the backend explicitly supports atomic batches.
- Avoid giant replay transactions that block the queue.

## 35. Multi-Device Synchronization
- Support multi-device workflows by treating each device as a possible source of queued intents.
- Avoid local-only assumptions; always refresh shared server state after reconnect.
- Coordinate active session state using tenant-safe sync markers.
- Detect out-of-date devices and prompt for refresh when necessary.

## 36. Sync Observability
- Provide telemetry for queue length, retry counts, sync success, and failure reasons.
- Expose offline sync state in diagnostics without leaking tenant data.
- Track background sync activity separately from user-initiated mutations.
- Make sync health visible in admin dashboards and logs.

## 37. Offline UX Rules
- Keep the UI responsive while background sync operates.
- Display clear offline indicators and sync progress.
- Allow users to continue critical tasks even when connectivity is unavailable.
- Avoid blocking forms, navigation, or data entry during synchronization.

## 38. AI Safety Rules
AI-guided implementation must forbid:
- in-memory-only offline queues
- blocking the UI during sync operations
- synchronous media uploads on the main thread
- giant replay transactions that span unrelated commands
- non-idempotent offline sync behavior
- tenant leakage in persisted offline storage
- silent conflict overwrites without user visibility

## 39. Forbidden Offline Anti-Patterns
- relying on temporary in-memory queues only
- performing sync on every state change without batching
- storing server entities in localStorage as a database
- forcing long-running uploads in the foreground
- applying auto-merge conflicts without explicit resolution paths
- using offline data across tenants without isolation

## 40. Real-World Agricultural Scenarios
- **Remote desert farm:** a field inspector records drought reports and crop measurements offline, then reconnects through a satellite link to replay queued commands in order.
- **Mobile equipment check:** a mechanic captures machine diagnostics and photos offline, with metadata persisted separately from the large media upload queue.
- **Supervisor overlap:** two supervisors edit the same enclosure offline and later reconcile conflicting status updates through a guided merge workflow.
- **Harvest season spike:** the app prioritizes yield capture and inventory adjustments while deferring non-critical telemetry and background analytics sync.
- **Partial sync inventory:** a warehouse worker submits inventory deductions offline, and the platform recovers from partially applied sync by validating final counts and retrying failed entries.

## 41. Future Offline Evolution Strategy
- advance native bridge support for platform-specific persistence and background execution
- explore server-assisted CRDT patterns for selected collaboration workflows
- improve websocket and push-based sync for low-latency reconnects
- refine edge sync for local caching and service-worker-managed retry
- evolve the offline engine to support more intelligent priority and conflict handling over time
