import os
import django
import sys

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from apps.farm.models import LocationNode
from apps.reports.selectors import get_location_analytics

def test_selector(node_id):
    print(f"--- Testing Selector for Node {node_id} ---")
    try:
        node = LocationNode.objects.get(id=node_id)
        data = get_location_analytics(node)
        print("Success!")
        print("Summary:", data.get('summary'))
    except Exception as e:
        print("EXCEPTION:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_selector(20)
