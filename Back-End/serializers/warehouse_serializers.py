from rest_framework import serializers
from apps.warehouse.models import Item, Movement, Warehouse


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ["id", "name", "location", "is_active", "company"]
        read_only_fields = ["company"]
        # Disable automatic UniqueTogetherValidator to handle it manually
        validators = []

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        user_company = getattr(user, "company", None)
        
        # If we can't find a company, we try to see if it's already in attrs
        # (though normally it shouldn't be sent from frontend)
        final_company = user_company or attrs.get("company")
        
        if not final_company:
             raise serializers.ValidationError({"company": "تعذر العثور على الشركة المرتبطة بحسابك. يرجى إعادة تسجيل الدخول."})
             
        attrs["company"] = final_company
        
        # Manual uniqueness check
        name = attrs.get("name")
        if name and final_company:
            # Check if name exists for this company
            exists = Warehouse.objects.filter(
                company=final_company, 
                name=name, 
                is_active=True
            ).exclude(id=self.instance.id if self.instance else None).exists()
            
            if exists:
                raise serializers.ValidationError({"name": "هذا الاسم موجود مسبقاً في مخازنك"})
                
        return attrs

    def create(self, validated_data):
        # Double check company before creation to prevent 500/IntegrityError
        if not validated_data.get('company'):
            request = self.context.get("request")
            validated_data['company'] = request.user.company
            
        return Warehouse.objects.create(**validated_data)


class ItemSerializer(serializers.ModelSerializer):
    updated_by_name = serializers.CharField(
        source="updated_by.get_full_name", read_only=True
    )

    class Meta:
        model = Item
        fields = ["id", "name", "category", "quantity", "warehouse", "unit", "updated_by_name", "company", "updated_by"]
        read_only_fields = ["company", "updated_by"]

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        user_company = getattr(user, "company", None)
        
        if not user_company:
             raise serializers.ValidationError({"company": "تعذر العثور على الشركة المرتبطة بحسابك."})
             
        # Normalize empty strings for warehouse FK
        warehouse_val = attrs.get("warehouse")
        if warehouse_val == "" or warehouse_val == "null":
            attrs["warehouse"] = None

        attrs["company"] = user_company
        attrs["updated_by"] = user
        return attrs

    def create(self, validated_data):
        if not validated_data.get('company'):
            request = self.context.get("request")
            validated_data['company'] = request.user.company
        if not validated_data.get('updated_by'):
            request = self.context.get("request")
            validated_data['updated_by'] = request.user
        return super().create(validated_data)


class MovementSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source="item.name", read_only=True)
    user_name = serializers.SerializerMethodField()
    responsible_user_name = serializers.SerializerMethodField()
    location_name = serializers.SerializerMethodField()
    engineer_name = serializers.SerializerMethodField()  # اسم المهندس المسؤول (الواجهة)

    class Meta:
        model = Movement
        fields = [
            "id", "item", "movement_type", "quantity", "note", "date", 
            "item_name", "user_name", "company", "user", 
            "location", "other_location", "responsible_user",
            "responsible_user_name", "location_name", "engineer_name"
        ]
        read_only_fields = ["company", "user"]

    def _resolve_name(self, user_obj):
        """Get best available name from user object."""
        if not user_obj:
            return None
        full = user_obj.get_full_name().strip()
        if full:
            return full
        # fallback to name field (custom) or username
        return getattr(user_obj, 'name', None) or user_obj.username or str(user_obj)

    def get_user_name(self, obj):
        return self._resolve_name(obj.user)

    def get_responsible_user_name(self, obj):
        return self._resolve_name(obj.responsible_user)

    def get_engineer_name(self, obj):
        # Priority: responsible_user > user
        name = self._resolve_name(obj.responsible_user)
        if not name:
            name = self._resolve_name(obj.user)
        return name

    def get_location_name(self, obj):
        return obj.location.name if obj.location else None

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        user_company = getattr(user, "company", None)
        
        if not user_company:
             raise serializers.ValidationError({"company": "تعذر العثور على الشركة المرتبطة بحسابك."})
             
        # Convert empty strings/null strings to None for optional foreign keys
        for fk in ["responsible_user", "location", "item"]:
            val = attrs.get(fk)
            if val == "" or val == "null":
                attrs[fk] = None

        attrs["company"] = user_company
        attrs["user"] = user
        return attrs

    def create(self, validated_data):
        if not validated_data.get('company'):
            request = self.context.get("request")
            validated_data['company'] = request.user.company
        if not validated_data.get('user'):
            request = self.context.get("request")
            validated_data['user'] = request.user
        return super().create(validated_data)
