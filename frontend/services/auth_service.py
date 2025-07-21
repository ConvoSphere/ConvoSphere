"""
Authentication service for user login, registration, and session management.

This module provides authentication functionality using the API client
with proper error handling and session management.
"""

from typing import Any

from nicegui import ui
from services.api_client import api_client


class AuthService:
    """Authentication service for user management."""

    def __init__(self):
        """Initialize the authentication service."""
        self.current_user: dict[str, Any] | None = None
        self.is_authenticated = False

    async def login(self, email: str, password: str) -> bool:
        """
        Login user with email and password.

        Args:
            email: User email
            password: User password

        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            # Validate input
            if not email or not password:
                return False

            # Make API request
            response = await api_client.login(email, password)

            if response.get("success"):
                # Store authentication token
                token = response.get("access_token")
                if token:
                    api_client.set_auth_token(token)

                # Store user information
                user_data = response.get("user")
                if user_data:
                    self.current_user = user_data
                    self.is_authenticated = True

                return True
            # Handle login error
            error_message = response.get("error", "Login failed")
            ui.notify(error_message, type="negative")
            return False

        except Exception as e:
            ui.notify(f"Login error: {str(e)}", type="negative")
            return False

    async def register(self, user_data: dict[str, Any]) -> bool:
        """
        Register new user.

        Args:
            user_data: User registration data

        Returns:
            bool: True if registration successful, False otherwise
        """
        try:
            # Validate required fields
            required_fields = [
                "email",
                "username",
                "password",
                "first_name",
                "last_name",
            ]
            for field in required_fields:
                if not user_data.get(field):
                    ui.notify(f"Field '{field}' is required", type="negative")
                    return False

            # Make API request
            response = await api_client.register(user_data)

            if response.get("success"):
                return True
            # Handle registration error
            error_message = response.get("error", "Registration failed")
            ui.notify(error_message, type="negative")
            return False

        except Exception as e:
            ui.notify(f"Registration error: {str(e)}", type="negative")
            return False

    async def logout(self) -> bool:
        """
        Logout current user.

        Returns:
            bool: True if logout successful, False otherwise
        """
        try:
            # Make API request
            response = await api_client.logout()

            # Clear local state regardless of API response
            self.current_user = None
            self.is_authenticated = False
            api_client.clear_auth_token()

            return True

        except Exception as e:
            # Clear local state even if API call fails
            self.current_user = None
            self.is_authenticated = False
            api_client.clear_auth_token()

            ui.notify(f"Logout error: {str(e)}", type="warning")
            return False

    async def get_current_user(self) -> dict[str, Any] | None:
        """
        Get current user information.

        Returns:
            Dict containing user information or None if not authenticated
        """
        try:
            if not self.is_authenticated:
                return None

            response = await api_client.get_current_user()

            if response.get("success"):
                user_data = response.get("user")
                if user_data:
                    self.current_user = user_data
                    return user_data

            return None

        except Exception as e:
            ui.notify(f"Error fetching user data: {str(e)}", type="negative")
            return None

    def is_user_authenticated(self) -> bool:
        """
        Check if user is currently authenticated.

        Returns:
            bool: True if user is authenticated, False otherwise
        """
        return self.is_authenticated and self.current_user is not None

    def get_user_info(self) -> dict[str, Any] | None:
        """
        Get current user information from local state.

        Returns:
            Dict containing user information or None if not authenticated
        """
        return self.current_user if self.is_authenticated else None

    async def refresh_session(self) -> bool:
        """
        Refresh user session.

        Returns:
            bool: True if session refresh successful, False otherwise
        """
        try:
            if not self.is_authenticated:
                return False

            user_data = await self.get_current_user()
            return user_data is not None

        except Exception as e:
            ui.notify(f"Session refresh error: {str(e)}", type="negative")
            return False

    def validate_email(self, email: str) -> bool:
        """
        Validate email format.

        Args:
            email: Email to validate

        Returns:
            bool: True if email is valid, False otherwise
        """
        import re

        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None

    def validate_password(self, password: str) -> tuple[bool, str]:
        """
        Validate password strength.

        Args:
            password: Password to validate

        Returns:
            tuple: (is_valid, error_message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"

        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"

        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"

        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number"

        return True, ""

    def validate_username(self, username: str) -> tuple[bool, str]:
        """
        Validate username format.

        Args:
            username: Username to validate

        Returns:
            tuple: (is_valid, error_message)
        """
        if len(username) < 3:
            return False, "Username must be at least 3 characters long"

        if len(username) > 30:
            return False, "Username must be less than 30 characters"

        import re

        pattern = r"^[a-zA-Z0-9_-]+$"
        if not re.match(pattern, username):
            return (
                False,
                "Username can only contain letters, numbers, underscores, and hyphens",
            )

        return True, ""


# Global auth service instance
auth_service = AuthService()
