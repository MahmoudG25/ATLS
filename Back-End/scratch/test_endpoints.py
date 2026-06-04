import os
import sys
import django

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from apps.reports.models import Season
from apps.reports.selectors import get_operation_coverage, irrigation_analytics_by_season, harvest_analytics_by_season
from apps.users.models import Company

company = Company.objects.first()
season = Season.objects.filter(company=company).first()

if season:
    print(f"Testing selectors with Season: {season.name} ({season.id})")
    print("-" * 60)
    
    # Operation Coverage
    coverage_data = get_operation_coverage(company, season.id)
    print(f"Operation Coverage (Summary Count): {len(coverage_data)}")
    if coverage_data:
        print(f"First Op: {coverage_data[0]['operation_name']} -> coverage: {coverage_data[0]['coverage_pct']}%")
        
    # Irrigation
    irr_data = irrigation_analytics_by_season(company, season.id)
    print(f"Irrigation (Summary Count): {len(irr_data)}")
    if irr_data:
        print(f"First Stage Irrigation: {irr_data[0]['stage_name']} -> hours: {irr_data[0]['total_hours']}")
        
    # Harvest
    har_data = harvest_analytics_by_season(company, season.id)
    print(f"Harvest (Summary Count): {len(har_data)}")
    if har_data:
        print(f"First Location Harvest: {har_data[0]['location_name']} -> total: {har_data[0]['total_harvested']}")

else:
    print("No seasons found in database.")
