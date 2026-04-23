from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from serializers.farm_serializers import FarmSerializer, CropTypeSerializer, SectorSerializer, PlotSerializer
from services.farm_service import list_farms, list_crop_types, get_farm_structure, create_sector, create_plot, get_plot_stats
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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_sector_view(request):
    serializer = SectorSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    sector = create_sector(serializer.validated_data)
    # Refetch to get the crop_type relations for the response
    sector_full = get_farm_structure().get(id=sector.id)
    return Response(SectorSerializer(sector_full).data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_plot_view(request):
    serializer = PlotSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    plot = create_plot(serializer.validated_data)
    return Response(PlotSerializer(plot).data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated, HasModuleAccess])
def plot_stats_view(request, id):
    try:
        stats = get_plot_stats(id)
        return Response(stats, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
