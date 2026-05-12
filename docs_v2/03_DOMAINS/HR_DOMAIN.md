# ATLS Platform: HR Domain Architecture

> **Confidential & Proprietary**  
> **Target Audience:** Principal Architects, Engineering Leads, AI Implementation Agents  
> **Domain:** Agricultural ERP & Operations Platform  

---

## 1. Domain Purpose
The HR Domain is not a conventional corporate employee directory. It is a rugged, field-centric workforce management and labor operations system tailored for agricultural environments. It governs the identity, attendance, productivity, assignments, and operational compliance of everyone on the farm—from specialized engineers and supervisors to rotating daily workers and external contractor groups.

## 2. Business Goals
*   **Operational Labor Tracking:** Accurately measure who did what, where, and for how long, mapping labor costs directly to operations and harvest yields.
*   **Workforce Flexibility:** Seamlessly handle extreme workforce elasticity, managing seasonal surges, daily contractors, and permanent staff without administrative bottlenecks.
*   **Field Compliance:** Ensure only licensed and authorized operators handle heavy equipment or specialized agricultural chemicals.
*   **Fair Compensation Foundation:** Establish an immutable audit trail of attendance, overtime, piece-rate productivity, and penalties to feed future payroll and labor costing systems.

## 3. Ubiquitous Language
*   **Worker:** The fundamental entity representing a human being performing work on the farm (distinct from a System User).
*   **Contractor Group:** A third-party entity providing labor. Workers belong to these groups.
*   **Crew:** A dynamic, often temporary grouping of workers executing a specific operation together.
*   **Attendance Record:** A timestamped log indicating a worker's presence, optionally linked to a specific geographic location or biometric scan.
*   **Piece-Rate:** Compensation or productivity measured by output (e.g., bins of fruit harvested) rather than time.

## 4. Core Concepts
The core principle is **Operational Reality over Administrative Fiction**. The system must reflect exactly what happens in the field—including offline work, sudden crew reassignments, and workers showing up without pre-registration—capturing data cleanly for later administrative processing.

## 5. HR Aggregate Design
The `WorkerAggregate` is the primary bounded entity.
*   **Owned Entities:** `AttendanceLog`, `AssignmentHistory`, `ProductivityMetric`, `DisciplinaryRecord`, `WorkerNote`.
*   **Invariants:**
    *   Must belong to a valid `tenant_id`.
    *   Worker identification (e.g., National ID, internal badge) must be unique within a tenant.
    *   Attendance records cannot overlap in conflicting physical locations.

## 6. Worker Identity Rules
Worker identity is paramount and immutable. A worker might be hired, fired, and rehired across multiple seasons, or shift from contractor to permanent status. Their underlying `worker_id` remains constant, ensuring continuous historical tracking of their skills, productivity, and incidents across their entire lifetime with the tenant.

## 7. User vs Worker Separation
*   **CRITICAL RULE:** A `Worker` is an operational asset. A `User` is a system authentication identity.
*   A Worker (e.g., a daily picker) almost never has a User account.
*   A User (e.g., an Agronomist) may have a linked Worker profile to track their field operations.
*   **Never mix auth logic with HR logic.**

## 8. Worker Classification
Workers are classified to dictate their lifecycle and rules:
*   **Permanent Workers:** Standard salary/wage employees.
*   **Seasonal Workers:** Hired for specific campaigns (e.g., Harvest 2026).
*   **Daily Workers:** Transient labor paid by the day or piece.
*   **Engineers & Technicians:** Specialized staff requiring skill and licensing tracking.
*   **Supervisors:** Workers authorized to log data on behalf of other workers.

## 9. Contractor Management
*   Workers can be affiliated with external Contractor Groups.
*   The system tracks labor hours and productivity against the Contractor Group for invoice reconciliation, not individual payroll.
*   Contractor workers can be mixed into internal operations seamlessly.

## 10. Crew System
*   Crews are dynamic. A "Harvest Crew A" might exist for a season, but its members change daily.
*   Supervisors assign operations to a Crew. The system expands this to individual Worker assignments based on that day's Crew attendance.
*   Supports gang-based productivity tracking (e.g., the crew harvested 50 tons, split evenly among 10 members).

## 11. Shift Management
*   Defines expected working hours, standard break times, and grace periods.
*   Used to calculate tardiness, absences, and automatic overtime thresholds.
*   Supports rotating shifts and night operations.

## 12. Attendance Workflow
*   **Check-In/Out:** Executed via supervisor tablets (barcode/NFC) or future biometric terminals.
*   **Offline Capability:** Supervisors can check in an entire crew offline in a remote field. Timestamps are securely cached.
*   **Reconciliation:** Anomalies (missed check-outs) are flagged for supervisor review at the end of the shift.

## 13. Assignment Workflow
*   Workers are assigned to Operations (e.g., Pruning Sector 4).
*   Assignments lock in the cost center (Farm/Sector/Enclosure) for that worker's labor hours.

## 14. Cross-Farm Assignments
*   Workers can be permanently stationed at one farm but temporarily assigned to another within the same tenant.
*   Labor costing logic dynamically routes the financial burden to the target farm for the duration of the assignment.

## 15. Productivity Tracking
Supports multi-dimensional productivity metrics:
*   **Enclosure-based:** E.g., Pruned 5 rows in Enclosure B.
*   **Operation-based:** E.g., Completed 500 liters of spraying.
*   **Crew-based:** E.g., Crew loaded 3 trucks.
*   **Seasonal:** Aggregated yields across a campaign.
Productivity events emit payloads consumed by the Analytics Domain.

## 16. Overtime Rules
*   Calculated dynamically based on Shift definitions and local labor laws (configured per tenant).
*   Overtime hours are categorized (e.g., 1.5x, 2.0x for holidays) and locked once approved by a supervisor.

## 17. Penalty & Bonus Rules
*   Supervisors can log penalties (e.g., safety violation, damaged equipment) or bonuses (e.g., exceptional quality).
*   **Auditability:** Every penalty requires a reason code, a supervisor signature (digital), and generates an immutable audit log to prevent abuse or wage theft disputes.

## 18. Worker Notes & Incidents
*   A chronological journal attached to the worker's profile.
*   Captures informal warnings, medical incidents, or performance commendations.
*   Access is strictly role-based.

## 19. Operator Licensing Rules
*   Tracks licenses for heavy machinery, CDL (drivers), or chemical handling certifications.
*   Includes expiry dates and mandatory renewal alerts.

## 20. Equipment Operator Relationships
*   The Equipment Domain queries the HR Domain to validate if a worker is authorized to operate a specific machine.
*   If a license is expired, the system blocks the operator assignment for that tractor.

## 21. Operations Relationships
*   The Operations Domain consumes HR Workers to execute tasks.
*   Labor hours are attached to the `OperationLog`, feeding the operational cost calculations.

## 22. Reporting Relationships
*   HR incidents (accidents, severe violations) utilize the Reporting Domain to attach photographic evidence and formal supervisor incident reports.

## 23. Harvest Relationships
*   Harvest yield is directly tied to Worker Productivity.
*   The Harvest Domain records the weight/bins; the HR Domain tracks *who* picked them and calculates the piece-rate compensation.

## 24. Payroll Future Architecture
*   This domain **does not calculate taxes or cut checks.**
*   It generates a finalized, immutable "Labor Period Export" containing verified regular hours, overtime, piece-rate earnings, bonuses, and penalties, designed to be ingested by external accounting/payroll systems.

## 25. Offline Workforce Logging
*   All supervisor actions (attendance, assigning crews, logging piece-rate bins) must function without network connectivity.
*   Sync logic handles conflict resolution by prioritizing the supervisor's physical device timestamp.

## 26. Mobile Attendance Architecture
*   Designed for high-throughput (checking in 50 workers arriving on a bus in 2 minutes).
*   UI utilizes rapid scanning (QR/NFC) or quick-tap crew selection.

## 27. GPS Attendance Future Rules
*   Future iterations will append GPS coordinates to check-in/out events to ensure workers are physically at the assigned sector, combatting "buddy punching."

## 28. Read Models
*   "Current Roll Call" dashboards query fast read models reflecting real-time attendance and location state.
*   Read models are updated via `WorkerCheckedIn` and `WorkerAssigned` events.

## 29. CQRS Relationships
*   **Commands:** `ClockInWorker`, `AssignCrewToOperation`, `LogProductivity`, `IssuePenalty`.
*   **Queries:** `GetActiveCrewRoster`, `GetWorkerLicenseStatus`, `GetDailyOvertimeReport`.

## 30. Analytics Relationships
*   Labor data flows into data lakes to analyze cost-per-hectare, contractor efficiency comparisons, and seasonal labor forecasting.

## 31. Permissions
*   `can_manage_attendance`: Field Supervisors.
*   `can_approve_overtime`: Operations Managers.
*   `can_edit_worker_profile`: HR Administrators.

## 32. Mobile UX Considerations
*   Interfaces must assume harsh sunlight, dirty screens, and thick fingers.
*   High-contrast buttons, large touch targets, and minimal typing required in the field.

## 33. RTL Considerations
*   Worker names, incident notes, and scheduling timelines must natively support right-to-left languages (Arabic/Hebrew) using CSS logical properties.

## 34. Performance Constraints
*   Attendance API endpoints must ingest batch check-ins rapidly without synchronous blocking.
*   Reporting a piece-rate scan must respond in under 100ms to allow continuous rapid scanning.

## 35. AI Safety Rules
> [!CAUTION]
> **MANDATORY AI IMPLEMENTATION RULES**
> *   **No Auth Coupling:** AI MUST NOT link `Worker` creation directly to Django `User` creation unless explicitly instructed for specific admin roles.
> *   **Immutable Audit Logs:** AI MUST NOT create functions that hard-delete attendance or penalty records. Edits must be additive (canceling the old, writing a new one with a reason).
> *   **License Validation:** AI MUST NEVER bypass license checks when generating equipment assignment logic.

## 36. Anti-Patterns
*   **The "Everyone is a User" Mistake:** Forcing 500 daily pickers to have email addresses and passwords.
*   **Synchronous Costing:** Attempting to recalculate the entire farm's financial labor cost synchronously the moment someone clocks out.
*   **Losing Offline Data:** Rejecting a check-in payload because the timestamp is 8 hours old (due to the device being offline in the field).

## 37. Real-World Scenarios
**Scenario:** A contractor crew arrives at Sector 4 for Apple Harvest, but the network is down.
*   **Action:** The supervisor uses their tablet offline to scan 20 worker badges, checking them in. During the day, they scan bins of apples against specific workers.
*   **Sync:** The supervisor drives back to the main office. The tablet connects to Wi-Fi.
*   **Result:** The system receives the batch. It processes attendance retroactively, logs the piece-rate productivity against the Harvest operation, calculates the contractor group's yield contribution, and readies the data for the daily labor cost report.
