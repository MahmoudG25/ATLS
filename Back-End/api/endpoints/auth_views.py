from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from serializers.user_serializers import (
    UserSerializer,
    RegisterSerializer,
    LoginSerializer,
)
from services.user_service import (
    create_user,
    authenticate_user,
    approve_user,
    list_users,
    deactivate_user,
    soft_delete_user,
    update_user_role,
)
from permissions.role_permissions import IsSuperAdmin, CanManageUsers
from apps.users.models import LandingContent


@api_view(["GET"])
@permission_classes([AllowAny])
def landing_content_view(request):
    """
    GET /auth/public/landing
    Returns public landing page content.
    """
    content = LandingContent.objects.first()
    if not content:
        content = LandingContent.objects.create()

    return Response(
        {
            "en": {
                "translation": {
                    "hero_title": content.hero_title_en,
                    "hero_text": content.hero_text_en,
                    "palm_text": content.palm_text_en,
                    "olive_text": content.olive_text_en,
                    "logo_text": content.logo_text_en,
                    "logo_url": content.logo_url,
                    "about_title": content.about_title_en,
                    "about_text": content.about_text_en,
                    "features_title": content.features_title_en,
                    "contact_title": content.contact_title_en,
                    "contact_text": content.contact_text_en,
                    "contact_email": content.contact_email,
                    "contact_phone": content.contact_phone,
                }
            },
            "ar": {
                "translation": {
                    "hero_title": content.hero_title_ar,
                    "hero_text": content.hero_text_ar,
                    "palm_text": content.palm_text_ar,
                    "olive_text": content.olive_text_ar,
                    "logo_text": content.logo_text_ar,
                    "logo_url": content.logo_url,
                    "about_title": content.about_title_ar,
                    "about_text": content.about_text_ar,
                    "features_title": content.features_title_ar,
                    "contact_title": content.contact_title_ar,
                    "contact_text": content.contact_text_ar,
                    "contact_email": content.contact_email,
                    "contact_phone": content.contact_phone,
                }
            },
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
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
    return Response(
        {
            "message": "Registration successful. Waiting for admin approval.",
            "user": UserSerializer(user).data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    """
    POST /auth/login
    Authenticates an approved, active user and returns JWT.
    """
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    tokens = authenticate_user(
        email=serializer.validated_data["email"],
        password=serializer.validated_data["password"],
    )

    return Response(
        {
            "access": tokens["access"],
            "refresh": tokens["refresh"],
            "user": UserSerializer(tokens["user"]).data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def me_view(request):
    """
    GET /auth/me - Returns current authenticated user details.
    PATCH /auth/me - Updates current authenticated user details (name, phones).
    """
    if request.method == "GET":
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == "PATCH":
        # Exclude critical fields from being updated directly via PATCH
        if "role" in request.data:
            request.data.pop("role")
        if "is_approved" in request.data:
            request.data.pop("is_approved")
        if "is_active" in request.data:
            request.data.pop("is_active")

        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    """
    PATCH /auth/me/security - Change current user's password.
    """
    old_password = request.data.get("old_password")
    new_password = request.data.get("new_password")

    if not old_password or not new_password:
        return Response(
            {"detail": "Both old and new passwords are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        from services.user_service import change_user_password

        change_user_password(request.user, old_password, new_password)
        return Response(
            {"message": "Password updated successfully."}, status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated, CanManageUsers])
def approve_user_view(request, id):
    """
    PATCH /users/{id}/approve
    Admin only: Approves a user account.
    """
    try:
        user = approve_user(id)
        return Response(
            {
                "message": "User approved successfully.",
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )
    except ObjectDoesNotExist:
        return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated, CanManageUsers])
def deactivate_user_view(request, id):
    """
    PATCH /users/{id}/deactivate
    Admin only: Deactivates a user account.
    """
    try:
        user = deactivate_user(id)
        return Response(
            {
                "message": "User deactivated successfully.",
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )
    except ObjectDoesNotExist:
        return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
@permission_classes([IsAuthenticated, CanManageUsers])
def users_collection_view(request):
    """
    GET /users
    Admin only: Retrieve full account architecture.
    """
    users = list_users()
    return Response(UserSerializer(users, many=True).data)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def update_user_role_view(request, id):
    """
    PATCH /users/{id}/role
    Admin only: Updates a user's role.
    """
    role = request.data.get("role")
    if not role:
        return Response(
            {"detail": "Role is required."}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        user = update_user_role(id, role)
        return Response(
            {"message": "Role updated.", "user": UserSerializer(user).data},
            status=status.HTTP_200_OK,
        )
    except ObjectDoesNotExist:
        return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def delete_user_view(request, id):
    """
    DELETE /users/{id}/delete
    Admin only: Soft deletes a user account.
    """
    try:
        soft_delete_user(id)
        return Response(
            {"message": "User soft deleted successfully."}, status=status.HTTP_200_OK
        )
    except ObjectDoesNotExist:
        return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def engineers_list_view(request):
    """
    GET /users/engineers
    Returns active, approved users eligible to be assigned as engineers
    on a DailyTaskReport (ENGINEER, MANAGER, OWNER, SUPER_ADMIN roles).
    Accessible to all authenticated users — used by report creation forms.
    Scoped to the requester's company (multi-tenant safe).
    Returns minimal payload: id, name, role only.
    """
    from apps.users.models import User

    FIELD_ROLES = ["ENGINEER", "MANAGER", "OWNER", "SUPER_ADMIN"]
    qs = User.objects.filter(is_active=True, is_approved=True, role__in=FIELD_ROLES)
    if getattr(request.user, "company_id", None):
        qs = qs.filter(company_id=request.user.company_id)
    return Response(
        [{"id": u.id, "name": u.name, "role": u.role} for u in qs.order_by("name")]
    )


@api_view(["GET", "PATCH"])
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

    if request.method == "GET":
        return Response(
            {
                "hero_title_en": content.hero_title_en,
                "hero_title_ar": content.hero_title_ar,
                "hero_text_en": content.hero_text_en,
                "hero_text_ar": content.hero_text_ar,
                "palm_text_en": content.palm_text_en,
                "palm_text_ar": content.palm_text_ar,
                "olive_text_en": content.olive_text_en,
                "olive_text_ar": content.olive_text_ar,
                "logo_text_en": content.logo_text_en,
                "logo_text_ar": content.logo_text_ar,
                "logo_url": content.logo_url,
                "about_title_en": content.about_title_en,
                "about_title_ar": content.about_title_ar,
                "about_text_en": content.about_text_en,
                "about_text_ar": content.about_text_ar,
                "features_title_en": content.features_title_en,
                "features_title_ar": content.features_title_ar,
                "contact_title_en": content.contact_title_en,
                "contact_title_ar": content.contact_title_ar,
                "contact_text_en": content.contact_text_en,
                "contact_text_ar": content.contact_text_ar,
                "contact_email": content.contact_email,
                "contact_phone": content.contact_phone,
            },
            status=status.HTTP_200_OK,
        )

    elif request.method == "PATCH":
        for field, value in request.data.items():
            if hasattr(content, field):
                setattr(content, field, value)
        content.save()
        return Response(
            {"detail": "Landing Content Updated"}, status=status.HTTP_200_OK
        )


import random
from apps.users.models import User, PasswordResetRequest

@api_view(["POST"])
@permission_classes([AllowAny])
def password_reset_request_view(request):
    """
    POST /auth/password-reset/request
    Submit a password reset request. Generates a 6-digit code.
    """
    email = request.data.get("email")
    if not email:
        return Response({"detail": "البريد الإلكتروني مطلوب."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if user exists
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"detail": "البريد الإلكتروني غير مسجل في النظام."}, status=status.HTTP_404_NOT_FOUND)
        
    # Generate 6-digit random code
    code = f"{random.randint(100000, 999999)}"
    
    # Deactivate or mark old requests as used
    PasswordResetRequest.objects.filter(email=email, is_used=False).update(is_used=True)
    
    # Create new request
    reset_req = PasswordResetRequest.objects.create(
        email=email,
        code=code,
        is_approved=False
    )
    
    # Create a system notification for admins/managers
    try:
        from apps.users.models import Notification
        # Get managers and super admins
        managers = User.objects.filter(role__in=["SUPER_ADMIN", "OWNER", "MANAGER"])
        for manager in managers:
            Notification.objects.create(
                recipient=manager,
                message_ar=f"طلب استرداد كلمة المرور للمستخدم {email}. الرمز: {code}",
                message_en=f"Password recovery requested for user {email}. Code: {code}",
                type="system"
            )
    except Exception:
        pass
        
    return Response({
        "message": "تم تقديم طلب استرداد كلمة المرور بنجاح للمدير المباشر.",
        "code": code  # Return code so user can tell manager offline
    }, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([AllowAny])
def password_reset_status_view(request):
    """
    POST /auth/password-reset/status
    Check if a reset code has been approved by the manager.
    """
    email = request.data.get("email")
    code = request.data.get("code")
    if not email or not code:
        return Response({"detail": "البريد الإلكتروني والرمز مطلوبان."}, status=status.HTTP_400_BAD_REQUEST)
        
    try:
        req = PasswordResetRequest.objects.get(email=email, code=code, is_used=False)
        return Response({
            "is_approved": req.is_approved,
            "is_used": req.is_used
        }, status=status.HTTP_200_OK)
    except PasswordResetRequest.DoesNotExist:
        return Response({"detail": "رمز التحقق أو البريد الإلكتروني غير صحيح، أو انتهت صلاحية الطلب."}, status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
@permission_classes([AllowAny])
def password_reset_confirm_view(request):
    """
    POST /auth/password-reset/confirm
    Reset user password after manager has approved the reset request.
    """
    email = request.data.get("email")
    code = request.data.get("code")
    new_password = request.data.get("new_password")
    
    if not email or not code or not new_password:
        return Response({"detail": "جميع الحقول مطلوبة."}, status=status.HTTP_400_BAD_REQUEST)
        
    try:
        req = PasswordResetRequest.objects.get(email=email, code=code, is_approved=True, is_used=False)
    except PasswordResetRequest.DoesNotExist:
        return Response({"detail": "الطلب لم يوافق عليه المدير بعد، أو الرمز غير صحيح."}, status=status.HTTP_400_BAD_REQUEST)
        
    try:
        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.save()
        
        # Mark request as used
        req.is_used = True
        req.save()
        
        return Response({"message": "تم تغيير كلمة المرور بنجاح. يمكنك الآن تسجيل الدخول."}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"detail": "المستخدم غير موجود."}, status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_password_resets_list_view(request):
    """
    GET /auth/admin/password-resets
    Lists all pending password reset requests for managers.
    """
    # Verify the requester is a manager or admin
    if request.user.role not in ["SUPER_ADMIN", "OWNER", "MANAGER"]:
        return Response({"detail": "غير مصرح لك بالوصول لهذا القسم."}, status=status.HTTP_403_FORBIDDEN)
        
    reqs = PasswordResetRequest.objects.filter(is_used=False).order_by("-created_at")
    
    # Map to serializable response
    data = []
    for r in reqs:
        data.append({
            "id": str(r.id),
            "email": r.email,
            "code": r.code,
            "is_approved": r.is_approved,
            "created_at": r.created_at.isoformat() if r.created_at else None
        })
        
    return Response(data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def admin_password_reset_action_view(request, id, action):
    """
    POST /auth/admin/password-resets/<uuid:id>/<str:action>
    Approve or reject a password reset request.
    """
    if request.user.role not in ["SUPER_ADMIN", "OWNER", "MANAGER"]:
        return Response({"detail": "غير مصرح لك بالوصول لهذا القسم."}, status=status.HTTP_403_FORBIDDEN)
        
    try:
        req = PasswordResetRequest.objects.get(id=id)
    except PasswordResetRequest.DoesNotExist:
        return Response({"detail": "الطلب غير موجود."}, status=status.HTTP_404_NOT_FOUND)
        
    if action == "approve":
        req.is_approved = True
        req.save()
        return Response({"message": "تمت الموافقة على طلب استعادة كلمة المرور بنجاح."}, status=status.HTTP_200_OK)
    elif action == "reject":
        req.is_used = True # Mark as used/invalidated
        req.save()
        return Response({"message": "تم رفض طلب استعادة كلمة المرور بنجاح."}, status=status.HTTP_200_OK)
    else:
        return Response({"detail": "إجراء غير صالح."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def get_app_permissions_view(request):
    """
    GET /api/auth/permissions
    Lists all available custom permissions.
    """
    from apps.users.models import AppPermission
    if AppPermission.objects.count() == 0 or not AppPermission.objects.filter(code="can_post_announcement").exists():
        defaults = [
            ("reports.create", "إضافة التقارير", "صلاحية كتابة تقرير يومي أو تقرير حصاد"),
            ("reports.delete", "حذف التقارير", "صلاحية حذف التقارير اليومية أو الحصاد"),
            ("farm.manage", "إدارة هيكل المزرعة", "صلاحية إدارة الأقسام والقطاعات والأحواش"),
            ("warehouse.manage", "إدارة المخازن والمخزون", "صلاحية إضافة وتعديل المخازن وحركات المخزون"),
            ("accounting.view", "عرض التقارير المالية", "صلاحية استعراض المصروفات والإيرادات في الحسابات"),
            ("equipment.manage", "إدارة الأسطول والمعدات", "صلاحية إضافة المعدات وتحديثها وتغيير الزيت"),
            ("hr.manage", "إدارة الموارد البشرية", "صلاحية إدارة شؤون الموظفين والعمال والرواتب"),
            ("can_post_announcement", "نشر الإعلانات", "صلاحية نشر وإدارة الإعلانات على لوحة الإعلانات"),
        ]
        for code, name, desc in defaults:
            AppPermission.objects.get_or_create(code=code, defaults={"name": name, "description": desc})
            
    perms = AppPermission.objects.all().order_by("name")
    return Response([
        {"id": str(p.id), "code": p.code, "name": p.name, "description": p.description}
        for p in perms
    ])


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def user_permissions_view(request, id):
    """
    GET /api/users/<uuid:id>/permissions - Get user permissions
    POST /api/users/<uuid:id>/permissions - Update user permissions
    """
    from apps.users.models import User, AppPermission
    try:
        user = User.objects.get(id=id)
        # Check company if not super admin
        if request.user.role != "SUPER_ADMIN" and user.company != request.user.company:
            return Response({"detail": "غير مصرح لك بالوصول لهذا المستخدم."}, status=status.HTTP_403_FORBIDDEN)
            
        if request.method == "GET":
            perms = user.app_permissions.all()
            return Response([p.code for p in perms])
            
        elif request.method == "POST":
            permission_codes = request.data.get("permissions", [])
            perms = AppPermission.objects.filter(code__in=permission_codes)
            user.app_permissions.set(perms)
            user.save()
            return Response({"message": "تم تحديث الصلاحيات بنجاح."})
            
    except User.DoesNotExist:
        return Response({"detail": "المستخدم غير موجود."}, status=status.HTTP_404_NOT_FOUND)


# ============================================================================
# ANNOUNCEMENTS — Bulletin Board
# ============================================================================

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def announcements_view(request):
    """
    GET  /api/announcements/ — All users: list active announcements for their company.
    POST /api/announcements/ — Users with can_post_announcement (or SUPER_ADMIN/OWNER) can create.
    """
    from apps.users.models import Announcement
    from django.db.models import Q

    company = getattr(request.user, "company", None)

    if request.method == "GET":
        category = request.query_params.get("category")
        is_pinned = request.query_params.get("is_pinned")
        is_archived = request.query_params.get("is_archived")
        q = request.query_params.get("q")

        qs = Announcement.objects.filter(is_active=True)
        if company:
            qs = qs.filter(company=company)

        if category:
            qs = qs.filter(category=category)
        if is_pinned is not None:
            qs = qs.filter(is_pinned=is_pinned.lower() == "true")
        if is_archived is not None:
            qs = qs.filter(is_archived=is_archived.lower() == "true")
        else:
            qs = qs.filter(is_archived=False)

        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(body__icontains=q))

        qs = qs.order_by("-is_pinned", "-created_at")

        total_count = qs.count()
        page = request.query_params.get("page")
        page_size = request.query_params.get("page_size") or 10

        if page:
            try:
                page = int(page)
                page_size = int(page_size)
                start = (page - 1) * page_size
                end = start + page_size
                qs_slice = qs[start:end]
                
                has_next = end < total_count
                total_pages = (total_count + page_size - 1) // page_size
                
                data = [
                    {
                        "id": a.id,
                        "title": a.title,
                        "body": a.body,
                        "image_url": a.image_url,
                        "video_url": a.video_url,
                        "file_url": a.file_url,
                        "file_name": a.file_name,
                        "is_pinned": a.is_pinned,
                        "is_archived": a.is_archived,
                        "category": a.category,
                        "published_by": a.published_by.name if a.published_by else "النظام",
                        "created_at": a.created_at.isoformat(),
                    }
                    for a in qs_slice
                ]
                return Response({
                    "results": data,
                    "count": total_count,
                    "total_pages": total_pages,
                    "current_page": page,
                    "has_next": has_next
                })
            except ValueError:
                pass

        data = [
            {
                "id": a.id,
                "title": a.title,
                "body": a.body,
                "image_url": a.image_url,
                "video_url": a.video_url,
                "file_url": a.file_url,
                "file_name": a.file_name,
                "is_pinned": a.is_pinned,
                "is_archived": a.is_archived,
                "category": a.category,
                "published_by": a.published_by.name if a.published_by else "النظام",
                "created_at": a.created_at.isoformat(),
            }
            for a in qs[:30]
        ]
        return Response(data)

    # POST — check permission
    role = getattr(request.user, "role", "")
    has_perm = role in ["SUPER_ADMIN", "OWNER", "MANAGER"] or \
               request.user.app_permissions.filter(code="can_post_announcement").exists()

    if not has_perm:
        return Response({"detail": "ليس لديك صلاحية نشر إعلانات."}, status=status.HTTP_403_FORBIDDEN)

    title = request.data.get("title", "").strip()
    if not title:
        return Response({"detail": "عنوان الإعلان مطلوب."}, status=status.HTTP_400_BAD_REQUEST)

    ann = Announcement.objects.create(
        company=company,
        title=title,
        body=request.data.get("body", ""),
        image_url=request.data.get("image_url", ""),
        video_url=request.data.get("video_url", ""),
        file_url=request.data.get("file_url", ""),
        file_name=request.data.get("file_name", ""),
        is_pinned=request.data.get("is_pinned", False),
        is_archived=request.data.get("is_archived", False),
        category=request.data.get("category", "general"),
        published_by=request.user,
    )
    return Response({
        "id": ann.id,
        "title": ann.title,
        "body": ann.body,
        "image_url": ann.image_url,
        "video_url": ann.video_url,
        "file_url": ann.file_url,
        "file_name": ann.file_name,
        "is_pinned": ann.is_pinned,
        "is_archived": ann.is_archived,
        "category": ann.category,
        "published_by": ann.published_by.name if ann.published_by else "النظام",
        "created_at": ann.created_at.isoformat(),
    }, status=status.HTTP_201_CREATED)


@api_view(["PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def announcement_detail_view(request, pk):
    """
    PATCH  /api/announcements/<pk>/ — Edit an announcement (publisher or admin only).
    DELETE /api/announcements/<pk>/ — Soft-delete an announcement (publisher or admin only).
    """
    from apps.users.models import Announcement

    try:
        ann = Announcement.objects.get(pk=pk)
    except Announcement.DoesNotExist:
        return Response({"detail": "الإعلان غير موجود."}, status=status.HTTP_404_NOT_FOUND)

    role = getattr(request.user, "role", "")
    is_owner = ann.published_by == request.user
    is_admin = role in ["SUPER_ADMIN", "OWNER", "MANAGER"]

    if not (is_owner or is_admin):
        return Response({"detail": "ليس لديك الصلاحية لتعديل أو حذف هذا الإعلان."}, status=status.HTTP_403_FORBIDDEN)

    if request.method == "PATCH":
        editable = ["title", "body", "image_url", "video_url", "file_url", "file_name", "is_pinned", "is_archived", "category"]
        for field in editable:
            if field in request.data:
                setattr(ann, field, request.data[field])
        ann.save()
        return Response({
            "id": ann.id,
            "title": ann.title,
            "body": ann.body,
            "image_url": ann.image_url,
            "video_url": ann.video_url,
            "file_url": ann.file_url,
            "file_name": ann.file_name,
            "is_pinned": ann.is_pinned,
            "is_archived": ann.is_archived,
            "category": ann.category,
            "published_by": ann.published_by.name if ann.published_by else "النظام",
            "created_at": ann.created_at.isoformat(),
        })

    # DELETE
    ann.is_active = False
    ann.save(update_fields=["is_active"])
    return Response({"message": "تم حذف الإعلان بنجاح."})


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def reset_user_avatar_view(request, id):
    """
    PATCH /api/users/<uuid:id>/reset-avatar
    Resets the avatar_url of a user.
    Accessible by the user themselves or users with roles: SUPER_ADMIN, OWNER, MANAGER.
    If not SUPER_ADMIN, user.company must match request.user.company.
    """
    from apps.users.models import User
    try:
        user = User.objects.get(id=id)
    except (User.DoesNotExist, ValueError):
        return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    # Permission check:
    requester = request.user
    is_self = requester.id == user.id
    is_admin = requester.role in ["SUPER_ADMIN", "OWNER", "MANAGER"]

    if not (is_self or is_admin):
        return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

    # Tenant isolation:
    if requester.role != "SUPER_ADMIN":
        if user.company_id != requester.company_id:
            return Response({"detail": "Permission denied. Users belong to different companies."}, status=status.HTTP_403_FORBIDDEN)

    user.avatar_url = ""
    user.save()

    return Response(UserSerializer(user).data, status=status.HTTP_200_OK)

