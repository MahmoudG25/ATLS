# Phase 02: Operational Excellence & Domain Integration

| Metadata | Details |
| :--- | :--- |
| **Document ID** | ATLS-EXE-P02 |
| **Status** | AUTHORITATIVE |
| **Version** | 2.0.0 |
| **Owner** | Domain Engineering & Operations Team |
| **Applicability** | Core Business Domain Implementation |

## 1. Phase Vision
Phase 02 transforms the technical foundation of Phase 01 into a living **Operational ERP**. The focus is on implementing the core agricultural domains (Farm, Harvest, Inventory) while ensuring they remain decoupled via an event-driven architecture.

## 2. Strategic Goals
- **Domain Purity**: Implementation of isolated bounded contexts.
- **Operational Data Integrity**: Mandatory audit and season-binding for all records.
- **Event-Driven Flow**: Decoupling domains via asynchronous messaging.
- **Offline Reliability**: Expansion of offline capabilities to complex operational forms.

## 3. Scope Definition
Implementation of the following domains and their respective service layers: Farm, Operations, Reporting, Harvest, and Inventory. This includes the dynamic hierarchy engine and cross-domain event orchestration.

## 4. Dynamic Hierarchy Engine
- Implementation of the flexible `Enclosure` and `Block` hierarchy.
- Support for parent-child relationship depth validation.
- Integration with GeoJSON for spatial boundaries.

## 5. Farm Domain Implementation
- Creation of `Farm`, `Block`, and `Enclosure` models and services.
- `SeasonSystem` integration: All farm operations must be bound to a temporal season.

## 6. Operations Domain Implementation
- `OperationalJournal` for daily task logging.
- Status workflow (Draft -> Pending -> Approved -> Archived).
- Labor and equipment allocation tracking within journals.

## 7. Reporting Domain Implementation
- Operational report generator engine.
- Multi-format export service (Excel/PDF) for regulatory compliance.
- Search read-model for historical report retrieval.

## 8. Harvest Domain Implementation
- `HarvestLoad` tracking (Weight, Quality, Batch).
- Destination tracking (Warehouse, Customer, Processing).
- Real-time yield-per-hectare calculations.

## 9. Inventory Domain Implementation
- `InventoryBatch` management.
- Movement logs (Purchase, Usage, Adjustment, Waste).
- Integration with Operations (e.g., auto-deducting chemicals used in a task).

## 10. Event System Integration
- Implementation of the `Transactional Outbox` pattern.
- Publication of domain events (e.g., `harvest.load.completed`).
- Event consumers for cross-domain side effects (e.g., Inventory deduction).

## 11. CQRS Projection Setup
- Definition of materialized views/read-models for performance.
- Async projection tasks triggered by domain events.

## 12. Offline Sync Expansion
- Implementation of "Smart Sync" for complex forms.
- Delta-based synchronization to reduce data usage.
- Conflict resolution workspace for supervisors.

## 13. Media Pipeline Integration
- Automated thumbnail generation for harvest evidence.
- GPS and Timestamp extraction from operational photos.
- Signed-URL delivery for secure evidence viewing.

## 14. Notification Integration
- Operational alerts (e.g., "New Harvest Load Pending Approval").
- Critical escalation for safety violations.

## 15. Audit Integration
- Mandatory "Before/After" state snapshots for all state changes.
- Correlation IDs linking UI actions to multiple domain events.

## 16. Mobile UX Integration
- "One-Tap" capture for field workers.
- High-contrast, RTL-native data entry screens.
- Optimistic UI updates for immediate user feedback.

## 17. Dashboard Integration
- Operational overview for farm managers.
- Real-time "Active Operations" feed.

## 18. Validation Pipelines
- Zod-based frontend validation mirrored by DRF/Service-layer backend validation.
- Cross-entity validation (e.g., ensuring a worker is not in two fields simultaneously).

## 19. Security Validation
- Re-verification of tenant isolation in complex cross-domain queries.
- RBAC enforcement for domain actions (e.g., only Supervisors can approve harvests).

## 20. Performance Validation
- N+1 audit for new domain endpoints.
- Database index optimization for reporting queries.

## 21. Deliverables
- Fully functional Farm/Harvest/Inventory modules.
- Event-driven inventory deduction engine.
- Offline-ready operational journal.
- Automated audit trails for all operations.

## 22. Risks
- **Circular Dependencies**: High risk; mitigated by strict EDA enforcement.
- **Sync Conflict Bloat**: Mitigated by simplified "Last-Win" rules for non-critical fields.
- **Reporting Latency**: Mitigated by CQRS read-models.

## 23. Acceptance Criteria
- [ ] Harvest records are immutable once approved.
- [ ] Inventory counts accurately reflect operational usage.
- [ ] Audit logs exist for every state change.
- [ ] Tenant A cannot see Tenant B's harvest yields.
- [ ] Offline reports sync successfully upon reconnection.

## 24. Done Definition
- All domain modules merged and tested.
- Integration tests cover cross-domain event flows.
- Documentation updated with new domain boundaries.
- Staging environment updated with Phase 02 features.

## 25. Agricultural Constraints
- **Traceability**: Every harvest load must be traceable to a specific block and season.
- **Evidence**: Critical reports must require at least one verified photo/media attachment.

## 26. Final Phase Checklist
- [ ] Dynamic hierarchy engine operational.
- [ ] Farm/Harvest/Inventory services active.
- [ ] Transactional Outbox pattern implemented.
- [ ] Audit trails capturing state diffs.
- [ ] Offline sync handling complex forms.
- [ ] Tenant isolation verified for all new modules.
- [ ] Media processing pipeline integrated.
- [ ] All cross-domain events firing correctly.
