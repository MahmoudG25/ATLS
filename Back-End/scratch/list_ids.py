
import os
import django
import sys

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.reports.models import Variety, Unit, Contractor

def list_ids():
    print("Varieties:")
    for v in Variety.objects.all():
        print(f"  ID: {v.id}, Name: {v.name}")
    
    print("\nUnits:")
    for u in Unit.objects.all():
        print(f"  ID: {u.id}, Name: {u.name}")
        
    print("\nContractors:")
    for c in Contractor.objects.all():
        print(f"  ID: {c.id}, Name: {c.name}")

if __name__ == "__main__":
    list_ids()
