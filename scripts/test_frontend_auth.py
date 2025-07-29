#!/usr/bin/env python3
"""
Test script to simulate frontend authentication flow and identify the issue.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8081/api/v1"

def test_frontend_auth_flow():
    """Simulate the exact frontend authentication flow."""
    print("=== Testing Frontend Auth Flow ===")
    
    # Step 1: Login (like frontend does)
    print("1. Login...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"   Login status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   Login failed: {response.text}")
        return
    
    data = response.json()
    access_token = data.get("access_token")
    refresh_token = data.get("refresh_token")
    expires_in = data.get("expires_in", 30 * 60)  # 30 minutes default
    
    print(f"   Got access token: {access_token[:20]}...")
    print(f"   Token expires in: {expires_in} seconds")
    
    # Step 2: Test /auth/me immediately (like frontend does)
    print("\n2. Testing /auth/me immediately...")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"   /auth/me status: {response.status_code}")
    
    if response.status_code == 200:
        user_data = response.json()
        print(f"   User: {user_data.get('username')} ({user_data.get('email')})")
    else:
        print(f"   /auth/me failed: {response.text}")
    
    # Step 3: Test without Authorization header (like the problematic frontend call)
    print("\n3. Testing /auth/me WITHOUT Authorization header...")
    response = requests.get(f"{BASE_URL}/auth/me")
    print(f"   /auth/me status (no auth): {response.status_code}")
    
    if response.status_code != 200:
        print(f"   Expected 403, got: {response.status_code}")
    
    # Step 4: Test with malformed Authorization header
    print("\n4. Testing /auth/me with malformed Authorization header...")
    headers = {"Authorization": "Bearer invalid-token"}
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"   /auth/me status (invalid token): {response.status_code}")
    
    # Step 5: Test with empty Authorization header
    print("\n5. Testing /auth/me with empty Authorization header...")
    headers = {"Authorization": ""}
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"   /auth/me status (empty auth): {response.status_code}")
    
    # Step 6: Test with missing Bearer prefix
    print("\n6. Testing /auth/me with missing Bearer prefix...")
    headers = {"Authorization": access_token}
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"   /auth/me status (no bearer): {response.status_code}")

if __name__ == "__main__":
    test_frontend_auth_flow() 