"""
Integration tests for password reset security features.

This module tests the integration of rate limiting, CSRF protection,
and audit logging for password reset operations.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from backend.app.main import app
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.models.audit_extended import ExtendedAuditLog


class TestPasswordResetRateLimiting:
    """Test cases for password reset rate limiting integration."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def test_user(self, db_session):
        """Create test user."""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password",
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        return user

    def test_forgot_password_rate_limit_by_ip(self, client, test_user):
        """Test rate limiting by IP address for forgot password."""
        # Make 5 requests (limit)
        for i in range(5):
            response = client.post(
                "/api/v1/auth/forgot-password",
                json={"email": "test@example.com"}
            )
            assert response.status_code == 200
        
        # 6th request should be rate limited
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "test@example.com"}
        )
        assert response.status_code == 429
        assert "Too many password reset requests" in response.json()["detail"]

    def test_forgot_password_rate_limit_by_email(self, client, test_user):
        """Test rate limiting by email address for forgot password."""
        # Make 3 requests (limit)
        for i in range(3):
            response = client.post(
                "/api/v1/auth/forgot-password",
                json={"email": "test@example.com"}
            )
            assert response.status_code == 200
        
        # 4th request should be rate limited
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "test@example.com"}
        )
        assert response.status_code == 429
        assert "Too many password reset requests for this email" in response.json()["detail"]

    def test_forgot_password_rate_limit_case_insensitive(self, client, test_user):
        """Test that email rate limiting is case insensitive."""
        # Make 3 requests with different cases
        emails = ["test@example.com", "TEST@EXAMPLE.COM", "Test@Example.com"]
        
        for email in emails:
            response = client.post(
                "/api/v1/auth/forgot-password",
                json={"email": email}
            )
            assert response.status_code == 200
        
        # 4th request should be rate limited regardless of case
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "test@EXAMPLE.com"}
        )
        assert response.status_code == 429

    def test_forgot_password_rate_limit_different_emails(self, client, test_user):
        """Test that different emails have separate rate limits."""
        # Use up limit for first email
        for i in range(3):
            response = client.post(
                "/api/v1/auth/forgot-password",
                json={"email": "test@example.com"}
            )
            assert response.status_code == 200
        
        # Different email should still be allowed
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "other@example.com"}
        )
        assert response.status_code == 200

    @patch('backend.app.services.email_service.email_service.send_password_reset_email')
    def test_forgot_password_audit_logging(self, mock_send_email, client, test_user, db_session):
        """Test audit logging for forgot password requests."""
        mock_send_email.return_value = True
        
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "test@example.com"}
        )
        assert response.status_code == 200
        
        # Check audit log
        audit_logs = db_session.query(ExtendedAuditLog).filter(
            ExtendedAuditLog.event_type == "password_reset_requested"
        ).all()
        
        assert len(audit_logs) == 1
        audit_log = audit_logs[0]
        assert audit_log.event_category == "authentication"
        assert audit_log.severity == "info"
        assert audit_log.context["email"] == "test@example.com"
        assert audit_log.context["success"] is True

    @patch('backend.app.services.email_service.email_service.send_password_reset_email')
    def test_forgot_password_audit_logging_user_not_found(self, mock_send_email, client, db_session):
        """Test audit logging for forgot password with non-existent user."""
        mock_send_email.return_value = True
        
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "nonexistent@example.com"}
        )
        assert response.status_code == 200
        
        # Check audit log
        audit_logs = db_session.query(ExtendedAuditLog).filter(
            ExtendedAuditLog.event_type == "password_reset_requested"
        ).all()
        
        assert len(audit_logs) == 1
        audit_log = audit_logs[0]
        assert audit_log.context["email"] == "nonexistent@example.com"
        assert audit_log.context["success"] is False
        assert audit_log.context["reason"] == "user_not_found"


class TestPasswordResetCSRFProtection:
    """Test cases for CSRF protection integration."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_csrf_token_generation(self, client):
        """Test CSRF token generation endpoint."""
        response = client.get("/api/v1/auth/csrf-token")
        
        assert response.status_code == 200
        data = response.json()
        assert "csrf_token" in data
        assert "expires_in" in data
        assert "session_id" in data
        assert data["expires_in"] == 30 * 60  # 30 minutes

    def test_csrf_token_generation_with_session_id(self, client):
        """Test CSRF token generation with session ID header."""
        headers = {"X-Session-ID": "test-session-123"}
        response = client.get("/api/v1/auth/csrf-token", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "test-session-123"


class TestPasswordResetAuditLogging:
    """Test cases for password reset audit logging."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def test_user_with_token(self, db_session):
        """Create test user with password reset token."""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password",
            is_active=True,
            password_reset_token="valid-token-123",
            password_reset_expires_at="2024-12-31T23:59:59Z"
        )
        db_session.add(user)
        db_session.commit()
        return user

    @patch('backend.app.services.email_service.email_service.send_password_changed_notification')
    def test_reset_password_audit_logging_success(self, mock_send_notification, client, test_user_with_token, db_session):
        """Test audit logging for successful password reset."""
        mock_send_notification.return_value = True
        
        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": "valid-token-123",
                "new_password": "NewPassword123!"
            }
        )
        
        # Check audit log for successful reset
        audit_logs = db_session.query(ExtendedAuditLog).filter(
            ExtendedAuditLog.event_type == "password_reset_completed"
        ).all()
        
        assert len(audit_logs) == 1
        audit_log = audit_logs[0]
        assert audit_log.event_category == "authentication"
        assert audit_log.severity == "info"
        assert audit_log.context["success"] is True

    def test_reset_password_audit_logging_failure(self, client, db_session):
        """Test audit logging for failed password reset."""
        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": "invalid-token",
                "new_password": "NewPassword123!"
            }
        )
        
        assert response.status_code == 400
        
        # Check audit log for failed reset
        audit_logs = db_session.query(ExtendedAuditLog).filter(
            ExtendedAuditLog.event_type == "password_reset_failed"
        ).all()
        
        assert len(audit_logs) == 1
        audit_log = audit_logs[0]
        assert audit_log.event_category == "authentication"
        assert audit_log.severity == "warning"
        assert audit_log.context["success"] is False
        assert audit_log.context["token_provided"] is True


class TestPasswordResetSecurityHeaders:
    """Test cases for security headers in password reset endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_forgot_password_security_headers(self, client):
        """Test security headers for forgot password endpoint."""
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "test@example.com"}
        )
        
        # Check for security headers
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "X-XSS-Protection" in response.headers

    def test_reset_password_security_headers(self, client):
        """Test security headers for reset password endpoint."""
        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": "test-token",
                "new_password": "NewPassword123!"
            }
        )
        
        # Check for security headers
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "X-XSS-Protection" in response.headers

    def test_csrf_token_security_headers(self, client):
        """Test security headers for CSRF token endpoint."""
        response = client.get("/api/v1/auth/csrf-token")
        
        # Check for security headers
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "X-XSS-Protection" in response.headers