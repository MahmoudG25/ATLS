from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from serializers.farm_serializers import FarmSerializer, CropTypeSerializer, SectorSerializer, PlotSerializer
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

from apps.farm.models import Farm

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def hierarchy_view(request):
    farm = Farm.objects.filter(is_active=True).first()
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

    return Response({
        'farm': {'id': farm.id, 'name': farm.name},
        'crops': crops_data
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
