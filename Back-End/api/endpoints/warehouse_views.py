from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from serializers.warehouse_serializers import ItemSerializer, MovementSerializer
from services.warehouse_service import list_items, get_movements, create_item, create_movement

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def items_view(request):
    if request.method == 'GET':
        items = list_items()
        return Response(ItemSerializer(items, many=True).data)
    elif request.method == 'POST':
        serializer = ItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = create_item(serializer.validated_data)
        return Response(ItemSerializer(item).data, status=status.HTTP_201_CREATED)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def movements_view(request):
    if request.method == 'GET':
        item_id = request.query_params.get('item')
        movs = get_movements(item_id)
        return Response(MovementSerializer(movs, many=True).data)
    elif request.method == 'POST':
        serializer = MovementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mov = create_movement(serializer.validated_data)
        return Response(MovementSerializer(mov).data, status=status.HTTP_201_CREATED)
