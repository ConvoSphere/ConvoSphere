"""
Token service for password reset functionality.

This module provides secure token generation and validation
for password reset operations.
"""

import secrets
import string
from datetime import datetime, timedelta
from typing import Optional
from loguru import logger

from backend.app.core.config import get_settings
from backend.app.models.user import User
from sqlalchemy.orm import Session


class TokenService:
    """Service for managing password reset tokens."""

    def __init__(self):
        """Initialize TokenService with settings."""
        self.settings = get_settings()
        self.token_length = 32
        self.token_expire_minutes = getattr(
            self.settings, 'password_reset_token_expire_minutes', 60
        )

    def generate_password_reset_token(self) -> str:
        """
        Generate a secure password reset token.

        Returns:
            str: Secure random token
        """
        # Generate a cryptographically secure random token
        alphabet = string.ascii_letters + string.digits
        token = ''.join(secrets.choice(alphabet) for _ in range(self.token_length))
        
        logger.debug(f"Generated password reset token: {token[:8]}...")
        return token

    def validate_password_reset_token(self, token: str, db: Session) -> bool:
        """
        Validate a password reset token.

        Args:
            token: Token to validate
            db: Database session

        Returns:
            bool: True if token is valid, False otherwise
        """
        if not token:
            return False

        # Find user with this token
        user = self.get_user_by_reset_token(token, db)
        if not user:
            logger.warning(f"Invalid password reset token: {token[:8]}...")
            return False

        # Check if token has expired
        if user.password_reset_expires_at and user.password_reset_expires_at < datetime.utcnow():
            logger.warning(f"Expired password reset token: {token[:8]}...")
            return False

        return True

    def get_user_by_reset_token(self, token: str, db: Session) -> Optional[User]:
        """
        Get user by password reset token.

        Args:
            token: Password reset token
            db: Database session

        Returns:
            User: User object if found, None otherwise
        """
        return db.query(User).filter(User.password_reset_token == token).first()

    def create_password_reset_token(self, user: User, db: Session) -> str:
        """
        Create a new password reset token for a user.

        Args:
            user: User object
            db: Database session

        Returns:
            str: Generated token
        """
        # Generate new token
        token = self.generate_password_reset_token()
        
        # Set expiration time
        expires_at = datetime.utcnow() + timedelta(minutes=self.token_expire_minutes)
        
        # Update user with token and expiration
        user.password_reset_token = token
        user.password_reset_expires_at = expires_at
        
        # Commit changes
        db.commit()
        
        logger.info(f"Created password reset token for user {user.email}")
        return token

    def clear_password_reset_token(self, user: User, db: Session) -> None:
        """
        Clear password reset token for a user.

        Args:
            user: User object
            db: Database session
        """
        user.password_reset_token = None
        user.password_reset_expires_at = None
        db.commit()
        
        logger.info(f"Cleared password reset token for user {user.email}")

    def cleanup_expired_tokens(self, db: Session) -> int:
        """
        Clean up expired password reset tokens.

        Args:
            db: Database session

        Returns:
            int: Number of tokens cleaned up
        """
        now = datetime.utcnow()
        expired_users = db.query(User).filter(
            User.password_reset_expires_at < now,
            User.password_reset_token.isnot(None)
        ).all()
        
        count = 0
        for user in expired_users:
            user.password_reset_token = None
            user.password_reset_expires_at = None
            count += 1
        
        if count > 0:
            db.commit()
            logger.info(f"Cleaned up {count} expired password reset tokens")
        
        return count


# Global token service instance
token_service = TokenService()