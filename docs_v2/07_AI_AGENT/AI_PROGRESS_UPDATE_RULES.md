# AI Progress Reporting & Transparency Governance

| Metadata | Details |
| :--- | :--- |
| **Document ID** | ATLS-AI-03 |
| **Status** | AUTHORITATIVE |
| **Version** | 2.0.0 |
| **Owner** | AI Agent & Product Team |
| **Applicability** | All AI Agent Communications & Task Summaries |

## 1. Progress Reporting Philosophy
Progress reporting in ATLS is about **Absolute Transparency**. We value truth over velocity. An AI agent's primary duty during reporting is to provide the human partner with an accurate, verifiable, and architecturally-aware status of the current task.
- **Verifiability**: Claims of completion must be backed by evidence (tests, files, logs).
- **Architectural Context**: Every update must explain *how* it affects the wider platform.
- **Honesty**: Failures and blockers are more important to report than successes.

## 2. Transparency Rules
- **No Obfuscation**: Do not use vague language like "optimized the code" or "updated the system."
- **Full Disclosure**: Always report if a task required bypassing a non-critical lint rule or making a design compromise.
- **Real-Time Truth**: If a task is 50% done, report it as 50%, not "nearly finished."

## 3. Required Update Structure
Every significant progress update must follow this structure:
1. **Executive Summary**: 1-2 sentences on what was achieved.
2. **Task Checklist**: Updated status of the `task.md` items.
3. **Files Modified**: List of all created or edited files with brief rationale.
4. **Architecture Impact**: Summary of any changes to domain boundaries, events, or storage.
5. **Verification Evidence**: Proof that the work functions (e.g., "Ran 5 tests, all passed").
6. **Next Steps**: What the AI will work on next.

## 4. Task Completion Format
- Use standard markdown checkboxes: `- [x]` for completed, `- [/]` for in-progress, `- [ ]` for pending.
- Every completed item must have a corresponding file change or test result.

## 5. File Change Reporting
- List files using absolute paths or clear relative project paths.
- **Example**: `Modified apps/harvest/services/reporting_service.py to include yield-per-hectare logic.`

## 6. Architecture Impact Reporting
- Explicitly state if the change:
    - Adds a new Domain Event.
    - Modifies a Database Schema (Migration).
    - Changes a Service Layer interface.
    - Updates a Global Design Token.

## 7. Dependency Reporting
- Report if the task required adding a new `npm` or `pip` package.
- Report if the work depends on a feature currently in development in another module.

## 8. Risk Reporting
- Identify potential side effects: "This change to `TenantManager` might impact query performance in the `AuditLog` module."

## 9. Blocker Reporting
- If an AI cannot proceed due to missing information, invalid tools, or system errors, it must stop and report the **exact blocker** immediately.

## 10. Refactor Reporting
- If the AI performed a refactor during a task, it must explain *why* it was necessary and *what* pattern was followed.

## 11. Bug Fix Reporting
- For bug fixes, report: **Root Cause**, **Fix Implementation**, and **Prevention Strategy** (e.g., the new test case added).

## 12. Migration Reporting
- Every database migration must be reported with its name and the specific models affected.

## 13. Performance Reporting
- Report if a change is expected to significantly increase or decrease API latency or frontend bundle size.

## 14. Security Reporting
- Explicitly state that "No hardcoded secrets were added" and "Tenant isolation was verified."

## 15. AI Confidence Reporting
Use a 1-5 scale for complex tasks:
- **Confidence 5**: Standard implementation, fully tested, follows all docs.
- **Confidence 3**: Experimental approach, requires manual review, tests are partial.
- **Confidence 1**: Speculative implementation, high risk of failure.

## 16. Partial Completion Rules
- If a task is partially complete due to a turn timeout or a specific error, the AI must summarize the **exact state of the world** so work can be resumed.

## 17. Failure Reporting
- If a tool call fails or a logic error occurs, report the **Raw Error** and the **AI's interpretation** of what went wrong.

## 18. Multi-Step Task Reporting
- For tasks spanning multiple turns, the AI must provide a "Continuity Summary" at the start of each turn.

## 19. Forbidden Reporting Behaviors
- **Faking Completion**: AI MUST NEVER claim a task is done if it hasn't verified it via a tool or test.
- **Hiding Failures**: FORBID omitting failed tool calls or error messages from the summary.
- **Exaggerating Progress**: FORBID claiming "All tests passed" if only a subset were run.
- **Skipping Impacts**: FORBID ignoring the architectural side effects of a change.
- **Omitting Files**: FORBID hiding any file modification made during the task.
- **Unverified Success**: FORBID claiming "The UI looks perfect" without taking a screenshot or verifying CSS properties.

## 20. Agricultural ERP Examples
- **Good**: "Updated the Harvest reporting logic in `harvest_service.py`. This adds a new `harvest.batch.created` event. Verified by running `pytest apps/harvest/tests/`. Confidence: 5/5."
- **Bad**: "Fixed the harvest bugs and made it faster."

## 21. Final Enforcement Checklist
- [ ] Task Checklist is updated.
- [ ] Modified files are listed with rationale.
- [ ] Architecture impacts are explicitly stated.
- [ ] Verification evidence (tests/logs) is provided.
- [ ] Risks and Blockers are identified.
- [ ] Confidence level is stated for complex logic.
- [ ] No vague or exaggerated language used.
- [ ] Continuity summary provided for multi-step tasks.
