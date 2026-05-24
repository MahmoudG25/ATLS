import os
import sys
import django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.users.models import Company
from services.equipment_service import (
    create_equipment,
    create_usage,
    create_oil_change,
    get_oil_change_alerts,
    get_equipment_details
)
from datetime import date

# Find or create a test company
company, _ = Company.objects.get_or_create(name="Test Company")

print("1. Creating equipment...")
eq = create_equipment({
    "name": "Tractor X100",
    "type": "TRACTOR",
    "model": "2025",
    "serial_number": "TX-12345",
    "oil_change_interval_hours": 200.0,
    "oil_change_interval_days": 100,
    "specifications": {"engine": "V8"}
}, company)
print(f"Created equipment: {eq.name}, ID: {eq.id}")

try:
    print("2. Verifying initial alerts (should be empty because current_hours is 0)...")
    alerts = get_oil_change_alerts(company)
    print(f"Alerts found: {len(alerts)}")

    print("3. Logging usage to exceed oil change interval (250 hours)...")
    usage = create_usage({
        "equipment": eq,
        "date": date.today(),
        "hours_used": 250.0,
        "fuel_consumption": 50.0
    }, company)
    
    # Reload equipment
    eq.refresh_from_db()
    print(f"Usage logged. Equipment hours: {eq.current_hours}")

    print("4. Checking alerts now (should have 1 alert)...")
    alerts = get_oil_change_alerts(company)
    print(f"Alerts found: {len(alerts)}")
    assert len(alerts) == 1, f"Expected 1 alert, got {len(alerts)}"
    print("Alert verification passed!")

    print("5. Logging oil change...")
    oil_change = create_oil_change({
        "equipment": eq,
        "date": date.today(),
        "hours_at_change": 250.0,
        "cost": 120.0,
        "notes": "Premium synthetic oil used"
    }, company)
    print(f"Oil change logged at: {oil_change.hours_at_change} hrs")

    print("6. Verifying equipment updated stats...")
    eq.refresh_from_db()
    print(f"Last oil change hours: {eq.last_oil_change_hours}")
    print(f"Last oil change date: {eq.last_oil_change_date}")
    assert eq.last_oil_change_hours == 250.0
    assert eq.last_oil_change_date == date.today()

    print("7. Checking alerts after oil change (should be empty)...")
    alerts = get_oil_change_alerts(company)
    print(f"Alerts found: {len(alerts)}")
    assert len(alerts) == 0, f"Expected 0 alerts, got {len(alerts)}"

    print("All assertions passed!")
finally:
    # Clean up
    eq.delete()
    print("Test equipment cleaned up!")
