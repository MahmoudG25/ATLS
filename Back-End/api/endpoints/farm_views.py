from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.farm.models import Farm, LocationNode, FarmSettings
from serializers.farm_serializers import (
    FarmSerializer,
    LocationNodeCreateSerializer,
    LocationNodeSerializer,
    FarmSettingsSerializer,
)
from services.farm_service import list_farms
from services.activity_service import log_activity
from permissions.role_permissions import HasModuleAccess


def _get_active_farm(user):
    """
    Resolves the active Farm for the given user.
    - Super Admins have no company FK, so they get the first active farm globally.
    - Regular users are scoped to their company's farm.
    Returns None if no active farm is found.
    """
    qs = Farm.objects.filter(is_active=True)
    if getattr(user, "is_superuser", False) or not getattr(user, "company_id", None):
        return qs.first()
    return qs.filter(company_id=user.company_id).first()


from rest_framework.pagination import PageNumberPagination

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def farms_list_view(request):
    farms = list_farms(company=getattr(request.user, "company", None))
    
    search_query = request.query_params.get("search", None)
    if search_query:
        farms = farms.filter(name__icontains=search_query)
        
    paginator = PageNumberPagination()
    paginator.page_size = 25
    result_page = paginator.paginate_queryset(farms, request)
    serializer = FarmSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def farm_settings_view(request):
    """
    GET: Retrieve the settings for the active farm.
    PATCH: Update the settings.
    """
    farm = _get_active_farm(request.user)

    if not farm:
        return Response(
            {"detail": "No active farm found."}, status=status.HTTP_400_BAD_REQUEST
        )

    # get_or_create to ensure every farm has a settings record
    # Use farm.company as the tenant
    settings_obj, _ = FarmSettings.objects.get_or_create(
        farm=farm, defaults={"company": farm.company}
    )

    if request.method == "PATCH":
        serializer = FarmSettingsSerializer(
            settings_obj, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        log_activity(request.user, f"Updated Farm Settings for {farm.name}", "Farm")
        return Response(serializer.data)

    serializer = FarmSettingsSerializer(settings_obj)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def location_tree_view(request):
    """
    Returns a recursive tree of LocationNodes for the active farm.
    Optionally filters based on FarmSettings if ?filtered=1 is passed.
    """
    farm = _get_active_farm(request.user)

    if not farm:
        return Response({"tree": [], "farm": None})

    settings_obj, _ = FarmSettings.objects.get_or_create(
        farm=farm, defaults={"company": farm.company}
    )
    apply_filter = request.query_params.get("filtered") == "1"

    nodes = list(
        LocationNode.objects.filter(farm=farm, is_active=True).order_by(
            "order", "created_at"
        )
    )

    # Build a lookup dictionary
    node_map = {
        node.id: {
            "id": node.id,
            "name": node.name,
            "type": node.type,
            "parent_id": node.parent_id,
            "children": [],
        }
        for node in nodes
    }

    tree = []
    for node in nodes:
        node_data = node_map[node.id]

        # Filtering logic: Skip disabled node types
        if apply_filter:
            if node.type == LocationNode.TYPE_SECTOR and not settings_obj.enable_sector:
                continue
            if node.type == LocationNode.TYPE_STAGE and not settings_obj.enable_stage:
                continue
            if (
                node.type == LocationNode.TYPE_ENCLOSURE
                and not settings_obj.enable_enclosure
            ):
                continue

        if node.parent_id and node.parent_id in node_map:
            node_map[node.parent_id]["children"].append(node_data)
        else:
            tree.append(node_data)

    return Response(
        {
            "tree": tree,
            "farm": FarmSerializer(farm).data,
            "settings": FarmSettingsSerializer(settings_obj).data,
        }
    )


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def location_nodes_view(request):
    """
    GET  /farm/location-nodes/?type=STAGE
    GET  /farm/location-nodes/?type=ENCLOSURE&parent=<node_id>
    POST /farm/location-nodes/  — create a new LocationNode

    GET: Returns active LocationNodes filtered by type and optionally parent.
    POST: Creates a new node with full nesting validation.
    """
    farm = _get_active_farm(request.user)

    # ── POST: create a new node ───────────────────────────────────────────────
    if request.method == "POST":
        if not farm:
            return Response(
                {"detail": "لا توجد مزرعة نشطة."}, status=status.HTTP_400_BAD_REQUEST
            )
        serializer = LocationNodeCreateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        # SUPER_ADMIN has no company FK — fall back to farm.company (already tenant-scoped)
        company = getattr(request.user, "company", None) or farm.company
        node = serializer.save(
            farm=farm,
            company=company,
        )
        log_activity(
            request.user, f"Created LocationNode: {node.type}:{node.name}", "Farm"
        )
        return Response(
            LocationNodeSerializer(node).data, status=status.HTTP_201_CREATED
        )

    # ── GET: list filtered nodes ──────────────────────────────────────────────
    node_type = request.query_params.get("type")
    parent_id = request.query_params.get("parent")

    qs = LocationNode.objects.filter(is_active=True).select_related("parent")
    if farm:
        qs = qs.filter(farm=farm)

    if node_type:
        qs = qs.filter(type=node_type)
    if parent_id:
        qs = qs.filter(parent_id=parent_id)

    data = [
        {
            "id": node.id,
            "name": node.name,
            "type": node.type,
            "parent_id": node.parent_id,
            "parent_name": node.parent.name if node.parent_id else None,
        }
        for node in qs.order_by("order", "created_at")
    ]
    return Response(data)


@api_view(["PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def location_node_detail_view(request, pk):
    """
    PATCH  /farm/location-nodes/<pk>/  — rename or reorder a node
    DELETE /farm/location-nodes/<pk>/  — soft-delete (is_active=False)
    """
    try:
        node = LocationNode.objects.get(pk=pk)
    except LocationNode.DoesNotExist:
        return Response(
            {"detail": "العنصر غير موجود."}, status=status.HTTP_404_NOT_FOUND
        )

    # Tenant safety check
    if not request.user.is_superuser and node.company_id != getattr(request.user, "company_id", None):
        return Response({"detail": "غير مصرح."}, status=status.HTTP_403_FORBIDDEN)

    if request.method == "PATCH":
        # Only allow renaming and reordering — parent/type changes are not allowed after creation
        allowed = {k: v for k, v in request.data.items() if k in ("name", "order")}
        serializer = LocationNodeSerializer(node, data=allowed, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        log_activity(request.user, f"Updated LocationNode: {node.pk}", "Farm")
        return Response(LocationNodeSerializer(node).data)

    elif request.method == "DELETE":
        node.is_active = False
        node.save(update_fields=["is_active"])
        # Also deactivate all descendants
        node.get_descendants().update(is_active=False)
        log_activity(
            request.user, f"Archived LocationNode: {node.type}:{node.name}", "Farm"
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


# ─── Enclosure Operational Profile Views ──────────────────────────────────

from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from apps.reports.selectors import get_location_timeline, get_location_analytics
from serializers.reports_serializers import OperationLogTimelineSerializer


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def location_node_profile_view(request, pk):
    """
    GET: Returns high-level profile summary for an enclosure (Entity-Centric).
    PATCH: Updates the agricultural profile (tree count, crop, yield, etc.).
    """
    try:
        node = LocationNode.objects.get(pk=pk)
    except LocationNode.DoesNotExist:
        return Response({"detail": "العنصر غير موجود."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "PATCH":
        # Update or create the profile
        from apps.farm.models import EnclosureProfile
        from django.db import transaction
        
        try:
            with transaction.atomic():
                profile, created = EnclosureProfile.objects.get_or_create(
                    location_node=node,
                    defaults={"company": node.company}
                )
                
                # Extract and clean fields (handle empty strings from frontend)
                def clean_num(val, default=None):
                    if val is None or val == "": return default
                    try: return int(float(val))
                    except: return default

                def clean_decimal(val, default=None):
                    if val is None or val == "": return default
                    try: return val
                    except: return default

                crop_type = request.data.get("crop_type")
                planting_year = clean_num(request.data.get("planting_year"))
                tree_count = clean_num(request.data.get("tree_count"), 0)
                seedling_count = clean_num(request.data.get("seedling_count"), 0)
                expected_yield = clean_decimal(request.data.get("expected_yield"))
                profile_data = request.data.get("profile_data")

                if crop_type is not None: profile.crop_type = crop_type
                if planting_year is not None: profile.planting_year = planting_year
                if tree_count is not None: profile.tree_count = tree_count
                if seedling_count is not None: profile.seedling_count = seedling_count
                if expected_yield is not None: profile.expected_yield = expected_yield
                
                general_notes = request.data.get("general_notes")
                if general_notes is not None:
                    profile.general_notes = general_notes
                    
                if profile_data is not None:
                    if not profile.profile_data: profile.profile_data = {}
                    profile.profile_data.update(profile_data)
                    
                profile.save()
                log_activity(request.user, f"Updated Agricultural Profile for Enclosure {node.name}", "Farm")
        except Exception as e:
            return Response({"detail": f"خطأ أثناء تحديث البيانات: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Basic analytics for profile header with safety fallback
    try:
        analytics = get_location_analytics(node)
    except Exception:
        analytics = {
            "summary": {"total_ops": 0, "total_hours": 0, "last_op_date": None},
            "distribution": [],
            "cost_trend": []
        }
    
    # Resolve hierarchy breadcrumbs safely
    try:
        ancestors = node.get_ancestors()
        sector = ancestors.filter(type=LocationNode.TYPE_SECTOR).first()
        stage = ancestors.filter(type=LocationNode.TYPE_STAGE).first()
    except Exception:
        sector = stage = None

    # Fetch Enclosure Profile if it exists (using safe hasattr)
    profile_data = {}
    if hasattr(node, "profile") and node.profile:
        p = node.profile
        profile_data = {
            "crop_type": p.crop_type,
            "planting_year": p.planting_year,
            "tree_count": p.tree_count,
            "seedling_count": p.seedling_count,
            "expected_yield": float(p.expected_yield) if p.expected_yield else 0,
            "actual_yield": float(p.actual_yield) if p.actual_yield else 0,
            "profile_data": p.profile_data,
            "general_notes": p.general_notes,
        }

    return Response({
        "id": node.id,
        "name": node.name,
        "type": node.type,
        "status": "active" if node.is_active else "inactive",
        "hierarchy": {
            "sector": {"id": sector.id, "name": sector.name} if sector else None,
            "stage": {"id": stage.id, "name": stage.name} if stage else None,
        },
        "asset_profile": profile_data,
        "summary_metrics": {
            "total_operations": analytics.get("summary", {}).get("total_ops") or 0,
            "total_work_hours": round(float(analytics.get("summary", {}).get("total_hours") or 0), 2),
            "total_harvested_kg": analytics.get("summary", {}).get("total_harvested_kg") or 0,
            "last_operation_date": analytics.get("summary", {}).get("last_op_date"),
            "last_irrigation_date": analytics.get("summary", {}).get("last_irrigation_date"),
            "last_fertilization_date": analytics.get("summary", {}).get("last_fertilization_date")
        }
    })


class LocationNodeTimelineView(APIView):
    """
    Paginated dynamic timeline of operations for an enclosure.
    Uses OperationLog as the atomic event source.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            node = LocationNode.objects.get(pk=pk)
        except LocationNode.DoesNotExist:
            return Response({"detail": "العنصر غير موجود."}, status=status.HTTP_404_NOT_FOUND)

        profile_type = request.query_params.get("profile_type")
        if profile_type == "all":
            profile_type = None
        operation_id = request.query_params.get("operation_id")
        search = request.query_params.get("search")
        
        logs = get_location_timeline(node, profile_type=profile_type, operation_id=operation_id, search=search)
        
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(logs, request)
        serializer = OperationLogTimelineSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def location_node_analytics_view(request, pk):
    """
    Aggregated analytics with high reliability. Never returns 500.
    """
    try:
        node = LocationNode.objects.get(pk=pk)
        analytics = get_location_analytics(node)
        return Response(analytics)
    except LocationNode.DoesNotExist:
        return Response({"detail": "العنصر غير موجود."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        # Graceful degradation for analytics
        return Response({
            "summary": {"total_ops": 0, "total_hours": 0, "last_op_date": None},
            "distribution": [],
            "cost_trend": [],
            "error_hint": str(e)
        })
