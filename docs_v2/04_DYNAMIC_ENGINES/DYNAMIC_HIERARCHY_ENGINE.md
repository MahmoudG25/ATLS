# ATLS Platform: Dynamic Hierarchy Engine Architecture

> **Confidential & Proprietary**  
> **Target Audience:** Principal Architects, Engineering Leads, AI Implementation Agents  
> **Domain:** Agricultural ERP & Operations Platform  

---

## 1. Engine Purpose
The Dynamic Hierarchy Engine is a core architectural foundation of the ATLS platform. Its purpose is to flexibly model diverse agricultural land structures—such as Farm → Sector → Stage → Enclosure, or simply Farm → Enclosure—without hardcoding these layers into the application's source code. It governs how spatial and organizational nodes relate, propagate data, and scope permissions.

## 2. Business Goals
*   **Tenant Flexibility:** Allow a vineyard to structure their land differently than a massive row-crop farm, entirely via configuration.
*   **Operational Precision:** Enable task assignment, reporting, and analytics at any level of granularity (e.g., assigning a task to an entire Farm vs. a single Enclosure).
*   **Future-Proofing:** Support inevitable organizational changes, mergers, or land acquisitions without requiring database schema migrations.
*   **Scalable Scoping:** Provide a lightning-fast mechanism to filter analytics and enforce access control (e.g., "User X can only see data under Sector 4").

## 3. Ubiquitous Language
*   **Node:** Any individual element within the spatial/organizational tree (e.g., Farm A, Sector B).
*   **Node Type:** The classification of a Node (e.g., `FARM`, `SECTOR`, `ENCLOSURE`).
*   **Hierarchy Depth:** The number of levels from the Root Node down to the Leaf Node.
*   **Materialized Path:** A string-based representation of a node's ancestry (e.g., `1.4.12.56`).
*   **Closure Table:** A database pattern storing all ancestor-descendant relationships to enable fast recursive querying.

## 4. Core Concepts
The core concept is **Structural Agnosticism**. The application logic must not assume that an `Enclosure` is always a direct child of a `Sector`. It must rely on the Hierarchy Engine to resolve ancestry, descendants, and relationships dynamically.

## 5. Dynamic Hierarchy Philosophy
*   Code handles *Nodes*, not specific land types.
*   Configuration dictates what Node Types are allowed and how they nest.
*   Operations and metrics cascade down or roll up the tree dynamically.

## 6. Hierarchy Node Architecture
*   A `Node` entity contains structural metadata: `id`, `tenant_id`, `parent_id`, `node_type_id`, `name`, and pathing data.
*   Domain-specific data (e.g., the soil type of an enclosure, the coordinates of a farm) is stored in specialized Domain models that maintain a 1:1 foreign key to the structural `Node`.

## 7. Node Type System
*   Node Types are defined per tenant (or inherited from global templates).
*   They dictate the physical or logical meaning of the node.
*   Examples: `TENANT_ROOT`, `FARM`, `REGION`, `SECTOR`, `BLOCK`, `ENCLOSURE`, `IRRIGATION_ZONE`.

## 8. Parent/Child Rules
*   Defined by `AllowedRelationships` configuration.
*   For example, a tenant's rules engine might enforce that a `BLOCK` can only be a child of a `SECTOR`, and an `ENCLOSURE` can only be a child of a `BLOCK`.
*   The engine validates every insertion or relocation against these tenant-specific rules.

## 9. Root Node Rules
*   Every tenant has exactly one invisible `TENANT_ROOT` node.
*   All top-level organizational entities (e.g., `FARM`) are direct children of the `TENANT_ROOT`.
*   This ensures a unified tree for tenant-wide queries.

## 10. Path Resolution Strategy
*   To avoid complex recursive joins in standard queries, the engine must quickly resolve the question: "Is Node X under Node Y?"
*   This requires a specialized database strategy to store the tree shape.

## 11. Materialized Path vs Closure Table Decision
*   The engine utilizes the **Materialized Path** (or `ltree` in PostgreSQL) pattern for fast read operations and simple branch copying.
*   *Tradeoff:* Materialized paths require recalculation on node relocation, but agricultural hierarchies are read-heavy and rarely restructured mid-season.

## 12. Traversal Strategy
*   **Upward Traversal:** Resolving a node's ancestry (e.g., finding the Farm an Enclosure belongs to).
*   **Downward Traversal:** Resolving all descendants (e.g., finding all Enclosures under a Sector).
*   **Sibling Traversal:** Finding adjacent nodes sharing the same parent.
*   **Scoped Traversal:** Finding all descendants of a specific `Node Type` (e.g., "Get all ENCLOSURES under this FARM").

## 13. Recursive Query Rules
*   The system abstracts recursive database queries behind a `HierarchyRepository`.
*   UI and Domain logic must never write raw CTEs (Common Table Expressions) to traverse the tree.

## 14. Cycle Prevention Rules
*   **CRITICAL:** A hierarchy cannot contain cycles (Node A is parent of Node B, Node B is parent of Node A).
*   The Engine executes a cycle-check algorithm synchronously before committing any `parent_id` mutation.

## 15. Hierarchy Mutation Rules
*   Nodes can be created, renamed, or relocated.
*   Deleting a node requires a `CASCADE` or `RESTRICT` policy based on tenant configuration to prevent Orphan Nodes. Typically, soft-deletes are enforced.

## 16. Node Relocation Rules
*   When a Node (e.g., a Sector) is moved to a new Parent (e.g., a different Farm), its Materialized Path and all descendant paths are synchronously recalculated and updated.
*   Relocation must be strictly validated against `Parent/Child Rules`.

## 17. Historical Integrity Rules
*   **CRITICAL:** If Sector A is moved from Farm 1 to Farm 2 on July 1st, operations performed *before* July 1st must still report under Farm 1 for historical financial integrity.
*   Transactional records (like `OperationLog` or `HarvestYield`) snapshot the `ancestor_path` at the exact moment of creation. They do not rely on the current live hierarchy.

## 18. Propagation Architecture
*   Events occurring on a parent node often need to affect descendants.
*   Example: Changing the irrigation schedule at the `SECTOR` level propagates the setting down to all `ENCLOSURES` within that sector.

## 19. Operation Propagation
*   If an Operations Task is assigned to a `SECTOR`, the system must be capable of expanding that task into granular sub-tasks for every `ENCLOSURE` leaf-node beneath it, if required by the operation type.

## 20. Analytics Scoping
*   Dashboards use the Hierarchy Engine to aggregate data.
*   A user viewing a `SECTOR` dashboard triggers a query: `SELECT SUM(yield) FROM harvest WHERE path <@ 'root.farm_1.sector_2'`. (PostgreSQL `ltree` syntax).

## 21. Permission Scoping
*   Access Control is tightly bound to the Hierarchy Engine.
*   If User A is granted `MANAGER` access on `SECTOR 4`, the authorization middleware uses the Hierarchy Engine to automatically grant access to all descendant nodes of `SECTOR 4`.

## 22. Search & Filtering Strategy
*   Search APIs accept `node_id` and automatically apply a descendant filter.
*   Users can search for "Enclosure 12" and the API returns its full hierarchical context (Farm -> Sector -> Enclosure 12).

## 23. Breadcrumb Architecture
*   APIs returning node data automatically include a lightweight `breadcrumbs` array containing the `id`, `name`, and `node_type` of all ancestors.
*   Ensures the frontend can instantly render navigation headers without issuing a secondary "get parents" request.

## 24. Tree Caching Strategy
*   The overall structural tree of a tenant changes rarely (seasonally or annually).
*   The entire tree structure is cached in Redis upon load and invalidated/rebuilt via event (`HierarchyMutatedEvent`) when a node is added, moved, or deleted.

## 25. Read Models
*   `HierarchyTreeReadModel`: A full nested JSON representation of the tree, optimized for UI dropdowns and tree-view components.
*   Updated asynchronously via the event stream.

## 26. CQRS Relationships
*   **Commands:** `CreateNode`, `MoveNode`, `DeactivateNode`.
*   **Queries:** `GetDescendants`, `GetAncestors`, `GetFullTree`.

## 27. Offline Hierarchy Strategy
*   The mobile application synchronizes the `HierarchyTreeReadModel` upon login.
*   Offline workers can navigate the full farm structure, assign tasks to any node, and rely on the local cache. Changes to the tree structure while offline are rare and resolved via Last-Write-Wins on sync.

## 28. Mobile Navigation UX
*   Tree navigation on mobile requires intuitive drill-down menus, not complex desktop-style expanding tree-grids.
*   Users tap a Farm -> view Sectors -> tap a Sector -> view Enclosures.

## 29. RTL Navigation Rules
*   Tree indentation, chevron icons, and breadcrumb separators (e.g., Farm > Sector) must reverse direction logically for RTL languages.

## 30. Performance Constraints
*   Hierarchy traversal queries (e.g., checking if Node A is under Node B) must execute in < 10ms to ensure authorization checks do not bottleneck the entire platform.
*   Path recalculations during a mass-node move are permitted to take longer but must execute within an ACID transaction.

## 31. Multi-Tenant Isolation
*   Hierarchy tables and path strings MUST strictly include `tenant_id`. A path string of `1.5.10` is meaningless without the `tenant_id` context.

## 32. AI Safety Rules
> [!CAUTION]
> **MANDATORY AI IMPLEMENTATION RULES**
> *   **No Hardcoded Depths:** AI MUST NOT write logic assuming the hierarchy is exactly 3 levels deep.
> *   **Historical Paths:** AI MUST NOT write SQL that dynamically joins current hierarchy state to calculate historical aggregations. Always use the snapshotted path on the transactional record.
> *   **Mandatory Cycle Checks:** AI MUST ensure the cycle-prevention algorithm is invoked synchronously before any node update.

## 33. Anti-Patterns
*   **The Recursive N+1 Problem:** Fetching a node, then querying for its children, then looping and querying for *their* children over the network.
*   **Hardcoded Node Names in Code:** Writing logic like `if node.name == 'Sector 1'`.
*   **Ignoring the Snapshot:** Updating the live hierarchy and breaking last year's financial reports because the records dynamically look up their current parent.

## 34. Real-World Scenarios
**Scenario:** A company acquires a neighboring farm and integrates it into their ATLS tenant.
*   **Action:** The Admin uses the UI to create a new `FARM` node. They then mass-import the new farm's sectors and enclosures.
*   **Engine Result:** The engine dynamically creates the nodes, generates Materialized Paths, validates that they follow the tenant's structural rules, and invalidates the Redis tree cache.
*   **Platform Result:** Without any code deployment, the new farm appears in mobile dropdowns, Operations can be assigned to it, and the Analytics engine begins aggregating its data in isolation from the original farm.

## 35. Future Expansion Strategy
*   **GIS Integration:** Associating GIS Polygon boundaries directly with Hierarchy Nodes.
*   **Spatial Queries:** Enabling the engine to answer "Which node contains this GPS coordinate?"
*   **Temporal Hierarchies:** Supporting fully versioned trees where the application can query "What did the hierarchy look like on Jan 1st, 2024?".

## 36. Architectural Tradeoffs
*   We chose Materialized Paths over Adjacency Lists (simple `parent_id`) for read speed, sacrificing write speed during complex relocations.
*   We duplicate `ancestor_path` onto transactional records (denormalization) to guarantee historical integrity, sacrificing some database storage space.
ذ