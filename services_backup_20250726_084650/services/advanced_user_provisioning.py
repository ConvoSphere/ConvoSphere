"""
Advanced user provisioning service for SSO integration.

This module provides advanced user provisioning features including:
- Group and role mapping from SSO attributes
- Conditional user creation based on domain/attributes
- Attribute transformation and validation
- Bulk user provisioning
- User synchronization
"""

from datetime import datetime
from typing import Any

from app.models.user import AuthProvider, User
from app.schemas.user import SSOUserCreate
from app.services.user_service import UserService
from loguru import logger
from sqlalchemy.orm import Session


class AttributeMapper:
    """Maps SSO attributes to user fields and groups/roles."""

    def __init__(self):
        self.attribute_mappings = {
            "google": {
                "email": "email",
                "given_name": "first_name",
                "family_name": "last_name",
                "name": "display_name",
                "picture": "avatar_url",
                "hd": "domain",
                "groups": "groups",
            },
            "microsoft": {
                "email": "email",
                "given_name": "first_name",
                "surname": "last_name",
                "display_name": "display_name",
                "job_title": "job_title",
                "department": "department",
                "groups": "groups",
            },
            "github": {
                "email": "email",
                "name": "display_name",
                "login": "username",
                "avatar_url": "avatar_url",
                "company": "company",
                "location": "location",
            },
            "saml": {
                "email": "email",
                "givenName": "first_name",
                "sn": "last_name",
                "displayName": "display_name",
                "department": "department",
                "title": "job_title",
                "memberOf": "groups",
            },
        }

    def map_attributes(
        self,
        provider: str,
        sso_attributes: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Map SSO attributes to user fields.

        Args:
            provider: SSO provider name
            sso_attributes: Raw SSO attributes

        Returns:
            Dict: Mapped user attributes
        """
        mapping = self.attribute_mappings.get(provider, {})
        mapped = {}

        for sso_key, user_key in mapping.items():
            if sso_key in sso_attributes:
                mapped[user_key] = sso_attributes[sso_key]

        return mapped


class GroupRoleMapper:
    """Maps SSO groups to application roles and permissions."""

    def __init__(self):
        self.group_mappings = {
            "google": {
                "admin": ["admin", "administrator", "super_admin"],
                "manager": ["manager", "team_lead", "supervisor"],
                "user": ["user", "member", "employee"],
            },
            "microsoft": {
                "admin": ["Global Administrator", "User Administrator"],
                "manager": ["Team Administrator", "Group Administrator"],
                "user": ["User", "Guest User"],
            },
            "saml": {
                "admin": ["admin", "administrator", "cn=admins"],
                "manager": ["manager", "team_lead", "cn=managers"],
                "user": ["user", "member", "cn=users"],
            },
        }

        self.domain_mappings = {
            "admin": ["admin.example.com", "it.example.com"],
            "manager": ["management.example.com", "lead.example.com"],
            "user": ["example.com", "staff.example.com"],
        }

    def map_groups_to_roles(self, provider: str, groups: list[str]) -> list[str]:
        """
        Map SSO groups to application roles.

        Args:
            provider: SSO provider name
            groups: List of SSO groups

        Returns:
            List: Application roles
        """
        provider_mappings = self.group_mappings.get(provider, {})
        roles = []

        for group in groups:
            for role, group_patterns in provider_mappings.items():
                if any(pattern.lower() in group.lower() for pattern in group_patterns):
                    roles.append(role)

        return list(set(roles))  # Remove duplicates

    def map_domain_to_roles(self, email: str) -> list[str]:
        """
        Map email domain to roles.

        Args:
            email: User email address

        Returns:
            List: Application roles
        """
        domain = email.split("@")[1].lower()
        roles = []

        for role, allowed_domains in self.domain_mappings.items():
            if domain in allowed_domains:
                roles.append(role)

        return roles


class ConditionalProvisioning:
    """Handles conditional user provisioning based on rules."""

    def __init__(self):
        self.provisioning_rules = {
            "allowed_domains": ["example.com", "company.com"],
            "blocked_domains": ["temp.com", "test.com"],
            "required_attributes": ["email", "first_name"],
            "auto_approve_domains": ["trusted-partner.com"],
            "require_approval_domains": ["external-vendor.com"],
        }

    def should_provision_user(self, user_info: dict[str, Any]) -> tuple[bool, str]:
        """
        Determine if user should be provisioned based on rules.

        Args:
            user_info: User information from SSO

        Returns:
            Tuple[bool, str]: (should_provision, reason)
        """
        email = user_info.get("email", "")
        domain = email.split("@")[1].lower() if "@" in email else ""

        # Check blocked domains
        if domain in self.provisioning_rules["blocked_domains"]:
            return False, f"Domain {domain} is blocked"

        # Check required attributes
        for attr in self.provisioning_rules["required_attributes"]:
            if not user_info.get(attr):
                return False, f"Missing required attribute: {attr}"

        # Auto-approve trusted domains
        if domain in self.provisioning_rules["auto_approve_domains"]:
            return True, "Auto-approved trusted domain"

        # Require approval for external domains
        if domain in self.provisioning_rules["require_approval_domains"]:
            return False, "Requires manual approval"

        # Default allow for allowed domains
        if domain in self.provisioning_rules["allowed_domains"]:
            return True, "Domain in allowed list"

        return False, "Domain not in allowed list"

    def get_provisioning_status(self, user_info: dict[str, Any]) -> str:
        """
        Get provisioning status for user.

        Args:
            user_info: User information from SSO

        Returns:
            str: Provisioning status
        """
        should_provision, reason = self.should_provision_user(user_info)

        if should_provision:
            return "approved"
        if "approval" in reason.lower():
            return "pending_approval"
        return "blocked"


class AdvancedUserProvisioning:
    """Advanced user provisioning service."""

    def __init__(self):
        self.attribute_mapper = AttributeMapper()
        self.group_role_mapper = GroupRoleMapper()
        self.conditional_provisioning = ConditionalProvisioning()

    async def provision_user_advanced(
        self,
        user_info: dict[str, Any],
        provider: str,
        db: Session,
    ) -> tuple[User | None, str, dict[str, Any]]:
        """
        Advanced user provisioning with group/role mapping and conditional logic.

        Args:
            user_info: Raw user information from SSO
            provider: SSO provider name
            db: Database session

        Returns:
            Tuple[Optional[User], str, Dict]: (user, status, metadata)
        """
        try:
            # Check conditional provisioning rules
            should_provision, reason = (
                self.conditional_provisioning.should_provision_user(user_info)
            )
            status = self.conditional_provisioning.get_provisioning_status(user_info)

            if not should_provision:
                logger.warning(f"User provisioning blocked: {reason}")
                return None, status, {"reason": reason}

            # Map SSO attributes to user fields
            mapped_attributes = self.attribute_mapper.map_attributes(
                provider,
                user_info,
            )

            # Extract groups and map to roles
            groups = user_info.get("groups", [])
            if isinstance(groups, str):
                groups = [groups]

            roles = self.group_role_mapper.map_groups_to_roles(provider, groups)

            # Add domain-based roles
            domain_roles = self.group_role_mapper.map_domain_to_roles(
                user_info["email"],
            )
            roles.extend(domain_roles)
            roles = list(set(roles))  # Remove duplicates

            # Create enhanced user data
            enhanced_user_info = {
                **user_info,
                **mapped_attributes,
                "roles": roles,
                "groups": groups,
                "provisioning_metadata": {
                    "provider": provider,
                    "provisioned_at": datetime.utcnow().isoformat(),
                    "status": status,
                    "reason": reason,
                },
            }

            # Create or update user
            user_service = UserService(db)
            auth_provider = self._get_auth_provider(provider)

            # Check if user exists
            existing_user = user_service.get_user_by_external_id(
                user_info["external_id"],
                auth_provider,
            )

            if existing_user:
                # Update existing user
                user = await self._update_existing_user(
                    existing_user,
                    enhanced_user_info,
                    db,
                )
                action = "updated"
            else:
                # Create new user
                user = await self._create_new_user(
                    enhanced_user_info,
                    auth_provider,
                    db,
                )
                action = "created"

            metadata = {
                "action": action,
                "roles_assigned": roles,
                "groups_mapped": groups,
                "provisioning_status": status,
                "reason": reason,
            }

            logger.info(
                f"Advanced user provisioning {action} user {user.email} with roles: {roles}",
            )
            return user, status, metadata

        except Exception as e:
            logger.error(f"Advanced user provisioning failed: {e}")
            return None, "error", {"error": str(e)}

    async def _update_existing_user(
        self,
        user: User,
        user_info: dict[str, Any],
        db: Session,
    ) -> User:
        """Update existing user with new SSO information."""
        # Update basic fields
        if user_info.get("first_name"):
            user.first_name = user_info["first_name"]
        if user_info.get("last_name"):
            user.last_name = user_info["last_name"]
        if user_info.get("display_name"):
            user.display_name = user_info["display_name"]
        if user_info.get("avatar_url"):
            user.avatar_url = user_info["avatar_url"]

        # Update SSO attributes
        user.sso_attributes = {
            **user.sso_attributes,
            **user_info.get("sso_attributes", {}),
            "roles": user_info.get("roles", []),
            "groups": user_info.get("groups", []),
            "last_sync": datetime.utcnow().isoformat(),
        }

        db.commit()
        return user

    async def _create_new_user(
        self,
        user_info: dict[str, Any],
        auth_provider: AuthProvider,
        db: Session,
    ) -> User:
        """Create new user with advanced provisioning."""
        user_service = UserService(db)

        sso_user_data = SSOUserCreate(
            email=user_info["email"],
            username=user_info.get("username") or user_info["email"].split("@")[0],
            first_name=user_info.get("first_name"),
            last_name=user_info.get("last_name"),
            display_name=user_info.get("display_name"),
            avatar_url=user_info.get("avatar_url"),
            auth_provider=auth_provider,
            external_id=user_info["external_id"],
            sso_attributes={
                **user_info.get("sso_attributes", {}),
                "roles": user_info.get("roles", []),
                "groups": user_info.get("groups", []),
                "provisioning_metadata": user_info.get("provisioning_metadata", {}),
            },
        )

        return user_service.create_sso_user(sso_user_data)

    def _get_auth_provider(self, provider: str) -> AuthProvider:
        """Convert provider string to AuthProvider enum."""
        provider_mapping = {
            "google": AuthProvider.OAUTH_GOOGLE,
            "microsoft": AuthProvider.OAUTH_MICROSOFT,
            "github": AuthProvider.OAUTH_GITHUB,
            "saml": AuthProvider.SAML,
        }
        return provider_mapping.get(provider, AuthProvider.LOCAL)

    async def bulk_sync_users(
        self,
        provider: str,
        user_list: list[dict[str, Any]],
        db: Session,
    ) -> dict[str, Any]:
        """
        Bulk sync users from SSO provider.

        Args:
            provider: SSO provider name
            user_list: List of users from SSO
            db: Database session

        Returns:
            Dict: Sync results
        """
        results = {
            "total": len(user_list),
            "created": 0,
            "updated": 0,
            "skipped": 0,
            "errors": 0,
            "details": [],
        }

        for user_info in user_list:
            try:
                user, status, metadata = await self.provision_user_advanced(
                    user_info,
                    provider,
                    db,
                )

                if user:
                    if metadata["action"] == "created":
                        results["created"] += 1
                    else:
                        results["updated"] += 1
                elif status == "blocked":
                    results["skipped"] += 1
                else:
                    results["errors"] += 1

                results["details"].append(
                    {
                        "email": user_info.get("email"),
                        "status": status,
                        "metadata": metadata,
                    },
                )

            except Exception as e:
                results["errors"] += 1
                results["details"].append(
                    {
                        "email": user_info.get("email"),
                        "status": "error",
                        "metadata": {"error": str(e)},
                    },
                )

        logger.info(f"Bulk sync completed: {results}")
        return results

    async def get_user_provisioning_status(
        self,
        user_id: str,
        db: Session,
    ) -> dict[str, Any]:
        """
        Get provisioning status for a user.

        Args:
            user_id: User ID
            db: Database session

        Returns:
            Dict: Provisioning status information
        """
        user_service = UserService(db)
        user = user_service.get_user_by_id(user_id)

        if not user:
            return {"error": "User not found"}

        sso_attrs = user.sso_attributes or {}

        return {
            "user_id": user.id,
            "email": user.email,
            "auth_provider": user.auth_provider.value,
            "roles": sso_attrs.get("roles", []),
            "groups": sso_attrs.get("groups", []),
            "last_sync": sso_attrs.get("last_sync"),
            "provisioning_metadata": sso_attrs.get("provisioning_metadata", {}),
        }


# Global instance
advanced_user_provisioning = AdvancedUserProvisioning()
