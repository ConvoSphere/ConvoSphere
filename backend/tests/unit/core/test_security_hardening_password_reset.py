"""
Unit tests for password reset security features.

This module tests the security hardening functionality
for password reset operations.
"""

import time
from unittest.mock import patch

import pytest

from backend.app.core.csrf_protection import CSRFProtection
from backend.app.core.security_hardening import SSOSecurityValidator


class TestPasswordResetRateLimiting:
    """Test cases for password reset rate limiting."""

    @pytest.fixture
    def security_validator(self):
        """Create SSOSecurityValidator instance for testing."""
        return SSOSecurityValidator()

    def test_rate_limit_password_reset_by_ip(self, security_validator):
        """Test rate limiting by IP address."""
        ip_address = "192.168.1.1"
        
        # First 5 requests should be allowed
        for i in range(5):
            assert security_validator.rate_limit_password_reset_by_ip(ip_address) is True
        
        # 6th request should be blocked
        assert security_validator.rate_limit_password_reset_by_ip(ip_address) is False

    def test_rate_limit_password_reset_by_email(self, security_validator):
        """Test rate limiting by email address."""
        email = "test@example.com"
        
        # First 3 requests should be allowed
        for i in range(3):
            assert security_validator.rate_limit_password_reset_by_email(email) is True
        
        # 4th request should be blocked
        assert security_validator.rate_limit_password_reset_by_email(email) is False

    def test_rate_limit_password_reset_case_insensitive(self, security_validator):
        """Test that email rate limiting is case insensitive."""
        email1 = "test@example.com"
        email2 = "TEST@EXAMPLE.COM"
        
        # Use up the limit with one case
        for i in range(3):
            assert security_validator.rate_limit_password_reset_by_email(email1) is True
        
        # Should be blocked with different case
        assert security_validator.rate_limit_password_reset_by_email(email2) is False

    def test_rate_limit_password_reset_window_expiry(self, security_validator):
        """Test that rate limits reset after the time window."""
        ip_address = "192.168.1.1"
        
        # Use up the limit
        for i in range(5):
            assert security_validator.rate_limit_password_reset_by_ip(ip_address) is True
        
        # Should be blocked
        assert security_validator.rate_limit_password_reset_by_ip(ip_address) is False
        
        # Mock time to advance beyond the window
        with patch('time.time') as mock_time:
            mock_time.return_value = time.time() + 3601  # 1 hour + 1 second
            
            # Should be allowed again
            assert security_validator.rate_limit_password_reset_by_ip(ip_address) is True

    def test_rate_limit_password_reset_different_identifiers(self, security_validator):
        """Test that different identifiers have separate rate limits."""
        ip1 = "192.168.1.1"
        ip2 = "192.168.1.2"
        email1 = "test1@example.com"
        email2 = "test2@example.com"
        
        # Use up limits for first identifiers
        for i in range(5):
            assert security_validator.rate_limit_password_reset_by_ip(ip1) is True
        
        for i in range(3):
            assert security_validator.rate_limit_password_reset_by_email(email1) is True
        
        # Second identifiers should still be allowed
        assert security_validator.rate_limit_password_reset_by_ip(ip2) is True
        assert security_validator.rate_limit_password_reset_by_email(email2) is True

    def test_rate_limit_password_reset_custom_limits(self, security_validator):
        """Test rate limiting with custom limits."""
        ip_address = "192.168.1.1"
        
        # Test with custom limits
        for i in range(10):
            assert security_validator.rate_limit_password_reset_by_ip(ip_address, max_requests=10) is True
        
        # 11th request should be blocked
        assert security_validator.rate_limit_password_reset_by_ip(ip_address, max_requests=10) is False


class TestCSRFProtection:
    """Test cases for CSRF protection."""

    @pytest.fixture
    def csrf_protection(self):
        """Create CSRFProtection instance for testing."""
        return CSRFProtection()

    def test_generate_csrf_token(self, csrf_protection):
        """Test CSRF token generation."""
        token = csrf_protection.generate_csrf_token()
        
        assert token is not None
        assert len(token) > 20  # Should be reasonably long
        assert token in csrf_protection.token_cache

    def test_generate_csrf_token_with_session(self, csrf_protection):
        """Test CSRF token generation with session ID."""
        session_id = "test-session-123"
        token = csrf_protection.generate_csrf_token(session_id)
        
        assert token is not None
        assert csrf_protection.token_cache[token]["session_id"] == session_id

    def test_validate_csrf_token_valid(self, csrf_protection):
        """Test validation of valid CSRF token."""
        token = csrf_protection.generate_csrf_token()
        
        assert csrf_protection.validate_csrf_token(token) is True

    def test_validate_csrf_token_invalid(self, csrf_protection):
        """Test validation of invalid CSRF token."""
        assert csrf_protection.validate_csrf_token("invalid-token") is False

    def test_validate_csrf_token_empty(self, csrf_protection):
        """Test validation of empty CSRF token."""
        assert csrf_protection.validate_csrf_token("") is False
        assert csrf_protection.validate_csrf_token(None) is False

    def test_validate_csrf_token_expired(self, csrf_protection):
        """Test validation of expired CSRF token."""
        token = csrf_protection.generate_csrf_token()
        
        # Mock time to advance beyond expiration
        with patch('time.time') as mock_time:
            mock_time.return_value = time.time() + (31 * 60)  # 31 minutes (expires at 30)
            
            assert csrf_protection.validate_csrf_token(token) is False

    def test_validate_csrf_token_session_mismatch(self, csrf_protection):
        """Test validation with session ID mismatch."""
        session_id = "test-session-123"
        token = csrf_protection.generate_csrf_token(session_id)
        
        # Should fail with different session ID
        assert csrf_protection.validate_csrf_token(token, "different-session") is False
        
        # Should pass with correct session ID
        assert csrf_protection.validate_csrf_token(token, session_id) is True

    def test_consume_csrf_token(self, csrf_protection):
        """Test consuming a CSRF token."""
        token = csrf_protection.generate_csrf_token()
        
        # Should be valid before consumption
        assert csrf_protection.validate_csrf_token(token) is True
        
        # Should be consumed successfully
        assert csrf_protection.consume_csrf_token(token) is True
        
        # Should be invalid after consumption
        assert csrf_protection.validate_csrf_token(token) is False

    def test_consume_csrf_token_invalid(self, csrf_protection):
        """Test consuming an invalid CSRF token."""
        assert csrf_protection.consume_csrf_token("invalid-token") is False

    def test_cleanup_expired_tokens(self, csrf_protection):
        """Test cleanup of expired tokens."""
        # Generate some tokens
        token1 = csrf_protection.generate_csrf_token()
        csrf_protection.generate_csrf_token()
        
        # Mock time to expire one token
        with patch('time.time') as mock_time:
            mock_time.return_value = time.time() + (31 * 60)  # 31 minutes
            
            # Cleanup should remove expired tokens
            count = csrf_protection.cleanup_expired_tokens()
            assert count > 0
            
            # Expired token should be gone
            assert csrf_protection.validate_csrf_token(token1) is False

    def test_get_token_info(self, csrf_protection):
        """Test getting token information."""
        session_id = "test-session-123"
        token = csrf_protection.generate_csrf_token(session_id)
        
        info = csrf_protection.get_token_info(token)
        
        assert info is not None
        assert info["session_id"] == session_id
        assert "expires_at" in info
        assert "created_at" in info

    def test_get_token_info_not_found(self, csrf_protection):
        """Test getting information for non-existent token."""
        info = csrf_protection.get_token_info("non-existent-token")
        assert info is None