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

            if response.status_code == 201:
                return response.json()
            return {}

        except Exception:
            return {}

    def test_list_users(self) -> dict[str, Any]:
        """Test listing users with filters."""

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

            if response.status_code == 200:
                return response.json()
            return {}

        except Exception:
            return {}

    def test_get_user(self, user_id: str) -> dict[str, Any]:
        """Test getting a specific user."""

        try:
            response = requests.get(
                f"{self.users_endpoint}/{user_id}",
                headers=self.get_headers(),
            )

            if response.status_code == 200:
                return response.json()
            return {}

        except Exception:
            return {}

    def test_update_user(self, user_id: str) -> dict[str, Any]:
        """Test updating a user."""

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

            if response.status_code == 200:
                return response.json()
            return {}

        except Exception:
            return {}

    def test_create_group(self) -> dict[str, Any]:
        """Test creating a user group."""

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

            if response.status_code == 201:
                return response.json()
            return {}

        except Exception:
            return {}

    def test_list_groups(self) -> dict[str, Any]:
        """Test listing user groups."""

        try:
            response = requests.get(
                f"{self.users_endpoint}/groups",
                headers=self.get_headers(),
            )

            if response.status_code == 200:
                return response.json()
            return []

        except Exception:
            return []

    def test_assign_users_to_groups(self, user_ids: list, group_ids: list) -> bool:
        """Test assigning users to groups."""

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

            if response.status_code == 200:
                response.json()
                return True
            return False

        except Exception:
            return False

    def test_bulk_update_users(self, user_ids: list) -> bool:
        """Test bulk updating users."""

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

            if response.status_code == 200:
                response.json()
                return True
            return False

        except Exception:
            return False

    def test_create_sso_user(self) -> dict[str, Any]:
        """Test creating a user via SSO."""

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

            if response.status_code == 201:
                return response.json()
            return {}

        except Exception:
            return {}

    def test_user_stats(self) -> dict[str, Any]:
        """Test getting user statistics."""

        try:
            response = requests.get(
                f"{self.users_endpoint}/stats/overview",
                headers=self.get_headers(),
            )

            if response.status_code == 200:
                return response.json()
            return {}

        except Exception:
            return {}

    def test_user_search(self, email: str) -> dict[str, Any]:
        """Test searching for a user by email."""

        try:
            response = requests.get(
                f"{self.users_endpoint}/search/email/{email}",
                headers=self.get_headers(),
            )

            if response.status_code == 200:
                return response.json()
            return {}

        except Exception:
            return {}

    def test_authenticate_user(self, email: str, password: str) -> bool:
        """Test user authentication."""

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

            if response.status_code == 200:
                response.json()
                return True
            return False

        except Exception:
            return False

    def run_all_tests(self):
        """Run all tests for the Users API."""

        # Test user creation
        user = self.test_create_user()
        if not user:
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
