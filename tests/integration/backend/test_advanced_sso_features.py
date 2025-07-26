"""
Tests for advanced SSO features.

This module tests advanced SSO functionality including:
- Account linking/unlinking
- Advanced user provisioning
- Group/role mapping
- Bulk operations
"""

from unittest.mock import MagicMock, patch

import pytest
from backend.app.services.advanced_user_provisioning import (
    AdvancedUserProvisioning,
    AttributeMapper,
    ConditionalProvisioning,
    GroupRoleMapper,
)


class TestAttributeMapper:
    """Test cases for AttributeMapper."""

    @pytest.fixture
    def mapper(self):
        """Create AttributeMapper instance."""
        return AttributeMapper()

    def test_google_attribute_mapping(self, mapper):
        """Test Google OAuth attribute mapping."""
        sso_attributes = {
            "email": "test@example.com",
            "given_name": "John",
            "family_name": "Doe",
            "name": "John Doe",
            "picture": "https://example.com/avatar.jpg",
            "hd": "example.com",
            "groups": ["admin", "user"],
        }

        mapped = mapper.map_attributes("google", sso_attributes)

        assert mapped["email"] == "test@example.com"
        assert mapped["first_name"] == "John"
        assert mapped["last_name"] == "Doe"
        assert mapped["display_name"] == "John Doe"
        assert mapped["avatar_url"] == "https://example.com/avatar.jpg"
        assert mapped["domain"] == "example.com"
        assert mapped["groups"] == ["admin", "user"]

    def test_microsoft_attribute_mapping(self, mapper):
        """Test Microsoft OAuth attribute mapping."""
        sso_attributes = {
            "email": "test@example.com",
            "given_name": "Jane",
            "surname": "Smith",
            "display_name": "Jane Smith",
            "job_title": "Software Engineer",
            "department": "Engineering",
            "groups": ["Global Administrator"],
        }

        mapped = mapper.map_attributes("microsoft", sso_attributes)

        assert mapped["email"] == "test@example.com"
        assert mapped["first_name"] == "Jane"
        assert mapped["last_name"] == "Smith"
        assert mapped["display_name"] == "Jane Smith"
        assert mapped["job_title"] == "Software Engineer"
        assert mapped["department"] == "Engineering"
        assert mapped["groups"] == ["Global Administrator"]

    def test_saml_attribute_mapping(self, mapper):
        """Test SAML attribute mapping."""
        sso_attributes = {
            "email": "test@example.com",
            "givenName": "Bob",
            "sn": "Johnson",
            "displayName": "Bob Johnson",
            "department": "IT",
            "title": "System Administrator",
            "memberOf": ["cn=admins,dc=example,dc=com"],
        }

        mapped = mapper.map_attributes("saml", sso_attributes)

        assert mapped["email"] == "test@example.com"
        assert mapped["first_name"] == "Bob"
        assert mapped["last_name"] == "Johnson"
        assert mapped["display_name"] == "Bob Johnson"
        assert mapped["department"] == "IT"
        assert mapped["job_title"] == "System Administrator"
        assert mapped["groups"] == ["cn=admins,dc=example,dc=com"]

    def test_unknown_provider_mapping(self, mapper):
        """Test mapping with unknown provider."""
        sso_attributes = {"email": "test@example.com"}
        mapped = mapper.map_attributes("unknown", sso_attributes)
        assert mapped == {}


class TestGroupRoleMapper:
    """Test cases for GroupRoleMapper."""

    @pytest.fixture
    def mapper(self):
        """Create GroupRoleMapper instance."""
        return GroupRoleMapper()

    def test_google_group_mapping(self, mapper):
        """Test Google group to role mapping."""
        groups = ["admin", "team_lead", "user"]
        roles = mapper.map_groups_to_roles("google", groups)

        assert "admin" in roles
        assert "manager" in roles
        assert "user" in roles

    def test_microsoft_group_mapping(self, mapper):
        """Test Microsoft group to role mapping."""
        groups = ["Global Administrator", "Team Administrator", "User"]
        roles = mapper.map_groups_to_roles("microsoft", groups)

        assert "admin" in roles
        assert "manager" in roles
        assert "user" in roles

    def test_saml_group_mapping(self, mapper):
        """Test SAML group to role mapping."""
        groups = ["cn=admins,dc=example,dc=com", "cn=managers,dc=example,dc=com"]
        roles = mapper.map_groups_to_roles("saml", groups)

        assert "admin" in roles
        assert "manager" in roles

    def test_domain_role_mapping(self, mapper):
        """Test domain to role mapping."""
        email = "admin@admin.example.com"
        roles = mapper.map_domain_to_roles(email)

        assert "admin" in roles

        email = "manager@management.example.com"
        roles = mapper.map_domain_to_roles(email)

        assert "manager" in roles

    def test_unknown_domain_mapping(self, mapper):
        """Test domain mapping for unknown domain."""
        email = "user@unknown.com"
        roles = mapper.map_domain_to_roles(email)

        assert roles == []


class TestConditionalProvisioning:
    """Test cases for ConditionalProvisioning."""

    @pytest.fixture
    def provisioning(self):
        """Create ConditionalProvisioning instance."""
        return ConditionalProvisioning()

    def test_allowed_domain_provisioning(self, provisioning):
        """Test provisioning for allowed domain."""
        user_info = {"email": "user@example.com", "first_name": "John"}

        should_provision, reason = provisioning.should_provision_user(user_info)
        assert should_provision is True
        assert "allowed" in reason

    def test_blocked_domain_provisioning(self, provisioning):
        """Test provisioning for blocked domain."""
        user_info = {"email": "user@temp.com", "first_name": "John"}

        should_provision, reason = provisioning.should_provision_user(user_info)
        assert should_provision is False
        assert "blocked" in reason

    def test_missing_required_attributes(self, provisioning):
        """Test provisioning with missing required attributes."""
        user_info = {
            "email": "user@example.com",
            # Missing first_name
        }

        should_provision, reason = provisioning.should_provision_user(user_info)
        assert should_provision is False
        assert "Missing required attribute" in reason

    def test_auto_approve_domain(self, provisioning):
        """Test auto-approval for trusted domains."""
        user_info = {"email": "user@trusted-partner.com", "first_name": "John"}

        should_provision, reason = provisioning.should_provision_user(user_info)
        assert should_provision is True
        assert "Auto-approved" in reason

    def test_require_approval_domain(self, provisioning):
        """Test approval requirement for external domains."""
        user_info = {"email": "user@external-vendor.com", "first_name": "John"}

        should_provision, reason = provisioning.should_provision_user(user_info)
        assert should_provision is False
        assert "approval" in reason

    def test_provisioning_status(self, provisioning):
        """Test provisioning status determination."""
        # Approved user
        user_info = {"email": "user@example.com", "first_name": "John"}
        status = provisioning.get_provisioning_status(user_info)
        assert status == "approved"

        # Pending approval user
        user_info = {"email": "user@external-vendor.com", "first_name": "John"}
        status = provisioning.get_provisioning_status(user_info)
        assert status == "pending_approval"

        # Blocked user
        user_info = {"email": "user@temp.com", "first_name": "John"}
        status = provisioning.get_provisioning_status(user_info)
        assert status == "blocked"


class TestAdvancedUserProvisioning:
    """Test cases for AdvancedUserProvisioning."""

    @pytest.fixture
    def provisioning(self):
        """Create AdvancedUserProvisioning instance."""
        return AdvancedUserProvisioning()

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        return MagicMock()

    @pytest.fixture
    def mock_user_service(self):
        """Create mock user service."""
        return MagicMock()

    @pytest.mark.asyncio
    async def test_provision_user_approved(self, provisioning, mock_db, mock_user_service):
        """Test successful user provisioning."""
        user_info = {
            "email": "user@example.com",
            "external_id": "user123",
            "first_name": "John",
            "last_name": "Doe",
            "groups": ["admin", "user"],
        }

        # Mock user service
        with patch(
            "app.services.advanced_user_provisioning.UserService",
        ) as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.get_user_by_external_id.return_value = None

            # Mock user creation
            mock_user = MagicMock()
            mock_user.id = "user123"
            mock_user.email = "user@example.com"
            mock_service.create_sso_user.return_value = mock_user

            user, status, metadata = await provisioning.provision_user_advanced(
                user_info,
                "google",
                mock_db,
            )

            assert user is not None
            assert status == "approved"
            assert metadata["action"] == "created"
            assert "admin" in metadata["roles_assigned"]
            assert "user" in metadata["roles_assigned"]

    @pytest.mark.asyncio
    async def test_provision_user_blocked(self, provisioning, mock_db):
        """Test blocked user provisioning."""
        user_info = {
            "email": "user@temp.com",
            "external_id": "user123",
            "first_name": "John",
        }

        user, status, metadata = await provisioning.provision_user_advanced(
            user_info,
            "google",
            mock_db,
        )

        assert user is None
        assert status == "blocked"
        assert "blocked" in metadata["reason"]

    @pytest.mark.asyncio
    async def test_update_existing_user(self, provisioning, mock_db):
        """Test updating existing user."""
        user_info = {
            "email": "user@example.com",
            "external_id": "user123",
            "first_name": "John",
            "last_name": "Doe",
            "groups": ["admin"],
        }

        # Mock existing user
        existing_user = MagicMock()
        existing_user.email = "user@example.com"
        existing_user.sso_attributes = {}

        with patch(
            "app.services.advanced_user_provisioning.UserService",
        ) as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.get_user_by_external_id.return_value = existing_user

            user, status, metadata = await provisioning.provision_user_advanced(
                user_info,
                "google",
                mock_db,
            )

            assert user is not None
            assert status == "approved"
            assert metadata["action"] == "updated"
            assert "admin" in metadata["roles_assigned"]

    @pytest.mark.asyncio
    async def test_bulk_sync_users(self, provisioning, mock_db):
        """Test bulk user synchronization."""
        user_list = [
            {
                "email": "user1@example.com",
                "external_id": "user1",
                "first_name": "User1",
            },
            {"email": "user2@temp.com", "external_id": "user2", "first_name": "User2"},
        ]

        with patch.object(provisioning, "provision_user_advanced") as mock_provision:
            # Mock first user as created, second as blocked
            mock_provision.side_effect = [
                (MagicMock(), "approved", {"action": "created"}),
                (None, "blocked", {"reason": "blocked"}),
            ]

            results = await provisioning.bulk_sync_users("google", user_list, mock_db)

            assert results["total"] == 2
            assert results["created"] == 1
            assert results["skipped"] == 1
            assert results["errors"] == 0

    @pytest.mark.asyncio
    async def test_get_user_provisioning_status(self, provisioning, mock_db):
        """Test getting user provisioning status."""
        user_id = "user123"

        with patch(
            "app.services.advanced_user_provisioning.UserService",
        ) as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service

            # Mock user
            mock_user = MagicMock()
            mock_user.id = "user123"
            mock_user.email = "user@example.com"
            mock_user.auth_provider.value = "oauth_google"
            mock_user.sso_attributes = {
                "roles": ["admin", "user"],
                "groups": ["admin"],
                "last_sync": "2023-01-01T00:00:00Z",
                "provisioning_metadata": {"status": "approved"},
            }

            mock_service.get_user_by_id.return_value = mock_user

            status_info = await provisioning.get_user_provisioning_status(
                user_id,
                mock_db,
            )

            assert status_info["user_id"] == "user123"
            assert status_info["email"] == "user@example.com"
            assert status_info["auth_provider"] == "oauth_google"
            assert "admin" in status_info["roles"]
            assert "user" in status_info["roles"]

    @pytest.mark.asyncio
    async def test_get_user_provisioning_status_not_found(self, provisioning, mock_db):
        """Test getting provisioning status for non-existent user."""
        user_id = "nonexistent"

        with patch(
            "app.services.advanced_user_provisioning.UserService",
        ) as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.get_user_by_id.return_value = None

            status_info = await provisioning.get_user_provisioning_status(
                user_id,
                mock_db,
            )

            assert status_info["error"] == "User not found"


class TestAdvancedSSOIntegration:
    """Integration tests for advanced SSO features."""

    @pytest.mark.asyncio
    async def test_complete_user_provisioning_flow(self):
        """Test complete user provisioning flow with all components."""
        # Create instances
        provisioning = AdvancedUserProvisioning()
        mock_db = MagicMock()

        # Test user data
        user_info = {
            "email": "admin@admin.example.com",
            "external_id": "admin123",
            "first_name": "Admin",
            "last_name": "User",
            "groups": ["admin", "super_admin"],
            "sso_attributes": {
                "hd": "admin.example.com",
                "picture": "https://example.com/avatar.jpg",
            },
        }

        with patch(
            "app.services.advanced_user_provisioning.UserService",
        ) as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.get_user_by_external_id.return_value = None

            # Mock user creation
            mock_user = MagicMock()
            mock_user.id = "admin123"
            mock_user.email = "admin@admin.example.com"
            mock_service.create_sso_user.return_value = mock_user

            # Execute provisioning
            user, status, metadata = await provisioning.provision_user_advanced(
                user_info,
                "google",
                mock_db,
            )

            # Verify results
            assert user is not None
            assert status == "approved"
            assert metadata["action"] == "created"
            assert "admin" in metadata["roles_assigned"]  # From groups
            assert "admin" in metadata["roles_assigned"]  # From domain
            assert len(metadata["roles_assigned"]) == 1  # Duplicate removed

    @pytest.mark.asyncio
    async def test_conditional_provisioning_rules(self):
        """Test various conditional provisioning scenarios."""
        provisioning = AdvancedUserProvisioning()
        mock_db = MagicMock()

        test_cases = [
            {
                "user_info": {
                    "email": "user@example.com",
                    "external_id": "user1",
                    "first_name": "User1",
                },
                "expected_status": "approved",
                "expected_action": "created",
            },
            {
                "user_info": {
                    "email": "user@temp.com",
                    "external_id": "user2",
                    "first_name": "User2",
                },
                "expected_status": "blocked",
                "expected_action": None,
            },
            {
                "user_info": {
                    "email": "user@external-vendor.com",
                    "external_id": "user3",
                    "first_name": "User3",
                },
                "expected_status": "pending_approval",
                "expected_action": None,
            },
        ]

        for test_case in test_cases:
            user, status, metadata = await provisioning.provision_user_advanced(
                test_case["user_info"],
                "google",
                mock_db,
            )

            assert status == test_case["expected_status"]
            if test_case["expected_action"]:
                assert metadata["action"] == test_case["expected_action"]
            else:
                assert user is None
