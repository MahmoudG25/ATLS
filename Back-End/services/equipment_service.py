from apps.equipment.models import Equipment, Maintenance, Usage, OilChangeLog
from datetime import date


def get_equipment_list(company):
    return Equipment.objects.filter(company=company)


def create_equipment(data, company):
    data["company"] = company
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
