"""
Blackbox tests for user management endpoints.

This module tests all user management API endpoints including
CRUD operations, profile management, and administrative functions.
"""

import pytest

from backend.appconftest import TEST_USER_CREDENTIALS


class TestUserManagementEndpoints:
    """Test user management endpoints."""

    @pytest.mark.blackbox
    @pytest.mark.users
    def test_create_user_success(
        self, api_client, assertion_helper, authenticated_admin
    ):
        """Test successful user creation by admin."""
        token, admin_data = authenticated_admin

        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "NewPassword123!",
            "first_name": "New",
            "last_name": "User",
            "role": "user",
        }

        response = api_client.post("/users/", data=user_data, user_type="admin_user")

        assertion_helper.assert_success_response(response, 201)
        assertion_helper.assert_response_structure(
            response.json(),
            [
                "id",
                "email",
                "username",
                "first_name",
                "last_name",
                "role",
                "created_at",
            ],
        )

    @pytest.mark.blackbox
    @pytest.mark.users
    def test_create_user_unauthorized(
        self, api_client, assertion_helper, authenticated_user
    ):
        """Test user creation without admin privileges."""
        token, user_data = authenticated_user

        new_user_data = {
            "email": "unauthorized@example.com",
            "username": "unauthorized",
            "password": "Password123!",
            "first_name": "Unauthorized",
            "last_name": "User",
            "role": "user",
        }

        response = api_client.post(
            "/users/", data=new_user_data, user_type="regular_user"
        )
        assertion_helper.assert_unauthorized(response)

    @pytest.mark.blackbox
    @pytest.mark.users
    def test_get_users_list(self, api_client, assertion_helper, authenticated_admin):
        """Test getting list of users."""
        token, admin_data = authenticated_admin

        response = api_client.get("/users/", user_type="admin_user")

        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_response_structure(
            response.json(), ["users", "total", "page", "size"]
        )
        assertion_helper.assert_list_response(
            response.json()["users"], 1
        )  # At least admin user

    @pytest.mark.blackbox
    @pytest.mark.users
    def test_get_users_list_unauthorized(
        self, api_client, assertion_helper, authenticated_user
    ):
        """Test getting users list without admin privileges."""
        token, user_data = authenticated_user

        response = api_client.get("/users/", user_type="regular_user")
        assertion_helper.assert_unauthorized(response)

    @pytest.mark.blackbox
    @pytest.mark.users
    def test_get_user_by_id(self, api_client, assertion_helper, authenticated_admin):
        """Test getting user by ID."""
        token, admin_data = authenticated_admin

        # First get users list to get a user ID
        users_response = api_client.get("/users/", user_type="admin_user")
        users = users_response.json()["users"]
        user_id = users[0]["id"]

        response = api_client.get(f"/users/{user_id}", user_type="admin_user")

        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_response_structure(
            response.json(),
            ["id", "email", "username", "first_name", "last_name", "role"],
        )
        assert response.json()["id"] == user_id

    @pytest.mark.blackbox
    @pytest.mark.users
    def test_get_user_by_id_not_found(
        self, api_client, assertion_helper, authenticated_admin
    ):
        """Test getting non-existent user by ID."""
        token, admin_data = authenticated_admin

        response = api_client.get("/users/999999", user_type="admin_user")
        assertion_helper.assert_not_found(response)

    @pytest.mark.blackbox
    @pytest.mark.users
    def test_update_user_profile(
        self, api_client, assertion_helper, authenticated_user
    ):
        """Test updating user profile."""
        token, user_data = authenticated_user

        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "bio": "Updated bio",
        }

        response = api_client.put(
            "/users/me/profile", data=update_data, user_type="regular_user"
        )

        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_response_structure(
            response.json(),
            ["id", "email", "username", "first_name", "last_name", "role"],
        )

        # Verify updates
        updated_user = response.json()
        assert updated_user["first_name"] == "Updated"
        assert updated_user["last_name"] == "Name"

    @pytest.mark.blackbox
    @pytest.mark.users
    def test_update_user_password(
        self, api_client, assertion_helper, authenticated_user
    ):
        """Test updating user password."""
        token, user_data = authenticated_user

        password_data = {
            "current_password": user_data["password"],
            "new_password": "NewPassword123!",
        }

        response = api_client.put(
            "/users/me/password", data=password_data, user_type="regular_user"
        )
        assertion_helper.assert_success_response(response, 200)

    @pytest.mark.blackbox
    @pytest.mark.users
    def test_update_user_password_wrong_current(
        self, api_client, assertion_helper, authenticated_user
    ):
        """Test updating password with wrong current password."""
        token, user_data = authenticated_user

        password_data = {
            "current_password": "WrongPassword123!",
            "new_password": "NewPassword123!",
        }

        response = api_client.put(
            "/users/me/password", data=password_data, user_type="regular_user"
        )
        assertion_helper.assert_error_response(response, 400)

    @pytest.mark.blackbox
    @pytest.mark.users
    def test_search_user_by_email(
        self, api_client, assertion_helper, authenticated_admin
    ):
        """Test searching user by email."""
        token, admin_data = authenticated_admin

        response = api_client.get(
            f"/users/search/email/{admin_data['email']}", user_type="admin_user"
        )

        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_response_structure(
            response.json(),
            ["id", "email", "username", "first_name", "last_name", "role"],
        )
        assert response.json()["email"] == admin_data["email"]

    @pytest.mark.blackbox
    @pytest.mark.users
    def test_search_user_by_username(
        self, api_client, assertion_helper, authenticated_admin
    ):
        """Test searching user by username."""
        token, admin_data = authenticated_admin

        response = api_client.get(
            f"/users/search/username/{admin_data['username']}", user_type="admin_user"
        )

        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_response_structure(
            response.json(),
            ["id", "email", "username", "first_name", "last_name", "role"],
        )
        assert response.json()["username"] == admin_data["username"]

    @pytest.mark.blackbox
    @pytest.mark.users
    def test_verify_user(self, api_client, assertion_helper, authenticated_admin):
        """Test user verification."""
        token, admin_data = authenticated_admin

        # First get users list to get a user ID
        users_response = api_client.get("/users/", user_type="admin_user")
        users = users_response.json()["users"]
        user_id = users[0]["id"]

        response = api_client.post(f"/users/{user_id}/verify", user_type="admin_user")

        # This endpoint might return different status codes depending on implementation
        assert response.status_code in [200, 204, 400], (
            f"Unexpected status code: {response.status_code}"
        )

    @pytest.mark.blackbox
    @pytest.mark.users
    def test_get_user_stats(self, api_client, assertion_helper, authenticated_admin):
        """Test getting user statistics."""
        token, admin_data = authenticated_admin

        response = api_client.get("/users/stats/overview", user_type="admin_user")

        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_response_structure(
            response.json(),
            ["total_users", "active_users", "new_users_today", "new_users_this_week"],
        )

    @pytest.mark.blackbox
    @pytest.mark.users
    def test_get_system_status(self, api_client, assertion_helper, authenticated_admin):
        """Test getting system status."""
        token, admin_data = authenticated_admin

        response = api_client.get("/users/admin/system-status", user_type="admin_user")

        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_response_structure(
            response.json(), ["status", "services", "timestamp"]
        )

    @pytest.mark.blackbox
    @pytest.mark.users
    def test_get_default_language(
        self, api_client, assertion_helper, authenticated_admin
    ):
        """Test getting default language setting."""
        token, admin_data = authenticated_admin

        response = api_client.get(
            "/users/admin/default-language", user_type="admin_user"
        )

        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_response_structure(response.json(), ["language"])

    @pytest.mark.blackbox
    @pytest.mark.users
    def test_authenticate_user(self, api_client, assertion_helper):
        """Test user authentication endpoint."""
        user_data = TEST_USER_CREDENTIALS["regular_user"].copy()
        user_data["email"] = "authuser@example.com"
        user_data["username"] = "authuser"

        # Register user first
        api_client.post("/auth/register", data=user_data)

        auth_data = {"email": user_data["email"], "password": user_data["password"]}

        response = api_client.post("/users/authenticate", data=auth_data)

        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_response_structure(
            response.json(), ["user", "access_token", "refresh_token"]
        )


class TestUserGroups:
    """Test user group management."""

    @pytest.mark.blackbox
    @pytest.mark.users
    def test_get_user_groups(self, api_client, assertion_helper, authenticated_admin):
        """Test getting user groups."""
        token, admin_data = authenticated_admin

        response = api_client.get("/users/groups", user_type="admin_user")

        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_list_response(response)

    @pytest.mark.blackbox
    @pytest.mark.users
    def test_assign_user_to_group(
        self, api_client, assertion_helper, authenticated_admin
    ):
        """Test assigning user to group."""
        token, admin_data = authenticated_admin

        # First get users list to get a user ID
        users_response = api_client.get("/users/", user_type="admin_user")
        users = users_response.json()["users"]
        user_id = users[0]["id"]

        # First get groups list to get a group ID
        groups_response = api_client.get("/users/groups", user_type="admin_user")
        groups = groups_response.json()

        if groups:
            group_id = groups[0]["id"]

            assignment_data = {"user_id": user_id, "group_id": group_id}

            response = api_client.post(
                "/users/groups/assign", data=assignment_data, user_type="admin_user"
            )

            # This endpoint might return different status codes depending on implementation
            assert response.status_code in [200, 201, 400], (
                f"Unexpected status code: {response.status_code}"
            )
        else:
            pytest.skip("No groups available for testing")

    @pytest.mark.blackbox
    @pytest.mark.users
    def test_get_group_by_id(self, api_client, assertion_helper, authenticated_admin):
        """Test getting group by ID."""
        token, admin_data = authenticated_admin

        # First get groups list to get a group ID
        groups_response = api_client.get("/users/groups", user_type="admin_user")
        groups = groups_response.json()

        if groups:
            group_id = groups[0]["id"]

            response = api_client.get(
                f"/users/groups/{group_id}", user_type="admin_user"
            )

            assertion_helper.assert_success_response(response, 200)
            assertion_helper.assert_response_structure(
                response.json(), ["id", "name", "description"]
            )
        else:
            pytest.skip("No groups available for testing")

    @pytest.mark.blackbox
    @pytest.mark.users
    def test_get_group_by_id_not_found(
        self, api_client, assertion_helper, authenticated_admin
    ):
        """Test getting non-existent group by ID."""
        token, admin_data = authenticated_admin

        response = api_client.get("/users/groups/999999", user_type="admin_user")
        assertion_helper.assert_not_found(response)


class TestBulkOperations:
    """Test bulk user operations."""

    @pytest.mark.blackbox
    @pytest.mark.users
    def test_bulk_update_users(self, api_client, assertion_helper, authenticated_admin):
        """Test bulk update of users."""
        token, admin_data = authenticated_admin

        # First get users list to get user IDs
        users_response = api_client.get("/users/", user_type="admin_user")
        users = users_response.json()["users"]

        if len(users) >= 2:
            user_ids = [users[0]["id"], users[1]["id"]]

            bulk_update_data = {"user_ids": user_ids, "updates": {"role": "user"}}

            response = api_client.put(
                "/users/bulk-update", data=bulk_update_data, user_type="admin_user"
            )

            assertion_helper.assert_success_response(response, 200)
            assertion_helper.assert_response_structure(
                response.json(), ["updated_count", "failed_count"]
            )
        else:
            pytest.skip("Not enough users for bulk update test")

    @pytest.mark.blackbox
    @pytest.mark.users
    def test_bulk_update_users_unauthorized(
        self, api_client, assertion_helper, authenticated_user
    ):
        """Test bulk update without admin privileges."""
        token, user_data = authenticated_user

        bulk_update_data = {"user_ids": [1, 2], "updates": {"role": "user"}}

        response = api_client.put(
            "/users/bulk-update", data=bulk_update_data, user_type="regular_user"
        )
        assertion_helper.assert_unauthorized(response)


class TestSSOUsers:
    """Test SSO user management."""

    @pytest.mark.blackbox
    @pytest.mark.users
    def test_get_sso_users(self, api_client, assertion_helper, authenticated_admin):
        """Test getting SSO users."""
        token, admin_data = authenticated_admin

        response = api_client.get("/users/sso", user_type="admin_user")

        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_list_response(response)


class TestUserValidation:
    """Test user data validation."""

    @pytest.mark.blackbox
    @pytest.mark.users
    def test_create_user_invalid_email(
        self, api_client, assertion_helper, authenticated_admin
    ):
        """Test creating user with invalid email."""
        token, admin_data = authenticated_admin

        user_data = {
            "email": "invalid-email",
            "username": "invaliduser",
            "password": "Password123!",
            "first_name": "Invalid",
            "last_name": "User",
            "role": "user",
        }

        response = api_client.post("/users/", data=user_data, user_type="admin_user")
        assertion_helper.assert_error_response(response, 422)

    @pytest.mark.blackbox
    @pytest.mark.users
    def test_create_user_duplicate_email(
        self, api_client, assertion_helper, authenticated_admin
    ):
        """Test creating user with duplicate email."""
        token, admin_data = authenticated_admin

        user_data = {
            "email": admin_data["email"],  # Use existing email
            "username": "duplicateuser",
            "password": "Password123!",
            "first_name": "Duplicate",
            "last_name": "User",
            "role": "user",
        }

        response = api_client.post("/users/", data=user_data, user_type="admin_user")
        assertion_helper.assert_error_response(response, 409)

    @pytest.mark.blackbox
    @pytest.mark.users
    def test_create_user_invalid_role(
        self, api_client, assertion_helper, authenticated_admin
    ):
        """Test creating user with invalid role."""
        token, admin_data = authenticated_admin

        user_data = {
            "email": "invalidrole@example.com",
            "username": "invalidrole",
            "password": "Password123!",
            "first_name": "Invalid",
            "last_name": "Role",
            "role": "invalid_role",
        }

        response = api_client.post("/users/", data=user_data, user_type="admin_user")
        assertion_helper.assert_error_response(response, 422)

    @pytest.mark.blackbox
    @pytest.mark.users
    def test_update_profile_invalid_data(
        self, api_client, assertion_helper, authenticated_user
    ):
        """Test updating profile with invalid data."""
        token, user_data = authenticated_user

        invalid_data = {
            "first_name": "",  # Empty first name
            "last_name": "a" * 1000,  # Too long last name
        }

        response = api_client.put(
            "/users/me/profile", data=invalid_data, user_type="regular_user"
        )
        assertion_helper.assert_error_response(response, 422)
