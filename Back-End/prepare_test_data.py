#!/usr/bin/env python
"""
Step 4 Validation - Database Setup Helper
Prepares the database for testing by ensuring required test data exists.

Run this BEFORE running validate_step4.py if tests are failing due to missing data.

    python prepare_test_data.py

This script:
1. Creates a test company if needed
2. Creates/approves an admin user for testing
3. Creates sample farms and locations if needed
4. Verifies database connectivity
5. Reports success or specific errors
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.users.models import User, Company
from apps.farm.models import Farm, LocationNode
from django.contrib.auth.models import Group

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def log(level, message):
    """Log with color coding"""
    colors = {
        'info': BLUE,
        'success': GREEN,
        'warning': YELLOW,
        'error': RED,
    }
    color = colors.get(level, RESET)
    print(f"{color}[{level.upper()}]{RESET} {message}")

def setup_database():
    """Prepare test database"""
    log('info', "Preparing test database...")
    
    try:
        # Step 1: Create test company if needed
        log('info', "Checking company...")
        company, created = Company.objects.get_or_create(
            name='Test Farm Company',
            defaults={
                'subscription_plan': 'starter',
            }
        )
        if created:
            log('success', f"Created test company: {company.name} (ID: {company.id})")
        else:
            log('info', f"Using existing company: {company.name} (ID: {company.id})")
        
        # Step 2: Create/approve admin user
        log('info', "Checking admin user...")
        admin_user, created = User.objects.get_or_create(
            email='admin@example.com',
            defaults={
                'name': 'Admin User',
                'company': company,
                'is_approved': True,
                'is_active': True,
                'role': 'SUPER_ADMIN',
            }
        )
        
        admin_user.set_password('admin')
        admin_user.is_approved = True
        admin_user.is_active = True
        admin_user.save()
        if created:
            log('success', f"Created admin user: {admin_user.email}")
        else:
            log('success', f"Updated and verified admin user password: {admin_user.email}")
        
        # Step 3: Create sample farm if needed
        log('info', "Checking farms...")
        farm, created = Farm.objects.get_or_create(
            company=company,
            name='Test Farm Alpha',
            defaults={
                'is_active': True,
            }
        )
        
        if created:
            log('success', f"Created test farm: {farm.name} (ID: {farm.id})")
        else:
            log('info', f"Using existing farm: {farm.name} (ID: {farm.id})")
        
        # Step 4: Create sample location node if needed
        log('info', "Checking location nodes...")
        node, created = LocationNode.objects.get_or_create(
            farm=farm,
            name='Test Sector 1',
            defaults={
                'company': company,
                'type': 'SECTOR',
                'is_active': True,
            }
        )
        
        if created:
            log('success', f"Created test location node: {node.name} (ID: {node.id})")
        else:
            log('info', f"Using existing location node: {node.name} (ID: {node.id})")
        
        # Step 5: Summary
        print()
        log('info', "Database Preparation Summary:")
        log('success', f"  Company: {company.name} (ID: {company.id})")
        log('success', f"  Admin User: {admin_user.email} (approved: {admin_user.is_approved})")
        log('success', f"  Farm: {farm.name} (ID: {farm.id})")
        log('success', f"  Location Node: {node.name} (ID: {node.id})")
        print()
        
        log('success', "Database preparation complete!")
        log('info', "You can now run: python validate_step4.py")
        
        return True
        
    except Exception as e:
        log('error', f"Database setup failed: {e}")
        log('error', "Make sure:")
        log('error', "  1. PostgreSQL is running")
        log('error', "  2. Database 'erp_db' exists")
        log('error', "  3. Django migrations have been applied: python manage.py migrate")
        return False

if __name__ == "__main__":
    try:
        success = setup_database()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        log('warning', "Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        log('error', f"Unexpected error: {e}")
        sys.exit(1)
