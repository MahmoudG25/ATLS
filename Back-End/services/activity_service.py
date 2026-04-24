from apps.users.models import ActivityLog

def log_activity(user, action, module, description="", ip_address=None):
    """
    Logs a user activity to the database.
    """
    try:
        ActivityLog.objects.create(
            user=user,
            action=action,
            module=module,
            description=description,
            ip_address=ip_address
        )
    except Exception as e:
        # We don't want activity logging to break the main flow
        print(f"Error logging activity: {e}")
