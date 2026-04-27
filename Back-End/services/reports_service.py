from apps.reports.models import DailyTaskReport

def list_reports(engineer_id=None, location_id=None):
    qs = DailyTaskReport.objects.select_related('engineer', 'location').all().order_by('-report_date')
    if engineer_id:
        qs = qs.filter(engineer_id=engineer_id)
    if location_id:
        qs = qs.filter(location_id=location_id)
    return qs

def create_report(user, data):
    data['engineer'] = user
    data['company'] = getattr(user, 'company', None)
    return DailyTaskReport.objects.create(**data)
