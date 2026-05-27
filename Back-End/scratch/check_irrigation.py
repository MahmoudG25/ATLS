import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from apps.reports.models import IrrigationReport, OperationalLocationAllocation
from django.contrib.contenttypes.models import ContentType

reports = IrrigationReport.objects.all()[:10]
print(f"Total reports: {IrrigationReport.objects.count()}")
for r in reports:
    print(f"ID: {r.id}, Date: {r.date}, CoWorkers: {r.company_workers}, ContWorkers: {r.contractor_workers}, ContWorkersA: {r.contractor_workers_a}, ContWorkersB: {r.contractor_workers_b}")
    content_type = ContentType.objects.get_for_model(r)
    allocs = OperationalLocationAllocation.objects.filter(content_type=content_type, object_id=r.id)
    for a in allocs:
        print(f"  Alloc Enclosure: {a.enclosure.name}, Co: {a.allocated_workers_company}, A: {a.allocated_workers_contractor_a}, B: {a.allocated_workers_contractor_b}")
