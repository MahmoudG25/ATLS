#!/usr/bin/env python
"""
Manual API Testing Script
This script tests the Django API endpoints for authentication and farm list.
Run after starting the Django server: python manage.py runserver 0.0.0.0:8000

Usage:
1. Start Django server in one terminal
2. Run this script in another terminal
3. Review the output for status codes and errors
"""

import requests
import json
import sys
from django.core.management import execute_from_command_line

def test_api():
    BASE_URL = "http://localhost:8000/api"
    LOGIN_URL = f"{BASE_URL}/auth/login/"
    FARMS_URL = f"{BASE_URL}/farm/farms/"
    
    print("=" * 80)
    print("DJANGO API TEST SUITE")
    print("=" * 80)
    
    # Test 1: Login endpoint
    print("\n[TEST 1] Testing Login Endpoint")
    print(f"URL: POST {LOGIN_URL}")
    print("-" * 80)
    
    login_credentials = {
        "email": "admin@example.com",
        "password": "admin"
    }
    
    print(f"Request Body: {json.dumps(login_credentials, indent=2)}")
    
    try:
        login_response = requests.post(
            LOGIN_URL,
            json=login_credentials,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"\nResponse Status Code: {login_response.status_code}")
        print(f"Response Headers: {dict(login_response.headers)}")
        
        try:
            response_data = login_response.json()
            print(f"Response Body:\n{json.dumps(response_data, indent=2)}")
            
            # Extract JWT token if login successful
            if login_response.status_code == 200 and "access" in response_data:
                access_token = response_data["access"]
                print(f"\n✓ Login successful!")
                print(f"Access Token (first 50 chars): {access_token[:50]}...")
                
                # Test 2: Farm list endpoint with JWT token
                print("\n" + "=" * 80)
                print("[TEST 2] Testing Farm List Endpoint")
                print(f"URL: GET {FARMS_URL}")
                print("-" * 80)
                
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
                
                print(f"Request Headers: Authorization: Bearer {access_token[:20]}...")
                
                try:
                    farms_response = requests.get(
                        FARMS_URL,
                        headers=headers,
                        timeout=10
                    )
                    
                    print(f"\nResponse Status Code: {farms_response.status_code}")
                    print(f"Response Headers: {dict(farms_response.headers)}")
                    
                    try:
                        farms_data = farms_response.json()
                        print(f"Response Body:\n{json.dumps(farms_data, indent=2)}")
                        
                        if farms_response.status_code == 200:
                            print(f"\n✓ Farm list endpoint successful!")
                            print(f"Number of farms: {len(farms_data) if isinstance(farms_data, list) else 'N/A'}")
                        else:
                            print(f"\n✗ Farm list endpoint returned status {farms_response.status_code}")
                    except json.JSONDecodeError:
                        print(f"\n✗ Could not decode farm response as JSON")
                        print(f"Raw response: {farms_response.text}")
                        
                except requests.exceptions.RequestException as e:
                    print(f"\n✗ Farm list request failed: {e}")
            else:
                print(f"\n✗ Login failed with status {login_response.status_code}")
                print(f"Error: {response_data.get('detail', 'Unknown error')}")
        except json.JSONDecodeError:
            print(f"\n✗ Could not decode login response as JSON")
            print(f"Raw response: {login_response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"\n✗ Login request failed: {e}")
        print("\n⚠ Make sure Django server is running: python manage.py runserver 0.0.0.0:8000")
    
    print("\n" + "=" * 80)
    print("TEST SUITE COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    test_api()
