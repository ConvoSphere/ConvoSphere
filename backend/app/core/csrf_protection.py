"""
CSRF (Cross-Site Request Forgery) protection utilities.

This module provides CSRF token generation, validation, and protection
for sensitive operations like password reset.
"""

import secrets
import time
from typing import Optional
from loguru import logger

from backend.app.core.config import get_settings


class CSRFProtection:
    """CSRF protection for sensitive operations."""

    def __init__(self):
        """Initialize CSRF protection."""
        self.settings = get_settings()
        self.token_cache = {}
        self.token_length = 32
        self.token_expire_minutes = 30  # 30 minutes default

    def generate_csrf_token(self, session_id: str = None) -> str:
        """
        Generate a CSRF token.

        Args:
            session_id: Optional session identifier

        Returns:
            str: Generated CSRF token
        """
        token = secrets.token_urlsafe(self.token_length)
        expires_at = time.time() + (self.token_expire_minutes * 60)
        
        # Store token with expiration
        self.token_cache[token] = {
            "expires_at": expires_at,
            "session_id": session_id,
            "created_at": time.time()
        }
        
        logger.debug(f"Generated CSRF token: {token[:8]}...")
        return token

    def validate_csrf_token(self, token: str, session_id: str = None) -> bool:
        """
        Validate a CSRF token.

        Args:
            token: CSRF token to validate
            session_id: Optional session identifier

        Returns:
            bool: True if token is valid
        """
        if not token:
            logger.warning("CSRF token is empty")
            return False

        if token not in self.token_cache:
            logger.warning(f"CSRF token not found: {token[:8]}...")
            return False

        token_data = self.token_cache[token]
        current_time = time.time()

        # Check if token has expired
        if current_time > token_data["expires_at"]:
            logger.warning(f"CSRF token expired: {token[:8]}...")
            self._remove_token(token)
            return False

        # Check session ID if provided
        if session_id and token_data["session_id"] and token_data["session_id"] != session_id:
            logger.warning(f"CSRF token session mismatch: {token[:8]}...")
            return False

        return True

    def consume_csrf_token(self, token: str, session_id: str = None) -> bool:
        """
        Consume a CSRF token (one-time use).

        Args:
            token: CSRF token to consume
            session_id: Optional session identifier

        Returns:
            bool: True if token was valid and consumed
        """
        if self.validate_csrf_token(token, session_id):
            self._remove_token(token)
            logger.debug(f"CSRF token consumed: {token[:8]}...")
            return True
        return False

    def _remove_token(self, token: str) -> None:
        """Remove a token from cache."""
        if token in self.token_cache:
            del self.token_cache[token]

    def cleanup_expired_tokens(self) -> int:
        """
        Clean up expired tokens.

        Returns:
            int: Number of tokens cleaned up
        """
        current_time = time.time()
        expired_tokens = [
            token for token, data in self.token_cache.items()
            if current_time > data["expires_at"]
        ]
        
        for token in expired_tokens:
            self._remove_token(token)
        
        if expired_tokens:
            logger.info(f"Cleaned up {len(expired_tokens)} expired CSRF tokens")
        
        return len(expired_tokens)

    def get_token_info(self, token: str) -> Optional[dict]:
        """
        Get information about a CSRF token.

        Args:
            token: CSRF token

        Returns:
            dict: Token information or None if not found
        """
        if token in self.token_cache:
            return self.token_cache[token].copy()
        return None


# Global CSRF protection instance
csrf_protection = CSRFProtection()


def generate_csrf_token(session_id: str = None) -> str:
    """Generate a CSRF token."""
    return csrf_protection.generate_csrf_token(session_id)


def validate_csrf_token(token: str, session_id: str = None) -> bool:
    """Validate a CSRF token."""
    return csrf_protection.validate_csrf_token(token, session_id)


def consume_csrf_token(token: str, session_id: str = None) -> bool:
    """Consume a CSRF token."""
    return csrf_protection.consume_csrf_token(token, session_id)