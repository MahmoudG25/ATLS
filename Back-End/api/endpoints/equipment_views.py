from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from permissions.role_permissions import HasModuleAccess
from serializers.equipment_serializers import (
    EquipmentSerializer,
    MaintenanceSerializer,
    UsageSerializer,
    OilChangeLogSerializer,
)
from services.equipment_service import (
    get_equipment_list,
    create_equipment,
    get_equipment_details,
    create_maintenance,
    create_usage,
    create_oil_change,
    get_oil_change_alerts,
)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, HasModuleAccess])
def equipment_list_view(request):
    company = request.user.company
    if request.method == "GET":
        eqs = get_equipment_list(company)
        return Response(EquipmentSerializer(eqs, many=True).data)
    elif request.method == "POST":
        serializer = EquipmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        eq = create_equipment(serializer.validated_data, company)
        return Response(EquipmentSerializer(eq).data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAuthenticated, HasModuleAccess])
def equipment_detail_view(request, id):
    company = request.user.company
    data = get_equipment_details(id, company)
    return Response(
        {
            "equipment": EquipmentSerializer(data["equipment"]).data,
            "maintenances": MaintenanceSerializer(data["maintenances"], many=True).data,
            "usages": UsageSerializer(data["usages"], many=True).data,
            "oil_changes": OilChangeLogSerializer(data["oil_changes"], many=True).data,
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated, HasModuleAccess])
def maintenance_view(request):
    company = request.user.company
    serializer = MaintenanceSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    m = create_maintenance(serializer.validated_data, company)
    return Response(MaintenanceSerializer(m).data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsAuthenticated, HasModuleAccess])
def usage_view(request):
    company = request.user.company
    serializer = UsageSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    u = create_usage(serializer.validated_data, company)
    return Response(UsageSerializer(u).data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsAuthenticated, HasModuleAccess])
def oil_change_view(request):
    company = request.user.company
    serializer = OilChangeLogSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    o = create_oil_change(serializer.validated_data, company)
    return Response(OilChangeLogSerializer(o).data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAuthenticated, HasModuleAccess])
def oil_alerts_view(request):
    company = request.user.company
    alerts = get_oil_change_alerts(company)
    return Response(alerts)
