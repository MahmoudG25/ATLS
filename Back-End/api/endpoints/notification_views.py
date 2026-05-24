from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from services.notification_service import (
    get_user_notifications,
    get_unread_count,
    mark_notification_read,
    mark_all_read,
)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def notifications_list_view(request):
    """
    GET /api/notifications/
    Returns notifications for the current user.
    Query params: ?unread=true for unread only.
    """
    unread_only = request.query_params.get("unread", "").lower() == "true"
    notifications = get_user_notifications(request.user, unread_only=unread_only)
    unread_count = get_unread_count(request.user)

    data = [
        {
            "id": n.id,
            "message_ar": n.message_ar,
            "message_en": n.message_en,
            "type": n.type,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat(),
            "link": n.link,
        }
        for n in notifications
    ]

    return Response(
        {
            "notifications": data,
            "unread_count": unread_count,
        }
    )


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def notification_read_view(request, id):
    """
    PATCH /api/notifications/{id}/read/
    Mark a single notification as read.
    """
    try:
        mark_notification_read(id, request.user)
        return Response({"message": "Notification marked as read."})
    except Exception:
        return Response(
            {"detail": "Notification not found."}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def notifications_read_all_view(request):
    """
    PATCH /api/notifications/read-all/
    Mark all notifications as read.
    """
    mark_all_read(request.user)
    return Response({"message": "All notifications marked as read."})
