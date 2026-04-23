from apps.reports.models import DailyReport

def list_reports(engineer_id=None, sector_id=None):
    qs = DailyReport.objects.select_related('engineer', 'sector', 'plot').all().order_by('-date')
    if engineer_id:
        qs = qs.filter(engineer_id=engineer_id)
    if sector_id:
        qs = qs.filter(sector_id=sector_id)
    return qs

def create_report(user, data):
    data['engineer'] = user
    return DailyReport.objects.create(**data)
