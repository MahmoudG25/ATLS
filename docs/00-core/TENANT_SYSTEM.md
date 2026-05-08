# Tenant System — ATLS Farm ERP

> **Authority**: Tier 1. Defines multi-tenant isolation rules.

---

## 1. Tenant Model

The tenant unit is `Company`. Every piece of data belongs to exactly one Company.

```python
class Company(models.Model):
    name       = models.CharField(max_length=200)
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

---

## 2. TenantAwareModel — Base Class

Every data model MUST inherit this:

```python
class TenantAwareModel(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='%(class)s_set'
    )

    objects = TenantManager()

    class Meta:
        abstract = True
```

The `TenantManager` provides the scoped queryset:

```python
class TenantManager(models.Manager):
    def for_company(self, company):
        return self.filter(company=company)
```

---

## 3. Tenant Isolation Rules

### Golden Rule
```python
# ❌ NEVER — unscoped query (security breach)
DailyTaskReport.objects.all()
DailyTaskReport.objects.filter(date=today)

# ✅ ALWAYS — company-scoped
DailyTaskReport.objects.for_company(request.user.company)
DailyTaskReport.objects.for_company(request.user.company).filter(date=today)
```

### FK Validation Rule
Every serializer that accepts a FK must validate same-company ownership:
```python
def validate_location(self, value):
    if value.company != self.context['request'].user.company:
        raise serializers.ValidationError("Not found.")
    return value
```

### Nested Serializer Rule
Nested serializers must never expose cross-company data:
```python
# ✅ Scoped nested queryset
class ReportSerializer(serializers.ModelSerializer):
    def get_location(self, obj):
        # obj.location is already company-scoped by the queryset
        return LocationSerializer(obj.location).data
```

---

## 4. User-Tenant Relationship

```python
class User(AbstractUser):
    company    = models.ForeignKey(Company, on_delete=models.CASCADE)
    role       = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_approved = models.BooleanField(default=False)
```

- A User belongs to exactly one Company
- A User cannot access data from another Company (except SUPER_ADMIN)
- `is_approved=False` users cannot authenticate

---

## 5. SUPER_ADMIN Exception

SUPER_ADMIN is the only role that can cross company boundaries:

```python
def get_queryset(self):
    user = self.request.user
    if user.role == 'SUPER_ADMIN':
        return DailyTaskReport.objects.all().select_related(...)
    return DailyTaskReport.objects.for_company(user.company).select_related(...)
```

This exception MUST always be explicit — never implicit.

---

## 6. Data Creation Rule

When creating any record, always inject company from the authenticated user:

```python
def perform_create(self, serializer):
    serializer.save(
        company=self.request.user.company,
        created_by=self.request.user
    )
```

Never accept `company` from request data — it must come from the JWT token.

---

## 7. Tenant Checklist Per Endpoint

```
[ ] Queryset uses .for_company(request.user.company)
[ ] All FK fields validated for same company
[ ] company injected from request.user on create
[ ] Nested data is also scoped
[ ] SUPER_ADMIN check is explicit if cross-company is needed
```

---

## 8. SaaS Configuration Model

Each Company can configure:
- Farm name and type
- LocationNode hierarchy (via Admin Dashboard)
- Custom report fields (`CustomFieldDefinition`)
- Contractor list
- Operation types
- Variety/crop types

This means **zero code changes** when onboarding a new farm tenant.
All configuration lives in the database, not in code.
