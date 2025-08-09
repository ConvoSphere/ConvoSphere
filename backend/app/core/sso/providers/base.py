"""
Base SSO Provider interface.

This module provides the base interface for all SSO providers including
LDAP, SAML, OAuth, and OpenID Connect.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict

from sqlalchemy.orm import Session

from backend.app.models.user import User

logger = logging.getLogger(__name__)


class BaseSSOProvider(ABC):
    """Base class for SSO providers."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = config.get("name", "unknown")
        self.enabled = config.get("enabled", False)
        self.priority = config.get("priority", 0)

    @abstractmethod
    async def authenticate(
        self,
        credentials: Dict[str, Any],
        db: Session,
    ) -> tuple[User, Dict[str, Any]]:
        """
        Authenticate user and return user object with additional data.

        Args:
            credentials: Authentication credentials
            db: Database session

        Returns:
            Tuple of (User, additional_data)

        Raises:
            AuthenticationError: If authentication fails
        """

    @abstractmethod
    async def get_user_info(self, user_id: str, db: Session) -> Dict[str, Any]:
        """
        Get user information from SSO provider.

        Args:
            user_id: User identifier
            db: Database session

        Returns:
            User information dictionary
        """

    @abstractmethod
    async def sync_user_groups(self, user: User, db: Session) -> list[str]:
        """
        Synchronize user groups from SSO provider.

        Args:
            user: User object
            db: Database session

        Returns:
            List of group names
        """

    @abstractmethod
    async def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate SSO token.

        Args:
            token: Token to validate

        Returns:
            Token validation result
        """

    def is_enabled(self) -> bool:
        """Check if provider is enabled."""
        return self.enabled

    def get_priority(self) -> int:
        """Get provider priority."""
        return self.priority

    def get_name(self) -> str:
        """Get provider name."""
        return self.name
