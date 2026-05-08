# Archive Notice — Legacy Documentation

> **IMPORTANT**: Documents in this folder are VOIDED. They exist for historical reference only.
> Do NOT implement anything from these documents.
> Do NOT reference them in code or new documentation.

---

## Why These Files Are Here

These files existed before the documentation architecture refactor (2026-05).
They contain outdated designs, deprecated models, or near-empty stubs.

| File | Why Voided |
|------|------------|
| `back-end-farm-structure.md` | References old `Sector` and `Plot` tables — replaced by `LocationNode` |
| `back-end-report-linking.md` | References old Sector/Plot FK on reports — replaced by `LocationNode` FK |
| `back-end-olive-module.md` | References deprecated `OliveRecord` model — replaced by `CropRecord(crop_type='olive')` |
| `back-end-palm-module.md` | References deprecated `PalmRecord` model — replaced by `CropRecord(crop_type='palm')` |
| `back-end-reports.md` | Empty stub — superseded by `02-backend/reports/OPERATION_LOG.md` and `ANALYTICS_API.md` |
| `back-end-production.md` | Empty stub — superseded by `01-product/MODULES_OVERVIEW.md` |
| `back-end-module-pages.md` | Empty stub |
| `front-end-profile.md` | Empty stub |
| `front-end-arm-ui.md` | Empty stub |
| `front-end-README.md` | Broken links to files that never existed |

---

## Current Replacements

| Old File | Current Authoritative Document |
|----------|-------------------------------|
| `back-end-farm-structure.md` | `docs/02-backend/farm/FARM_STRUCTURE.md` |
| `back-end-report-linking.md` | `docs/02-backend/reports/OPERATION_LOG.md` |
| `back-end-olive-module.md` | `docs/00-core/DOMAIN_LANGUAGE.md` (Section 8) |
| `back-end-palm-module.md` | `docs/00-core/DOMAIN_LANGUAGE.md` (Section 8) |
| `back-end-reports.md` | `docs/02-backend/reports/ANALYTICS_API.md` |
| `front-end-README.md` | `docs/03-frontend/FRONTEND_OVERVIEW.md` |

---

## For AI Agents

If you find a reference to any document in this folder in the codebase or other docs:
1. The reference is outdated
2. Find the replacement in the table above
3. Update the reference to point to the current authoritative document
4. Do NOT implement based on the archived content

**The SOURCE_OF_TRUTH for any of these topics is in `docs/00-core/` or `docs/02-backend/`.**
