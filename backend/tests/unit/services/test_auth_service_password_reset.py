"""
Unit tests for AuthService password reset functionality.

This module tests the password reset features added to the AuthService.
"""

from unittest.mock import Mock, patch

import pytest

from backend.app.models.user import User
from backend.app.services.auth_service import AuthService


class TestAuthServicePasswordReset:
    """Test cases for AuthService password reset functionality."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        return Mock()

    @pytest.fixture
    def mock_user_service(self):
        """Create mock user service."""
        return Mock()

    @pytest.fixture
    def sample_user(self):
        """Create sample user for testing."""
        user = User(
            id="test-user-id",
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password",
            language="de"
        )
        return user

    @pytest.fixture
    def auth_service(self, mock_db, mock_user_service):
        """Create AuthService instance for testing."""
        service = AuthService(mock_db)
        service.user_service = mock_user_service
        return service

    @patch('backend.app.services.auth_service.token_service')
    @patch('backend.app.services.auth_service.email_service')
    @patch('backend.app.services.auth_service.get_settings')
    def test_request_password_reset_success(
        self, mock_get_settings, mock_email_service, mock_token_service, 
        auth_service, mock_user_service, sample_user
    ):
        """Test successful password reset request."""
        # Mock settings
        mock_settings = Mock()
        mock_settings.password_reset_base_url = "http://localhost:3000"
        mock_get_settings.return_value = mock_settings
        
        # Mock user service
        mock_user_service.get_user_by_email.return_value = sample_user
        
        # Mock token service
        mock_token_service.create_password_reset_token.return_value = "test_token_123"
        
        # Mock email service
        mock_email_service.send_password_reset_email.return_value = True
        
        # Test password reset request
        result = auth_service.request_password_reset("test@example.com")
        
        assert result is True
        mock_user_service.get_user_by_email.assert_called_once_with("test@example.com")
        mock_token_service.create_password_reset_token.assert_called_once_with(sample_user, mock_db)
        mock_email_service.send_password_reset_email.assert_called_once()

    @patch('backend.app.services.auth_service.token_service')
    @patch('backend.app.services.auth_service.email_service')
    @patch('backend.app.services.auth_service.get_settings')
    def test_request_password_reset_user_not_found(
        self, mock_get_settings, mock_email_service, mock_token_service, 
        auth_service, mock_user_service
    ):
        """Test password reset request for non-existent user."""
        # Mock user service returning None
        mock_user_service.get_user_by_email.return_value = None
        
        # Test password reset request
        with pytest.raises(ValueError, match="User not found"):
            auth_service.request_password_reset("nonexistent@example.com")
        
        mock_user_service.get_user_by_email.assert_called_once_with("nonexistent@example.com")
        mock_token_service.create_password_reset_token.assert_not_called()
        mock_email_service.send_password_reset_email.assert_not_called()

    @patch('backend.app.services.auth_service.token_service')
    @patch('backend.app.services.auth_service.email_service')
    @patch('backend.app.services.auth_service.get_settings')
    def test_request_password_reset_email_failure(
        self, mock_get_settings, mock_email_service, mock_token_service, 
        auth_service, mock_user_service, sample_user
    ):
        """Test password reset request when email sending fails."""
        # Mock settings
        mock_settings = Mock()
        mock_settings.password_reset_base_url = "http://localhost:3000"
        mock_get_settings.return_value = mock_settings
        
        # Mock user service
        mock_user_service.get_user_by_email.return_value = sample_user
        
        # Mock token service
        mock_token_service.create_password_reset_token.return_value = "test_token_123"
        
        # Mock email service returning False
        mock_email_service.send_password_reset_email.return_value = False
        
        # Test password reset request
        result = auth_service.request_password_reset("test@example.com")
        
        assert result is False
        mock_email_service.send_password_reset_email.assert_called_once()

    @patch('backend.app.services.auth_service.token_service')
    @patch('backend.app.services.auth_service.email_service')
    @patch('backend.app.services.auth_service.get_password_hash')
    def test_reset_password_with_token_success(
        self, mock_get_password_hash, mock_email_service, mock_token_service,
        auth_service, mock_user_service, sample_user
    ):
        """Test successful password reset with valid token."""
        # Mock token service
        mock_token_service.validate_password_reset_token.return_value = True
        mock_token_service.get_user_by_reset_token.return_value = sample_user
        mock_token_service.clear_password_reset_token.return_value = None
        
        # Mock password hashing
        mock_get_password_hash.return_value = "new_hashed_password"
        
        # Mock email service
        mock_email_service.send_password_changed_notification.return_value = True
        
        # Test password reset
        result = auth_service.reset_password_with_token("valid_token", "new_password")
        
        assert result is True
        mock_token_service.validate_password_reset_token.assert_called_once_with("valid_token", mock_db)
        mock_token_service.get_user_by_reset_token.assert_called_once_with("valid_token", mock_db)
        mock_token_service.clear_password_reset_token.assert_called_once_with(sample_user, mock_db)
        mock_get_password_hash.assert_called_once_with("new_password")
        mock_email_service.send_password_changed_notification.assert_called_once()

    @patch('backend.app.services.auth_service.token_service')
    def test_reset_password_with_token_invalid(
        self, mock_token_service, auth_service
    ):
        """Test password reset with invalid token."""
        # Mock token service returning False
        mock_token_service.validate_password_reset_token.return_value = False
        
        # Test password reset
        with pytest.raises(ValueError, match="Invalid or expired token"):
            auth_service.reset_password_with_token("invalid_token", "new_password")
        
        mock_token_service.validate_password_reset_token.assert_called_once_with("invalid_token", mock_db)

    @patch('backend.app.services.auth_service.token_service')
    def test_reset_password_with_token_user_not_found(
        self, mock_token_service, auth_service
    ):
        """Test password reset when user not found."""
        # Mock token service
        mock_token_service.validate_password_reset_token.return_value = True
        mock_token_service.get_user_by_reset_token.return_value = None
        
        # Test password reset
        with pytest.raises(ValueError, match="User not found"):
            auth_service.reset_password_with_token("valid_token", "new_password")
        
        mock_token_service.validate_password_reset_token.assert_called_once_with("valid_token", mock_db)
        mock_token_service.get_user_by_reset_token.assert_called_once_with("valid_token", mock_db)

    @patch('backend.app.services.auth_service.token_service')
    def test_validate_reset_token_valid(
        self, mock_token_service, auth_service
    ):
        """Test validation of valid reset token."""
        # Mock token service returning True
        mock_token_service.validate_password_reset_token.return_value = True
        
        # Test validation
        result = auth_service.validate_reset_token("valid_token")
        
        assert result is True
        mock_token_service.validate_password_reset_token.assert_called_once_with("valid_token", mock_db)

    @patch('backend.app.services.auth_service.token_service')
    def test_validate_reset_token_invalid(
        self, mock_token_service, auth_service
    ):
        """Test validation of invalid reset token."""
        # Mock token service returning False
        mock_token_service.validate_password_reset_token.return_value = False
        
        # Test validation
        result = auth_service.validate_reset_token("invalid_token")
        
        assert result is False
        mock_token_service.validate_password_reset_token.assert_called_once_with("invalid_token", mock_db)