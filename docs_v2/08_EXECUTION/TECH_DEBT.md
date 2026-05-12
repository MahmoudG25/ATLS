# Technical Debt Governance

| Metadata | Details |
| :--- | :--- |
| **Document ID** | ATLS-EXE-DEBT |
| **Status** | AUTHORITATIVE |
| **Version** | 2.0.0 |
| **Owner** | Project Engineering Team |
| **Applicability** | Tracking, Management, and Resolution of Technical Debt |

## 1. Technical Debt Philosophy
In ATLS, technical debt is not a failure; it is a **Strategic Financial Tool**. Like financial debt, technical debt can accelerate speed-to-market, provided it is documented, managed, and paid back with interest.
- **Transparency**: All debt must be labeled and tracked.
- **Intentionality**: Debt is only accepted if it provides a clear operational advantage.
- **Zero-Hidden Hacks**: AI agents and developers MUST NOT hide compromises.

## 2. Debt Classification
1. **Strategic Debt**: Deliberate shortcuts taken to meet a critical harvest or release deadline.
2. **Evolutionary Debt**: Debt that occurs when the platform scales beyond its original design.
3. **Accidental Debt**: Poor patterns introduced due to a lack of domain context.
4. **Tooling Debt**: Limitations imposed by external libraries or framework versions.

## 3. Architectural Debt
- **Modular Monolith Boundaries**: Temporary cross-domain imports that violate the [DJANGO_STRUCTURE.md] rules.
- **Event System Bypass**: Synchronous calls between domains that should be event-driven.

## 4. Performance Debt
- **N+1 Queries**: Unoptimized ORM calls that are acceptable for low-traffic staging but must be fixed for production.
- **Missing Projections**: Using operational tables for analytics instead of CQRS read-models.

## 5. Security Debt
- **Permission Granularity**: Using broad roles (e.g., `Supervisor`) instead of fine-grained permissions for an MVP.
- **Audit Lag**: Short-lived delays in non-critical audit log synchronization.

## 6. Frontend Debt
- **Component Prop Drilling**: Bypassing a Zustand store for a small, temporary UI feature.
- **Non-Generic Components**: Ad-hoc UI elements that should be moved to the Design System.

## 7. Backend Debt
- **Fat Views**: Temporary logic in views that should be moved to a Service Layer.
- **Mock Data**: Using hardcoded responses for external integrations (e.g., Weather API) during development.

## 8. Offline Debt
- **Simplified Conflict Resolution**: Using "Last Win" logic for complex data fields where "Manual Review" is eventually required.
- **Partial Asset Caching**: Not all static assets are cached for offline mode in the early phases.

## 9. Mobile Debt
- **RAM Footprint**: High memory usage in the data-entry grid that requires optimization for low-end Android devices.
- **In-App Media Processing**: Postponing server-side video transcoding to later phases.

## 10. Analytics Debt
- **Direct Queries**: Running reports against the live PostgreSQL DB instead of a dedicated analytics replica or warehouse.

## 11. AI Workflow Debt
- **Manual Task Templates**: Relying on human-generated templates before the full [AI_TASK_TEMPLATE.md] automation is integrated.

## 12. Documentation Debt
- **Stale Specs**: Implementation diverging from the original doc in minor, undocumented ways.
- **Missing Walkthroughs**: Tasks completed without a corresponding `walkthrough.md`.

## 13. Testing Debt
- **Missing E2E coverage**: Focusing only on unit tests for an early sprint.
- **Incomplete Mobile Simulator Tests**: Relying only on browser-based responsive testing.

## 14. Refactor Priorities
Debt is repaid in order of **System Risk**:
1. **Security Debt** (Fixed immediately).
2. **Architectural Debt** (Fixed before next domain phase).
3. **Performance Debt** (Fixed before production launch).
4. **UI/UX Debt** (Fixed as part of polish sprints).

## 15. Risk Matrix
| Debt Type | Stability Risk | Scalability Risk | Complexity Cost |
| :--- | :--- | :--- | :--- |
| **Architectural** | High | High | High |
| **Security** | Critical | Low | Medium |
| **Performance** | Low | High | Medium |
| **Documentation**| Medium | Low | Low |

## 16. Severity Classification
- **SEV-1**: Breaking changes or isolation bypasses. (Must fix before next PR).
- **SEV-2**: Performance bottlenecks or pattern violations. (Must fix in current phase).
- **SEV-3**: Polish, documentation, or minor lints. (Backlogged for tech-debt sprints).

## 17. Mitigation Strategy
- **Tech Debt Fridays**: 20% of every sprint dedicated to debt repayment.
- **Debt Labeling**: All debt-laden code must be marked with `// TODO (TECH_DEBT): [Explanation]`.

## 18. Refactor Workflow
1. Identify the debt record in this document.
2. Create an [AI_TASK_TEMPLATE.md] specifically for the refactor.
3. Verify the fix against the original architecture docs.
4. Update this document to mark the debt as resolved.

## 19. Temporary Workaround Rules
- Workarounds MUST be documented in the `Notes` section of the relevant domain file.
- Workarounds MUST have a defined "Expiry Date" or "Trigger Event" for refactoring.

## 20. Forbidden Debt Patterns
- **The "Permanent" Hack**: No temporary fix can stay for more than two strategic phases.
- **Silently Bypassing Isolation**: Tenant isolation bypasses are NEVER permitted, even as temporary debt.
- **Unlabeled Hacks**: Code that doesn't follow patterns must be labeled.

## 21. Agricultural ERP Constraints
- **Harvest Window**: During peak harvest (2-4 weeks), we may accept high levels of operational debt to maintain system uptime, with a mandatory "Post-Harvest" repayment phase.

## 22. Final Debt Checklist
- [ ] Debt is explicitly labeled in the code.
- [ ] Debt is categorized and ranked by severity.
- [ ] Mitigation strategy is defined.
- [ ] No tenant isolation or security bypasses are present.
- [ ] Expiry events defined for temporary workarounds.
- [ ] Refactor priority is aligned with the roadmap.
