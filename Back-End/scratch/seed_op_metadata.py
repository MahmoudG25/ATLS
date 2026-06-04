import os
import sys
import django

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from apps.reports.models import Operation

print("Seeding Operation Metadata Sensible Defaults...")
print("-" * 60)

for op in Operation.objects.all():
    name = op.name.lower()
    cat = op.category.lower()
    
    # Sensible default rule engine
    coverage_type = "TIME_BASED"
    repeatable = True
    allow_over_coverage = True
    
    if "تلقيح" in name or cat == "pollination":
        coverage_type = "TREE_BASED"
        allow_over_coverage = False
    elif "تقليم" in name or "تكريب" in name or "جني وتقليم" in name:
        coverage_type = "TREE_BASED"
        allow_over_coverage = False
    elif "مكافحة" in name or "سوسة" in name or "رش مبيد" in name or cat == "protection":
        coverage_type = "TREE_BASED"
        allow_over_coverage = False
    elif "زراعة" in name or "تقليع" in name or cat == "planting":
        coverage_type = "TREE_BASED"
        allow_over_coverage = False
    elif "حشائش" in name or "تجوير" in name or "إزالة الأربطة" in name or "العروسه" in name or "فك السبايط" in name or "فك الخوص" in name:
        coverage_type = "TREE_BASED"
        allow_over_coverage = False
    elif "حصاد" in name or "تعبئة" in name:
        coverage_type = "PRODUCTION_BASED"
        allow_over_coverage = True
    elif "متابعة" in name or cat == "monitoring":
        coverage_type = "EVENT_BASED"
        allow_over_coverage = True
    elif "ري" in name or "صيانة" in name or cat == "maintenance":
        coverage_type = "TIME_BASED"
        allow_over_coverage = True
        
    # Update operation
    op.coverage_type = coverage_type
    op.repeatable = repeatable
    op.allow_over_coverage = allow_over_coverage
    op.save()
    print(f"Updated '{op.name}': coverage_type={op.coverage_type}, allow_over_coverage={op.allow_over_coverage}")

print("Seeding Operation Metadata Completed Successfully.")
