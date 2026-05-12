# ATLS Platform: Harvest & Production Domain Architecture

> **Confidential & Proprietary**  
> **Target Audience:** Principal Architects, Engineering Leads, AI Implementation Agents  
> **Domain:** Agricultural ERP & Operations Platform  

---

## 1. Domain Purpose
The Harvest Domain is fundamentally distinct from the Operations Domain. While Operations manage field work, the Harvest Domain is a **production, yield, transformation, and post-harvest processing domain**. It manages the flow of physical biomass from the moment it leaves the tree to the moment it enters the finished-goods warehouse, ensuring absolute traceability and mass balance closure.

## 2. Business Goals
*   **Yield Accuracy:** Establish the irrefutable truth of farm production output.
*   **Traceability:** Ensure every packaged box can be traced back to a specific enclosure, date, and season.
*   **Mass Balance:** Prevent shrinkage, theft, or unaccounted loss during complex multi-stage processing.
*   **Quality Grading:** Maximize farm revenue by accurately sorting, grading, and routing premium vs. secondary products.

## 3. Ubiquitous Language
*   **Harvest Batch:** The raw collected yield from a specific origin (e.g., "10 Tons from Sector A on Monday").
*   **Lot:** A distinct, transformed portion of a Batch resulting from processing (e.g., "Premium Grade Lot").
*   **Mass Balance:** The strict accounting equation: `Input Weight = Output Weight + Waste + Natural Loss`.
*   **Yield Loss:** Natural mass reduction (e.g., moisture evaporation during drying).
*   **Waste:** Physical biomass discarded due to damage, rot, or processing artifacts.

## 4. Core Concepts
The domain operates on the concept of **Transformation with Traceability**. Raw material enters the system and flows through a directed graph of processing steps (sorting, drying, grading). Every step changes the state, weight, or categorization of the product, but the aggregate lineage back to the origin remains unbroken.

## 5. Harvest Aggregate Design
The `HarvestBatchAggregate` is the root entity for raw intake.
*   **Owned Entities:** `ProcessingLot`, `QualityGradeRecord`, `WeightRecord`, `WasteLog`.
*   **Invariants:**
    *   Total weight of child Lots + Waste + Loss MUST exactly equal the Batch input weight.
    *   A Batch must map to a valid physical origin (Enclosure/Sector).
    *   Cannot transition to `INTAKE_COMPLETE` until Mass Balance is reconciled.

## 6. Harvest Seasons
Harvesting represents the financial climax of a `SeasonAggregate`. Harvest records are strictly bound to a Season. Yield generated outside an active Season violates domain invariants.

## 7. Yield Recording
*   **Supported Units:** Tons, Kilograms, Boxes, Crates, and configurable custom measurement units.
*   **Unit Conversion:** The system standardizes all internal accounting to a base unit (e.g., Kilograms) via precise conversion tables to allow accurate mass balancing.

## 8. Harvest Collection Workflow
*   **Field Logging:** Bins/crates are filled and logged offline in the field.
*   **Collection Point:** Bins are consolidated at collection points.
*   **Handover:** Transfer of custody from the field supervisor to the processing facility manager, supported by QR/Barcode handshakes (or manual digital signatures).

## 9. Batch Management
Raw materials are grouped into `HarvestBatchAggregates` based on origin criteria (Enclosure, Crop, Date). If crops from two distinct sectors are physically mixed, they form a new composed Batch, but the lineage references both parent sectors.

## 10. Lot Tracking
As a Batch is processed, it is split into `Lots`. A single Batch of 10 tons might split into Lot A (Premium, 5t) and Lot B (Secondary, 3t). Lots form a genealogical tree pointing back to the parent Batch.

## 11. Weight Measurement Rules
*   **Tare & Gross:** The system enforces standard Gross - Tare = Net calculations.
*   **Scale Integration:** Designed to eventually integrate with physical weighbridges or industrial scales.
*   **Tolerance:** Minor scale discrepancies across different facilities are handled via an explicit `ScaleToleranceLoss` categorization, preventing mass balance validation failures for fractional discrepancies.

## 12. Sorting Workflow
The first step of transformation. Raw biomass is sorted by physical characteristics (size, color). Sorting creates initial sub-lots and immediately generates the first layer of `WasteLogs` (e.g., dropping rotten fruit).

## 13. Grading Workflow
*   **Dynamic Grading Systems:** Grades are not hardcoded. Tenants configure their own matrices (e.g., Class 1, Class 2, Export Grade, Local Grade).
*   **Quality Application:** Grading acts as metadata applied to a specific `Lot`, determining its final routing and financial value.

## 14. Drying Workflow
*   **Moisture Loss Tracking:** As product dries, it loses weight. This weight loss is not Waste; it is `NaturalYieldLoss`. 
*   **Mass Balance Impact:** The drying step explicitly records input weight and output weight, calculating the delta to satisfy the mass balance equation.

## 15. Rutab Workflow
Specific post-harvest processing for Rutab (half-ripe dates). Involves rapid cold-chain transitions and specific moisture preservation steps. Routing to the Rutab workflow bypasses standard drying stages.

## 16. Ajwa Workflow
Specific processing for premium Ajwa dates. Mandates hyper-strict QA sampling rates, distinct cleaning processes, and premium packaging routing.

## 17. Waste & Damaged Product Workflow
*   **Quantification:** All waste MUST be weighed and categorized (e.g., Pest Damage, Mechanical Damage, Overripe).
*   **Reporting Link:** Extreme waste events optionally trigger the `Reporting Domain` to capture photographic evidence for crop insurance or management review.

## 18. Mass Balance Rules
> [!IMPORTANT]
> **The Golden Equation:** `Total Batch Intake = (Sum of Final Lots) + Recorded Waste + Yield Loss`.
*   If this equation does not perfectly balance, the Batch CANNOT be locked or transferred to the Inventory Domain.

## 19. Yield Loss Rules
Differentiates biological/chemical loss (moisture evaporation) from physical loss (dropping product on the floor). Yield loss is an expected processing artifact and has tenant-configured acceptable percentage thresholds.

## 20. Production Conversion Rules
Maps the transformation of bulk raw material into packaged goods (e.g., 1000kg of graded dates -> 2000 x 500g retail boxes). This is the final step before warehouse intake.

## 21. Warehouse Intake Integration
Once a Batch completes processing and mass balance is closed, it hits the warehouse boundary.
*   **Eventual Consistency:** The Harvest Domain emits `FinishedGoodsReadyEvent`.
*   **Boundary Handoff:** The Inventory Domain listens to this event to increase warehouse stock. Harvest NEVER directly updates the Inventory SQL tables.

## 22. Inventory Relationships
The Harvest Domain *produces* inventory. It depends on the Inventory Domain only for retrieving packaging materials (e.g., consuming empty boxes) during the processing phase.

## 23. Equipment Relationships
Processing equipment (sorters, dryers, packaging lines) are logged against the Batch to calculate machine runtime and associate equipment failure with potential product contamination.

## 24. Worker Relationships
Processing line labor is tracked and attached to the Batch to calculate the exact post-harvest processing cost-per-kilogram.

## 25. Reporting Relationships
Any significant defect, contamination, or major mass balance discrepancy requires a formal `ReportAggregate` (with photos and supervisor notes) to serve as verified evidence.

## 26. Quality Control Rules
*   **Sampling Rates:** The system generates prompts for QA workers to pull samples (e.g., "Pull 1 box per 100 boxes").
*   **Dynamic Checks:** QC forms use the Dynamic Form Engine to assess brix levels, moisture content, or visual defects.

## 27. Approval Workflow
*   **States:** `INTAKE` -> `PROCESSING` -> `RECONCILIATION` -> `APPROVED` -> `WAREHOUSED`.
*   Moving from `RECONCILIATION` to `APPROVED` requires a manager to sign off on the mass balance and QC results.

## 28. Offline Harvest Recording
*   Remote collection points without cellular coverage can log crate weights, assign origins, and scan worker badges.
*   Data is synced to the backend queue upon reaching connectivity, triggering the instantiation of the `HarvestBatchAggregate`.

## 29. Mobile UX Considerations
*   **Speed:** Weighing and field collection interfaces must prioritize rapid data entry (e.g., big numpads, swipe-to-log).
*   **Hardware Integration:** Architecture must support future Bluetooth scale integrations and native camera barcode/QR scanning.

## 30. Read Models
Yield analytics require heavy aggregations. The domain populates denormalized Read Models mapping Total Yield by Sector, Yield by Grade, and Waste Percentages, ensuring dashboard queries return in milliseconds.

## 31. CQRS Relationships
*   **Commands:** `CreateHarvestBatch`, `SplitLot`, `RecordWaste`, `CloseMassBalance`.
*   **Queries:** `GetBatchLineage`, `GetProcessingQueue`, `GetDailyYield`.

## 32. Analytics Relationships
Analytics consumes harvest events to train predictive yield models (e.g., correlating Operations Domain spray activities with Harvest Domain defect rates).

## 33. Performance Constraints
*   **Graph Traversal:** Tracing a single retail box back through 5 layers of Lot splits to its originating field must be optimized (e.g., using Postgres Ltree or recursive CTEs) to prevent API timeouts during trace audits.

## 34. AI Safety Rules
> [!CAUTION]
> **MANDATORY AI IMPLEMENTATION RULES**
*   **Never Bypass Mass Balance:** AI agents MUST NOT write logic that allows a Batch to be marked `APPROVED` without the mass balance invariants evaluating to exactly zero variance.
*   **Never Write Synchronous Inventory Updates:** AI MUST NOT instantiate Inventory models or call Inventory repositories from within the Harvest domain.
*   **Never Mutate Lineage:** AI MUST NOT alter the parent/child references of `ProcessingLots` once they are created.

## 35. Anti-Patterns
*   **Silent Weight Mutation:** Fixing a mass balance error by silently updating the original intake weight. (Requires an explicit `WeightCorrectionLog` instead).
*   **The Black Box Processor:** Logging 10 tons in and 8 tons out without logging the 2 tons of waste or loss.
*   **Cross-Domain ORM Joins:** Creating a Django/SQLAlchemy query that joins `HarvestBatch` directly with `InventoryStock`.

## 36. Real-World Scenarios
**Scenario: The 10-Ton Intake**
*   **Action:** 10 tons of raw dates arrive from Sector A.
*   **Sorting/Grading:** The system records 1 ton of rotten waste (`WasteLog`). 9 tons remain.
*   **Processing Split:** The 9 tons are split into Lot 1 (Premium Ajwa, 4t) and Lot 2 (Standard Rutab, 5t).
*   **Drying (Lot 1):** The 4t of Ajwa goes through drying, losing 0.5t in moisture (`NaturalYieldLoss`). 3.5t remain.
*   **Packaging:** The 3.5t Ajwa becomes 7,000x 500g boxes. The 5t Rutab becomes 5,000x 1kg boxes.
*   **Reconciliation:** The manager views the Mass Balance: `Input (10t) = Packaged (3.5t + 5t) + Waste (1t) + Loss (0.5t)`. Equation balances. Batch `APPROVED`. `FinishedGoodsReadyEvent` emitted to Inventory.
