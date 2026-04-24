from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from serializers.warehouse_serializers import ItemSerializer, MovementSerializer
from services.warehouse_service import list_items, get_movements, create_item, create_movement, update_item, delete_item

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def items_view(request):
    if request.method == 'GET':
        items = list_items()
        return Response(ItemSerializer(items, many=True).data)
    elif request.method == 'POST':
        serializer = ItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = create_item(serializer.validated_data, user=request.user)
        return Response(ItemSerializer(item).data, status=status.HTTP_201_CREATED)

@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def item_detail_view(request, pk):
    try:
        from apps.warehouse.models import Item
        # We check existence
        Item.objects.get(pk=pk)
    except Exception:
        return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)
        
    if request.method == 'PUT':
        serializer = ItemSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        item = update_item(pk, serializer.validated_data, user=request.user)
        return Response(ItemSerializer(item).data)
        
    elif request.method == 'DELETE':
        delete_item(pk, user=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

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
        mov = create_movement(serializer.validated_data, user=request.user)
        return Response(MovementSerializer(mov).data, status=status.HTTP_201_CREATED)
