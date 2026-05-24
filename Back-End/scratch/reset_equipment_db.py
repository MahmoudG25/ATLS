import os
import sys
import shutil

sys.path.append(os.getcwd())

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.db import connection

print("Dropping equipment tables...")
with connection.cursor() as cursor:
    cursor.execute("DROP TABLE IF EXISTS equipment_oilchangelog CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS equipment_usage CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS equipment_maintenance CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS equipment_equipment CASCADE;")
    cursor.execute("DELETE FROM django_migrations WHERE app = 'equipment';")
print("Tables dropped successfully.")

migrations_dir = os.path.join("apps", "equipment", "migrations")
print("Cleaning up migrations in:", migrations_dir)
for filename in os.listdir(migrations_dir):
    if filename != "__init__.py" and filename != "__pycache__":
        filepath = os.path.join(migrations_dir, filename)
        if os.path.isfile(filepath):
            os.remove(filepath)
        elif os.path.isdir(filepath):
            shutil.rmtree(filepath)

# Also clear pycache
pycache_dir = os.path.join(migrations_dir, "__pycache__")
if os.path.exists(pycache_dir):
    shutil.rmtree(pycache_dir)

print("Migration cleanup done.")
