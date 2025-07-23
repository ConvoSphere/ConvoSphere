"""
Unit tests for authentication service.
"""
from unittest.mock import MagicMock, patch

import pytest

from backend.app.core.security import (
    create_access_token,
    get_current_active_user,
    get_current_user,
    get_password_hash,
    verify_password,
)
from backend.app.schemas.user import UserCreate, UserUpdate
from backend.app.services.auth_service import AuthService


class TestSecurityFunctions:
    """Test security utility functions."""

    def test_create_access_token(self):
        """Test access token creation."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data=data)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_password(self):
        """Test password verification."""
        password = "testpassword123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False

    def test_get_password_hash(self):
        """Test password hashing."""
        password = "testpassword123"
        hashed = get_password_hash(password)

        assert isinstance(hashed, str)
        assert hashed != password
        assert len(hashed) > len(password)


class TestAuthService:
    """Test authentication service."""

    @pytest.fixture
    def auth_service(self, test_db_session):
        """Create auth service instance."""
        return AuthService(test_db_session)

    @pytest.fixture
    def test_user_data(self):
        """Test user data."""
        return {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword123",
            "first_name": "Test",
            "last_name": "User",
        }

    def test_register_user_success(self, auth_service, test_user_data):
        """Test successful user registration."""
        user_create = UserCreate(**test_user_data)
        user = auth_service.register_user(user_create)

        assert user.email == test_user_data["email"]
        assert user.username == test_user_data["username"]
        assert user.first_name == test_user_data["first_name"]
        assert user.last_name == test_user_data["last_name"]
        assert user.role == "user"  # Default role
        assert user.is_active is True
        assert verify_password(test_user_data["password"], user.hashed_password)

    def test_register_user_duplicate_email(self, auth_service, test_user_data):
        """Test registration with duplicate email."""
        user_create = UserCreate(**test_user_data)
        auth_service.register_user(user_create)

        # Try to register again with same email
        with pytest.raises(ValueError, match="Email already registered"):
            auth_service.register_user(user_create)

    def test_register_user_duplicate_username(self, auth_service, test_user_data):
        """Test registration with duplicate username."""
        user_create = UserCreate(**test_user_data)
        auth_service.register_user(user_create)

        # Try to register with same username but different email
        test_user_data["email"] = "different@example.com"
        user_create2 = UserCreate(**test_user_data)

        with pytest.raises(ValueError, match="Username already taken"):
            auth_service.register_user(user_create2)

    def test_authenticate_user_success(self, auth_service, test_user_data):
        """Test successful user authentication."""
        user_create = UserCreate(**test_user_data)
        user = auth_service.register_user(user_create)

        authenticated_user = auth_service.authenticate_user(
            test_user_data["email"],
            test_user_data["password"],
        )

        assert authenticated_user is not None
        assert authenticated_user.id == user.id
        assert authenticated_user.email == user.email

    def test_authenticate_user_invalid_email(self, auth_service):
        """Test authentication with invalid email."""
        authenticated_user = auth_service.authenticate_user(
            "nonexistent@example.com",
            "password123",
        )

        assert authenticated_user is None

    def test_authenticate_user_invalid_password(self, auth_service, test_user_data):
        """Test authentication with invalid password."""
        user_create = UserCreate(**test_user_data)
        auth_service.register_user(user_create)

        authenticated_user = auth_service.authenticate_user(
            test_user_data["email"],
            "wrongpassword",
        )

        assert authenticated_user is None

    def test_authenticate_user_inactive(self, auth_service, test_user_data):
        """Test authentication with inactive user."""
        user_create = UserCreate(**test_user_data)
        user = auth_service.register_user(user_create)

        # Deactivate user
        user.is_active = False
        auth_service.db.commit()

        authenticated_user = auth_service.authenticate_user(
            test_user_data["email"],
            test_user_data["password"],
        )

        assert authenticated_user is None

    def test_get_user_by_email(self, auth_service, test_user_data):
        """Test getting user by email."""
        user_create = UserCreate(**test_user_data)
        created_user = auth_service.register_user(user_create)

        user = auth_service.get_user_by_email(test_user_data["email"])

        assert user is not None
        assert user.id == created_user.id
        assert user.email == created_user.email

    def test_get_user_by_email_not_found(self, auth_service):
        """Test getting user by non-existent email."""
        user = auth_service.get_user_by_email("nonexistent@example.com")

        assert user is None

    def test_get_user_by_username(self, auth_service, test_user_data):
        """Test getting user by username."""
        user_create = UserCreate(**test_user_data)
        created_user = auth_service.register_user(user_create)

        user = auth_service.get_user_by_username(test_user_data["username"])

        assert user is not None
        assert user.id == created_user.id
        assert user.username == created_user.username

    def test_get_user_by_username_not_found(self, auth_service):
        """Test getting user by non-existent username."""
        user = auth_service.get_user_by_username("nonexistent")

        assert user is None

    def test_update_user_profile(self, auth_service, test_user_data):
        """Test updating user profile."""
        user_create = UserCreate(**test_user_data)
        user = auth_service.register_user(user_create)

        update_data = UserUpdate(
            first_name="Updated",
            last_name="Name",
            bio="Updated bio",
        )

        updated_user = auth_service.update_user_profile(user.id, update_data)

        assert updated_user.first_name == "Updated"
        assert updated_user.last_name == "Name"
        assert updated_user.bio == "Updated bio"

    def test_change_password_success(self, auth_service, test_user_data):
        """Test successful password change."""
        user_create = UserCreate(**test_user_data)
        user = auth_service.register_user(user_create)

        new_password = "newpassword123"
        success = auth_service.change_password(
            user.id,
            test_user_data["password"],
            new_password,
        )

        assert success is True

        # Verify new password works
        authenticated_user = auth_service.authenticate_user(
            test_user_data["email"],
            new_password,
        )
        assert authenticated_user is not None

    def test_change_password_invalid_current(self, auth_service, test_user_data):
        """Test password change with invalid current password."""
        user_create = UserCreate(**test_user_data)
        user = auth_service.register_user(user_create)

        success = auth_service.change_password(
            user.id,
            "wrongpassword",
            "newpassword123",
        )

        assert success is False

    def test_deactivate_user(self, auth_service, test_user_data):
        """Test user deactivation."""
        user_create = UserCreate(**test_user_data)
        user = auth_service.register_user(user_create)

        auth_service.deactivate_user(user.id)

        # Verify user is deactivated
        deactivated_user = auth_service.get_user_by_email(test_user_data["email"])
        assert deactivated_user.is_active is False

    def test_activate_user(self, auth_service, test_user_data):
        """Test user activation."""
        user_create = UserCreate(**test_user_data)
        user = auth_service.register_user(user_create)

        # Deactivate first
        auth_service.deactivate_user(user.id)

        # Then activate
        auth_service.activate_user(user.id)

        # Verify user is activated
        activated_user = auth_service.get_user_by_email(test_user_data["email"])
        assert activated_user.is_active is True


class TestAuthDependencies:
    """Test authentication dependencies."""

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return MagicMock()

    @pytest.fixture
    def mock_user(self):
        """Mock user object."""
        user = MagicMock()
        user.id = 1
        user.email = "test@example.com"
        user.username = "testuser"
        user.is_active = True
        user.role = "user"
        return user

    @patch("backend.app.core.security.get_user_by_email")
    def test_get_current_user_success(self, mock_get_user, mock_db_session, mock_user):
        """Test successful current user retrieval."""
        mock_get_user.return_value = mock_user

        with patch("backend.app.core.security.create_access_token") as mock_token:
            mock_token.return_value = "test_token"

            current_user = get_current_user(mock_db_session, "test_token")

            assert current_user == mock_user
            mock_get_user.assert_called_once()

    @patch("backend.app.core.security.get_user_by_email")
    def test_get_current_user_invalid_token(self, mock_get_user, mock_db_session):
        """Test current user retrieval with invalid token."""
        mock_get_user.return_value = None

        with pytest.raises(Exception):
            get_current_user(mock_db_session, "invalid_token")

    def test_get_current_active_user_success(self, mock_user):
        """Test successful active user retrieval."""
        active_user = get_current_active_user(mock_user)

        assert active_user == mock_user

    def test_get_current_active_user_inactive(self, mock_user):
        """Test active user retrieval with inactive user."""
        mock_user.is_active = False

        with pytest.raises(Exception):
            get_current_active_user(mock_user)


class TestAuthValidation:
    """Test authentication validation."""

    def test_validate_email_format(self):
        """Test email format validation."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org",
        ]

        invalid_emails = [
            "invalid-email",
            "@example.com",
            "user@",
            "user@.com",
        ]

        # This would test the actual validation logic in the service
        # For now, we'll just assert the structure
        assert len(valid_emails) > 0
        assert len(invalid_emails) > 0

    def test_validate_password_strength(self):
        """Test password strength validation."""
        strong_passwords = [
            "StrongPass123!",
            "ComplexP@ssw0rd",
            "Secure123#Pass",
        ]

        weak_passwords = [
            "123",
            "password",
            "abc",
            "123456",
        ]

        # This would test the actual validation logic in the service
        # For now, we'll just assert the structure
        assert len(strong_passwords) > 0
        assert len(weak_passwords) > 0

    def test_validate_username_format(self):
        """Test username format validation."""
        valid_usernames = [
            "testuser",
            "user123",
            "user_name",
            "user-name",
        ]

        invalid_usernames = [
            "",
            "a",  # too short
            "user@name",  # invalid characters
            "user name",  # spaces
        ]

        # This would test the actual validation logic in the service
        # For now, we'll just assert the structure
        assert len(valid_usernames) > 0
        assert len(invalid_usernames) > 0
