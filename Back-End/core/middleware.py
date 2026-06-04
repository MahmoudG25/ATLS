import hashlib
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache

class CompanyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        company = None
        
        if user and getattr(user, "is_authenticated", False):
            company = getattr(user, "company", None)
            
            # Fallback to the first available company if user has no assigned company.
            # This ensures that global/system users can still interact with data.
            if not company:
                try:
                    from apps.users.models import Company
                    company = Company.objects.first()
                except Exception:
                    pass
                    
        request.company = company
        return self.get_response(request)


class UserPermissionsHashMiddleware(MiddlewareMixin):
    """
    Middleware that adds the X-User-Permissions-Hash header to all responses 
    for authenticated users to allow real-time permission sync on the frontend.
    """
    def process_response(self, request, response):
        if hasattr(request, "user") and request.user and request.user.is_authenticated:
            user = request.user
            cache_key = f"user_perms_hash_{user.id}"
            p_hash = cache.get(cache_key)
            if p_hash is None:
                codes = sorted(list(user.app_permissions.values_list("code", flat=True)))
                content = f"{user.role}:{','.join(codes)}"
                p_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
                # Cache for 5 minutes
                cache.set(cache_key, p_hash, 300)
            
            response["X-User-Permissions-Hash"] = p_hash
        return response
