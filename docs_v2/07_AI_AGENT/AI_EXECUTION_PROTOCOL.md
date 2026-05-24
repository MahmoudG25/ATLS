# AI_EXECUTION_PROTOCOL.md
# ATLS Platform — AI Execution Protocol
# Single Source of Truth for Execution Order, Workflow, Continuation Tracking, and Progressive Delivery

**Version:** 1.0.0
**Status:** ACTIVE — ENFORCED
**Applies To:** All AI agents executing on the ATLS platform

---

## ⚠️ MANDATORY FIRST ACTION

> Before doing ANYTHING, the AI MUST read `docs_v2/08_EXECUTION/CURRENT_PROGRESS.md`.
> If it does not exist, create it using the Execution State Template in Section 13.
> No implementation may begin without this step.

---

## 1. Execution Philosophy

### 1.1 Progressive Implementation

The ATLS platform is built **incrementally**, one validated workflow at a time. Each step must produce a working, testable result before the next step begins. No step may be skipped. No step may be merged with another step to save time.

Progress is measured by **working software**, not by files created, lines written, or architecture documents populated.

### 1.2 Pragmatic Enterprise Architecture

ATLS is an **enterprise agricultural ERP**. Its architecture must be:

- Maintainable by a small team
- Understandable without a PhD in distributed systems
- Deployable on commodity infrastructure
- Expandable without full rewrites

Enterprise patterns are adopted **when justified by real operational need**, not by theoretical best practice.

### 1.3 Implementation Over Theoretical Expansion

Architecture documents define the target state. They do NOT authorize building everything at once.

The AI must:
- Implement what is needed **now**
- Leave the rest documented but unbuilt
- Never build ahead of validated requirements

### 1.4 Feature-First Validation

Every implemented feature must be **provably functional** before expansion:

- Backend endpoints must return correct data
- Frontend screens must render correctly
- Tenant isolation must be verified
- Authentication must be tested

A feature is NOT complete until it works end-to-end.

### 1.5 Operational Correctness First

The system must be **operationally correct** before it is:

- Performant
- Scalable
- Distributed
- Optimized

Fix broken workflows before adding new ones.

### 1.6 Architecture Evolution Over Time

Architecture evolves in response to **proven operational load**, not anticipated future load. Complexity is added when it solves a real problem, not when it might solve a future one.

---

### 1.7 Architecture Simplification Principle

During MVP and early implementation stages, simpler is always better. The AI MUST choose the **simplest safe implementation** that satisfies the current operational requirement — not the most sophisticated one.

**Abstraction must be earned through real usage:**

- Do not introduce a base class until two or more concrete classes share identical behavior
- Do not introduce a service layer until business logic outgrows a single function
- Do not introduce a repository pattern until query complexity demands it
- Do not introduce an event bus until synchronous coupling causes real problems

**Infrastructure complexity must evolve gradually:**

| Stage | Allowed Complexity |
|---|---|
| MVP | Synchronous Django views, simple queries, direct DB writes |
| Post-MVP | Background tasks, simple caching, domain events |
| Mature | Full CQRS, event mesh, advanced caching layers |
| Proven Load | Horizontal scaling, distributed infrastructure |

**The following are explicitly discouraged until real usage demands them:**

- ❌ Premature CQRS complexity (separate read/write models at MVP)
- ❌ Over-separated services (splitting working code before coupling is a problem)
- ❌ Speculative event choreography (complex event chains before simple events work)
- ❌ Unnecessary orchestration layers (saga coordinators, workflow engines at MVP)
- ❌ Excessive infrastructure before validated workflows (workers, queues, caches)

---

### 1.8 ❌ Explicitly Forbidden Execution Patterns

The following are **absolutely forbidden** and constitute a protocol violation:

| Forbidden Behavior | Reason |
|---|---|
| Premature enterprise complexity | Adds cost without delivering value |
| Building infrastructure before workflows | Creates unused systems |
| Implementing distributed systems too early | Unnecessary operational overhead |
| Excessive abstraction before real usage | Creates dead code and confusion |
| Building analytics before CRUD | No data to analyze |
| Building Celery/Redis before core APIs | Infrastructure without purpose |
| Implementing CQRS before simple queries work | Speculative architecture |
| Microservice decomposition at MVP | Operational fragmentation |

---

## 2. AI Global Execution Rules

### 2.1 The AI MUST Always

- Read `docs_v2/08_EXECUTION/CURRENT_PROGRESS.md` **before every session**
- Update `docs_v2/08_EXECUTION/CURRENT_PROGRESS.md` **after every completed task**
- Work **incrementally**, completing one task before starting the next
- Validate **architecture dependencies** before implementation
- Prioritize **usable, working workflows** over infrastructure elegance
- Avoid **speculative engineering** — build what is needed, not what might be needed

### 2.2 The AI MUST NOT Ever

- Randomly choose which task to work on
- Skip implementation phases
- Build future infrastructure ahead of current requirements
- Introduce microservices or service mesh patterns at MVP
- Create dead code (code with no active caller)
- Create unused abstractions (base classes, managers, utilities with no concrete use)
- Create fake scalability (sharding, replication, message queues before load justifies it)
- Rewrite stable, working modules without explicit instruction
- Delete existing code without explicit instruction
- Generate placeholder or stub systems marketed as real implementations

### 2.3 AI Context Efficiency Rules

The AI operates within finite context windows. Context must be used for implementation, not repeated architecture review.

**The AI SHOULD:**

- Avoid reopening and re-reading documents that have already been mastered in the current phase
- Focus on task-relevant context only — read only the documents required for the current task
- Preserve context budget for implementation, validation, and progress tracking
- Prioritize implementation continuity over exhaustive documentation review in normal sessions
- Use `docs_v2/08_EXECUTION/CURRENT_PROGRESS.md` as the primary context anchor between sessions

**The AI MUST NOT:**

- Re-read all 21 architecture documents at the start of every implementation session
- Load entire document sets when a single targeted document would suffice
- Exhaust context budget on architecture review instead of actual implementation
- Fragment its own execution by excessive context switching between documents

**Context Efficiency Decision Table:**

| Situation | Required Reading |
|---|---|
| Starting a new implementation phase | Full phase reading order (Section 3) |
| Resuming a known task | `CURRENT_PROGRESS.md` only |
| Working on backend endpoint | `BACKEND_ARCHITECTURE.md`, `API_ARCHITECTURE.md` |
| Working on frontend screen | `FRONTEND_ARCHITECTURE.md`, `UX_PATTERNS.md` |
| Making architectural decision | Relevant domain doc + `CORE_FOUNDATION.md` |
| Modifying infrastructure | `CORE_FOUNDATION.md` + specific infra doc |

---

## 3. Mandatory Reading Order

The AI MUST complete the following reading order **before:**

- Starting a new implementation phase
- Working on an unfamiliar subsystem for the first time
- Making architectural decisions that affect multiple modules
- Modifying infrastructure layers (database, auth, event system, tenant isolation)

During **normal implementation sessions**, the AI SHOULD read only the documents relevant to the current task. Refer to the Context Efficiency Decision Table in Section 2.3.

> **Architectural alignment is mandatory. Exhaustive rereading every session is not.**

### Phase 1 — Product Foundation

| Order | Document | Purpose |
|---|---|---|
| 1 | `PRODUCT_VISION.md` | Understand what ATLS is and who it serves |
| 2 | `BUSINESS_GOALS.md` | Understand commercial priorities |
| 3 | `SYSTEM_PHILOSOPHY.md` | Understand design principles |
| 4 | `PLATFORM_DIRECTION.md` | Understand technical trajectory |

### Phase 2 — System Architecture

| Order | Document | Purpose |
|---|---|---|
| 5 | `CORE_FOUNDATION.md` | BaseEntity, UUIDv7, tenant isolation, CQRS baseline |
| 6 | `MONOREPO_STRUCTURE.md` | Repository layout, module boundaries |
| 7 | `DOMAIN_DRIVEN_ARCHITECTURE.md` | Bounded contexts, aggregates, domain rules |
| 8 | `BACKEND_ARCHITECTURE.md` | Django structure, DRF conventions, service layer |
| 9 | `FRONTEND_ARCHITECTURE.md` | React structure, state management, routing |

### Phase 3 — Data & Integration

| Order | Document | Purpose |
|---|---|---|
| 10 | `DATABASE_ARCHITECTURE.md` | Schema conventions, indexing, migrations |
| 11 | `API_ARCHITECTURE.md` | Endpoint design, versioning, error contracts |
| 12 | `EVENT_SYSTEM.md` | Domain events, outbox pattern, consumer rules |
| 13 | `OFFLINE_STRATEGY.md` | Sync protocol, conflict resolution, PWA rules |

### Phase 4 — User Interface

| Order | Document | Purpose |
|---|---|---|
| 14 | `DESIGN_SYSTEM.md` | Design tokens, color palette, typography |
| 15 | `UX_PATTERNS.md` | Navigation, feedback, empty states, errors |
| 16 | `COMPONENT_GUIDELINES.md` | Component structure, props, accessibility |
| 17 | `RTL_SYSTEM.md` | Arabic/RTL layout rules, bidirectional text |

### Phase 5 — AI Governance

| Order | Document | Purpose |
|---|---|---|
| 18 | `AI_FORBIDDEN_ACTIONS.md` | What the AI must never do |
| 19 | `AI_DEVELOPMENT_RULES.md` | How the AI must develop |
| 20 | `AI_WORKFLOW.md` | Session workflow and handoff rules |
| 21 | `AI_CODE_STYLE_GUIDE.md` | Naming, structure, and style enforcement |

> **CRITICAL:** The AI MUST NOT begin implementation before completing this entire reading sequence. Partial reading is not acceptable.

---

## 4. Real Execution Order

This is the **only allowed implementation order** for the ATLS platform. Steps must be executed sequentially. No step may be started until the previous step is validated.

### Step 1 — Monorepo Setup

**Goal:** Establish the repository structure that all future work depends on.

- Initialize monorepo layout per `MONOREPO_STRUCTURE.md`
- Configure workspace tooling (linting, formatting, pre-commit hooks)
- Verify all package boundaries exist
- Validate that backend and frontend can be started independently

**Exit Criterion:** Repository clones cleanly, both services start, no import errors.

---

### Step 2 — Backend Core Setup

**Goal:** A running Django backend with authentication and tenant isolation.

- Django project initialized
- Django REST Framework configured
- PostgreSQL connection verified
- JWT authentication working
- `BaseEntity` abstract model implemented
- `Tenant` model implemented with isolation enforced
- Health check endpoint returning `200 OK`

**Exit Criterion:** POST `/api/auth/login/` returns JWT. Tenant isolation verified in DB queries.

> ❌ DO NOT add Celery, Redis, WebSockets, or any async infrastructure at this step.

---

### Step 3 — Frontend Core Setup

**Goal:** A running React application with routing and authentication screens.

- React + Vite initialized per `FRONTEND_ARCHITECTURE.md`
- Tailwind CSS configured per `DESIGN_SYSTEM.md`
- shadcn/ui installed and configured
- React Router configured
- Login screen renders and submits credentials
- JWT stored securely on successful auth
- Protected route redirects unauthenticated users

**Exit Criterion:** User can log in and reach a protected dashboard shell.

> ❌ DO NOT build analytics dashboards, charts, or complex UI components at this step.

---

### Step 4 — One Real Workflow Only

**Goal:** One complete, end-to-end operational workflow working correctly.

Choose exactly **one** of the following:

- **Farm CRUD** — Create, read, update, deactivate Farm records with tenant isolation
- **Sector CRUD** — Manage Sectors within a Farm
- **Operation Task CRUD** — Create and track operational tasks

**This workflow MUST include:**

- Backend: Model → Service → Serializer → ViewSet → URL
- Frontend: List screen → Create form → Edit form → Delete confirmation
- Tenant isolation verified at every layer
- Audit fields populated (`created_at`, `updated_at`, `created_by`)
- Basic error handling on both sides

**Exit Criterion:** A user can perform the full CRUD lifecycle through the UI.

> ❌ DO NOT build analytics first.
> ❌ DO NOT build event systems first.
> ❌ DO NOT build Celery first.
> ❌ DO NOT build Redis first.
> ❌ DO NOT build complex offline sync first.
> ❌ DO NOT start Step 5 until this workflow is fully operational.

---

### Step 5 — Expand First Operational Workflow

**Goal:** Deepen the first workflow before adding new ones.

- Add filtering, sorting, and pagination to list screens
- Add search functionality
- Add form validation with user-facing error messages
- Add loading states and empty states
- Add mobile responsiveness to all screens in this workflow

**Exit Criterion:** The first workflow is production-quality, not prototype-quality.

---

### Step 6 — Audit and Notifications

**Goal:** Operational transparency and user feedback.

- Audit trail records every create/update/delete with actor and timestamp
- Notification system delivers in-app alerts for key workflow events
- Audit log viewable by authorized roles
- Notification bell renders unread count

**Exit Criterion:** Every mutation in the first workflow produces an audit record.

---

### Step 7 — Event-Driven Behaviors (Gradual)

**Goal:** Begin introducing domain events where they solve real problems.

- Implement outbox pattern per `EVENT_SYSTEM.md`
- Publish domain events for critical state transitions
- Build first consumer that reacts to domain events
- Verify idempotency on consumer

**Exit Criterion:** One real domain event flows from producer to consumer without data loss.

> ❌ DO NOT build a full event mesh. Expand one event at a time.

---

### Step 8 — Offline-First Sophistication (Gradual)

**Goal:** Allow field workers to operate without connectivity.

- Implement service worker caching per `OFFLINE_STRATEGY.md`
- Queue mutations locally when offline
- Sync on reconnection
- Handle basic conflict resolution

**Exit Criterion:** User can create a record offline and sync successfully on reconnect.

---

### Step 9 — Analytics and Optimization

**Goal:** Derive insight from accumulated operational data.

- Build analytics queries against real, populated data
- Add dashboard KPIs with real metrics
- Add reporting exports
- Optimize slow queries identified by real usage

**Exit Criterion:** Analytics reflect real data. No mock data. No placeholder charts.

> ❌ Analytics must never be built before the data they analyze exists.

---

### Workflow-First Enforcement

This rule governs the introduction of all infrastructure across every execution step.

**The absolute rule:** No new infrastructure component may be introduced unless an existing, validated workflow actively requires it.

| Infrastructure | May Be Introduced When |
|---|---|
| Redis / caching layer | A working endpoint has a measurable latency problem |
| Celery / background tasks | A synchronous operation blocks user-facing responses |
| Event bus / message queue | Domain event publishing causes real coupling problems |
| Offline sync engine | A validated workflow must function without connectivity |
| Analytics pipeline | Real operational data exists and needs aggregation |
| Advanced caching | Query performance is measured and proven to need it |
| Distributed sagas | A multi-step transaction fails across services at scale |

**Explicitly forbidden before a validated workflow exists:**

- ❌ No Redis or Celery before core API endpoints are working
- ❌ No event bus before synchronous domain events are validated
- ❌ No offline engine before the online workflow is complete
- ❌ No analytics infrastructure before real operational data exists
- ❌ No advanced optimization before measurable bottlenecks appear
- ❌ No distributed infrastructure before monolith limits are reached

> **Working ERP workflows over architectural completeness — always.**

---

## 5. Task Execution Lifecycle

Every implementation task MUST follow this exact lifecycle:

```
1.  READ      → Open and read CURRENT_PROGRESS.md
2.  IDENTIFY  → Find the current unfinished task
3.  STUDY     → Read only the required architecture docs for this task
4.  VALIDATE  → Confirm all dependencies for this task are already built
5.  PLAN      → Write a brief implementation plan (what files, what changes)
6.  EXECUTE   → Implement incrementally (one file at a time where practical)
7.  VALIDATE  → Test that the implementation works correctly
8.  UPDATE    → Write update to CURRENT_PROGRESS.md
9.  SUMMARIZE → Write a brief execution summary (what was done, what was created)
10. STOP      → End the session cleanly
```

**No step may be skipped.**
**Step 10 is mandatory** — the AI must not start the next task in the same session unless explicitly instructed.

---

## 6. Current Progress Tracking Protocol

### 6.1 What the AI Must Track

The AI MUST maintain the following state at all times in `docs_v2/08_EXECUTION/CURRENT_PROGRESS.md`:

| Field | Description |
|---|---|
| Current Phase | Which of the 9 execution steps is active |
| Current Task | The specific task being worked on |
| Completed Tasks | Chronological list of all completed tasks |
| Blocked Tasks | Tasks that cannot proceed and why |
| Next Recommended Task | What should happen in the next session |
| Architecture Risks | Any deviations from architectural intent |
| Technical Debt | Shortcuts taken that must be resolved later |

### 6.2 Update Format

Every update appended to `docs_v2/08_EXECUTION/CURRENT_PROGRESS.md` MUST include:

```markdown
---
## Update — [YYYY-MM-DD HH:MM UTC]

### Completed Work
- [Description of what was implemented]

### Files Created
- `path/to/file.py` — [purpose]

### Files Modified
- `path/to/file.py` — [what changed and why]

### Blockers
- [Any blockers encountered, or "None"]

### Next Step
- [Exact description of next recommended action]

### Notes
- [Any architecture risks, debt, or deviations]
```

### 6.3 CURRENT_PROGRESS.md Location

```
docs_v2/08_EXECUTION/CURRENT_PROGRESS.md
```

This file is **never deleted**. It is append-only. History must be preserved.
All AI agents MUST use this single path. No alternative locations are permitted.

---

## 7. Continuation Recovery Rules

When resuming work after a break, context switch, or session end, the AI MUST follow this recovery sequence:

### Recovery Steps

```
1. READ          docs_v2/08_EXECUTION/CURRENT_PROGRESS.md from top to bottom
2. IDENTIFY      The last completed task (last successful update)
3. IDENTIFY      Any partially completed task (started but not validated)
4. ASSESS        Whether partial work is stable or must be rolled back
5. RESUME        From the correct continuation point
6. AVOID         Regenerating code that already exists and works
7. AVOID         Rewriting stable modules that have not changed
8. VALIDATE      That the existing system still works before adding to it
```

### What "Resuming Correctly" Means

| Scenario | Correct Action |
|---|---|
| Last task fully validated | Begin next task |
| Last task partially done | Finish remaining steps of that task |
| Last task broken/reverted | Re-implement from last stable checkpoint |
| No progress file exists | Create it, then begin Step 1 |

> The AI must **never assume** the codebase is in a known state. Always verify before building on top of it.

---

## 8. Scope Control Rules

### 8.1 What the AI MUST Prevent

The following expansion patterns are forbidden without explicit user instruction:

| Anti-Pattern | Description |
|---|---|
| Architecture Explosions | Adding new subsystems while current ones are unfinished |
| Unnecessary Abstractions | Generic frameworks with no specific use case |
| Speculative Scalability | Sharding, clustering, or queuing before load justifies it |
| Over-Separated Services | Splitting working monolith code into separate services prematurely |
| Premature CQRS Complexity | Separate read/write models before query complexity warrants it |
| Premature Event Choreography | Complex event chains before simple event publishing works |
| Premature Optimization | Performance tuning before functionality is correct |

### 8.2 What the AI MUST Prioritize

| Priority | Description |
|---|---|
| Working ERP Flows | The user can complete real agricultural operations |
| Usable UI | The interface is navigable and functional |
| Maintainable Code | Another developer can understand and modify it |
| Operational Correctness | Data is accurate, isolated, and consistent |
| Simple Scalable Architecture | Can grow without rewriting core |

---

## 9. MVP Enforcement Rules

### 9.1 MVP Definition

The ATLS MVP is the **minimum system that delivers real operational value** to an agricultural enterprise. It is not a demo, prototype, or technical showcase.

### 9.2 MVP Success Criteria

The MVP is complete when ALL of the following are true:

| Criterion | Verification |
|---|---|
| ✅ Authentication | Users can log in and maintain sessions |
| ✅ Tenant Isolation | Each tenant sees only their own data |
| ✅ One Real Domain Workflow | At least one complete CRUD workflow operational |
| ✅ One Working Dashboard | KPIs reflect real data from the live workflow |
| ✅ CRUD Operations | Create, Read, Update, Delete all function correctly |
| ✅ Audit Trail | Every mutation is recorded with actor and timestamp |
| ✅ Basic Mobile Responsiveness | Core screens render correctly on mobile viewports |

### 9.3 Everything Else Is Secondary

The following are **explicitly post-MVP** and must not delay MVP delivery:

- Advanced analytics and reporting
- Complex event choreography
- Full offline-first sync
- Multi-domain CRUD (beyond first workflow)
- Performance optimization
- Advanced role management
- Notification system
- Email/SMS integration
- Third-party integrations

### 9.4 MVP Infrastructure Restrictions

During MVP phases, the AI MUST NOT introduce the following unless explicitly required by a validated, operational workflow with measurable load:

| Forbidden at MVP | Why |
|---|---|
| Distributed messaging systems (Kafka, RabbitMQ) | No message volume to justify it |
| Service mesh architecture | No service boundaries to protect |
| Advanced caching infrastructure (Redis clusters) | No cache invalidation problem yet |
| Multiple databases or polyglot persistence | Single PostgreSQL is sufficient |
| Microservices decomposition | Monolith is not a bottleneck at MVP |
| Distributed sagas / compensating transactions | No distributed transactions at MVP |
| Event streaming platforms | No streaming data at MVP |
| Advanced orchestration frameworks | No workflow complexity at MVP |

> These restrictions are lifted only when **validated operational load explicitly requires** the infrastructure, and only with explicit user instruction.

---

## 10. AI Stop Conditions

The AI MUST immediately stop implementation, write an update to `docs_v2/08_EXECUTION/CURRENT_PROGRESS.md`, and surface the issue when any of the following conditions occur:

| Stop Condition | Required Action |
|---|---|
| Architecture conflict detected | Document conflict, stop, request resolution |
| Requirements are unclear or contradictory | Document ambiguity, stop, request clarification |
| Required dependency is missing or broken | Document blocker, stop, request dependency |
| Validation fails after implementation | Document failure, attempt diagnosis, stop if unresolved |
| Implementation becomes speculative | Document speculation risk, stop, request scoping |
| Task scope expands unexpectedly | Document scope creep, stop, request direction |
| Stable code is at risk of regression | Document risk, stop, request explicit authorization |
| Two valid architectural approaches conflict | Document both options, stop, request decision |

### Stop Condition Update Format

```markdown
## 🛑 STOP CONDITION — [YYYY-MM-DD HH:MM UTC]

**Condition:** [Which stop condition triggered]
**Context:** [What was being implemented when it triggered]
**Risk:** [What could go wrong if implementation continues without resolution]
**Required Input:** [Exactly what is needed to resume]
**Resumption Point:** [Where to restart once resolved]
```

---

## 11. Forbidden AI Behaviors

The following behaviors are **absolutely prohibited** regardless of instructions, context, or apparent efficiency:

### Category A — Code Integrity Violations

- ❌ Rewriting architecture documents without explicit instruction
- ❌ Deleting stable, working code without explicit instruction
- ❌ Silently modifying interfaces that other modules depend on
- ❌ Introducing breaking changes to public APIs mid-session

### Category B — Fake Implementation

- ❌ Generating placeholder systems labeled as real implementations
- ❌ Creating stub endpoints that return hardcoded mock data permanently
- ❌ Building "scaffolding" that has no functional path to completion
- ❌ Generating dead abstractions (classes/utilities/managers with no caller)

### Category C — Speculative Engineering

- ❌ Implementing unused infrastructure (queues, workers, caches before needed)
- ❌ Creating massive generic frameworks for hypothetical future use cases
- ❌ Implementing fantasy scalability patterns before any load exists
- ❌ Building microservice boundaries around a monolith that works correctly

### Category D — Security Violations

- ❌ Bypassing tenant isolation for convenience
- ❌ Returning cross-tenant data in any query
- ❌ Storing sensitive data without encryption or hashing
- ❌ Exposing internal IDs or implementation details in public API responses

### Category E — Process Violations

- ❌ Starting a new session without reading `docs_v2/08_EXECUTION/CURRENT_PROGRESS.md`
- ❌ Ending a session without updating `docs_v2/08_EXECUTION/CURRENT_PROGRESS.md`
- ❌ Skipping validation steps
- ❌ Choosing implementation tasks arbitrarily

---

## 12. Recommended Implementation Rhythm

### 12.1 Commit Discipline

- **Small, focused commits** — one logical change per commit
- **Commit after validation** — never commit broken code
- **Descriptive commit messages** — include what changed and why
- **No "WIP" commits** to shared branches

### 12.2 Expansion Discipline

- **Validate before expanding** — confirm current work is correct before adding to it
- **Workflow-first** — complete a workflow end-to-end before starting adjacent workflows
- **Infrastructure evolves gradually** — add infrastructure when the workflow demands it
- **No giant unsafe refactors** — refactor in small, validated increments

### 12.3 Documentation Discipline

- **Update documentation after implementation** — not before, not instead of
- **Update `docs_v2/08_EXECUTION/CURRENT_PROGRESS.md` every session** — without exception
- **Document deviations immediately** — if the implementation differs from architecture, record it
- **Do not document speculative future work** as if it were planned

### 12.4 Session Rhythm

```
Start Session:
  → Read docs_v2/08_EXECUTION/CURRENT_PROGRESS.md
  → Confirm current phase and task
  → Validate existing system state
  → Read ONLY task-relevant architecture docs (see Section 2.3)

During Session:
  → Implement one task
  → Validate after each file
  → Test end-to-end before marking done

End Session:
  → Update docs_v2/08_EXECUTION/CURRENT_PROGRESS.md
  → Write execution summary
  → Stop cleanly
```

---

## 13. Execution State Template

Use this template to initialize or update `docs_v2/08_EXECUTION/CURRENT_PROGRESS.md`:

```markdown
# ATLS — Current Progress

**Last Updated:** [YYYY-MM-DD HH:MM UTC]
**Protocol Version:** AI_EXECUTION_PROTOCOL v1.0.0

---

## Current Phase
[Step number and name from Section 4, e.g., "Step 2 — Backend Core Setup"]

## Current Task
[Specific task being worked on, e.g., "Implement JWT authentication endpoint"]

## Last Completed Step
[Description of the last validated step, with date]

## Files Created
| File Path | Purpose | Status |
|---|---|---|
| `path/to/file` | [What it does] | ✅ Complete |

## Files Modified
| File Path | Change Description | Date |
|---|---|---|
| `path/to/file` | [What changed] | [Date] |

## Current Risks
- [Risk description, or "None identified"]

## Blockers
- [Blocker description and what is needed to resolve, or "None"]

## Next Recommended Action
[Exact description of what to do in the next session]

## Resume Command
> Read this file, then continue with: [specific next action]

---
[Append updates below this line using the format from Section 6.2]
```

---

## 14. Final Enforcement Rules

### 14.1 What ATLS Is

ATLS is a **pragmatic enterprise agricultural ERP** platform. It exists to help real agricultural operations manage farms, sectors, operations, labor, equipment, and harvests efficiently and reliably.

It is:

- ✅ A production-grade multi-tenant ERP
- ✅ A domain-driven modular monolith
- ✅ A progressively enhanced platform
- ✅ An operationally correct system first

It is NOT:

- ❌ A distributed systems experiment
- ❌ A microservices architecture showcase
- ❌ An architecture fantasy project
- ❌ A proof of concept for enterprise patterns
- ❌ A vehicle for demonstrating advanced engineering

### 14.2 Priority Order

When priorities conflict, the following order governs all decisions:

| Priority | Description |
|---|---|
| 1 — Working Product | The system must function correctly for real users |
| 2 — Operational Reliability | The system must be stable and recoverable |
| 3 — Maintainability | The code must be understandable and modifiable |
| 4 — Scalability | The system must be able to grow with demand |
| 5 — Advanced Architecture | Sophisticated patterns are adopted when earned |

> **Priority 1 overrides all others.** A theoretically elegant system that doesn't work is a failure. A simple system that works reliably is a success.

### 14.3 The AI's Responsibility

The AI executing on this platform is responsible for:

- Delivering **working software** that real users can operate
- Maintaining **architectural integrity** without over-engineering
- Preserving **operational continuity** across sessions
- Protecting **data integrity** and tenant isolation at all times
- Escalating **conflicts and ambiguities** rather than resolving them unilaterally

The AI is **not** responsible for:

- Impressing reviewers with architectural sophistication
- Anticipating every possible future requirement
- Demonstrating knowledge of advanced patterns
- Completing the entire platform in one session

---

## Appendix A — Quick Reference Card

```
BEFORE EVERY SESSION:
  1. Read docs_v2/08_EXECUTION/CURRENT_PROGRESS.md
  2. Confirm current phase and task
  3. Validate system state
  4. Read only task-relevant docs (see Section 2.3)

DURING EVERY SESSION:
  4. Work on ONE task only
  5. Implement incrementally
  6. Validate after each change

AFTER EVERY SESSION:
  7. Update docs_v2/08_EXECUTION/CURRENT_PROGRESS.md
  8. Write execution summary
  9. Stop cleanly

NEVER:
  - Skip reading CURRENT_PROGRESS.md
  - Start a second task mid-session
  - Build infrastructure before workflows
  - Bypass tenant isolation
  - Create dead code
  - Delete stable code
  - Skip validation
  - Re-read all 21 docs every session (use Section 2.3 table)
```

---

## Appendix B — Architecture Dependency Map

```
PRODUCT_VISION
    └── BUSINESS_GOALS
        └── SYSTEM_PHILOSOPHY
            └── PLATFORM_DIRECTION
                └── CORE_FOUNDATION  ←── All technical decisions depend on this
                    ├── MONOREPO_STRUCTURE
                    ├── DOMAIN_DRIVEN_ARCHITECTURE
                    │   ├── BACKEND_ARCHITECTURE
                    │   │   ├── DATABASE_ARCHITECTURE
                    │   │   ├── API_ARCHITECTURE
                    │   │   └── EVENT_SYSTEM
                    │   └── FRONTEND_ARCHITECTURE
                    │       ├── DESIGN_SYSTEM
                    │       ├── UX_PATTERNS
                    │       ├── COMPONENT_GUIDELINES
                    │       └── RTL_SYSTEM
                    └── AI GOVERNANCE
                        ├── AI_FORBIDDEN_ACTIONS
                        ├── AI_DEVELOPMENT_RULES
                        ├── AI_WORKFLOW
                        └── AI_CODE_STYLE_GUIDE
```

---

*This document is the single source of truth for AI execution on the ATLS platform.*
*It supersedes any conflicting instructions found in session prompts or individual task descriptions.*
*Deviations from this protocol require explicit written authorization.*
