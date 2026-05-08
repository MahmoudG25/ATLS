# Database Rules — ATLS Farm ERP

> **Authority**: Tier 1. All model design decisions must comply with these rules.

---

## 1. Global Model Rules

### Rule 1 — TenantAwareModel is Mandatory
```python
# ✅ Every model MUST inherit TenantAwareModel
class DailyTaskReport(TenantAwareModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    ...

# ❌ Never — plain model without tenant
class Report(models.Model):
    ...
```

### Rule 2 — No Duplicate Models
Before creating any model, check all apps for similar entities.
If a model exists → extend or reuse it. Do NOT create a duplicate.

Examples of correct reuse:
- `CropRecord(crop_type='palm')` instead of `PalmRecord`
- `LocationNode(type='ENCLOSURE')` instead of `Plot`

### Rule 3 — No Hardcoded Values
Use DB tables instead of hardcoded choices where the business drives configuration:
- ❌ `CROP_CHOICES = [('palm', 'Palm'), ('olive', 'Olive')]` — Admin can't extend this
- ✅ `Variety` model with `crop_type` field — Admin adds new varieties from dashboard

Exception: Role names, location types, and status fields ARE acceptable as TextChoices
because they are architectural constants, not business data.

### Rule 4 — Always Use ForeignKey
```python
# ✅ Correct
location = models.ForeignKey(LocationNode, on_delete=models.CASCADE)

# ❌ Wrong — raw ID
location_id = models.IntegerField()
```

### Rule 5 — Every Important Model Must Support Analytics
Every model that stores operational data MUST have:
- A date field (`report_date`, `created_at`, or similar)
- A relation to `LocationNode` (directly or via parent)
- A relation to `Operation` (directly or via parent)

---

## 2. Location Rule (Critical)

```
ONE location model exists: LocationNode
```

LocationNode type system:
```python
class LocationNode(TenantAwareModel):
    TYPE_CHOICES = [
        ('SECTOR',    'Sector'),     # قطاع
        ('STAGE',     'Stage'),      # مرحلة
        ('ENCLOSURE', 'Enclosure'),  # حوشة
    ]
    farm   = models.ForeignKey(Farm, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    name   = models.CharField(max_length=200)
    type   = models.CharField(max_length=20, choices=TYPE_CHOICES)
```

Do NOT create:
- ❌ `Sector` table
- ❌ `Stage` table
- ❌ `Plot` table
- ❌ `Hosh` table
- ❌ Any other location abstraction

---

## 3. Reusability Rule

Before creating any model, ask:
> "Can this be used in more than one module?"

| Entity | Must be reusable across |
|--------|------------------------|
| `LocationNode` | All modules |
| `Contractor` | Reports, Accounting, Analytics |
| `Operation` | Reports, Analytics |
| `Variety` | Reports, CropRecord, Production |
| `Unit` | Reports, Warehouse |
| `Attachment` | Reports, HR |

If the answer is YES → make it a global shared model, not module-local.

---

## 4. Anti-Patterns (Forbidden)

```python
# ❌ Dropdown table for business entities
class ReportDropdownOption(models.Model):
    type = models.CharField()   # 'operation', 'variety', 'unit'
    value = models.CharField()  # use proper models instead

# ❌ Duplicate models
class PalmRecord(models.Model): ...   # use CropRecord(crop_type='palm')
class OliveRecord(models.Model): ...  # use CropRecord(crop_type='olive')

# ❌ GenericForeignKey (except CustomField system)
content_type = models.ForeignKey(ContentType, ...)
object_id    = models.PositiveIntegerField()
```

---

## 5. Query Optimization Rules

### Always Use:
```python
# select_related for FK traversal (forward)
Report.objects.select_related('engineer', 'operation', 'location', 'farm')

# prefetch_related for reverse relations (one-to-many)
Report.objects.prefetch_related('labor_entries', 'attachments')

# Both together
Report.objects \
    .for_company(company) \
    .select_related('engineer', 'operation', 'location') \
    .prefetch_related('labor_entries')
```

### Index Strategy:
```python
class Meta:
    indexes = [
        models.Index(fields=['company', 'report_date']),
        models.Index(fields=['company', 'operation', 'report_date']),
        models.Index(fields=['engineer', 'report_date']),
    ]
```

Mandatory indexes on: `company`, date fields, `status`, frequently filtered FKs.

---

## 6. Validation Rules

### Prevent Cross-Company Data
```python
# ✅ Always validate tenant scope in serializers
def validate_location(self, value):
    user = self.context['request'].user
    if value.company != user.company:
        raise serializers.ValidationError("Location not found.")
    return value
```

### Prevent Orphan Records
- All models use `on_delete=models.CASCADE` or `SET_NULL` — never `DO_NOTHING`
- Soft delete via `status='terminated'` / `is_active=False` instead of hard delete

---

## 7. Performance Rules

- All list endpoints MUST be paginated: `DEFAULT_PAGINATION_CLASS` with `PAGE_SIZE=25`
- Avoid N+1 queries — always use `select_related`/`prefetch_related`
- Use `values()` or `values_list()` for analytics aggregation queries
- Use `annotate()` + `aggregate()` for computed metrics — never Python loops on querysets

---

## 8. Analytics Readiness

Every model storing operational data must be queryable by:

```python
# Group by date
.values('report_date').annotate(count=Count('id'))

# Group by location
.values('location__id', 'location__name').annotate(total=Sum('workers'))

# Group by operation
.values('operation__name').annotate(avg=Avg('productivity'))
```

If a model cannot support these patterns → its design is wrong.

---

## 9. Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Table names | auto from model | `reports_dailytaskreport` |
| Field names | `snake_case` | `report_date`, `company_workers` |
| FK fields | `entity_name` | `location`, `engineer`, `contractor` |
| Boolean fields | `is_` prefix | `is_active`, `is_approved` |
| Date fields | `_date` or `_at` | `report_date`, `created_at` |
| Status fields | `status` with TextChoices | `status = 'active'` |

---

## 10. Database Result

A correct database is:
- **Normalized** — no redundant data
- **Clean** — no orphan or stale records
- **Scalable** — supports multi-tenant growth
- **Analytics-ready** — every important metric is queryable
- **Secure** — no cross-tenant data access possible
