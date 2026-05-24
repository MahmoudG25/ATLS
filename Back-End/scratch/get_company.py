import os
import sys
sys.path.append(os.getcwd())

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()
from apps.users.models import Company
company = Company.objects.first()
if company:
    print("COMPANY_ID:", company.id)
else:
    print("NO COMPANY FOUND")
