# AI Workflow & Execution Lifecycle

| Metadata | Details |
| :--- | :--- |
| **Document ID** | ATLS-AI-05 |
| **Status** | AUTHORITATIVE |
| **Version** | 2.0.0 |
| **Owner** | AI Agent & Engineering Team |
| **Applicability** | All AI-Driven Engineering Workflows |

## 1. Workflow Philosophy
The AI workflow in ATLS is **Intentional, Verifiable, and Documentation-First**. We believe that planning is 70% of the work. Blind execution is a critical failure.
- **Plan-First**: No code changes without an approved implementation plan.
- **Verify-Always**: Every step must be validated against the architecture.
- **Traceable**: Every action must leave a trail in artifacts (`task.md`, `implementation_plan.md`).

## 2. Task Intake
- The workflow begins when an AI receives a task via the [AI_TASK_TEMPLATE.md].
- **Validation**: AI must confirm the task is well-defined (Objective, Scope, Constraints are present).

## 3. Context Analysis
- AI reads all relevant domain, architecture, and design documents in `docs_v2`.
- AI explores the current codebase to understand existing patterns and data structures.

## 4. Dependency Mapping
- Identify all modules, services, and events that will be affected.
- **Map**: Visual or list-based map of the "Blast Radius."

## 5. Risk Evaluation
- Categorize risks: `Performance`, `Data Integrity`, `Security`, `UX Consistency`.
- Propose mitigation strategies in the implementation plan.

## 6. Planning Phase
- Create `implementation_plan.md`.
- Group changes by component.
- Define specific file modifications.
- **User Approval**: Stop and wait for explicit human approval for complex tasks.

## 7. Architecture Validation
- Cross-reference the plan with [AI_FORBIDDEN_ACTIONS.md] and [AI_CODE_STYLE_GUIDE.md].
- Ensure no "Red Lines" are crossed.

## 8. Execution Phase
- Initialize `task.md`.
- Implement changes incrementally.
- Update `task.md` with `[/]` and `[x]` after every atomic change.

## 9. Incremental Delivery
- Work on one file or one small logic block at a time.
- Verify each block before moving to the next.

## 10. Validation Phase
- Run linters, unit tests, and performance checks.
- Verify UI changes via screenshots or browser tools.
- Ensure tenant isolation is maintained.

## 11. Testing Workflow
- Write tests *before* or *during* implementation (TDD approach preferred).
- All new features must have > 80% test coverage for the specific logic added.

## 12. Refactor Workflow
1. Identify technical debt.
2. Propose new pattern in the plan.
3. Migrate logic incrementally.
4. Delete legacy code only after verification.

## 13. Bug Fix Workflow
1. Reproduce bug via a failing test.
2. Identify root cause.
3. Implement fix.
4. Verify test passes.

## 14. Migration Workflow
1. Draft schema change.
2. Create migration file.
3. Verify forward and backward compatibility.
4. Test with sample tenant data.

## 15. UI Workflow
1. Review [DESIGN_SYSTEM.md].
2. Build components in isolation.
3. Integrate into the page.
4. Verify RTL and Responsive behavior.

## 16. Backend Workflow
1. Define Service interface.
2. Implement Repository layer.
3. Implement Service logic.
4. Expose via Serializer/View.

## 17. Offline Workflow
1. Implement local storage (IndexedDB).
2. Implement sync queue.
3. Implement conflict resolution logic.
4. Verify behavior with simulated "Offline" state.

## 18. Security Workflow
1. Check permissions.
2. Verify tenant filters.
3. Sanitize inputs.
4. Audit critical state changes.

## 19. Deployment Safety
- Ensure all changes are backward compatible.
- Check for "Breaking Changes" in the implementation plan.

## 20. Rollback Planning
- Every major feature must have a "Kill Switch" or a clearly defined rollback procedure (e.g., reverting migrations).

## 21. Human Escalation Rules
- Stop and escalate if:
    - You discover a conflict between two authoritative docs.
    - You find a security vulnerability.
    - The task requires a change to the core `Audit` or `Security` modules.
    - You are unsure of the architectural pattern to follow.

## 22. AI Safety Rules
- **Planning**: AI agents MUST NOT skip the planning phase for tasks involving > 2 files.
- **Blind Execution**: FORBID modifying code without first reading the relevant domain documentation.
- **Unrelated Systems**: FORBID modifying files or systems not defined in the task scope.
- **Validation**: FORBID claiming completion without running a verification step (test/lint).
- **Dependencies**: FORBID ignoring the downstream impact on other modules.
- **Unsafe Changes**: FORBID committing code that breaks existing tests or violates tenant isolation.

## 23. Forbidden Workflow Behaviors
- **Silence**: Working for hours without an update.
- **Ambiguity**: Claiming "It's almost done" without evidence.
- **Override**: Ignoring human feedback on a plan.

## 24. Agricultural ERP Examples
- **Scenario**: Adding a new "Harvest Type."
- **Workflow**: Context analysis (Season rules) -> Plan (Service update + Migration) -> Exec (Service logic) -> Verify (Test creation) -> Summarize.

## 25. Final Enforcement Checklist
- [ ] Context analysis performed.
- [ ] Dependency map created.
- [ ] Risks identified and mitigated.
- [ ] Implementation plan approved by user.
- [ ] Task progress tracked in `task.md`.
- [ ] Architecture validation pass completed.
- [ ] Tests run and verified.
- [ ] Walkthrough artifact generated.
- [ ] No "Red Lines" crossed.
