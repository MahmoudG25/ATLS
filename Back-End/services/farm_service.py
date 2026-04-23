from apps.farm.models import Farm, CropType, Sector, Plot
from apps.olive.models import OliveRecord
from apps.palm.models import PalmRecord
from apps.production.models import AnnualYield
from django.db.models import Sum

def list_farms():
    return Farm.objects.all()

def list_crop_types():
    return CropType.objects.all()

def get_farm_structure(farm_id=None):
    """
    Returns full hierarchy of sectors and their plots
    """
    sectors = Sector.objects.select_related('crop_type').prefetch_related('plots').all()
    if farm_id:
        sectors = sectors.filter(farm_id=farm_id)
    return sectors

def create_sector(data):
    return Sector.objects.create(**data)

def create_plot(data):
    return Plot.objects.create(**data)

def get_plot_stats(plot_id):
    plot = Plot.objects.select_related('sector__crop_type').get(id=plot_id)
    crop_type = plot.sector.crop_type.name.lower()
    
    total_trees = 0
    if 'palm' in crop_type:
        records = PalmRecord.objects.filter(plot=plot)
        total_trees = sum([r.trees_count for r in records])
    else:
        records = OliveRecord.objects.filter(plot=plot)
        total_trees = sum([r.trees_count for r in records])
        
    total_yield = AnnualYield.objects.filter(plot=plot).aggregate(Sum('production_amount'))['production_amount__sum'] or 0

    return {
        'total_trees': total_trees,
        'lifetime_yield': total_yield
    }
