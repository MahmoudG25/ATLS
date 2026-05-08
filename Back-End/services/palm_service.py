from apps.palm.models import PalmRecord
from rest_framework.exceptions import ValidationError


def list_palm_records(plot_id=None):
    records = PalmRecord.objects.select_related("plot", "plot__sector").all()
    if plot_id:
        records = records.filter(plot_id=plot_id)
    return records


def create_palm_record(data):
    if data.get("trees_count", 0) <= 0:
        raise ValidationError({"trees_count": "Trees count must be greater than 0."})
    return PalmRecord.objects.create(**data)


def update_palm_record(record_id, data):
    if "trees_count" in data and data["trees_count"] <= 0:
        raise ValidationError({"trees_count": "Trees count must be greater than 0."})

    record = PalmRecord.objects.get(id=record_id)
    for key, value in data.items():
        setattr(record, key, value)
    record.save()
    return record
