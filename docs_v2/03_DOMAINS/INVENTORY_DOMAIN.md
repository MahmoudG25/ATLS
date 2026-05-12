# ATLS Platform: Inventory Domain Architecture

> **Confidential & Proprietary**  
> **Target Audience:** Principal Architects, Engineering Leads, AI Implementation Agents  
> **Domain:** Agricultural ERP & Operations Platform  

---

## 1. Domain Purpose
The Inventory Domain is the absolute ledger of physical assets across the ATLS platform. It is a strict, ledger-based warehouse management system, managing the entire lifecycle of physical goods—from bulk fertilizers and fuel to packaged harvested goods and spare parts. It provides the irrefutable truth of what physical assets exist, where they are, and their financial value.

## 2. Business Goals
*   **Asset Traceability:** Ensure every gram of chemical or box of dates can be traced from intake to consumption or dispatch.
*   **Mass Balance & Shrinkage Control:** Prevent untracked asset loss by enforcing strict movement and adjustment ledgers.
*   **Financial Integrity:** Provide accurate costing data based on moving average cost (MAC) or FIFO valuations.
*   **Safety & Compliance:** Prevent the application of expired chemicals and enforce hazardous material storage rules.

## 3. Ubiquitous Language
*   **Ledger Record:** An immutable entry representing an addition or deduction of stock.
*   **Stock Item:** A unique physical material type (e.g., "Pesticide X").
*   **Batch:** A specific delivery of a Stock Item sharing a manufacturing date, expiry date, and cost.
*   **Reservation:** Stock that is physically present but allocated to a planned operation.
*   **Location:** A node in the physical warehouse hierarchy.

## 4. Core Concepts
Inventory is **event-sourced and ledger-based**. Stock quantities are NEVER directly updated; they are the calculated sum of all historical movements. The domain operates asynchronously with Operations and Harvest to ensure field workers are never blocked by administrative stock errors.

## 5. Inventory Aggregate Design
The `InventoryLedgerAggregate` is the root entity for stock logic.
*   **Owned Entities:** `LedgerEntry`, `StockReservation`, `BatchRecord`, `InventoryAdjustment`.
*   **Invariants:**
    *   Direct mutation of total stock quantity is physically impossible.
    *   Ledger entries are append-only.
    *   A ledger entry must map to a valid `WarehouseLocation`.

## 6. Warehouse Architecture
Warehouses are not flat lists; they are hierarchical structures representing physical reality.
*   **Physical Locations:** Primary warehouses, secondary sheds, cold storage rooms.
*   **Virtual Locations:** Mobile field storage (e.g., a specific tractor's chemical tank) or logical transit locations.

## 7. Warehouse Hierarchy
*   **Zone / Sector:** Logical groupings within a warehouse (e.g., "Chemical Storage Zone").
*   **Bin / Shelf:** Micro-locations for precise barcode mapping.
*   **Tank:** Specialized locations for bulk fluids (Fuel, Liquid Fertilizer) requiring volumetric tracking.

## 8. Stock Ledger System
> [!IMPORTANT]
> **No Direct Mutations:** An API call like `UPDATE inventory SET qty = 50` is strictly forbidden.
*   Every stock change must be an `INSERT` into the `LedgerEntry` table.
*   Current stock is calculated as `SUM(qty) WHERE location_id = X AND batch_id = Y`.

## 9. Inventory Movement Rules
*   **Types:** IN (Receipt), OUT (Dispatch/Consumption), TRANSFER (Internal move).
*   **Requirements:** Every movement must have an actor (User), a timestamp, and a reason code.

## 10. Stock Reservation Rules
*   When an Operation is scheduled, the required inventory is marked as a `StockReservation`.
*   Reserved stock reduces the *Available Quantity* without reducing the *Physical Quantity*.
*   Reservations expire or are converted into actual consumptions when the Operation completes.

## 11. Transfer Workflow
*   Moving stock between locations generates a paired Ledger transaction: an OUT entry from Location A and an IN entry to Location B.
*   Transits spanning multiple days use a virtual "In-Transit" location to maintain global mass balance.

## 12. Adjustment Workflow
*   Used to correct shrinkage, theft, or spoilage.
*   Requires a mandatory reason code, photographic evidence (via Reporting Domain), and supervisor approval for large variances.
*   Generates an explicit `AdjustmentLedgerEntry`.

## 13. Inventory Counting Workflow
*   Cycle counting tasks generate a snapshot of expected stock.
*   Workers enter actual counts offline.
*   Variances automatically generate pending `AdjustmentWorkflows` for managerial approval.

## 14. Batch Tracking
*   Essential for chemicals, fertilizers, and harvested goods.
*   A Batch tracks origin, supplier lot number, and intake cost.
*   All consumptions must deduct from a specific Batch to ensure FIFO compliance and accurate cost-of-goods-sold (COGS) calculations.

## 15. Expiry Tracking
*   **Alerts:** Async workers check batch expiry dates, emitting `ExpiryWarning` events 30 days prior.
*   **Soft Warnings:** UI flags batches nearing expiry to encourage FIFO consumption.
*   **Blocking Rules:** Once a chemical passes its exact expiry date, the API strictly blocks its inclusion in any new `StockReservation`.

## 16. Chemical Safety Rules
*   Chemical items require safety metadata (e.g., Re-Entry Intervals, Pre-Harvest Intervals).
*   The system prevents the transfer of incompatible chemicals into the same physical `Bin/Shelf` location based on HAZMAT rules.

## 17. Fuel Inventory Rules
*   Fuel is tracked volumetrically (Liters/Gallons) in `Tank` locations.
*   Requires temperature-adjusted mass balancing if operating in extreme climates, utilizing specialized tolerance logic.

## 18. Packaging Inventory Rules
*   Tracks boxes, pallets, and plastics.
*   Consumed asynchronously when the Harvest Domain emits packaging conversion events.

## 19. Harvest Intake Integration
*   The Harvest Domain is the producer of finished goods.
*   When Harvest emits `FinishedGoodsReadyEvent`, the Inventory domain listens and generates a ledger IN entry. No direct API calls exist between the two domains.

## 20. Operations Consumption Integration
*   Operations emit `InventoryConsumedEvent`.
*   **Eventual Consistency Safety:** If an Operation consumes 50L of chemical but the ledger only has 40L, the ledger executes the deduction (creating a temporary negative balance) and emits a `NegativeStockAlert`. Field operations are NEVER blocked by inventory data mismatch.

## 21. Equipment Fuel Consumption Integration
*   Equipment Domain emits `FuelConsumedEvent` when a tractor logs its hours/refueling.
*   Inventory domain deducts the volume from the designated mobile or static `Tank` location.

## 22. Reporting Relationships
Any manual adjustment or damaged stock intake requires a verified `ReportAggregate` (from the Reporting Domain) containing photo evidence before the ledger entry is finalized.

## 23. Approval Workflow
*   Routine movements are auto-approved.
*   High-value adjustments (e.g., writing off $5,000 of fertilizer) transition to `REVIEW_PENDING` and require executive override.

## 24. Offline Inventory Operations
*   Mobile warehouse scanners operate offline in deep storage rooms.
*   Ledger entries are cached locally and synced using client-side timestamps to ensure chronological integrity when applied to the master ledger.

## 25. Barcode/QR Architecture
*   Every `StockItem`, `Batch`, and `Location` generates a deterministic QR code.
*   The system must support future RFID and IoT scale integrations via generic ingestion APIs.

## 26. Read Models
*   Calculating `SUM(qty)` across millions of ledger rows per API request is unscalable.
*   CQRS projections maintain flat `CurrentStockReadModel` tables, updated asynchronously by every ledger insert.

## 27. CQRS Relationships
*   **Commands:** `ReceiveStock`, `TransferStock`, `ReserveStock`. (Processed by Domain layer).
*   **Queries:** `GetAvailableStock`, `GetBatchHistory`. (Processed by Read Models).

## 28. Analytics Relationships
Analytics consume ledger events to calculate inventory turnover ratios, carrying costs, and predictive stock-out warnings.

## 29. Permissions
*   `can_view_stock`: Basic visibility.
*   `can_transfer_stock`: Warehouse worker level.
*   `can_adjust_stock`: Managerial level; allows submitting corrections.

## 30. Mobile UX Considerations
*   Warehouse UI must be optimized for laser scanners and rapid touch targets.
*   Must support "Scan Location -> Scan Item -> Enter Quantity" continuous flows.

## 31. RTL Considerations
*   Stock tables and transfer wizards must natively flow right-to-left for Arabic/Hebrew users using logical CSS structures.

## 32. Performance Constraints
*   Ledger appends must occur in sub-100ms.
*   Extensive historical batch tracing must utilize database partitioning by year to prevent slow table scans.

## 33. AI Safety Rules
> [!CAUTION]
> **MANDATORY AI IMPLEMENTATION RULES**
*   **No State Mutation:** AI agents MUST NOT write ORM updates like `item.quantity = new_qty`.
*   **No Synchronous Blocks:** AI MUST NOT make synchronous calls to the Operations domain during an inventory transfer.
*   **Mandatory Actor Traceability:** AI MUST ensure every ledger entry includes the executing `user_id` and `tenant_id`.

## 34. Anti-Patterns
*   **The Update Bypass:** Altering a historical ledger row to "fix" a mistake. (A compensating ledger entry must be created instead).
*   **The Global Warehouse:** Putting all items into a single default warehouse, destroying location traceability.
*   **Negative Stock Rejection:** Hard-failing an API request from the Operations domain because the ledger calculates negative stock, which stops farmers from working.

## 35. Real-World Scenarios
**Scenario:** A worker logs an offline operation consuming 20L of pesticide. The system thinks only 15L exist.
*   **Action:** Mobile device syncs the `InventoryConsumedEvent`.
*   **Processing:** Ledger inserts an OUT entry for 20L. Current stock drops to -5L.
*   **Resolution:** A `NegativeStockAlert` is fired to the warehouse manager. The manager investigates, realizes a recent delivery wasn't logged, logs the 50L delivery (backdated), and the stock resolves to 45L. Traceability is unbroken.

## 36. Future Expansion Strategy
The ledger-based architecture guarantees future readiness for:
*   Automated Guided Vehicles (AGVs) integrating via API.
*   IoT weight sensors on bulk tanks triggering automatic IN/OUT ledger events.
*   Third-Party Logistics (3PL) integrations via standard supply chain EDI formats.
