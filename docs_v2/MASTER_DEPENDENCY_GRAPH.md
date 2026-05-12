# ATLS Platform: Master Dependency Graph & Governance

> **Confidential & Proprietary**  
> **Target Audience:** Principal Architects, Senior Engineering Team, AI Implementation Agents  
> **Scope:** Global Architecture Map & Dependency Governance  

---

## 1. Purpose Of Dependency Governance

Enterprise distributed systems do not fail because of slow algorithms; they collapse due to uncontrolled implementation chaos and circular dependencies. In a distributed agricultural ERP like ATLS—which relies on offline-first synchronization, event-driven workflows, and dynamic engines—uncontrolled integrations destroy scalability.

Dependency governance exists to:
*   **Prevent Circular Dependencies:** Stopping Domain A from requiring Domain B which requires Domain A.
*   **Define Ownership Boundaries:** Guaranteeing that every line of code, database table, and domain event has an explicit, uncontested owner.
*   **Prevent Implementation Chaos:** Ensuring isolated, testable bounded contexts rather than a monolithic "Big Ball of Mud".
*   **Enforce Domain Isolation:** Enabling teams (and AI agents) to work on domains concurrently without stepping on each other's toes.

---

## 2. Dependency Philosophy

*   **Directional Dependency Rules:** Dependencies must flow downwards from highest volatility (UI/Interface) to lowest volatility (Core Domain). Upward imports are strictly forbidden.
*   **Dependency Inversion:** Interfaces are defined by the consumer but implemented by the provider. Core domains do not know about infrastructure.
*   **Bounded Context Isolation:** One domain cannot directly read or write to another domain's repository.
*   **Shared Kernel Restrictions:** Shared code must be purely conceptual (e.g., standard IDs, standard Enums) with ZERO business logic.
*   **Anti-Corruption Layers (ACL):** When a domain must communicate with a legacy or external domain, it must translate the external payload into its own internal models immediately.

> [!CAUTION]
> **Explicitly Prohibited:**  
> *   **Bidirectional Dependencies:** Domain A imports B, and B imports A.
> *   **Hidden Integrations:** Triggers or shared views directly mapped across bounded context schemas.
> *   **Cyclic Service Calls:** Sync HTTP or internal service calls that loop back.

---

## 3. Global Architecture Layers

The platform is strictly partitioned into horizontal layers. Dependencies may ONLY point downwards.

1.  **Interface Layer (Highest Volatility):** Mobile Apps, Web UI, API Gateways. *Depends on Integration & Read Models.*
2.  **Integration Layer:** Application Services, REST/GraphQL endpoints. *Depends on Domain & Infrastructure.*
3.  **Read Model Layer (CQRS):** Projections, ElasticSearch, Analytics. *Depends on Infrastructure (Broker).*
4.  **Dynamic Engine Layer:** Hierarchy Engine, Form Engine. *Depends on Core Foundation.*
5.  **Domain Layer:** Farm, Enclosures, Operations. *Depends on Core Foundation.*
6.  **Core Foundation Layer (Lowest Volatility):** Tenant abstractions, Shared Kernel UUIDs, Base Exceptions. *Depends on NOTHING.*
7.  **Infrastructure Layer:** Postgres, Redis, Celery, Outbox relay. *Inverted; implements Core Interfaces.*

---

## 4. Domain Dependency Matrix

The table below dictates exact cross-domain dependencies. **If a dependency is not listed here, it is FORBIDDEN.**

| Domain | Upstream Dependencies (Consumes) | Downstream Consumers (Used By) | Forbidden Dependencies | Integration Style | Dependency Risk Level |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Farm** | Core Foundation | Operations, Harvest, Equipment | Inventory, HR | Sync (Internal API) | LOW |
| **Operations** | Farm, Dynamic Engines | Reporting, Analytics | Harvest, Analytics | Async (Events) | CRITICAL |
| **Harvest** | Farm, Operations | Analytics, Inventory | HR | Async (Events) | HIGH |
| **Inventory** | Harvest, Equipment | Analytics, Operations | HR, Audit | Async (Events) | HIGH |
| **HR** | Core Foundation | Operations, Harvest | Operations (Circular) | Sync (Internal API) | MEDIUM |
| **Reporting** | Operations, Harvest | Analytics | Analytics (Circular) | Async (Events) | MEDIUM |
| **Analytics** | ALL DOMAINS | UI / Read Models | Operations, Farm | Async (Event Stream) | LOW |
| **Audit** | ALL DOMAINS | Security, Compliance | Operations | Async (Event Stream) | LOW |
| **Media** | Core Foundation | Farm, Operations, Enclosure | UI directly | Sync (Internal API) | LOW |
| **Notification** | ALL DOMAINS | None (End of line) | Core Foundation | Async (Events) | LOW |
| **Equipment** | Farm, Inventory | Operations | HR | Sync (Internal API) | MEDIUM |

---

## 5. Dynamic Engine Dependency Rules

Dynamic engines provide runtime configurations. They are foundational blocks, but they hold **NO DOMAIN KNOWLEDGE**.

*   **Dynamic Form Engine:** Consumed by Operations, Harvest, HR. Must never know what a "Crop" or "Task" is.
*   **Dynamic Hierarchy Engine:** Consumed by Farm, Operations. Must never know what an "Enclosure" is.
*   **Permission Engine:** Consumed by Integration Layer.
*   **Dashboard Engine:** Consumed by Analytics.
*   **Theme Engine:** Consumed by Interface Layer.

> [!IMPORTANT]
> **Isolation Rule:** Engines MUST remain isolated from the domains that consume them. They operate on abstract constructs (Nodes, Fields, Roles).

---

## 6. Shared Kernel Rules

The Shared Kernel is a dangerous architectural area. It must be aggressively minimized.

**Allowed Shared Concepts:**
*   Canonical Identifiers (`tenant_id`, `enclosure_id`, `operation_id`).
*   Global value objects (e.g., `Money`, `Coordinates`, `TimeZone`).
*   Domain Event Base Classes.

**Forbidden Shared Concepts:**
*   **Shared Business Logic:** Abstract classes containing validation logic for multiple domains.
*   **Cross-Domain Contracts:** Sharing entire Data Transfer Objects (DTOs) between Operations and Inventory. Each must define its own translation.

---

## 7. Anti-Corruption Layer (ACL) Strategy

Domains communicate safely via ACLs to prevent their internal models from leaking.

*   **Translation Boundaries:** When the `Harvest` domain listens to an `OperationCompleted` event, its ACL translates the generic payload into a `HarvestTask` concept before processing.
*   **Legacy Isolation:** Any integration with legacy farm hardware or third-party ERPs MUST pass through an ACL to map external data into pristine ATLS DDD objects.
*   **Event Translation:** Services must never save a raw incoming event payload directly to the database. It must be mapped into the aggregate's dialect.

---

## 8. Event Dependency Governance

The ATLS nervous system runs on Domain Events via the Transactional Outbox.

*   **Event Ownership:** The aggregate that emits the event owns the schema.
*   **Event Consumers:** Consumers depend on the event schema, not the producing service.
*   **Retry Isolation:** Consumer A failing to process an event MUST NOT block Consumer B from processing the exact same event.
*   **Event Versioning:** Events evolve via additive schemas (e.g., `v2`). 

**Explicitly Forbidden:**
*   **Event Payload Mutation:** Consumers must treat event payloads as read-only.
*   **Synchronous Dependency Chains:** Emitting an event, forcing the consumer to run synchronously, and waiting for its result. This breaks bounded contexts.

---

## 9. Read Model Dependency Rules

CQRS Read Models are heavily optimized, eventually consistent projections for UI dashboards.

*   **CQRS Read Ownership:** Projections are owned by the Analytics or Reporting domains.
*   **Projection Boundaries:** A Read Model can listen to events from Farm, Operations, and HR to build a single "Daily Overview" table.
*   **Cache Invalidation:** The domain that owns the Read Model owns the invalidation logic, triggered exclusively by incoming Domain Events.

> [!WARNING]
> Read Models MUST NOT own business logic. They are dumb, flat, materialized views optimized for `SELECT` speeds. They cannot enforce invariants.

---

## 10. Offline System Dependency Rules

Mobile synchronization introduces immense complexity and requires strict dependency isolation.

*   **Sync Engine Ownership:** The `OfflineMergeService` owns the resolution layer, acting as a gateway before hitting the Core Domains.
*   **Merge Ownership:** Conflict resolution logic lives strictly within the target Aggregate.
*   **Mobile Cache Boundaries:** Mobile payload DTOs depend on the Sync Engine schemas, NOT the Core Domain Entities.

---

## 11. AI Agent Dependency Governance

> [!CAUTION]
> **AI IMPLEMENTATION DIRECTIVES**  
> All AI implementation agents are strictly bound by the Master Dependency Graph.

*   **Forbidden Imports:** AI agents MUST NOT import models or repositories from `Domain A` into `Domain B`.
*   **Forbidden Cross-Domain Writes:** AI agents MUST NOT write code that executes synchronous updates across domain boundaries.
*   **Forbidden Direct Integrations:** No raw SQL joins crossing domain schema boundaries.
*   **Mandatory ACLs:** Agents generating integration code MUST include an explicit translation layer (ACL).

**Automatic Rejection Conditions:**
Any AI-generated pull request containing circular imports, cross-domain synchronous `.save()` calls, or shared mutable DTOs MUST be automatically rejected by the CI/CD pipeline.

---

## 12. Dependency Risk Classification

Dependency complexity is evaluated to ensure architectural safety.

| Risk Level | Description | Examples |
| :--- | :--- | :--- |
| **LOW** | Unidirectional, async event streams with no immediate consistency requirement. | Analytics reading from Operations. Audit logging. |
| **MEDIUM** | Synchronous internal API calls to highly stable core domains. | Operations fetching a configuration from Farm. |
| **HIGH** | Complex async workflows requiring compensation or saga management. | Harvest triggering Inventory deductions. |
| **CRITICAL** | Core structural integrations with massive downstream blast radiuses. | Dynamic Hierarchy mapping to Operations. |

---

## 13. Architectural Hotspots

These intersections are extremely dangerous and require Principal Architect oversight:

*   **Operations ↔ Inventory:** High risk of race conditions if offline sync deducts inventory that no longer exists.
*   **Operations ↔ Analytics:** High risk of database locks if analytics query operational tables directly. Must use CQRS.
*   **Harvest ↔ Reporting:** High risk of complex joins.
*   **Offline Sync ↔ Conflict Resolution:** High risk of data loss due to LWW (Last-Write-Wins) overwriting additive intents.
*   **Hierarchy ↔ Propagation:** High risk of infinite loops and memory exhaustion.

---

## 14. Implementation Sequencing Rules

> [!IMPORTANT]  
> **THE ONLY ALLOWED IMPLEMENTATION ORDER**  
> Violating this sequence guarantees technical collapse, cascading rework, and broken tests.

1.  **Core Domain Foundations:** Tenant IDs, Base Entities, Shared Kernel.
2.  **Aggregate Rules:** Invariants, value objects, domain logic (No DB attached yet).
3.  **Domain Services:** Orchestration logic, Repository interfaces.
4.  **Event Infrastructure:** Transactional Outbox, Base Event Schemas.
5.  **Infrastructure Implementation:** Postgres Repositories, Celery Workers.
6.  **Read Models (CQRS):** Projection tables and event handlers.
7.  **Integration Layer:** Application Services and REST APIs.
8.  **UI & Mobile Offline:** Interfaces consuming the APIs.
9.  **Analytics:** End-of-the-line reporting.

---

## 15. Architectural Anti-Patterns

If these are found in the ATLS codebase, the architecture has failed.

*   **Circular Domain Imports:** `operations.models` imports `harvest.models`, and `harvest.models` imports `operations.models`. Result: Python import errors and tight coupling.
*   **Shared Database Tables:** Two domains reading/writing to the same raw Postgres table without an Aggregate Root boundary.
*   **Direct ORM Coupling:** Passing a Django QuerySet or SQLAlchemy object from the Data layer up to the UI view.
*   **Shared Mutable DTOs:** Modifying an event payload in transit and passing it to the next consumer.
*   **Cross-Domain Transactions:** A single `transaction.atomic()` wrapping an Operations write and an Inventory write.
*   **Analytics Mutating State:** A dashboard triggering a status update on a task.

---

## 16. Final Governance Principles

**Architecture Integrity > Rapid Delivery**  
A quick integration that introduces a circular dependency creates a permanent tax on the entire engineering organization.

**Domain Isolation > DRY (Don't Repeat Yourself)**  
It is better to have two slightly duplicated DTOs in two separate domains than to create a massive shared kernel object that couples them together forever.

**Dependency Discipline**  
Nothing enters a domain unless the domain explicitly asks for it via an interface it controls. 

**Governance Over Shortcuts**  
No timeline pressure justifies breaking the dependency graph. The graph is the platform. Break the graph, break the ERP.
