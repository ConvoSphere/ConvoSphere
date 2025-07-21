#!/usr/bin/env python3
"""
Test script for Users API with enterprise features.

This script tests the comprehensive Users API including:
- User CRUD operations
- User groups management
- SSO user creation
- Bulk operations
- User statistics
- Authentication and security features
"""

import uuid
from typing import Any

import requests


class UsersAPITester:
    """Test class for Users API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        self.users_endpoint = f"{self.api_base}/users"
        self.auth_token = None

    def set_auth_token(self, token: str):
        """Set authentication token for API requests."""
        self.auth_token = token

    def get_headers(self) -> dict[str, str]:
        """Get headers for API requests."""
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers

    def test_create_user(self) -> dict[str, Any]:
        """Test creating a new user."""
        print("\n=== Testing User Creation ===")

        user_data = {
            "email": f"testuser_{uuid.uuid4().hex[:8]}@example.com",
            "username": f"testuser_{uuid.uuid4().hex[:8]}",
            "password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "User",
            "display_name": "Test User",
            "role": "user",
            "status": "active",
            "department": "Engineering",
            "job_title": "Software Engineer",
            "employee_id": "EMP001",
            "language": "de",
            "timezone": "Europe/Berlin",
        }

        try:
            response = requests.post(
                f"{self.users_endpoint}/",
                json=user_data,
                headers=self.get_headers(),
            )

            print(f"Status Code: {response.status_code}")
            if response.status_code == 201:
                user = response.json()
                print(f"✅ User created successfully: {user['email']}")
                return user
            print(f"❌ Failed to create user: {response.text}")
            return {}

        except Exception as e:
            print(f"❌ Error creating user: {e}")
            return {}

    def test_list_users(self) -> dict[str, Any]:
        """Test listing users with filters."""
        print("\n=== Testing User Listing ===")

        try:
            response = requests.get(
                f"{self.users_endpoint}/",
                params={
                    "page": 1,
                    "size": 10,
                    "role": "user",
                },
                headers=self.get_headers(),
            )

            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Users listed successfully: {data['total']} total users")
                print(f"   Page {data['page']} of {data['pages']}")
                return data
            print(f"❌ Failed to list users: {response.text}")
            return {}

        except Exception as e:
            print(f"❌ Error listing users: {e}")
            return {}

    def test_get_user(self, user_id: str) -> dict[str, Any]:
        """Test getting a specific user."""
        print(f"\n=== Testing Get User {user_id} ===")

        try:
            response = requests.get(
                f"{self.users_endpoint}/{user_id}",
                headers=self.get_headers(),
            )

            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                user = response.json()
                print(f"✅ User retrieved successfully: {user['email']}")
                return user
            print(f"❌ Failed to get user: {response.text}")
            return {}

        except Exception as e:
            print(f"❌ Error getting user: {e}")
            return {}

    def test_update_user(self, user_id: str) -> dict[str, Any]:
        """Test updating a user."""
        print(f"\n=== Testing Update User {user_id} ===")

        update_data = {
            "display_name": "Updated Test User",
            "department": "Updated Engineering",
            "job_title": "Senior Software Engineer",
            "bio": "Updated bio for testing",
            "phone": "+49 123 456789",
        }

        try:
            response = requests.put(
                f"{self.users_endpoint}/{user_id}",
                json=update_data,
                headers=self.get_headers(),
            )

            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                user = response.json()
                print(f"✅ User updated successfully: {user['display_name']}")
                return user
            print(f"❌ Failed to update user: {response.text}")
            return {}

        except Exception as e:
            print(f"❌ Error updating user: {e}")
            return {}

    def test_create_group(self) -> dict[str, Any]:
        """Test creating a user group."""
        print("\n=== Testing Group Creation ===")

        group_data = {
            "name": f"Test Group {uuid.uuid4().hex[:8]}",
            "description": "Test group for API testing",
            "permissions": ["assistant:read", "conversation:read"],
            "settings": {"max_assistants": 5, "max_conversations": 100},
        }

        try:
            response = requests.post(
                f"{self.users_endpoint}/groups",
                json=group_data,
                headers=self.get_headers(),
            )

            print(f"Status Code: {response.status_code}")
            if response.status_code == 201:
                group = response.json()
                print(f"✅ Group created successfully: {group['name']}")
                return group
            print(f"❌ Failed to create group: {response.text}")
            return {}

        except Exception as e:
            print(f"❌ Error creating group: {e}")
            return {}

    def test_list_groups(self) -> dict[str, Any]:
        """Test listing user groups."""
        print("\n=== Testing Group Listing ===")

        try:
            response = requests.get(
                f"{self.users_endpoint}/groups",
                headers=self.get_headers(),
            )

            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                groups = response.json()
                print(f"✅ Groups listed successfully: {len(groups)} groups")
                return groups
            print(f"❌ Failed to list groups: {response.text}")
            return []

        except Exception as e:
            print(f"❌ Error listing groups: {e}")
            return []

    def test_assign_users_to_groups(self, user_ids: list, group_ids: list) -> bool:
        """Test assigning users to groups."""
        print("\n=== Testing User-Group Assignment ===")

        assignment_data = {
            "user_ids": user_ids,
            "group_ids": group_ids,
            "operation": "add",
        }

        try:
            response = requests.post(
                f"{self.users_endpoint}/groups/assign",
                json=assignment_data,
                headers=self.get_headers(),
            )

            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Users assigned to groups successfully: {result['message']}")
                return True
            print(f"❌ Failed to assign users to groups: {response.text}")
            return False

        except Exception as e:
            print(f"❌ Error assigning users to groups: {e}")
            return False

    def test_bulk_update_users(self, user_ids: list) -> bool:
        """Test bulk updating users."""
        print("\n=== Testing Bulk User Update ===")

        bulk_data = {
            "user_ids": user_ids,
            "status": "active",
            "department": "Bulk Updated Department",
        }

        try:
            response = requests.post(
                f"{self.users_endpoint}/bulk-update",
                json=bulk_data,
                headers=self.get_headers(),
            )

            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Bulk update successful: {result['message']}")
                return True
            print(f"❌ Failed to bulk update users: {response.text}")
            return False

        except Exception as e:
            print(f"❌ Error bulk updating users: {e}")
            return False

    def test_create_sso_user(self) -> dict[str, Any]:
        """Test creating a user via SSO."""
        print("\n=== Testing SSO User Creation ===")

        sso_data = {
            "email": f"sso_user_{uuid.uuid4().hex[:8]}@example.com",
            "username": f"sso_user_{uuid.uuid4().hex[:8]}",
            "first_name": "SSO",
            "last_name": "User",
            "display_name": "SSO Test User",
            "auth_provider": "oauth_google",
            "external_id": f"google_{uuid.uuid4().hex}",
            "sso_attributes": {
                "sub": f"google_{uuid.uuid4().hex}",
                "email_verified": True,
                "picture": "https://example.com/avatar.jpg",
            },
            "role": "user",
            "status": "active",
        }

        try:
            response = requests.post(
                f"{self.users_endpoint}/sso",
                json=sso_data,
                headers=self.get_headers(),
            )

            print(f"Status Code: {response.status_code}")
            if response.status_code == 201:
                user = response.json()
                print(f"✅ SSO user created successfully: {user['email']}")
                return user
            print(f"❌ Failed to create SSO user: {response.text}")
            return {}

        except Exception as e:
            print(f"❌ Error creating SSO user: {e}")
            return {}

    def test_user_stats(self) -> dict[str, Any]:
        """Test getting user statistics."""
        print("\n=== Testing User Statistics ===")

        try:
            response = requests.get(
                f"{self.users_endpoint}/stats/overview",
                headers=self.get_headers(),
            )

            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                stats = response.json()
                print("✅ User stats retrieved successfully:")
                print(f"   Total users: {stats['total_users']}")
                print(f"   Active users: {stats['active_users']}")
                print(f"   Verified users: {stats['verified_users']}")
                return stats
            print(f"❌ Failed to get user stats: {response.text}")
            return {}

        except Exception as e:
            print(f"❌ Error getting user stats: {e}")
            return {}

    def test_user_search(self, email: str) -> dict[str, Any]:
        """Test searching for a user by email."""
        print("\n=== Testing User Search by Email ===")

        try:
            response = requests.get(
                f"{self.users_endpoint}/search/email/{email}",
                headers=self.get_headers(),
            )

            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                user = response.json()
                print(f"✅ User found by email: {user['email']}")
                return user
            print(f"❌ Failed to find user by email: {response.text}")
            return {}

        except Exception as e:
            print(f"❌ Error searching user by email: {e}")
            return {}

    def test_authenticate_user(self, email: str, password: str) -> bool:
        """Test user authentication."""
        print("\n=== Testing User Authentication ===")

        auth_data = {
            "email": email,
            "password": password,
        }

        try:
            response = requests.post(
                f"{self.users_endpoint}/authenticate",
                json=auth_data,
                headers=self.get_headers(),
            )

            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Authentication successful: {result['message']}")
                return True
            print(f"❌ Authentication failed: {response.text}")
            return False

        except Exception as e:
            print(f"❌ Error during authentication: {e}")
            return False

    def run_all_tests(self):
        """Run all tests for the Users API."""
        print("🚀 Starting Users API Tests")
        print("=" * 50)

        # Test user creation
        user = self.test_create_user()
        if not user:
            print("❌ Cannot continue without a test user")
            return

        user_id = user["id"]

        # Test listing users
        self.test_list_users()

        # Test getting specific user
        self.test_get_user(user_id)

        # Test updating user
        updated_user = self.test_update_user(user_id)

        # Test group creation
        group = self.test_create_group()
        if group:
            group_id = group["id"]

            # Test listing groups
            self.test_list_groups()

            # Test assigning users to groups
            self.test_assign_users_to_groups([user_id], [group_id])

        # Test bulk operations
        self.test_bulk_update_users([user_id])

        # Test SSO user creation
        self.test_create_sso_user()

        # Test user statistics
        self.test_user_stats()

        # Test user search
        if updated_user:
            self.test_user_search(updated_user["email"])

        # Test authentication
        self.test_authenticate_user(user["email"], "SecurePass123!")

        print("\n" + "=" * 50)
        print("✅ Users API Tests Completed")


def main():
    """Main function to run the tests."""
    # Initialize tester
    tester = UsersAPITester()

    # Set authentication token if available
    # tester.set_auth_token("your-auth-token-here")

    # Run all tests
    tester.run_all_tests()


if __name__ == "__main__":
    main()
