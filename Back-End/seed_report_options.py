"""
Run with: python manage.py shell < seed_report_options.py
"""

import django, os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from apps.reports.models import ReportDropdownOption, Operation

DATA = {
    "variety": [
        "مجدول",
        "ليمون",
        "الصوب",
        "اخرى",
        "كل الاصناف",
    ],
    "contractor": [
        "1",
        "2",
        "3",
        "7",
        "8",
        "1+2",
        "7+8",
        "1/7",
        "2/7",
        "خارجي",
        "مقاول خارجي",
    ],
    "unit": [
        "نخلة",
        "جورة",
        "فسيلة",
        "فسيلة+كوز",
        "كوز",
        "حوشة",
        "تحضيرة",
        "تحضيره",
    ],
    "enclosure": [],
}

OPERATIONS = [
    "تلقيح",
    "إزالة حشائش",
    "إزالة حشائش+تجوير",
    "تقليع فسائل",
    "زراعة فسائل",
    "زراعة الشتلات",
    "تجوير",
    "حفر جور وتجهيز للزراعة",
    "فك السبايط",
    "فك الخوص",
    "إزالة الأربطة",
    "ازالة العروسه من السبايط",
    "خصى العروسه",
    "متابعة عمليات المشتل",
    "متابعة عملية الفصل",
    "نقل وتحميل الفسائل",
    "صيانة صوب وتنشير أكواز دكار",
    "رش مبيد حشري",
    "توزيع وتنزيل السماد",
]

created = 0
skipped = 0

for category, names in DATA.items():
    for raw in names:
        name = raw.strip()
        if not name:
            continue
        obj, is_new = ReportDropdownOption.objects.get_or_create(
            name=name, category=category, defaults={"is_active": True}
        )
        if is_new:
            created += 1
            print(f"  [OK] Created [{category}] {name}")
        else:
            skipped += 1

for raw in OPERATIONS:
    name = raw.strip()
    if not name:
        continue
    obj, is_new = Operation.objects.get_or_create(
        name=name, defaults={"category": "other"}
    )
    if is_new:
        created += 1
        print(f"  [OK] Created [operation] {name}")
    else:
        skipped += 1

print(f"\nDone. Created: {created}, Skipped (already exist): {skipped}")
