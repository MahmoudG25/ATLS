from django.core.exceptions import ValidationError
from django.db import models


class TenantQuerySet(models.QuerySet):
    def for_company(self, company):
        if company is None:
            return self.none()
        
        from django.db import models
        if hasattr(self.model, 'is_system'):
            return self.filter(models.Q(company=company) | models.Q(is_system=True))
            
        return self.filter(company=company)


class TenantManager(models.Manager):
    def get_queryset(self):
        return TenantQuerySet(self.model, using=self._db)

    def for_company(self, company):
        return self.get_queryset().for_company(company)


from core.models import BaseEntity

class TenantAwareModel(BaseEntity):
    company = models.ForeignKey("users.Company", on_delete=models.CASCADE)
    objects = TenantManager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def assert_same_company(self, obj, path_name):
        obj_company_id = getattr(obj, "company_id", None)
        if obj_company_id and obj_company_id != self.company_id:
            raise ValidationError({path_name: "Invalid tenant relation"})
