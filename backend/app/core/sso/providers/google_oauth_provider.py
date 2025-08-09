"""
Google OAuth2 Provider.

This module provides Google OAuth2 authentication and user management.
"""

import logging
from datetime import UTC, datetime
from typing import Any, Dict

from sqlalchemy.orm import Session

from backend.app.core.sso.providers.oauth_provider import OAuthProvider
from backend.app.models.domain_groups import DomainGroup
from backend.app.models.user import AuthProvider, User, UserRole, UserStatus
from backend.app.utils.exceptions import (
    AuthenticationError,
    GroupSyncError,
    SSOConfigurationError,
    UserNotFoundError,
)

logger = logging.getLogger(__name__)


class GoogleOAuthProvider(OAuthProvider):
    """Google OAuth2 provider."""

    def __init__(self, config: Dict[str, Any]):
        # Google-specific configuration
        google_config = {
            "client_id": config.get("client_id"),
            "client_secret": config.get("client_secret"),
            "authorization_url": "https://accounts.google.com/o/oauth2/auth",
            "token_url": "https://oauth2.googleapis.com/token",
            "userinfo_url": "https://www.googleapis.com/oauth2/v2/userinfo",
            "scope": "openid email profile",
            "attribute_mapping": {
                "username": "sub",
                "email": "email",
                "first_name": "given_name",
                "last_name": "family_name",
                "groups": "groups",
            },
            "default_role": config.get("default_role", UserRole.USER),
            "role_mapping": config.get("role_mapping", {}),
        }
        
        super().__init__(google_config)
        self.name = "Google"
        self.provider_type = "google"

    async def authenticate(
        self,
        credentials: Dict[str, Any],
        db: Session,
    ) -> tuple[User, Dict[str, Any]]:
        """Authenticate user via Google OAuth2."""
        try:
            # Use parent OAuth authentication
            user, additional_data = await super().authenticate(credentials, db)
            
            # Add Google-specific data
            additional_data["provider"] = "google"
            additional_data["google_id"] = additional_data.get("oauth_user_id")
            
            return user, additional_data
            
        except Exception as e:
            logger.exception(f"Google OAuth authentication failed: {str(e)}")
            raise AuthenticationError(f"Google OAuth authentication failed: {str(e)}")

    async def get_user_info(self, user_id: str, db: Session) -> Dict[str, Any]:
        """Get user information from Google."""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise UserNotFoundError("User not found")

            # Try to refresh user info from Google
            try:
                # This would require storing refresh tokens securely
                # For now, return cached information
                return {
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "provider": "google",
                    "last_sync": user.last_login.isoformat() if user.last_login else None,
                }
            except Exception as e:
                logger.exception(f"Failed to get Google user info: {str(e)}")
                return {"error": str(e)}
                
        except Exception as e:
            logger.exception(f"Failed to get Google user info: {str(e)}")
            return {"error": str(e)}

    async def sync_user_groups(self, user: User, db: Session) -> list[str]:
        """Synchronize user groups from Google (not supported by default)."""
        # Google OAuth2 doesn't provide groups by default
        # This would require Google Workspace API integration
        logger.info(f"Group sync not supported for Google OAuth2 user {user.id}")
        return []

    async def _create_domain_group_from_google(
        self,
        google_group: str,
        db: Session,
    ) -> DomainGroup | None:
        """Create domain group from Google group."""
        try:
            # Check if domain group already exists
            existing_group = (
                db.query(DomainGroup)
                .filter(DomainGroup.external_id == f"google:{google_group}")
                .first()
            )

            if existing_group:
                return existing_group

            # Create new domain group
            domain_group = DomainGroup(
                name=google_group,
                display_name=f"Google Group: {google_group}",
                domain_type="TEAM",
                external_id=f"google:{google_group}",
                tags=["google", "auto-created"],
                is_system=True,
                settings={"google_source": True},
            )

            db.add(domain_group)
            db.commit()
            db.refresh(domain_group)

            return domain_group

        except Exception as e:
            logger.exception(f"Failed to create domain group from Google: {str(e)}")
            return None