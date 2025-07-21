"""
User service for the AI Assistant Platform.

This module provides comprehensive user management functionality including
profile management, settings, preferences, and admin features.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from utils.helpers import generate_id
from utils.validators import validate_password, validate_user_data

from .api import api_client
from .error_handler import handle_api_error, handle_network_error


class UserRole(Enum):
    """User role enumeration."""

    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"


class UserStatus(Enum):
    """User status enumeration."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


@dataclass
class UserPreferences:
    """User preferences data model."""

    theme: str = "light"
    language: str = "de"
    timezone: str = "Europe/Berlin"
    notifications_enabled: bool = True
    email_notifications: bool = True
    push_notifications: bool = False
    auto_save: bool = True
    chat_history_limit: int = 100
    default_assistant_id: str | None = None
    ui_compact_mode: bool = False
    accessibility_mode: bool = False
    high_contrast: bool = False
    font_size: str = "medium"
    sound_enabled: bool = True


@dataclass
class UserProfile:
    """User profile data model."""

    id: str
    username: str
    email: str
    first_name: str
    last_name: str
    role: UserRole
    status: UserStatus
    created_at: datetime
    updated_at: datetime
    last_login: datetime | None = None
    avatar_url: str | None = None
    bio: str | None = None
    location: str | None = None
    website: str | None = None
    preferences: UserPreferences | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class UserStats:
    """User statistics data model."""

    total_conversations: int = 0
    total_messages: int = 0
    total_assistants: int = 0
    total_documents: int = 0
    total_tools: int = 0
    last_activity: datetime | None = None
    storage_used: int = 0
    storage_limit: int = 0


class UserService:
    """Service for user management and profile handling."""

    def __init__(self):
        """Initialize the user service."""
        self.current_user: UserProfile | None = None
        self.users: list[UserProfile] = []
        self.is_loading = False
        self.user_stats: UserStats | None = None

        # Settings cache
        self.settings_cache: dict[str, Any] = {}

    async def get_current_user(self, force_refresh: bool = False) -> UserProfile | None:
        """
        Get current user profile.

        Args:
            force_refresh: Force refresh from API

        Returns:
            Current user profile or None
        """
        if not force_refresh and self.current_user:
            return self.current_user

        try:
            response = await api_client.get_current_user()

            if response.success and response.data:
                self.current_user = self._create_user_profile_from_data(response.data)
                return self.current_user
            handle_api_error(response, "Laden des Benutzerprofils")
            return None

        except Exception as e:
            handle_network_error(e, "Laden des Benutzerprofils")
            return None

    async def update_profile(self, profile_data: dict[str, Any]) -> UserProfile | None:
        """
        Update user profile.

        Args:
            profile_data: Updated profile data

        Returns:
            Updated user profile or None
        """
        try:
            # Validate profile data
            validation = validate_user_data(profile_data)
            if not validation["valid"]:
                raise ValueError(f"Profile validation failed: {validation['errors']}")

            response = await api_client.update_profile(profile_data)

            if response.success and response.data:
                self.current_user = self._create_user_profile_from_data(response.data)
                return self.current_user
            handle_api_error(response, "Aktualisieren des Profils")
            return None

        except Exception as e:
            handle_network_error(e, "Aktualisieren des Profils")
            return None

    async def change_password(self, current_password: str, new_password: str) -> bool:
        """
        Change user password.

        Args:
            current_password: Current password
            new_password: New password

        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate new password
            validation = validate_password(new_password)
            if not validation["valid"]:
                raise ValueError(f"Password validation failed: {validation['errors']}")

            response = await api_client.change_password(current_password, new_password)

            if response.success:
                return True
            handle_api_error(response, "Passwort ändern")
            return False

        except Exception as e:
            handle_network_error(e, "Passwort ändern")
            return False

    async def upload_avatar(self, avatar_data: bytes, filename: str) -> str | None:
        """
        Upload user avatar.

        Args:
            avatar_data: Avatar image data
            filename: Avatar filename

        Returns:
            Avatar URL or None
        """
        try:
            response = await api_client.upload_avatar(avatar_data, filename)

            if response.success and response.data:
                avatar_url = response.data.get("avatar_url")
                if self.current_user:
                    self.current_user.avatar_url = avatar_url
                return avatar_url
            handle_api_error(response, "Avatar hochladen")
            return None

        except Exception as e:
            handle_network_error(e, "Avatar hochladen")
            return None

    async def get_user_preferences(self) -> UserPreferences | None:
        """
        Get user preferences.

        Args:
            User preferences or None
        """
        try:
            response = await api_client.get_user_preferences()

            if response.success and response.data:
                return self._create_user_preferences_from_data(response.data)
            handle_api_error(response, "Laden der Benutzereinstellungen")
            return None

        except Exception as e:
            handle_network_error(e, "Laden der Benutzereinstellungen")
            return None

    async def update_user_preferences(self, preferences: UserPreferences) -> bool:
        """
        Update user preferences.

        Args:
            preferences: Updated preferences

        Returns:
            True if successful, False otherwise
        """
        try:
            preferences_data = self._preferences_to_dict(preferences)
            response = await api_client.update_user_preferences(preferences_data)

            if response.success:
                if self.current_user:
                    self.current_user.preferences = preferences
                return True
            handle_api_error(response, "Aktualisieren der Benutzereinstellungen")
            return False

        except Exception as e:
            handle_network_error(e, "Aktualisieren der Benutzereinstellungen")
            return False

    async def get_user_stats(self) -> UserStats | None:
        """
        Get user statistics.

        Args:
            User statistics or None
        """
        try:
            response = await api_client.get_user_stats()

            if response.success and response.data:
                self.user_stats = self._create_user_stats_from_data(response.data)
                return self.user_stats
            handle_api_error(response, "Laden der Benutzerstatistiken")
            return None

        except Exception as e:
            handle_network_error(e, "Laden der Benutzerstatistiken")
            return None

    # Admin functions
    async def get_all_users(self, skip: int = 0, limit: int = 100) -> list[UserProfile]:
        """
        Get all users (admin only).

        Args:
            skip: Number of users to skip
            limit: Maximum number of users to return

        Returns:
            List of user profiles
        """
        try:
            response = await api_client.get_all_users(skip=skip, limit=limit)

            if response.success and response.data:
                self.users = [
                    self._create_user_profile_from_data(user_data)
                    for user_data in response.data
                ]
                return self.users
            handle_api_error(response, "Laden der Benutzer")
            return []

        except Exception as e:
            handle_network_error(e, "Laden der Benutzer")
            return []

    async def get_user_by_id(self, user_id: str) -> UserProfile | None:
        """
        Get user by ID (admin only).

        Args:
            user_id: User ID

        Returns:
            User profile or None
        """
        try:
            response = await api_client.get_user_by_id(user_id)

            if response.success and response.data:
                return self._create_user_profile_from_data(response.data)
            handle_api_error(response, f"Laden des Benutzers {user_id}")
            return None

        except Exception as e:
            handle_network_error(e, f"Laden des Benutzers {user_id}")
            return None

    async def update_user_role(self, user_id: str, role: UserRole) -> bool:
        """
        Update user role (admin only).

        Args:
            user_id: User ID
            role: New role

        Returns:
            True if successful, False otherwise
        """
        try:
            response = await api_client.update_user_role(user_id, role.value)

            if response.success:
                # Update in local list
                for user in self.users:
                    if user.id == user_id:
                        user.role = role
                        break
                return True
            handle_api_error(response, f"Rolle für Benutzer {user_id} aktualisieren")
            return False

        except Exception as e:
            handle_network_error(e, f"Rolle für Benutzer {user_id} aktualisieren")
            return False

    async def update_user_status(self, user_id: str, status: UserStatus) -> bool:
        """
        Update user status (admin only).

        Args:
            user_id: User ID
            status: New status

        Returns:
            True if successful, False otherwise
        """
        try:
            response = await api_client.update_user_status(user_id, status.value)

            if response.success:
                # Update in local list
                for user in self.users:
                    if user.id == user_id:
                        user.status = status
                        break
                return True
            handle_api_error(response, f"Status für Benutzer {user_id} aktualisieren")
            return False

        except Exception as e:
            handle_network_error(e, f"Status für Benutzer {user_id} aktualisieren")
            return False

    async def delete_user(self, user_id: str) -> bool:
        """
        Delete user (admin only).

        Args:
            user_id: User ID

        Returns:
            True if successful, False otherwise
        """
        try:
            response = await api_client.delete_user(user_id)

            if response.success:
                # Remove from local list
                self.users = [u for u in self.users if u.id != user_id]
                return True
            handle_api_error(response, f"Benutzer {user_id} löschen")
            return False

        except Exception as e:
            handle_network_error(e, f"Benutzer {user_id} löschen")
            return False

    async def get_system_stats(self) -> dict[str, Any]:
        """
        Get system statistics (admin only).

        Args:
            System statistics dictionary
        """
        try:
            response = await api_client.get_system_stats()

            if response.success and response.data:
                return response.data
            handle_api_error(response, "Laden der Systemstatistiken")
            return {}

        except Exception as e:
            handle_network_error(e, "Laden der Systemstatistiken")
            return {}

    # Utility functions
    def is_admin(self) -> bool:
        """Check if current user is admin."""
        return self.current_user and self.current_user.role == UserRole.ADMIN

    def is_moderator(self) -> bool:
        """Check if current user is moderator."""
        return self.current_user and self.current_user.role in [
            UserRole.ADMIN,
            UserRole.MODERATOR,
        ]

    def can_manage_user(self, target_user: UserProfile) -> bool:
        """Check if current user can manage target user."""
        if not self.current_user:
            return False

        # Admins can manage everyone
        if self.current_user.role == UserRole.ADMIN:
            return True

        # Moderators can manage regular users
        if (
            self.current_user.role == UserRole.MODERATOR
            and target_user.role == UserRole.USER
        ):
            return True

        # Users can only manage themselves
        return self.current_user.id == target_user.id

    def get_users_by_role(self, role: UserRole) -> list[UserProfile]:
        """Get users by role."""
        return [u for u in self.users if u.role == role]

    def get_users_by_status(self, status: UserStatus) -> list[UserProfile]:
        """Get users by status."""
        return [u for u in self.users if u.status == status]

    def search_users(self, query: str) -> list[UserProfile]:
        """Search users by name or email."""
        query_lower = query.lower()
        return [
            u
            for u in self.users
            if query_lower in u.username.lower()
            or query_lower in u.email.lower()
            or query_lower in f"{u.first_name} {u.last_name}".lower()
        ]

    def get_storage_usage_percentage(self) -> float:
        """Get storage usage percentage."""
        if not self.user_stats or self.user_stats.storage_limit == 0:
            return 0.0
        return (self.user_stats.storage_used / self.user_stats.storage_limit) * 100

    def _create_user_profile_from_data(self, data: dict[str, Any]) -> UserProfile:
        """Create UserProfile object from API data."""
        preferences = None
        if data.get("preferences"):
            preferences = self._create_user_preferences_from_data(data["preferences"])

        return UserProfile(
            id=data.get("id", generate_id("user_")),
            username=data.get("username", ""),
            email=data.get("email", ""),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            role=UserRole(data.get("role", "user")),
            status=UserStatus(data.get("status", "active")),
            created_at=datetime.fromisoformat(data["created_at"])
            if data.get("created_at")
            else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"])
            if data.get("updated_at")
            else datetime.now(),
            last_login=datetime.fromisoformat(data["last_login"])
            if data.get("last_login")
            else None,
            avatar_url=data.get("avatar_url"),
            bio=data.get("bio"),
            location=data.get("location"),
            website=data.get("website"),
            preferences=preferences,
            metadata=data.get("metadata"),
        )

    def _create_user_preferences_from_data(
        self, data: dict[str, Any],
    ) -> UserPreferences:
        """Create UserPreferences object from API data."""
        return UserPreferences(
            theme=data.get("theme", "light"),
            language=data.get("language", "de"),
            timezone=data.get("timezone", "Europe/Berlin"),
            notifications_enabled=data.get("notifications_enabled", True),
            email_notifications=data.get("email_notifications", True),
            push_notifications=data.get("push_notifications", False),
            auto_save=data.get("auto_save", True),
            chat_history_limit=data.get("chat_history_limit", 100),
            default_assistant_id=data.get("default_assistant_id"),
            ui_compact_mode=data.get("ui_compact_mode", False),
            accessibility_mode=data.get("accessibility_mode", False),
            high_contrast=data.get("high_contrast", False),
            font_size=data.get("font_size", "medium"),
            sound_enabled=data.get("sound_enabled", True),
        )

    def _create_user_stats_from_data(self, data: dict[str, Any]) -> UserStats:
        """Create UserStats object from API data."""
        return UserStats(
            total_conversations=data.get("total_conversations", 0),
            total_messages=data.get("total_messages", 0),
            total_assistants=data.get("total_assistants", 0),
            total_documents=data.get("total_documents", 0),
            total_tools=data.get("total_tools", 0),
            last_activity=datetime.fromisoformat(data["last_activity"])
            if data.get("last_activity")
            else None,
            storage_used=data.get("storage_used", 0),
            storage_limit=data.get("storage_limit", 0),
        )

    def _preferences_to_dict(self, preferences: UserPreferences) -> dict[str, Any]:
        """Convert UserPreferences to dictionary."""
        return {
            "theme": preferences.theme,
            "language": preferences.language,
            "timezone": preferences.timezone,
            "notifications_enabled": preferences.notifications_enabled,
            "email_notifications": preferences.email_notifications,
            "push_notifications": preferences.push_notifications,
            "auto_save": preferences.auto_save,
            "chat_history_limit": preferences.chat_history_limit,
            "default_assistant_id": preferences.default_assistant_id,
            "ui_compact_mode": preferences.ui_compact_mode,
            "accessibility_mode": preferences.accessibility_mode,
            "high_contrast": preferences.high_contrast,
            "font_size": preferences.font_size,
            "sound_enabled": preferences.sound_enabled,
        }


# Global user service instance
user_service = UserService()
