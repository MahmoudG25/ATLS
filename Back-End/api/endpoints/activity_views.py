from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.users.models import ActivityLog
from serializers.user_serializers import ActivityLogSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def activity_log_view(request):
    """
    Returns activity logs.
    Employees see only their own.
    Super Admin and Managers see all.
    """
    user = request.user
    if user.role in ["SUPER_ADMIN", "MANAGER"]:
        logs = ActivityLog.objects.all()
    else:
        logs = ActivityLog.objects.filter(user=user)

    # Optional filtering by module
    module = request.query_params.get("module")
    if module:
        logs = logs.filter(module=module)

    return Response(ActivityLogSerializer(logs[:100], many=True).data)
