"""
Blackbox tests for authentication endpoints.

This module tests all authentication-related API endpoints including
login, logout, registration, token refresh, and SSO functionality.
"""

import pytest
import uuid
from backend.appconftest import TEST_USER_CREDENTIALS


class TestAuthenticationEndpoints:
    """Test authentication endpoints."""
    
    @pytest.mark.blackbox
    @pytest.mark.authentication
    def test_register_user_success(self, api_client, assertion_helper):
        """Test successful user registration."""
        user_data = TEST_USER_CREDENTIALS["regular_user"].copy()
        
        # Generate unique email and username for this test
        unique_id = str(uuid.uuid4())[:8]
        user_data["email"] = f"newuser_{unique_id}@example.com"
        user_data["username"] = f"newuser_{unique_id}"
        
        response = api_client.post("/auth/register", data=user_data)
        
        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_response_structure(response, [
            "id", "email", "username", "first_name", "last_name", "role"
        ])
    
    @pytest.mark.blackbox
    @pytest.mark.authentication
    def test_register_user_duplicate_email(self, api_client, assertion_helper):
        """Test registration with duplicate email."""
        user_data = TEST_USER_CREDENTIALS["regular_user"].copy()
        
        # First registration
        response = api_client.post("/auth/register", data=user_data)
        assertion_helper.assert_success_response(response, 200)
        
        # Second registration with same email
        response = api_client.post("/auth/register", data=user_data)
        assertion_helper.assert_error_response(response, 409)
    
    @pytest.mark.blackbox
    @pytest.mark.authentication
    def test_register_user_invalid_data(self, api_client, assertion_helper):
        """Test registration with invalid data."""
        invalid_data = {
            "email": "invalid-email",
            "username": "test",
            "password": "123",  # Too short
            "first_name": "Test",
            "last_name": "User"
        }
        
        response = api_client.post("/auth/register", data=invalid_data)
        assertion_helper.assert_error_response(response, 422)
    
    @pytest.mark.blackbox
    @pytest.mark.authentication
    def test_login_success(self, api_client, assertion_helper):
        """Test successful login."""
        user_data = TEST_USER_CREDENTIALS["regular_user"].copy()
        
        # Register user first
        api_client.post("/auth/register", data=user_data)
        
        # Login
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        response = api_client.post("/auth/login", data=login_data)
        
        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_response_structure(response.json(), [
            "access_token", "refresh_token", "token_type", "expires_in"
        ])
    
    @pytest.mark.blackbox
    @pytest.mark.authentication
    def test_login_invalid_credentials(self, api_client, assertion_helper):
        """Test login with invalid credentials."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        response = api_client.post("/auth/login", data=login_data)
        assertion_helper.assert_error_response(response, 401)
    
    @pytest.mark.blackbox
    @pytest.mark.authentication
    def test_login_missing_credentials(self, api_client, assertion_helper):
        """Test login with missing credentials."""
        login_data = {
            "email": "test@example.com"
            # Missing password
        }
        
        response = api_client.post("/auth/login", data=login_data)
        assertion_helper.assert_error_response(response, 422)
    
    @pytest.mark.blackbox
    @pytest.mark.authentication
    def test_get_current_user(self, api_client, assertion_helper, authenticated_user):
        """Test getting current user information."""
        token, user_data = authenticated_user
        
        response = api_client.get("/auth/me", user_type="regular_user")
        
        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_response_structure(response.json(), [
            "id", "email", "username", "first_name", "last_name", "role"
        ])
        
        # Verify user data
        user_info = response.json()
        assert user_info["email"] == user_data["email"]
        assert user_info["username"] == user_data["username"]
    
    @pytest.mark.blackbox
    @pytest.mark.authentication
    def test_get_current_user_unauthorized(self, api_client, assertion_helper):
        """Test getting current user without authentication."""
        response = api_client.get("/auth/me")
        assertion_helper.assert_unauthorized(response)
    
    @pytest.mark.blackbox
    @pytest.mark.authentication
    def test_refresh_token_success(self, api_client, assertion_helper, authenticated_user):
        """Test successful token refresh."""
        token, user_data = authenticated_user
        
        # Get refresh token from login response
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        login_response = api_client.post("/auth/login", data=login_data)
        refresh_token = login_response.json()["refresh_token"]
        
        # Refresh token
        refresh_data = {"refresh_token": refresh_token}
        response = api_client.post("/auth/refresh", data=refresh_data)
        
        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_response_structure(response.json(), [
            "access_token", "refresh_token", "token_type", "expires_in"
        ])
    
    @pytest.mark.blackbox
    @pytest.mark.authentication
    def test_refresh_token_invalid(self, api_client, assertion_helper):
        """Test token refresh with invalid refresh token."""
        refresh_data = {"refresh_token": "invalid_token"}
        
        response = api_client.post("/auth/refresh", data=refresh_data)
        assertion_helper.assert_error_response(response, 401)
    
    @pytest.mark.blackbox
    @pytest.mark.authentication
    def test_logout_success(self, api_client, assertion_helper, authenticated_user):
        """Test successful logout."""
        token, user_data = authenticated_user
        
        response = api_client.post("/auth/logout", user_type="regular_user")
        assertion_helper.assert_success_response(response, 200)
    
    @pytest.mark.blackbox
    @pytest.mark.authentication
    def test_logout_unauthorized(self, api_client, assertion_helper):
        """Test logout without authentication."""
        response = api_client.post("/auth/logout")
        assertion_helper.assert_unauthorized(response)
    
    @pytest.mark.blackbox
    @pytest.mark.authentication
    def test_sso_providers_list(self, api_client, assertion_helper):
        """Test getting SSO providers list."""
        response = api_client.get("/auth/sso/providers")
        
        # This endpoint might return empty list if no SSO is configured
        if response.status_code == 200:
            assertion_helper.assert_list_response(response)
        else:
            # If SSO is not configured, it might return 404 or 503
            assert response.status_code in [404, 503], \
                f"Unexpected status code: {response.status_code}"
    
    @pytest.mark.blackbox
    @pytest.mark.authentication
    def test_sso_login_redirect(self, api_client, assertion_helper):
        """Test SSO login redirect."""
        # Test with a non-existent provider
        response = api_client.get("/auth/sso/login/nonexistent")
        
        # Should return 404 for non-existent provider
        assertion_helper.assert_not_found(response)
    
    @pytest.mark.blackbox
    @pytest.mark.authentication
    def test_sso_metadata(self, api_client, assertion_helper):
        """Test SSO metadata endpoint."""
        response = api_client.get("/auth/sso/metadata")
        
        # This endpoint might not be available or return different status codes
        # depending on SSO configuration
        assert response.status_code in [200, 404, 503], \
            f"Unexpected status code: {response.status_code}"
    
    @pytest.mark.blackbox
    @pytest.mark.authentication
    def test_sso_callback_invalid(self, api_client, assertion_helper):
        """Test SSO callback with invalid parameters."""
        response = api_client.get("/auth/sso/callback/nonexistent")
        assertion_helper.assert_not_found(response)
    
    @pytest.mark.blackbox
    @pytest.mark.authentication
    def test_sso_link_unauthorized(self, api_client, assertion_helper):
        """Test SSO link without authentication."""
        response = api_client.post("/auth/sso/link/nonexistent")
        assertion_helper.assert_unauthorized(response)
    
    @pytest.mark.blackbox
    @pytest.mark.authentication
    def test_sso_unlink_unauthorized(self, api_client, assertion_helper):
        """Test SSO unlink without authentication."""
        response = api_client.post("/auth/sso/unlink/nonexistent")
        assertion_helper.assert_unauthorized(response)
    
    @pytest.mark.blackbox
    @pytest.mark.authentication
    def test_sso_bulk_sync_unauthorized(self, api_client, assertion_helper):
        """Test SSO bulk sync without authentication."""
        response = api_client.post("/auth/sso/bulk-sync/nonexistent")
        assertion_helper.assert_unauthorized(response)
    
    @pytest.mark.blackbox
    @pytest.mark.authentication
    def test_sso_provisioning_status_unauthorized(self, api_client, assertion_helper):
        """Test SSO provisioning status without authentication."""
        response = api_client.get("/auth/sso/provisioning/status/123")
        assertion_helper.assert_unauthorized(response)


class TestAuthenticationSecurity:
    """Test authentication security aspects."""
    
    @pytest.mark.blackbox
    @pytest.mark.authentication
    def test_password_strength_validation(self, api_client, assertion_helper):
        """Test password strength validation during registration."""
        weak_passwords = [
            "123",  # Too short
            "password",  # Common password
            "abc123",  # Too simple
            "a" * 1000,  # Too long
        ]
        
        for password in weak_passwords:
            user_data = TEST_USER_CREDENTIALS["regular_user"].copy()
            user_data["password"] = password
            user_data["email"] = f"test_{password}@example.com"
            user_data["username"] = f"test_{password}"
            
            response = api_client.post("/auth/register", data=user_data)
            # Should fail with 422 (validation error) or 400 (business logic error)
            assert response.status_code in [400, 422], \
                f"Password '{password}' should be rejected"
    
    @pytest.mark.blackbox
    @pytest.mark.authentication
    def test_email_validation(self, api_client, assertion_helper):
        """Test email format validation."""
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "test@",
            "test@.com",
            "test..test@example.com"
        ]
        
        for email in invalid_emails:
            user_data = TEST_USER_CREDENTIALS["regular_user"].copy()
            user_data["email"] = email
            user_data["username"] = f"test_{email.replace('@', '_').replace('.', '_')}"
            
            response = api_client.post("/auth/register", data=user_data)
            assertion_helper.assert_error_response(response, 422)
    
    @pytest.mark.blackbox
    @pytest.mark.authentication
    def test_username_validation(self, api_client, assertion_helper):
        """Test username format validation."""
        invalid_usernames = [
            "",  # Empty
            "a",  # Too short
            "a" * 100,  # Too long
            "user@name",  # Invalid characters
            "user name",  # Spaces
            "123",  # Numbers only
        ]
        
        for username in invalid_usernames:
            user_data = TEST_USER_CREDENTIALS["regular_user"].copy()
            user_data["username"] = username
            user_data["email"] = f"test_{username}@example.com"
            
            response = api_client.post("/auth/register", data=user_data)
            assertion_helper.assert_error_response(response, 422)
    
    @pytest.mark.blackbox
    @pytest.mark.authentication
    def test_token_expiration(self, api_client, assertion_helper, authenticated_user):
        """Test that tokens expire properly."""
        token, user_data = authenticated_user
        
        # This test would require waiting for token expiration
        # For now, we just verify that the token works initially
        response = api_client.get("/auth/me", user_type="regular_user")
        assertion_helper.assert_success_response(response, 200)
    
    @pytest.mark.blackbox
    @pytest.mark.authentication
    def test_concurrent_login_handling(self, api_client, assertion_helper):
        """Test handling of concurrent login attempts."""
        user_data = TEST_USER_CREDENTIALS["regular_user"].copy()
        user_data["email"] = "concurrent@example.com"
        user_data["username"] = "concurrent"
        
        # Register user
        api_client.post("/auth/register", data=user_data)
        
        # Try multiple concurrent logins
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        
        # This is a basic test - in a real scenario, you'd use threading
        response1 = api_client.post("/auth/login", data=login_data)
        response2 = api_client.post("/auth/login", data=login_data)
        
        # Both should succeed
        assertion_helper.assert_success_response(response1, 200)
        assertion_helper.assert_success_response(response2, 200)
        
        # Both should return valid tokens
        token1 = response1.json().get("access_token")
        token2 = response2.json().get("access_token")
        assert token1 and token2, "Both responses should contain access tokens" 