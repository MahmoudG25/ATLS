# Phase 01: Core Foundation & Bedrock

| Metadata | Details |
| :--- | :--- |
| **Document ID** | ATLS-EXE-P01 |
| **Status** | AUTHORITATIVE |
| **Version** | 2.0.0 |
| **Owner** | Foundation & DevOps Team |
| **Applicability** | Initial Project Setup & Infrastructure |

## 1. Phase Vision
Phase 01 establishes the **Architectural Bedrock** of the ATLS platform. The goal is to move from "Design" to "Infrastructure," ensuring that every subsequent domain module is built upon a secure, multi-tenant, and mobile-ready foundation.

## 2. Strategic Goals
- **Isolation**: 100% verified tenant data partitioning.
- **Security**: Robust JWT-based authentication and RBAC foundation.
- **Developer Velocity**: Automated CI/CD and standardized development workflows.
- **Mobile Readiness**: Offline-first architecture and design system initialized.

## 3. Scope Definition
This phase covers the technical infrastructure, monorepo configuration, and core services. No business domain logic (e.g., Harvest, Inventory) is implemented during this phase.

## 4. Monorepo Setup
- Structure:
    - `/apps/backend`: Django Modular Monolith.
    - `/apps/frontend`: React + Vite PWA.
    - `/docs_v2`: Authoritative documentation.
    - `/infra`: Docker, Terraform, and K8s configs.

## 5. Backend Bootstrap
- Django 4.2+ (LTS).
- Django REST Framework (DRF).
- Folder structure following [DJANGO_STRUCTURE.md].
- UUIDv7 as the primary key standard.

## 6. Frontend Bootstrap
- React 18+ with Vite.
- TypeScript (Strict mode).
- Folder structure following [COMPONENT_GUIDELINES.md].

## 7. PostgreSQL Setup
- Schema design for `Tenants` and `Users`.
- Global `TenantManager` initialization.
- Connection pooling configuration (pgBouncer).

## 8. Redis & Celery Setup
- Redis as the primary message broker and cache.
- Celery worker initialization for async task processing.
- Dead Letter Queue (DLQ) configuration.

## 9. Authentication Setup
- SimpleJWT for token-based auth.
- Login, Refresh, and Logout endpoints.
- User profile base model.

## 10. Tenant Isolation Setup
- Mandatory `tenant_id` on all shared models.
- Middleware to inject `request.tenant` into the execution context.
- Manager-level filtering to prevent cross-tenant data leakage.

## 11. Shared UI Foundation
- Design Tokens (Colors, Typography, Spacing).
- Basic Layout components (Sidebar, Navbar, Mobile Bottom-Nav).

## 12. Tailwind & shadcn Setup
- Standard Tailwind configuration.
- Integration of shadcn/ui primitives.
- RTL-native layout utilities.

## 13. Design Token Setup
- Integration of `DESIGN_SYSTEM.md` tokens into CSS variables.
- Support for Light/Dark modes from day one.

## 14. Routing Setup
- React Router (v6+).
- Protected Routes (Auth-guarded).
- Tenant-scoped route structures.

## 15. State Management Setup
- Zustand for global client-side state.
- Atomic stores (AuthStore, UIStore, TenantStore).

## 16. API Client Setup
- Axios instance with interceptors for JWT injection and 401 handling.
- Standardized error response handling.

## 17. Offline Foundation Setup
- IndexedDB initialization (using `idb` library).
- Service Worker baseline for PWA functionality.
- Sync Queue for offline data persistence.

## 18. Docker Environment
- `docker-compose.yml` for local development (DB, Redis, Celery, Backend, Frontend).
- Multi-stage Dockerfiles for production builds.

## 19. CI/CD Bootstrap
- GitHub Actions / GitLab CI pipeline.
- Stages: `Lint -> Test -> Build -> Deploy (Staging)`.

## 20. Logging Setup
- Structured JSON logging for backend.
- Centralized log aggregation foundation.

## 21. Error Monitoring Setup
- Sentry integration (Frontend & Backend).
- Error boundary implementation in React.

## 22. Initial Testing Setup
- Pytest for Backend (Unit & Integration).
- Vitest for Frontend (Unit & Component).
- Playwright for E2E baseline.

## 23. Developer Workflow Setup
- Pre-commit hooks (Black, Isort, ESLint, Prettier).
- Standardized `Makefile` or `npm scripts` for common tasks.

## 24. AI Workflow Integration
- Configuration of [AI_TASK_TEMPLATE.md] and [AI_WORKFLOW.md] in the repository.
- Baseline PR template for AI-generated code.

## 25. Deliverables
- Functional Monorepo.
- Authenticated Login/Logout flow.
- Verified Tenant Isolation (Automated test).
- Working PWA shell.
- Automated CI/CD pipeline.

## 26. Risks
- **Tenant Leakage**: High risk; mitigated by strict automated isolation testing.
- **CI/CD Complexity**: Mitigated by starting with a minimal, robust pipeline.
- **Offline Sync Conflicts**: Mitigated by establishing sync rules early.

## 27. Validation Criteria
- [ ] `tenant_id` filter cannot be bypassed in domain queries.
- [ ] JWT tokens are encrypted and non-reusable after logout.
- [ ] Frontend bundle is < 200KB (Gzipped) baseline.
- [ ] All tests pass in the CI/CD pipeline.

## 28. Done Definition
- Code is merged to `main`.
- Infrastructure is deployed to Staging.
- All Phase 01 tasks in `task.md` are checked.
- Architecture docs updated with implementation details.

## 29. Agricultural Constraints
- **Connectivity**: Baseline must support 100% offline navigation.
- **Simplicity**: UI foundation must support high-contrast display for field use.

## 30. Final Phase Checklist
- [ ] Monorepo structure finalized.
- [ ] Docker environment operational.
- [ ] Tenant isolation verified.
- [ ] JWT Auth active.
- [ ] Design system tokens integrated.
- [ ] Offline sync foundation active.
- [ ] CI/CD pipeline green.
- [ ] Developer workflow documented.
