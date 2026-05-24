
import os
import django
import uuid

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from apps.reports.models import Operation, Unit, Variety
from apps.users.models import Company

def seed_data():
    company = Company.objects.first()
    if not company:
        print("No company found. Please register first.")
        return

    # Seed Operations
    ops = [
        {"name": "تسميد ورقي", "category": "fertilization", "profile_type": "fertilization"},
        {"name": "ري غمر", "category": "other", "profile_type": "irrigation"},
        {"name": "مكافحة سوسة النخيل", "category": "protection", "profile_type": "generic"},
        {"name": "جني وتقليم", "category": "maintenance", "profile_type": "harvest"},
    ]
    for op_data in ops:
        Operation.objects.get_or_create(
            company=company,
            name=op_data["name"],
            defaults={
                "category": op_data["category"],
                "profile_type": op_data["profile_type"],
                "is_active": True
            }
        )

    # Seed Units
    units = ["كيلو", "نخلة", "شجرة", "ساعة", "فدان"]
    for unit_name in units:
        Unit.objects.get_or_create(company=company, name=unit_name)

    # Seed Varieties
    varieties = ["سيوي", "مجدول", "بارحي", "زيتون تفاحي"]
    for var_name in varieties:
        Variety.objects.get_or_create(company=company, name=var_name)

    print("Successfully seeded Operations, Units, and Varieties.")

if __name__ == "__main__":
    seed_data()
