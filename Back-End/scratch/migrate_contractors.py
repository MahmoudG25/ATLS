
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.reports.models import Variety, Unit, Contractor, ReportDropdownOption
from apps.users.models import Company

def migrate_data():
    default_company = Company.objects.first()
    if not default_company:
        print("No company found.")
        return

    # Migrate Contractors
    for option in ReportDropdownOption.objects.filter(category='contractor'):
        company = option.company or default_company
        Contractor.objects.get_or_create(
            company=company,
            name=option.name,
            defaults={'rate_per_hour': 0, 'is_active': True}
        )
    
    print(f"Contractors migrated. Total count: {Contractor.objects.count()}")

if __name__ == "__main__":
    migrate_data()
