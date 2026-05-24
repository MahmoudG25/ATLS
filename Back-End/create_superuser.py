import os
import django

def create_admin_superuser():
    # Set the settings module for the Django project
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    django.setup()

    from apps.users.models import User, Company

    email = "admin@example.com"
    password = "admin123"

    # Get or create a default company so the user has full access context
    company = Company.objects.first()
    if not company:
        company = Company.objects.create(name="شركة أطلس الزراعية", subscription_plan="enterprise")
        print(f"Created default company: {company.name}")

    try:
        user = User.objects.get(email=email)
        print(f"User {email} already exists. Updating credentials and settings...")
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.is_approved = True
        user.is_active = True
        user.role = "SUPER_ADMIN"
        if not user.company:
            user.company = company
        user.save()
        print(f"Successfully updated superuser credentials for {email}")
    except User.DoesNotExist:
        print(f"Creating superuser {email}...")
        user = User.objects.create_superuser(
            email=email,
            password=password,
            name="Super Admin",
            company=company,
        )
        print(f"Successfully created superuser {email}")

if __name__ == "__main__":
    create_admin_superuser()
