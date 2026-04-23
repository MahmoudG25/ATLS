from apps.users.models import Notification

def get_user_notifications(user, unread_only=False):
    """
    Retrieve notifications for a user, optionally only unread.
    """
    qs = Notification.objects.filter(recipient=user)
    if unread_only:
        qs = qs.filter(is_read=False)
    return qs[:50]

def get_unread_count(user):
    """
    Count unread notifications for badge display.
    """
    return Notification.objects.filter(recipient=user, is_read=False).count()

def mark_notification_read(notification_id, user):
    """
    Mark a single notification as read.
    """
    notification = Notification.objects.get(id=notification_id, recipient=user)
    notification.is_read = True
    notification.save()
    return notification

def mark_all_read(user):
    """
    Mark all notifications as read for a user.
    """
    Notification.objects.filter(recipient=user, is_read=False).update(is_read=True)

def create_notification(recipient, message_ar, message_en, notification_type='system', link=''):
    """
    Create a new notification for a user.
    """
    return Notification.objects.create(
        recipient=recipient,
        message_ar=message_ar,
        message_en=message_en,
        type=notification_type,
        link=link,
    )

def notify_admins_new_user(new_user):
    """
    Send notification to all admins when a new user registers.
    """
    from apps.users.models import User
    admins = User.objects.filter(role__in=['SUPER_ADMIN', 'OWNER', 'MANAGER'], is_approved=True, is_active=True)
    for admin in admins:
        create_notification(
            recipient=admin,
            message_ar=f'مستخدم جديد ينتظر الموافقة: {new_user.name}',
            message_en=f'New user pending approval: {new_user.name}',
            notification_type='user_pending',
            link='/admin',
        )
