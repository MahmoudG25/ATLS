from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from serializers.equipment_serializers import EquipmentSerializer, MaintenanceSerializer, UsageSerializer
from services.equipment_service import get_equipment_list, create_equipment, get_equipment_details, create_maintenance, create_usage

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def equipment_list_view(request):
    if request.method == 'GET':
        eqs = get_equipment_list()
        return Response(EquipmentSerializer(eqs, many=True).data)
    elif request.method == 'POST':
        serializer = EquipmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        eq = create_equipment(serializer.validated_data)
        return Response(EquipmentSerializer(eq).data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def equipment_detail_view(request, id):
    data = get_equipment_details(id)
    return Response({
        'equipment': EquipmentSerializer(data['equipment']).data,
        'maintenances': MaintenanceSerializer(data['maintenances'], many=True).data,
        'usages': UsageSerializer(data['usages'], many=True).data
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def maintenance_view(request):
    serializer = MaintenanceSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    m = create_maintenance(serializer.validated_data)
    return Response(MaintenanceSerializer(m).data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def usage_view(request):
    serializer = UsageSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    u = create_usage(serializer.validated_data)
    return Response(UsageSerializer(u).data, status=status.HTTP_201_CREATED)
