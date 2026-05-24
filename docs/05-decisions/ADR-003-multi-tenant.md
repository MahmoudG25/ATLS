# ADR-003 — Multi-Tenant Architecture (Company-Scoped Isolation)

- **Status**: Accepted
- **Date**: 2026-05
- **Deciders**: System Architect

---

## Context

ATLS is designed as a SaaS platform to be sold to multiple farm companies.
Each company must have complete data isolation — no data leakage between tenants.

The challenge: how to implement multi-tenancy without a separate database per tenant
(which would make deployment and maintenance extremely expensive).

---

## Decision

**Single database, row-level tenant isolation via `company` FK on every model.**

```python
class TenantAwareModel(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    class Meta:
        abstract = True

class TenantManager(models.Manager):
    def for_company(self, company):
        return self.filter(company=company)
```

Every queryset in every view MUST use `.for_company(request.user.company)`.
Company is never accepted from request data — it comes from the JWT token.

---

## Rationale

| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| Separate DB per tenant | Perfect isolation | Complex ops, expensive | ❌ Rejected |
| Schema-per-tenant | Good isolation | Django doesn't support well | ❌ Rejected |
| Row-level (company FK) | Simple, cheap, Django-native | Must be disciplined in queries | ✅ **Chosen** |

---

## Consequences

**Positive:**
- Simple deployment — one database, one Django instance
- Standard Django ORM — no special libraries
- SUPER_ADMIN can query across tenants easily
- Easy to onboard new companies via Admin Dashboard

**Negative:**
- Every queryset must be explicitly scoped — discipline required
- A missed `.for_company()` is a data leak (caught by code review + pre-commit checks)

**Mitigations:**
- `TenantManager.for_company()` makes scoping easy
- `AI_AGENT_RULES.md` explicitly forbids unscoped queries
- Pre-commit checklist includes tenant scope verification
- Serializer-level FK validation catches cross-company references

---

## SUPER_ADMIN Exception

SUPER_ADMIN bypasses tenant isolation. This is intentional:
- System management requires cross-company visibility
- This exception must always be explicit in code:

```python
if request.user.role == 'SUPER_ADMIN':
    queryset = Model.objects.all()
else:
    queryset = Model.objects.for_company(request.user.company)
```

---

## References
- `00-core/TENANT_SYSTEM.md`
- `00-core/DATABASE_RULES.md`
- `00-core/PERMISSIONS.md`
