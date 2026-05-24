import os
import django
from django.db import connection

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

with connection.cursor() as cursor:
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'reports_dailytaskreport'
    """)
    rows = cursor.fetchall()
    for row in rows:
        print(f"Column: {row[0]}, Type: {row[1]}")
