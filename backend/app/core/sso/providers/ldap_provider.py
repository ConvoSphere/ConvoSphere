"""
LDAP/Active Directory SSO provider.

This module provides LDAP authentication and group synchronization.
"""

import logging
from datetime import UTC, datetime
from typing import Any, Dict

from ldap3 import SUBTREE, Connection, Server
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


class LDAPProvider(BaseSSOProvider):
    """LDAP/Active Directory SSO provider."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.server_url = config.get("server_url")
        self.base_dn = config.get("base_dn")
        self.bind_dn = config.get("bind_dn")
        self.bind_password = config.get("bind_password")
        self.user_search_base = config.get("user_search_base", self.base_dn)
        self.group_search_base = config.get("group_search_base", self.base_dn)
        self.user_search_filter = config.get(
            "user_search_filter",
            "(sAMAccountName={username})",
        )
        self.group_search_filter = config.get(
            "group_search_filter",
            "(member={user_dn})",
        )
        self.attributes = config.get(
            "attributes",
            ["cn", "mail", "displayName", "memberOf"],
        )

        # Role mapping configuration
        self.role_mapping = config.get("role_mapping", {})
        self.default_role = config.get("default_role", UserRole.USER)

        # Group mapping configuration
        self.group_mapping = config.get("group_mapping", {})
        self.auto_create_groups = config.get("auto_create_groups", False)

        # Connection settings
        self.use_ssl = config.get("use_ssl", True)
        self.timeout = config.get("timeout", 10)

        if not all([self.server_url, self.base_dn, self.bind_dn, self.bind_password]):
            raise SSOConfigurationError("LDAP configuration incomplete")

    async def authenticate(
        self,
        credentials: Dict[str, Any],
        db: Session,
    ) -> tuple[User, Dict[str, Any]]:
        """Authenticate user against LDAP."""
        username = credentials.get("username")
        password = credentials.get("password")

        if not username or not password:
            raise AuthenticationError("Username and password required")

        try:
            # Connect to LDAP server
            server = Server(
                self.server_url,
                use_ssl=self.use_ssl,
                connect_timeout=self.timeout,
            )
            conn = Connection(
                server,
                user=self.bind_dn,
                password=self.bind_password,
                auto_bind=True,
            )

            # Search for user
            user_filter = self.user_search_filter.format(username=username)
            conn.search(
                self.user_search_base,
                user_filter,
                SUBTREE,
                attributes=self.attributes,
            )

            if not conn.entries:
                raise AuthenticationError("User not found in LDAP")

            user_entry = conn.entries[0]
            user_dn = user_entry.entry_dn

            # Verify password
            user_conn = Connection(
                server,
                user=user_dn,
                password=password,
                auto_bind=True,
            )
            if not user_conn.bound:
                raise AuthenticationError("Invalid credentials")

            # Get user attributes
            user_attrs = user_entry.entry_attributes
            email = user_attrs.get("mail", [""])[0] if user_attrs.get("mail") else ""
            display_name = (
                user_attrs.get("displayName", [""])[0]
                if user_attrs.get("displayName")
                else ""
            )

            # Get or create user in database
            user = await self._get_or_create_user(username, email, display_name, db)

            # Sync groups
            groups = await self.sync_user_groups(user, db)

            # Additional data
            additional_data = {
                "ldap_dn": user_dn,
                "ldap_groups": groups,
                "provider": "ldap",
                "last_sync": datetime.now(UTC).isoformat(),
            }

            return user, additional_data

        except Exception as e:
            logger.exception(f"LDAP authentication failed: {str(e)}")
            raise AuthenticationError(f"LDAP authentication failed: {str(e)}")

    async def get_user_info(self, user_id: str, db: Session) -> Dict[str, Any]:
        """Get user information from LDAP."""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise UserNotFoundError("User not found")

            server = Server(
                self.server_url,
                use_ssl=self.use_ssl,
                connect_timeout=self.timeout,
            )
            conn = Connection(
                server,
                user=self.bind_dn,
                password=self.bind_password,
                auto_bind=True,
            )

            user_filter = self.user_search_filter.format(username=user.username)
            conn.search(
                self.user_search_base,
                user_filter,
                SUBTREE,
                attributes=self.attributes,
            )

            if not conn.entries:
                return {"error": "User not found in LDAP"}

            user_entry = conn.entries[0]
            user_attrs = user_entry.entry_attributes

            return {
                "dn": user_entry.entry_dn,
                "email": (
                    user_attrs.get("mail", [""])[0] if user_attrs.get("mail") else ""
                ),
                "display_name": (
                    user_attrs.get("displayName", [""])[0]
                    if user_attrs.get("displayName")
                    else ""
                ),
                "groups": await self.sync_user_groups(user, db),
                "last_sync": datetime.now(UTC).isoformat(),
            }

        except Exception as e:
            logger.exception(f"Failed to get LDAP user info: {str(e)}")
            return {"error": str(e)}

    async def sync_user_groups(self, user: User, db: Session) -> list[str]:
        """Synchronize user groups from LDAP."""
        try:
            server = Server(
                self.server_url,
                use_ssl=self.use_ssl,
                connect_timeout=self.timeout,
            )
            conn = Connection(
                server,
                user=self.bind_dn,
                password=self.bind_password,
                auto_bind=True,
            )

            # Get user DN
            user_filter = self.user_search_filter.format(username=user.username)
            conn.search(
                self.user_search_base,
                user_filter,
                SUBTREE,
                attributes=["distinguishedName"],
            )

            if not conn.entries:
                return []

            user_dn = conn.entries[0].entry_dn

            # Search for groups
            group_filter = self.group_search_filter.format(user_dn=user_dn)
            conn.search(
                self.group_search_base,
                group_filter,
                SUBTREE,
                attributes=["cn", "distinguishedName"],
            )

            ldap_groups = []
            for entry in conn.entries:
                group_cn = entry.entry_attributes.get("cn", [""])[0]
                if group_cn:
                    ldap_groups.append(group_cn)

            # Map LDAP groups to application groups
            app_groups = []
            for ldap_group in ldap_groups:
                if ldap_group in self.group_mapping:
                    app_groups.append(self.group_mapping[ldap_group])
                elif self.auto_create_groups:
                    # Auto-create domain groups for LDAP groups
                    domain_group = await self._create_domain_group_from_ldap(
                        ldap_group,
                        db,
                    )
                    if domain_group:
                        app_groups.append(str(domain_group.id))

            return app_groups

        except Exception as e:
            logger.exception(f"Failed to sync LDAP groups: {str(e)}")
            raise GroupSyncError(f"LDAP group sync failed: {str(e)}")

    async def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate LDAP token (not applicable for LDAP)."""
        return {"valid": False, "error": "Token validation not supported for LDAP"}

    async def _get_or_create_user(
        self,
        username: str,
        email: str,
        display_name: str,
        db: Session,
    ) -> User:
        """Get existing user or create new one from LDAP."""
        user = db.query(User).filter(User.username == username).first()

        if not user:
            # Create new user
            user = User(
                username=username,
                email=email,
                full_name=display_name,
                auth_provider=AuthProvider.LDAP,
                role=self.default_role,
                status=UserStatus.ACTIVE,
                email_verified=True,  # LDAP users are considered verified
                last_login=datetime.now(UTC),
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            # Update existing user
            user.email = email
            user.full_name = display_name
            user.last_login = datetime.now(UTC)
            db.commit()

        return user

    async def _create_domain_group_from_ldap(
        self,
        ldap_group: str,
        db: Session,
    ) -> DomainGroup | None:
        """Create domain group from LDAP group."""
        try:
            # Check if domain group already exists
            existing_group = (
                db.query(DomainGroup)
                .filter(DomainGroup.external_id == f"ldap:{ldap_group}")
                .first()
            )

            if existing_group:
                return existing_group

            # Create new domain group
            domain_group = DomainGroup(
                name=ldap_group,
                display_name=f"LDAP Group: {ldap_group}",
                domain_type="TEAM",
                external_id=f"ldap:{ldap_group}",
                tags=["ldap", "auto-created"],
                is_system=True,
                settings={"ldap_source": True},
            )

            db.add(domain_group)
            db.commit()
            db.refresh(domain_group)

            return domain_group

        except Exception as e:
            logger.exception(f"Failed to create domain group from LDAP: {str(e)}")
            return None