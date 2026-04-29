
import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def check_tables():
    with connection.cursor() as cursor:
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE 'reports_%';")
        tables = [row[0] for row in cursor.fetchall()]
        print("Existing reports tables:", tables)
        
        expected = ['reports_variety', 'reports_unit', 'reports_contractor', 'reports_dailytaskreport']
        for table in expected:
            if table not in tables:
                print(f"MISSING TABLE: {table}")

if __name__ == "__main__":
    check_tables()
