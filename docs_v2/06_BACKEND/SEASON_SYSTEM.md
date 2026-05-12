# Agricultural Season Lifecycle Governance

| Metadata | Details |
| :--- | :--- |
| **Document ID** | ATLS-BACK-06 |
| **Status** | AUTHORITATIVE |
| **Version** | 2.0.0 |
| **Owner** | Operations & Backend Team |
| **Applicability** | All Season-Dependent Operations & Reporting |

## 1. Season Philosophy
The **Season** is the foundational temporal unit of the ATLS ERP. Every operational action—harvesting, labor, inventory, finance—must be anchored to a specific season. 
- **Temporal Anchor**: Data is not just "current"; it belongs to a specific agricultural cycle.
- **Immutable History**: Once a season is closed, it becomes a permanent record of the farm's performance.
- **Financial Boundary**: Profit/Loss and Yield metrics are calculated per season.

## 2. Season Lifecycle
A season follows a unidirectional lifecycle:
`Draft` -> `Active` -> `Closing` -> `Closed` -> `Archived`.

## 3. Season States
- **Draft**: Configuration phase. Plans and budgets are set. No operational data entry allowed.
- **Active**: Primary operational state. Data entry, harvesting, and labor tracking are live.
- **Closing**: Reconciliation phase. Final yields are verified, inventory is audited. New operations are restricted.
- **Closed**: Read-only state. Data is locked for auditing and reporting.
- **Archived**: Historical storage. Moved to cold storage/materialized views.

## 4. Opening Rules
- **Prerequisites**: A season can only be opened if the previous season is at least in `Closing` or `Closed` state (depending on farm overlap configuration).
- **Validation**: Opening requires a defined Start Date, targeted Crops, and an approved Operational Budget.
- **Tenant Limit**: Maximum 2 `Active` seasons per tenant simultaneously (to support overlap).

## 5. Closing Rules
- **Audit**: All `Pending` reports and `Draft` harvests must be resolved or cancelled.
- **Inventory**: Remaining stock must be either rolled over to the next season or written off.
- **Finality**: Closing is a non-reversible operation (requires admin override and audit log).

## 6. Archival Strategy
- **Materialization**: Upon closing, key performance indicators (KPIs) are calculated and stored in a `SeasonProjection` table for fast analytical access.
- **Cold Storage**: Detailed transaction logs are moved to compressed historical tables after 24 months in `Closed` state.

## 7. Operational Binding
- **Mandatory Link**: Every `OperationalJournal` entry must have a non-nullable `season_id`.
- **Validation**: Transactions can only be recorded against `Active` or `Closing` seasons.

## 8. Harvest Binding
- **Yield Tracking**: Every load of produce must be linked to the season it was planted/grown in, ensuring accurate yield-per-hectare calculations.

## 9. Inventory Binding
- **Batches**: Inventory items are tracked by `Batch`. Every batch is linked to a season.
- **Usage**: You can use inventory from Season A in Season B, but the cost is recorded against Season B.

## 10. Historical Integrity
- **No Deletion**: Season records and their linked operational data can never be deleted.
- **Audit Trail**: Any change to a `Closing` or `Closed` season's metadata is recorded with a "Critical Alert" status.

## 11. Rollovers
- **Automated**: System provides a "Season Rollover" tool to clone farm block configurations, labor rates, and asset lists from the previous season.

## 12. Reporting Boundaries
- Reports are scoped by `season_id`. 
- **FORBIDDEN**: Generating a report that blends transactional data from two different seasons into a single "Current" total without explicit season markers.

## 13. Analytics Impact
- **Comparisons**: The Season system allows for "Year-over-Year" or "Season-over-Season" analytics by comparing standardized projections.

## 14. Multi-Season Handling
- ATLS supports overlapping seasons (e.g., harvesting Season 1 while planting Season 2).
- Users must select the "Context Season" in the app header for data entry.

## 15. Audit Rules
- Mandatory full audit logs for state transitions (`Draft` -> `Active`, etc.).
- The `closed_by` and `closed_at` fields must be captured for every season.

## 16. Async Processing
- Closing a season triggers a heavy Celery task to:
    - Finalize inventory balances.
    - Generate final yield reports.
    - Snapshot seasonal metrics.

## 17. Performance Constraints
- **Selector Speed**: Querying "Current Active Season" must be < 10ms (cached).
- **Listing**: Season lists must support filtering by status and year.

## 18. AI Safety Rules
- **Deleting**: AI agents MUST NOT implement deletion logic for seasons or linked operational data.
- **Mutation**: FORBID any logic that allows non-admins to edit records linked to a `Closed` season.
- **Season-less**: FORBID creating operational records without a valid `season_id`.
- **Rewrites**: FORBID "Historical Rewrites" (altering past season data to fix current inventory errors).

## 19. Forbidden Season Anti-Patterns
- **The Never-Ending Season**: Keeping a season `Active` for > 18 months.
- **Duplicate Naming**: Using the same name for two seasons in the same tenant.
- **Hardcoded IDs**: Referring to seasons by primary keys instead of their operational `slug` or `status`.

## 20. Agricultural Scenarios
- **Table Grapes**: Season 2024 begins in Sept (Pruning) and ends in April (Post-Harvest). During March, Season 2025 starts (Early fertilization), requiring both seasons to be `Active`.
- **Crop Failure**: A season is closed early with a `Cancelled` flag, requiring a specific audit note and write-off of all remaining input costs.

## 21. Enforcement Checklist
- [ ] Season-based manager active for all operational models.
- [ ] State transition validations implemented.
- [ ] Non-nullable `season_id` enforced at the DB level.
- [ ] "Context Season" selector present in the UI.
- [ ] Closing reconciliation task defined in Celery.
- [ ] Historical data locked for `Closed` seasons.
- [ ] Reporting supports multi-season comparison.
