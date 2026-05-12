# AI Prompt Library & Execution Templates

| Metadata | Details |
| :--- | :--- |
| **Document ID** | ATLS-AI-06 |
| **Status** | AUTHORITATIVE |
| **Version** | 2.0.0 |
| **Owner** | AI Agent & Engineering Team |
| **Applicability** | Global Prompt Standards for AI Interactions |

## 1. Prompt Philosophy
In ATLS, a prompt is an **Engineering Specification**. Vague prompts lead to architectural decay. Every prompt must contain the high-fidelity context required to execute a task safely within the Modular Monolith.
- **Context is King**: Always provide the relevant `docs_v2` references.
- **Constraints are Safety**: Explicitly state the boundaries and "Forbidden Actions."
- **Verification-First**: Include the expected output and testing requirements.

## 2. Prompt Structure Standards
Every master prompt must follow this structure:
1. **Persona**: Define the AI's role (e.g., "Expert Django Architect").
2. **Task**: Clear, action-oriented objective.
3. **Scope**: Exact file paths or domain boundaries.
4. **Docs Reference**: Mandatory links to `docs_v2/` documents.
5. **Constraints**: Implementation red lines.
6. **Expected Output**: Specific artifacts (files, tests, summaries).

## 3. Frontend Prompt Template
```markdown
Persona: Senior React & Tailwind Developer.
Task: Implement [Component Name] following [DESIGN_SYSTEM.md].
Scope: `apps/frontend/src/features/[domain]/[component].tsx`.
Constraints: Use shadcn/ui primitives. Must be mobile-first and support RTL.
Verification: Take a screenshot and verify against [UX_PATTERNS.md].
```

## 4. Backend Prompt Template
```markdown
Persona: Expert Django & DRF Architect.
Task: Create [Service/Endpoint] for [Domain].
Scope: `apps/backend/[domain]/services/`, `apps/backend/[domain]/api/`.
Docs: Follow [DJANGO_SERVICES_LAYER.md] and [SERIALIZER_RULES.md].
Constraints: No fat views. Use the Result pattern for error handling.
Verification: Run pytest and check for tenant isolation in queries.
```

## 5. Refactor Prompt Template
```markdown
Persona: Refactoring Specialist.
Task: Migrate [Legacy Logic] to [New Pattern] in [File].
Scope: [Target Files].
Constraints: Maintain backward compatibility. Do not break existing tests.
Verification: Run regression suite. Delete old code only after full pass.
```

## 6. Bug Fix Prompt Template
```markdown
Persona: Senior Debugging Engineer.
Task: Fix the [Issue] in [Component/Service].
Scope: [File Path].
Context: [Traceback/Error Logs].
Requirement: Create a failing test case first, then implement the fix.
```

## 7. Performance Optimization Prompts
```markdown
Task: Optimize the [Query/Component] in [File].
Goal: Reduce [Latency/Render Count] by [X]%.
Constraint: Do not use complex caching unless [QUERY_RULES.md] is followed.
```

## 8. Security Review Prompt
```markdown
Task: Audit [Component/Service] for security vulnerabilities.
Checklist: Tenant isolation, Permission checks, Input sanitization, PII exposure.
Requirement: Report all findings before implementing fixes.
```

## 9. Offline Sync Prompt
```markdown
Task: Implement offline support for [Feature] using [IndexedDB].
Docs: Follow [OFFLINE_FIRST_STRATEGY.md].
Constraint: Must handle [Conflict Scenario] as defined in domain rules.
```

## 10. Event-Driven Prompt
```markdown
Task: Emit [Event Name] from [Service] when [Action] occurs.
Docs: Follow [EVENT_SYSTEM.md].
Requirement: Ensure the event is published within the same DB transaction.
```

## 11. CQRS Prompt
```markdown
Task: Create a Read Model for [Entity] in [Domain].
Scope: `apps/backend/[domain]/projections/`.
Constraint: Do not query the primary operational table for this view.
```

## 12. UI/UX Prompt Template
```markdown
Task: Polish the [Page] following [ANIMATION_SYSTEM.md].
Constraint: Animations must be < 300ms and GPU-optimized.
```

## 13. Tailwind Prompts
- "Use utility-first classes. No arbitrary values unless they match the design system scale."

## 14. shadcn Prompts
- "Extend the [Primitive] following the ATLS component guidelines. Ensure Radix UI accessibility attributes are preserved."

## 15. Django Prompts
- "Implement the [Model] with UUIDv7 as the primary key. Ensure `tenant_id` is present and filtered via the manager."

## 16. DRF Prompts
- "Create a Serializer that forbids nested writes. Use DTOs for input validation."

## 17. Celery Prompts
- "Create an idempotent task for [Logic]. Handle retries with exponential backoff."

## 18. Testing Prompts
- "Write integration tests for [Service]. Mock external APIs. Verify that Tenant A cannot access Tenant B's records."

## 19. Documentation Prompts
- "Update [AUDIT_DOMAIN.md] to include the new [Entity] change tracking rules."

## 20. Architecture Review Prompt
```markdown
Task: Review [Proposed Change] against [MODULAR_MONOLITH_RULES.md].
Output: Identify any circular dependencies or layer violations.
```

## 21. AI Safety Prompt Rules
- **Vagueness**: AI agents MUST NOT generate or accept vague prompts like "Fix the bugs."
- **Constraints**: FORBID prompts that lack explicit implementation constraints.
- **Architecture**: FORBID prompts that ignore or override authoritative `docs_v2` patterns.
- **Scope**: FORBID "Unbounded Prompts" that don't define a clear file or domain scope.
- **Unsafe**: FORBID prompts that suggest bypassing security or tenant isolation.

## 22. Forbidden Prompt Patterns
- "Write the code as fast as possible."
- "Ignore the existing structure and use [New Unvetted Library]."
- "Just get it working for now, we'll fix the architecture later."

## 23. Agricultural ERP Examples
- **Prompt**: "Expert Django Architect: Implement the `CalculateHarvestYieldService` in `apps/harvest/services/`. **Docs**: Follow [DJANGO_SERVICES_LAYER.md]. **Constraint**: All calculations must use `Decimal` with 4-point precision. **Verification**: Create tests in `apps/harvest/tests/test_yield.py`."

## 24. Final Enforcement Checklist
- [ ] Prompt includes a clear Persona and Task.
- [ ] Exact file scope is defined.
- [ ] Relevant `docs_v2` documents are linked.
- [ ] Architecture constraints are explicitly stated.
- [ ] Verification/Testing requirements are included.
- [ ] No "Forbidden Patterns" used.
- [ ] Output artifacts are specified.
- [ ] Tenant isolation is mentioned as a constraint for backend tasks.
