"""
Microsoft OAuth2 Provider.

This module provides Microsoft OAuth2 authentication and user management.
"""

import logging
from typing import Any, Dict

from sqlalchemy.orm import Session

from backend.app.core.sso.providers.oauth_provider import OAuthProvider
from backend.app.models.domain_groups import DomainGroup
from backend.app.models.user import User, UserRole
from backend.app.utils.exceptions import (
    AuthenticationError,
    GroupSyncError,
    UserNotFoundError,
)

logger = logging.getLogger(__name__)


class MicrosoftOAuthProvider(OAuthProvider):
    """Microsoft OAuth2 provider."""

    def __init__(self, config: Dict[str, Any]):
        # Microsoft-specific configuration
        tenant_id = config.get("tenant_id", "common")
        microsoft_config = {
            "client_id": config.get("client_id"),
            "client_secret": config.get("client_secret"),
            "authorization_url": f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize",
            "token_url": f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token",
            "userinfo_url": "https://graph.microsoft.com/v1.0/me",
            "scope": "openid email profile User.Read",
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

        super().__init__(microsoft_config)
        self.name = "Microsoft"
        self.provider_type = "microsoft"
        self.tenant_id = tenant_id

    async def authenticate(
        self,
        credentials: Dict[str, Any],
        db: Session,
    ) -> tuple[User, Dict[str, Any]]:
        """Authenticate user via Microsoft OAuth2."""
        try:
            # Use parent OAuth authentication
            user, additional_data = await super().authenticate(credentials, db)

            # Add Microsoft-specific data
            additional_data["provider"] = "microsoft"
            additional_data["microsoft_id"] = additional_data.get("oauth_user_id")
            additional_data["tenant_id"] = self.tenant_id

            return user, additional_data

        except Exception as e:
            logger.exception(f"Microsoft OAuth authentication failed: {str(e)}")
            raise AuthenticationError(
                f"Microsoft OAuth authentication failed: {str(e)}"
            )

    async def get_user_info(self, user_id: str, db: Session) -> Dict[str, Any]:
        """Get user information from Microsoft Graph API."""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise UserNotFoundError("User not found")

            # Try to refresh user info from Microsoft Graph API
            try:
                # This would require storing refresh tokens securely
                # For now, return cached information
                return {
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "provider": "microsoft",
                    "tenant_id": self.tenant_id,
                    "last_sync": (
                        user.last_login.isoformat() if user.last_login else None
                    ),
                }
            except Exception as e:
                logger.exception(f"Failed to get Microsoft user info: {str(e)}")
                return {"error": str(e)}

        except Exception as e:
            logger.exception(f"Failed to get Microsoft user info: {str(e)}")
            return {"error": str(e)}

    async def sync_user_groups(self, user: User, db: Session) -> list[str]:
        """Synchronize user groups from Microsoft Graph API."""
        try:
            # This would require Microsoft Graph API integration
            # For now, return empty list
            logger.info(
                f"Group sync not implemented for Microsoft OAuth2 user {user.id}"
            )
            return []

        except Exception as e:
            logger.exception(f"Failed to sync Microsoft groups: {str(e)}")
            raise GroupSyncError(f"Microsoft group sync failed: {str(e)}")

    async def _create_domain_group_from_microsoft(
        self,
        microsoft_group: str,
        db: Session,
    ) -> DomainGroup | None:
        """Create domain group from Microsoft group."""
        try:
            # Check if domain group already exists
            existing_group = (
                db.query(DomainGroup)
                .filter(DomainGroup.external_id == f"microsoft:{microsoft_group}")
                .first()
            )

            if existing_group:
                return existing_group

            # Create new domain group
            domain_group = DomainGroup(
                name=microsoft_group,
                display_name=f"Microsoft Group: {microsoft_group}",
                domain_type="TEAM",
                external_id=f"microsoft:{microsoft_group}",
                tags=["microsoft", "auto-created"],
                is_system=True,
                settings={"microsoft_source": True, "tenant_id": self.tenant_id},
            )

            db.add(domain_group)
            db.commit()
            db.refresh(domain_group)

            return domain_group

        except Exception as e:
            logger.exception(f"Failed to create domain group from Microsoft: {str(e)}")
            return None
