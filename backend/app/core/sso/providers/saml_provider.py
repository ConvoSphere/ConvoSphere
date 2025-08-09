"""
SAML 2.0 SSO provider.

This module provides SAML authentication and group synchronization.
"""

import logging
from datetime import UTC, datetime
from typing import Any, Dict, List

from saml2 import BINDING_HTTP_POST, BINDING_HTTP_REDIRECT
from saml2.client import Saml2Client
from saml2.config import Config as SamlConfig
from saml2.response import AuthnResponse
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


class SAMLProvider(BaseSSOProvider):
    """SAML 2.0 SSO provider."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.idp_metadata_url = config.get("idp_metadata_url")
        self.idp_entity_id = config.get("idp_entity_id")
        self.sp_entity_id = config.get("sp_entity_id")
        self.acs_url = config.get("acs_url")
        self.slo_url = config.get("slo_url")
        self.cert_file = config.get("cert_file")
        self.key_file = config.get("key_file")

        # Attribute mapping
        self.attribute_mapping = config.get(
            "attribute_mapping",
            {
                "username": "urn:oid:0.9.2342.19200300.100.1.1",  # uid
                "email": "urn:oid:0.9.2342.19200300.100.1.3",  # mail
                "first_name": "urn:oid:2.5.4.42",  # givenName
                "last_name": "urn:oid:2.5.4.4",  # sn
                "groups": "urn:oid:1.3.6.1.4.1.5923.1.5.1.1",  # eduPersonAffiliation
            },
        )

        # Role mapping
        self.role_mapping = config.get("role_mapping", {})
        self.default_role = config.get("default_role", UserRole.USER)

        # Initialize SAML client
        self._init_saml_client()

    def _init_saml_client(self):
        """Initialize SAML client configuration."""
        try:
            saml_config = {
                "entityid": self.sp_entity_id,
                "service": {
                    "sp": {
                        "endpoints": {
                            "assertion_consumer_service": [
                                (self.acs_url, BINDING_HTTP_POST),
                            ],
                            "single_logout_service": [
                                (self.slo_url, BINDING_HTTP_REDIRECT),
                            ],
                        },
                        "allow_unsolicited": True,
                        "authn_requests_signed": False,
                        "want_assertions_signed": True,
                        "want_response_signed": False,
                    },
                },
                "metadata": {"remote": [{"url": self.idp_metadata_url}]},
                "key_file": self.key_file,
                "cert_file": self.cert_file,
                "encryption_keypairs": [
                    {"key_file": self.key_file, "cert_file": self.cert_file},
                ],
            }

            self.saml_config = SamlConfig()
            self.saml_config.load(saml_config)
            self.saml_client = Saml2Client(self.saml_config)

        except Exception as e:
            logger.exception(f"Failed to initialize SAML client: {str(e)}")
            raise SSOConfigurationError(f"SAML configuration error: {str(e)}")

    async def authenticate(
        self,
        credentials: Dict[str, Any],
        db: Session,
    ) -> tuple[User, Dict[str, Any]]:
        """Authenticate user via SAML."""
        saml_response = credentials.get("saml_response")
        credentials.get("relay_state")

        if not saml_response:
            raise AuthenticationError("SAML response required")

        try:
            # Parse and validate SAML response
            authn_response = AuthnResponse(self.saml_config)
            authn_response.loads(saml_response, BINDING_HTTP_POST)

            if not authn_response.is_valid():
                raise AuthenticationError("Invalid SAML response")

            # Extract user attributes
            attributes = authn_response.ava
            username = attributes.get(self.attribute_mapping["username"], [""])[0]
            email = attributes.get(self.attribute_mapping["email"], [""])[0]
            first_name = attributes.get(self.attribute_mapping["first_name"], [""])[0]
            last_name = attributes.get(self.attribute_mapping["last_name"], [""])[0]
            groups = attributes.get(self.attribute_mapping["groups"], [])

            if not username:
                raise AuthenticationError("Username not found in SAML response")

            # Get or create user
            user = await self._get_or_create_user(
                username,
                email,
                first_name,
                last_name,
                db,
            )

            # Sync groups
            await self.sync_user_groups(user, groups, db)

            additional_data = {
                "saml_session_index": authn_response.session_index,
                "saml_name_id": authn_response.name_id,
                "saml_groups": groups,
                "provider": "saml",
                "last_sync": datetime.now(UTC).isoformat(),
            }

            return user, additional_data

        except Exception as e:
            logger.exception(f"SAML authentication failed: {str(e)}")
            raise AuthenticationError(f"SAML authentication failed: {str(e)}")

    async def get_user_info(self, user_id: str, db: Session) -> Dict[str, Any]:
        """Get user information from SAML provider."""
        # SAML doesn't support direct user info queries
        # Return cached information from database
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise UserNotFoundError("User not found")

        return {
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "provider": "saml",
            "last_sync": user.last_login.isoformat() if user.last_login else None,
        }

    async def sync_user_groups(self, user: User, db: Session) -> List[str]:
        """Synchronize user groups from SAML."""
        # This method signature differs from the base class
        # We need to handle the groups parameter differently
        return []

    async def sync_user_groups_with_groups(
        self,
        user: User,
        groups: List[str],
        db: Session,
    ) -> List[str]:
        """Synchronize user groups from SAML with provided groups."""
        try:
            app_groups = []
            for group in groups:
                if group in self.role_mapping:
                    # Map SAML groups to roles
                    mapped_role = self.role_mapping[group]
                    if user.role != mapped_role:
                        user.role = mapped_role
                        db.commit()

                # Create domain groups for SAML groups
                domain_group = await self._create_domain_group_from_saml(group, db)
                if domain_group:
                    app_groups.append(str(domain_group.id))

            return app_groups

        except Exception as e:
            logger.exception(f"Failed to sync SAML groups: {str(e)}")
            raise GroupSyncError(f"SAML group sync failed: {str(e)}")

    async def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate SAML token."""
        # SAML doesn't use traditional tokens
        return {"valid": False, "error": "Token validation not supported for SAML"}

    async def _get_or_create_user(
        self,
        username: str,
        email: str,
        first_name: str,
        last_name: str,
        db: Session,
    ) -> User:
        """Get existing user or create new one from SAML."""
        user = db.query(User).filter(User.username == username).first()

        if not user:
            # Create new user
            user = User(
                username=username,
                email=email,
                full_name=f"{first_name} {last_name}".strip(),
                auth_provider=AuthProvider.SAML,
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

    async def _create_domain_group_from_saml(
        self,
        saml_group: str,
        db: Session,
    ) -> DomainGroup | None:
        """Create domain group from SAML group."""
        try:
            # Check if domain group already exists
            existing_group = (
                db.query(DomainGroup)
                .filter(DomainGroup.external_id == f"saml:{saml_group}")
                .first()
            )

            if existing_group:
                return existing_group

            # Create new domain group
            domain_group = DomainGroup(
                name=saml_group,
                display_name=f"SAML Group: {saml_group}",
                domain_type="TEAM",
                external_id=f"saml:{saml_group}",
                tags=["saml", "auto-created"],
                is_system=True,
                settings={"saml_source": True},
            )

            db.add(domain_group)
            db.commit()
            db.refresh(domain_group)

            return domain_group

        except Exception as e:
            logger.exception(f"Failed to create domain group from SAML: {str(e)}")
            return None