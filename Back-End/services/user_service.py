from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from apps.users.models import User


def create_user(validated_data):
    """
    Register a new user.
    By default, users are NOT approved upon registration.
    """
    password = validated_data.pop("password", None)
    user = User(**validated_data)
    user.is_approved = False  # Ensures user is not approved
    
    # --- TEMPORARY SINGLE-TENANT COMPATIBILITY FALLBACK ---
    # TODO: [Strict Tenant Assignment Enforcement]
    # Future multi-tenant expansion MUST require the registration flow 
    # or an admin to explicitly map users to a specific company.
    # For now, we auto-assign to the first company to prevent orphaned users.
    from apps.users.models import Company
    main_company = Company.objects.first()
    if main_company:
        user.company = main_company
    # ------------------------------------------------------
        
    if password:
        user.set_password(password)
    user.save()
    return user


def authenticate_user(email, password):
    """
    Authenticate user, check constraints, and generate JWT.
    """
    user = authenticate(email=email, password=password)

    if not user:
        raise AuthenticationFailed("Invalid email or password.")

    if not user.is_approved:
        raise PermissionDenied("Your account is pending approval.")

    if not user.is_active:
        raise PermissionDenied("Your account has been deactivated.")

    refresh = RefreshToken.for_user(user)
    return {"refresh": str(refresh), "access": str(refresh.access_token), "user": user}


def approve_user(user_id):
    """
    Approve a pending user.
    """
    user = User.objects.get(id=user_id)
    user.is_approved = True
    user.save()
    return user


def deactivate_user(user_id):
    """
    Deactivate an active user.
    """
    user = User.objects.get(id=user_id)
    user.is_active = False
    opt = user.is_approved
    user.is_approved = False  # Revoke approvals implicitly if deactivated
    user.save()
    return user


def list_users():
    """
    List all platform accounts for admin governance.
    """
    return User.objects.all().order_by("-date_joined")


def soft_delete_user(user_id):
    """
    Soft delete a user by deactivating and altering email to prevent login but retain data.
    """
    user = User.objects.get(id=user_id)
    user.is_active = False
    user.is_approved = False
    if not user.email.startswith("deleted_"):
        user.email = f"deleted_{user.id}_{user.email}"
    user.save()
    return user


def update_user_role(user_id, new_role):
    """
    Update a user's role.
    """
    user = User.objects.get(id=user_id)
    user.role = new_role
    user.save()
    return user


def change_user_password(user, old_password, new_password):
    """
    Validate old password and securely set the new one.
    """
    if not user.check_password(old_password):
        from rest_framework.exceptions import AuthenticationFailed

        raise AuthenticationFailed("Old password does not match.")
    user.set_password(new_password)
    user.save()
