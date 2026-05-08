from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsManagerOrAbove(BasePermission):
    """
    Allows access to users with SUPER_ADMIN, OWNER, or MANAGER role.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None)
            in ["SUPER_ADMIN", "OWNER", "MANAGER"]
        )


class IsManagerOrReadOnly(BasePermission):
    """
    Allows read-only access to all authenticated users, but restricts write to Managers+.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None)
            in ["SUPER_ADMIN", "OWNER", "MANAGER"]
        )
