# ADR-002 — LocationNode as Universal Location Model

- **Status**: Accepted
- **Date**: 2026-05
- **Deciders**: System Architect

---

## Context

The original system had separate tables for farm location hierarchy:
- `Sector` model (top-level farm area)
- `Plot` / `Hosh` (leaf-level enclosure)
- `CropType` (linked to Sector)

This caused:
- Reports referenced `Sector` (FK) and sometimes `Plot` (FK) separately
- Adding a new location level required a new model and migration
- Analytics could not query across the full hierarchy in one query
- The system was not SaaS-ready — every new farm had different tables

---

## Decision

**All farm location data lives in a single `LocationNode` model.**

The `type` field defines the level:
```python
class LocationNode(TenantAwareModel):
    farm   = models.ForeignKey(Farm, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    name   = models.CharField(max_length=200)
    type   = models.CharField(max_length=20, choices=[
        ('SECTOR',    'Sector'),      # قطاع — Level 1
        ('STAGE',     'Stage'),       # مرحلة — Level 2
        ('ENCLOSURE', 'Enclosure'),   # حوشة — Level 3
    ])
```

**Important**: Stage is a valid, canonical business level. It is NOT deprecated.
Stage (مرحلة) represents a subdivision within a Sector, containing Enclosures.

Hierarchy:
```
Farm
└── LocationNode (SECTOR)       # e.g., "North Sector"
    └── LocationNode (STAGE)    # e.g., "Stage A"
        └── LocationNode (ENCLOSURE)  # e.g., "Enclosure 12"
```

All foreign keys to locations use:
```python
location = models.ForeignKey(LocationNode, on_delete=models.CASCADE)
```

---

## Consequences

**Positive:**
- Any number of hierarchy levels without new models
- Reports, analytics, and all modules use a single location FK
- Tree-based queries using MPTT or recursive self-join
- Admin configures the hierarchy — no code changes for new farms

**Negative:**
- Old code referencing `Sector`, `Plot`, `Stage` as separate models must be updated
- The `farm-structure.md` legacy doc references the old design — it is voided

**Deprecated (do not use):**
- `Sector` table → use `LocationNode(type='SECTOR')`
- `Plot` / `Hosh` table → use `LocationNode(type='ENCLOSURE')`
- `CropType` table → use `crop_type` CharField on `CropRecord`

---

## Alternatives Considered

1. **Separate Sector + Stage + Enclosure tables** — rejected: doesn't scale, breaks SaaS model
2. **JSON hierarchy field** — rejected: not queryable, not indexable
3. **MPTT (django-mptt)** — acceptable option but adds dependency; self-join FK is sufficient for 3 levels

---

## References
- `00-core/SYSTEM_ARCHITECTURE.md` (Section 4 — LocationNode Hierarchy)
- `02-backend/farm/FARM_STRUCTURE.md`
- `00-core/DOMAIN_LANGUAGE.md` (Section 2 — LocationNode Type System)
