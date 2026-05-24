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
