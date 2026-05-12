# ATLS Platform: Operations Domain Architecture

> **Confidential & Proprietary**  
> **Target Audience:** Principal Architects, Engineering Leads, AI Implementation Agents  
> **Domain:** Agricultural ERP & Operations Platform  

---

## 1. Domain Purpose
The Operations Domain is the transactional beating heart of the ATLS agricultural ERP platform. It manages the complete lifecycle of all field activities (e.g., pruning, spraying, harvesting, irrigation) executed across the farm hierarchy. It transforms physical agricultural intent into auditable, cost-tracked, and propagated digital reality.

## 2. Business Goals
*   **Traceability:** Ensure every drop of water, gram of fertilizer, and minute of labor is tracked to a specific enclosure and season.
*   **Mobility:** Empower supervisors to record operations offline in the middle of a field and sync seamlessly.
*   **Costing:** Provide the foundation for accurate cost-per-hectare and cost-per-kilo analytics.
*   **Compliance:** Maintain unshakeable audit trails for agricultural regulatory bodies (e.g., GlobalGAP).

## 3. Ubiquitous Language
*   **Operation:** A discrete agricultural activity (e.g., "Spraying Block A").
*   **Enclosure:** The physical bounding area (defined in `FARM_DOMAIN`) where the operation occurs.
*   **Propagation:** The automatic roll-up of operational metrics (costs, quantities) from child enclosures to parent sectors/regions.
*   **Consumption:** The deduction of physical inventory (e.g., chemicals) due to an operation.
*   **Completion:** The measured progress of an operation (0-100%), which may be calculated via area, trees, or quantity.

## 4. Core Concepts
The domain operates on intent and execution. An operation transitions from a planned schedule into a physical reality. Operations can target a single Enclosure or span across multiple Enclosures, triggering complex asynchronous propagation workflows to ensure parent hierarchies reflect the aggregated work.

## 5. Operation Aggregate Design
The `OperationAggregate` is the root entity.
*   **Owned Entities:** `WorkerAssignment`, `EquipmentUsage`, `InventoryConsumption`, `OperationLog`.
*   **Invariants:** 
    *   Cannot be assigned to an inactive Enclosure.
    *   Cannot consume more inventory than available (checked via eventual consistency or strict locks).
    *   Must belong to an active `SeasonAggregate`.

## 6. Operation Types
Operations are highly polymorphic, driven by a dynamic engine, but fundamentally grouped into:
*   **Standard Operations:** Pruning, weeding, planting.
*   **Application Operations:** Spraying, fertilization (requires Inventory constraints).
*   **Harvest Operations:** Yield gathering (interfaces heavily with the Harvest Domain).
*   **Measurement Operations:** Soil sampling, phenological tracking.

## 7. Completion Logic
Completion is a dynamic calculation, not a static field.
*   **Area-Based:** Completed Hectares / Total Hectares.
*   **Tree-Based:** Pruned Trees / Total Living Trees.
*   **Quantity-Based:** Harvested Kilos / Estimated Kilos.
*   **Manual Override:** Supervisors can manually force completion to 100%, bypassing dynamic calculations, triggering an explicit audit event.

## 8. Propagation Rules
*(Respecting `FARM_DOMAIN.md` constraints)*
*   Operations recorded at a child `Plot` level emit events that the `OperationPropagationService` uses to asynchronously update the parent `Sector` or `Region`.
*   Propagation is strictly asynchronous (Event-Driven) to prevent synchronous database locks on high-level hierarchy nodes.
*   Idempotency locks ensure siblings do not overwrite each other during concurrent propagation.

## 9. Worker Assignment Logic
*   Workers are attached to the `OperationAggregate`.
*   Includes time-tracking (start/end) or piece-rate tracking (e.g., paid per tree pruned).
*   Integrates with the HR domain via Domain Events (`WorkerAssignedToOperation`), but `Operations` holds the authoritative transactional record of the labor execution.

## 10. Equipment Assignment Logic
*   Equipment (tractors, sprayers) are assigned with meter readings (e.g., starting/ending engine hours).
*   Usage data emits `EquipmentUsed` events, consumed by the Equipment Domain for maintenance scheduling.

## 11. Inventory Consumption Rules
*   Operations recording chemical or fertilizer usage trigger `InventoryConsumed` events.
*   **Eventual Consistency:** The mobile app allows negative local deductions. The server resolves this via the Inventory Domain. If stock falls below zero, a `NegativeInventoryAlert` is escalated to managers. Operations do NOT fail to save due to missing inventory to ensure field work is always recorded.

## 12. Seasonal Relationships
*   Every operation is strictly bound to a `SeasonAggregate`.
*   If a season is `CLOSED`, no new operations can be created, and existing operations become immutable.
*   Cross-season operations are forbidden. A multi-year task must be split.

## 13. Recurring Operations
*   Configured via cron-style schedules.
*   A background worker evaluates active recurrences daily and instantiates physical `OperationAggregates` in a `PLANNED` state.

## 14. Scheduled Operations
*   Operations start as `PLANNED` or `SCHEDULED`.
*   They carry forecasted worker/equipment needs.
*   Transitioning a scheduled operation to `IN_PROGRESS` locks its foundational parameters (target enclosure, type).

## 15. Offline Recording Rules
*   Mobile clients download `PLANNED` operations and the Enclosure hierarchy.
*   Supervisors record completions, worker hours, and inventory usage offline.
*   Payloads are stored locally with a `sync_uuid` and client-side timestamp.

## 16. Conflict Resolution
*   Handled by `OfflineMergeService`.
*   **Additive Merge:** If Device A logs 50 trees pruned, and Device B logs 40 trees pruned on the same operation, the server merges to 90 trees. 
*   **Last-Write-Wins (LWW):** Applied *only* to scalar metadata (e.g., changing the operation "Notes" field), based on the client timestamp.

## 17. Validation Rules
*   Dates must be contiguous (End Date >= Start Date).
*   Operation cannot target an Enclosure that doesn't support the crop required by the operation type.
*   All validations execute synchronously before the `OperationAggregate` is saved to the database.

## 18. Operational State Machines
*   **Flow:** `PLANNED` -> `IN_PROGRESS` -> `REVIEW_PENDING` -> `COMPLETED` -> `ARCHIVED`.
*   Transitions are unidirectional. Reverting `COMPLETED` to `IN_PROGRESS` requires a `SUPER_ADMIN` override audit.

## 19. Domain Events
*   `OperationCreated`
*   `OperationStateChanged`
*   `OperationMetricsUpdated`
*   `WorkerHoursLogged`
*   `InventoryConsumed`
Events are published via the Transactional Outbox.

## 20. Audit Rules
*   Every state transition and completion update generates an immutable `OperationAuditLog` entry containing the `user_id`, `device_id`, and `correlation_id`.
*   Audit logs are append-only.

## 21. Read Models
*   Complex dashboards (e.g., "Daily Farm Activities") query heavily denormalized `OperationReadModel` tables in ElasticSearch or specialized Postgres views.
*   Read models are updated asynchronously via `OperationMetricsUpdated` events.

## 22. CQRS Relationships
*   **Commands:** `CreateOperation`, `LogWorkerHours`, `CompleteOperation` (Handled by Application Services, mutating the Aggregate).
*   **Queries:** `GetOperationsByEnclosure`, `GetDailyActivitySummary` (Handled by Read Model projections, bypassing the Aggregate).

## 23. Permissions
*   Permissions evaluate dynamically against the hierarchy: `can_edit_operation` checks if the user's explicit scope includes the target `Enclosure` or its parent `Region`.
*   Role assignment is flexible, but access is boundary-restricted.

## 24. Mobile UX Considerations
*   Operations are downloaded as flattened DTOs.
*   Forms use the Dynamic Form Engine, adapting to the operation type seamlessly.
*   Inputs favor large tap targets for gloved hands in field conditions.

## 25. RTL Considerations
*   The operational timeline and step-by-step wizards must natively reverse direction using logical CSS properties (`margin-inline-start`) for Arabic/Hebrew tenants.

## 26. Analytics Relationships
*   Analytics depend on Operations. Operations NEVER depend on Analytics.
*   Operational data is streamed to data lakes via events to calculate high-level farm yield and efficiency KPIs.

## 27. AI Safety Rules
> [!CAUTION]
> **MANDATORY AI IMPLEMENTATION RULES**
*   **No Synchronous Side-Effects:** AI must not write code that deducts inventory or updates the HR system synchronously within an Operation save.
*   **No Direct DB Updates:** AI must not use `Operation.objects.update(status='COMPLETED')`. State transitions must call `operation.complete()`.
*   **Tenant Scoping:** Every single query must include `tenant_id`. AI code omitting this will be rejected.

## 28. Performance Constraints
*   **Batching:** Mobile syncs batch operations (max 100 per payload).
*   **Lazy Loading:** `OperationAggregate` does not eagerly load its entire audit history to preserve memory.
*   **Propagation Limits:** Hierarchy propagation yields to the message broker if depth exceeds tenant thresholds.

## 29. Anti-Patterns
*   **The God Operation:** Storing inventory stock levels inside the Operation table.
*   **Blocking Integrations:** Waiting for a weather API to confirm conditions before allowing a spray operation to be saved.
*   **Hidden Writes:** Mutating the `SeasonAggregate` from inside the `OperationAggregate`.

## 30. Real-World Scenarios
**Scenario:** A manager offline in "Sector A" logs 500 liters of pesticide used across 10 enclosures, but only 400 liters exist in inventory.
*   **Action:** The mobile app accepts the operation. 
*   **Sync:** Device hits cellular connectivity. Payload uploads to `OfflineMergeService`.
*   **Result:** Operations are saved. `InventoryConsumed` events fire. The Inventory domain processes the events, drops stock to -100, and immediately fires a `CriticalNegativeStock` alert to the purchaser. Field work is not blocked by administrative stock errors.

---

## 31. Operation Templates System
The platform utilizes a robust templating architecture to standardize recurring field activities across the enterprise.
*   **Reusable Operation Templates:** Defines baseline metadata (e.g., standard fertilizer dosage, default equipment) to rapidly generate planned operations.
*   **Crop & Seasonal Specificity:** Templates can be scoped strictly to specific crops or `SeasonAggregates`.
*   **Enclosure-Type Templates:** Templates scoped to Enclosure attributes (e.g., "Trellis Repair" only available for vine-based enclosures).
*   **Template Inheritance:** A global "Pruning Base" template can be inherited and overridden by regional templates.
*   **Template Versioning:** Modifying a template creates a new version (`v2`). Existing `PLANNED` operations derived from `v1` are unaffected to preserve historical intent.
*   **Deactivation Rules:** Templates cannot be hard-deleted. They are marked `is_active=False` to prevent future usage.
*   **Propagation Behavior:** When templates are attached to recurring schedules, they act as the factory definition, spinning up actual `OperationAggregate` instances and pushing them as `PLANNED` into the mobile offline payloads.

## 32. Operation Cost Engine
The Operations Domain holds the absolute source of truth for all direct field execution costs.
*   **Labor Cost Calculations:** Derived from `WorkerAssignment` durations multiplied by HR rate cards or piece-rate logs.
*   **Contractor Cost Calculations:** Invoice-aligned tracking for third-party labor groups.
*   **Equipment Operational Cost:** Engine hours multiplied by equipment depreciation/maintenance rates.
*   **Material Consumption Cost:** Exact inventory deductions evaluated against the moving average cost (MAC) or FIFO cost at the exact time of consumption.
*   **Estimated vs Actual Cost:** The template holds the *estimated* cost. The executed operation holds the *actual* cost.
*   **Variance Calculations:** The engine exposes cost variance (Actual - Estimated) for financial alerting.
*   **Async Cost Recalculation:** Costing is strictly asynchronous. If the HR domain retroactively updates a worker's hourly rate, it emits an event that triggers an eventual recalculation of the historical operation cost.

## 33. Approval Workflow System
High-risk or high-cost operations require explicit approval workflows to prevent unauthorized physical execution.
*   **Required States:** `DRAFT` -> `SUBMITTED` -> `REVIEW_PENDING` -> `APPROVED` -> `REJECTED` -> `LOCKED`.
*   **Approval Authority:** Permission engine checks if the approving user has the exact `can_approve_operation` capability for the target Enclosure and Operation Type.
*   **Immutable States:** Once `LOCKED` (e.g., after the financial season closes), no further transitions or data edits can occur.
*   **Rejection Handling:** Transitions to `REJECTED` demand an audit reason. The operation can be cloned, but the rejected record remains as an audit artifact.
*   **Mandatory Approvals:** Standard pruning may not require approval, but *pesticide spraying*, *inventory-heavy operations*, and *high-cost operations* natively force the `REVIEW_PENDING` state before they can hit the mobile offline payload.
*   **Emergency Override Behavior:** Field conditions change rapidly. A `SUPER_ADMIN` can execute an emergency override, bypassing the queue, which instantly escalates an SMS/Email to farm executives.

## 34. Operation Dependency Graph
Operations do not exist in a vacuum; they form a sequential execution graph.
*   **Dependency Validation:** Prevents execution of an operation if prerequisite operations are incomplete (e.g., "Fertilization" strictly requires "Irrigation" completion).
*   **Soft vs Hard Dependencies:** 
    *   *Hard:* Harvest is strictly blocked during a pesticide spray's Re-Entry Interval (REI).
    *   *Soft:* Pruning should happen before pollination, but can be bypassed with a warning.
*   **Circular Dependency Prevention:** The graph validates at creation time to prevent Deadlocks (A requires B, B requires A).
*   **Seasonal Dependency Behavior:** Dependencies reset upon transitioning to a new `SeasonAggregate`.

## 35. Operational KPI Engine
Operations emit events to populate eventually consistent Read Models for real-time KPIs.
*   **Productivity KPIs:** Productivity per worker (kilos/hour), productivity per enclosure.
*   **Cost KPIs:** Cost per living tree, cost per kilogram of yield.
*   **Efficiency:** Operation duration vs estimated template duration.
*   **Delayed/Failed Operations:** Flags operations that missed their scheduled window or were abandoned.
*   **Async Generation & Projection:** KPIs are NOT calculated inside the transactional boundary. They are generated asynchronously via projection rules owned by the Analytics domain, parsing `OperationMetricsUpdated` events.

## 36. AI Safety Enhancements (Operations Domain)
> [!CAUTION]
> **ENHANCED AI-AGENT RULES FOR OPERATIONS**
*   **Prohibited Synchronous Analytics:** AI agents MUST NOT implement KPI calculations inside the `OperationAggregate.save()` method or its synchronous lifecycle.
*   **Prohibited Direct Cost Mutations:** AI agents MUST NOT directly update the `.total_cost` attribute. Costs must be derived via the Cost Engine recalculation handlers.
*   **Prohibited Workflow Bypasses:** AI agents MUST NOT write code that transitions an operation directly from `DRAFT` to `IN_PROGRESS` if the operation type flags `requires_approval=True`.
*   **Prohibited Deletion:** AI agents MUST NOT write ORM delete calls (`.delete()`) for historical operational records. Only `.soft_delete()` is permitted.
