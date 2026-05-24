from apps.farm.models import Farm

def list_farms(company=None):
    qs = Farm.objects.filter(is_active=True)
    if company:
        qs = qs.filter(company=company)
    return qs
