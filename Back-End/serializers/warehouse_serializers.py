from rest_framework import serializers
from apps.warehouse.models import Item, Movement

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'

class MovementSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    
    class Meta:
        model = Movement
        fields = '__all__'
