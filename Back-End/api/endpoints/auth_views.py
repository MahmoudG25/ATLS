from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from serializers.user_serializers import UserSerializer, RegisterSerializer, LoginSerializer
from services.user_service import create_user, authenticate_user, approve_user, list_users, deactivate_user, soft_delete_user, update_user_role
from permissions.role_permissions import IsSuperAdmin, CanManageUsers
from apps.users.models import LandingContent

@api_view(['GET'])
@permission_classes([AllowAny])
def landing_content_view(request):
    """
    GET /auth/public/landing
    Returns public landing page content.
    """
    content = LandingContent.objects.first()
    if not content:
        content = LandingContent.objects.create()
    
    return Response({
        'en': {
            'translation': {
                'hero_title': content.hero_title_en,
                'hero_text': content.hero_text_en,
                'palm_text': content.palm_text_en,
                'olive_text': content.olive_text_en,
            }
        },
        'ar': {
            'translation': {
                'hero_title': content.hero_title_ar,
                'hero_text': content.hero_text_ar,
                'palm_text': content.palm_text_ar,
                'olive_text': content.olive_text_ar,
            }
        }
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    POST /auth/register
    Creates a new user account (pending approval).
    """
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = create_user(serializer.validated_data)
    # Notify admins of new pending user
    try:
        from services.notification_service import notify_admins_new_user
        notify_admins_new_user(user)
    except Exception:
        pass  # Non-critical — don't block registration
    return Response({
        'message': 'Registration successful. Waiting for admin approval.',
        'user': UserSerializer(user).data
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    POST /auth/login
    Authenticates an approved, active user and returns JWT.
    """
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    tokens = authenticate_user(
        email=serializer.validated_data['email'],
        password=serializer.validated_data['password']
    )
    
    return Response({
        'access': tokens['access'],
        'refresh': tokens['refresh'],
        'user': UserSerializer(tokens['user']).data
    }, status=status.HTTP_200_OK)

@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def me_view(request):
    """
    GET /auth/me - Returns current authenticated user details.
    PATCH /auth/me - Updates current authenticated user details (name, phones).
    """
    if request.method == 'GET':
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PATCH':
        # Exclude critical fields from being updated directly via PATCH
        if 'role' in request.data: request.data.pop('role')
        if 'is_approved' in request.data: request.data.pop('is_approved')
        if 'is_active' in request.data: request.data.pop('is_active')

        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    """
    PATCH /auth/me/security - Change current user's password.
    """
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    
    if not old_password or not new_password:
        return Response({'detail': 'Both old and new passwords are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
    try:
        from services.user_service import change_user_password
        change_user_password(request.user, old_password, new_password)
        return Response({'message': 'Password updated successfully.'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated, CanManageUsers])
def approve_user_view(request, id):
    """
    PATCH /users/{id}/approve
    Admin only: Approves a user account.
    """
    try:
        user = approve_user(id)
        return Response({
            'message': 'User approved successfully.',
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated, CanManageUsers])
def deactivate_user_view(request, id):
    """
    PATCH /users/{id}/deactivate
    Admin only: Deactivates a user account.
    """
    try:
        user = deactivate_user(id)
        return Response({
            'message': 'User deactivated successfully.',
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated, CanManageUsers])
def users_collection_view(request):
    """
    GET /users
    Admin only: Retrieve full account architecture.
    """
    users = list_users()
    return Response(UserSerializer(users, many=True).data)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def update_user_role_view(request, id):
    """
    PATCH /users/{id}/role
    Admin only: Updates a user's role.
    """
    role = request.data.get('role')
    if not role:
        return Response({'detail': 'Role is required.'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        user = update_user_role(id, role)
        return Response({'message': 'Role updated.', 'user': UserSerializer(user).data}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def delete_user_view(request, id):
    """
    DELETE /users/{id}/delete
    Admin only: Soft deletes a user account.
    """
    try:
        soft_delete_user(id)
        return Response({'message': 'User soft deleted successfully.'}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def manage_landing_content_view(request):
    """
    GET /auth/admin/landing-content - Admin retrieval of raw string config.
    PATCH /auth/admin/landing-content - Updates the site's CMS strings natively.
    """
    from apps.users.models import LandingContent
    content = LandingContent.objects.first()
    if not content:
        content = LandingContent.objects.create()

    if request.method == 'GET':
        return Response({
            'hero_title_en': content.hero_title_en,
            'hero_title_ar': content.hero_title_ar,
            'hero_text_en': content.hero_text_en,
            'hero_text_ar': content.hero_text_ar,
            'palm_text_en': content.palm_text_en,
            'palm_text_ar': content.palm_text_ar,
            'olive_text_en': content.olive_text_en,
            'olive_text_ar': content.olive_text_ar,
        }, status=status.HTTP_200_OK)
    
    elif request.method == 'PATCH':
        for field, value in request.data.items():
            if hasattr(content, field):
                setattr(content, field, value)
        content.save()
        return Response({"detail": "Landing Content Updated"}, status=status.HTTP_200_OK)
