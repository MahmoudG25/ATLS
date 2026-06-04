from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from permissions.role_permissions import HasModuleAccess
from rest_framework.response import Response
from serializers.palm_serializers import PalmRecordSerializer
from services.palm_service import (
    list_palm_records,
    create_palm_record,
    update_palm_record,
)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, HasModuleAccess])
def palm_collection_view(request):
    if request.method == "GET":
        plot_id = request.query_params.get("plot")
        records = list_palm_records(plot_id)
        return Response(PalmRecordSerializer(records, many=True).data)
    elif request.method == "POST":
        serializer = PalmRecordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        record = create_palm_record(serializer.validated_data)
        return Response(
            PalmRecordSerializer(record).data, status=status.HTTP_201_CREATED
        )

palm_collection_view.required_module = "palm"


@api_view(["PUT"])
@permission_classes([IsAuthenticated, HasModuleAccess])
def palm_detail_view(request, id):
    serializer = PalmRecordSerializer(data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    record = update_palm_record(id, serializer.validated_data)
    return Response(PalmRecordSerializer(record).data, status=status.HTTP_200_OK)

palm_detail_view.required_module = "palm"
