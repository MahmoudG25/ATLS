from rest_framework import serializers
from apps.users.models import User, ActivityLog


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "name",
            "role",
            "phones",
            "is_approved",
            "is_active",
            "last_login",
            "date_joined",
        ]
        read_only_fields = [
            "id",
            "is_approved",
            "is_active",
            "last_login",
            "date_joined",
        ]


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
