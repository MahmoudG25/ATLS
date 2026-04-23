from rest_framework.permissions import BasePermission

ROLE_FEATURES_MAP = {
    'SUPER_ADMIN': 'all',
    'OWNER': 'all',
    'MANAGER': 'all',
    'ENGINEER': ['reports', 'farm', 'palm', 'olive', 'equipment', 'production'],
    'ACCOUNTANT': ['accounting', 'farm', 'reports'],
    'WAREHOUSE': ['warehouse', 'farm', 'reports'],
    'HR': ['farm', 'reports']
}

class IsSuperAdmin(BasePermission):
    """
    Allows access only to users with the 'SUPER_ADMIN' role.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            getattr(request.user, 'role', None) == 'SUPER_ADMIN'
        )

class CanManageUsers(BasePermission):
    """
    Allows access to users with SUPER_ADMIN, OWNER, or MANAGER role.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            getattr(request.user, 'role', None) in ['SUPER_ADMIN', 'OWNER', 'MANAGER']
        )

class HasModuleAccess(BasePermission):
    """
    Global RBAC evaluation resolving the requested sub-domain against 
    the active token's role map. Enforces Read-Only on Unassigned Domains.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        role = getattr(request.user, 'role', None)
        if not role: return False
        
        allowed_domains = ROLE_FEATURES_MAP.get(role, [])
        if allowed_domains == 'all':
            return True
            
        # Allow open READS for situational awareness globally
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
            
        path_segments = request.path.strip('/').split('/')
        if len(path_segments) >= 2 and path_segments[0] == 'api':
            target_module = path_segments[1] # e.g., 'warehouse', 'accounting'
            return target_module in allowed_domains
            
        return False
