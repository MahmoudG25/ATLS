"""
Run with: python manage.py shell < seed_report_options.py
"""

import django, os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from apps.reports.models import ReportDropdownOption, Operation, Season, Unit, Variety
from apps.users.models import Company
from datetime import date

# Attempt to get the first company
try:
    default_company = Company.objects.first()
    if not default_company:
        default_company = Company.objects.create(name="Seed Company")
except Exception as e:
    print(f"Error: {e}")
    default_company = None

# Seed Seasons
SEASONS = [
    ("2024", date(2024, 1, 1), date(2024, 12, 31)),
    ("2025", date(2025, 1, 1), date(2025, 12, 31)),
    ("2026", date(2026, 1, 1), date(2026, 12, 31)),
    ("2027", date(2027, 1, 1), date(2027, 12, 31)),
]

for name, start, end in SEASONS:
    Season.objects.get_or_create(
        name=name, company=default_company,
        defaults={"start_date": start, "end_date": end, "status": "OPEN"}
    )
    print(f"  [OK] Season {name}")

# Seed Units
UNITS = ["كجم", "طن", "صندوق", "عبوة"]
for name in UNITS:
    Unit.objects.get_or_create(name=name, company=default_company)
    print(f"  [OK] Unit {name}")

# Seed Varieties
VARIETIES = ["مجدول", "صقعي", "خلاص", "بارحي"]
for name in VARIETIES:
    Variety.objects.get_or_create(name=name, company=default_company)
    print(f"  [OK] Variety {name}")

print("\nSeeding complete.")
