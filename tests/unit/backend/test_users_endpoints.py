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

    @pytest.mark.unit
    @pytest.mark.api
    def test_create_user_success(self, client: TestClient, test_admin_headers: dict):
        """Test successful user creation by admin."""
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

    @pytest.mark.unit
    @pytest.mark.api
    def test_create_user_already_exists(self, client: TestClient, test_admin_headers: dict):
        """Test user creation when user already exists."""
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

    @pytest.mark.unit
    @pytest.mark.api
    def test_create_user_permission_denied(self, client: TestClient, test_user_headers: dict):
        """Test user creation without admin permissions."""
        request_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "password123",
            "first_name": "New",
            "last_name": "User"
        }
        
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.create_user.side_effect = Exception("Permission denied")
            
            response = client.post(
                "/api/v1/users/",
                json=request_data,
                headers=test_user_headers
            )
            
            assert response.status_code == 403

    @pytest.mark.unit
    @pytest.mark.api
    def test_list_users_success(self, client: TestClient, test_admin_headers: dict):
        """Test successful user listing."""
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            mock_service.list_users.return_value = {
                "users": [
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
                ],
                "total": 2,
                "page": 1,
                "size": 20
            }
            
            response = client.get(
                "/api/v1/users/?page=1&size=20",
                headers=test_admin_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["users"]) == 2
            assert data["total"] == 2

    @pytest.mark.unit
    @pytest.mark.api
    def test_list_users_with_filters(self, client: TestClient, test_admin_headers: dict):
        """Test user listing with various filters."""
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            mock_service.list_users.return_value = {
                "users": [],
                "total": 0,
                "page": 1,
                "size": 20
            }
            
            # Test with role filter
            response = client.get(
                "/api/v1/users/?role=admin",
                headers=test_admin_headers
            )
            assert response.status_code == 200
            
            # Test with status filter
            response = client.get(
                "/api/v1/users/?status=active",
                headers=test_admin_headers
            )
            assert response.status_code == 200
            
            # Test with auth provider filter
            response = client.get(
                "/api/v1/users/?auth_provider=local",
                headers=test_admin_headers
            )
            assert response.status_code == 200

    @pytest.mark.unit
    @pytest.mark.api
    def test_list_users_invalid_pagination(self, client: TestClient, test_admin_headers: dict):
        """Test user listing with invalid pagination parameters."""
        # Test invalid page number
        response = client.get(
            "/api/v1/users/?page=0",
            headers=test_admin_headers
        )
        assert response.status_code == 422
        
        # Test invalid size
        response = client.get(
            "/api/v1/users/?size=0",
            headers=test_admin_headers
        )
        assert response.status_code == 422
        
        # Test size too large
        response = client.get(
            "/api/v1/users/?size=101",
            headers=test_admin_headers
        )
        assert response.status_code == 422

    @pytest.mark.unit
    @pytest.mark.api
    def test_get_user_success(self, client: TestClient, test_admin_headers: dict):
        """Test successful user retrieval."""
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            mock_service.get_user_by_id.return_value = {
                "id": "user-123",
                "email": "test@example.com",
                "username": "testuser",
                "first_name": "Test",
                "last_name": "User",
                "role": "user",
                "status": "active"
            }
            
            response = client.get(
                "/api/v1/users/user-123",
                headers=test_admin_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == "user-123"
            assert data["email"] == "test@example.com"

    @pytest.mark.unit
    @pytest.mark.api
    def test_get_user_not_found(self, client: TestClient, test_admin_headers: dict):
        """Test user retrieval for non-existent user."""
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.get_user_by_id.side_effect = Exception("User not found")
            
            response = client.get(
                "/api/v1/users/nonexistent",
                headers=test_admin_headers
            )
            
            assert response.status_code == 404

    @pytest.mark.unit
    @pytest.mark.api
    def test_update_user_success(self, client: TestClient, test_admin_headers: dict):
        """Test successful user update."""
        request_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "role": "admin"
        }
        
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            mock_service.update_user.return_value = {
                "id": "user-123",
                "email": "test@example.com",
                "first_name": "Updated",
                "last_name": "Name",
                "role": "admin"
            }
            
            response = client.put(
                "/api/v1/users/user-123",
                json=request_data,
                headers=test_admin_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["first_name"] == "Updated"
            assert data["last_name"] == "Name"
            assert data["role"] == "admin"

    @pytest.mark.unit
    @pytest.mark.api
    def test_delete_user_success(self, client: TestClient, test_admin_headers: dict):
        """Test successful user deletion."""
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.delete_user.return_value = True
            
            response = client.delete(
                "/api/v1/users/user-123",
                headers=test_admin_headers
            )
            
            assert response.status_code == 204
            mock_service.delete_user.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.api
    def test_get_my_profile_success(self, client: TestClient, test_user_headers: dict):
        """Test successful profile retrieval."""
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            mock_service.get_user_by_id.return_value = {
                "id": "user-123",
                "email": "test@example.com",
                "username": "testuser",
                "first_name": "Test",
                "last_name": "User",
                "role": "user",
                "status": "active"
            }
            
            response = client.get(
                "/api/v1/users/me/profile",
                headers=test_user_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["email"] == "test@example.com"

    @pytest.mark.unit
    @pytest.mark.api
    def test_update_my_profile_success(self, client: TestClient, test_user_headers: dict):
        """Test successful profile update."""
        request_data = {
            "first_name": "Updated",
            "last_name": "Name"
        }
        
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            mock_service.update_user.return_value = {
                "id": "user-123",
                "email": "test@example.com",
                "first_name": "Updated",
                "last_name": "Name"
            }
            
            response = client.put(
                "/api/v1/users/me/profile",
                json=request_data,
                headers=test_user_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["first_name"] == "Updated"
            assert data["last_name"] == "Name"

    @pytest.mark.unit
    @pytest.mark.api
    def test_update_my_password_success(self, client: TestClient, test_user_headers: dict):
        """Test successful password update."""
        request_data = {
            "current_password": "oldpassword",
            "new_password": "newpassword123"
        }
        
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.update_password.return_value = True
            
            response = client.put(
                "/api/v1/users/me/password",
                json=request_data,
                headers=test_user_headers
            )
            
            assert response.status_code == 200
            mock_service.update_password.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.api
    def test_update_my_password_invalid_current(self, client: TestClient, test_user_headers: dict):
        """Test password update with invalid current password."""
        request_data = {
            "current_password": "wrongpassword",
            "new_password": "newpassword123"
        }
        
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.update_password.side_effect = Exception("Invalid current password")
            
            response = client.put(
                "/api/v1/users/me/password",
                json=request_data,
                headers=test_user_headers
            )
            
            assert response.status_code == 400

    @pytest.mark.unit
    @pytest.mark.api
    def test_bulk_update_users_success(self, client: TestClient, test_admin_headers: dict):
        """Test successful bulk user update."""
        request_data = {
            "user_ids": ["user-1", "user-2"],
            "updates": {
                "role": "admin",
                "status": "active"
            }
        }
        
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.bulk_update_users.return_value = {
                "updated": 2,
                "failed": 0
            }
            
            response = client.post(
                "/api/v1/users/bulk-update",
                json=request_data,
                headers=test_admin_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["updated"] == 2
            assert data["failed"] == 0

    @pytest.mark.unit
    @pytest.mark.api
    def test_create_group_success(self, client: TestClient, test_admin_headers: dict):
        """Test successful group creation."""
        request_data = {
            "name": "Test Group",
            "description": "A test group",
            "organization_id": "org-123"
        }
        
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            mock_service.create_group.return_value = {
                "id": "group-123",
                "name": "Test Group",
                "description": "A test group",
                "organization_id": "org-123"
            }
            
            response = client.post(
                "/api/v1/users/groups",
                json=request_data,
                headers=test_admin_headers
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["name"] == "Test Group"
            assert data["id"] == "group-123"

    @pytest.mark.unit
    @pytest.mark.api
    def test_list_groups_success(self, client: TestClient, test_admin_headers: dict):
        """Test successful group listing."""
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            mock_service.list_groups.return_value = [
                {
                    "id": "group-1",
                    "name": "Group 1",
                    "description": "First group"
                },
                {
                    "id": "group-2",
                    "name": "Group 2",
                    "description": "Second group"
                }
            ]
            
            response = client.get(
                "/api/v1/users/groups",
                headers=test_admin_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2

    @pytest.mark.unit
    @pytest.mark.api
    def test_get_group_success(self, client: TestClient, test_admin_headers: dict):
        """Test successful group retrieval."""
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            mock_service.get_group_by_id.return_value = {
                "id": "group-123",
                "name": "Test Group",
                "description": "A test group",
                "organization_id": "org-123"
            }
            
            response = client.get(
                "/api/v1/users/groups/group-123",
                headers=test_admin_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == "group-123"
            assert data["name"] == "Test Group"

    @pytest.mark.unit
    @pytest.mark.api
    def test_update_group_success(self, client: TestClient, test_admin_headers: dict):
        """Test successful group update."""
        request_data = {
            "name": "Updated Group",
            "description": "Updated description"
        }
        
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            mock_service.update_group.return_value = {
                "id": "group-123",
                "name": "Updated Group",
                "description": "Updated description"
            }
            
            response = client.put(
                "/api/v1/users/groups/group-123",
                json=request_data,
                headers=test_admin_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "Updated Group"

    @pytest.mark.unit
    @pytest.mark.api
    def test_delete_group_success(self, client: TestClient, test_admin_headers: dict):
        """Test successful group deletion."""
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.delete_group.return_value = True
            
            response = client.delete(
                "/api/v1/users/groups/group-123",
                headers=test_admin_headers
            )
            
            assert response.status_code == 204
            mock_service.delete_group.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.api
    def test_assign_users_to_groups_success(self, client: TestClient, test_admin_headers: dict):
        """Test successful user-group assignment."""
        request_data = {
            "user_ids": ["user-1", "user-2"],
            "group_ids": ["group-1", "group-2"]
        }
        
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.assign_users_to_groups.return_value = {
                "assigned": 4,
                "failed": 0
            }
            
            response = client.post(
                "/api/v1/users/groups/assign",
                json=request_data,
                headers=test_admin_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["assigned"] == 4
            assert data["failed"] == 0

    @pytest.mark.unit
    @pytest.mark.api
    def test_create_sso_user_success(self, client: TestClient):
        """Test successful SSO user creation."""
        request_data = {
            "email": "sso@example.com",
            "username": "ssouser",
            "first_name": "SSO",
            "last_name": "User",
            "provider": "google",
            "provider_user_id": "google-123"
        }
        
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            mock_service.create_sso_user.return_value = {
                "id": "user-123",
                "email": "sso@example.com",
                "username": "ssouser",
                "auth_provider": "google"
            }
            
            response = client.post(
                "/api/v1/users/sso",
                json=request_data
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["email"] == "sso@example.com"
            assert data["auth_provider"] == "google"

    @pytest.mark.unit
    @pytest.mark.api
    def test_get_user_stats_success(self, client: TestClient, test_admin_headers: dict):
        """Test successful user statistics retrieval."""
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            mock_service.get_user_stats.return_value = {
                "total_users": 100,
                "active_users": 85,
                "inactive_users": 15,
                "verified_users": 90,
                "unverified_users": 10,
                "admin_users": 5,
                "regular_users": 95
            }
            
            response = client.get(
                "/api/v1/users/stats/overview",
                headers=test_admin_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["total_users"] == 100
            assert data["active_users"] == 85

    @pytest.mark.unit
    @pytest.mark.api
    def test_verify_user_email_success(self, client: TestClient, test_admin_headers: dict):
        """Test successful user email verification."""
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.verify_email.return_value = True
            
            response = client.post(
                "/api/v1/users/user-123/verify",
                headers=test_admin_headers
            )
            
            assert response.status_code == 200
            mock_service.verify_email.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.api
    def test_get_user_by_email_success(self, client: TestClient, test_admin_headers: dict):
        """Test successful user retrieval by email."""
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            mock_service.get_user_by_email.return_value = {
                "id": "user-123",
                "email": "test@example.com",
                "username": "testuser",
                "first_name": "Test",
                "last_name": "User"
            }
            
            response = client.get(
                "/api/v1/users/search/email/test@example.com",
                headers=test_admin_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["email"] == "test@example.com"

    @pytest.mark.unit
    @pytest.mark.api
    def test_get_user_by_username_success(self, client: TestClient, test_admin_headers: dict):
        """Test successful user retrieval by username."""
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            mock_service.get_user_by_username.return_value = {
                "id": "user-123",
                "email": "test@example.com",
                "username": "testuser",
                "first_name": "Test",
                "last_name": "User"
            }
            
            response = client.get(
                "/api/v1/users/search/username/testuser",
                headers=test_admin_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["username"] == "testuser"

    @pytest.mark.unit
    @pytest.mark.api
    def test_authenticate_user_success(self, client: TestClient):
        """Test successful user authentication."""
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            mock_service.authenticate_user.return_value = {
                "id": "user-123",
                "email": "test@example.com",
                "username": "testuser",
                "access_token": "token-123"
            }
            
            response = client.post(
                "/api/v1/users/authenticate",
                params={"email": "test@example.com", "password": "password123"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["email"] == "test@example.com"
            assert "access_token" in data

    @pytest.mark.unit
    @pytest.mark.api
    def test_authenticate_user_invalid_credentials(self, client: TestClient):
        """Test user authentication with invalid credentials."""
        with patch('backend.app.api.v1.endpoints.users.UserService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.authenticate_user.side_effect = Exception("Invalid credentials")
            
            response = client.post(
                "/api/v1/users/authenticate",
                params={"email": "wrong@example.com", "password": "wrongpass"}
            )
            
            assert response.status_code == 400

    @pytest.mark.unit
    @pytest.mark.api
    def test_get_default_language_success(self, client: TestClient, test_admin_headers: dict):
        """Test successful default language retrieval."""
        with patch('backend.app.api.v1.endpoints.users.get_settings') as mock_settings:
            mock_settings.return_value.default_language = "en"
            
            response = client.get(
                "/api/v1/users/admin/default-language",
                headers=test_admin_headers
            )
            
            assert response.status_code == 200
            assert response.json() == "en"

    @pytest.mark.unit
    @pytest.mark.api
    def test_set_default_language_success(self, client: TestClient, test_admin_headers: dict):
        """Test successful default language setting."""
        with patch('backend.app.api.v1.endpoints.users.get_settings') as mock_settings:
            mock_settings.return_value.default_language = "de"
            
            response = client.put(
                "/api/v1/users/admin/default-language",
                json="de",
                headers=test_admin_headers
            )
            
            assert response.status_code == 200
            assert response.json() == "de"

    @pytest.mark.unit
    @pytest.mark.api
    def test_get_system_status_success(self, client: TestClient, test_admin_headers: dict):
        """Test successful system status retrieval."""
        with patch('backend.app.api.v1.endpoints.users.check_db_connection') as mock_db:
            with patch('backend.app.api.v1.endpoints.users.check_redis_connection') as mock_redis:
                with patch('backend.app.api.v1.endpoints.users.check_weaviate_connection') as mock_weaviate:
                    mock_db.return_value = True
                    mock_redis.return_value = True
                    mock_weaviate.return_value = True
                    
                    response = client.get(
                        "/api/v1/users/admin/system-status",
                        headers=test_admin_headers
                    )
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert "database" in data
                    assert "redis" in data
                    assert "weaviate" in data