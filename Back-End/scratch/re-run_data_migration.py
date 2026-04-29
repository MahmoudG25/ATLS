
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.reports.models import Variety, Unit, Contractor, ReportDropdownOption, DailyTaskReport

def migrate_data():
    variety_map = {}
    unit_map = {}
    contractor_map = {}

    # Step 1: Pre-populate models and maps from existing options
    for option in ReportDropdownOption.objects.all():
        if not option.company:
            continue

        option_type = option.category
        
        if option_type == 'contractor':
            obj, _ = Contractor.objects.get_or_create(
                company=option.company,
                name=option.name,
                defaults={'rate_per_hour': 0, 'is_active': True}
            )
            contractor_map[option.pk] = obj.pk

        elif option_type == 'unit':
            obj, _ = Unit.objects.get_or_create(
                company=option.company,
                name=option.name
            )
            unit_map[option.pk] = obj.pk

        elif option_type == 'variety':
            obj, _ = Variety.objects.get_or_create(
                company=option.company,
                name=option.name
            )
            variety_map[option.pk] = obj.pk

    print(f"Created {len(variety_map)} varieties, {len(unit_map)} units, {len(contractor_map)} contractors.")

if __name__ == "__main__":
    migrate_data()
