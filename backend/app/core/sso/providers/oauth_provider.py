"""
OAuth 2.0 / OpenID Connect SSO provider.

This module provides OAuth authentication and group synchronization.
"""

import logging
from datetime import UTC, datetime
from typing import Any, Dict, List

import requests
from sqlalchemy.orm import Session

from backend.app.core.sso.providers.base import BaseSSOProvider
from backend.app.models.domain_groups import DomainGroup
from backend.app.models.user import AuthProvider, User, UserRole, UserStatus
from backend.app.utils.exceptions import (
    AuthenticationError,
    GroupSyncError,
    SSOConfigurationError,
    UserNotFoundError,
)

logger = logging.getLogger(__name__)


class OAuthProvider(BaseSSOProvider):
    """OAuth 2.0 / OpenID Connect SSO provider."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client_id = config.get("client_id")
        self.client_secret = config.get("client_secret")
        self.authorization_url = config.get("authorization_url")
        self.token_url = config.get("token_url")
        self.userinfo_url = config.get("userinfo_url")
        self.scope = config.get("scope", "openid email profile")

        # Attribute mapping
        self.attribute_mapping = config.get(
            "attribute_mapping",
            {
                "username": "sub",
                "email": "email",
                "first_name": "given_name",
                "last_name": "family_name",
                "groups": "groups",
            },
        )

        # Role mapping
        self.role_mapping = config.get("role_mapping", {})
        self.default_role = config.get("default_role", UserRole.USER)

        # Token validation
        self.jwks_url = config.get("jwks_url")
        self.issuer = config.get("issuer")

        if not all(
            [
                self.client_id,
                self.client_secret,
                self.authorization_url,
                self.token_url,
            ],
        ):
            raise SSOConfigurationError("OAuth configuration incomplete")

    async def authenticate(
        self,
        credentials: Dict[str, Any],
        db: Session,
    ) -> tuple[User, Dict[str, Any]]:
        """Authenticate user via OAuth."""
        authorization_code = credentials.get("code")
        redirect_uri = credentials.get("redirect_uri")

        if not authorization_code or not redirect_uri:
            raise AuthenticationError("Authorization code and redirect URI required")

        try:
            # Exchange authorization code for access token
            token_data = await self._exchange_code_for_token(
                authorization_code,
                redirect_uri,
            )
            access_token = token_data.get("access_token")

            if not access_token:
                raise AuthenticationError("Failed to obtain access token")

            # Get user information
            user_info = await self._get_user_info(access_token)

            # Extract user attributes
            username = user_info.get(self.attribute_mapping["username"])
            email = user_info.get(self.attribute_mapping["email"])
            first_name = user_info.get(self.attribute_mapping["first_name"], "")
            last_name = user_info.get(self.attribute_mapping["last_name"], "")
            groups = user_info.get(self.attribute_mapping["groups"], [])

            if not username:
                raise AuthenticationError("Username not found in OAuth response")

            # Get or create user
            user = await self._get_or_create_user(
                username,
                email,
                first_name,
                last_name,
                db,
            )

            # Sync groups
            await self.sync_user_groups_with_groups(user, groups, db)

            additional_data = {
                "oauth_access_token": access_token,
                "oauth_refresh_token": token_data.get("refresh_token"),
                "oauth_groups": groups,
                "provider": "oauth",
                "last_sync": datetime.now(UTC).isoformat(),
            }

            return user, additional_data

        except Exception as e:
            logger.exception(f"OAuth authentication failed: {str(e)}")
            raise AuthenticationError(f"OAuth authentication failed: {str(e)}")

    async def get_user_info(self, user_id: str, db: Session) -> Dict[str, Any]:
        """Get user information from OAuth provider."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise UserNotFoundError("User not found")

        # Try to refresh user info from OAuth provider
        try:
            # This would require storing refresh tokens securely
            # For now, return cached information
            return {
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "provider": "oauth",
                "last_sync": user.last_login.isoformat() if user.last_login else None,
            }
        except Exception as e:
            logger.exception(f"Failed to get OAuth user info: {str(e)}")
            return {"error": str(e)}

    async def sync_user_groups(self, user: User, db: Session) -> List[str]:
        """Synchronize user groups from OAuth provider."""
        # This method signature differs from the base class
        # We need to handle the groups parameter differently
        return []

    async def sync_user_groups_with_groups(
        self,
        user: User,
        groups: List[str],
        db: Session,
    ) -> List[str]:
        """Synchronize user groups from OAuth provider with provided groups."""
        try:
            app_groups = []
            for group in groups:
                if group in self.role_mapping:
                    # Map OAuth groups to roles
                    mapped_role = self.role_mapping[group]
                    if user.role != mapped_role:
                        user.role = mapped_role
                        db.commit()

                # Create domain groups for OAuth groups
                domain_group = await self._create_domain_group_from_oauth(group, db)
                if domain_group:
                    app_groups.append(str(domain_group.id))

            return app_groups

        except Exception as e:
            logger.exception(f"Failed to sync OAuth groups: {str(e)}")
            raise GroupSyncError(f"OAuth group sync failed: {str(e)}")

    async def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate OAuth token."""
        try:
            # Validate token with OAuth provider
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(self.userinfo_url, headers=headers, timeout=30)

            if response.status_code == 200:
                return {"valid": True, "user_info": response.json()}
            return {"valid": False, "error": "Invalid token"}

        except Exception as e:
            logger.exception(f"Token validation failed: {str(e)}")
            return {"valid": False, "error": str(e)}

    async def _exchange_code_for_token(
        self,
        authorization_code: str,
        redirect_uri: str,
    ) -> Dict[str, Any]:
        """Exchange authorization code for access token."""
        token_data = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        response = requests.post(self.token_url, data=token_data, timeout=30)
        response.raise_for_status()

        return response.json()

    async def _get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from OAuth provider."""
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(self.userinfo_url, headers=headers, timeout=30)
        response.raise_for_status()

        return response.json()

    async def _get_or_create_user(
        self,
        username: str,
        email: str,
        first_name: str,
        last_name: str,
        db: Session,
    ) -> User:
        """Get existing user or create new one from OAuth."""
        user = db.query(User).filter(User.username == username).first()

        if not user:
            # Create new user
            user = User(
                username=username,
                email=email,
                full_name=f"{first_name} {last_name}".strip(),
                auth_provider=AuthProvider.OAUTH,
                role=self.default_role,
                status=UserStatus.ACTIVE,
                email_verified=True,
                last_login=datetime.now(UTC),
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            # Update existing user
            user.email = email
            user.full_name = f"{first_name} {last_name}".strip()
            user.last_login = datetime.now(UTC)
            db.commit()

        return user

    async def _create_domain_group_from_oauth(
        self,
        oauth_group: str,
        db: Session,
    ) -> DomainGroup | None:
        """Create domain group from OAuth group."""
        try:
            # Check if domain group already exists
            existing_group = (
                db.query(DomainGroup)
                .filter(DomainGroup.external_id == f"oauth:{oauth_group}")
                .first()
            )

            if existing_group:
                return existing_group

            # Create new domain group
            domain_group = DomainGroup(
                name=oauth_group,
                display_name=f"OAuth Group: {oauth_group}",
                domain_type="TEAM",
                external_id=f"oauth:{oauth_group}",
                tags=["oauth", "auto-created"],
                is_system=True,
                settings={"oauth_source": True},
            )

            db.add(domain_group)
            db.commit()
            db.refresh(domain_group)

            return domain_group

        except Exception as e:
            logger.exception(f"Failed to create domain group from OAuth: {str(e)}")
            return None
