# Farm Structure — Feature Overview

> Feature: Dynamic Adaptive Farm Hierarchy Management
> ADR: `05-decisions/ADR-002-locationnode.md`

---

## What This Feature Does

Allows admins and managers to define and manage the farm's physical hierarchy:
- Create Sectors (قطاعات) — top-level farm areas
- Create Stages (مراحل) — subdivisions within sectors
- Create Enclosures (حوشات) — leaf-level units within stages

The UI adapts dynamically: as more nodes are added, their visual size shrinks to fit.

---

## User Flow

```
Manager opens Farm Structure page
  ↓
Sees tree: Sectors expanded → Stages → Enclosures
  ↓
Can: Add sector / Add stage to sector / Add enclosure to stage
Can: Edit name / Delete node (cascades children)
Can: Collapse/Expand any branch
Can: Search by name (highlights matches, dims others)
```

---

## Key Design Rules

| Element | Rule |
|---------|------|
| Node size | Scales with sibling count: 1-3→lg, 4-6→md, 7-12→sm, 13+→xs |
| Enclosure grid | 1-4→2 cols, 5-8→3 cols, 9-12→4 cols, 13+→5 cols |
| Stage layout | flex-wrap horizontal within sector |
| Sector layout | Full-width row per sector |
| Connectors | Dashed right border (RTL) |

---

## Backend

- API: `GET /farm/location-tree/` — returns nested tree JSON
- Models: `Farm`, `LocationNode` (type: SECTOR / STAGE / ENCLOSURE)
- Service: `services/farm_service.py`
- Reference: `02-backend/farm/FARM_STRUCTURE.md`

## Frontend

- Page: `src/pages/farm/FarmStructure.jsx`
- Styles: `src/pages/farm/FarmStructure.css`
- Services: `src/features/farm/services.js`
- Full implementation: `04-features/farm-structure/PHASE_01.md`

---

## Current Status: ⚠️ Phase 1 Partially Implemented

Completed:
- ✅ Adaptive node sizing algorithm
- ✅ Collapse/Expand per branch
- ✅ Search with highlight/dim
- ✅ Hover actions (Edit/Delete)
- ✅ Count badges
- ✅ Enclosure grid layout

Pending:
- ⬜ RTL connector lines alignment
- ⬜ Drag-and-drop reordering
