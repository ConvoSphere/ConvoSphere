"""
Integration tests for password reset API endpoints.

This module tests the password reset endpoints with a real database.
"""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from backend.app.core.security import get_password_hash
from backend.app.main import app
from backend.app.models.user import User


class TestPasswordResetEndpoints:
    """Test cases for password reset API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def sample_user(self, db_session):
        """Create sample user in database."""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("oldpassword"),
            language="de",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    def test_forgot_password_success(self, client, sample_user):
        """Test successful password reset request."""
        with patch(
            "backend.app.services.email_service.email_service.send_password_reset_email"
        ) as mock_send_email:
            mock_send_email.return_value = True

            response = client.post(
                "/api/v1/auth/forgot-password", json={"email": "test@example.com"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "password reset link has been sent" in data["message"]

            # Verify email was sent
            mock_send_email.assert_called_once()

    def test_forgot_password_user_not_found(self, client):
        """Test password reset request for non-existent user."""
        response = client.post(
            "/api/v1/auth/forgot-password", json={"email": "nonexistent@example.com"}
        )

        # Should still return success for security reasons
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "password reset link has been sent" in data["message"]

    def test_forgot_password_invalid_email(self, client):
        """Test password reset request with invalid email format."""
        response = client.post(
            "/api/v1/auth/forgot-password", json={"email": "invalid-email"}
        )

        assert response.status_code == 422  # Validation error

    def test_reset_password_success(self, client, sample_user, db_session):
        """Test successful password reset with valid token."""
        # First, create a password reset token
        from backend.app.services.token_service import token_service

        token = token_service.create_password_reset_token(sample_user, db_session)

        # Reset password
        response = client.post(
            "/api/v1/auth/reset-password",
            json={"token": token, "new_password": "newpassword123"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["message"] == "Password reset successfully"

        # Verify password was changed
        db_session.refresh(sample_user)
        from backend.app.core.security import verify_password

        assert verify_password("newpassword123", sample_user.hashed_password)

        # Verify token was cleared
        assert sample_user.password_reset_token is None
        assert sample_user.password_reset_expires_at is None

    def test_reset_password_invalid_token(self, client):
        """Test password reset with invalid token."""
        response = client.post(
            "/api/v1/auth/reset-password",
            json={"token": "invalid_token", "new_password": "newpassword123"},
        )

        assert response.status_code == 400
        data = response.json()
        assert "Invalid or expired token" in data["detail"]

    def test_reset_password_expired_token(self, client, sample_user, db_session):
        """Test password reset with expired token."""
        # Create an expired token
        from datetime import datetime, timedelta

        sample_user.password_reset_token = "expired_token"
        sample_user.password_reset_expires_at = datetime.utcnow() - timedelta(hours=1)
        db_session.commit()

        response = client.post(
            "/api/v1/auth/reset-password",
            json={"token": "expired_token", "new_password": "newpassword123"},
        )

        assert response.status_code == 400
        data = response.json()
        assert "Invalid or expired token" in data["detail"]

    def test_reset_password_weak_password(self, client, sample_user, db_session):
        """Test password reset with weak password."""
        # Create a valid token
        from backend.app.services.token_service import token_service

        token = token_service.create_password_reset_token(sample_user, db_session)

        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": token,
                "new_password": "123",  # Too short
            },
        )

        assert response.status_code == 422  # Validation error

    def test_validate_reset_token_valid(self, client, sample_user, db_session):
        """Test validation of valid reset token."""
        # Create a valid token
        from backend.app.services.token_service import token_service

        token = token_service.create_password_reset_token(sample_user, db_session)

        response = client.post(
            "/api/v1/auth/validate-reset-token", json={"token": token}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["message"] == "Token is valid"

    def test_validate_reset_token_invalid(self, client):
        """Test validation of invalid reset token."""
        response = client.post(
            "/api/v1/auth/validate-reset-token", json={"token": "invalid_token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert data["message"] == "Token is invalid or expired"

    def test_validate_reset_token_expired(self, client, sample_user, db_session):
        """Test validation of expired reset token."""
        # Create an expired token
        from datetime import datetime, timedelta

        sample_user.password_reset_token = "expired_token"
        sample_user.password_reset_expires_at = datetime.utcnow() - timedelta(hours=1)
        db_session.commit()

        response = client.post(
            "/api/v1/auth/validate-reset-token", json={"token": "expired_token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert data["message"] == "Token is invalid or expired"

    def test_reset_password_token_reuse(self, client, sample_user, db_session):
        """Test that reset token can only be used once."""
        # Create a valid token
        from backend.app.services.token_service import token_service

        token = token_service.create_password_reset_token(sample_user, db_session)

        # Use token first time
        response1 = client.post(
            "/api/v1/auth/reset-password",
            json={"token": token, "new_password": "newpassword123"},
        )

        assert response1.status_code == 200

        # Try to use same token again
        response2 = client.post(
            "/api/v1/auth/reset-password",
            json={"token": token, "new_password": "anotherpassword123"},
        )

        assert response2.status_code == 400
        data = response2.json()
        assert "Invalid or expired token" in data["detail"]
