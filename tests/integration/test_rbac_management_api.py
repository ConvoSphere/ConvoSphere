"""
Integration tests for RBAC Management API.

This module tests the RBAC management API endpoints including:
- Permission management (CRUD operations)
- ABAC rules and policies
- Permission testing and validation
- Performance monitoring
- Security events
- Cache management
"""

from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.permissions import PermissionAction, PermissionResource
from backend.app.models.user import User, UserRole


class TestRBACManagementAPI:
    """Test class for RBAC Management API endpoints."""

    @pytest.fixture
    def admin_user(self, db_session: Session) -> User:
        """Create admin user for testing."""
        admin = User(
            email="admin@test.com",
            username="admin",
            hashed_password="hashed_password",
            first_name="Admin",
            last_name="User",
            role=UserRole.ADMIN,
            is_active=True,
        )
        db_session.add(admin)
        db_session.commit()
        db_session.refresh(admin)
        return admin

    @pytest.fixture
    def regular_user(self, db_session: Session) -> User:
        """Create regular user for testing."""
        user = User(
            email="user@test.com",
            username="user",
            hashed_password="hashed_password",
            first_name="Regular",
            last_name="User",
            role=UserRole.USER,
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    @pytest.fixture
    def admin_headers(self, client: TestClient, admin_user: User) -> dict[str, str]:
        """Get admin authentication headers."""
        # Mock authentication
        with patch(
            "backend.app.api.v1.endpoints.rbac_management.get_current_user"
        ) as mock_auth:
            mock_auth.return_value = admin_user
            return {"Authorization": "Bearer admin-token"}

    @pytest.fixture
    def user_headers(self, client: TestClient, regular_user: User) -> dict[str, str]:
        """Get regular user authentication headers."""
        # Mock authentication
        with patch(
            "backend.app.api.v1.endpoints.rbac_management.get_current_user"
        ) as mock_auth:
            mock_auth.return_value = regular_user
            return {"Authorization": "Bearer user-token"}

    @pytest.fixture
    def sample_permission_data(self) -> dict[str, Any]:
        """Sample permission data for testing."""
        return {
            "name": "read_documents",
            "description": "Permission to read documents",
            "resource": PermissionResource.DOCUMENTS,
            "action": PermissionAction.READ,
            "is_active": True,
        }

    @pytest.fixture
    def sample_abac_rule_data(self) -> dict[str, Any]:
        """Sample ABAC rule data for testing."""
        return {
            "name": "time_based_access",
            "description": "Allow access only during business hours",
            "resource_type": "documents",
            "action": "read",
            "effect": "allow",
            "conditions": {"time": {"start": "09:00", "end": "17:00"}},
            "is_active": True,
        }

    @pytest.fixture
    def sample_abac_policy_data(self) -> dict[str, Any]:
        """Sample ABAC policy data for testing."""
        return {
            "name": "document_access_policy",
            "description": "Policy for document access control",
            "rules": ["time_based_access"],
            "priority": 1,
            "is_active": True,
        }

    def test_create_permission_success(
        self,
        client: TestClient,
        admin_headers: dict[str, str],
        sample_permission_data: dict[str, Any],
    ):
        """Test successful permission creation."""
        with patch(
            "backend.app.api.v1.endpoints.rbac_management.RBACService"
        ) as mock_rbac:
            mock_service = MagicMock()
            mock_permission = MagicMock()
            mock_permission.id = "perm_123"
            mock_permission.name = "read_documents"
            mock_service.create_permission.return_value = mock_permission
            mock_service._permission_to_response.return_value = {
                "id": "perm_123",
                "name": "read_documents",
                "description": "Permission to read documents",
                "resource": "documents",
                "action": "read",
                "is_active": True,
            }
            mock_rbac.return_value = mock_service

            response = client.post(
                "/api/v1/rbac/permissions",
                json=sample_permission_data,
                headers=admin_headers,
            )

            assert response.status_code == 201
            data = response.json()
            assert data["id"] == "perm_123"
            assert data["name"] == "read_documents"
            assert data["resource"] == "documents"
            assert data["action"] == "read"

    def test_create_permission_unauthorized(
        self,
        client: TestClient,
        user_headers: dict[str, str],
        sample_permission_data: dict[str, Any],
    ):
        """Test permission creation by unauthorized user."""
        with patch(
            "backend.app.api.v1.endpoints.rbac_management.RBACService"
        ) as mock_rbac:
            mock_service = MagicMock()
            mock_service.create_permission.side_effect = Exception("Permission denied")
            mock_rbac.return_value = mock_service

            response = client.post(
                "/api/v1/rbac/permissions",
                json=sample_permission_data,
                headers=user_headers,
            )

            assert response.status_code == 403

    def test_list_permissions_success(
        self, client: TestClient, admin_headers: dict[str, str]
    ):
        """Test successful permission listing."""
        with patch(
            "backend.app.api.v1.endpoints.rbac_management.RBACService"
        ) as mock_rbac:
            mock_service = MagicMock()
            mock_permission = MagicMock()
            mock_permission.id = "perm_123"
            mock_permission.name = "read_documents"
            mock_service.list_permissions.return_value = [mock_permission]
            mock_service._permission_to_response.return_value = {
                "id": "perm_123",
                "name": "read_documents",
                "description": "Permission to read documents",
                "resource": "documents",
                "action": "read",
                "is_active": True,
            }
            mock_rbac.return_value = mock_service

            response = client.get("/api/v1/rbac/permissions", headers=admin_headers)

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 1
            assert data[0]["id"] == "perm_123"

    def test_list_permissions_with_filters(
        self, client: TestClient, admin_headers: dict[str, str]
    ):
        """Test permission listing with filters."""
        with patch(
            "backend.app.api.v1.endpoints.rbac_management.RBACService"
        ) as mock_rbac:
            mock_service = MagicMock()
            mock_service.list_permissions.return_value = []
            mock_service._permission_to_response.return_value = {}
            mock_rbac.return_value = mock_service

            response = client.get(
                "/api/v1/rbac/permissions?resource=documents&action=read&is_active=true",
                headers=admin_headers,
            )

            assert response.status_code == 200
            mock_service.list_permissions.assert_called_once()

    def test_get_permission_success(
        self, client: TestClient, admin_headers: dict[str, str]
    ):
        """Test successful permission retrieval."""
        with patch(
            "backend.app.api.v1.endpoints.rbac_management.RBACService"
        ) as mock_rbac:
            mock_service = MagicMock()
            mock_permission = MagicMock()
            mock_permission.id = "perm_123"
            mock_service.get_permission_by_id.return_value = mock_permission
            mock_service._permission_to_response.return_value = {
                "id": "perm_123",
                "name": "read_documents",
                "description": "Permission to read documents",
                "resource": "documents",
                "action": "read",
                "is_active": True,
            }
            mock_rbac.return_value = mock_service

            response = client.get(
                "/api/v1/rbac/permissions/perm_123", headers=admin_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == "perm_123"

    def test_get_permission_not_found(
        self, client: TestClient, admin_headers: dict[str, str]
    ):
        """Test permission retrieval when not found."""
        with patch(
            "backend.app.api.v1.endpoints.rbac_management.RBACService"
        ) as mock_rbac:
            mock_service = MagicMock()
            mock_service.get_permission_by_id.return_value = None
            mock_rbac.return_value = mock_service

            response = client.get(
                "/api/v1/rbac/permissions/nonexistent", headers=admin_headers
            )

            assert response.status_code == 404

    def test_update_permission_success(
        self, client: TestClient, admin_headers: dict[str, str]
    ):
        """Test successful permission update."""
        update_data = {
            "description": "Updated permission description",
            "is_active": False,
        }

        with patch(
            "backend.app.api.v1.endpoints.rbac_management.RBACService"
        ) as mock_rbac:
            mock_service = MagicMock()
            mock_permission = MagicMock()
            mock_permission.id = "perm_123"
            mock_service.update_permission.return_value = mock_permission
            mock_service._permission_to_response.return_value = {
                "id": "perm_123",
                "name": "read_documents",
                "description": "Updated permission description",
                "resource": "documents",
                "action": "read",
                "is_active": False,
            }
            mock_rbac.return_value = mock_service

            response = client.put(
                "/api/v1/rbac/permissions/perm_123",
                json=update_data,
                headers=admin_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["description"] == "Updated permission description"
            assert data["is_active"] is False

    def test_delete_permission_success(
        self, client: TestClient, admin_headers: dict[str, str]
    ):
        """Test successful permission deletion."""
        with patch(
            "backend.app.api.v1.endpoints.rbac_management.RBACService"
        ) as mock_rbac:
            mock_service = MagicMock()
            mock_service.delete_permission.return_value = True
            mock_rbac.return_value = mock_service

            response = client.delete(
                "/api/v1/rbac/permissions/perm_123", headers=admin_headers
            )

            assert response.status_code == 204

    def test_create_abac_rule_success(
        self,
        client: TestClient,
        admin_headers: dict[str, str],
        sample_abac_rule_data: dict[str, Any],
    ):
        """Test successful ABAC rule creation."""
        with patch(
            "backend.app.api.v1.endpoints.rbac_management.RBACService"
        ) as mock_rbac:
            mock_service = MagicMock()
            mock_rule = MagicMock()
            mock_rule.id = "rule_123"
            mock_service.create_abac_rule.return_value = mock_rule
            mock_service._abac_rule_to_response.return_value = {
                "id": "rule_123",
                "name": "time_based_access",
                "description": "Allow access only during business hours",
                "resource_type": "documents",
                "action": "read",
                "effect": "allow",
                "is_active": True,
            }
            mock_rbac.return_value = mock_service

            response = client.post(
                "/api/v1/rbac/abac/rules",
                json=sample_abac_rule_data,
                headers=admin_headers,
            )

            assert response.status_code == 201
            data = response.json()
            assert data["id"] == "rule_123"
            assert data["name"] == "time_based_access"

    def test_list_abac_rules_success(
        self, client: TestClient, admin_headers: dict[str, str]
    ):
        """Test successful ABAC rules listing."""
        with patch(
            "backend.app.api.v1.endpoints.rbac_management.RBACService"
        ) as mock_rbac:
            mock_service = MagicMock()
            mock_rule = MagicMock()
            mock_rule.id = "rule_123"
            mock_service.list_abac_rules.return_value = [mock_rule]
            mock_service._abac_rule_to_response.return_value = {
                "id": "rule_123",
                "name": "time_based_access",
                "resource_type": "documents",
                "action": "read",
                "effect": "allow",
                "is_active": True,
            }
            mock_rbac.return_value = mock_service

            response = client.get("/api/v1/rbac/abac/rules", headers=admin_headers)

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 1
            assert data[0]["id"] == "rule_123"

    def test_get_abac_rule_success(
        self, client: TestClient, admin_headers: dict[str, str]
    ):
        """Test successful ABAC rule retrieval."""
        with patch(
            "backend.app.api.v1.endpoints.rbac_management.RBACService"
        ) as mock_rbac:
            mock_service = MagicMock()
            mock_rule = MagicMock()
            mock_rule.id = "rule_123"
            mock_service.get_abac_rule_by_id.return_value = mock_rule
            mock_service._abac_rule_to_response.return_value = {
                "id": "rule_123",
                "name": "time_based_access",
                "description": "Allow access only during business hours",
                "resource_type": "documents",
                "action": "read",
                "effect": "allow",
                "is_active": True,
            }
            mock_rbac.return_value = mock_service

            response = client.get(
                "/api/v1/rbac/abac/rules/rule_123", headers=admin_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == "rule_123"

    def test_update_abac_rule_success(
        self, client: TestClient, admin_headers: dict[str, str]
    ):
        """Test successful ABAC rule update."""
        update_data = {"description": "Updated rule description", "is_active": False}

        with patch(
            "backend.app.api.v1.endpoints.rbac_management.RBACService"
        ) as mock_rbac:
            mock_service = MagicMock()
            mock_rule = MagicMock()
            mock_rule.id = "rule_123"
            mock_service.update_abac_rule.return_value = mock_rule
            mock_service._abac_rule_to_response.return_value = {
                "id": "rule_123",
                "name": "time_based_access",
                "description": "Updated rule description",
                "resource_type": "documents",
                "action": "read",
                "effect": "allow",
                "is_active": False,
            }
            mock_rbac.return_value = mock_service

            response = client.put(
                "/api/v1/rbac/abac/rules/rule_123",
                json=update_data,
                headers=admin_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["description"] == "Updated rule description"
            assert data["is_active"] is False

    def test_delete_abac_rule_success(
        self, client: TestClient, admin_headers: dict[str, str]
    ):
        """Test successful ABAC rule deletion."""
        with patch(
            "backend.app.api.v1.endpoints.rbac_management.RBACService"
        ) as mock_rbac:
            mock_service = MagicMock()
            mock_service.delete_abac_rule.return_value = True
            mock_rbac.return_value = mock_service

            response = client.delete(
                "/api/v1/rbac/abac/rules/rule_123", headers=admin_headers
            )

            assert response.status_code == 204

    def test_create_abac_policy_success(
        self,
        client: TestClient,
        admin_headers: dict[str, str],
        sample_abac_policy_data: dict[str, Any],
    ):
        """Test successful ABAC policy creation."""
        with patch(
            "backend.app.api.v1.endpoints.rbac_management.RBACService"
        ) as mock_rbac:
            mock_service = MagicMock()
            mock_policy = MagicMock()
            mock_policy.id = "policy_123"
            mock_service.create_abac_policy.return_value = mock_policy
            mock_service._abac_policy_to_response.return_value = {
                "id": "policy_123",
                "name": "document_access_policy",
                "description": "Policy for document access control",
                "rules": ["time_based_access"],
                "priority": 1,
                "is_active": True,
            }
            mock_rbac.return_value = mock_service

            response = client.post(
                "/api/v1/rbac/abac/policies",
                json=sample_abac_policy_data,
                headers=admin_headers,
            )

            assert response.status_code == 201
            data = response.json()
            assert data["id"] == "policy_123"
            assert data["name"] == "document_access_policy"

    def test_list_abac_policies_success(
        self, client: TestClient, admin_headers: dict[str, str]
    ):
        """Test successful ABAC policies listing."""
        with patch(
            "backend.app.api.v1.endpoints.rbac_management.RBACService"
        ) as mock_rbac:
            mock_service = MagicMock()
            mock_policy = MagicMock()
            mock_policy.id = "policy_123"
            mock_service.list_abac_policies.return_value = [mock_policy]
            mock_service._abac_policy_to_response.return_value = {
                "id": "policy_123",
                "name": "document_access_policy",
                "description": "Policy for document access control",
                "rules": ["time_based_access"],
                "priority": 1,
                "is_active": True,
            }
            mock_rbac.return_value = mock_service

            response = client.get("/api/v1/rbac/abac/policies", headers=admin_headers)

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 1
            assert data[0]["id"] == "policy_123"

    def test_test_permission_success(
        self, client: TestClient, admin_headers: dict[str, str]
    ):
        """Test permission testing endpoint."""
        test_data = {
            "user_id": "user_123",
            "permission": "read_documents",
            "resource_id": "doc_456",
            "context": {"time": "14:30", "location": "office"},
        }

        with patch(
            "backend.app.api.v1.endpoints.rbac_management.RBACService"
        ) as mock_rbac:
            mock_service = MagicMock()
            mock_service.test_permission.return_value = {
                "allowed": True,
                "reason": "Permission granted",
                "applied_rules": ["time_based_access"],
            }
            mock_rbac.return_value = mock_service

            response = client.post(
                "/api/v1/rbac/test-permission", json=test_data, headers=admin_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["allowed"] is True
            assert "reason" in data

    def test_get_rbac_stats_success(
        self, client: TestClient, admin_headers: dict[str, str]
    ):
        """Test RBAC statistics endpoint."""
        with patch(
            "backend.app.api.v1.endpoints.rbac_management.RBACService"
        ) as mock_rbac:
            mock_service = MagicMock()
            mock_service.get_rbac_stats.return_value = {
                "total_permissions": 50,
                "total_roles": 10,
                "total_users": 100,
                "active_permissions": 45,
                "active_roles": 8,
                "active_users": 95,
            }
            mock_rbac.return_value = mock_service

            response = client.get("/api/v1/rbac/stats", headers=admin_headers)

            assert response.status_code == 200
            data = response.json()
            assert "total_permissions" in data
            assert "total_roles" in data
            assert "total_users" in data

    def test_get_cache_stats_success(
        self, client: TestClient, admin_headers: dict[str, str]
    ):
        """Test cache statistics endpoint."""
        with patch(
            "backend.app.api.v1.endpoints.rbac_management.rbac_cache"
        ) as mock_cache:
            mock_cache.get_stats.return_value = {
                "hits": 1000,
                "misses": 100,
                "hit_rate": 0.91,
                "size": 500,
                "max_size": 1000,
            }

            response = client.get("/api/v1/rbac/cache/stats", headers=admin_headers)

            assert response.status_code == 200
            data = response.json()
            assert "hits" in data
            assert "misses" in data
            assert "hit_rate" in data

    def test_get_performance_stats_success(
        self, client: TestClient, admin_headers: dict[str, str]
    ):
        """Test performance statistics endpoint."""
        with patch(
            "backend.app.api.v1.endpoints.rbac_management.rbac_performance_monitor"
        ) as mock_monitor:
            mock_monitor.get_user_stats.return_value = {
                "user_id": "user_123",
                "total_checks": 500,
                "avg_response_time": 0.05,
                "cache_hits": 450,
                "cache_misses": 50,
                "permissions": {"read_documents": {"checks": 200, "avg_time": 0.03}},
            }

            response = client.get(
                "/api/v1/rbac/performance/stats/user_123", headers=admin_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == "user_123"
            assert "total_checks" in data
            assert "avg_response_time" in data

    def test_clear_rbac_cache_success(
        self, client: TestClient, admin_headers: dict[str, str]
    ):
        """Test cache clearing endpoint."""
        with patch(
            "backend.app.api.v1.endpoints.rbac_management.rbac_cache"
        ) as mock_cache:
            mock_cache.clear.return_value = True

            response = client.post("/api/v1/rbac/cache/clear", headers=admin_headers)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    def test_clear_rbac_cache_for_user(
        self, client: TestClient, admin_headers: dict[str, str]
    ):
        """Test cache clearing for specific user."""
        with patch(
            "backend.app.api.v1.endpoints.rbac_management.rbac_cache"
        ) as mock_cache:
            mock_cache.clear_user_cache.return_value = True

            response = client.post(
                "/api/v1/rbac/cache/clear?user_id=user_123", headers=admin_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    def test_get_security_events_success(
        self, client: TestClient, admin_headers: dict[str, str]
    ):
        """Test security events endpoint."""
        with patch(
            "backend.app.api.v1.endpoints.rbac_management.RBACService"
        ) as mock_rbac:
            mock_service = MagicMock()
            mock_service.get_security_events.return_value = [
                {
                    "id": "event_123",
                    "timestamp": datetime.now(UTC).isoformat(),
                    "event_type": "permission_denied",
                    "user_id": "user_123",
                    "resource": "documents",
                    "action": "write",
                    "threat_level": "medium",
                    "details": "Unauthorized access attempt",
                }
            ]
            mock_rbac.return_value = mock_service

            response = client.get("/api/v1/rbac/security/events", headers=admin_headers)

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 1
            assert data[0]["event_type"] == "permission_denied"

    def test_get_security_events_with_filters(
        self, client: TestClient, admin_headers: dict[str, str]
    ):
        """Test security events with filters."""
        with patch(
            "backend.app.api.v1.endpoints.rbac_management.RBACService"
        ) as mock_rbac:
            mock_service = MagicMock()
            mock_service.get_security_events.return_value = []
            mock_rbac.return_value = mock_service

            response = client.get(
                "/api/v1/rbac/security/events?event_type=permission_denied&threat_level=high&user_id=user_123&limit=50",
                headers=admin_headers,
            )

            assert response.status_code == 200
            mock_service.get_security_events.assert_called_once()

    def test_get_permission_matrix_success(
        self, client: TestClient, admin_headers: dict[str, str]
    ):
        """Test permission matrix endpoint."""
        with patch(
            "backend.app.api.v1.endpoints.rbac_management.RBACService"
        ) as mock_rbac:
            mock_service = MagicMock()
            mock_service.get_permission_matrix.return_value = {
                "users": ["user_1", "user_2", "user_3"],
                "permissions": ["read", "write", "delete"],
                "matrix": [
                    [True, False, False],
                    [True, True, False],
                    [True, True, True],
                ],
            }
            mock_rbac.return_value = mock_service

            response = client.get(
                "/api/v1/rbac/permission-matrix", headers=admin_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert "users" in data
            assert "permissions" in data
            assert "matrix" in data

    def test_invalid_permission_data(
        self, client: TestClient, admin_headers: dict[str, str]
    ):
        """Test permission creation with invalid data."""
        invalid_data = {
            "name": "",  # Empty name
            "resource": "invalid_resource",  # Invalid resource
            "action": "invalid_action",  # Invalid action
        }

        response = client.post(
            "/api/v1/rbac/permissions", json=invalid_data, headers=admin_headers
        )

        assert response.status_code == 422

    def test_invalid_abac_rule_data(
        self, client: TestClient, admin_headers: dict[str, str]
    ):
        """Test ABAC rule creation with invalid data."""
        invalid_data = {
            "name": "",  # Empty name
            "resource_type": "",  # Empty resource type
            "action": "",  # Empty action
            "effect": "invalid_effect",  # Invalid effect
        }

        response = client.post(
            "/api/v1/rbac/abac/rules", json=invalid_data, headers=admin_headers
        )

        assert response.status_code == 422

    def test_permission_denied_error_handling(
        self, client: TestClient, admin_headers: dict[str, str]
    ):
        """Test handling of permission denied errors."""
        with patch(
            "backend.app.api.v1.endpoints.rbac_management.RBACService"
        ) as mock_rbac:
            mock_service = MagicMock()
            mock_service.create_permission.side_effect = Exception("Permission denied")
            mock_rbac.return_value = mock_service

            response = client.post(
                "/api/v1/rbac/permissions",
                json={"name": "test", "resource": "documents", "action": "read"},
                headers=admin_headers,
            )

            assert response.status_code == 403

    def test_database_error_handling(
        self, client: TestClient, admin_headers: dict[str, str]
    ):
        """Test handling of database errors."""
        with patch(
            "backend.app.api.v1.endpoints.rbac_management.RBACService"
        ) as mock_rbac:
            mock_service = MagicMock()
            mock_service.create_permission.side_effect = Exception("Database error")
            mock_rbac.return_value = mock_service

            response = client.post(
                "/api/v1/rbac/permissions",
                json={"name": "test", "resource": "documents", "action": "read"},
                headers=admin_headers,
            )

            assert response.status_code == 500

    def test_pagination_support(
        self, client: TestClient, admin_headers: dict[str, str]
    ):
        """Test pagination support in listing endpoints."""
        with patch(
            "backend.app.api.v1.endpoints.rbac_management.RBACService"
        ) as mock_rbac:
            mock_service = MagicMock()
            mock_service.list_permissions.return_value = []
            mock_service._permission_to_response.return_value = {}
            mock_rbac.return_value = mock_service

            response = client.get(
                "/api/v1/rbac/permissions?page=1&size=10", headers=admin_headers
            )

            assert response.status_code == 200

    def test_sorting_support(self, client: TestClient, admin_headers: dict[str, str]):
        """Test sorting support in listing endpoints."""
        with patch(
            "backend.app.api.v1.endpoints.rbac_management.RBACService"
        ) as mock_rbac:
            mock_service = MagicMock()
            mock_service.list_permissions.return_value = []
            mock_service._permission_to_response.return_value = {}
            mock_rbac.return_value = mock_service

            response = client.get(
                "/api/v1/rbac/permissions?sort_by=name&sort_order=desc",
                headers=admin_headers,
            )

            assert response.status_code == 200
