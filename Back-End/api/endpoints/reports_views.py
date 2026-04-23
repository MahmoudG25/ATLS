from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from serializers.reports_serializers import DailyReportSerializer
from services.reports_service import list_reports, create_report

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def reports_view(request):
    if request.method == 'GET':
        engineer_id = request.query_params.get('engineer')
        sector_id = request.query_params.get('sector')
        reports = list_reports(engineer_id, sector_id)
        return Response(DailyReportSerializer(reports, many=True).data)
    elif request.method == 'POST':
        serializer = DailyReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Assuming the currently authenticated user is the engineer
        obj = create_report(request.user, serializer.validated_data)
        return Response(DailyReportSerializer(obj).data, status=status.HTTP_201_CREATED)
