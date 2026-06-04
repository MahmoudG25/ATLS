import os
import sys
import django

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from apps.farm.models import Farm, LocationNode, EnclosureProfile, StageProfile
from apps.users.models import Company
from django.core.exceptions import ValidationError

print("Testing validations...")
company = Company.objects.first()
farm = Farm.objects.first()

# Create test stage
stage = LocationNode.objects.create(
    company=company,
    farm=farm,
    name="مرحلة تجريبية",
    type=LocationNode.TYPE_STAGE,
    order=100
)
stage_profile = StageProfile.objects.create(
    company=company,
    location_node=stage,
    tree_count=1000
)

# Create enclosure 1
enc1 = LocationNode.objects.create(
    company=company,
    farm=farm,
    parent=stage,
    name="حوشة تجريبية 1",
    type=LocationNode.TYPE_ENCLOSURE,
    order=101
)
enc1_profile = EnclosureProfile.objects.create(
    company=company,
    location_node=enc1,
    tree_count=600
)

# Create enclosure 2
enc2 = LocationNode.objects.create(
    company=company,
    farm=farm,
    parent=stage,
    name="حوشة تجريبية 2",
    type=LocationNode.TYPE_ENCLOSURE,
    order=102
)
enc2_profile = EnclosureProfile.objects.create(
    company=company,
    location_node=enc2,
    tree_count=300
)

print(f"Total Stage Limit: {stage_profile.tree_count}")
print(f"Enclosure 1: {enc1_profile.tree_count}")
print(f"Enclosure 2: {enc2_profile.tree_count}")
print(f"Current sum: {enc1_profile.tree_count + enc2_profile.tree_count} (<= 1000, OK)")

# Try to update enc2 to 500 (total = 1100 > 1000, should fail)
try:
    enc2_profile.tree_count = 500
    enc2_profile.clean()
    enc2_profile.save()
    print("Error: validation failed to trigger (total exceeded stage limit but saved!)")
except ValidationError as e:
    print(f"Success: validation triggered correctly as expected: {e}")

# Try to update stage tree count to 800 (below current enclosures total 900, should fail)
try:
    stage_profile.tree_count = 800
    stage_profile.clean()
    stage_profile.save()
    print("Error: validation failed to trigger (stage limit set below enclosures sum but saved!)")
except ValidationError as e:
    print(f"Success: validation triggered correctly as expected: {e}")

# Cleanup
enc1_profile.delete()
enc2_profile.delete()
enc1.delete()
enc2.delete()
stage_profile.delete()
stage.delete()
print("Cleanup completed.")
