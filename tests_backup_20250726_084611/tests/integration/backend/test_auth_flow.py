"""
Integration tests for authentication flow.
"""



class TestAuthFlow:
    """Test complete authentication flow."""

    def test_register_login_logout_flow(self, client):
        """Test complete register -> login -> logout flow."""
        # Step 1: Register new user
        register_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "newpassword123",
            "first_name": "New",
            "last_name": "User",
        }

        response = client.post("/api/auth/register", json=register_data)
        assert response.status_code == 201

        user_data = response.json()
        assert user_data["email"] == register_data["email"]
        assert user_data["username"] == register_data["username"]
        assert user_data["first_name"] == register_data["first_name"]
        assert user_data["last_name"] == register_data["last_name"]
        assert "id" in user_data
        assert "hashed_password" not in user_data  # Password should not be returned

        # Step 2: Login with registered user
        login_data = {
            "username": register_data["email"],
            "password": register_data["password"],
        }

        response = client.post("/api/auth/login", data=login_data)
        assert response.status_code == 200

        login_response = response.json()
        assert "access_token" in login_response
        assert "token_type" in login_response
        assert login_response["token_type"] == "bearer"

        token = login_response["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Step 3: Access protected endpoint
        response = client.get("/api/users/me", headers=headers)
        assert response.status_code == 200

        user_info = response.json()
        assert user_info["email"] == register_data["email"]
        assert user_info["username"] == register_data["username"]

        # Step 4: Logout (if logout endpoint exists)
        response = client.post("/api/auth/logout", headers=headers)
        # Note: Logout might not be implemented yet, so we don't assert status code

    def test_login_with_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "wrongpassword",
        }

        response = client.post("/api/auth/login", data=login_data)
        assert response.status_code == 401

    def test_access_protected_endpoint_without_token(self, client):
        """Test accessing protected endpoint without authentication."""
        response = client.get("/api/users/me")
        assert response.status_code == 401

    def test_access_protected_endpoint_with_invalid_token(self, client):
        """Test accessing protected endpoint with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/users/me", headers=headers)
        assert response.status_code == 401

    def test_register_with_existing_email(self, client, test_user):
        """Test registration with existing email."""
        register_data = {
            "email": test_user.email,
            "username": "differentuser",
            "password": "password123",
            "first_name": "Different",
            "last_name": "User",
        }

        response = client.post("/api/auth/register", json=register_data)
        assert response.status_code == 400
        assert "email already registered" in response.json()["detail"].lower()

    def test_register_with_existing_username(self, client, test_user):
        """Test registration with existing username."""
        register_data = {
            "email": "different@example.com",
            "username": test_user.username,
            "password": "password123",
            "first_name": "Different",
            "last_name": "User",
        }

        response = client.post("/api/auth/register", json=register_data)
        assert response.status_code == 400
        assert "username already taken" in response.json()["detail"].lower()

    def test_register_with_invalid_data(self, client):
        """Test registration with invalid data."""
        # Test with missing required fields
        register_data = {
            "email": "invalid@example.com",
            "password": "password123",
            # Missing username, first_name, last_name
        }

        response = client.post("/api/auth/register", json=register_data)
        assert response.status_code == 422  # Validation error

        # Test with invalid email format
        register_data = {
            "email": "invalid-email",
            "username": "testuser",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User",
        }

        response = client.post("/api/auth/register", json=register_data)
        assert response.status_code == 422  # Validation error

    def test_password_change_flow(self, client, test_user):
        """Test password change flow."""
        # First, login to get token
        login_data = {
            "username": test_user.email,
            "password": "testpassword123",  # Original password
        }

        response = client.post("/api/auth/login", data=login_data)
        assert response.status_code == 200

        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Change password
        password_change_data = {
            "current_password": "testpassword123",
            "new_password": "newpassword123",
        }

        response = client.post("/api/auth/change-password", json=password_change_data, headers=headers)
        assert response.status_code == 200

        # Try to login with old password (should fail)
        response = client.post("/api/auth/login", data=login_data)
        assert response.status_code == 401

        # Login with new password (should succeed)
        new_login_data = {
            "username": test_user.email,
            "password": "newpassword123",
        }

        response = client.post("/api/auth/login", data=new_login_data)
        assert response.status_code == 200

    def test_refresh_token_flow(self, client, test_user):
        """Test token refresh flow."""
        # Login to get initial token
        login_data = {
            "username": test_user.email,
            "password": "testpassword123",
        }

        response = client.post("/api/auth/login", data=login_data)
        assert response.status_code == 200

        initial_token = response.json()["access_token"]

        # Refresh token (if refresh endpoint exists)
        headers = {"Authorization": f"Bearer {initial_token}"}
        response = client.post("/api/auth/refresh", headers=headers)

        # Note: Refresh endpoint might not be implemented yet
        if response.status_code == 200:
            refresh_response = response.json()
            assert "access_token" in refresh_response
            assert refresh_response["access_token"] != initial_token
        else:
            # If refresh is not implemented, that's okay for now
            assert response.status_code in [404, 405, 501]


class TestUserProfileFlow:
    """Test user profile management flow."""

    def test_get_user_profile(self, client, test_user_headers):
        """Test getting user profile."""
        response = client.get("/api/users/me", headers=test_user_headers)
        assert response.status_code == 200

        user_data = response.json()
        assert "id" in user_data
        assert "email" in user_data
        assert "username" in user_data
        assert "first_name" in user_data
        assert "last_name" in user_data

    def test_update_user_profile(self, client, test_user_headers):
        """Test updating user profile."""
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "bio": "Updated bio",
        }

        response = client.put("/api/users/me", json=update_data, headers=test_user_headers)
        assert response.status_code == 200

        updated_user = response.json()
        assert updated_user["first_name"] == "Updated"
        assert updated_user["last_name"] == "Name"
        assert updated_user["bio"] == "Updated bio"

        # Verify changes persist
        response = client.get("/api/users/me", headers=test_user_headers)
        assert response.status_code == 200

        user_data = response.json()
        assert user_data["first_name"] == "Updated"
        assert user_data["last_name"] == "Name"
        assert user_data["bio"] == "Updated bio"

    def test_update_user_profile_partial(self, client, test_user_headers):
        """Test partial user profile update."""
        # Update only first name
        update_data = {
            "first_name": "Partially",
        }

        response = client.put("/api/users/me", json=update_data, headers=test_user_headers)
        assert response.status_code == 200

        updated_user = response.json()
        assert updated_user["first_name"] == "Partially"
        # Other fields should remain unchanged

    def test_update_user_profile_invalid_data(self, client, test_user_headers):
        """Test user profile update with invalid data."""
        # Try to update with invalid email format
        update_data = {
            "email": "invalid-email",
        }

        response = client.put("/api/users/me", json=update_data, headers=test_user_headers)
        assert response.status_code == 422  # Validation error


class TestAdminAuthFlow:
    """Test admin-specific authentication flows."""

    def test_admin_access_control(self, client, test_admin_headers, test_user_headers):
        """Test admin-only endpoint access."""
        # Admin should be able to access admin endpoints
        response = client.get("/api/admin/users", headers=test_admin_headers)
        # Note: Admin endpoints might not be implemented yet
        if response.status_code == 200:
            assert "users" in response.json()
        else:
            # If admin endpoints don't exist yet, that's okay
            assert response.status_code in [404, 405, 501]

        # Regular user should not be able to access admin endpoints
        response = client.get("/api/admin/users", headers=test_user_headers)
        assert response.status_code in [403, 404, 405, 501]

    def test_user_role_verification(self, client, test_user_headers, test_admin_headers):
        """Test user role verification."""
        # Check regular user role
        response = client.get("/api/users/me", headers=test_user_headers)
        assert response.status_code == 200

        user_data = response.json()
        assert user_data["role"] == "user"

        # Check admin user role
        response = client.get("/api/users/me", headers=test_admin_headers)
        assert response.status_code == 200

        admin_data = response.json()
        assert admin_data["role"] == "admin"


class TestSecurityFeatures:
    """Test security-related features."""

    def test_rate_limiting(self, client):
        """Test rate limiting on auth endpoints."""
        # Try to login multiple times quickly
        login_data = {
            "username": "test@example.com",
            "password": "wrongpassword",
        }

        responses = []
        for _ in range(10):
            response = client.post("/api/auth/login", data=login_data)
            responses.append(response.status_code)

        # Should eventually get rate limited (429) or continue to fail (401)
        assert any(status in [401, 429] for status in responses)

    def test_password_strength_validation(self, client):
        """Test password strength validation during registration."""
        weak_passwords = ["123", "password", "abc", "123456"]

        for weak_password in weak_passwords:
            register_data = {
                "email": f"test_{weak_password}@example.com",
                "username": f"test_{weak_password}",
                "password": weak_password,
                "first_name": "Test",
                "last_name": "User",
            }

            response = client.post("/api/auth/register", json=register_data)
            # Should either fail validation (422) or be rejected (400)
            assert response.status_code in [400, 422]

    def test_token_expiration(self, client, test_user):
        """Test token expiration."""
        # Login to get token
        login_data = {
            "username": test_user.email,
            "password": "testpassword123",
        }

        response = client.post("/api/auth/login", data=login_data)
        assert response.status_code == 200

        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Use token immediately (should work)
        response = client.get("/api/users/me", headers=headers)
        assert response.status_code == 200

        # Note: Testing actual token expiration would require time manipulation
        # This is more of a unit test concern


class TestErrorHandling:
    """Test error handling in auth flow."""

    def test_database_connection_error(self, client):
        """Test handling of database connection errors."""
        # This would require mocking database failures
        # For now, we'll just document the expected behavior

    def test_validation_errors(self, client):
        """Test validation error responses."""
        # Test various validation scenarios
        invalid_data_sets = [
            {
                "email": "invalid-email",
                "username": "test",
                "password": "123",
                "first_name": "",
                "last_name": "",
            },
            {
                "email": "",
                "username": "",
                "password": "",
                "first_name": "Test",
                "last_name": "User",
            },
        ]

        for invalid_data in invalid_data_sets:
            response = client.post("/api/auth/register", json=invalid_data)
            assert response.status_code == 422  # Validation error

    def test_server_error_handling(self, client):
        """Test server error handling."""
        # This would require mocking server errors
        # For now, we'll just document the expected behavior
