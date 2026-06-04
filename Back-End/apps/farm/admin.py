from django.contrib import admin
from .models import Farm, LocationNode, FarmSettings, EnclosureProfile, StageProfile

@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_active")

@admin.register(LocationNode)
class LocationNodeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "type", "parent", "farm", "is_active")
    list_filter = ("type", "is_active", "farm")
    search_fields = ("name",)

@admin.register(FarmSettings)
class FarmSettingsAdmin(admin.ModelAdmin):
    list_display = ("id", "farm", "enable_sector", "enable_stage", "enable_enclosure")

@admin.register(EnclosureProfile)
class EnclosureProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "location_node", "crop_type", "tree_count", "planting_year")
    list_filter = ("crop_type",)
    search_fields = ("location_node__name",)

@admin.register(StageProfile)
class StageProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "location_node", "tree_count")
    search_fields = ("location_node__name",)
