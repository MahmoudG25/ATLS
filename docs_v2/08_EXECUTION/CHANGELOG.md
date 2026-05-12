# Platform Master Changelog

| Metadata | Details |
| :--- | :--- |
| **Document ID** | ATLS-EXE-CHAN |
| **Status** | ACTIVE |
| **Version** | 2.0.0 |
| **Owner** | Release Engineering Team |
| **Applicability** | Global Change Tracking & Version History |

## 1. Changelog Philosophy
The ATLS Changelog is the **Chronological Source of Truth**. It provides a clear, impact-focused narrative of the platform's evolution. It is designed to be read by humans (Managers/Admins) and parsed by AI agents to understand historical context.
- **Truth over Hype**: Document failures and rollbacks as clearly as new features.
- **Impact-First**: Explain *what* changed and *how* it affects the end-user or system.

## 2. Semantic Versioning Rules (SemVer)
We follow the `MAJOR.MINOR.PATCH` format:
- **MAJOR**: Breaking changes (e.g., Database schema rework, Auth system swap).
- **MINOR**: New features (e.g., New Harvest Domain, New Analytics Dashboard).
- **PATCH**: Bug fixes, lints, and documentation updates.

## 3. Release Categories
- `Added`: New features or capabilities.
- `Changed`: Modifications to existing functionality.
- `Deprecated`: Soon-to-be-removed features.
- `Removed`: Deleted features or code.
- `Fixed`: Bug resolutions.
- `Security`: Vulnerability patches or hardening.
- `Architecture`: Changes to global patterns or monorepo structure.

## 4. Breaking Change Rules
- Breaking changes MUST be highlighted with a `[BREAKING]` prefix.
- They MUST include a "Migration Guide" or "Manual Action Required" section.

## 5. Migration Logging Rules
- Every database migration must be logged with its timestamp and a list of affected tables.
- **Critical**: Note if the migration is "Forward Only" or "Reversible."

## 6. Architecture Change Logging
- Document changes to global `docs_v2` standards (e.g., updating the [ANIMATION_SYSTEM.md]).

## 7. Security Change Logging
- Document all security hardening, dependency updates (CVE fixes), and permission changes.

## 8. Performance Change Logging
- Document optimizations that significantly reduce latency or bundle size.

## 9. Database Change Logging
- Log schema additions, index updates, and data-fix scripts.

## 10. API Change Logging
- Document new endpoints, parameter changes, and deprecated versions.

## 11. Frontend Change Logging
- Document UI updates, new shared components, and design system adjustments.

## 12. AI-Generated Change Logging
- Changes primarily implemented by an AI agent must be tagged with `[AI]`.

## 13. Rollback Tracking
- Document every release that was rolled back, including the **Reason** and the **Target Version** rolled back to.

## 14. Release Approval Workflow
1. **QA Pass**: All tests green in Staging.
2. **Architecture Sign-off**: Verified against [AI_FORBIDDEN_ACTIONS.md].
3. **Drafting**: AI generates the changelog draft based on commit history.
4. **Human Review**: Lead Architect approves the version.

## 15. Agricultural ERP Examples

### [1.2.0] - 2026-06-15
**Added**
- `[AI]` Harvest Batch Tracking system. Users can now group harvest loads into "Batches" for export traceability.
- `[FEATURE]` Offline support for Daily Journal entries.

**Fixed**
- Resolved a critical N+1 query issue in the `PersonnelRepository` that was causing 2s latency on farm manager dashboards.

**Changed**
- `[BREAKING]` Updated the `HarvestLoad` model to include a mandatory `batch_id`. **Migration Required**: Run `python manage.py migrate` and execute the `migrate_orphan_loads` script.

---

### [1.1.2] - 2026-06-01
**Security**
- Updated `SimpleJWT` to version 5.3.0 to patch an authentication vulnerability.
- Enforced 10-minute session expiry for `Admin` roles.

**Architecture**
- Finalized [AUDIT_DOMAIN.md] and established immutable change tracking for financial entities.

---

## 16. Changelog Templates

### Standard Entry
```markdown
### [X.Y.Z] - YYYY-MM-DD
**Added/Changed/Fixed**
- [Brief description of change].
- `[AI]` [AI-generated contribution].
```

### Breaking Change Entry
```markdown
### [X.Y.Z] - YYYY-MM-DD
**Changed**
- `[BREAKING]` [Description of the breaking change].
**Migration Guide**
- Step 1: [Action].
- Step 2: [Action].
```

## 17. Final Changelog Checklist
- [ ] Version number follows SemVer rules.
- [ ] Dates are in YYYY-MM-DD format.
- [ ] Breaking changes are explicitly highlighted.
- [ ] Database migrations are noted.
- [ ] AI-generated changes are tagged with `[AI]`.
- [ ] Migration guides included for breaking changes.
- [ ] Rollbacks (if any) are documented with reasons.
- [ ] Links to relevant architecture docs updated.
