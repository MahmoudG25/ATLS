# ATLS Platform: Reporting Domain Architecture

> **Confidential & Proprietary**  
> **Target Audience:** Principal Architects, Engineering Leads, AI Implementation Agents  
> **Domain:** Agricultural ERP & Operations Platform  

---

## 1. Domain Purpose
The Reporting Domain is the absolute operational evidence layer of the ATLS platform. If the Operations Domain defines agricultural **INTENT** (e.g., "We plan to spray Sector A"), the Reporting Domain defines the **ACTUAL FIELD EXECUTION** (e.g., "Supervisor X sprayed Sector A at 14:00, using 50L of pesticide, with GPS evidence and photo attachments"). It bridges the gap between planned ERP data and physical reality.

## 2. Business Goals
*   **Operational Evidence:** Provide undisputable photographic and metadata-backed proof of agricultural execution.
*   **Traceability & Auditability:** Ensure every field action can be traced back to a specific user, device, time, and location.
*   **Correction & Verification:** Facilitate structured workflows for supervisors to catch errors in field data before it permanently impacts inventory or payroll.
*   **Offline Robustness:** Guarantee that workers in deep rural fields can capture high-fidelity reports without cellular connectivity.

## 3. Ubiquitous Language
*   **Report:** A discrete submission of field evidence.
*   **Attachment:** An image, video, document, or voice note strictly bound to a Report.
*   **Verification:** The act of a supervisor approving a submitted Report.
*   **Correction Request:** A workflow rejecting a Report and pushing it back to the original author for amendment.
*   **Evidence:** The immutable culmination of metadata, media, and logging that proves an event occurred.

## 4. Core Concepts
Reports exist to capture reality. They can be tightly coupled to an existing `Operation` or exist standalone (e.g., an ad-hoc report of a broken fence). Reports flow through a strict state machine from creation, to submission, verification, and final immutability.

## 5. Report Aggregate Design
The `ReportAggregate` is the core bounded context entity.
*   **Owned Entities:** `MediaAttachment`, `WorkerLog`, `EquipmentLog`, `GeolocationSnapshot`, `WeatherSnapshot`.
*   **Invariants:**
    *   Must belong to a valid `tenant_id`.
    *   Cannot be modified once in the `APPROVED` state.
    *   Must be linked to a spatial boundary (Enclosure/Sector/Stage) or an Operation.

## 6. Daily Reports
A roll-up mechanism for supervisors to document end-of-day activities. Daily reports act as a container tying together multiple operational updates and ad-hoc field observations occurring within a single shift.

## 7. Enclosure Reports
Reports explicitly bound to a single `EnclosureAggregate` (e.g., Plot or Block). Captures hyper-localized evidence like pest sightings or specific irrigation leaks.

## 8. Stage Reports
Bound to broader phenological or operational stages of a crop lifecycle (e.g., "Pre-Harvest Stage Report") covering multiple physical enclosures simultaneously.

## 9. Sector Reports
Aggregated evidence covering a parent hierarchical node. Often used by regional managers to document general conditions across a massive geographical area.

## 10. Operation-Linked Reports
The most common report type. Explicitly bound to an `OperationAggregate` UUID. Completing or updating the Report inherently drives the completion metrics of the parent Operation via Domain Events.

## 11. Standalone Reports
Ad-hoc reports generated without a planned operation. Examples include safety incidents, broken equipment, or sudden weather damage (e.g., frost).

## 12. Media Attachments
Reports MUST support:
*   **Images:** High-res photos of crop conditions.
*   **Videos:** Short clips of machinery issues or application techniques.
*   **Documents:** Scanned delivery notes or chemical manifests.
*   **Voice Notes:** Audio transcriptions for rapid field documentation.

## 13. Image/Video/File Ownership
> [!IMPORTANT]
> **Strict Media Ownership Rule:**
> Media MUST belong to their exact operational context. Never create a global unstructured media dump. Every `MediaAttachment` is a child entity of the `ReportAggregate` and shares its lifecycle.

## 14. Cloud Media Strategy
*   **Storage:** Media is uploaded directly to cloud object storage (S3/Azure Blob) via mobile pre-signed URLs to bypass API bottlenecks.
*   **Pointers:** The `ReportAggregate` stores the exact object keys, not the binary data.
*   **Access:** Rendered via time-expiring, tenant-scoped URLs to prevent unauthorized data scraping.

## 15. Offline Reporting Architecture
*   Reports are generated entirely client-side on the mobile device.
*   Media and JSON payloads are stored in local SQLite/Realm databases.
*   Background sync workers push binary media first, acquire cloud URLs, and finally sync the JSON Report payload.

## 16. Sync Conflict Resolution
*   **Draft Resolution:** Local drafts overwrite server drafts (Last-Write-Wins based on client timestamp).
*   **Immutable Conflict:** If a mobile device attempts to sync edits to a Report that was already `APPROVED` by a supervisor, the sync is rejected, and an exception is logged.

## 17. Geolocation Rules
*   GPS metadata (Lat/Long/Accuracy) is captured at the exact moment of report creation.
*   **Optionality:** Geolocation must exist but remain optional. If a user denies GPS permissions, the report saves with a `null` location, flagged accordingly in the audit trail.

## 18. Device Metadata
Every report inherently logs:
*   Device OS (iOS/Android) and version.
*   App Version (crucial for debugging sync issues).
*   Battery level and connection type (Cellular/WiFi) at the time of creation.

## 19. Weather Snapshot Rules
If GPS data is present, backend services asynchronously fetch the nearest meteorological data for that exact timestamp and save a `WeatherSnapshot` against the report. This prevents future disputes over field conditions.

## 20. Worker Logging
Reports capture the *actual* execution of labor. Supervisors use Reports to scan worker NFC tags/QR codes, appending them to the `ReportAggregate` with exact timestamps.

## 21. Equipment Logging
Captures physical equipment usage evidence (e.g., a photo of the tractor's odometer/hour-meter) to validate maintenance tracking.

## 22. Inventory References
Reports document the physical barcode scans or batch numbers of chemicals applied. This is the evidence backing the `InventoryConsumption` rules in the Operations Domain.

## 23. Completion Evidence
When a report claims an Operation is 100% complete, the attached media and worker logs serve as the definitive, auditable proof of that completion.

## 24. Verification Workflow
*   Reports move from `DRAFT` to `SUBMITTED`.
*   A user with `can_verify_reports` permission reviews the media and metrics.
*   Upon approval, the Report becomes `APPROVED`.
*   Domain events (e.g., `ReportApprovedEvent`) trigger actual inventory/cost deductions in other domains.

## 25. Correction Workflow
*   If evidence is flawed (e.g., wrong chemical batch entered), the verifier transitions the report to `CORRECTION_REQUESTED`.
*   The original author receives a mobile push notification.
*   The author amends the `DRAFT` and resubmits.

## 26. Immutable Audit Trails
> [!CAUTION]
> **Historical Truth:**
> Reports MUST preserve historical truth forever. Never mutate historical operational evidence silently. If a report is `APPROVED` and an error is found 3 months later, an explicit *Compensation Report* must be filed. Hard deletions are forbidden.

## 27. Read Models
Reporting dashboards are powered by heavily optimized, denormalized ElasticSearch indexes or CQRS projection tables to allow supervisors to instantly search thousands of attachments by crop, date, or user.

## 28. CQRS Relationships
*   **Commands:** `SubmitReport`, `AttachMedia`, `ApproveReport`. (Domain layer).
*   **Queries:** `ListPendingVerifications`, `GetEnclosureHistory`. (Read Model layer).

## 29. Analytics Relationships
Analytics aggregates rely on the factual evidence generated by Reports. Data lakes consume `ReportApprovedEvent` payloads to build predictive models on operational efficiency.

## 30. Permissions
*   `can_create_report`: Base field worker level.
*   `can_verify_report`: Supervisor level, scoped to specific Hierarchy boundaries (e.g., Supervisor A cannot verify reports for Sector B).

## 31. Mobile UX Considerations
*   Camera functionality must be native, fast, and aggressively compressed to save bandwidth.
*   Voice notes must support offline transcription queues.
*   Drafts must auto-save every 5 seconds to prevent data loss in extreme heat or device crashes.

## 32. RTL Considerations
*   Image galleries, timeline histories, and media carousels must automatically flow right-to-left.
*   Timestamp alignments and metadata layouts must use logical CSS (`text-align: start`).

## 33. Performance Constraints
*   **Media Payloads:** Video attachments must enforce hard duration limits (e.g., 60 seconds) or resolution caps (720p) to prevent offline sync queue blockages over 3G edge networks.
*   **Batching:** JSON syncs must batch, but binary uploads must stream individually.

## 34. AI Safety Rules
> [!CAUTION]
> **MANDATORY AI IMPLEMENTATION RULES**
*   **No Global Media:** AI agents MUST NOT create a generic `Media` table. All media MUST have a mandatory `report_id` foreign key.
*   **No Silent Mutations:** AI MUST NOT write scripts or ORM queries that bypass the Correction Workflow to update a report's evidence.
*   **Preserve Offline Isolation:** AI MUST NOT introduce synchronous API calls to external services (like weather APIs) into the mobile report submission endpoint.

## 35. Anti-Patterns
*   **The Unverifiable Operation:** Allowing an operation to be marked `COMPLETED` without an attached, verified `ReportAggregate`.
*   **Media Dumping:** Storing raw binary files in the Postgres database instead of S3/Azure.
*   **Sync Blocking:** Failing the entire mobile sync batch because one photo out of 50 failed to upload.

## 36. Real-World Scenarios
**Scenario:** A worker submits a report claiming a 10-hectare block was completely pruned. The attached photo shows unpruned trees.
*   **Action:** The supervisor hits "Request Correction" and adds a voice note explaining the rejection.
*   **Sync:** The worker's mobile device receives the `CORRECTION_REQUESTED` state.
*   **Result:** The worker returns to the block, finishes the pruning, takes a new photo, and resubmits. Historical truth is preserved, and payroll is not issued for incomplete work.
