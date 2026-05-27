from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from permissions.role_permissions import HasModuleAccess
from serializers.equipment_serializers import (
    EquipmentSerializer,
    MaintenanceSerializer,
    UsageSerializer,
    OilChangeLogSerializer,
    EquipmentLogSerializer,
    FleetMaintenanceAlertSerializer,
)
from services.equipment_service import (
    get_equipment_list,
    create_equipment,
    get_equipment_details,
    create_maintenance,
    create_usage,
    create_oil_change,
    get_oil_change_alerts,
    create_equipment_log,
    get_maintenance_alerts,
    resolve_maintenance_alert,
)
from apps.equipment.models import Equipment, EquipmentLog


# ── Existing Endpoints (for backward compatibility) ──

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


# ── New / Upgraded REST API View Handlers ──

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, HasModuleAccess])
def equipment_list_create_api(request):
    company = request.user.company
    if request.method == "GET":
        eqs = get_equipment_list(company)
        return Response(EquipmentSerializer(eqs, many=True).data)
    elif request.method == "POST":
        data = request.data.copy() if hasattr(request.data, "copy") else request.data
        image_file = request.FILES.get("image")
        if image_file:
            from services.upload_service import upload_file
            image_url = upload_file(image_file, folder="equipment")
            data["image"] = image_url
            
        serializer = EquipmentSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        eq = create_equipment(serializer.validated_data, company)
        return Response(EquipmentSerializer(eq).data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsAuthenticated, HasModuleAccess])
def equipment_logs_create_api(request):
    company = request.user.company
    serializer = EquipmentLogSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    log = create_equipment_log(serializer.validated_data, company)
    return Response(EquipmentLogSerializer(log).data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAuthenticated, HasModuleAccess])
def equipment_alerts_list_api(request):
    company = request.user.company
    alerts = get_maintenance_alerts(company)
    return Response(FleetMaintenanceAlertSerializer(alerts, many=True).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated, HasModuleAccess])
def equipment_alerts_resolve_api(request, pk):
    company = request.user.company
    try:
        resolve_maintenance_alert(pk, company)
        return Response({"success": True, "message": "تم تأكيد إجراء الصيانة بنجاح."})
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated, HasModuleAccess])
def equipment_profile_detail_api(request, pk):
    company = request.user.company
    try:
        equipment = Equipment.objects.get(id=pk, company=company)
        logs = equipment.logs.filter(company=company).order_by("-date", "-created_at")
        
        return Response({
            "profile": EquipmentSerializer(equipment).data,
            "historyLogs": EquipmentLogSerializer(logs, many=True).data
        })
    except Equipment.DoesNotExist:
        return Response({"detail": "المعدة غير موجودة."}, status=status.HTTP_404_NOT_FOUND)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated, HasModuleAccess])
def equipment_detail_api(request, pk):
    company = request.user.company
    equipment = get_object_or_404(Equipment, id=pk, company=company)
    
    if request.method == "GET":
        return Response(EquipmentSerializer(equipment).data)
        
    elif request.method in ["PUT", "PATCH"]:
        partial = (request.method == "PATCH")
        data = request.data.copy() if hasattr(request.data, "copy") else request.data
        image_file = request.FILES.get("image")
        if image_file:
            from services.upload_service import upload_file
            image_url = upload_file(image_file, folder="equipment")
            data["image"] = image_url
            
        serializer = EquipmentSerializer(equipment, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(EquipmentSerializer(equipment).data)
        
    elif request.method == "DELETE":
        # Delete related logs/maintenances etc. are handled by models CASCADE or DB triggers
        equipment.delete()
        return Response({"success": True, "message": "تم حذف المعدة بنجاح."}, status=status.HTTP_204_NO_CONTENT)

