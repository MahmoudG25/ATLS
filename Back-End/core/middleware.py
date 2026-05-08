class CompanyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        request.company = (
            getattr(user, "company", None)
            if user and getattr(user, "is_authenticated", False)
            else None
        )
        return self.get_response(request)
