
import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def check_columns():
    with connection.cursor() as cursor:
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'reports_dailytaskreport';")
        columns = [row[0] for row in cursor.fetchall()]
        print("Columns in reports_dailytaskreport:", columns)

if __name__ == "__main__":
    check_columns()
