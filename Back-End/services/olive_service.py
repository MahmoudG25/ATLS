from apps.olive.models import OliveRecord
from rest_framework.exceptions import ValidationError

def list_olive_records(plot_id=None):
    records = OliveRecord.objects.select_related('plot', 'plot__sector').all()
    if plot_id:
        records = records.filter(plot_id=plot_id)
    return records

def create_olive_record(data):
    if data.get('trees_count', 0) <= 0:
        raise ValidationError({'trees_count': 'Trees count must be greater than 0.'})
    return OliveRecord.objects.create(**data)

def update_olive_record(record_id, data):
    if 'trees_count' in data and data['trees_count'] <= 0:
        raise ValidationError({'trees_count': 'Trees count must be greater than 0.'})
        
    record = OliveRecord.objects.get(id=record_id)
    for key, value in data.items():
        setattr(record, key, value)
    record.save()
    return record
