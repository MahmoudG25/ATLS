from apps.equipment.models import (
    Equipment,
    Maintenance,
    Usage,
    OilChangeLog,
    EquipmentLog,
    FleetMaintenanceAlert,
)
from datetime import date
from django.db import transaction


def get_equipment_list(company):
    return Equipment.objects.filter(company=company).order_by('-created_at')


def create_equipment(data, company):
    data["company"] = company
    
    # Map front-end fields if present
    if "type" in data and not "equipment_type" in data:
        t_val = data["type"].lower()
        if t_val == "harvester":
            data["equipment_type"] = "tractor"
        elif t_val == "truck":
            data["equipment_type"] = "car"
        elif t_val == "irrigation_pump":
            data["equipment_type"] = "generator"
        else:
            data["equipment_type"] = t_val if t_val in ['tractor', 'car', 'motorcycle', 'generator', 'sprayer'] else 'tractor'
            
    if "serial_number" in data and not "plate_number" in data:
        data["plate_number"] = data["serial_number"]

    # Map meter type based on equipment type
    if not "meter_type" in data:
        if data.get("equipment_type") == "car":
            data["meter_type"] = "km"
        elif data.get("equipment_type") == "motorcycle":
            data["meter_type"] = "days"
        else:
            data["meter_type"] = "hours"

    if "current_hours" in data and not "current_meter" in data:
        data["current_meter"] = data["current_hours"]

    if "current_meter" in data and not "last_maintenance_meter" in data:
        data["last_maintenance_meter"] = data["current_meter"]

    return Equipment.objects.create(**data)


def get_equipment_details(equipment_id, company):
    eq = Equipment.objects.get(id=equipment_id, company=company)
    maintenances = eq.maintenances.filter(company=company).order_by("-date")
    usages = eq.usages.filter(company=company).order_by("-date")
    oil_changes = eq.oil_changes.filter(company=company).order_by("-date")
    return {
        "equipment": eq,
        "maintenances": maintenances,
        "usages": usages,
        "oil_changes": oil_changes,
    }


def create_maintenance(data, company):
    data["company"] = company
    return Maintenance.objects.create(**data)


def create_usage(data, company):
    data["company"] = company
    usage = Usage.objects.create(**data)
    
    # Automatically update current running hours on the equipment
    eq = usage.equipment
    eq.current_hours += usage.hours_used
    eq.current_meter = eq.current_hours
    eq.save()
    
    return usage


def create_oil_change(data, company):
    data["company"] = company
    log = OilChangeLog.objects.create(**data)
    
    # Automatically update last oil change stats on the equipment
    eq = log.equipment
    eq.last_oil_change_hours = log.hours_at_change
    eq.last_oil_change_date = log.date
    eq.save()
    
    return log


def get_oil_change_alerts(company):
    """
    Returns a list of equipment that are due for an oil change.
    Criteria:
      - (current_hours - last_oil_change_hours) >= oil_change_interval_hours
      OR
      - last_oil_change_date is set and (today - last_oil_change_date).days >= oil_change_interval_days
    """
    equipment_list = Equipment.objects.filter(company=company)
    alerts = []
    today = date.today()
    
    for eq in equipment_list:
        hours_since_change = eq.current_hours - eq.last_oil_change_hours
        days_since_change = None
        if eq.last_oil_change_date:
            days_since_change = (today - eq.last_oil_change_date).days
            
        due_by_hours = hours_since_change >= eq.oil_change_interval_hours
        due_by_days = False
        if days_since_change is not None:
            due_by_days = days_since_change >= eq.oil_change_interval_days
            
        if due_by_hours or due_by_days:
            alerts.append({
                "id": str(eq.id),
                "name": eq.name,
                "type": eq.type,
                "current_hours": float(eq.current_hours),
                "last_oil_change_hours": float(eq.last_oil_change_hours),
                "last_oil_change_date": str(eq.last_oil_change_date) if eq.last_oil_change_date else None,
                "hours_since_change": float(hours_since_change),
                "days_since_change": days_since_change,
                "oil_change_interval_hours": float(eq.oil_change_interval_hours),
                "oil_change_interval_days": eq.oil_change_interval_days,
                "due_by_hours": due_by_hours,
                "due_by_days": due_by_days,
            })
            
    return alerts


# ── Upgraded API Service Handlers ──

def create_equipment_log(data, company):
    data["company"] = company
    
    with transaction.atomic():
        eq = data["equipment"]
        
        # If days-based, automatically override/calculate meter_reading
        if eq.meter_type == 'days':
            start = eq.purchase_date or (eq.created_at.date() if eq.created_at else date.today())
            data["meter_reading"] = (data["date"] - start).days
            
        log = EquipmentLog.objects.create(**data)
        
        # Update current meter reading on the equipment
        if log.meter_reading > eq.current_meter:
            eq.current_meter = log.meter_reading
            eq.current_hours = log.meter_reading  # compatibility
            eq.save()
            
        # Double-write to legacy tables to maintain reporting compatibility
        if log.log_type == 'maintenance':
            Maintenance.objects.create(
                company=company,
                equipment=eq,
                date=log.date,
                notes=log.details,
                cost=log.cost
            )
            # Resolve maintenance alerts and update last maintenance counters
            eq.last_maintenance_meter = eq.current_meter
            eq.last_maintenance_date = log.date
            eq.save()
            FleetMaintenanceAlert.objects.filter(equipment=eq, is_resolved=False).update(is_resolved=True)
            
        elif log.log_type == 'oil_change':
            notes_str = f"{log.details} | الكمية: {log.amount_liters} لتر" if log.amount_liters else log.details
            OilChangeLog.objects.create(
                company=company,
                equipment=eq,
                date=log.date,
                hours_at_change=log.meter_reading,
                notes=notes_str,
                cost=log.cost
            )
            # Update last oil change stats
            eq.last_oil_change_hours = log.meter_reading
            eq.last_oil_change_date = log.date
            # Also reset maintenance counters for this oil change event
            eq.last_maintenance_meter = eq.current_meter
            eq.last_maintenance_date = log.date
            eq.save()
            FleetMaintenanceAlert.objects.filter(equipment=eq, is_resolved=False).update(is_resolved=True)
            
        elif log.log_type == 'fueling':
            Usage.objects.create(
                company=company,
                equipment=eq,
                date=log.date,
                hours_used=0.0,
                fuel_consumption=log.amount_liters,
                operator=log.assigned_operator.name if log.assigned_operator else ""
            )
            
        return log


def get_maintenance_alerts(company):
    return FleetMaintenanceAlert.objects.filter(company=company, is_resolved=False)


def resolve_maintenance_alert(alert_id, company):
    with transaction.atomic():
        alert = FleetMaintenanceAlert.objects.get(id=alert_id, company=company)
        alert.is_resolved = True
        alert.save()
        
        # Update equipment's last maintenance meter to current_meter to reset delta
        eq = alert.equipment
        eq.last_maintenance_meter = eq.current_meter
        eq.last_maintenance_date = date.today()
        eq.save()
        
        return alert

