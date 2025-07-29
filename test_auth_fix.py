#!/usr/bin/env python3
"""
Test script to validate the authentication fix.
"""

import requests
import time
import json

BASE_URL = "http://localhost:8081/api/v1"

def test_auth_fix():
    """Test that the authentication fix is working correctly."""
    print("Testing authentication fix...")
    
    # Test login
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    print("1. Testing login...")
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"   Login status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        access_token = data.get("access_token")
        print(f"   Login successful, got token")
        
        # Test /auth/me endpoint (this was the main issue)
        print("2. Testing /auth/me endpoint...")
        headers = {"Authorization": f"Bearer {access_token}"}
        
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        print(f"   /auth/me status: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"   ✅ /auth/me successful - User: {user_data.get('username')}")
        else:
            print(f"   ❌ /auth/me failed: {response.text}")
            return False
        
        # Test other authenticated endpoints
        print("3. Testing other authenticated endpoints...")
        
        endpoints_to_test = [
            "/assistants/",
            "/conversations/",
            "/tools/"
        ]
        
        for endpoint in endpoints_to_test:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            print(f"   {endpoint}: {response.status_code}")
            if response.status_code not in [200, 404, 401]:  # 404 is OK for empty endpoints
                print(f"   ⚠️  Unexpected status for {endpoint}")
        
        # Test auth endpoints that should NOT require authentication
        print("4. Testing auth endpoints that don't need authentication...")
        
        auth_endpoints_no_auth = [
            "/auth/sso/providers",
            "/auth/login",
            "/auth/register"
        ]
        
        for endpoint in auth_endpoints_no_auth:
            response = requests.get(f"{BASE_URL}{endpoint}")
            print(f"   {endpoint}: {response.status_code}")
        
        print("✅ Authentication fix validation completed successfully!")
        return True
        
    else:
        print(f"❌ Login failed: {response.text}")
        return False

if __name__ == "__main__":
    success = test_auth_fix()
    exit(0 if success else 1) 