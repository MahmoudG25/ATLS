# ATLS Platform: Equipment Domain Architecture

> **Confidential & Proprietary**  
> **Target Audience:** Principal Architects, Engineering Leads, AI Implementation Agents  
> **Domain:** Agricultural ERP & Operations Platform  

---

## 1. Domain Purpose
The Equipment Domain is the operational lifecycle and maintenance management system for all physical machinery. It ensures that tractors, trailers, atomizers, and pumps are tracked, maintained, fueled, and utilized effectively. It bridges the gap between field operations (where equipment is used) and asset management (how equipment is maintained).

## 2. Business Goals
*   **Maximize Uptime:** Prevent costly field breakdowns during critical operational windows (e.g., Harvest) through rigorous preventive maintenance.
*   **Operational Costing:** Accurately track fuel burn, depreciation, and maintenance costs to calculate the true cost of farm operations.
*   **Asset Accountability:** Maintain an unshakeable audit trail of who operated a machine, when it broke, and who authorized the repair.
*   **Future Readiness:** Establish an architecture capable of absorbing high-frequency IoT telemetry and CAN bus data.

## 3. Ubiquitous Language
*   **Equipment / Asset:** Any managed physical machine (Tractor, Pump, Generator).
*   **Runtime:** The cumulative hours or mileage a machine has operated.
*   **Work Order (WO):** A formal directive to perform maintenance, inspections, or repairs.
*   **Breakdown:** An unscheduled failure of equipment, immediately transitioning its state to `OUT_OF_SERVICE`.
*   **Telematics:** Sensor-derived data (GPS, engine codes) emitted by the equipment.

## 4. Core Concepts
The Equipment Domain operates on **Condition and Lifecycle**. Machines degrade over time or usage. The system’s responsibility is to track that degradation (Runtime), schedule interventions (Maintenance), and manage the physical state (Available, In-Use, Broken, Scrapped) without tightly coupling to the Operations domain.

## 5. Equipment Aggregate Design
The `EquipmentAggregate` is the core entity.
*   **Owned Entities:** `RuntimeLog`, `FuelLog`, `MaintenanceWorkOrder`, `AssignmentHistory`.
*   **Invariants:**
    *   Must belong to a valid `tenant_id`.
    *   Cannot be assigned to an operation if state is `OUT_OF_SERVICE` or `SCRAPPED`.
    *   Runtime meters (Hours/Mileage) can only monotonically increase; they cannot be rolled back without an explicit audit override.

## 6. Equipment Types
*   **Mobile Assets:** Tractors, Harvesters, Motorcycles, ATVs.
*   **Implements/Attachments:** Trailers, Atomizers, Plows (often assigned together with a Mobile Asset).
*   **Static Assets:** Generators, Fixed Pumps, Weather Stations.
*   **Small Tools:** Chainsaws, Pruning Shears (tracked in bulk or simple assignment).

## 7. Asset Classification Rules
Classification dictates maintenance behavior. A Tractor requires hour-meter tracking, whereas a Delivery Truck requires mileage tracking. Small tools may only require time-based inspections.

## 8. Equipment Lifecycle
*   **States:** `COMMISSIONED` -> `AVAILABLE` -> `IN_USE` -> `MAINTENANCE` -> `OUT_OF_SERVICE` -> `SCRAPPED`.
*   State transitions are protected by domain events. Transitioning to `SCRAPPED` requires executive approval.

## 9. Equipment Assignment Workflow
*   Equipment is assigned to specific Farms, Sectors, or Operations.
*   Assignments generate `EquipmentAssignedEvent` payloads.
*   When an operation completes, the equipment automatically transitions back to `AVAILABLE`.

## 10. Operator Assignment Rules
*   An `OperatorHistory` record binds a specific HR Worker to an Equipment ID for a specific time window.
*   Crucial for accountability: If a tractor breaks down, the exact operator at the time of failure is logged.

## 11. Runtime Tracking
The lifeblood of the maintenance engine.
*   Runtime is updated via mobile field logs or future IoT integrations.
*   Updates trigger an internal evaluation against the Preventive Maintenance Engine.

## 12. Hour Meter Rules
*   Applies primarily to tractors and heavy machinery.
*   Calculated monotonically. A log of 500 hours followed by 490 hours is rejected at the API boundary.

## 13. Mileage Tracking
*   Applies to transport vehicles.
*   Operates identically to hour meters but utilizes a distinct measurement unit to prevent UI/UX confusion.

## 14. Fuel Consumption Tracking
*   Operators log fuel added to the machine (e.g., "Added 50L of Diesel").
*   Generates a `FuelConsumedEvent`.

## 15. Fuel Efficiency Analytics
*   The read model correlates `FuelLogs` with `RuntimeLogs` to calculate Liters/Hour or Liters/Km.
*   Anomalous drops in efficiency trigger mechanical inspection warnings.

## 16. Preventive Maintenance Engine
Evaluates every `RuntimeLog` and `TimeElapsed` tick against predefined schedules.
*   Supports multiple triggers: Time-based (Every 6 months), Runtime-based (Every 250 Hours), Mileage-based (Every 10,000 Km).

## 17. Maintenance Scheduling
When a threshold is breached (e.g., Tractor hits 245 hours of a 250-hour interval), the system generates a `PLANNED` Maintenance Work Order and flags the equipment as `SERVICE_DUE`.

## 18. Maintenance Work Orders
*   **Phases:** `DRAFT` -> `SCHEDULED` -> `IN_PROGRESS` -> `COMPLETED`.
*   Contains required tasks, expected duration, and required spare parts.

## 19. Breakdown Workflow
*   A field worker logs a Breakdown via the mobile app.
*   State instantly shifts to `OUT_OF_SERVICE`.
*   Automatically generates an `EMERGENCY` Work Order, overriding standard scheduling queues.

## 20. Inspection Workflow
*   Routine checklists (e.g., "Daily Pre-Start Check").
*   Failures on critical inspection items automatically trigger Breakdowns.

## 21. Spare Parts Integration
*   Work Orders require physical parts (e.g., Oil Filters, Belts).
*   Parts are consumed, emitting events.

## 22. Inventory Relationships
*   **Fuel Integration:** When a `FuelConsumedEvent` fires, the Inventory domain asynchronously deducts fuel from the parent storage tank.
*   **Parts Integration:** Completing a Work Order emits `PartsConsumedEvent`, triggering the Inventory Domain to deduct spare parts from the workshop.
*   **Eventual Consistency Safety:** A mechanic can finish a repair even if the system shows 0 oil filters in stock.

## 23. Operations Relationships
*   Operations bind `Equipment` to execute tasks.
*   If a tractor suffers a Breakdown mid-operation, an event alerts the Operations Domain to halt or reassign the planned task.

## 24. Reporting Relationships
Breakdowns, accidents, and major repairs utilize the Reporting Domain to attach verified photographic evidence and supervisor voice notes to the Work Order.

## 25. Offline Equipment Logging
*   Remote farm workers can log runtimes, inspections, and breakdowns entirely offline.
*   Background sync respects Last-Write-Wins (LWW) for simple metadata, but additive merges for runtime logs.

## 26. GPS & Telematics Future Architecture
*   Architecture must prepare for high-volume streaming data.
*   Telemetry endpoints will bypass standard REST APIs, flowing through MQTT or Kafka streams to update Read Models without overloading the transactional Postgres database.

## 27. Read Models
*   Dashboards showing "Current Equipment Status" query denormalized ElasticSearch/Postgres Views.
*   Read models are updated by `EquipmentStateChanged` events.

## 28. CQRS Relationships
*   **Commands:** `LogRuntime`, `ReportBreakdown`, `CompleteWorkOrder`.
*   **Queries:** `GetAvailableTractors`, `GetMaintenanceSchedule`.

## 29. Analytics Relationships
Data lakes ingest maintenance histories to build predictive failure models (e.g., predicting water pump failure based on vibration data and runtime).

## 30. Permissions
*   `can_log_runtime`: Standard operators.
*   `can_create_work_order`: Mechanics.
*   `can_commission_equipment`: Fleet Managers.

## 31. Mobile UX Considerations
*   Inspection checklists must use rapid Yes/No toggles.
*   Reporting a breakdown must be an "Emergency Button" style interaction requiring minimal taps in the field.

## 32. RTL Considerations
*   Hour meter inputs and maintenance timelines must correctly orient right-to-left for Arabic/Hebrew locales, utilizing CSS logical properties.

## 33. Performance Constraints
*   Runtime logging APIs must respond in under 50ms to support rapid field entry.
*   Maintenance interval calculations evaluate asynchronously to prevent blocking the HTTP response when an hour meter is updated.

## 34. AI Safety Rules
> [!CAUTION]
> **MANDATORY AI IMPLEMENTATION RULES**
*   **No Negative Runtime:** AI agents MUST NOT write ORM logic that allows hour meters or mileage to decrease.
*   **No Synchronous Inventory:** AI MUST NOT instantiate Inventory models or deduct spare parts synchronously within a Work Order save method.
*   **Respect State Machines:** AI MUST NOT allow assigning a Work Order to an equipment item that is in a `SCRAPPED` state.

## 35. Anti-Patterns
*   **The Phantom Repair:** Updating the next service due date without actually creating a `Completed` Work Order.
*   **Silent Rollbacks:** Changing an operator assignment history retroactively without an explicit audit record.
*   **Hardcoded Intervals:** Hardcoding "250 hours" into code instead of reading from the dynamic Preventive Maintenance Engine.

## 36. Real-World Scenarios
**Scenario:** A tractor breaks an axle offline in Sector 5.
*   **Action:** The operator logs an offline breakdown, taking a photo.
*   **Sync:** Device hits connectivity. The system receives the payload.
*   **Result:** Tractor shifts to `OUT_OF_SERVICE`. An `Emergency` Work Order is created. The active Spraying Operation is flagged as `BLOCKED`. A notification fires to the lead mechanic. All actions trace back to the operator's exact offline timestamp.
