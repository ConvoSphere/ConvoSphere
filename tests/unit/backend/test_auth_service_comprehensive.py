"""
Comprehensive tests for AuthService.

This module provides thorough testing of the AuthService class,
covering all methods, edge cases, and error conditions.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from backend.app.services.auth_service import AuthService
from backend.app.models.user import User, UserRole
from backend.app.schemas.user import UserCreate, UserUpdate
from backend.app.utils.exceptions import UserAlreadyExistsError, UserNotFoundError


class TestAuthServiceComprehensive:
    """Comprehensive tests for AuthService."""

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

    # Test register_user method
    def test_register_user_success(self, auth_service, sample_user_create, sample_user):
        """Test successful user registration."""
        # Mock user service methods
        auth_service.user_service.get_user_by_email.return_value = None
        auth_service.user_service.get_user_by_username.return_value = None
        auth_service.user_service.create_user.return_value = sample_user

        # Execute
        result = auth_service.register_user(sample_user_create)

        # Assert
        assert result == sample_user
        auth_service.user_service.get_user_by_email.assert_called_once_with(sample_user_create.email)
        auth_service.user_service.get_user_by_username.assert_called_once_with(sample_user_create.username)
        auth_service.user_service.create_user.assert_called_once_with(user_data=sample_user_create)

    def test_register_user_email_already_exists(self, auth_service, sample_user_create, sample_user):
        """Test user registration with existing email."""
        # Mock user service to return existing user
        auth_service.user_service.get_user_by_email.return_value = sample_user

        # Execute and assert
        with pytest.raises(ValueError, match="Email already registered"):
            auth_service.register_user(sample_user_create)

        auth_service.user_service.get_user_by_email.assert_called_once_with(sample_user_create.email)
        auth_service.user_service.get_user_by_username.assert_not_called()
        auth_service.user_service.create_user.assert_not_called()

    def test_register_user_username_already_exists(self, auth_service, sample_user_create, sample_user):
        """Test user registration with existing username."""
        # Mock user service
        auth_service.user_service.get_user_by_email.return_value = None
        auth_service.user_service.get_user_by_username.return_value = sample_user

        # Execute and assert
        with pytest.raises(ValueError, match="Username already taken"):
            auth_service.register_user(sample_user_create)

        auth_service.user_service.get_user_by_email.assert_called_once_with(sample_user_create.email)
        auth_service.user_service.get_user_by_username.assert_called_once_with(sample_user_create.username)
        auth_service.user_service.create_user.assert_not_called()

    # Test authenticate_user method
    def test_authenticate_user_success(self, auth_service, sample_user):
        """Test successful user authentication."""
        # Mock user service
        auth_service.user_service.authenticate_user.return_value = sample_user

        # Execute
        result = auth_service.authenticate_user("test@example.com", "password123")

        # Assert
        assert result == sample_user
        auth_service.user_service.authenticate_user.assert_called_once_with("test@example.com", "password123")

    def test_authenticate_user_failure(self, auth_service):
        """Test failed user authentication."""
        # Mock user service to return None
        auth_service.user_service.authenticate_user.return_value = None

        # Execute
        result = auth_service.authenticate_user("test@example.com", "wrongpassword")

        # Assert
        assert result is None
        auth_service.user_service.authenticate_user.assert_called_once_with("test@example.com", "wrongpassword")

    def test_authenticate_user_empty_credentials(self, auth_service):
        """Test authentication with empty credentials."""
        # Mock user service to return None for empty credentials
        auth_service.user_service.authenticate_user.return_value = None
        
        # Execute
        result = auth_service.authenticate_user("", "")

        # Assert
        assert result is None
        auth_service.user_service.authenticate_user.assert_called_once_with("", "")

    # Test get_user_by_email method
    def test_get_user_by_email_success(self, auth_service, sample_user):
        """Test successful user retrieval by email."""
        # Mock user service
        auth_service.user_service.get_user_by_email.return_value = sample_user

        # Execute
        result = auth_service.get_user_by_email("test@example.com")

        # Assert
        assert result == sample_user
        auth_service.user_service.get_user_by_email.assert_called_once_with("test@example.com")

    def test_get_user_by_email_not_found(self, auth_service):
        """Test user retrieval by email when user not found."""
        # Mock user service to return None
        auth_service.user_service.get_user_by_email.return_value = None

        # Execute
        result = auth_service.get_user_by_email("nonexistent@example.com")

        # Assert
        assert result is None
        auth_service.user_service.get_user_by_email.assert_called_once_with("nonexistent@example.com")

    def test_get_user_by_email_invalid_format(self, auth_service):
        """Test user retrieval with invalid email format."""
        # Mock user service to return None
        auth_service.user_service.get_user_by_email.return_value = None

        # Execute
        result = auth_service.get_user_by_email("invalid-email")

        # Assert
        assert result is None
        auth_service.user_service.get_user_by_email.assert_called_once_with("invalid-email")

    # Test get_user_by_username method
    def test_get_user_by_username_success(self, auth_service, sample_user):
        """Test successful user retrieval by username."""
        # Mock user service
        auth_service.user_service.get_user_by_username.return_value = sample_user

        # Execute
        result = auth_service.get_user_by_username("testuser")

        # Assert
        assert result == sample_user
        auth_service.user_service.get_user_by_username.assert_called_once_with("testuser")

    def test_get_user_by_username_not_found(self, auth_service):
        """Test user retrieval by username when user not found."""
        # Mock user service to return None
        auth_service.user_service.get_user_by_username.return_value = None

        # Execute
        result = auth_service.get_user_by_username("nonexistentuser")

        # Assert
        assert result is None
        auth_service.user_service.get_user_by_username.assert_called_once_with("nonexistentuser")

    def test_get_user_by_username_empty(self, auth_service):
        """Test user retrieval with empty username."""
        # Mock user service to return None
        auth_service.user_service.get_user_by_username.return_value = None

        # Execute
        result = auth_service.get_user_by_username("")

        # Assert
        assert result is None
        auth_service.user_service.get_user_by_username.assert_called_once_with("")

    # Test update_user_profile method
    def test_update_user_profile_success(self, auth_service, sample_user, sample_user_update):
        """Test successful user profile update."""
        # Mock user service
        auth_service.user_service.get_user_by_id.return_value = sample_user
        auth_service.user_service.update_user.return_value = sample_user

        # Execute
        result = auth_service.update_user_profile("user-123", sample_user_update)

        # Assert
        assert result == sample_user
        auth_service.user_service.get_user_by_id.assert_called_once_with("user-123")
        auth_service.user_service.update_user.assert_called_once_with("user-123", sample_user_update, sample_user)

    def test_update_user_profile_user_not_found(self, auth_service, sample_user_update):
        """Test user profile update when user not found."""
        # Mock user service to return None
        auth_service.user_service.get_user_by_id.return_value = None

        # Execute and assert
        with pytest.raises(ValueError, match="User not found"):
            auth_service.update_user_profile("nonexistent-user", sample_user_update)

        auth_service.user_service.get_user_by_id.assert_called_once_with("nonexistent-user")
        auth_service.user_service.update_user.assert_not_called()

    def test_update_user_profile_partial_update(self, auth_service, sample_user):
        """Test user profile update with partial data."""
        # Mock user service
        auth_service.user_service.get_user_by_id.return_value = sample_user
        auth_service.user_service.update_user.return_value = sample_user

        # Create partial update
        partial_update = UserUpdate(first_name="NewName")

        # Execute
        result = auth_service.update_user_profile("user-123", partial_update)

        # Assert
        assert result == sample_user
        auth_service.user_service.get_user_by_id.assert_called_once_with("user-123")
        auth_service.user_service.update_user.assert_called_once_with("user-123", partial_update, sample_user)

    # Test change_password method
    def test_change_password_success(self, auth_service, sample_user):
        """Test successful password change."""
        # Mock user service and security functions
        auth_service.user_service.get_user_by_id.return_value = sample_user
        
        with patch('backend.app.services.auth_service.verify_password') as mock_verify:
            with patch('backend.app.services.auth_service.get_password_hash') as mock_hash:
                mock_verify.return_value = True
                mock_hash.return_value = "new_hashed_password"

                # Execute
                result = auth_service.change_password("user-123", "oldpassword", "newpassword")

                # Assert
                assert result is True
                assert sample_user.hashed_password == "new_hashed_password"
                auth_service.db_session.commit.assert_called_once()
                mock_verify.assert_called_once_with("oldpassword", "hashed_password_123")
                mock_hash.assert_called_once_with("newpassword")

    def test_change_password_user_not_found(self, auth_service):
        """Test password change when user not found."""
        # Mock user service to return None
        auth_service.user_service.get_user_by_id.return_value = None

        # Execute and assert
        with pytest.raises(ValueError, match="User not found"):
            auth_service.change_password("nonexistent-user", "oldpassword", "newpassword")

        auth_service.user_service.get_user_by_id.assert_called_once_with("nonexistent-user")
        auth_service.db_session.commit.assert_not_called()

    def test_change_password_incorrect_current_password(self, auth_service, sample_user):
        """Test password change with incorrect current password."""
        # Mock user service
        auth_service.user_service.get_user_by_id.return_value = sample_user
        
        with patch('backend.app.services.auth_service.verify_password') as mock_verify:
            mock_verify.return_value = False

            # Execute and assert
            with pytest.raises(ValueError, match="Current password is incorrect"):
                auth_service.change_password("user-123", "wrongpassword", "newpassword")

            mock_verify.assert_called_once_with("wrongpassword", sample_user.hashed_password)
            auth_service.db_session.commit.assert_not_called()

    def test_change_password_weak_new_password(self, auth_service, sample_user):
        """Test password change with weak new password."""
        # Mock user service
        auth_service.user_service.get_user_by_id.return_value = sample_user
        
        with patch('backend.app.services.auth_service.verify_password') as mock_verify:
            mock_verify.return_value = True

            # Execute with weak password
            result = auth_service.change_password("user-123", "oldpassword", "123")

            # Assert - should still work as validation is handled elsewhere
            assert result is True

    # Test deactivate_user method
    def test_deactivate_user_success(self, auth_service, sample_user):
        """Test successful user deactivation."""
        # Mock user service
        auth_service.user_service.get_user_by_id.return_value = sample_user

        # Execute
        result = auth_service.deactivate_user("user-123")

        # Assert
        assert result is True
        assert sample_user.is_active is False
        auth_service.user_service.get_user_by_id.assert_called_once_with("user-123")
        auth_service.db_session.commit.assert_called_once()

    def test_deactivate_user_not_found(self, auth_service):
        """Test user deactivation when user not found."""
        # Mock user service to return None
        auth_service.user_service.get_user_by_id.return_value = None

        # Execute and assert
        with pytest.raises(ValueError, match="User not found"):
            auth_service.deactivate_user("nonexistent-user")

        auth_service.user_service.get_user_by_id.assert_called_once_with("nonexistent-user")
        auth_service.db_session.commit.assert_not_called()

    def test_deactivate_user_already_inactive(self, auth_service, sample_user):
        """Test deactivation of already inactive user."""
        # Set user as inactive
        sample_user.is_active = False
        
        # Mock user service
        auth_service.user_service.get_user_by_id.return_value = sample_user

        # Execute
        result = auth_service.deactivate_user("user-123")

        # Assert
        assert result is True
        assert sample_user.is_active is False
        auth_service.user_service.get_user_by_id.assert_called_once_with("user-123")
        auth_service.db_session.commit.assert_called_once()

    # Test activate_user method
    def test_activate_user_success(self, auth_service, sample_user):
        """Test successful user activation."""
        # Set user as inactive
        sample_user.is_active = False
        
        # Mock user service
        auth_service.user_service.get_user_by_id.return_value = sample_user

        # Execute
        result = auth_service.activate_user("user-123")

        # Assert
        assert result is True
        assert sample_user.is_active is True
        auth_service.user_service.get_user_by_id.assert_called_once_with("user-123")
        auth_service.db_session.commit.assert_called_once()

    def test_activate_user_not_found(self, auth_service):
        """Test user activation when user not found."""
        # Mock user service to return None
        auth_service.user_service.get_user_by_id.return_value = None

        # Execute and assert
        with pytest.raises(ValueError, match="User not found"):
            auth_service.activate_user("nonexistent-user")

        auth_service.user_service.get_user_by_id.assert_called_once_with("nonexistent-user")
        auth_service.db_session.commit.assert_not_called()

    def test_activate_user_already_active(self, auth_service, sample_user):
        """Test activation of already active user."""
        # Ensure user is active
        sample_user.is_active = True
        
        # Mock user service
        auth_service.user_service.get_user_by_id.return_value = sample_user

        # Execute
        result = auth_service.activate_user("user-123")

        # Assert
        assert result is True
        assert sample_user.is_active is True
        auth_service.user_service.get_user_by_id.assert_called_once_with("user-123")
        auth_service.db_session.commit.assert_called_once()

    # Test edge cases and error conditions
    def test_auth_service_initialization(self, mock_db_session):
        """Test AuthService initialization."""
        with patch('backend.app.services.auth_service.UserService') as mock_user_service_class:
            mock_user_service = Mock()
            mock_user_service_class.return_value = mock_user_service
            
            # Execute
            service = AuthService(mock_db_session)
            
            # Assert
            assert service.db_session == mock_db_session
            assert service.user_service == mock_user_service
            mock_user_service_class.assert_called_once_with(mock_db_session)

    def test_register_user_with_none_values(self, auth_service):
        """Test user registration with None values."""
        user_create = UserCreate(
            email="test@example.com",
            username="testuser",
            password="password123",
            first_name=None,
            last_name=None,
        )
        
        # Mock user service
        auth_service.user_service.get_user_by_email.return_value = None
        auth_service.user_service.get_user_by_username.return_value = None
        auth_service.user_service.create_user.return_value = Mock()

        # Execute
        result = auth_service.register_user(user_create)

        # Assert
        assert result is not None
        auth_service.user_service.create_user.assert_called_once_with(user_data=user_create)

    def test_change_password_with_same_password(self, auth_service, sample_user):
        """Test password change with same password."""
        # Mock user service
        auth_service.user_service.get_user_by_id.return_value = sample_user
        
        with patch('backend.app.services.auth_service.verify_password') as mock_verify:
            with patch('backend.app.services.auth_service.get_password_hash') as mock_hash:
                mock_verify.return_value = True
                mock_hash.return_value = "new_hashed_password"

                # Execute
                result = auth_service.change_password("user-123", "oldpassword", "oldpassword")

                # Assert
                assert result is True
                mock_verify.assert_called_once_with("oldpassword", "hashed_password_123")
                mock_hash.assert_called_once_with("oldpassword")

    def test_database_session_error_handling(self, auth_service, sample_user):
        """Test error handling when database session fails."""
        # Mock user service
        auth_service.user_service.get_user_by_id.return_value = sample_user
        auth_service.db_session.commit.side_effect = Exception("Database error")
        
        with patch('backend.app.services.auth_service.verify_password') as mock_verify:
            mock_verify.return_value = True

            # Execute and assert
            with pytest.raises(Exception, match="Database error"):
                auth_service.change_password("user-123", "oldpassword", "newpassword")

    def test_user_service_integration(self, mock_db_session):
        """Test integration with UserService."""
        with patch('backend.app.services.auth_service.UserService') as mock_user_service_class:
            mock_user_service = Mock()
            mock_user_service_class.return_value = mock_user_service
            
            # Create service
            service = AuthService(mock_db_session)
            
            # Assert UserService was created with correct session
            mock_user_service_class.assert_called_once_with(mock_db_session)
            assert service.user_service == mock_user_service

    # Test performance and concurrency
    def test_multiple_operations_same_user(self, auth_service, sample_user):
        """Test multiple operations on the same user."""
        # Mock user service
        auth_service.user_service.get_user_by_id.return_value = sample_user
        auth_service.user_service.get_user_by_email.return_value = sample_user
        
        with patch('backend.app.services.auth_service.verify_password') as mock_verify:
            with patch('backend.app.services.auth_service.get_password_hash') as mock_hash:
                mock_verify.return_value = True
                mock_hash.return_value = "new_hashed_password"

                # Execute multiple operations
                user1 = auth_service.get_user_by_email("test@example.com")
                auth_service.change_password("user-123", "oldpassword", "newpassword")
                auth_service.deactivate_user("user-123")
                auth_service.activate_user("user-123")

                # Assert
                assert user1 == sample_user
                assert sample_user.is_active is True
                assert auth_service.db_session.commit.call_count == 3

    def test_error_propagation(self, auth_service):
        """Test that errors from UserService are properly propagated."""
        # Mock UserService to raise exceptions
        auth_service.user_service.get_user_by_email.side_effect = Exception("UserService error")
        auth_service.user_service.get_user_by_username.side_effect = Exception("UserService error")
        auth_service.user_service.get_user_by_id.side_effect = Exception("UserService error")

        # Execute and assert
        with pytest.raises(Exception, match="UserService error"):
            auth_service.get_user_by_email("test@example.com")

        with pytest.raises(Exception, match="UserService error"):
            auth_service.get_user_by_username("testuser")

        with pytest.raises(Exception, match="UserService error"):
            auth_service.deactivate_user("user-123")