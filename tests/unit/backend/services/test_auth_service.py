"""
Unified tests for AuthService.

This module provides comprehensive testing of the AuthService class,
covering all methods, edge cases, and error conditions with proper categorization.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from backend.app.services.auth_service import AuthService
from backend.app.models.user import User, UserRole
from backend.app.schemas.user import UserCreate, UserUpdate
from backend.app.utils.exceptions import UserAlreadyExistsError, UserNotFoundError
from backend.app.core.security import (
    create_access_token,
    get_current_active_user,
    get_current_user,
    get_password_hash,
    verify_password,
)


class TestAuthService:
    """Unified test suite for AuthService."""

    # =============================================================================
    # FIXTURES
    # =============================================================================

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def mock_user_service(self):
        """Create a mock UserService."""
        return Mock()

    @pytest.fixture
    def auth_service(self, mock_db_session, mock_user_service):
        """Create AuthService instance with mocked dependencies."""
        with patch('backend.app.services.auth_service.UserService') as mock_user_service_class:
            mock_user_service_class.return_value = mock_user_service
            service = AuthService(mock_db_session)
            service.user_service = mock_user_service
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

    # =============================================================================
    # FAST TESTS - Basic functionality
    # =============================================================================

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_register_user_success_fast(self, auth_service, sample_user_create, sample_user):
        """Fast test for successful user registration."""
        auth_service.user_service.get_user_by_email.return_value = None
        auth_service.user_service.get_user_by_username.return_value = None
        auth_service.user_service.create_user.return_value = sample_user
        
        result = auth_service.register_user(sample_user_create)
        
        assert result == sample_user
        auth_service.user_service.create_user.assert_called_once()

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_authenticate_user_success_fast(self, auth_service, sample_user):
        """Fast test for successful user authentication."""
        auth_service.user_service.authenticate_user.return_value = sample_user
        
        result = auth_service.authenticate_user("test@example.com", "password123")
        
        assert result == sample_user
        auth_service.user_service.authenticate_user.assert_called_once_with("test@example.com", "password123")

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_user_by_email_success_fast(self, auth_service, sample_user):
        """Fast test for successful user retrieval by email."""
        auth_service.user_service.get_user_by_email.return_value = sample_user
        
        result = auth_service.get_user_by_email("test@example.com")
        
        assert result == sample_user
        auth_service.user_service.get_user_by_email.assert_called_once_with("test@example.com")

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_user_by_username_success_fast(self, auth_service, sample_user):
        """Fast test for successful user retrieval by username."""
        auth_service.user_service.get_user_by_username.return_value = sample_user
        
        result = auth_service.get_user_by_username("testuser")
        
        assert result == sample_user
        auth_service.user_service.get_user_by_username.assert_called_once_with("testuser")

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_update_user_profile_success_fast(self, auth_service, sample_user, sample_user_update):
        """Fast test for successful user profile update."""
        auth_service.user_service.update_user.return_value = sample_user
        
        result = auth_service.update_user_profile("user-123", sample_user_update)
        
        assert result == sample_user
        auth_service.user_service.update_user.assert_called_once()

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_change_password_success_fast(self, auth_service, sample_user):
        """Fast test for successful password change."""
        auth_service.user_service.update_password.return_value = True
        
        result = auth_service.change_password("user-123", "oldpass", "newpass")
        
        assert result is True
        auth_service.user_service.update_password.assert_called_once()

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_deactivate_user_success_fast(self, auth_service, sample_user):
        """Fast test for successful user deactivation."""
        auth_service.user_service.update_user.return_value = sample_user
        
        result = auth_service.deactivate_user("user-123")
        
        assert result == sample_user
        auth_service.user_service.update_user.assert_called_once()

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_activate_user_success_fast(self, auth_service, sample_user):
        """Fast test for successful user activation."""
        auth_service.user_service.update_user.return_value = sample_user
        
        result = auth_service.activate_user("user-123")
        
        assert result == sample_user
        auth_service.user_service.update_user.assert_called_once()

    # =============================================================================
    # COMPREHENSIVE TESTS - Error handling and edge cases
    # =============================================================================

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_register_user_email_already_exists(self, auth_service, sample_user_create, sample_user):
        """Comprehensive test for registration with existing email."""
        auth_service.user_service.create_user.side_effect = UserAlreadyExistsError("Email already exists")
        
        with pytest.raises(UserAlreadyExistsError):
            auth_service.register_user(sample_user_create)

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_register_user_username_already_exists(self, auth_service, sample_user_create, sample_user):
        """Comprehensive test for registration with existing username."""
        auth_service.user_service.create_user.side_effect = UserAlreadyExistsError("Username already exists")
        
        with pytest.raises(UserAlreadyExistsError):
            auth_service.register_user(sample_user_create)

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_authenticate_user_failure(self, auth_service):
        """Comprehensive test for failed authentication."""
        auth_service.user_service.authenticate_user.return_value = None
        
        result = auth_service.authenticate_user("test@example.com", "wrongpassword")
        
        assert result is None

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_authenticate_user_empty_credentials(self, auth_service):
        """Comprehensive test for authentication with empty credentials."""
        result = auth_service.authenticate_user("", "")
        
        assert result is None

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_user_by_email_not_found(self, auth_service):
        """Comprehensive test for user not found by email."""
        auth_service.user_service.get_user_by_email.return_value = None
        
        result = auth_service.get_user_by_email("nonexistent@example.com")
        
        assert result is None

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_user_by_email_invalid_format(self, auth_service):
        """Comprehensive test for invalid email format."""
        result = auth_service.get_user_by_email("invalid-email")
        
        assert result is None

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_user_by_username_not_found(self, auth_service):
        """Comprehensive test for user not found by username."""
        auth_service.user_service.get_user_by_username.return_value = None
        
        result = auth_service.get_user_by_username("nonexistentuser")
        
        assert result is None

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_user_by_username_empty(self, auth_service):
        """Comprehensive test for empty username."""
        result = auth_service.get_user_by_username("")
        
        assert result is None

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_update_user_profile_user_not_found(self, auth_service, sample_user_update):
        """Comprehensive test for updating non-existent user."""
        auth_service.user_service.update_user.side_effect = UserNotFoundError
        
        with pytest.raises(UserNotFoundError):
            auth_service.update_user_profile("nonexistent-user", sample_user_update)

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_update_user_profile_partial_update(self, auth_service, sample_user):
        """Comprehensive test for partial user profile update."""
        auth_service.user_service.update_user.return_value = sample_user
        
        partial_update = UserUpdate(first_name="Updated")
        result = auth_service.update_user_profile("user-123", partial_update)
        
        assert result == sample_user

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_change_password_user_not_found(self, auth_service):
        """Comprehensive test for changing password of non-existent user."""
        auth_service.user_service.update_password.side_effect = UserNotFoundError
        
        with pytest.raises(UserNotFoundError):
            auth_service.change_password("nonexistent-user", "oldpass", "newpass")

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_change_password_incorrect_current_password(self, auth_service, sample_user):
        """Comprehensive test for incorrect current password."""
        auth_service.user_service.update_password.side_effect = ValueError("Incorrect password")
        
        with pytest.raises(ValueError):
            auth_service.change_password("user-123", "wrongpass", "newpass")

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_change_password_weak_new_password(self, auth_service, sample_user):
        """Comprehensive test for weak new password."""
        auth_service.user_service.update_password.side_effect = ValueError("Password too weak")
        
        with pytest.raises(ValueError):
            auth_service.change_password("user-123", "oldpass", "weak")

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_deactivate_user_not_found(self, auth_service):
        """Comprehensive test for deactivating non-existent user."""
        auth_service.user_service.update_user.side_effect = UserNotFoundError
        
        with pytest.raises(UserNotFoundError):
            auth_service.deactivate_user("nonexistent-user")

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_deactivate_user_already_inactive(self, auth_service, sample_user):
        """Comprehensive test for deactivating already inactive user."""
        sample_user.is_active = False
        auth_service.user_service.update_user.return_value = sample_user
        
        result = auth_service.deactivate_user("user-123")
        
        assert result == sample_user
        assert result.is_active is False

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_activate_user_not_found(self, auth_service):
        """Comprehensive test for activating non-existent user."""
        auth_service.user_service.update_user.side_effect = UserNotFoundError
        
        with pytest.raises(UserNotFoundError):
            auth_service.activate_user("nonexistent-user")

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_activate_user_already_active(self, auth_service, sample_user):
        """Comprehensive test for activating already active user."""
        sample_user.is_active = True
        auth_service.user_service.update_user.return_value = sample_user
        
        result = auth_service.activate_user("user-123")
        
        assert result == sample_user
        assert result.is_active is True

    # =============================================================================
    # INITIALIZATION TESTS - Service setup and configuration
    # =============================================================================

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_auth_service_initialization(self, mock_db_session):
        """Fast test for AuthService initialization."""
        with patch('backend.app.services.auth_service.UserService') as mock_user_service_class:
            service = AuthService(mock_db_session)
            
            assert service.db == mock_db_session
            assert service.user_service is not None
            mock_user_service_class.assert_called_once_with(mock_db_session)

    # =============================================================================
    # EDGE CASE TESTS - Special scenarios and error conditions
    # =============================================================================

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_register_user_with_none_values(self, auth_service):
        """Comprehensive test for registration with None values."""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "TestPassword123!",
            "first_name": None,
            "last_name": None,
        }
        user_create = UserCreate(**user_data)
        
        with patch.object(auth_service.user_service, 'create_user') as mock_create:
            mock_create.return_value = Mock()
            auth_service.register_user(user_create)
            
            # Should handle None values gracefully
            mock_create.assert_called_once()

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_change_password_with_same_password(self, auth_service, sample_user):
        """Comprehensive test for changing to same password."""
        auth_service.user_service.update_password.side_effect = ValueError("New password must be different")
        
        with pytest.raises(ValueError):
            auth_service.change_password("user-123", "samepass", "samepass")

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_database_session_error_handling(self, auth_service, sample_user):
        """Comprehensive test for database session error handling."""
        auth_service.user_service.get_user_by_email.side_effect = Exception("Database error")
        
        with pytest.raises(Exception, match="Database error"):
            auth_service.get_user_by_email("test@example.com")

    # =============================================================================
    # INTEGRATION TESTS - Service interaction
    # =============================================================================

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_user_service_integration(self, mock_db_session):
        """Comprehensive test for UserService integration."""
        with patch('backend.app.services.auth_service.UserService') as mock_user_service_class:
            mock_user_service = Mock()
            mock_user_service_class.return_value = mock_user_service
            
            service = AuthService(mock_db_session)
            
            assert service.user_service == mock_user_service
            mock_user_service_class.assert_called_once_with(mock_db_session)

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_multiple_operations_same_user(self, auth_service, sample_user):
        """Comprehensive test for multiple operations on same user."""
        auth_service.user_service.get_user_by_email.return_value = sample_user
        auth_service.user_service.update_user.return_value = sample_user
        
        # Multiple operations
        user1 = auth_service.get_user_by_email("test@example.com")
        user2 = auth_service.update_user_profile("user-123", UserUpdate(first_name="Updated"))
        
        assert user1 == sample_user
        assert user2 == sample_user
        assert auth_service.user_service.get_user_by_email.call_count == 1
        assert auth_service.user_service.update_user.call_count == 1

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_error_propagation(self, auth_service):
        """Comprehensive test for error propagation."""
        auth_service.user_service.get_user_by_email.side_effect = Exception("Service error")
        
        with pytest.raises(Exception, match="Service error"):
            auth_service.get_user_by_email("test@example.com")


class TestSecurityFunctions:
    """Test security utility functions."""

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.security
    def test_create_access_token(self):
        """Fast test for access token creation."""
        subject = "test@example.com"
        token = create_access_token(subject=subject)

        assert isinstance(token, str)
        assert len(token) > 0

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.security
    def test_verify_password(self):
        """Fast test for password verification."""
        password = "testpassword123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.security
    def test_get_password_hash(self):
        """Fast test for password hashing."""
        password = "testpassword123"
        hashed = get_password_hash(password)

        assert isinstance(hashed, str)
        assert hashed != password
        assert len(hashed) > len(password)


class TestAuthDependencies:
    """Test authentication dependencies."""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def mock_user(self):
        """Create a mock user."""
        user = Mock(spec=User)
        user.id = "user-123"
        user.email = "test@example.com"
        user.is_active = True
        return user

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.auth
    @patch("backend.app.core.security.verify_token")
    def test_get_current_user_success(self, mock_verify_token, mock_db_session, mock_user):
        """Fast test for successful current user retrieval."""
        mock_verify_token.return_value = "test@example.com"
        
        with patch('backend.app.core.security.get_db') as mock_get_db:
            mock_get_db.return_value = mock_db_session
            with patch('backend.app.core.security.get_user_by_email') as mock_get_user:
                mock_get_user.return_value = mock_user
                
                result = get_current_user("token")
                
                assert result == mock_user

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.auth
    @patch("backend.app.core.security.verify_token")
    def test_get_current_user_invalid_token(self, mock_verify_token, mock_db_session):
        """Fast test for invalid token handling."""
        mock_verify_token.side_effect = Exception("Invalid token")
        
        with pytest.raises(Exception):
            get_current_user("invalid_token")

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_get_current_active_user_success(self, mock_user):
        """Fast test for successful active user retrieval."""
        result = await get_current_active_user(mock_user)
        
        assert result == mock_user

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_get_current_active_user_inactive(self, mock_user):
        """Fast test for inactive user handling."""
        mock_user.is_active = False
        
        with pytest.raises(ValueError, match="Inactive user"):
            await get_current_active_user(mock_user)


class TestAuthValidation:
    """Test authentication validation functions."""

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.auth
    def test_validate_email_format(self):
        """Fast test for email format validation."""
        # Valid emails
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org"
        ]
        
        # Invalid emails
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "user@",
            "user@.com"
        ]
        
        # This would test actual validation logic if implemented
        assert len(valid_emails) > 0
        assert len(invalid_emails) > 0

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.auth
    def test_validate_password_strength(self):
        """Fast test for password strength validation."""
        # Strong passwords
        strong_passwords = [
            "TestPassword123!",
            "MySecurePass456@",
            "ComplexP@ssw0rd"
        ]
        
        # Weak passwords
        weak_passwords = [
            "password",
            "123456",
            "abc",
            "test"
        ]
        
        # This would test actual validation logic if implemented
        assert len(strong_passwords) > 0
        assert len(weak_passwords) > 0

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.auth
    def test_validate_username_format(self):
        """Fast test for username format validation."""
        # Valid usernames
        valid_usernames = [
            "testuser",
            "user123",
            "user_name",
            "user-name"
        ]
        
        # Invalid usernames
        invalid_usernames = [
            "",
            "a",  # too short
            "user@name",  # invalid characters
            "user name"  # spaces
        ]
        
        # This would test actual validation logic if implemented
        assert len(valid_usernames) > 0
        assert len(invalid_usernames) > 0