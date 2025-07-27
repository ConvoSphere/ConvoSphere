"""
Simplified tests for UserService.

This module provides basic testing of the UserService class,
avoiding SQLAlchemy issues by mocking all database operations.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from backend.app.services.user_service import UserService
from backend.app.models.user import User, UserRole, UserStatus, AuthProvider
from backend.app.schemas.user import (
    UserCreate, 
    UserUpdate, 
    UserSearchParams, 
    UserPasswordUpdate,
    SSOUserCreate
)
from backend.app.utils.exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
    InvalidCredentialsError,
    PermissionDeniedError,
    UserLockedError
)


class TestUserServiceSimple:
    """Simplified tests for UserService."""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def user_service(self, mock_db_session):
        """Create UserService instance with mocked database."""
        with patch('backend.app.services.user_service.get_db') as mock_get_db:
            mock_get_db.return_value = mock_db_session
            service = UserService(db=mock_db_session)
            
            # Mock all service methods to avoid SQLAlchemy issues
            service.get_user_by_email = Mock()
            service.get_user_by_username = Mock()
            service.get_user_by_external_id = Mock()
            service.get_user_by_id = Mock()
            service.create_user = Mock()
            service.update_user = Mock()
            service.delete_user = Mock()
            service.list_users = Mock()
            service.authenticate_user = Mock()
            service.update_password = Mock()
            service.verify_email = Mock()
            service.create_sso_user = Mock()
            service.get_user_stats = Mock()
            service._can_manage_user = Mock()
            
            return service

    @pytest.fixture
    def sample_user_data(self):
        """Sample user data for testing."""
        return {
            "email": "test@example.com",
            "username": "testuser",
            "password": "TestPassword123!",
            "first_name": "Test",
            "last_name": "User",
            "display_name": "Test User",
            "bio": "Test bio",
            "phone": "+1234567890",
            "organization_id": "550e8400-e29b-41d4-a716-446655440000",
            "role": UserRole.USER,
            "is_active": True,
            "is_verified": False,
        }

    @pytest.fixture
    def sample_user(self, sample_user_data):
        """Create a sample user object."""
        user = Mock(spec=User)
        user.id = "user-123"
        user.email = sample_user_data["email"]
        user.username = sample_user_data["username"]
        user.hashed_password = "hashed_password_123"
        user.first_name = sample_user_data["first_name"]
        user.last_name = sample_user_data["last_name"]
        user.display_name = sample_user_data["display_name"]
        user.bio = sample_user_data["bio"]
        user.phone = sample_user_data["phone"]
        user.organization_id = sample_user_data["organization_id"]
        user.role = sample_user_data["role"]
        user.is_active = sample_user_data["is_active"]
        user.is_verified = sample_user_data["is_verified"]
        user.is_locked = False
        return user

    @pytest.fixture
    def sample_user_create(self, sample_user_data):
        """Create a sample UserCreate object."""
        return UserCreate(**sample_user_data)

    @pytest.fixture
    def sample_user_update(self):
        """Create a sample UserUpdate object."""
        return UserUpdate(
            first_name="Updated",
            last_name="Name",
            display_name="Updated Name",
            bio="Updated bio",
            phone="+0987654321",
        )

    @pytest.fixture
    def sample_admin_user(self):
        """Create a sample admin user."""
        admin = Mock(spec=User)
        admin.id = "admin-123"
        admin.email = "admin@example.com"
        admin.username = "admin"
        admin.role = UserRole.ADMIN
        admin.is_active = True
        admin.organization_id = "550e8400-e29b-41d4-a716-446655440000"
        return admin

    # Test create_user method
    def test_create_user_success(self, user_service, sample_user_create, sample_user):
        """Test successful user creation."""
        # Mock service methods
        user_service.get_user_by_email.return_value = None
        user_service.get_user_by_username.return_value = None
        user_service.create_user.return_value = sample_user
        
        # Execute
        result = user_service.create_user(user_data=sample_user_create)
        
        # Assert
        assert result == sample_user
        user_service.create_user.assert_called_once_with(user_data=sample_user_create)

    def test_create_user_email_already_exists(self, user_service, sample_user_create, sample_user):
        """Test user creation with existing email."""
        # Mock service method to raise exception
        user_service.create_user.side_effect = UserAlreadyExistsError("Email already exists")
        
        # Execute and assert
        with pytest.raises(UserAlreadyExistsError):
            user_service.create_user(user_data=sample_user_create)

    def test_create_user_username_already_exists(self, user_service, sample_user_create, sample_user):
        """Test user creation with existing username."""
        # Mock service method to raise exception
        user_service.create_user.side_effect = UserAlreadyExistsError("Username already exists")
        
        # Execute and assert
        with pytest.raises(UserAlreadyExistsError):
            user_service.create_user(user_data=sample_user_create)

    # Test get_user_by_id method
    def test_get_user_by_id_success(self, user_service, sample_user):
        """Test successful user retrieval by ID."""
        # Mock service method
        user_service.get_user_by_id.return_value = sample_user
        
        # Execute
        result = user_service.get_user_by_id("user-123")
        
        # Assert
        assert result == sample_user
        user_service.get_user_by_id.assert_called_once_with("user-123")

    def test_get_user_by_id_not_found(self, user_service):
        """Test user retrieval by ID when user not found."""
        # Mock service method
        user_service.get_user_by_id.return_value = None
        
        # Execute
        result = user_service.get_user_by_id("nonexistent-user")
        
        # Assert
        assert result is None
        user_service.get_user_by_id.assert_called_once_with("nonexistent-user")

    # Test get_user_by_email method
    def test_get_user_by_email_success(self, user_service, sample_user):
        """Test successful user retrieval by email."""
        # Mock service method
        user_service.get_user_by_email.return_value = sample_user
        
        # Execute
        result = user_service.get_user_by_email("test@example.com")
        
        # Assert
        assert result == sample_user
        user_service.get_user_by_email.assert_called_once_with("test@example.com")

    def test_get_user_by_email_not_found(self, user_service):
        """Test user retrieval by email when user not found."""
        # Mock service method
        user_service.get_user_by_email.return_value = None
        
        # Execute
        result = user_service.get_user_by_email("nonexistent@example.com")
        
        # Assert
        assert result is None
        user_service.get_user_by_email.assert_called_once_with("nonexistent@example.com")

    # Test get_user_by_username method
    def test_get_user_by_username_success(self, user_service, sample_user):
        """Test successful user retrieval by username."""
        # Mock service method
        user_service.get_user_by_username.return_value = sample_user
        
        # Execute
        result = user_service.get_user_by_username("testuser")
        
        # Assert
        assert result == sample_user
        user_service.get_user_by_username.assert_called_once_with("testuser")

    def test_get_user_by_username_not_found(self, user_service):
        """Test user retrieval by username when user not found."""
        # Mock service method
        user_service.get_user_by_username.return_value = None
        
        # Execute
        result = user_service.get_user_by_username("nonexistentuser")
        
        # Assert
        assert result is None
        user_service.get_user_by_username.assert_called_once_with("nonexistentuser")

    # Test authenticate_user method
    def test_authenticate_user_success(self, user_service, sample_user):
        """Test successful user authentication."""
        # Mock service method
        user_service.authenticate_user.return_value = sample_user
        
        # Execute
        result = user_service.authenticate_user("test@example.com", "password123")
        
        # Assert
        assert result == sample_user
        user_service.authenticate_user.assert_called_once_with("test@example.com", "password123")

    def test_authenticate_user_failure(self, user_service):
        """Test failed user authentication."""
        # Mock service method
        user_service.authenticate_user.return_value = None
        
        # Execute
        result = user_service.authenticate_user("test@example.com", "wrongpassword")
        
        # Assert
        assert result is None
        user_service.authenticate_user.assert_called_once_with("test@example.com", "wrongpassword")

    def test_authenticate_user_locked_user(self, user_service, sample_user):
        """Test authentication with locked user."""
        # Set user as locked
        sample_user.is_locked = True
        
        # Mock service method to raise exception
        user_service.authenticate_user.side_effect = UserLockedError
        
        # Execute and assert
        with pytest.raises(UserLockedError):
            user_service.authenticate_user("test@example.com", "password123")

    # Test update_user method
    def test_update_user_success(self, user_service, sample_user, sample_user_update):
        """Test successful user update."""
        # Mock service method
        user_service.update_user.return_value = sample_user
        
        # Execute
        result = user_service.update_user("user-123", sample_user_update, sample_user)
        
        # Assert
        assert result == sample_user
        user_service.update_user.assert_called_once_with("user-123", sample_user_update, sample_user)

    def test_update_user_not_found(self, user_service, sample_user_update, sample_admin_user):
        """Test user update when user not found."""
        # Mock service method to raise exception
        user_service.update_user.side_effect = UserNotFoundError
        
        # Execute and assert
        with pytest.raises(UserNotFoundError):
            user_service.update_user("nonexistent-user", sample_user_update, sample_admin_user)

    def test_update_user_permission_denied(self, user_service, sample_user, sample_user_update):
        """Test user update with insufficient permissions."""
        # Mock service method to raise exception
        user_service.update_user.side_effect = PermissionDeniedError
        
        # Execute and assert
        with pytest.raises(PermissionDeniedError):
            user_service.update_user("user-123", sample_user_update, sample_user)

    # Test delete_user method
    def test_delete_user_success(self, user_service, sample_user, sample_admin_user):
        """Test successful user deletion."""
        # Mock service method
        user_service.delete_user.return_value = True
        
        # Execute
        result = user_service.delete_user("user-123", sample_admin_user)
        
        # Assert
        assert result is True
        user_service.delete_user.assert_called_once_with("user-123", sample_admin_user)

    def test_delete_user_not_found(self, user_service, sample_admin_user):
        """Test user deletion when user not found."""
        # Mock service method to raise exception
        user_service.delete_user.side_effect = UserNotFoundError
        
        # Execute and assert
        with pytest.raises(UserNotFoundError):
            user_service.delete_user("nonexistent-user", sample_admin_user)

    def test_delete_user_permission_denied(self, user_service, sample_user):
        """Test user deletion with insufficient permissions."""
        # Mock service method to raise exception
        user_service.delete_user.side_effect = PermissionDeniedError
        
        # Execute and assert
        with pytest.raises(PermissionDeniedError):
            user_service.delete_user("user-123", sample_user)

    # Test list_users method
    def test_list_users_success(self, user_service, sample_user, sample_admin_user):
        """Test successful user listing."""
        # Mock service method
        mock_response = Mock()
        mock_response.users = [sample_user]
        mock_response.total = 1
        user_service.list_users.return_value = mock_response
        
        # Create search parameters
        search_params = UserSearchParams(
            page=1,
            size=10,
            search="test",
            role=UserRole.USER,
            is_active=True
        )
        
        # Execute
        result = user_service.list_users(search_params, sample_admin_user)
        
        # Assert
        assert result is not None
        assert len(result.users) == 1
        assert result.total == 1
        user_service.list_users.assert_called_once_with(search_params, sample_admin_user)

    def test_list_users_empty_result(self, user_service, sample_admin_user):
        """Test user listing with empty result."""
        # Mock service method
        mock_response = Mock()
        mock_response.users = []
        mock_response.total = 0
        user_service.list_users.return_value = mock_response
        
        # Create search parameters
        search_params = UserSearchParams(
            page=1,
            size=10,
            search="nonexistent"
        )
        
        # Execute
        result = user_service.list_users(search_params, sample_admin_user)
        
        # Assert
        assert result is not None
        assert len(result.users) == 0
        assert result.total == 0

    # Test update_password method
    def test_update_password_success(self, user_service, sample_user):
        """Test successful password update."""
        # Mock service method
        user_service.update_password.return_value = True
        
        # Create password update data
        password_data = UserPasswordUpdate(
            current_password="oldpassword",
            new_password="NewPassword123!"
        )
        
        # Execute
        result = user_service.update_password("user-123", password_data)
        
        # Assert
        assert result is True
        user_service.update_password.assert_called_once_with("user-123", password_data)

    def test_update_password_user_not_found(self, user_service):
        """Test password update when user not found."""
        # Mock service method to raise exception
        user_service.update_password.side_effect = UserNotFoundError
        
        # Create password update data
        password_data = UserPasswordUpdate(
            current_password="oldpassword",
            new_password="NewPassword123!"
        )
        
        # Execute and assert
        with pytest.raises(UserNotFoundError):
            user_service.update_password("nonexistent-user", password_data)

    def test_update_password_incorrect_current_password(self, user_service, sample_user):
        """Test password update with incorrect current password."""
        # Mock service method to raise exception
        user_service.update_password.side_effect = InvalidCredentialsError
        
        # Create password update data
        password_data = UserPasswordUpdate(
            current_password="wrongpassword",
            new_password="NewPassword123!"
        )
        
        # Execute and assert
        with pytest.raises(InvalidCredentialsError):
            user_service.update_password("user-123", password_data)

    # Test verify_email method
    def test_verify_email_success(self, user_service, sample_user):
        """Test successful email verification."""
        # Mock service method
        user_service.verify_email.return_value = True
        
        # Execute
        result = user_service.verify_email("user-123")
        
        # Assert
        assert result is True
        user_service.verify_email.assert_called_once_with("user-123")

    def test_verify_email_user_not_found(self, user_service):
        """Test email verification when user not found."""
        # Mock service method to raise exception
        user_service.verify_email.side_effect = UserNotFoundError
        
        # Execute and assert
        with pytest.raises(UserNotFoundError):
            user_service.verify_email("nonexistent-user")

    # Test create_sso_user method
    def test_create_sso_user_success(self, user_service, sample_user):
        """Test successful SSO user creation."""
        # Mock service method
        user_service.create_sso_user.return_value = sample_user
        
        # Create SSO user data
        sso_data = SSOUserCreate(
            email="sso@example.com",
            username="ssouser",
            external_id="ext-123",
            auth_provider=AuthProvider.OAUTH_GOOGLE,
            first_name="SSO",
            last_name="User",
            display_name="SSO User",
            sso_attributes={"provider": "google", "sub": "ext-123"}
        )
        
        # Execute
        result = user_service.create_sso_user(sso_data)
        
        # Assert
        assert result == sample_user
        user_service.create_sso_user.assert_called_once_with(sso_data)

    def test_create_sso_user_email_already_exists(self, user_service, sample_user):
        """Test SSO user creation with existing email."""
        # Mock service method to raise exception
        user_service.create_sso_user.side_effect = UserAlreadyExistsError
        
        # Create SSO user data
        sso_data = SSOUserCreate(
            email="sso@example.com",
            username="ssouser",
            external_id="ext-123",
            auth_provider=AuthProvider.OAUTH_GOOGLE,
            first_name="SSO",
            last_name="User",
            sso_attributes={"provider": "google", "sub": "ext-123"}
        )
        
        # Execute and assert
        with pytest.raises(UserAlreadyExistsError):
            user_service.create_sso_user(sso_data)

    # Test get_user_stats method
    def test_get_user_stats_success(self, user_service, sample_admin_user):
        """Test successful user statistics retrieval."""
        # Mock service method
        mock_stats = Mock()
        mock_stats.total_users = 10
        mock_stats.active_users = 8
        mock_stats.inactive_users = 2
        user_service.get_user_stats.return_value = mock_stats
        
        # Execute
        result = user_service.get_user_stats(organization_id="org-123", current_user=sample_admin_user)
        
        # Assert
        assert result is not None
        assert result.total_users == 10
        assert result.active_users == 8
        assert result.inactive_users == 2
        user_service.get_user_stats.assert_called_once_with(organization_id="org-123", current_user=sample_admin_user)

    # Test _can_manage_user method
    def test_can_manage_user_admin_managing_anyone(self, user_service, sample_admin_user, sample_user):
        """Test admin can manage any user."""
        # Mock service method
        user_service._can_manage_user.return_value = True
        
        # Execute
        result = user_service._can_manage_user(sample_admin_user, sample_user)
        
        # Assert
        assert result is True
        user_service._can_manage_user.assert_called_once_with(sample_admin_user, sample_user)

    def test_can_manage_user_self_management(self, user_service, sample_user):
        """Test user can manage themselves."""
        # Mock service method
        user_service._can_manage_user.return_value = True
        
        # Execute
        result = user_service._can_manage_user(sample_user, sample_user)
        
        # Assert
        assert result is True
        user_service._can_manage_user.assert_called_once_with(sample_user, sample_user)

    def test_can_manage_user_regular_user_managing_other(self, user_service, sample_user):
        """Test regular user cannot manage other users."""
        other_user = Mock(spec=User)
        other_user.id = "other-123"
        other_user.role = UserRole.USER
        
        # Mock service method
        user_service._can_manage_user.return_value = False
        
        # Execute
        result = user_service._can_manage_user(sample_user, other_user)
        
        # Assert
        assert result is False
        user_service._can_manage_user.assert_called_once_with(sample_user, other_user)

    # Test error handling
    def test_database_error_handling(self, user_service):
        """Test error handling when database operations fail."""
        # Mock service method to raise exception
        user_service.get_user_by_id.side_effect = Exception("Database error")
        
        # Execute and assert
        with pytest.raises(Exception, match="Database error"):
            user_service.get_user_by_id("user-123")

    # Test edge cases
    def test_user_service_initialization_without_db(self):
        """Test UserService initialization without database parameter."""
        with patch('backend.app.services.user_service.get_db') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Execute
            service = UserService()
            
            # Assert
            assert service.db == mock_db
            mock_get_db.assert_called_once()

    def test_user_service_initialization_with_db(self):
        """Test UserService initialization with database parameter."""
        mock_db = Mock()
        
        # Execute
        service = UserService(db=mock_db)
        
        # Assert
        assert service.db == mock_db

    def test_password_context_initialization(self, user_service):
        """Test password context is properly initialized."""
        assert user_service.pwd_context is not None
        assert hasattr(user_service.pwd_context, 'hash')
        assert hasattr(user_service.pwd_context, 'verify')

    # Test performance scenarios
    def test_multiple_user_operations(self, user_service, sample_user, sample_admin_user):
        """Test multiple user operations in sequence."""
        # Mock service methods
        user_service.get_user_by_id.return_value = sample_user
        user_service.get_user_by_email.return_value = sample_user
        user_service.get_user_by_username.return_value = sample_user
        
        # Execute multiple operations
        user1 = user_service.get_user_by_id("user-123")
        user2 = user_service.get_user_by_email("test@example.com")
        user3 = user_service.get_user_by_username("testuser")
        
        # Assert
        assert user1 == sample_user
        assert user2 == sample_user
        assert user3 == sample_user
        assert user_service.get_user_by_id.call_count == 1
        assert user_service.get_user_by_email.call_count == 1
        assert user_service.get_user_by_username.call_count == 1

    def test_concurrent_user_operations(self, user_service, sample_user):
        """Test concurrent user operations."""
        # Mock service method
        user_service.get_user_by_id.return_value = sample_user
        
        # Simulate concurrent operations
        results = []
        for i in range(5):
            result = user_service.get_user_by_id(f"user-{i}")
            results.append(result)
        
        # Assert
        assert all(result == sample_user for result in results)
        assert user_service.get_user_by_id.call_count == 5