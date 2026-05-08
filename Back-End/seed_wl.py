import os, sys

sys.stdout.reconfigure(encoding="utf-8")
os.environ["DJANGO_SETTINGS_MODULE"] = "core.settings"
import django

django.setup()
from apps.reports.models import ReportDropdownOption, Operation

wl_items = [
    "المرحلة الاولى",
    "المرحلة الثانية",
    "المرحلة الثالثة",
    "المرحلة الرابعة",
    "المرحلة الخامسة",
    "المرحلة السادسة",
    "المرحلة السابعة",
    "المرحلة الثامنة",
    "التاسعه",
    "العاشره",
    "الليمون",
    "الصوب",
    "كل المزرعة",
]
c = 0
for n in wl_items:
    _, new = ReportDropdownOption.objects.get_or_create(
        name=n.strip(), category="work_location", defaults={"is_active": True}
    )
    if new:
        c += 1

cat_wl = ReportDropdownOption.objects.filter(category="work_location").count()
cat_var = ReportDropdownOption.objects.filter(category="variety").count()
cat_con = ReportDropdownOption.objects.filter(category="contractor").count()
cat_uni = ReportDropdownOption.objects.filter(category="unit").count()
ops = Operation.objects.count()

print(f"work_location new: {c}")
print(f"work_location total: {cat_wl}")
print(f"variety: {cat_var}, contractor: {cat_con}, unit: {cat_uni}")
print(f"operations: {ops}")
