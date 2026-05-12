# AI Task Template & Execution Governance

| Metadata | Details |
| :--- | :--- |
| **Document ID** | ATLS-AI-04 |
| **Status** | AUTHORITATIVE |
| **Version** | 2.0.0 |
| **Owner** | AI Agent & Architecture Team |
| **Applicability** | All AI-Assisted Tasks & Workflows |

## 1. Task Philosophy
Tasks in ATLS are **Atomic, Context-Rich, and Bound**. An AI agent should never work in a vacuum; every task must be defined with clear entry and exit criteria to prevent scope creep and architectural drift.
- **Precision**: Focus on the specific problem, not the entire system.
- **Guardrails**: Explicitly state what the AI **cannot** do.
- **Traceability**: Link tasks to specific domain documents and architecture rules.

## 2. Standard Task Structure
Every AI task definition must follow this structure:
1. **Title**: Concise action-based name.
2. **Objective**: High-level goal.
3. **Scope**: Specific list of files and features to modify.
4. **Constraints**: Implementation red lines and architecture rules.
5. **Dependencies**: Required services, events, or data.
6. **Acceptance Criteria**: Verifiable checkboxes.

## 3. Objective Definition
- Use active verbs (e.g., "Refactor", "Implement", "Fix").
- Explain the **Why** alongside the **What**.
- **Example**: "Refactor the Harvest Repository to support seasonal partitioning to improve query performance."

## 4. Scope Definition
- **Include**: Explicit list of file paths.
- **Exclude**: Explicit list of modules or layers that must not be touched.
- **Red Line**: "Do not modify the `apps.core` module."

## 5. Constraints Section
- Reference specific architecture docs (e.g., "Must follow [QUERY_RULES.md]").
- Set performance targets (e.g., "API response must be < 200ms").
- Enforce styles (e.g., "Use Tailwind utility classes only").

## 6. Dependencies Section
- List internal service dependencies (e.g., "Depends on `InventoryService`").
- List external dependencies (e.g., "Requires access to the Weather API").

## 7. File Targeting Rules
- AI MUST NOT modify files outside the defined `Scope`.
- If a change requires touching a cross-domain file, the AI must request permission or suggest an event-driven alternative.

## 8. Acceptance Criteria
- Must be binary (Pass/Fail).
- Include:
    - Code quality (Linter pass).
    - Functional logic (Tests pass).
    - Performance (Speed metrics).
    - Security (Tenant isolation verified).

## 9. Output Expectations
- **Artifacts**: New or updated `task.md`, `implementation_plan.md`, `walkthrough.md`.
- **Code**: Clean, formatted, and documented source code.
- **Reporting**: Final summary following [AI_PROGRESS_UPDATE_RULES.md].

## 10. Validation Rules
- Mandatory dry-run or lint check before final submission.
- Manual verification of critical domain rules (e.g., checking tenant filtering).

## 11. Architecture Protection
- The task must include a "Protect" clause: "Protect the integrity of the `AuditLog` domain; ensure no state changes occur without a log entry."

## 12. Refactor Task Template
```markdown
### [REFACTOR] [Target Entity]
**Goal**: Improve [Metric/Readability/Structure].
**Pattern**: [Service/Repository/DTO].
**Legacy Cleanup**: Remove [Old Pattern/Code].
```

## 13. Bug Fix Task Template
```markdown
### [BUG] [Issue Summary]
**Root Cause**: [Diagnosis].
**Fix Strategy**: [Implementation].
**Regression Prevention**: [New Test Case].
```

## 14. Feature Task Template
```markdown
### [FEATURE] [Feature Name]
**Domain**: [Bounded Context].
**User Value**: [Requirement].
**Schema Changes**: [New Fields/Models].
**Events**: [New Domain Events].
```

## 15. Migration Task Template
```markdown
### [MIGRATION] [Schema Change]
**Target Model**: [Model Name].
**Safety**: [Forward/Backward Compatibility].
**Data Migration**: [Script Logic].
```

## 16. UI Task Template
```markdown
### [UI] [Component Name]
**Design System**: [DESIGN_SYSTEM.md].
**Accessibility**: [REDUCED_MOTION].
**Responsive**: [Mobile-First Grid].
```

## 17. Backend Task Template
```markdown
### [BACKEND] [Logic Flow]
**Service**: [Service Name].
**Transaction**: [Atomic Boundary].
**Validation**: [Zod/Schema].
```

## 18. Documentation Task Template
```markdown
### [DOC] [Document Name]
**Source of Truth**: [Domain Doc].
**Audience**: [Engineering/Product].
**Sections**: [Required List].
```

## 19. Multi-Step Execution Template
1. **Analysis**: Read relevant docs.
2. **Plan**: Write `implementation_plan.md`.
3. **Draft**: Create `task.md`.
4. **Execute**: Implement code.
5. **Verify**: Run tests/lint.
6. **Summarize**: Write `walkthrough.md`.

## 20. Failure Handling Template
1. **Log Error**: Capture raw traceback.
2. **Diagnose**: Analyze tool/logic failure.
3. **Propose Fix**: Suggest alternative approach.
4. **Retry/Escalate**: Execute fix or stop for human review.

## 21. AI Safety Rules
- **Modifying**: AI agents MUST NOT modify unspecified files; stay within the defined scope.
- **Expansion**: FORBID "Silent Scope Creep" (implementing extra features not in the objective).
- **Constraints**: FORBID ignoring explicitly stated constraints or architecture rules.
- **Invention**: FORBID "Architectural Hallucination" (creating new global patterns not found in `docs_v2`).
- **Bypass**: FORBID marking a task as "Complete" without verifying the acceptance criteria.

## 22. Forbidden Prompting Patterns
- **"Just fix it"**: Too vague; requires specific scope.
- **"Improve everything"**: Leading to massive unmanageable diffs.
- **"Ignore the errors"**: Bypassing safety/linting guardrails.

## 23. Agricultural ERP Examples
- **Task**: "Implement the `HarvestLoadWeight` validation in the `HarvestService`. **Constraint**: Must use the `CropSchema` for weight limits. **Scope**: `apps/harvest/services/harvest_service.py`."

## 24. Final Enforcement Checklist
- [ ] Objective is action-oriented and clear.
- [ ] Scope is explicitly defined by file paths.
- [ ] Constraints reference existing architecture docs.
- [ ] Acceptance criteria are binary and verifiable.
- [ ] Architecture protection clause is included.
- [ ] Output artifacts (task/plan/walkthrough) are specified.
- [ ] No vague or unbounded objectives.
