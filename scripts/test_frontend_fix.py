#!/usr/bin/env python3
"""
Test script to verify frontend fixes and check for refresh loops.
"""

import requests
import time
import json

BASE_URL = "http://localhost:8081/api/v1"

def test_auth_without_loop():
    """Test authentication without causing refresh loops."""
    print("Testing authentication without refresh loops...")
    
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
        refresh_token = data.get("refresh_token")
        print(f"   Login successful, got tokens")
        
        # Test a few authenticated requests without triggering refresh
        print("2. Testing authenticated requests...")
        headers = {"Authorization": f"Bearer {access_token}"}
        
        for i in range(3):
            response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
            print(f"   Request {i+1} /auth/me: {response.status_code}")
            time.sleep(1)  # Small delay between requests
        
        # Test SSO providers endpoint (should not cause loops)
        print("3. Testing SSO providers endpoint...")
        response = requests.get(f"{BASE_URL}/auth/sso/providers")
        print(f"   SSO providers status: {response.status_code}")
        
        # Test one token refresh (should work)
        print("4. Testing single token refresh...")
        refresh_data = {"refresh_token": refresh_token}
        response = requests.post(f"{BASE_URL}/auth/refresh", json=refresh_data)
        print(f"   Refresh status: {response.status_code}")
        
        if response.status_code == 200:
            print("   Token refresh successful")
        else:
            print(f"   Token refresh failed: {response.text}")
            
    else:
        print(f"   Login failed: {response.text}")

def monitor_rate_limits():
    """Monitor rate limiting behavior."""
    print("\nMonitoring rate limiting...")
    
    # Make several requests to test rate limiting
    for i in range(5):
        response = requests.get(f"{BASE_URL}/auth/sso/providers")
        print(f"   Request {i+1} SSO providers: {response.status_code}")
        if response.status_code == 429:
            print(f"   Rate limit hit on request {i+1}")
        time.sleep(0.5)

if __name__ == "__main__":
    test_auth_without_loop()
    monitor_rate_limits()
    print("\nTest completed!") 