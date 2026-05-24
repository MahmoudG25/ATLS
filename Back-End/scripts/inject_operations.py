
import os
import django
import sys

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
sys.path.append(os.path.join(os.getcwd()))
django.setup()

from apps.reports.models import Operation
from apps.users.models import Company

def inject():
    company = Company.objects.first()
    if not company:
        print("Error: No company found in the database.")
        return

    operations_to_inject = [
        {
            "name": "تلقيح",
            "category_key": "pollination",
            "profile_type": "pollination"
        },
        {
            "name": "إزالة حشائش",
            "category_key": "maintenance",
            "profile_type": "generic"
        },
        {
            "name": "إزالة حشائش+تجوير",
            "category_key": "maintenance",
            "profile_type": "generic"
        },
        {
            "name": "تقليع فسائل",
            "category_key": "planting",
            "profile_type": "generic"
        },
        {
            "name": "زراعة فسائل",
            "category_key": "planting",
            "profile_type": "generic"
        },
        {
            "name": "زراعة الشتلات",
            "category_key": "planting",
            "profile_type": "generic"
        },
        {
            "name": "تجوير",
            "category_key": "maintenance",
            "profile_type": "generic"
        },
        {
            "name": "حفر جور وتجهيز للزراعة",
            "category_key": "maintenance",
            "profile_type": "generic"
        },
        {
            "name": "فك السبايط",
            "category_key": "maintenance",
            "profile_type": "generic"
        },
        {
            "name": "فك الخوص",
            "category_key": "maintenance",
            "profile_type": "generic"
        },
        {
            "name": "إزالة الأربطة",
            "category_key": "maintenance",
            "profile_type": "generic"
        },
        {
            "name": "ازالة العروسه من السبايط",
            "category_key": "maintenance",
            "profile_type": "generic"
        },
        {
            "name": "خصى العروسه",
            "category_key": "maintenance",
            "profile_type": "generic"
        },
        {
            "name": "متابعة عمليات المشتل",
            "category_key": "monitoring",
            "profile_type": "generic"
        },
        {
            "name": "متابعة عملية الفصل",
            "category_key": "monitoring",
            "profile_type": "generic"
        },
        {
            "name": "نقل وتحميل الفسائل",
            "category_key": "transport",
            "profile_type": "generic"
        },
        {
            "name": "صيانة صوب وتنشير أكواز دكار",
            "category_key": "maintenance",
            "profile_type": "generic"
        },
        {
            "name": "رش مبيد حشري",
            "category_key": "protection",
            "profile_type": "generic"
        },
        {
            "name": "توزيع وتنزيل السماد",
            "category_key": "fertilization",
            "profile_type": "fertilization"
        }
    ]

    count = 0
    for op in operations_to_inject:
        obj, created = Operation.objects.get_or_create(
            company=company,
            name=op["name"],
            defaults={
                "category": op["category_key"],
                "profile_type": op["profile_type"],
                "is_active": True
            }
        )
        if created:
            count += 1
        else:
            # Update category if it exists but is different
            if obj.category != op["category_key"]:
                obj.category = op["category_key"]
                obj.save()

    print(f"Injection complete. {count} new operations added.")

if __name__ == "__main__":
    inject()
