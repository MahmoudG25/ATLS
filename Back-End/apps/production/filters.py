import django_filters
from .models import HarvestReport
import logging

logger = logging.getLogger(__name__)

class HarvestFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(field_name="harvest_date", lookup_expr="gte")
    end_date = django_filters.DateFilter(field_name="harvest_date", lookup_expr="lte")
    
    # Hierarchical location filter (supports UUIDs)
    location = django_filters.UUIDFilter(method="filter_location")
    
    # Supervisor/Engineer filter
    supervisor = django_filters.UUIDFilter(field_name="supervisor_id")

    class Meta:
        model = HarvestReport
        fields = ["supervisor", "season", "status", "is_partial"]

    def filter_location(self, queryset, name, value):
        if not value:
            return queryset
        try:
            from apps.farm.models import LocationNode
            # Get node and all its children in the hierarchy
            node = LocationNode.objects.get(id=value)
            descendant_ids = node.get_descendants(include_self=True).values_list('id', flat=True)
            return queryset.filter(location_id__in=descendant_ids)
        except Exception as e:
            logger.error(f"Error in harvest location filter: {e}")
            return queryset
