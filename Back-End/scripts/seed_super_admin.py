import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from apps.users.models import User, Company

def seed():
    print("Creating system company...")
    company, created = Company.objects.get_or_create(
        name="System Admin Company",
        defaults={
            "subscription_plan": "enterprise"
        }
    )
    if created:
        print(f"Company '{company.name}' created.")
    
    print("Creating Super Admin user...")
    email = "admin@example.com"
    if not User.objects.filter(email=email).exists():
        user = User.objects.create_superuser(
            email=email,
            password="adminpassword123",
            name="Super Admin",
            company=company
        )
        print(f"Super Admin created with email: {email} and password: adminpassword123")
    else:
        print(f"Super Admin with email {email} already exists.")

if __name__ == "__main__":
    seed()
