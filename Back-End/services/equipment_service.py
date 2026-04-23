from apps.equipment.models import Equipment, Maintenance, Usage

def get_equipment_list():
    return Equipment.objects.all()

def create_equipment(data):
    return Equipment.objects.create(**data)

def get_equipment_details(equipment_id):
    eq = Equipment.objects.get(id=equipment_id)
    maintenances = eq.maintenances.all().order_by('-date')
    usages = eq.usages.all().order_by('-date')
    return {
        'equipment': eq,
        'maintenances': maintenances,
        'usages': usages
    }

def create_maintenance(data):
    return Maintenance.objects.create(**data)

def create_usage(data):
    return Usage.objects.create(**data)
