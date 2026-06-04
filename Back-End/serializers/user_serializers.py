from rest_framework import serializers
from apps.users.models import User, ActivityLog


class UserSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()
    permissions_hash = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "name",
            "role",
            "phones",
            "avatar_url",
            "company",
            "is_approved",
            "is_active",
            "last_login",
            "date_joined",
            "permissions",
            "permissions_hash",
        ]
        read_only_fields = [
            "id",
            "is_approved",
            "is_active",
            "last_login",
            "date_joined",
            "permissions",
            "permissions_hash",
        ]

    def get_permissions(self, obj):
        return list(obj.app_permissions.values_list("code", flat=True))

    def get_permissions_hash(self, obj):
        import hashlib
        from django.core.cache import cache
        
        cache_key = f"user_perms_hash_{obj.id}"
        p_hash = cache.get(cache_key)
        if p_hash is None:
            codes = sorted(list(obj.app_permissions.values_list("code", flat=True)))
            content = f"{obj.role}:{','.join(codes)}"
            p_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
            cache.set(cache_key, p_hash, 300)
        return p_hash


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "name", "role", "phones"]


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class ActivityLogSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_name = serializers.CharField(source="user.name", read_only=True)

    class Meta:
        model = ActivityLog
        fields = [
            "id",
            "user",
            "user_email",
            "user_name",
            "action",
            "module",
            "description",
            "ip_address",
            "created_at",
        ]
