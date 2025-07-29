#!/usr/bin/env python3
"""
Test script to verify authentication fixes.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8081/api/v1"

def test_auth_flow():
    """Test the complete authentication flow."""
    print("Testing authentication flow...")
    
    # Test login - try different credential formats
    login_attempts = [
        {"username": "admin", "password": "admin123"},
        {"email": "admin@convosphere.local", "password": "admin123"},
        {"username": "testuser", "password": "test123"},
        {"email": "test@example.com", "password": "test123"},
        {"username": "demo", "password": "demo123"},
        {"email": "demo@convosphere.com", "password": "demo123"}
    ]
    
    access_token = None
    refresh_token = None
    
    for i, login_data in enumerate(login_attempts):
        print(f"1.{i+1}. Testing login with {list(login_data.keys())[0]}: {list(login_data.values())[0]}...")
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"   Login status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get("access_token")
            refresh_token = data.get("refresh_token")
            print(f"   Login successful, got tokens")
            break
        else:
            print(f"   Login failed: {response.text}")
    
    if access_token and refresh_token:
        # Test token refresh
        print("2. Testing token refresh...")
        refresh_data = {"refresh_token": refresh_token}
        response = requests.post(f"{BASE_URL}/auth/refresh", json=refresh_data)
        print(f"   Refresh status: {response.status_code}")
        
        if response.status_code == 200:
            print("   Token refresh successful")
            
            # Test authenticated endpoint
            print("3. Testing authenticated endpoint...")
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
            print(f"   /auth/me status: {response.status_code}")
            
            if response.status_code == 200:
                print("   Authenticated endpoint successful")
            else:
                print(f"   Error: {response.text}")
        else:
            print(f"   Token refresh failed: {response.text}")
    else:
        print("   No successful login attempts")

def test_rate_limiting():
    """Test rate limiting behavior."""
    print("\nTesting rate limiting...")
    
    # Make multiple requests to test rate limiting
    for i in range(5):
        response = requests.get(f"{BASE_URL}/assistants")
        print(f"   Request {i+1}: {response.status_code}")
        time.sleep(0.1)

if __name__ == "__main__":
    test_auth_flow()
    test_rate_limiting()
    print("\nTest completed!") 