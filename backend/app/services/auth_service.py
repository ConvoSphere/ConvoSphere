"""
Authentication service.

This module provides authentication-specific functionality,
wrapping the UserService for authentication operations.
"""

from datetime import datetime

from backend.app.core.config import get_settings
from backend.app.core.security import get_password_hash, verify_password
from backend.app.models.user import User
from backend.app.schemas.user import UserCreate, UserUpdate
from backend.app.services.email_service import email_service
from backend.app.services.token_service import token_service
from backend.app.services.user_service import UserService


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db_session):
        """Initialize AuthService with database session."""
        self.db_session = db_session
        self.user_service = UserService(db_session)

    def register_user(self, user_create: UserCreate) -> User:
        """
        Register a new user.

        Args:
            user_create: User creation data

        Returns:
            User: Created user object

        Raises:
            ValueError: If email or username already exists
        """
        # Check if user already exists
        if self.user_service.get_user_by_email(user_create.email):
            raise ValueError("Email already registered")

        if self.user_service.get_user_by_username(user_create.username):
            raise ValueError("Username already taken")

        # Create user using UserService
        return self.user_service.create_user(user_data=user_create)

    def authenticate_user(self, email: str, password: str) -> User | None:
        """
        Authenticate a user with email and password.

        Args:
            email: User email
            password: User password

        Returns:
            User: Authenticated user or None if authentication fails
        """
        return self.user_service.authenticate_user(email, password)

    def get_user_by_email(self, email: str) -> User | None:
        """
        Get user by email.

        Args:
            email: User email

        Returns:
            User: User object or None if not found
        """
        return self.user_service.get_user_by_email(email)

    def get_user_by_username(self, username: str) -> User | None:
        """
        Get user by username.

        Args:
            username: User username

        Returns:
            User: User object or None if not found
        """
        return self.user_service.get_user_by_username(username)

    def update_user_profile(self, user_id: str, user_update: UserUpdate) -> User:
        """
        Update user profile.

        Args:
            user_id: User ID
            user_update: User update data

        Returns:
            User: Updated user object
        """
        current_user = self.user_service.get_user_by_id(user_id)
        if not current_user:
            raise ValueError("User not found")

        return self.user_service.update_user(user_id, user_update, current_user)

    def change_password(
        self, user_id: str, current_password: str, new_password: str
    ) -> bool:
        """
        Change user password.

        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password

        Returns:
            bool: True if password changed successfully

        Raises:
            ValueError: If current password is incorrect
        """
        user = self.user_service.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        if not verify_password(current_password, user.hashed_password):
            raise ValueError("Current password is incorrect")

        # Update password
        user.hashed_password = get_password_hash(new_password)
        self.db_session.commit()
        return True

    def deactivate_user(self, user_id: str) -> bool:
        """
        Deactivate a user.

        Args:
            user_id: User ID

        Returns:
            bool: True if user deactivated successfully
        """
        user = self.user_service.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        user.is_active = False
        self.db_session.commit()
        return True

    def activate_user(self, user_id: str) -> bool:
        """
        Activate a user.

        Args:
            user_id: User ID

        Returns:
            bool: True if user activated successfully
        """
        user = self.user_service.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        user.is_active = True
        self.db_session.commit()
        return True

    def request_password_reset(self, email: str) -> bool:
        """
        Request a password reset for a user.

        Args:
            email: User email address

        Returns:
            bool: True if reset request was successful

        Raises:
            ValueError: If user not found
        """
        user = self.user_service.get_user_by_email(email)
        if not user:
            raise ValueError("User not found")

        # Generate password reset token
        token = token_service.create_password_reset_token(user, self.db_session)

        # Build reset URL
        settings = get_settings()
        base_url = getattr(settings, 'password_reset_base_url', 'http://localhost:3000')
        reset_url = f"{base_url}/reset-password?token={token}"

        # Send password reset email
        success = email_service.send_password_reset_email(
            email=user.email,
            token=token,
            reset_url=reset_url,
            language=user.language
        )

        if success:
            # Log the password reset request
            from backend.app.services.audit_service import audit_service
            audit_service.log_security_event(
                user_id=user.id,
                event_type="password_reset_requested",
                details={"email": user.email, "ip_address": "unknown"}
            )

        return success

    def reset_password_with_token(self, token: str, new_password: str) -> bool:
        """
        Reset password using a valid token.

        Args:
            token: Password reset token
            new_password: New password

        Returns:
            bool: True if password was reset successfully

        Raises:
            ValueError: If token is invalid or expired
        """
        # Validate token
        if not token_service.validate_password_reset_token(token, self.db_session):
            raise ValueError("Invalid or expired token")

        # Get user by token
        user = token_service.get_user_by_reset_token(token, self.db_session)
        if not user:
            raise ValueError("User not found")

        # Update password
        user.hashed_password = get_password_hash(new_password)
        user.password_changed_at = datetime.utcnow()
        
        # Clear reset token
        token_service.clear_password_reset_token(user, self.db_session)
        
        # Commit changes
        self.db_session.commit()

        # Send password changed notification
        email_service.send_password_changed_notification(
            email=user.email,
            language=user.language
        )

        # Log the password reset
        from backend.app.services.audit_service import audit_service
        audit_service.log_security_event(
            user_id=user.id,
            event_type="password_reset_completed",
            details={"email": user.email, "ip_address": "unknown"}
        )

        return True

    def validate_reset_token(self, token: str) -> bool:
        """
        Validate a password reset token without resetting password.

        Args:
            token: Password reset token

        Returns:
            bool: True if token is valid, False otherwise
        """
        return token_service.validate_password_reset_token(token, self.db_session)
