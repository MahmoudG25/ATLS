# ATLS Platform: Monorepo Structure & Governance

> **Confidential & Proprietary**  
> **Target Audience:** Principal Architects, Engineering Leads, AI Implementation Agents  
> **Scope:** Physical Repository Architecture & Code Ownership  

---

## 1. Purpose Of Monorepo Governance

In a Domain-Driven Design (DDD) environment, **physical folder structure is architecture**. If the physical layout of the codebase does not reflect the bounded contexts of the domain, architectural integrity will erode immediately. 

Bad folder structures lead to circular dependencies, tight coupling, and "Big Ball of Mud" anti-patterns. For the ATLS enterprise agricultural ERP platform—which relies on Event-Driven Architecture, CQRS, and AI-agent-driven development—strict repository organization is mandatory. AI agents require absolute boundaries to safely generate, refactor, and review code without corrupting adjacent domains.

---

## 2. Monorepo Philosophy

*   **Bounded-Context-First:** The root directory structure maps strictly to bounded contexts, not technical layers (e.g., group by `operations`, not by `controllers` or `views`).
*   **Domain Isolation:** A domain folder is an impenetrable fortress. Its internal implementation cannot be imported directly by another domain.
*   **Vertical Slicing:** Features are sliced vertically from the API layer down to the infrastructure layer within the domain boundary.
*   **Package Ownership:** Every directory has an explicit domain owner.
*   **Infrastructure Inversion:** Infrastructure details depend on the domain, not the reverse.

> [!CAUTION]
> **Explicitly Prohibited:**  
> *   **Utility Dumping:** Creating a global `utils/` folder for random helper functions.
> *   **Shared God Folders:** Creating a global `models/` folder containing every entity in the system.
> *   **Cross-Domain Internal Imports:** Importing `apps/domains/farm/internal/models.py` from `apps/domains/operations/`.

---

## 3. Global Repository Layout

The ATLS monorepo is structured into high-level functional boundaries:

*   `apps/` - Deployable artifacts (Web, Mobile, Backend services, API Gateways).
*   `services/` - Standalone microservices or asynchronous worker pools (e.g., sync workers, analytics projectors).
*   `domains/` - The core ATLS business logic, strictly partitioned by bounded context.
*   `engines/` - Domain-agnostic runtime engines (e.g., Hierarchy, Form, Permissions).
*   `packages/` - Internal shared libraries, Shared Kernel, UI components, and infrastructure adapters.
*   `infrastructure/` - Deployment, Kubernetes manifests, and IaC (Infrastructure as Code).
*   `tools/` - CLI tooling, migration scripts, and AI-agent scaffolding utilities.
*   `docs_v2/` - Enterprise architectural governance and documentation.

---

## 4. Backend Repository Structure

The backend (enterprise Django/Python architecture) enforces strict DDD boundaries within `domains/`.

**Structure Example:**
*   `domains/farm/`
*   `domains/operations/`
*   `domains/harvest/`

**For EACH domain, the internal structure must strictly follow:**
*   `application/` - Application services orchestrating workflows, APIs, and REST/GraphQL serializers.
*   `domain/` - Aggregate Roots, Entities, Value Objects, Domain Exceptions, and Invariant Logic.
*   `infrastructure/` - ORM Models, Repository implementations, Broker adapters.
*   `contracts/` - Public DTOs and Interfaces exposed to other domains.
*   `events/` - Domain Events emitted by the aggregate (e.g., `events/outbox.py`).
*   `read_models/` - CQRS Projections and ElasticSearch serializers.

---

## 5. Frontend Repository Structure

The frontend (React/React Native) architecture mirrors the domain isolation of the backend.

**Structure Example:**
*   `apps/web/` - The primary ERP web dashboard.
*   `apps/mobile/` - The offline-first React Native mobile client.
*   `packages/shared/ui/` - Dumb, stateless UI components.
*   `packages/shared/contracts/` - API types generated from the backend.
*   `packages/shared/design-system/` - Theme tokens and styling rules.

**Rules:**
*   **Feature-Based Slicing:** Frontend code is organized by features (e.g., `features/harvest-reporting/`), not by technical layers (e.g., `components/`, `hooks/`).
*   **State Isolation:** Redux/Zustand slices are strictly scoped to their respective features.
*   **Mobile-First Organization:** Sync logic and offline cache handling are separated from UI rendering.

> [!CAUTION]
> **Explicitly Prohibited:**  
> *   Giant shared `components/` folders containing business-specific forms.
> *   Cross-feature imports (e.g., `features/farm` importing UI from `features/hr`).
> *   Business logic embedded directly inside React components.

---

## 6. Shared Kernel Rules

The Shared Kernel (`packages/shared_kernel/`) is the most dangerous area of a monorepo. It must be heavily restricted.

**Allowed in Shared Kernel:**
*   Canonical Identifiers (`UUID`, `TenantContext`).
*   Global Primitives (`Money`, `Coordinates`, `Weights`).
*   Abstract Base Domain Events.

**Explicitly Forbidden in Shared Kernel:**
*   Operations logic or task state machines.
*   Inventory calculation algorithms.
*   Reporting or projection logic.
*   Any code that imports from a specific `domain/`.

---

## 7. Domain Package Boundaries

How domains expose functionality safely without creating tight coupling:

*   **Public APIs:** Each domain exposes a strict `contracts/` or `__init__.py` file. Only elements exported here may be consumed by other domains.
*   **Internal-Only Modules:** Any file inside an `internal/` or `impl/` directory is strictly private.
*   **Anti-Corruption Layers (ACL):** When Domain A needs to translate a payload from Domain B, the ACL resides in `domains/A/infrastructure/acl/`.
*   **Integration Contracts:** Dependencies are defined as Python Protocols (interfaces). Domain A defines the Protocol, Domain B implements it.

---

## 8. Event Infrastructure Placement

Event-Driven Architecture requires strict physical placement to ensure reliability.

*   **Event Contracts:** `domains/<domain>/events/schemas/` defines the immutable event payload definitions.
*   **Outbox Infrastructure:** Generic outbox relays live in `packages/infrastructure/outbox/`. Domain-specific outbox mappers live in `domains/<domain>/infrastructure/`.
*   **Broker Adapters:** Kafka/RabbitMQ adapters reside in `packages/infrastructure/broker/`.
*   **Retry & DLQ:** Defined generically at the infrastructure package level, implemented via Celery tasks.

---

## 9. CQRS & Read Model Structure

CQRS projections are physically separated from command-side Domain aggregates.

*   **Projection Placement:** `domains/<domain>/read_models/` holds the projection handlers and ORM views.
*   **Analytics Ownership:** If a read model crosses multiple domains, it belongs to `domains/analytics/`, reading purely from domain events.
*   **Query Services:** GraphQL resolvers or REST views query the Read Models directly, bypassing the Domain Application layer entirely.

> [!WARNING]
> Projections are read-only views. **Business logic inside projections is strictly forbidden.** They are data formatting engines only.

---

## 10. Offline Synchronization Structure

Offline-first capabilities require extreme isolation to prevent corrupting the core domains.

*   **Sync Engine Location:** `engines/offline_sync/` handles payload conflict resolution, intent hashing, and queue management.
*   **Merge Handlers:** Domain-specific merge logic lives in `domains/<domain>/application/sync_handlers/`.
*   **Replay Queues:** Handled by infrastructure workers outside the core domains.
*   **Mobile Sync Contracts:** DTOs defining offline intent payloads exist in `packages/shared/contracts/sync/`.

---

## 11. Dynamic Engine Structure

Engines provide configurable, runtime logic but hold **zero domain knowledge**.

*   `engines/hierarchy/`
*   `engines/form/`
*   `engines/theme/`
*   `engines/permission/`
*   `engines/dashboard/`

**Requirement:** An engine must be completely oblivious to the ERP. The Form engine knows what a "Dropdown" is; it does NOT know what a "Crop Cultivar" is.

---

## 12. AI Agent Repository Governance

> [!CAUTION]
> **ENHANCED AI-AGENT RULES**  
> AI agents parsing or generating code in this repository MUST obey strict boundaries.

*   **AI-Safe Folder Boundaries:** Agents instructed to modify the "Harvest" domain are explicitly blocked from modifying files in `domains/operations/`.
*   **Protected Directories:** `/packages/shared_kernel/` and `/engines/` require explicit Principal Architect approval for any AI modification.
*   **Mandatory Architecture Validation:** AI agents must run dependency linting (e.g., `import-linter`) before finalizing any code block.
*   **Automatic Rejection:** Any AI-generated PR that introduces a cross-domain import into an `internal/` directory, dumps logic into a generic `utils/` folder, or bypasses the `contracts/` layer will be automatically rejected.

---

## 13. Testing Architecture Structure

Testing mirrors the vertical slicing of the repository.

*   **Unit Tests:** Live directly adjacent to the code they test (e.g., `domains/farm/domain/tests/`).
*   **Integration Tests:** Live in `domains/<domain>/application/tests/`, interacting with the database.
*   **Contract Tests:** Live in `packages/shared/contracts/tests/` to verify API shapes between frontend and backend.
*   **Event Tests:** Verify payload immutability and outbox emission.
*   **Offline Sync Tests:** Simulate intermittent connectivity and LWW (Last-Write-Wins) conflicts in `engines/offline_sync/tests/`.

---

## 14. Infrastructure Layer Structure

The system must remain infrastructure-agnostic.

*   **Adapters:** `packages/infrastructure/postgres/`, `packages/infrastructure/redis/`.
*   **External APIs:** `packages/infrastructure/weather_api/`, `packages/infrastructure/erp_connector/`.
*   **Replaceability:** The core domains interact with infrastructure strictly through interfaces. Swapping Postgres for another SQL dialect should only require changes inside `packages/infrastructure/`.

---

## 15. Monorepo Anti-Patterns

If these patterns appear in the physical file structure, the architecture has failed:

*   **Shared Utils Graveyard:** A global `utils/helpers.py` containing timezone logic, string parsers, and tax calculators.
*   **Giant Common Folder:** `frontend/src/common/` that grows to contain 80% of the UI components.
*   **Frontend Importing Backend Internals:** The React app directly importing Python enums or backend ORM definitions instead of relying on generated `contracts/`.
*   **Direct ORM Usage in UI Services:** A REST view ignoring the Application Service and importing `models.py` directly.
*   **Circular Package References:** Package A `package.json` depends on Package B, which depends on Package A.

---

## 16. Future Extraction Strategy

This strict monorepo structure guarantees that the ATLS platform is ready for future microservice extraction.

Because domains are strictly isolated, communicate via events, and share no database models, extracting the `Inventory` domain into a standalone microservice requires only:
1. Moving `domains/inventory/` to a new repository.
2. Swapping the internal Application Service calls with HTTP/gRPC API clients.
3. Keeping the Event Contracts (`packages/shared/contracts/`) identical.

---

## 17. Final Repository Governance Principles

**Structure Integrity Over Developer Convenience**  
It is always easier to drop a helper function into a global `utils.py`. Doing so creates a dependency tangle that destroys system scalability. Put code where it belongs, not where it is easiest.

**Bounded Contexts Are Physical Laws**  
A bounded context is not just a theoretical DDD concept; it is a physical folder boundary. Treat cross-folder imports with the same scrutiny as an external HTTP API call.

**Scalability Through Isolation**  
The platform will only scale to millions of synced operations if domains can evolve independently. The physical repository structure is the ultimate enforcer of that independence.

**AI-Safe Architecture**  
A predictable, highly-structured repository is the only way to allow AI coding agents to operate autonomously without introducing catastrophic architectural regressions.
