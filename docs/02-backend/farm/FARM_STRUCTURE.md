# Farm Structure — Backend Reference

> Canonical documentation for the Farm and LocationNode models.
> See `ADR-002-locationnode.md` for design rationale.

---

## 1. Models

### Farm
```python
class Farm(TenantAwareModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name    = models.CharField(max_length=200)
```

One Company has one Farm in the current implementation (extendable to multiple).

### LocationNode
```python
class LocationNode(TenantAwareModel):
    TYPE_CHOICES = [
        ('SECTOR',    'Sector'),      # قطاع — Level 1
        ('STAGE',     'Stage'),       # مرحلة — Level 2
        ('ENCLOSURE', 'Enclosure'),   # حوشة — Level 3
    ]
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    farm    = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='locations')
    parent  = models.ForeignKey('self', null=True, blank=True,
                                on_delete=models.CASCADE, related_name='children')
    name    = models.CharField(max_length=200)
    type    = models.CharField(max_length=20, choices=TYPE_CHOICES)

    class Meta:
        indexes = [
            models.Index(fields=['company', 'farm']),
            models.Index(fields=['parent']),
        ]
```

---

## 2. Hierarchy Rules

```
Farm
└── LocationNode (type=SECTOR)
    └── LocationNode (type=STAGE)       ← Stage is a VALID level, not deprecated
        └── LocationNode (type=ENCLOSURE)
```

**Validation rules (enforced in service layer):**
- A `SECTOR` node must have `parent=None` (or `parent` is a Farm-level virtual node)
- A `STAGE` node's parent must be a `SECTOR`
- An `ENCLOSURE` node's parent must be a `STAGE` (or directly under `SECTOR` if no stages)
- All nodes must belong to the same Company and Farm

---

## 3. API Endpoints

| Method | URL | Description | Permission |
|--------|-----|-------------|------------|
| `GET` | `/farm/location-tree/` | Full tree for current company/farm | ENGINEER+ |
| `GET` | `/farm/locations/` | Flat list of all nodes | ENGINEER+ |
| `POST` | `/farm/locations/` | Create a new node | MANAGER+ |
| `PATCH` | `/farm/locations/{id}/` | Update node name | MANAGER+ |
| `DELETE` | `/farm/locations/{id}/` | Delete node (cascades children) | MANAGER+ |

### Tree Response Format
```json
{
  "farm": { "id": 1, "name": "Main Farm" },
  "tree": [
    {
      "id": 1, "name": "North Sector", "type": "SECTOR",
      "children": [
        {
          "id": 5, "name": "Stage A", "type": "STAGE",
          "children": [
            { "id": 12, "name": "Enclosure 12", "type": "ENCLOSURE", "children": [] }
          ]
        }
      ]
    }
  ]
}
```

---

## 4. Service Layer

```python
# services/farm_service.py

def get_location_tree(company) -> dict:
    """Returns farm + nested LocationNode tree for company."""

def create_location_node(company, name, type, parent_id=None) -> LocationNode:
    """Creates a node with type validation."""

def update_location_node(company, node_id, name) -> LocationNode:
    """Updates name only — type and parent are immutable after creation."""

def delete_location_node(company, node_id) -> None:
    """Cascades deletion to all children."""
```

---

## 5. Frontend Integration

Frontend file: `Front-End/src/features/farm/services.js`

```javascript
export const getLocationTree = () => api.get('/farm/location-tree/')
export const createLocationNode = (data) => api.post('/farm/locations/', data)
export const updateLocationNode = (id, data) => api.patch(`/farm/locations/${id}/`, data)
export const deleteLocationNode = (id) => api.delete(`/farm/locations/${id}/`)
```

See `04-features/farm-structure/PHASE_01.md` for the complete adaptive UI implementation.

---

## 6. Do Not

- ❌ Create separate `Sector`, `Stage`, or `Plot` tables
- ❌ Add a location FK to any model other than `LocationNode`
- ❌ Use free-text location fields in reports
- ❌ Deprecate the `STAGE` type — it is a valid business level
