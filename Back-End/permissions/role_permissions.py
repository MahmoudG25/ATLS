import logging
from rest_framework.permissions import BasePermission
from django.db.models import Q

logger = logging.getLogger(__name__)

ROLE_FEATURES_MAP = {
    "SUPER_ADMIN": "all",
    "OWNER": "all",
    "MANAGER": "all",
    "ENGINEER": ["reports", "farm", "palm", "olive", "production"],
    "ACCOUNTANT": ["accounting", "farm", "reports"],
    "WAREHOUSE": ["warehouse", "farm", "reports", "equipment"],
    "HR": ["farm", "reports", "hr"],
}

MODULE_ROUTE_MAP = {
    "hr": ["api/hr/"],
    "warehouse": ["api/warehouse/"],
    "farm": ["api/farm/"],
    "palm": ["api/palm/"],
    "olive": ["api/olive/"],
    "production": ["api/production/"],
    "reports": ["api/reports/", "api/analytics/"],
    "accounting": ["api/accounting/"],
    "equipment": ["api/equipment/"],
}

FALLBACK_MODULE_MAP = {
    # Farm views mapping
    "farms_list_view": "farm",
    "farm_settings_view": "farm",
    "location_tree_view": "farm",
    "location_nodes_view": "farm",
    "location_node_detail_view": "farm",
    "location_node_profile_view": "farm",
    "location_node_analytics_view": "farm",
    "LocationNodeTimelineView": "farm",
    # Palm
    "palm_collection_view": "palm",
    "palm_detail_view": "palm",
    # Olive
    "olive_collection_view": "olive",
    "olive_detail_view": "olive",
    # Accounting views mapping
    "finance_summary_view": "accounting",
    "expenses_view": "accounting",
    "revenues_view": "accounting",
    "salaries_view": "accounting",
    "invoices_view": "accounting",
    "invoice_detail_view": "accounting",
    # Warehouse views mapping
    "items_view": "warehouse",
    "item_detail_view": "warehouse",
    "movements_view": "warehouse",
}


class IsSuperAdmin(BasePermission):
    """
    Allows access only to users with the 'SUPER_ADMIN' role.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None) == "SUPER_ADMIN"
        )


class CanManageUsers(BasePermission):
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


class HasModuleAccess(BasePermission):
    """
    Global RBAC evaluation resolving the requested sub-domain against
    the active token's role map and user's custom permissions.
    """

    def resolve_module(self, view, request):
        # 1. Check direct attribute on view instance
        module = getattr(view, "required_module", None)
        if module:
            return module

        # 2. Check function name or class name in fallback mapping
        view_name = view.__class__.__name__
        if view_name == "WrappedAPIView" and hasattr(view, "cls"):
            # DRF function-based view decorated with @api_view
            func = getattr(view, "wrapped_view", None) or getattr(view, "__name__", None)
            if func:
                module = getattr(func, "required_module", None)
                if module:
                    return module
            
            func_name = getattr(view, "__name__", None) or (view.cls.__name__ if hasattr(view, "cls") else "")
            if func_name in FALLBACK_MODULE_MAP:
                return FALLBACK_MODULE_MAP[func_name]

        if view_name in FALLBACK_MODULE_MAP:
            return FALLBACK_MODULE_MAP[view_name]

        # 3. Check centralized route mapping (Centralized Resolution Layer)
        normalized_path = request.path.lower().strip("/")
        for mod, prefixes in MODULE_ROUTE_MAP.items():
            for prefix in prefixes:
                clean_prefix = prefix.lower().strip("/")
                if normalized_path == clean_prefix or normalized_path.startswith(clean_prefix + "/"):
                    return mod

        # 4. Fallback to path segment parsing
        path_segments = request.path.strip("/").split("/")
        if len(path_segments) >= 2 and path_segments[0] == "api":
            return path_segments[1]

        return None

    def has_permission(self, request, view):
        try:
            if not request.user or not request.user.is_authenticated:
                logger.warning("Access denied: User is not authenticated. Fallback to DENY.")
                return False

            role = getattr(request.user, "role", None)
            if not role:
                logger.warning(f"Access denied: User {request.user.email} has no role. Fallback to DENY.")
                return False

            # SUPER_ADMIN and Django superusers bypass all checks
            if role == "SUPER_ADMIN" or getattr(request.user, "is_superuser", False):
                logger.info(f"Access granted: User {request.user.email} bypassed as SUPER_ADMIN / superuser.")
                return True

            # Resolve required module
            target_module = self.resolve_module(view, request)
            if not target_module:
                logger.warning(
                    f"Access denied: Could not resolve required module for view '{view.__class__.__name__}' "
                    f"and path '{request.path}'. Fallback to DENY."
                )
                return False

            # Check database dynamic custom overrides first (Priority 2)
            user_custom_perms = list(request.user.app_permissions.values_list('code', flat=True))
            has_custom_perm = any(
                p == target_module or p.startswith(target_module + ".")
                for p in user_custom_perms
            )
            if has_custom_perm:
                logger.info(
                    f"Access granted: User {request.user.email} (Role: {role}) has explicit override for module '{target_module}' "
                    f"(User custom permissions: {user_custom_perms})."
                )
                return True

            # Check default role permissions mapping (Priority 3)
            allowed_domains = ROLE_FEATURES_MAP.get(role, [])
            if allowed_domains == "all" or target_module in allowed_domains:
                logger.info(
                    f"Access granted: User {request.user.email} (Role: {role}) has default role access to module '{target_module}'. "
                    f"Allowed modules for role: {allowed_domains}."
                )
                return True

            logger.warning(
                f"Access denied: User {request.user.email} (Role: {role}) does not have access to module '{target_module}'. "
                f"User custom permissions: {user_custom_perms}. Allowed modules for role: {allowed_domains}. Fallback to DENY."
            )
            try:
                from apps.users.models import ActivityLog
                ActivityLog.objects.create(
                    user=request.user,
                    action="ACCESS_DENIED",
                    module=target_module,
                    description=f"User attempted to access route '{request.path}' (View: {view.__class__.__name__}) but was denied due to missing permissions."
                )
            except Exception as e:
                logger.error(f"Failed to log permission audit: {e}")
            return False

        except Exception as exc:
            logger.critical(
                f"Error during module access permission resolution: {exc}. Fallback to DENY.",
                exc_info=True
            )
            try:
                if request.user and request.user.is_authenticated:
                    from apps.users.models import ActivityLog
                    ActivityLog.objects.create(
                        user=request.user,
                        action="ACCESS_DENIED_ERROR",
                        module="unknown",
                        description=f"Exception during access validation for path '{request.path}': {str(exc)}"
                    )
            except:
                pass
            return False


def required_module(module_name):
    """
    Decorator for Django REST Framework function-based views to explicitly declare their required module.
    """
    def decorator(func):
        func.required_module = module_name
        return func
    return decorator


