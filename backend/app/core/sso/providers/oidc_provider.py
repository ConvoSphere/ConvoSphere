"""
OpenID Connect (OIDC) Provider.

This module provides OpenID Connect authentication and user management.
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


class OIDCProvider(OAuthProvider):
    """OpenID Connect provider."""

    def __init__(self, config: Dict[str, Any]):
        # OIDC-specific configuration
        issuer_url = config.get("issuer_url")
        if not issuer_url:
            raise SSOConfigurationError("OIDC issuer URL is required")
            
        oidc_config = {
            "client_id": config.get("client_id"),
            "client_secret": config.get("client_secret"),
            "authorization_url": f"{issuer_url}/authorize",
            "token_url": f"{issuer_url}/token",
            "userinfo_url": f"{issuer_url}/userinfo",
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
        
        super().__init__(oidc_config)
        self.name = "OIDC"
        self.provider_type = "oidc"
        self.issuer_url = issuer_url

    async def authenticate(
        self,
        credentials: Dict[str, Any],
        db: Session,
    ) -> tuple[User, Dict[str, Any]]:
        """Authenticate user via OpenID Connect."""
        try:
            # Use parent OAuth authentication
            user, additional_data = await super().authenticate(credentials, db)
            
            # Add OIDC-specific data
            additional_data["provider"] = "oidc"
            additional_data["oidc_sub"] = additional_data.get("oauth_user_id")
            additional_data["issuer_url"] = self.issuer_url
            
            return user, additional_data
            
        except Exception as e:
            logger.exception(f"OIDC authentication failed: {str(e)}")
            raise AuthenticationError(f"OIDC authentication failed: {str(e)}")

    async def get_user_info(self, user_id: str, db: Session) -> Dict[str, Any]:
        """Get user information from OIDC provider."""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise UserNotFoundError("User not found")

            # Try to refresh user info from OIDC provider
            try:
                # This would require storing refresh tokens securely
                # For now, return cached information
                return {
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "provider": "oidc",
                    "issuer_url": self.issuer_url,
                    "last_sync": user.last_login.isoformat() if user.last_login else None,
                }
            except Exception as e:
                logger.exception(f"Failed to get OIDC user info: {str(e)}")
                return {"error": str(e)}
                
        except Exception as e:
            logger.exception(f"Failed to get OIDC user info: {str(e)}")
            return {"error": str(e)}

    async def sync_user_groups(self, user: User, db: Session) -> list[str]:
        """Synchronize user groups from OIDC provider."""
        try:
            # This would require OIDC provider-specific group sync
            # For now, return empty list
            logger.info(f"Group sync not implemented for OIDC user {user.id}")
            return []
            
        except Exception as e:
            logger.exception(f"Failed to sync OIDC groups: {str(e)}")
            raise GroupSyncError(f"OIDC group sync failed: {str(e)}")

    async def _create_domain_group_from_oidc(
        self,
        oidc_group: str,
        db: Session,
    ) -> DomainGroup | None:
        """Create domain group from OIDC group."""
        try:
            # Check if domain group already exists
            existing_group = (
                db.query(DomainGroup)
                .filter(DomainGroup.external_id == f"oidc:{oidc_group}")
                .first()
            )

            if existing_group:
                return existing_group

            # Create new domain group
            domain_group = DomainGroup(
                name=oidc_group,
                display_name=f"OIDC Group: {oidc_group}",
                domain_type="TEAM",
                external_id=f"oidc:{oidc_group}",
                tags=["oidc", "auto-created"],
                is_system=True,
                settings={"oidc_source": True, "issuer_url": self.issuer_url},
            )

            db.add(domain_group)
            db.commit()
            db.refresh(domain_group)

            return domain_group

        except Exception as e:
            logger.exception(f"Failed to create domain group from OIDC: {str(e)}")
            return None