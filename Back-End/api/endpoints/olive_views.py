from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from permissions.role_permissions import HasModuleAccess
from rest_framework.response import Response
from serializers.olive_serializers import OliveRecordSerializer
from services.olive_service import (
    list_olive_records,
    create_olive_record,
    update_olive_record,
)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, HasModuleAccess])
def olive_collection_view(request):
    if request.method == "GET":
        plot_id = request.query_params.get("plot")
        records = list_olive_records(plot_id)
        return Response(OliveRecordSerializer(records, many=True).data)
    elif request.method == "POST":
        serializer = OliveRecordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        record = create_olive_record(serializer.validated_data)
        return Response(
            OliveRecordSerializer(record).data, status=status.HTTP_201_CREATED
        )

olive_collection_view.required_module = "olive"


@api_view(["PUT"])
@permission_classes([IsAuthenticated, HasModuleAccess])
def olive_detail_view(request, id):
    serializer = OliveRecordSerializer(data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    record = update_olive_record(id, serializer.validated_data)
    return Response(OliveRecordSerializer(record).data, status=status.HTTP_200_OK)

olive_detail_view.required_module = "olive"
