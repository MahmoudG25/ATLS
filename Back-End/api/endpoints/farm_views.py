from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from serializers.farm_serializers import (
    FarmSerializer, CropTypeSerializer, SectorSerializer, PlotSerializer,
    LocationNodeCreateSerializer, LocationNodeSerializer,
)
from services.farm_service import list_farms, list_crop_types, get_farm_structure, create_sector, create_plot, get_plot_stats, update_sector, delete_sector, update_plot, delete_plot
from services.activity_service import log_activity
from permissions.role_permissions import HasModuleAccess

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def farms_list_view(request):
    farms = list_farms()
    return Response(FarmSerializer(farms, many=True).data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def croptypes_list_view(request):
    crops = list_crop_types()
    return Response(CropTypeSerializer(crops, many=True).data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def structure_view(request):
    farm_id = request.query_params.get('farm_id')
    sectors = get_farm_structure(farm_id)
    return Response(SectorSerializer(sectors, many=True).data)

from apps.farm.models import Farm, LocationNode

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def hierarchy_view(request):
    farms_qs = Farm.objects.filter(is_active=True)
    if getattr(request.user, "company_id", None):
        farms_qs = farms_qs.filter(company_id=request.user.company_id)
    farm = farms_qs.first()
    if not farm:
        return Response({}, status=200)

    crops_data = []
    for crop in farm.crops.filter(is_active=True).order_by('order'):
        if crop.type == 'palm':
            stages_data = []
            for stage in crop.stages.filter(is_active=True).order_by('order'):
                enclosures_data = [
                    {'id': enc.id, 'name': enc.name}
                    for enc in stage.enclosures.filter(is_active=True).order_by('order')
                ]
                stages_data.append({
                    'id': stage.id,
                    'name': stage.name,
                    'enclosures': enclosures_data
                })
            crops_data.append({
                'id': crop.id,
                'name': crop.name,
                'type': crop.type,
                'stages': stages_data
            })
        else:
            regions_data = [
                {'id': enc.id, 'name': enc.name}
                for enc in crop.enclosures.filter(is_active=True, stage__isnull=True).order_by('order')
            ]
            crops_data.append({
                'id': crop.id,
                'name': crop.name,
                'type': crop.type,
                'regions': regions_data
            })

    nodes = list(
        LocationNode.objects.filter(farm=farm, is_active=True)
        .order_by("tree_id", "lft")
    )
    children_map = {}
    roots = []
    for node in nodes:
        if node.parent_id:
            children_map.setdefault(node.parent_id, []).append(node)
        else:
            roots.append(node)

    def to_node_payload(node):
        return {
            "id": node.id,
            "name": node.name,
            "type": node.type,
            "children": [to_node_payload(child) for child in children_map.get(node.id, [])],
        }

    return Response({
        'farm': {'id': farm.id, 'name': farm.name},
        'crops': crops_data,
        'location_nodes': [to_node_payload(node) for node in roots],
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_sector_view(request):
    serializer = SectorSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    sector = create_sector(serializer.validated_data)
    log_activity(request.user, f"Created Sector: {sector.name}", "Farm")
    # Refetch to get the crop_type relations for the response
    sector_full = get_farm_structure().get(id=sector.id)
    return Response(SectorSerializer(sector_full).data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_plot_view(request):
    serializer = PlotSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    plot = create_plot(serializer.validated_data)
    log_activity(request.user, f"Created Plot: {plot.name}", "Farm")
    return Response(PlotSerializer(plot).data, status=status.HTTP_201_CREATED)

@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def sector_detail_view(request, pk):
    if request.method == 'PUT':
        serializer = SectorSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        sector = update_sector(pk, serializer.validated_data)
        log_activity(request.user, f"Updated Sector: {sector.name}", "Farm")
        return Response(SectorSerializer(sector).data)
    elif request.method == 'DELETE':
        delete_sector(pk)
        log_activity(request.user, f"Archived Sector ID: {pk}", "Farm")
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def plot_detail_view(request, pk):
    if request.method == 'PUT':
        serializer = PlotSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        plot = update_plot(pk, serializer.validated_data)
        log_activity(request.user, f"Updated Plot: {plot.name}", "Farm")
        return Response(PlotSerializer(plot).data)
    elif request.method == 'DELETE':
        delete_plot(pk)
        log_activity(request.user, f"Archived Plot ID: {pk}", "Farm")
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAuthenticated, HasModuleAccess])
def plot_stats_view(request, id):
    try:
        stats = get_plot_stats(id)
        return Response(stats, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def location_tree_view(request):
    """
    GET /farm/location-tree/

    Returns the complete LocationNode hierarchy as a nested tree.
    Each node includes 'has_stages' and 'has_enclosures' flags so the
    frontend can decide which dropdowns to show dynamically.

    Structure example:
      SECTOR → STAGE → ENCLOSURE  (3-level)
      SECTOR → ENCLOSURE          (2-level, no stages)
    """
    farm_qs = Farm.objects.filter(is_active=True)
    if getattr(request.user, 'company_id', None):
        farm_qs = farm_qs.filter(company_id=request.user.company_id)
    farm = farm_qs.first()
    if not farm:
        return Response({'farm': None, 'tree': []}, status=200)

    nodes = list(
        LocationNode.objects.filter(farm=farm, is_active=True)
        .order_by('order', 'name')
    )
    children_map = {}
    roots = []
    for node in nodes:
        if node.parent_id:
            children_map.setdefault(node.parent_id, []).append(node)
        else:
            roots.append(node)

    def serialize_node(node):
        children = children_map.get(node.id, [])
        return {
            'id':             node.id,
            'name':           node.name,
            'type':           node.type,
            'parent_id':      node.parent_id,
            'order':          node.order,
            # Flags that tell the frontend what child types exist
            'has_stages':     any(c.type == LocationNode.TYPE_STAGE     for c in children),
            'has_enclosures': any(c.type == LocationNode.TYPE_ENCLOSURE for c in children),
            'children':       [serialize_node(child) for child in children],
        }

    return Response({
        'farm': {'id': farm.id, 'name': farm.name},
        'tree': [serialize_node(root) for root in roots],
    })


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def location_nodes_view(request):
    """
    GET  /farm/location-nodes/?type=STAGE
    GET  /farm/location-nodes/?type=ENCLOSURE&parent=<node_id>
    POST /farm/location-nodes/  — create a new LocationNode

    GET: Returns active LocationNodes filtered by type and optionally parent.
    POST: Creates a new node with full nesting validation.
    """
    farm_qs = Farm.objects.filter(is_active=True)
    if getattr(request.user, 'company_id', None):
        farm_qs = farm_qs.filter(company_id=request.user.company_id)
    farm = farm_qs.first()

    # ── POST: create a new node ───────────────────────────────────────────────
    if request.method == 'POST':
        if not farm:
            return Response({'detail': 'لا توجد مزرعة نشطة.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = LocationNodeCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        # SUPER_ADMIN has no company FK — fall back to farm.company (already tenant-scoped)
        company = getattr(request.user, 'company', None) or farm.company
        node = serializer.save(
            farm=farm,
            company=company,
        )
        log_activity(request.user, f"Created LocationNode: {node.type}:{node.name}", "Farm")
        return Response(LocationNodeSerializer(node).data, status=status.HTTP_201_CREATED)

    # ── GET: list filtered nodes ──────────────────────────────────────────────
    node_type = request.query_params.get('type')
    parent_id = request.query_params.get('parent')

    qs = LocationNode.objects.filter(is_active=True).select_related('parent')
    if farm:
        qs = qs.filter(farm=farm)

    if node_type:
        qs = qs.filter(type=node_type)
    if parent_id:
        qs = qs.filter(parent_id=parent_id)

    data = [
        {
            'id':          node.id,
            'name':        node.name,
            'type':        node.type,
            'parent_id':   node.parent_id,
            'parent_name': node.parent.name if node.parent_id else None,
        }
        for node in qs.order_by('order', 'name')
    ]
    return Response(data)


@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def location_node_detail_view(request, pk):
    """
    PATCH  /farm/location-nodes/<pk>/  — rename or reorder a node
    DELETE /farm/location-nodes/<pk>/  — soft-delete (is_active=False)
    """
    try:
        node = LocationNode.objects.get(pk=pk)
    except LocationNode.DoesNotExist:
        return Response({'detail': 'العنصر غير موجود.'}, status=status.HTTP_404_NOT_FOUND)

    # Tenant safety check
    company = getattr(request, 'company', None)
    if company and node.company_id != company.id:
        return Response({'detail': 'غير مصرح.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'PATCH':
        # Only allow renaming and reordering — parent/type changes are not allowed after creation
        allowed = {k: v for k, v in request.data.items() if k in ('name', 'order')}
        serializer = LocationNodeSerializer(node, data=allowed, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        log_activity(request.user, f"Updated LocationNode: {node.pk}", "Farm")
        return Response(LocationNodeSerializer(node).data)

    elif request.method == 'DELETE':
        node.is_active = False
        node.save(update_fields=['is_active'])
        # Also deactivate all descendants
        node.get_descendants().update(is_active=False)
        log_activity(request.user, f"Archived LocationNode: {node.type}:{node.name}", "Farm")
        return Response(status=status.HTTP_204_NO_CONTENT)
