"""
GitHub OAuth2 Provider.

This module provides GitHub OAuth2 authentication and user management.
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


class GitHubOAuthProvider(OAuthProvider):
    """GitHub OAuth2 provider."""

    def __init__(self, config: Dict[str, Any]):
        # GitHub-specific configuration
        github_config = {
            "client_id": config.get("client_id"),
            "client_secret": config.get("client_secret"),
            "authorization_url": "https://github.com/login/oauth/authorize",
            "token_url": "https://github.com/login/oauth/access_token",
            "userinfo_url": "https://api.github.com/user",
            "scope": "read:user user:email",
            "attribute_mapping": {
                "username": "login",
                "email": "email",
                "first_name": "name",
                "last_name": "",
                "groups": "organizations",
            },
            "default_role": config.get("default_role", UserRole.USER),
            "role_mapping": config.get("role_mapping", {}),
        }

        super().__init__(github_config)
        self.name = "GitHub"
        self.provider_type = "github"

    async def authenticate(
        self,
        credentials: Dict[str, Any],
        db: Session,
    ) -> tuple[User, Dict[str, Any]]:
        """Authenticate user via GitHub OAuth2."""
        try:
            # Use parent OAuth authentication
            user, additional_data = await super().authenticate(credentials, db)

            # Add GitHub-specific data
            additional_data["provider"] = "github"
            additional_data["github_id"] = additional_data.get("oauth_user_id")
            additional_data["github_username"] = additional_data.get("oauth_username")

            return user, additional_data

        except Exception as e:
            logger.exception(f"GitHub OAuth authentication failed: {str(e)}")
            raise AuthenticationError(f"GitHub OAuth authentication failed: {str(e)}")

    async def get_user_info(self, user_id: str, db: Session) -> Dict[str, Any]:
        """Get user information from GitHub API."""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise UserNotFoundError("User not found")

            # Try to refresh user info from GitHub API
            try:
                # This would require storing refresh tokens securely
                # For now, return cached information
                return {
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "provider": "github",
                    "last_sync": user.last_login.isoformat()
                    if user.last_login
                    else None,
                }
            except Exception as e:
                logger.exception(f"Failed to get GitHub user info: {str(e)}")
                return {"error": str(e)}

        except Exception as e:
            logger.exception(f"Failed to get GitHub user info: {str(e)}")
            return {"error": str(e)}

    async def sync_user_groups(self, user: User, db: Session) -> list[str]:
        """Synchronize user organizations from GitHub API."""
        try:
            # This would require GitHub API integration for organizations
            # For now, return empty list
            logger.info(
                f"Organization sync not implemented for GitHub OAuth2 user {user.id}"
            )
            return []

        except Exception as e:
            logger.exception(f"Failed to sync GitHub organizations: {str(e)}")
            raise GroupSyncError(f"GitHub organization sync failed: {str(e)}")

    async def _create_domain_group_from_github(
        self,
        github_org: str,
        db: Session,
    ) -> DomainGroup | None:
        """Create domain group from GitHub organization."""
        try:
            # Check if domain group already exists
            existing_group = (
                db.query(DomainGroup)
                .filter(DomainGroup.external_id == f"github:{github_org}")
                .first()
            )

            if existing_group:
                return existing_group

            # Create new domain group
            domain_group = DomainGroup(
                name=github_org,
                display_name=f"GitHub Organization: {github_org}",
                domain_type="TEAM",
                external_id=f"github:{github_org}",
                tags=["github", "auto-created"],
                is_system=True,
                settings={"github_source": True},
            )

            db.add(domain_group)
            db.commit()
            db.refresh(domain_group)

            return domain_group

        except Exception as e:
            logger.exception(f"Failed to create domain group from GitHub: {str(e)}")
            return None
