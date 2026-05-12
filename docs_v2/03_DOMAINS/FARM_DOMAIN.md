# FARM DOMAIN

> **Authority Document.** This file defines the canonical business logic, data rules, and behavioral contracts for the Farm Domain. All backend models, API endpoints, frontend components, and AI-generated code related to farms MUST conform to this document.

---

## Last Updated
2026-05-12

## Status
- [x] Active — Authoritative

## Dependencies
- `AI_DEVELOPMENT_RULES.md` — Engineering governance
- `04_DYNAMIC_ENGINES/DYNAMIC_HIERARCHY_ENGINE.md` — Hierarchy engine
- `04_DYNAMIC_ENGINES/ROLE_PERMISSION_ENGINE.md` — Access control
- `03_DOMAINS/OPERATIONS_DOMAIN.md` — Operation propagation
- `03_DOMAINS/HARVEST_DOMAIN.md` — Yield tracking
- `09_REFERENCE/GLOSSARY.md` — Ubiquitous language

---

## 1. Domain Purpose

The Farm Domain is the **root domain** of ATLS. Every other domain (Operations, Harvest, Inventory, HR, Equipment, Analytics) anchors its data to a Farm entity.

The Farm Domain is responsible for:
- Defining the physical and logical structure of agricultural land.
- Managing the dynamic, configurable hierarchy of farm sub-units.
- Owning the Enclosure (الحوشة) as the atomic operational unit.
- Governing season lifecycles that scope all operational activity.
- Maintaining a complete, auditable history of every enclosure's life.

This domain does NOT execute operations or harvest reports. It provides the structural foundation that those domains operate upon.

---

## 2. Business Goals

2.1. Enable farm owners and managers to model ANY real-world farm structure digitally, regardless of its physical organization depth or naming convention.

2.2. Ensure every agricultural operation, report, and harvest is traceable to a specific enclosure, including the date, season, and actor.

2.3. Support multi-tenant isolation so that Farm A's data is completely invisible to Farm B's users, even on shared infrastructure.

2.4. Provide a real-time, mobile-optimized view of farm status that field workers can use without internet connectivity.

2.5. Enable white-label operators to rename hierarchy levels, configure visible features, and brand the system per their client.

---

## 3. Core Domain Concepts

### 3.1 Farm (المزرعة)
The top-level entity. Represents a single agricultural property owned or managed by a tenant.

**Fields:**
- `name` — Display name (Arabic primary)
- `code` — Short unique identifier (e.g., `FARM-001`)
- `location` — GPS coordinates (latitude, longitude)
- `area_hectares` — Total land area
- `owner` — FK to User (FARM_OWNER role)
- `tenant` — FK to Tenant (multi-tenant isolation)
- `hierarchy_config` — FK to HierarchyConfiguration
- `active_season` — FK to Season (nullable)
- `is_active` — Soft delete flag
- `created_at`, `updated_at`, `created_by`

**Rules:**
- A Farm must always have exactly one `HierarchyConfiguration` assigned.
- A Farm may have zero or one `active_season` at any time.
- Deactivating a Farm does NOT delete its enclosures or history. All records are preserved.

---

### 3.2 HierarchyConfiguration (إعداد الهيكل)
Defines the number and labels of hierarchy levels for a specific Farm.

**Fields:**
- `farm` — OneToOne FK to Farm
- `depth` — Integer (1 to 4). Number of levels below Farm before Enclosure.
- `level_1_label` — Label for level 1 nodes (e.g., "Sector", "قطاع")
- `level_2_label` — Label for level 2 nodes (e.g., "Stage", "مرحلة")
- `level_3_label` — Label for level 3 nodes (e.g., "Row", "صف")
- Unused level labels are `null`.

**Depth Examples:**

| Depth | Structure |
|-------|-----------|
| 0 | Farm → Enclosure |
| 1 | Farm → Sector → Enclosure |
| 2 | Farm → Sector → Stage → Enclosure |
| 3 | Farm → Sector → Stage → Row → Enclosure |

**Rules:**
- Depth cannot be changed after Enclosures have been assigned to the farm without a migration plan.
- Labels are per-Farm and can be renamed at any time without data migration.
- Labels support both Arabic and English. Arabic is displayed by default.

---

### 3.3 HierarchyNode (عقدة الهيكل)
A generic, self-referencing tree node that represents any intermediate level between Farm and Enclosure.

**Fields:**
- `farm` — FK to Farm
- `parent` — FK to self (nullable — null means direct child of Farm)
- `level` — Integer (1-based depth level)
- `name` — Display name
- `code` — Short identifier
- `is_active`
- `created_at`, `updated_at`, `created_by`

**Rules:**
- A node's `level` must equal `parent.level + 1`. Root nodes have `level = 1`.
- A node cannot be parented to a node in a different Farm.
- Deactivating a node does NOT deactivate child nodes or enclosures automatically. This requires explicit bulk action with confirmation.
- A node at the maximum depth level (`farm.hierarchy_config.depth`) must only contain Enclosures as children, never other nodes.
- Nodes are ordered by `name` by default.

---

### 3.4 Enclosure (الحوشة)
The **atomic operational unit** of ATLS. The lowest-level container of agricultural activity.

**Fields:**
- `farm` — FK to Farm
- `parent_node` — FK to HierarchyNode (nullable — null if depth=0 farm)
- `name` — Display name (e.g., "A-01", "الحوشة الأولى")
- `code` — Unique within farm (e.g., `ENC-001`)
- `crop_type` — FK to CropType
- `tree_count` — Integer (for palm farms)
- `area_sqm` — Area in square meters
- `planting_date` — Date
- `is_active`
- `created_at`, `updated_at`, `created_by`

**Rules:**
- An Enclosure always belongs to exactly one Farm.
- An Enclosure belongs to one HierarchyNode IF the Farm depth > 0. If depth = 0, `parent_node` is null.
- An Enclosure's `crop_type` cannot be changed after the first harvest record is recorded. A new enclosure must be created.
- `tree_count` is relevant only for palm farms. For row crop farms, this field is `null`.
- Deactivating an Enclosure hides it from operational views but preserves all historical records.
- An Enclosure belongs to the currently active season implicitly — season scoping is done at query time, not stored per enclosure.

---

### 3.5 Season (الموسم)
Defines a time-bounded operational period for a Farm.

**Fields:**
- `farm` — FK to Farm
- `name` — e.g., "موسم 2025"
- `start_date` — Date
- `end_date` — Date (nullable while season is open)
- `status` — ENUM: `OPEN`, `CLOSED`, `ARCHIVED`
- `created_at`, `updated_at`, `created_by`

**Rules:**
- Only one Season per Farm may have status `OPEN` at any time.
- Closing a Season sets `end_date` to today and status to `CLOSED`.
- Archived seasons are read-only. No operations, reports, or harvests may be created against an archived season.
- All operational queries are implicitly scoped to the Farm's `active_season`.
- If no season is active, the Farm is in a dormant state. No new operational records may be created.

---

### 3.6 CropType (نوع المحصول)
A reference entity defining the agricultural product grown in an enclosure.

**Fields:**
- `name` — Arabic name (primary)
- `name_en` — English name
- `category` — ENUM: `PALM`, `VEGETABLE`, `FRUIT`, `GRAIN`, `OTHER`
- `is_active`

**Rules:**
- CropTypes are managed at the system (global) level, not per-tenant.
- Tenants may request custom CropTypes via support.
- Palm crops activate the `tree_count` field on enclosures.

---

## 4. Ubiquitous Language

| Arabic Term | English Term | Definition |
|---|---|---|
| المزرعة | Farm | Top-level property entity |
| الحوشة | Enclosure | Atomic operational unit |
| القطاع | Sector | Hierarchy level 1 (configurable label) |
| المرحلة | Stage | Hierarchy level 2 (configurable label) |
| الصف | Row | Hierarchy level 3 (configurable label) |
| الموسم | Season | Time-bounded operational period |
| العملية | Operation | Agricultural activity targeting an enclosure or node |
| التقرير | Report | Submitted record of completed daily work |
| الحصاد | Harvest | Yield collection event |
| نوع المحصول | Crop Type | Classification of grown agricultural product |
| هيكل التسلسل | Hierarchy | The configurable tree structure of a farm |
| عقدة الهيكل | Hierarchy Node | Any intermediate structural level |
| الإنجاز | Completion | Percentage of enclosures covered by an operation |

> All code variables, API fields, and UI labels must use these terms. When adding a new concept, add it here first.

---

## 5. Dynamic Hierarchy System

### 5.1 Core Principle
The hierarchy of a Farm is not hardcoded. It is a runtime-configurable tree defined by `HierarchyConfiguration.depth`. The system renders, validates, and queries the hierarchy dynamically based on this configuration.

### 5.2 Depth Scenarios

**Depth 0 — Direct Enclosures:**
```
Farm
└── Enclosure A
└── Enclosure B
└── Enclosure C
```
Enclosures belong directly to the Farm. `parent_node` is null.

**Depth 1 — One Level:**
```
Farm
└── Sector 1
    ├── Enclosure A
    └── Enclosure B
└── Sector 2
    └── Enclosure C
```

**Depth 2 — Two Levels:**
```
Farm
└── Sector 1
    └── Stage 1
        ├── Enclosure A
        └── Enclosure B
```

**Depth 3 — Three Levels:**
```
Farm
└── Sector 1
    └── Stage 1
        └── Row 1
            ├── Enclosure A
            └── Enclosure B
```

### 5.3 Node Addressing
Every Enclosure has a canonical path from root:
- Format: `{Farm.code} / {Node1.code} / {Node2.code} / {Enclosure.code}`
- Example: `FARM-001 / SEC-A / STG-2 / ENC-014`
- This path is computed dynamically, not stored.

### 5.4 Node Inheritance
When a property is set at a parent node, it DOES NOT automatically inherit to children unless the system explicitly propagates it. There is no silent inheritance. Propagation is always an explicit, logged, auditable action.

---

## 6. Hierarchy Node Rules

6.1. A node cannot be moved to a different parent after it has enclosures or operational records. To restructure, a data migration plan is required.

6.2. Node names must be unique within their parent scope (two siblings cannot share a name).

6.3. Node codes must be unique within their Farm.

6.4. Bulk-creating nodes is supported via CSV import. The import must validate hierarchy depth constraints before committing.

6.5. Deleting a node is a soft delete (`is_active = False`). The node and all its children are hidden from operational views but their historical records are preserved and queryable in reports.

6.6. A node can be reactivated if it was soft-deleted, as long as its parent is also active.

6.7. The API must return hierarchy trees as nested JSON. Flat arrays are forbidden for hierarchy representation.

---

## 7. Enclosure Rules

7.1. **Enclosure Identity:** Each enclosure is identified by its `code`, unique within its Farm. The system must enforce this uniqueness at the database level.

7.2. **Enclosure History:** An enclosure maintains a complete ordered history of:
- All operations performed on it (direct and propagated)
- All daily task reports referencing it
- All harvest records
- All media attachments
- All inventory movements targeting it

7.3. **Operational Status:** At any moment, an enclosure's operational status is computed — not stored — from its history:
- `NO_ACTIVITY` — no records in current season
- `ACTIVE` — has records in current season
- `COMPLETED` — all planned operations for season are done (requires season plan)
- `OVERDUE` — has overdue planned operations

7.4. **Completion Percentage:** The completion percentage of an enclosure within a season is:
```
completion% = (completed_operations / total_planned_operations) × 100
```
If no season plan exists, completion% = `null` (not 0%).

7.5. **Crop Change Policy:** Crop type can only be changed if the enclosure has zero harvest records in ANY season. Crop change invalidates all planned operations. The system must prompt a confirmation warning.

7.6. **Tree Count:** For palm enclosures, `tree_count` may change over time (new planting, tree removal). Changes must be logged as an audit event with before/after values. The system stores the current count. Historical tree counts at a given date are reconstructed from audit logs.

---

## 8. Crop Rules

8.1. Each enclosure has exactly one active CropType at any time.

8.2. Palm crops (`category = PALM`) unlock the tree counting system. All operations for palm enclosures can optionally specify which trees were targeted.

8.3. Vegetable and grain crops (`VEGETABLE`, `GRAIN`) use area-based tracking (sq meters or rows) rather than tree count.

8.4. Mixed cropping (two CropTypes in one Enclosure) is NOT supported. Each enclosure is single-crop. A physical mixed plot must be split into multiple enclosures.

8.5. Seasonal crop enclosures can be "replanted" by creating a new Season and resetting the planting_date. The old planting history is preserved in season-scoped records.

---

## 9. Palm Tree Logic

9.1. Palm farms are the primary use case for ATLS's tree-level tracking.

9.2. **Tree Count Fields per Enclosure:**
- `tree_count` — Total trees currently in enclosure
- `productive_tree_count` — Trees currently bearing fruit (computed or manually set)
- `dead_tree_count` — Trees confirmed dead (computed from logged events)

9.3. **Palm Age:** Age is computed from `planting_date`:
```
age_years = (today - planting_date).days / 365.25
```
Age is never stored, always computed.

9.4. **Palm Stages by Age:**
- `SEEDLING` — 0–3 years
- `JUVENILE` — 3–7 years
- `PRODUCTIVE` — 7–80 years
- `OLD` — 80+ years

These stages affect expected yield benchmarks in the Analytics domain.

9.5. **Tree-Level Operations:** Some operations target specific trees, not the whole enclosure. In this case, the operation record stores `targeted_tree_count` in addition to the enclosure reference.

---

## 10. Season System

10.1. **Season Scope:** A Season bounds the operational period of a Farm. All reports, operations, and harvests created during a Season belong to that Season.

10.2. **Season Lifecycle States:**

```
OPEN → (close action) → CLOSED → (archive action) → ARCHIVED
```

| State | Can Create Operations | Can Create Harvests | Editable | Deletable |
|---|---|---|---|---|
| OPEN | Yes | Yes | Yes | No |
| CLOSED | No | No | No (except admin) | No |
| ARCHIVED | No | No | No | No |

10.3. **Season Opening:** Only one season can be OPEN per Farm. Opening a new season while one is OPEN requires explicitly closing the current one first.

10.4. **Season Closing:** Closing a season computes and freezes:
- Total operations count
- Total harvest yield per enclosure
- Completion percentage per enclosure
- These frozen snapshots are stored in `SeasonSnapshot` model.

10.5. **Season Data Isolation:** A query for "enclosure data" without a season filter must always default to the current OPEN season. Queries that span seasons are explicitly season-comparative and must be flagged as such.

10.6. **No Season — No Operation Rule:** If no season is OPEN for a Farm, the system must block all operation and harvest creation with a clear error: "لا يوجد موسم نشط لهذه المزرعة".

---

## 11. Farm Lifecycle

```
[Setup] → [Season Open] → [Operational] → [Season Close] → [Review] → [New Season Open] → ...
```

**Setup Phase:**
- Farm is created.
- HierarchyConfiguration is defined.
- HierarchyNodes are created.
- Enclosures are created and assigned to nodes.
- CropTypes assigned to each enclosure.
- Staff assigned to farm.
- Equipment registered.

**Operational Phase:**
- Season is opened.
- Operations are planned and executed.
- Daily reports are submitted.
- Harvest events are recorded.
- Media is attached.

**Review Phase:**
- Season is closed.
- SeasonSnapshot is computed.
- Analytics are generated.
- Season is archived.

**Dormant State:**
- Between seasons, no operational records can be created.
- Farm data, structure, and history remain fully accessible.

---

## 12. Operational Relationships

12.1. **Operation → Farm:** Every operation is scoped to one Farm.

12.2. **Operation → Season:** Every operation is scoped to one Season.

12.3. **Operation → Target:** An operation targets one of:
- A specific `Enclosure` (direct)
- A `HierarchyNode` at any level (parent target)

12.4. **Propagation Rule (CRITICAL):**
When an operation targets a `HierarchyNode`, the system MUST automatically create propagated operation records for every **active** Enclosure that is a descendant of that node.

Propagation behavior:
- The parent operation is the `source` record.
- Each propagated enclosure record has `is_propagated = True` and `source_operation = FK`.
- Propagated records inherit: `operation_type`, `date`, `notes`, `season`.
- Propagated records are individually editable (override notes, completion, etc.).
- Deactivated enclosures are EXCLUDED from propagation.

12.5. **Completion Tracking:** Each propagated or direct operation record has a `completion_status`:
- `PENDING` — created but not confirmed complete
- `IN_PROGRESS` — partially done (for multi-day operations)
- `COMPLETED` — confirmed complete
- `SKIPPED` — intentionally skipped with reason

12.6. **Node-Level Completion:** The completion % of a HierarchyNode for an operation is:
```
node_completion% = (COMPLETED enclosures under node / total enclosures under node) × 100
```

---

## 13. Report Relationships

13.1. DailyTaskReports (from the Reporting Domain) are linked to Farms and Seasons.

13.2. Each report line item references a specific Enclosure.

13.3. Reports aggregate the operations performed in a given day. A report does not create operations — it records that a previously planned or spontaneous operation was executed.

13.4. The Farm Domain exposes an `EnclosureReportHistory` view that aggregates all report entries for a given enclosure across seasons.

13.5. The Farm Domain does NOT own report logic. It consumes report data for enclosure history views.

---

## 14. Harvest Relationships

14.1. Harvest records (from Harvest Domain) are linked to a specific Enclosure and Season.

14.2. The Farm Domain provides the `EnclosureYieldHistory` view: total yield per enclosure per season.

14.3. For palm enclosures, yield is recorded in `kg` per harvest event. Multiple harvest events per season are normal.

14.4. The Farm Domain exposes cumulative yield for analytics but does NOT own harvest creation logic.

14.5. Harvest data is frozen in `SeasonSnapshot` on season close.

---

## 15. Inventory Relationships

15.1. Inventory movements (from Inventory Domain) can reference a Farm and optionally an Enclosure.

15.2. The Farm Domain provides a read view of inventory consumed per enclosure per season.

15.3. Inventory consumption is linked to operations: when an operation of type `FERTILIZATION` is completed, it triggers inventory decrement for the consumed fertilizer.

15.4. The Farm Domain does NOT own inventory ledger logic. It consumes inventory data for enclosure cost tracking.

---

## 16. Equipment Relationships

16.1. Equipment (from Equipment Domain) is registered at the Farm level.

16.2. Equipment assignments to specific operations are recorded with enclosure references.

16.3. The Farm Domain provides an `EnclosureEquipmentHistory` view: which equipment was used in each enclosure per season.

16.4. Equipment does NOT belong to individual enclosures. It belongs to the Farm and is assigned per-operation.

---

## 17. Media Relationships

17.1. Media attachments (photos, videos) can be linked to:
- A Farm (farm-level photos)
- A HierarchyNode (sector/stage photos)
- An Enclosure (enclosure-specific media)
- An Operation (operation evidence photos)
- A Harvest Record (harvest photos)

17.2. The Farm Domain owns the media attachment points. The Media Domain handles storage, compression, and CDN delivery.

17.3. Enclosure media is displayed in chronological order in the Enclosure detail view.

17.4. Media attachments include:
- `file_url` — CDN URL
- `thumbnail_url` — Compressed thumbnail
- `uploaded_at`
- `uploaded_by`
- `context_type` — ENUM: `FARM`, `NODE`, `ENCLOSURE`, `OPERATION`, `HARVEST`
- `context_id` — ID of the associated entity
- `season` — FK to Season (nullable)
- `location` — GPS coordinates (if captured by mobile device)

17.5. Media tagged with GPS coordinates can be displayed on a farm map view.

---

## 18. Analytics Relationships

18.1. The Analytics Domain reads Farm, Enclosure, Season, and operation data to produce:
- Per-enclosure productivity scores
- Per-season yield trends
- Operation frequency analysis
- Cost-per-enclosure estimates
- Worker productivity ratios

18.2. The Farm Domain provides denormalized read models for analytics. It does NOT own analytics computation.

18.3. Key Farm Domain analytics surfaces:
- **Enclosure Heatmap:** Color-codes enclosures by completion%, yield, or operation frequency.
- **Season Comparison:** Side-by-side yield and operation counts across seasons.
- **Farm Productivity Index:** Weighted score across all enclosures combining yield, completion, and operation adherence.

18.4. Analytics data must always be season-scoped. Cross-season analytics are explicitly labeled as comparative.

---

## 19. Domain Events

The Farm Domain publishes the following events. All subscribers must implement idempotent handlers.

| Event Name | Trigger | Payload |
|---|---|---|
| `Farm.Created` | New farm saved | `{farm_id, tenant_id, name}` |
| `Farm.Deactivated` | Farm soft-deleted | `{farm_id, tenant_id}` |
| `Farm.Season.Opened` | Season status → OPEN | `{farm_id, season_id, start_date}` |
| `Farm.Season.Closed` | Season status → CLOSED | `{farm_id, season_id, end_date, snapshot_id}` |
| `Farm.Season.Archived` | Season status → ARCHIVED | `{farm_id, season_id}` |
| `Farm.Enclosure.Created` | New enclosure saved | `{farm_id, enclosure_id, node_id}` |
| `Farm.Enclosure.Deactivated` | Enclosure soft-deleted | `{farm_id, enclosure_id}` |
| `Farm.Enclosure.CropChanged` | CropType changed | `{enclosure_id, old_crop_id, new_crop_id}` |
| `Farm.Enclosure.TreeCountChanged` | tree_count updated | `{enclosure_id, old_count, new_count}` |
| `Farm.Node.Deactivated` | Node soft-deleted | `{farm_id, node_id, affected_enclosure_ids[]}` |
| `Farm.HierarchyConfig.Changed` | Depth or labels changed | `{farm_id, old_depth, new_depth}` |

**Event consumers:**
- Operations Domain: Listens to `Farm.Season.Closed` to freeze operation states.
- Harvest Domain: Listens to `Farm.Season.Closed` to freeze yield records.
- Analytics Domain: Listens to `Farm.Season.Closed` to trigger snapshot computation.
- Audit Domain: Listens to ALL Farm events for audit logging.

---

## 20. Permissions

Permission strings follow the pattern `{action}:{domain}:{resource}`.

| Permission | Role | Description |
|---|---|---|
| `create:farm:farm` | SUPER_ADMIN, TENANT_ADMIN | Create a new farm |
| `view:farm:farm` | ALL authenticated roles | View farm details |
| `edit:farm:farm` | TENANT_ADMIN, FARM_MANAGER | Edit farm settings |
| `deactivate:farm:farm` | TENANT_ADMIN | Soft-delete a farm |
| `create:farm:hierarchy` | TENANT_ADMIN, FARM_MANAGER | Create hierarchy nodes |
| `edit:farm:hierarchy` | TENANT_ADMIN, FARM_MANAGER | Edit hierarchy nodes |
| `deactivate:farm:hierarchy` | TENANT_ADMIN | Soft-delete a node |
| `create:farm:enclosure` | FARM_MANAGER | Create enclosures |
| `edit:farm:enclosure` | FARM_MANAGER | Edit enclosure metadata |
| `view:farm:enclosure_history` | FARM_MANAGER, SUPERVISOR | View full enclosure history |
| `create:farm:season` | TENANT_ADMIN, FARM_MANAGER | Create seasons |
| `close:farm:season` | TENANT_ADMIN, FARM_MANAGER | Close active season |
| `archive:farm:season` | TENANT_ADMIN | Archive closed season |
| `view:farm:analytics` | FARM_MANAGER, SUPERVISOR, OWNER | View analytics |

**Role Hierarchy:** SUPER_ADMIN > TENANT_ADMIN > FARM_MANAGER > SUPERVISOR > FIELD_WORKER

Field workers can view enclosure details relevant to their assigned operations but cannot modify Farm structure.

---

## 21. Validation Rules

### Farm Validation
- `name` — Required, 2–100 chars, Arabic or English
- `code` — Required, unique per tenant, alphanumeric + hyphens, 2–20 chars
- `area_hectares` — Required, DecimalField, > 0, max 999999.99
- `location` — Optional, if provided must be valid lat/lng pair

### HierarchyConfiguration Validation
- `depth` — Required, integer 0–3
- Level labels required for each depth level used
- Label length: 1–50 chars

### HierarchyNode Validation
- `name` — Required, 1–100 chars, unique within parent
- `code` — Required, unique within farm, alphanumeric + hyphens
- `level` — Must equal `parent.level + 1` or 1 if root
- Cannot create node at level > `farm.hierarchy_config.depth`

### Enclosure Validation
- `name` — Required, 1–100 chars
- `code` — Required, unique within farm
- `crop_type` — Required
- `tree_count` — Required if crop is PALM, must be integer ≥ 0
- `area_sqm` — Required, > 0
- `planting_date` — Required, must not be in the future
- `parent_node` — Required if farm depth > 0; must be a node at max depth level

### Season Validation
- `name` — Required, 1–100 chars
- `start_date` — Required
- `end_date` — Must be after `start_date` if provided
- Cannot open a new season if another is OPEN
- Cannot delete a season with any associated records

---

## 22. Multi-Tenant Rules

22.1. Every Farm record carries a `tenant_id`. Every ORM query in the Farm Domain must filter by `tenant_id` derived from the authenticated request. Missing tenant filter is a P0 security bug.

22.2. Farm codes are unique within a tenant, not globally.

22.3. HierarchyNodes, Enclosures, and Seasons are implicitly tenant-isolated through their `farm` FK. No additional tenant filter is needed if querying via farm.

22.4. Cross-tenant farm access is only possible for SUPER_ADMIN users with explicit multi-tenant scope flags. These users see a tenant selector and their queries include an explicit tenant override.

22.5. Analytics aggregation across farms within one tenant is permitted. Cross-tenant analytics is forbidden.

22.6. Tenant isolation is enforced at the Django queryset level via a custom `TenantManager` that overrides `get_queryset()` to inject the tenant filter automatically.

---

## 23. White-Label Rules

23.1. All hierarchy level labels (Sector, Stage, Row, Enclosure) are configurable per Farm via `HierarchyConfiguration`. The UI must render these labels from the configuration, never from hardcoded strings.

23.2. The term "Enclosure" (الحوشة) is the system's internal term. Tenants may relabel it (e.g., "Plot", "Block", "Unit"). This relabeling is stored in `HierarchyConfiguration.enclosure_label`.

23.3. The Farm Domain does not hardcode any crop-specific UI behavior. Crop-specific rules are driven by `CropType.category`.

23.4. White-label operators can disable the tree-count system entirely via the Configuration Engine if their farms do not grow palm trees.

23.5. Map view, satellite overlay, and GPS features can be toggled per tenant via feature flags.

---

## 24. Mobile-First UX Considerations

24.1. **Farm Overview Screen:** Card-based layout showing active season status, enclosure count, and completion percentage. Single-column on mobile, three-column grid on desktop.

24.2. **Hierarchy Navigation:** On mobile, each hierarchy level is a full-screen list with a sticky breadcrumb header. No nested expansion panels. Tap to drill down, back button to go up.

24.3. **Enclosure Detail:** Full-screen scrollable view with tabs: Info | Operations | Harvests | Media | Analytics.

24.4. **Quick Actions:** Floating Action Button (FAB) on enclosure screens for: Add Operation, Add Media, Add Harvest.

24.5. **Offline Consideration:** The hierarchy tree and enclosure list must be cached locally (via React Query's `staleTime` and `cacheTime` settings) for offline browsing. Write operations queue for sync when connectivity returns.

24.6. **Field Worker View:** Simplified view showing only the worker's assigned enclosures and today's operations. No hierarchy management tools visible.

---

## 25. RTL Considerations

25.1. All farm names and node names are Arabic by default. Text is right-aligned and uses RTL layout.

25.2. Hierarchy tree visualization must render in RTL: tree branches expand to the LEFT on screen.

25.3. Breadcrumb navigation: Home ← Sector ← Stage ← Enclosure (reversed visually in RTL, arrow points left).

25.4. Farm map overlays render geographic coordinates as-is (maps are not RTL). Only the UI controls and labels overlaid on the map follow RTL.

25.5. Enclosure completion heatmaps fill from right-to-left in RTL mode.

25.6. All Framer Motion slide transitions for hierarchy drill-down must use `useRTLMotion()` (see `AI_DEVELOPMENT_RULES.md §8.9`).

---

## 26. Future Expansion Strategy

26.1. **GPS-Bounded Enclosures:** Future support for polygon GPS boundaries per enclosure, enabling satellite integration and precision agriculture overlays.

26.2. **IoT Sensor Integration:** Attach soil moisture, temperature, and humidity sensor data to Enclosures. Sensor readings become part of the enclosure's history.

26.3. **Drone Survey Integration:** Drone imagery can be linked to Enclosures as a media type with auto-tagging of GPS coordinates.

26.4. **Yield Prediction Engine:** Using historical SeasonSnapshot data, an AI model predicts expected yield per enclosure for the upcoming season.

26.5. **Inter-Farm Benchmarking:** For tenants with multiple farms, cross-farm analytics that compare productivity indices while maintaining farm isolation.

26.6. **Dynamic Farm Templates:** Pre-built HierarchyConfigurations for common farm types (date palm farm, greenhouse, open field) that new farms can adopt as starting points.

---

## 27. Anti-Patterns

> Patterns explicitly forbidden in the Farm Domain:

- ❌ **Hardcoding hierarchy depth.** Never write `if level == 3` in code. Always derive from `HierarchyConfiguration.depth`.
- ❌ **Storing derived data without a cache strategy.** Completion percentage is computed, not stored. If performance requires caching, use Redis with an explicit invalidation strategy.
- ❌ **Season-unscoped queries in operational views.** Every operational list view must be scoped to a season. Returning unscoped enclosure data is a data integrity risk.
- ❌ **Silently excluding deactivated enclosures from history.** Deactivated enclosures appear greyed-out in history views. They are never invisible.
- ❌ **Allowing direct enclosure creation without a node (when depth > 0).** The system must enforce parent node assignment for enclosures in farms with depth > 0.
- ❌ **Mutating SeasonSnapshot after season close.** Snapshots are immutable write-once records.
- ❌ **Using enclosure `id` as a display identifier.** Always show `code` to users. PKs are internal only.
- ❌ **Propagating operations to inactive enclosures.** Propagation must filter to `is_active = True` enclosures only.
- ❌ **Merging two enclosures.** There is no merge operation. Split or restructure requires manual data migration with full audit logging.

---

## 28. Edge Cases

**EC-01: Farm with zero enclosures.**
A Farm can exist with zero enclosures. No operations or harvests can be created. The system shows an empty state with a call-to-action to add enclosures.

**EC-02: Season closed with open (PENDING) operations.**
Closing a season automatically sets all PENDING operations to `SKIPPED` with system note: "Season closed". A confirmation dialog must warn the manager before closing.

**EC-03: Enclosure deactivated mid-season.**
A deactivated enclosure mid-season retains all records for that season. Future propagated operations skip it. Existing propagated records remain with status `SKIPPED`.

**EC-04: HierarchyConfiguration depth changed after enclosures created.**
This is a DESTRUCTIVE change. The system must:
1. Block the change if any enclosure exists without an explicit admin override.
2. Require a written migration reason.
3. Log the change as a high-severity audit event.

**EC-05: Multiple farms under one tenant.**
Supported. Each farm has its own hierarchy, seasons, and enclosures. Analytics can aggregate across farms within the same tenant with explicit cross-farm scope.

**EC-06: Planting date in the past by decades.**
Valid. Old farms may have palm trees planted 30–80 years ago. No minimum-age restriction on planting_date.

**EC-07: Enclosure with tree_count = 0.**
Valid state for enclosures that have had all trees removed. They remain active for record-keeping. Operations can still target them (e.g., land preparation for replanting).

**EC-08: No active season when trying to create an operation.**
Return HTTP 422 with error body: `{"code": "NO_ACTIVE_SEASON", "message": "لا يوجد موسم نشط لهذه المزرعة"}`. Never silently create records without a season.

---

## 29. Technical Constraints

29.1. **Max hierarchy depth:** 3 levels below Farm (configurable, absolute maximum is 3). This keeps tree queries manageable with recursive CTEs.

29.2. **Max enclosures per farm:** Soft limit of 10,000. Above 500 enclosures, list APIs must enforce cursor-based pagination.

29.3. **Max nodes per level:** No hard limit, but UI performance degrades above 200 nodes per parent. Above 200, the UI switches to a searchable list view automatically.

29.4. **Propagation batch size:** When an operation targets a node with more than 200 child enclosures, propagation is processed asynchronously via a background task (Celery). The operation creation API returns immediately; propagated records appear as they complete.

29.5. **Season snapshot computation:** Triggered synchronously for farms with ≤ 500 enclosures. Above 500, triggered asynchronously via Celery task with a progress indicator in the UI.

29.6. **GPS precision:** Stored as `DecimalField(max_digits=9, decimal_places=6)` — approximately 0.1 meter precision.

29.7. **Database indexes required:**
- `(farm_id, is_active)` on Enclosure
- `(farm_id, status)` on Season
- `(farm_id, parent_id, is_active)` on HierarchyNode
- `(enclosure_id, season_id)` on any cross-reference table

---

## 30. Example Real-World Scenarios

### Scenario A: Date Palm Farm — Full Depth
**Client:** Large Saudi date palm farm, 800 enclosures.

**Configuration:** Depth = 2
- Farm: Al-Waha Farm
- Level 1 Label: "قطاع" (Sector)
- Level 2 Label: "مرحلة" (Stage)
- Level 3 (Enclosure) Label: "حوشة"

**Structure:**
```
Al-Waha Farm
├── Sector A
│   ├── Stage 1 → Enclosures 001–050
│   └── Stage 2 → Enclosures 051–100
└── Sector B
    └── Stage 1 → Enclosures 101–150
```

**Operation Example:** Manager creates "Fertilization" operation targeting "Sector A". System propagates to all 100 active enclosures in Sector A. Propagation is async (> 200 threshold not met). Field workers see their assigned enclosures in the daily work list.

---

### Scenario B: Small Vegetable Farm — No Hierarchy
**Client:** Small family vegetable farm, 12 enclosures.

**Configuration:** Depth = 0 (direct enclosures)

**Operation Example:** Manager creates "Irrigation" targeting Enclosure "Plot-03" directly. No propagation. Completion tracked per enclosure.

---

### Scenario C: Multi-Crop Greenhouse — Single Level
**Client:** Greenhouse operator, 60 enclosures across 4 sections.

**Configuration:** Depth = 1
- Level 1 Label: "قسم" (Section)

**Season Close Example:** Manager closes season. System detects 8 PENDING operations. Shows warning: "8 عمليات لم تكتمل. هل تريد إغلاق الموسم؟" Manager confirms. Pending operations set to SKIPPED. SeasonSnapshot computed synchronously (< 500 enclosures). Analytics available immediately.

---

### Scenario D: White-Label Deployment — Custom Labels
**Client:** Mango farm, using Arabic labels "بستان" (Orchard) instead of "قطاع".

**Configuration:** Depth = 1
- Level 1 Label: "بستان" (Orchard)
- Enclosure Label: "شجرة" (Tree block)

**Result:** All UI, reports, and exports use "بستان" and "شجرة". The internal data model uses `HierarchyNode` and `Enclosure` — never exposed to the user.

---

## 31. Farm Aggregate Boundaries

**Aggregate Roots:**
The Farm Domain is strictly divided into four Aggregate Roots. No transaction may modify entities across two Aggregate Roots simultaneously without using eventual consistency (Domain Events).

1. **Farm Aggregate**
   - **Root Entity:** `Farm`
   - **Child Entities:** `HierarchyConfiguration`, `Equipment`
   - **Invariants:** A Farm must have exactly one active `HierarchyConfiguration`. Deactivating a Farm disables all operational access.
   - **Consistency:** Strong. Changes to config depth immediately block incompatible node creation.

2. **Season Aggregate**
   - **Root Entity:** `Season`
   - **Child Entities:** `SeasonSnapshot`
   - **Invariants:** Only one Season can be OPEN per Farm. Start date must precede end date.
   - **Consistency:** Strong. Closing a season synchronously computes the SeasonSnapshot (if < 500 enclosures) or transitions state to CLOSING until async job finishes.

3. **Hierarchy Aggregate**
   - **Root Entity:** `HierarchyNode`
   - **Child Entities:** `HierarchyNode` (self-referential)
   - **Invariants:** Tree depth cannot exceed `HierarchyConfiguration.depth`. Cycles are forbidden.
   - **Consistency:** Strong. Deactivating a node hides its descendants in the same transaction.

4. **Enclosure Aggregate**
   - **Root Entity:** `Enclosure`
   - **Child Entities:** None directly (history is aggregated via views).
   - **Invariants:** Must belong to a valid leaf node if depth > 0. Must have one `CropType`.
   - **Consistency:** Strong. `tree_count` mutations are atomic.

**Aggregate Ownership:**
External domains (Harvest, Operations) hold references (IDs) to Farm Aggregates but cannot mutate them. To mutate a Farm Aggregate, external domains must emit a Domain Event that the Farm Domain consumes.

---

## 32. Farm Domain Services

Business logic is encapsulated in stateless, pure Domain Services located in `services.py`.

### `SeasonClosingService`
- **Responsibilities:** Validates season close conditions, computes final completion percentages, freezes yield data into `SeasonSnapshot`, archives pending operations.
- **Inputs:** `season_id`, `tenant_id`, `user_id`
- **Outputs:** `SeasonSnapshot` object
- **Transaction Behavior:** `transaction.atomic()`. Fails entirely if snapshot generation fails.
- **Events Published:** `Farm.Season.Closed`

### `OperationPropagationService`
- **Responsibilities:** Expands a node-targeted operation into individual enclosure operations.
- **Inputs:** `operation_id`, `target_node_id`, `tenant_id`
- **Outputs:** Count of propagated records.
- **Transaction Behavior:** Batch inserts inside `transaction.atomic()`. Dispatches to Celery if enclosures > 200.
- **Events Published:** None directly (Operations Domain owns the operation events).

### `HierarchyMigrationService`
- **Responsibilities:** Safely processes structural changes (e.g., depth changes or moving nodes).
- **Inputs:** `farm_id`, `new_config`, `node_mapping`
- **Outputs:** Updated `HierarchyConfiguration`.
- **Transaction Behavior:** Atomic. Requires Super Admin approval.
- **Events Published:** `Farm.HierarchyConfig.Changed`

### `EnclosureLifecycleService`
- **Responsibilities:** Handles Enclosure creation, deactivation, and crop changes.
- **Inputs:** `enclosure_data`, `tenant_id`, `user_id`
- **Outputs:** `Enclosure` instance.
- **Transaction Behavior:** Atomic. Checks season locks before mutation.
- **Events Published:** `Farm.Enclosure.Created`, `Farm.Enclosure.Deactivated`, `Farm.Enclosure.CropChanged`

### `CompletionCalculationService`
- **Responsibilities:** Computes realtime completion % for an enclosure or node.
- **Inputs:** `entity_id`, `season_id`
- **Outputs:** `{ "planned": int, "completed": int, "percentage": float }`
- **Transaction Behavior:** Read-only. No transaction.
- **Events Published:** None.

---

## 33. Farm Read Models (CQRS Strategy)

ATLS separates the write model (Aggregates) from the read model (Views) to handle complex analytics without locking tables.

33.1. **CQRS Strategy:** The write database handles pure transactions. Denormalized Read Models are built via database Views (for real-time) or async Celery tasks (for complex aggregations).

33.2. **`FarmHierarchyReadModel`**
- **Purpose:** Fast delivery of the full tree structure for mobile navigation.
- **Mechanism:** Materialized View updated asynchronously via Celery on `Farm.Node.*` events.
- **Invalidation:** Redis cache key `farm:{id}:tree` cleared on structural changes.

33.3. **`EnclosureDashboardReadModel`**
- **Purpose:** Serves the main operational table (Enclosures + Current Status + Completion %).
- **Mechanism:** Denormalized table `enclosure_dashboard_read` updated via Django signals on Operation/Harvest events.
- **Invalidation:** Eventual consistency (target: < 2 seconds delay).

33.4. **`EnclosureHistoryReadModel`**
- **Purpose:** Chronological timeline of everything that happened to an enclosure.
- **Mechanism:** Database View performing `UNION ALL` across Operations, Reports, and Harvests, indexed by `(enclosure_id, date)`.
- **Invalidation:** Real-time via View.

33.5. **`SeasonAnalyticsReadModel`**
- **Purpose:** Aggregate statistics for the current season.
- **Mechanism:** Computed nightly or on-demand via Redis. Frozen into `SeasonSnapshot` on close.

---

## 34. Operation Propagation Strategy

Current propagation is enhanced with a distributed, scalable strategy to prevent write amplification.

34.1. **Thresholds:**
- **< 50 enclosures:** Synchronous Eager Propagation. Immediate response.
- **50 – 500 enclosures:** Asynchronous Eager Propagation (Celery). UI shows "Propagation in progress".
- **> 500 enclosures:** Virtual Propagation.

34.2. **Virtual Propagation (Large Scale):**
- Does not create individual database rows immediately.
- Creates a single `VirtualOperation` record linked to the target node.
- When an enclosure is fetched, the API dynamically merges virtual operations with explicit enclosure operations.
- Explicit actions on a virtual operation for a specific enclosure (e.g., marking it complete) "materializes" that single record into the DB as an explicit override.

34.3. **Idempotency & Duplicate Prevention:**
- Propagation jobs are keyed by `hash(operation_id, target_node_id)`. Redis prevents duplicate identical propagation tasks from running simultaneously.

34.4. **Failure Recovery:**
- Celery tasks use `acks_late=True` and transaction boundaries. If a propagation task fails mid-batch, it retries and uses `get_or_create` to prevent duplicate row creation.

---

## 35. Offline Synchronization & Conflict Resolution

ATLS is a mobile-first field system. Network loss is expected.

35.1. **Optimistic Locking:** Every Enclosure and Operation record includes a `_version` field. Updates must include the version. If the server version > client version, an `HTTP 409 Conflict` is returned.

35.2. **Queueing Mobile Writes:**
- Write operations performed offline are stored in IndexedDB (frontend) in a Sync Queue.
- The queue stores the exact API payload and timestamp.

35.3. **Sync Strategy:**
- Upon reconnection, the frontend dispatches the Sync Queue sequentially.
- Transient errors (500, network) trigger exponential backoff retries.
- Persistent errors (400, 409) move the item to a "Conflict UI" state.

35.4. **Conflict Resolution Rules:**
- **Last-Write-Wins (LWW):** Applied to simple fields (notes, status) if `_version` matches.
- **Additive Merge:** Applied to collections (adding photos, logging harvest weight). Offline additions are always accepted.
- **Hard Conflict:** If a field worker tries to update an operation that a manager has locked or deleted, the worker receives a conflict notification. The local change is discarded.

---

## 36. Audit Severity & Security Escalation

Every domain event is logged by the Audit Domain with an explicit severity level.

| Severity | Triggers | Escalation & Alerts |
|---|---|---|
| **LOW** | Enclosure created, media uploaded, operation marked complete. | Stored in audit log only. No alerts. |
| **MEDIUM** | Crop type changed, tree count adjusted, season opened. | Highlighted in Farm Manager's daily digest. |
| **HIGH** | Season closed without 100% completion, Hierarchy node deleted. | In-app notification to Tenant Admin. Requires explicit confirmation reason. |
| **CRITICAL** | Hierarchy depth changed, Farm deactivated, mass-deletion. | SMS/Email alert to Super Admin. Blocked until Super Admin enters OTP / confirmation code. |

---

## 37. Domain Ownership Matrix

To prevent circular dependencies, ATLS strictly enforces the Source of Truth.

| Concept / Data | Authoritative Owner (Write) | Consumers (Read-Only) |
|---|---|---|
| Farm Hierarchy & Enclosures | **Farm Domain** | All Domains |
| Season State | **Farm Domain** | All Domains |
| Operation Records | **Operations Domain** | Farm (History), Analytics |
| Completion % | **Operations Domain** | Farm (Dashboard), Analytics |
| Daily Reports | **Reporting Domain** | Farm (History), HR (Payroll) |
| Harvest Yield | **Harvest Domain** | Farm (History), Analytics, Inventory |
| Inventory Consumption | **Inventory Domain** | Operations, Farm, Analytics |
| Season Snapshot | **Farm Domain** (Assembler) | Analytics |
| Worker Productivity | **Analytics Domain** | HR |

**Rule:** A domain may query another domain's Read Model, but may never write to another domain's database tables.

---

## 38. Farm Domain Performance Rules

38.1. **Query Complexity Limits:** No query may exceed 3 table joins (`select_related`). Complex queries must be routed to a denormalized Read Model.

38.2. **Maximum Recursion Depth:** Hierarchy tree fetching uses PostgreSQL CTEs (Common Table Expressions) limited strictly to the configured `HierarchyConfiguration.depth` (max 4). Infinite recursion is impossible by design.

38.3. **Mobile Payload Size:** The `/api/v1/farm/{id}/sync` endpoint must compress its payload. The maximum allowed payload size for the offline hierarchy initialization is 5MB. Above 5MB, enclosures must be lazy-loaded per sector.

38.4. **Pagination Strictness:** Endpoints returning Enclosures or Operations MUST enforce pagination. `limit` parameter is capped at 100. Bypassing pagination (`limit=0`) is forbidden.

38.5. **Analytics Caching:** Analytics endpoint queries spanning > 10,000 rows must hit a Redis cache (TTL: 1 hour) or a pre-computed projection. They must never execute raw aggregation against the transactional tables during business hours.

---

## 39. Farm Domain State Machines

Explicit state machines govern critical entities to prevent invalid transitions.

39.1. **Season State Machine**
- `PENDING` → `OPEN` (Trigger: Manager Action)
- `OPEN` → `CLOSING_ASYNC` (Trigger: Manager Action, if > 500 enclosures)
- `OPEN` / `CLOSING_ASYNC` → `CLOSED` (Trigger: Snapshot Complete)
- `CLOSED` → `ARCHIVED` (Trigger: Admin Action)
- *Forbidden:* `CLOSED` → `OPEN`.

39.2. **Enclosure Operational Status (Computed)**
- `DORMANT` (No season)
- `ACTIVE` (Season open, operations exist)
- `COMPLETED` (100% planned ops done)
- `OVERDUE` (Current date > planned op date & status != completed)

39.3. **Propagation Job State Machine**
- `QUEUED` → `PROCESSING` → `COMPLETED`
- `PROCESSING` → `FAILED_RETRY` → `PROCESSING`
- `FAILED_RETRY` → `DEAD_LETTER` (after 3 retries, requires manual intervention)

---

## 40. AI Implementation Safety Guards

> **CRITICAL DIRECTIVES FOR AI AGENTS WORKING IN THE FARM DOMAIN**

40.1. **Forbidden Direct DB Writes:** Never use `Enclosure.objects.filter(...).update(...)` to bypass the `EnclosureLifecycleService`. All writes must route through the Domain Services.

40.2. **Forbidden Cross-Aggregate Mutations:** Never write a function that saves a `Farm` and a `Season` in the same direct ORM block without using the appropriate services and emitting events.

40.3. **Mandatory Tenant Filtering:** EVERY single ORM query written by the AI MUST include a `tenant_id` check.
- ❌ `Enclosure.objects.get(code=code)`
- ✅ `Enclosure.objects.get(code=code, farm__tenant_id=tenant_id)`

40.4. **Forbidden N+1 Loops:** Never iterate over a queryset of Enclosures and execute a related query inside the loop.
- ❌ `for enc in enclosures: ops = enc.operations.all()`
- ✅ `enclosures.prefetch_related('operations')`

40.5. **Event Emission Mandate:** If an AI implements a feature that changes the state of a Farm, Season, Node, or Enclosure, it MUST include the corresponding `EventBus.publish(...)` call in the service layer.

40.6. **No "Magic" Deletes:** Never implement a `.delete()` method call. Always use `is_active = False` (soft delete) and append a timestamp to the unique code if necessary to free up the unique constraint.

---

> **This document is the law for the Farm Domain. Any implementation that contradicts these rules constitutes a domain violation and must be corrected before merge.**
