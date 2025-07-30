"""
Comprehensive tests for Users API endpoints.

This module tests all user management endpoints including:
- User CRUD operations
- User profile management
- User groups and permissions
- SSO user creation
- User statistics and admin functions
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.user import User, UserRole, UserStatus, AuthProvider
from backend.app.schemas.user import UserCreate, UserUpdate, UserProfileUpdate, UserPasswordUpdate


class TestUsersEndpoints:
    """Test suite for users API endpoints."""

    # =============================================================================
    # FAST TESTS - Basic functionality
    # =============================================================================

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.users
    def test_create_user_success(self, client: TestClient, test_admin_headers: dict):
        """Fast test for successful user creation by admin."""
        request_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "newpassword123",
            "first_name": "New",
            "last_name": "User",
            "role": "user"
        }
        
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_user.email = "newuser@example.com"
            mock_user.username = "newuser"
            
            mock_service.create_user.return_value = mock_user
            mock_service._user_to_response.return_value = {
                "id": "user-123",
                "email": "newuser@example.com",
                "username": "newuser",
                "first_name": "New",
                "last_name": "User",
                "role": "user",
                "status": "active"
            }
            
            response = client.post(
                "/api/v1/users/",
                json=request_data,
                headers=test_admin_headers
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["email"] == "newuser@example.com"
            assert data["username"] == "newuser"
            mock_service.create_user.assert_called_once()

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.users
    def test_list_users_success(self, client: TestClient, test_admin_headers: dict):
        """Fast test for successful user listing."""
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            mock_users = [
                {
                    "id": "user-1",
                    "email": "user1@example.com",
                    "username": "user1",
                    "role": "user",
                    "status": "active"
                },
                {
                    "id": "user-2",
                    "email": "user2@example.com",
                    "username": "user2",
                    "role": "admin",
                    "status": "active"
                }
            ]
            
            mock_service.get_users.return_value = mock_users
            mock_service.get_total_count.return_value = 2
            
            response = client.get(
                "/api/v1/users/",
                headers=test_admin_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["items"]) == 2
            assert data["total"] == 2

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.users
    def test_get_user_success(self, client: TestClient, test_admin_headers: dict):
        """Fast test for successful user retrieval."""
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            mock_user = {
                "id": "user-123",
                "email": "test@example.com",
                "username": "testuser",
                "role": "user",
                "status": "active"
            }
            
            mock_service.get_user_by_id.return_value = mock_user
            
            response = client.get(
                "/api/v1/users/user-123",
                headers=test_admin_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == "user-123"
            assert data["email"] == "test@example.com"

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.users
    def test_get_my_profile_success(self, client: TestClient, test_user_headers: dict):
        """Fast test for successful profile retrieval."""
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            mock_profile = {
                "id": "user-123",
                "email": "test@example.com",
                "username": "testuser",
                "first_name": "Test",
                "last_name": "User",
                "role": "user",
                "status": "active"
            }
            
            mock_service.get_current_user_profile.return_value = mock_profile
            
            response = client.get(
                "/api/v1/users/me/profile",
                headers=test_user_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["email"] == "test@example.com"
            assert data["username"] == "testuser"

    # =============================================================================
    # COMPREHENSIVE TESTS - Advanced functionality and edge cases
    # =============================================================================

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.users
    def test_create_user_already_exists(self, client: TestClient, test_admin_headers: dict):
        """Comprehensive test for user creation when user already exists."""
        request_data = {
            "email": "existing@example.com",
            "username": "existing",
            "password": "password123",
            "first_name": "Existing",
            "last_name": "User"
        }
        
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.create_user.side_effect = Exception("User already exists")
            
            response = client.post(
                "/api/v1/users/",
                json=request_data,
                headers=test_admin_headers
            )
            
            assert response.status_code == 409

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.users
    def test_create_user_permission_denied(self, client: TestClient, test_user_headers: dict):
        """Comprehensive test for user creation without admin permissions."""
        request_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "newpassword123",
            "first_name": "New",
            "last_name": "User"
        }
        
        response = client.post(
            "/api/v1/users/",
            json=request_data,
            headers=test_user_headers
        )
        
        assert response.status_code == 403

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.users
    def test_list_users_with_filters(self, client: TestClient, test_admin_headers: dict):
        """Comprehensive test for user listing with filters."""
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            mock_users = [
                {
                    "id": "user-1",
                    "email": "admin@example.com",
                    "username": "admin",
                    "role": "admin",
                    "status": "active"
                }
            ]
            
            mock_service.get_users.return_value = mock_users
            mock_service.get_total_count.return_value = 1
            
            response = client.get(
                "/api/v1/users/?role=admin&status=active&search=admin",
                headers=test_admin_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["items"]) == 1
            assert data["items"][0]["role"] == "admin"

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.users
    def test_list_users_invalid_pagination(self, client: TestClient, test_admin_headers: dict):
        """Comprehensive test for user listing with invalid pagination."""
        response = client.get(
            "/api/v1/users/?skip=-1&limit=0",
            headers=test_admin_headers
        )
        
        assert response.status_code == 422

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.users
    def test_get_user_not_found(self, client: TestClient, test_admin_headers: dict):
        """Comprehensive test for user not found."""
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.get_user_by_id.return_value = None
            
            response = client.get(
                "/api/v1/users/nonexistent-user",
                headers=test_admin_headers
            )
            
            assert response.status_code == 404

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.users
    def test_update_user_success(self, client: TestClient, test_admin_headers: dict):
        """Comprehensive test for successful user update."""
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "role": "admin"
        }
        
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            updated_user = {
                "id": "user-123",
                "email": "test@example.com",
                "username": "testuser",
                "first_name": "Updated",
                "last_name": "Name",
                "role": "admin",
                "status": "active"
            }
            
            mock_service.update_user.return_value = updated_user
            
            response = client.put(
                "/api/v1/users/user-123",
                json=update_data,
                headers=test_admin_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["first_name"] == "Updated"
            assert data["role"] == "admin"

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.users
    def test_delete_user_success(self, client: TestClient, test_admin_headers: dict):
        """Comprehensive test for successful user deletion."""
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.delete_user.return_value = True
            
            response = client.delete(
                "/api/v1/users/user-123",
                headers=test_admin_headers
            )
            
            assert response.status_code == 204

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.users
    def test_update_my_profile_success(self, client: TestClient, test_user_headers: dict):
        """Comprehensive test for successful profile update."""
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "bio": "Updated bio"
        }
        
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            updated_profile = {
                "id": "user-123",
                "email": "test@example.com",
                "username": "testuser",
                "first_name": "Updated",
                "last_name": "Name",
                "bio": "Updated bio",
                "role": "user",
                "status": "active"
            }
            
            mock_service.update_current_user_profile.return_value = updated_profile
            
            response = client.put(
                "/api/v1/users/me/profile",
                json=update_data,
                headers=test_user_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["first_name"] == "Updated"
            assert data["bio"] == "Updated bio"

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.users
    def test_update_my_password_success(self, client: TestClient, test_user_headers: dict):
        """Comprehensive test for successful password update."""
        password_data = {
            "current_password": "oldpassword",
            "new_password": "newpassword123"
        }
        
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.update_current_user_password.return_value = True
            
            response = client.put(
                "/api/v1/users/me/password",
                json=password_data,
                headers=test_user_headers
            )
            
            assert response.status_code == 200

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.users
    def test_update_my_password_invalid_current(self, client: TestClient, test_user_headers: dict):
        """Comprehensive test for password update with invalid current password."""
        password_data = {
            "current_password": "wrongpassword",
            "new_password": "newpassword123"
        }
        
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.update_current_user_password.side_effect = Exception("Invalid current password")
            
            response = client.put(
                "/api/v1/users/me/password",
                json=password_data,
                headers=test_user_headers
            )
            
            assert response.status_code == 400

    # =============================================================================
    # GROUP MANAGEMENT TESTS
    # =============================================================================

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.users
    def test_create_group_success(self, client: TestClient, test_admin_headers: dict):
        """Comprehensive test for successful group creation."""
        group_data = {
            "name": "Test Group",
            "description": "A test group",
            "permissions": ["read", "write"]
        }
        
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            created_group = {
                "id": "group-123",
                "name": "Test Group",
                "description": "A test group",
                "permissions": ["read", "write"]
            }
            
            mock_service.create_group.return_value = created_group
            
            response = client.post(
                "/api/v1/users/groups/",
                json=group_data,
                headers=test_admin_headers
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["name"] == "Test Group"

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.users
    def test_list_groups_success(self, client: TestClient, test_admin_headers: dict):
        """Comprehensive test for successful group listing."""
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            mock_groups = [
                {
                    "id": "group-1",
                    "name": "Admin Group",
                    "description": "Administrators",
                    "permissions": ["read", "write", "admin"]
                },
                {
                    "id": "group-2",
                    "name": "User Group",
                    "description": "Regular users",
                    "permissions": ["read"]
                }
            ]
            
            mock_service.get_groups.return_value = mock_groups
            mock_service.get_total_count.return_value = 2
            
            response = client.get(
                "/api/v1/users/groups/",
                headers=test_admin_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["items"]) == 2

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.users
    def test_get_group_success(self, client: TestClient, test_admin_headers: dict):
        """Comprehensive test for successful group retrieval."""
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            mock_group = {
                "id": "group-123",
                "name": "Test Group",
                "description": "A test group",
                "permissions": ["read", "write"]
            }
            
            mock_service.get_group_by_id.return_value = mock_group
            
            response = client.get(
                "/api/v1/users/groups/group-123",
                headers=test_admin_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == "group-123"
            assert data["name"] == "Test Group"

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.users
    def test_update_group_success(self, client: TestClient, test_admin_headers: dict):
        """Comprehensive test for successful group update."""
        update_data = {
            "name": "Updated Group",
            "description": "Updated description",
            "permissions": ["read", "write", "admin"]
        }
        
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            updated_group = {
                "id": "group-123",
                "name": "Updated Group",
                "description": "Updated description",
                "permissions": ["read", "write", "admin"]
            }
            
            mock_service.update_group.return_value = updated_group
            
            response = client.put(
                "/api/v1/users/groups/group-123",
                json=update_data,
                headers=test_admin_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "Updated Group"

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.users
    def test_delete_group_success(self, client: TestClient, test_admin_headers: dict):
        """Comprehensive test for successful group deletion."""
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.delete_group.return_value = True
            
            response = client.delete(
                "/api/v1/users/groups/group-123",
                headers=test_admin_headers
            )
            
            assert response.status_code == 204

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.users
    def test_assign_users_to_groups_success(self, client: TestClient, test_admin_headers: dict):
        """Comprehensive test for successful user-group assignment."""
        assignment_data = {
            "user_ids": ["user-1", "user-2"],
            "group_ids": ["group-1", "group-2"]
        }
        
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.assign_users_to_groups.return_value = True
            
            response = client.post(
                "/api/v1/users/groups/assign",
                json=assignment_data,
                headers=test_admin_headers
            )
            
            assert response.status_code == 200

    # =============================================================================
    # SSO AND AUTHENTICATION TESTS
    # =============================================================================

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.users
    def test_create_sso_user_success(self, client: TestClient):
        """Comprehensive test for successful SSO user creation."""
        sso_data = {
            "email": "sso@example.com",
            "username": "ssouser",
            "first_name": "SSO",
            "last_name": "User",
            "provider": "google",
            "provider_id": "google-123"
        }
        
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            created_user = {
                "id": "user-123",
                "email": "sso@example.com",
                "username": "ssouser",
                "provider": "google",
                "provider_id": "google-123"
            }
            
            mock_service.create_sso_user.return_value = created_user
            
            response = client.post(
                "/api/v1/users/sso/",
                json=sso_data
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["email"] == "sso@example.com"
            assert data["provider"] == "google"

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.users
    def test_authenticate_user_success(self, client: TestClient):
        """Comprehensive test for successful user authentication."""
        auth_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            auth_result = {
                "access_token": "test-token",
                "token_type": "bearer",
                "user": {
                    "id": "user-123",
                    "email": "test@example.com",
                    "username": "testuser"
                }
            }
            
            mock_service.authenticate_user.return_value = auth_result
            
            response = client.post(
                "/api/v1/users/auth/login",
                json=auth_data
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.users
    def test_authenticate_user_invalid_credentials(self, client: TestClient):
        """Comprehensive test for authentication with invalid credentials."""
        auth_data = {
            "email": "test@example.com",
            "password": "wrongpassword"
        }
        
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.authenticate_user.return_value = None
            
            response = client.post(
                "/api/v1/users/auth/login",
                json=auth_data
            )
            
            assert response.status_code == 401

    # =============================================================================
    # ADMIN AND UTILITY TESTS
    # =============================================================================

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.users
    def test_get_user_stats_success(self, client: TestClient, test_admin_headers: dict):
        """Comprehensive test for successful user statistics retrieval."""
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            stats = {
                "total_users": 100,
                "active_users": 85,
                "inactive_users": 15,
                "admin_users": 5,
                "regular_users": 95
            }
            
            mock_service.get_user_statistics.return_value = stats
            
            response = client.get(
                "/api/v1/users/stats",
                headers=test_admin_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["total_users"] == 100
            assert data["active_users"] == 85

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.users
    def test_verify_user_email_success(self, client: TestClient, test_admin_headers: dict):
        """Comprehensive test for successful email verification."""
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.verify_user_email.return_value = True
            
            response = client.post(
                "/api/v1/users/user-123/verify-email",
                headers=test_admin_headers
            )
            
            assert response.status_code == 200

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.users
    def test_get_user_by_email_success(self, client: TestClient, test_admin_headers: dict):
        """Comprehensive test for successful user retrieval by email."""
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            mock_user = {
                "id": "user-123",
                "email": "test@example.com",
                "username": "testuser",
                "role": "user",
                "status": "active"
            }
            
            mock_service.get_user_by_email.return_value = mock_user
            
            response = client.get(
                "/api/v1/users/by-email/test@example.com",
                headers=test_admin_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["email"] == "test@example.com"

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.users
    def test_get_user_by_username_success(self, client: TestClient, test_admin_headers: dict):
        """Comprehensive test for successful user retrieval by username."""
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            mock_user = {
                "id": "user-123",
                "email": "test@example.com",
                "username": "testuser",
                "role": "user",
                "status": "active"
            }
            
            mock_service.get_user_by_username.return_value = mock_user
            
            response = client.get(
                "/api/v1/users/by-username/testuser",
                headers=test_admin_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["username"] == "testuser"

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.users
    def test_get_default_language_success(self, client: TestClient, test_admin_headers: dict):
        """Fast test for successful default language retrieval."""
        response = client.get(
            "/api/v1/users/default-language",
            headers=test_admin_headers
        )
        
        assert response.status_code == 200

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.users
    def test_set_default_language_success(self, client: TestClient, test_admin_headers: dict):
        """Comprehensive test for successful default language setting."""
        language_data = {
            "language": "de"
        }
        
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.set_default_language.return_value = True
            
            response = client.put(
                "/api/v1/users/default-language",
                json=language_data,
                headers=test_admin_headers
            )
            
            assert response.status_code == 200

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.users
    def test_get_system_status_success(self, client: TestClient, test_admin_headers: dict):
        """Fast test for successful system status retrieval."""
        response = client.get(
            "/api/v1/users/system-status",
            headers=test_admin_headers
        )
        
        assert response.status_code == 200