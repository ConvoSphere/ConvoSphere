"""
Unit tests for TokenService.

This module tests the token service functionality for password reset operations.
"""

from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

from backend.app.models.user import User
from backend.app.services.token_service import TokenService


class TestTokenService:
    """Test cases for TokenService."""

    @pytest.fixture
    def token_service(self):
        """Create TokenService instance for testing."""
        return TokenService()

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        return Mock()

    @pytest.fixture
    def sample_user(self):
        """Create sample user for testing."""
        user = User(
            id="test-user-id",
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password",
        )
        return user

    def test_generate_password_reset_token(self, token_service):
        """Test password reset token generation."""
        token = token_service.generate_password_reset_token()

        assert token is not None
        assert len(token) == 32
        assert token.isalnum()  # Should only contain letters and numbers

    def test_generate_password_reset_token_unique(self, token_service):
        """Test that generated tokens are unique."""
        tokens = set()
        for _ in range(100):
            token = token_service.generate_password_reset_token()
            tokens.add(token)

        assert len(tokens) == 100  # All tokens should be unique

    def test_validate_password_reset_token_valid(
        self, token_service, mock_db, sample_user
    ):
        """Test validation of valid password reset token."""
        # Set up user with valid token
        sample_user.password_reset_token = "valid_token_123"
        sample_user.password_reset_expires_at = datetime.utcnow() + timedelta(hours=1)

        # Mock database query
        mock_db.query.return_value.filter.return_value.first.return_value = sample_user

        # Test validation
        result = token_service.validate_password_reset_token("valid_token_123", mock_db)

        assert result is True

    def test_validate_password_reset_token_invalid(self, token_service, mock_db):
        """Test validation of invalid password reset token."""
        # Mock database query returning None
        mock_db.query.return_value.filter.return_value.first.return_value = None

        # Test validation
        result = token_service.validate_password_reset_token("invalid_token", mock_db)

        assert result is False

    def test_validate_password_reset_token_expired(
        self, token_service, mock_db, sample_user
    ):
        """Test validation of expired password reset token."""
        # Set up user with expired token
        sample_user.password_reset_token = "expired_token_123"
        sample_user.password_reset_expires_at = datetime.utcnow() - timedelta(hours=1)

        # Mock database query
        mock_db.query.return_value.filter.return_value.first.return_value = sample_user

        # Test validation
        result = token_service.validate_password_reset_token(
            "expired_token_123", mock_db
        )

        assert result is False

    def test_validate_password_reset_token_empty(self, token_service, mock_db):
        """Test validation of empty token."""
        result = token_service.validate_password_reset_token("", mock_db)
        assert result is False

        result = token_service.validate_password_reset_token(None, mock_db)
        assert result is False

    def test_get_user_by_reset_token(self, token_service, mock_db, sample_user):
        """Test getting user by reset token."""
        # Mock database query
        mock_db.query.return_value.filter.return_value.first.return_value = sample_user

        # Test getting user
        result = token_service.get_user_by_reset_token("test_token", mock_db)

        assert result == sample_user

    def test_get_user_by_reset_token_not_found(self, token_service, mock_db):
        """Test getting user by non-existent reset token."""
        # Mock database query returning None
        mock_db.query.return_value.filter.return_value.first.return_value = None

        # Test getting user
        result = token_service.get_user_by_reset_token("non_existent_token", mock_db)

        assert result is None

    def test_create_password_reset_token(self, token_service, mock_db, sample_user):
        """Test creating password reset token for user."""
        # Mock database commit
        mock_db.commit.return_value = None

        # Test creating token
        token = token_service.create_password_reset_token(sample_user, mock_db)

        assert token is not None
        assert len(token) == 32
        assert sample_user.password_reset_token == token
        assert sample_user.password_reset_expires_at is not None
        assert sample_user.password_reset_expires_at > datetime.utcnow()
        mock_db.commit.assert_called_once()

    def test_clear_password_reset_token(self, token_service, mock_db, sample_user):
        """Test clearing password reset token for user."""
        # Set up user with token
        sample_user.password_reset_token = "test_token"
        sample_user.password_reset_expires_at = datetime.utcnow() + timedelta(hours=1)

        # Mock database commit
        mock_db.commit.return_value = None

        # Test clearing token
        token_service.clear_password_reset_token(sample_user, mock_db)

        assert sample_user.password_reset_token is None
        assert sample_user.password_reset_expires_at is None
        mock_db.commit.assert_called_once()

    def test_cleanup_expired_tokens(self, token_service, mock_db):
        """Test cleanup of expired tokens."""
        # Create users with expired tokens
        expired_user1 = User(
            id="user1",
            email="user1@example.com",
            username="user1",
            password_reset_token="expired_token1",
            password_reset_expires_at=datetime.utcnow() - timedelta(hours=1),
        )
        expired_user2 = User(
            id="user2",
            email="user2@example.com",
            username="user2",
            password_reset_token="expired_token2",
            password_reset_expires_at=datetime.utcnow() - timedelta(hours=2),
        )

        # Mock database query
        mock_db.query.return_value.filter.return_value.all.return_value = [
            expired_user1,
            expired_user2,
        ]
        mock_db.commit.return_value = None

        # Test cleanup
        count = token_service.cleanup_expired_tokens(mock_db)

        assert count == 2
        assert expired_user1.password_reset_token is None
        assert expired_user1.password_reset_expires_at is None
        assert expired_user2.password_reset_token is None
        assert expired_user2.password_reset_expires_at is None
        mock_db.commit.assert_called_once()

    def test_cleanup_expired_tokens_none(self, token_service, mock_db):
        """Test cleanup when no expired tokens exist."""
        # Mock database query returning empty list
        mock_db.query.return_value.filter.return_value.all.return_value = []

        # Test cleanup
        count = token_service.cleanup_expired_tokens(mock_db)

        assert count == 0
        mock_db.commit.assert_not_called()
