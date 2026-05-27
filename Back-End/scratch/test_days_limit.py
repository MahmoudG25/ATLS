import os
import sys
import django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.users.models import Company
from apps.equipment.models import Equipment, FleetMaintenanceAlert
from services.equipment_service import (
    create_equipment,
    create_equipment_log,
    get_maintenance_alerts,
)
from datetime import date, timedelta

# Find or create a test company
company, _ = Company.objects.get_or_create(name="Test Company")

print("1. Creating motorcycle with days-based tracking...")
eq = create_equipment({
    "name": "Motorcycle M200",
    "equipment_type": "motorcycle",
    "meter_type": "days",
    "maintenance_interval": 10.0,
    "purchase_date": date.today()
}, company)
print(f"Created: {eq.name}, meter_type: {eq.meter_type}, current_meter: {eq.current_meter}")

try:
    print("2. Verifying requires_maintenance (should be False)...")
    eq.refresh_from_db()
    print(f"Meter Delta: {eq.meter_delta}")
    assert not eq.requires_maintenance
    
    print("3. Simulating 11 days elapsed by shifting last_maintenance_date...")
    eq.last_maintenance_date = date.today() - timedelta(days=11)
    eq.save()
    
    eq.refresh_from_db()
    print(f"Meter Delta now: {eq.meter_delta}")
    assert eq.requires_maintenance
    
    print("4. Checking generated alerts...")
    alerts = get_maintenance_alerts(company)
    print(f"Pending alerts count: {alerts.count()}")
    assert alerts.filter(equipment=eq).exists()
    
    print("5. Recording maintenance log today to resolve...")
    log = create_equipment_log({
        "equipment": eq,
        "log_type": "maintenance",
        "date": date.today(),
        "details": "General checkup & cleaning",
        "cost": 50.0
    }, company)
    
    eq.refresh_from_db()
    print(f"After log, last_maintenance_date: {eq.last_maintenance_date}, Delta: {eq.meter_delta}")
    assert not eq.requires_maintenance
    
    # Check alert is resolved
    alerts = get_maintenance_alerts(company)
    assert not alerts.filter(equipment=eq).exists()
    print("Alert successfully resolved!")
    
    print("All assertions passed for days-based logic!")
finally:
    # Clean up
    eq.delete()
    print("Test equipment cleaned up!")
