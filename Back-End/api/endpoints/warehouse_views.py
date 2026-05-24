from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from serializers.warehouse_serializers import ItemSerializer, MovementSerializer, WarehouseSerializer
from apps.warehouse.models import Item, Movement, Warehouse
from services.warehouse_service import (
    list_items,
    get_movements,
    create_item,
    create_movement,
    update_item,
    delete_item,
)


class WarehouseListCreateView(generics.ListCreateAPIView):
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return Warehouse.objects.filter(company=self.request.user.company, is_active=True)

    def perform_create(self, serializer):
        # Ensure company is set from the logged-in user
        serializer.save(company=self.request.user.company)


class WarehouseDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Warehouse.objects.filter(company=self.request.user.company)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def items_view(request):
    if request.method == "GET":
        items = list_items().filter(company=request.user.company)
        return Response(ItemSerializer(items, many=True).data)
    elif request.method == "POST":
        serializer = ItemSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        # Use the service to handle business logic (logging, quantity init, etc.)
        item = create_item({**serializer.validated_data, "company": request.user.company}, user=request.user)
        return Response(ItemSerializer(item).data, status=status.HTTP_201_CREATED)


@api_view(["PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def item_detail_view(request, pk):
    try:
        item = Item.objects.get(pk=pk, company=request.user.company)
    except Item.DoesNotExist:
        return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "PUT":
        serializer = ItemSerializer(item, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        item = update_item(pk, serializer.validated_data, user=request.user)
        return Response(ItemSerializer(item).data)

    elif request.method == "DELETE":
        delete_item(pk, user=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def movements_view(request):
    if request.method == "GET":
        item_id = request.query_params.get("item")
        location_id = request.query_params.get("location")
        movs = get_movements(item_id=item_id, location_id=location_id).filter(company=request.user.company)
        return Response(MovementSerializer(movs, many=True).data)
    elif request.method == "POST":
        serializer = MovementSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        # Use the service to handle critical logic (quantity updates, validation)
        mov = create_movement({**serializer.validated_data, "company": request.user.company}, user=request.user)
        return Response(MovementSerializer(mov).data, status=status.HTTP_201_CREATED)
