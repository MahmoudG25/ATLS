import os
import django
import sys
from django.test import RequestFactory

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from apps.farm.models import LocationNode
from api.endpoints.farm_views import location_node_profile_view, location_node_analytics_view
from unittest.mock import MagicMock

def debug_endpoints(node_id):
    # Mock request with user
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.first()
    
    request = MagicMock()
    request.user = user
    request.query_params = {}
    
    print(f"\n--- Debugging Node {node_id} ---")
    
    # 1. Check Data Existence
    try:
        node = LocationNode.objects.get(id=node_id)
        print(f"Node Found: {node.name} ({node.type})")
        has_profile = hasattr(node, 'enclosureprofile')
        print(f"Has EnclosureProfile: {has_profile}")
    except LocationNode.DoesNotExist:
        print(f"ERROR: Node {node_id} does not exist.")
        return

    # 2. Test Profile View
    print("\n[Testing Profile View]")
    try:
        response = location_node_profile_view(request, pk=node_id)
        print(f"Response Status: {response.status_code}")
        if response.status_code == 500:
             print("Data: ", response.data if hasattr(response, 'data') else "No data")
    except Exception as e:
        print("EXCEPTION in Profile View:")
        import traceback
        traceback.print_exc()

    # 3. Test Analytics View
    print("\n[Testing Analytics View]")
    try:
        response = location_node_analytics_view(request, pk=node_id)
        print(f"Response Status: {response.status_code}")
    except Exception as e:
        print("EXCEPTION in Analytics View:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_endpoints(20)
