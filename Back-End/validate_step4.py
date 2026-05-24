#!/usr/bin/env python
"""
Step 4 Validation Script
Tests the primary workflow: Farm → LocationNode → Reports

Run this AFTER starting the Django dev server:
    python manage.py runserver 0.0.0.0:8000

Then in another terminal:
    python validate_step4.py
"""

import os
import sys
import django
import requests
import json
from django.utils import timezone
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.users.models import User, Company
from apps.farm.models import Farm, LocationNode
from apps.reports.models import DailyTaskReport

# Configuration
API_BASE = "http://localhost:8000/api"
TEST_EMAIL = "admin@example.com"
TEST_PASSWORD = "admin"

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

class TestRunner:
    def __init__(self):
        self.token = None
        self.user = None
        self.results = []
        
    def log(self, level, message):
        """Log with color coding"""
        colors = {
            'pass': GREEN,
            'fail': RED,
            'info': BLUE,
            'warn': YELLOW,
        }
        color = colors.get(level, RESET)
        print(f"{color}[{level.upper()}]{RESET} {message}")
        
    def test(self, name, condition, blocking=True):
        """Record test result"""
        status = "[PASS]" if condition else "[FAIL]"
        severity = "BLOCKING" if blocking else "warning"
        
        self.results.append({
            'test': name,
            'passed': condition,
            'blocking': blocking,
        })
        
        level = 'pass' if condition else 'fail'
        self.log(level, f"{status} | {name} ({severity})")
        
        return condition
        
    def phase(self, title):
        """Start new test phase"""
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}{title}{RESET}")
        print(f"{BLUE}{'='*60}{RESET}\n")
        
    def run_all(self):
        """Execute all test phases"""
        start_time = datetime.now()
        
        self.phase("PHASE 1: Database State Verification")
        self.phase_1_database()
        
        self.phase("PHASE 2: Authentication")
        self.phase_2_auth()
        
        if not self.token:
            self.log('fail', "Cannot continue without valid token. Stopping.")
            return self.summary(start_time)
        
        self.phase("PHASE 3: Farm CRUD & Tenant Isolation")
        self.phase_3_farms()
        
        self.phase("PHASE 4: Hierarchy & LocationNodes")
        self.phase_4_hierarchy()
        
        self.phase("PHASE 5: Reports Workflow")
        self.phase_5_reports()
        
        self.phase("PHASE 6: Data Integrity & Relationships")
        self.phase_6_integrity()
        
        return self.summary(start_time)
        
    def phase_1_database(self):
        """Verify database state before testing API"""
        self.log('info', "Checking database state...")
        
        # Check for admin user
        try:
            admin = User.objects.filter(email=TEST_EMAIL).first()
            if not admin:
                self.test("Admin user exists", False, blocking=True)
                self.log('warn', f"  Create user: User.objects.create_user(email='{TEST_EMAIL}', password='{TEST_PASSWORD}')")
                self.log('warn', f"  Then approve: user.is_approved = True; user.save()")
                return
            
            self.test("Admin user exists", True)
            
            if admin.company is None:
                self.test("Admin has company", False, blocking=True)
                self.log('warn', "  Assign company to admin user before testing")
                return
            
            self.test("Admin has company", True)
            self.test("Admin is approved", admin.is_approved, blocking=True)
            
            if not admin.is_active:
                self.test("Admin is active", False, blocking=True)
                return
            
            self.test("Admin is active", True)
            
        except Exception as e:
            self.test("Database accessible", False, blocking=True)
            self.log('fail', f"  Error: {e}")
            return
        
        # Check for farms
        try:
            farms = Farm.objects.filter(company=admin.company).count()
            self.test(f"Farms exist ({farms} found)", farms > 0, blocking=False)
        except Exception as e:
            self.log('fail', f"  Error checking farms: {e}")
        
        # Check for location nodes
        try:
            nodes = LocationNode.objects.filter(farm__company=admin.company).count()
            self.test(f"LocationNodes exist ({nodes} found)", nodes > 0, blocking=False)
        except Exception as e:
            self.log('fail', f"  Error checking nodes: {e}")
            
    def phase_2_auth(self):
        """Test authentication endpoints"""
        self.log('info', f"Testing login with {TEST_EMAIL}...")
        
        try:
            response = requests.post(
                f"{API_BASE}/auth/login",
                json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            
            if response.status_code == 200:
                self.test("Login endpoint returns 200", True)
                data = response.json()
                
                if "access" in data and "user" in data:
                    self.token = data["access"]
                    self.user = data["user"]
                    self.test("Response contains access token", True)
                    self.test("Response contains user data", True)
                    self.log('info', f"  Authenticated as: {self.user.get('email')}")
                else:
                    self.test("Response has access token", False, blocking=True)
                    self.log('fail', f"  Response: {data}")
            else:
                self.test(f"Login returns 200 (got {response.status_code})", False, blocking=True)
                self.log('fail', f"  Response: {response.text[:200]}")
                
        except requests.exceptions.ConnectionError:
            self.test("Backend server is running", False, blocking=True)
            self.log('fail', "  Cannot connect to http://localhost:8000")
            self.log('info', "  Start server: python manage.py runserver 0.0.0.0:8000")
        except Exception as e:
            self.test("Login request successful", False, blocking=True)
            self.log('fail', f"  Error: {e}")
    
    def phase_3_farms(self):
        """Test farm CRUD and tenant isolation"""
        self.log('info', "Testing farm endpoints...")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            # List farms
            response = requests.get(
                f"{API_BASE}/farm/farms",
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                self.test("Farm list endpoint returns 200", True)
                data = response.json()
                
                # Check if paginated
                if "results" in data:
                    farms = data["results"]
                    count = len(farms)
                else:
                    farms = data if isinstance(data, list) else []
                    count = len(farms)
                
                self.log('info', f"  Found {count} farms")
                
                # Verify tenant isolation
                if farms:
                    farm = farms[0]
                    farm_company = farm.get('company')
                    user_company = self.user.get('company')
                    
                    if farm_company == user_company:
                        self.test("Farm list respects tenant isolation", True)
                    else:
                        self.test("Farm list respects tenant isolation", False, blocking=True)
                        self.log('fail', f"  Farm company: {farm_company}, User company: {user_company}")
                else:
                    self.test("Farm list returns data", False, blocking=False)
                    self.log('warn', "  No farms in database (acceptable for first run)")
                    
            else:
                self.test(f"Farm list returns 200 (got {response.status_code})", False, blocking=True)
                self.log('fail', f"  Response: {response.text[:200]}")
                
        except Exception as e:
            self.test("Farm list request successful", False, blocking=True)
            self.log('fail', f"  Error: {e}")
    
    def phase_4_hierarchy(self):
        """Test hierarchy and location node endpoints"""
        self.log('info', "Testing hierarchy endpoints...")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = requests.get(
                f"{API_BASE}/farm/hierarchy",
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                self.test("Hierarchy endpoint returns 200", True)
                data = response.json()
                
                has_farms = "farms" in data and len(data.get("farms", [])) > 0
                has_nodes = "location_nodes" in data and len(data.get("location_nodes", [])) > 0
                
                self.log('info', f"  Farms in hierarchy: {len(data.get('farms', []))}")
                self.log('info', f"  LocationNodes: {len(data.get('location_nodes', []))}")
                
            else:
                self.test(f"Hierarchy returns 200 (got {response.status_code})", False, blocking=False)
                
        except Exception as e:
            self.test("Hierarchy request successful", False, blocking=False)
            self.log('fail', f"  Error: {e}")
    
    def phase_5_reports(self):
        """Test reports workflow"""
        self.log('info', "Testing reports endpoints...")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            # List reports
            response = requests.get(
                f"{API_BASE}/reports/tasks",
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                self.test("Reports list endpoint returns 200", True)
                data = response.json()
                
                results = data.get("results", data) if isinstance(data, dict) else data
                count = len(results) if isinstance(results, list) else 0
                self.log('info', f"  Found {count} reports")
                
            else:
                self.test(f"Reports returns 200 (got {response.status_code})", False, blocking=True)
                
        except Exception as e:
            self.test("Reports list request successful", False, blocking=True)
            self.log('fail', f"  Error: {e}")
    
    def phase_6_integrity(self):
        """Test data integrity and relationships"""
        self.log('info', "Verifying data relationships...")
        
        try:
            # Check that farms have location nodes
            user_company = Company.objects.get(id=self.user['company'])
            farms = Farm.objects.filter(company=user_company)
            
            if farms.exists():
                farm = farms.first()
                nodes = LocationNode.objects.filter(farm=farm)
                self.test(f"Farm has location nodes ({nodes.count()} found)", nodes.exists(), blocking=False)
            
            # Check that reports reference valid locations
            reports = DailyTaskReport.objects.filter(location__farm__company=user_company)
            if reports.exists():
                self.test("Reports reference valid locations", True, blocking=False)
            else:
                self.test("Reports exist in database", False, blocking=False)
                
        except Exception as e:
            self.log('fail', f"Integrity check error: {e}")
    
    def summary(self, start_time):
        """Print test summary"""
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r['passed'])
        failed = sum(1 for r in self.results if not r['passed'])
        blocking_failed = sum(1 for r in self.results if not r['passed'] and r['blocking'])
        
        self.phase("TEST SUMMARY")
        
        print(f"Total Tests:       {total}")
        print(f"Passed:            {GREEN}{passed}{RESET}")
        print(f"Failed:            {RED}{failed}{RESET}")
        print(f"Blocking Failures: {RED}{blocking_failed}{RESET}")
        print(f"Duration:          {duration:.2f}s")
        
        if blocking_failed > 0:
            print(f"\n{RED}FAILED: VALIDATION FAILED{RESET}")
            print(f"\n{YELLOW}Blocking failures detected. Fix these before proceeding to Step 5.{RESET}")
            return False
        else:
            print(f"\n{GREEN}PASSED: VALIDATION PASSED{RESET}")
            print(f"\n{GREEN}Step 4 workflow is operational. Ready for Step 5 expansion.{RESET}")
            return True


if __name__ == "__main__":
    runner = TestRunner()
    success = runner.run_all()
    sys.exit(0 if success else 1)
