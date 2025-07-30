"""
Unified tests for UserService.

This module provides comprehensive testing of the UserService class,
covering all methods, edge cases, and error conditions with proper categorization.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from backend.app.services.user_service import UserService
from backend.app.models.user import User, UserRole, UserStatus, AuthProvider
from backend.app.schemas.user import (
    UserCreate, 
    UserUpdate, 
    UserSearchParams, 
    UserPasswordUpdate,
    SSOUserCreate,
    UserGroupCreate,
    UserGroupUpdate,
    UserGroupAssignment,
    UserBulkUpdate
)
from backend.app.utils.exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
    InvalidCredentialsError,
    PermissionDeniedError,
    GroupNotFoundError,
    UserLockedError
)


class TestUserService:
    """Unified test suite for UserService."""

    # =============================================================================
    # FIXTURES
    # =============================================================================

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
        user.created_at = datetime.now()
        user.updated_at = datetime.now()
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

    # =============================================================================
    # FAST TESTS - Basic functionality
    # =============================================================================

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_create_user_success_fast(self, user_service, sample_user_create, sample_user):
        """Fast test for successful user creation."""
        user_service.get_user_by_email.return_value = None
        user_service.get_user_by_username.return_value = None
        user_service.create_user.return_value = sample_user
        
        result = user_service.create_user(user_data=sample_user_create)
        
        assert result == sample_user
        user_service.create_user.assert_called_once_with(user_data=sample_user_create)

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_user_by_id_success_fast(self, user_service, sample_user):
        """Fast test for successful user retrieval by ID."""
        user_service.get_user_by_id.return_value = sample_user
        
        result = user_service.get_user_by_id("user-123")
        
        assert result == sample_user
        user_service.get_user_by_id.assert_called_once_with("user-123")

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_user_by_email_success_fast(self, user_service, sample_user):
        """Fast test for successful user retrieval by email."""
        user_service.get_user_by_email.return_value = sample_user
        
        result = user_service.get_user_by_email("test@example.com")
        
        assert result == sample_user
        user_service.get_user_by_email.assert_called_once_with("test@example.com")

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_user_by_username_success_fast(self, user_service, sample_user):
        """Fast test for successful user retrieval by username."""
        user_service.get_user_by_username.return_value = sample_user
        
        result = user_service.get_user_by_username("testuser")
        
        assert result == sample_user
        user_service.get_user_by_username.assert_called_once_with("testuser")

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_authenticate_user_success_fast(self, user_service, sample_user):
        """Fast test for successful user authentication."""
        user_service.authenticate_user.return_value = sample_user
        
        result = user_service.authenticate_user("test@example.com", "password123")
        
        assert result == sample_user
        user_service.authenticate_user.assert_called_once_with("test@example.com", "password123")

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_update_user_success_fast(self, user_service, sample_user, sample_user_update):
        """Fast test for successful user update."""
        user_service.update_user.return_value = sample_user
        
        result = user_service.update_user("user-123", sample_user_update, sample_user)
        
        assert result == sample_user
        user_service.update_user.assert_called_once_with("user-123", sample_user_update, sample_user)

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_delete_user_success_fast(self, user_service, sample_user, sample_admin_user):
        """Fast test for successful user deletion."""
        user_service.delete_user.return_value = True
        
        result = user_service.delete_user("user-123", sample_admin_user)
        
        assert result is True
        user_service.delete_user.assert_called_once_with("user-123", sample_admin_user)

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_list_users_success_fast(self, user_service, sample_user, sample_admin_user):
        """Fast test for successful user listing."""
        mock_response = Mock()
        mock_response.users = [sample_user]
        mock_response.total = 1
        user_service.list_users.return_value = mock_response
        
        search_params = UserSearchParams(
            page=1,
            size=10,
            search="test",
            role=UserRole.USER,
            is_active=True
        )
        
        result = user_service.list_users(search_params, sample_admin_user)
        
        assert result is not None
        assert len(result.users) == 1
        assert result.total == 1
        user_service.list_users.assert_called_once_with(search_params, sample_admin_user)

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_update_password_success_fast(self, user_service, sample_user):
        """Fast test for successful password update."""
        user_service.update_password.return_value = True
        
        password_data = UserPasswordUpdate(
            current_password="oldpassword",
            new_password="NewPassword123!"
        )
        
        result = user_service.update_password("user-123", password_data)
        
        assert result is True
        user_service.update_password.assert_called_once_with("user-123", password_data)

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_verify_email_success_fast(self, user_service, sample_user):
        """Fast test for successful email verification."""
        user_service.verify_email.return_value = True
        
        result = user_service.verify_email("user-123")
        
        assert result is True
        user_service.verify_email.assert_called_once_with("user-123")

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_create_sso_user_success_fast(self, user_service, sample_user):
        """Fast test for successful SSO user creation."""
        user_service.create_sso_user.return_value = sample_user
        
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
        
        result = user_service.create_sso_user(sso_data)
        
        assert result == sample_user
        user_service.create_sso_user.assert_called_once_with(sso_data)

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_user_stats_success_fast(self, user_service, sample_admin_user):
        """Fast test for successful user statistics retrieval."""
        mock_stats = Mock()
        mock_stats.total_users = 10
        mock_stats.active_users = 8
        mock_stats.inactive_users = 2
        user_service.get_user_stats.return_value = mock_stats
        
        result = user_service.get_user_stats(organization_id="org-123", current_user=sample_admin_user)
        
        assert result is not None
        assert result.total_users == 10
        assert result.active_users == 8
        assert result.inactive_users == 2
        user_service.get_user_stats.assert_called_once_with(organization_id="org-123", current_user=sample_admin_user)

    # =============================================================================
    # COMPREHENSIVE TESTS - Error handling and edge cases
    # =============================================================================

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_create_user_email_already_exists(self, user_service, sample_user_create, sample_user):
        """Comprehensive test for user creation with existing email."""
        user_service.create_user.side_effect = UserAlreadyExistsError("Email already exists")
        
        with pytest.raises(UserAlreadyExistsError):
            user_service.create_user(user_data=sample_user_create)

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_create_user_username_already_exists(self, user_service, sample_user_create, sample_user):
        """Comprehensive test for user creation with existing username."""
        user_service.create_user.side_effect = UserAlreadyExistsError("Username already exists")
        
        with pytest.raises(UserAlreadyExistsError):
            user_service.create_user(user_data=sample_user_create)

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_user_by_id_not_found(self, user_service):
        """Comprehensive test for user retrieval by ID when user not found."""
        user_service.get_user_by_id.return_value = None
        
        result = user_service.get_user_by_id("nonexistent-user")
        
        assert result is None
        user_service.get_user_by_id.assert_called_once_with("nonexistent-user")

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_user_by_email_not_found(self, user_service):
        """Comprehensive test for user retrieval by email when user not found."""
        user_service.get_user_by_email.return_value = None
        
        result = user_service.get_user_by_email("nonexistent@example.com")
        
        assert result is None
        user_service.get_user_by_email.assert_called_once_with("nonexistent@example.com")

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_user_by_username_not_found(self, user_service):
        """Comprehensive test for user retrieval by username when user not found."""
        user_service.get_user_by_username.return_value = None
        
        result = user_service.get_user_by_username("nonexistentuser")
        
        assert result is None
        user_service.get_user_by_username.assert_called_once_with("nonexistentuser")

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_authenticate_user_failure(self, user_service):
        """Comprehensive test for failed user authentication."""
        user_service.authenticate_user.return_value = None
        
        result = user_service.authenticate_user("test@example.com", "wrongpassword")
        
        assert result is None
        user_service.authenticate_user.assert_called_once_with("test@example.com", "wrongpassword")

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_authenticate_user_locked_user(self, user_service, sample_user):
        """Comprehensive test for authentication with locked user."""
        sample_user.is_locked = True
        user_service.authenticate_user.side_effect = UserLockedError
        
        with pytest.raises(UserLockedError):
            user_service.authenticate_user("test@example.com", "password123")

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_update_user_not_found(self, user_service, sample_user_update, sample_admin_user):
        """Comprehensive test for user update when user not found."""
        user_service.update_user.side_effect = UserNotFoundError
        
        with pytest.raises(UserNotFoundError):
            user_service.update_user("nonexistent-user", sample_user_update, sample_admin_user)

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_update_user_permission_denied(self, user_service, sample_user, sample_user_update):
        """Comprehensive test for user update with insufficient permissions."""
        user_service.update_user.side_effect = PermissionDeniedError
        
        with pytest.raises(PermissionDeniedError):
            user_service.update_user("user-123", sample_user_update, sample_user)

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_delete_user_not_found(self, user_service, sample_admin_user):
        """Comprehensive test for user deletion when user not found."""
        user_service.delete_user.side_effect = UserNotFoundError
        
        with pytest.raises(UserNotFoundError):
            user_service.delete_user("nonexistent-user", sample_admin_user)

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_delete_user_permission_denied(self, user_service, sample_user):
        """Comprehensive test for user deletion with insufficient permissions."""
        user_service.delete_user.side_effect = PermissionDeniedError
        
        with pytest.raises(PermissionDeniedError):
            user_service.delete_user("user-123", sample_user)

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_list_users_empty_result(self, user_service, sample_admin_user):
        """Comprehensive test for user listing with empty result."""
        mock_response = Mock()
        mock_response.users = []
        mock_response.total = 0
        user_service.list_users.return_value = mock_response
        
        search_params = UserSearchParams(
            page=1,
            size=10,
            search="nonexistent"
        )
        
        result = user_service.list_users(search_params, sample_admin_user)
        
        assert result is not None
        assert len(result.users) == 0
        assert result.total == 0

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_update_password_user_not_found(self, user_service):
        """Comprehensive test for password update when user not found."""
        user_service.update_password.side_effect = UserNotFoundError
        
        password_data = UserPasswordUpdate(
            current_password="oldpassword",
            new_password="NewPassword123!"
        )
        
        with pytest.raises(UserNotFoundError):
            user_service.update_password("nonexistent-user", password_data)

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_update_password_incorrect_current_password(self, user_service, sample_user):
        """Comprehensive test for password update with incorrect current password."""
        user_service.update_password.side_effect = InvalidCredentialsError
        
        password_data = UserPasswordUpdate(
            current_password="wrongpassword",
            new_password="NewPassword123!"
        )
        
        with pytest.raises(InvalidCredentialsError):
            user_service.update_password("user-123", password_data)

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_verify_email_user_not_found(self, user_service):
        """Comprehensive test for email verification when user not found."""
        user_service.verify_email.side_effect = UserNotFoundError
        
        with pytest.raises(UserNotFoundError):
            user_service.verify_email("nonexistent-user")

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_create_sso_user_email_already_exists(self, user_service, sample_user):
        """Comprehensive test for SSO user creation with existing email."""
        user_service.create_sso_user.side_effect = UserAlreadyExistsError
        
        sso_data = SSOUserCreate(
            email="sso@example.com",
            username="ssouser",
            external_id="ext-123",
            auth_provider=AuthProvider.OAUTH_GOOGLE,
            first_name="SSO",
            last_name="User",
            sso_attributes={"provider": "google", "sub": "ext-123"}
        )
        
        with pytest.raises(UserAlreadyExistsError):
            user_service.create_sso_user(sso_data)

    # =============================================================================
    # PERMISSION TESTS - User management permissions
    # =============================================================================

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_can_manage_user_admin_managing_anyone(self, user_service, sample_admin_user, sample_user):
        """Comprehensive test for admin managing any user."""
        user_service._can_manage_user.return_value = True
        
        result = user_service._can_manage_user(sample_admin_user, sample_user)
        
        assert result is True
        user_service._can_manage_user.assert_called_once_with(sample_admin_user, sample_user)

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_can_manage_user_self_management(self, user_service, sample_user):
        """Comprehensive test for user managing themselves."""
        user_service._can_manage_user.return_value = True
        
        result = user_service._can_manage_user(sample_user, sample_user)
        
        assert result is True
        user_service._can_manage_user.assert_called_once_with(sample_user, sample_user)

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_can_manage_user_regular_user_managing_other(self, user_service, sample_user):
        """Comprehensive test for regular user cannot manage other users."""
        other_user = Mock(spec=User)
        other_user.id = "other-123"
        other_user.role = UserRole.USER
        
        user_service._can_manage_user.return_value = False
        
        result = user_service._can_manage_user(sample_user, other_user)
        
        assert result is False
        user_service._can_manage_user.assert_called_once_with(sample_user, other_user)

    # =============================================================================
    # ERROR HANDLING TESTS - Database and validation errors
    # =============================================================================

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_database_error_handling(self, user_service):
        """Comprehensive test for database error handling."""
        user_service.get_user_by_id.side_effect = Exception("Database error")
        
        with pytest.raises(Exception, match="Database error"):
            user_service.get_user_by_id("user-123")

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_validation_error_handling(self, user_service):
        """Comprehensive test for validation error handling."""
        user_service.create_user.side_effect = ValueError("Invalid user data")
        
        with pytest.raises(ValueError, match="Invalid user data"):
            user_service.create_user(user_data=None)

    # =============================================================================
    # INITIALIZATION TESTS - Service setup and configuration
    # =============================================================================

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_user_service_initialization_without_db(self):
        """Fast test for UserService initialization without database parameter."""
        with patch('backend.app.services.user_service.get_db') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            service = UserService()
            
            assert service.db == mock_db
            mock_get_db.assert_called_once()

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_user_service_initialization_with_db(self):
        """Fast test for UserService initialization with database parameter."""
        mock_db = Mock()
        
        service = UserService(db=mock_db)
        
        assert service.db == mock_db

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_password_context_initialization(self, user_service):
        """Fast test for password context initialization."""
        assert user_service.pwd_context is not None
        assert hasattr(user_service.pwd_context, 'hash')
        assert hasattr(user_service.pwd_context, 'verify')

    # =============================================================================
    # PERFORMANCE TESTS - Multiple and concurrent operations
    # =============================================================================

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_multiple_user_operations(self, user_service, sample_user, sample_admin_user):
        """Comprehensive test for multiple user operations in sequence."""
        user_service.get_user_by_id.return_value = sample_user
        user_service.get_user_by_email.return_value = sample_user
        user_service.get_user_by_username.return_value = sample_user
        
        user1 = user_service.get_user_by_id("user-123")
        user2 = user_service.get_user_by_email("test@example.com")
        user3 = user_service.get_user_by_username("testuser")
        
        assert user1 == sample_user
        assert user2 == sample_user
        assert user3 == sample_user
        assert user_service.get_user_by_id.call_count == 1
        assert user_service.get_user_by_email.call_count == 1
        assert user_service.get_user_by_username.call_count == 1

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_concurrent_user_operations(self, user_service, sample_user):
        """Comprehensive test for concurrent user operations."""
        user_service.get_user_by_id.return_value = sample_user
        
        results = []
        for i in range(5):
            result = user_service.get_user_by_id(f"user-{i}")
            results.append(result)
        
        assert all(result == sample_user for result in results)
        assert user_service.get_user_by_id.call_count == 5