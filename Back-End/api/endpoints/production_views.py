from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from serializers.production_serializers import AnnualYieldSerializer
from services.production_service import get_yields, create_yield


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def yield_view(request):
    if request.method == "GET":
        plot_id = request.query_params.get("plot")
        year = request.query_params.get("year")
        yields = get_yields(plot_id, year)
        return Response(AnnualYieldSerializer(yields, many=True).data)
    elif request.method == "POST":
        serializer = AnnualYieldSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = create_yield(serializer.validated_data)
        return Response(AnnualYieldSerializer(obj).data, status=status.HTTP_201_CREATED)
