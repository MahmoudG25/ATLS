from apps.production.models import AnnualYield
from rest_framework.exceptions import ValidationError

def get_yields(plot_id=None, year=None):
    qs = AnnualYield.objects.select_related('plot', 'plot__sector').all().order_by('-year')
    if plot_id:
        qs = qs.filter(plot_id=plot_id)
    if year:
        qs = qs.filter(year=year)
    return qs

def create_yield(data):
    if AnnualYield.objects.filter(plot=data['plot'], year=data['year']).exists():
        raise ValidationError({'detail': 'A yield record for this plot and year already exists.'})
    return AnnualYield.objects.create(**data)
