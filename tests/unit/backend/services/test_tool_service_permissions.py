"""
Unit tests for ToolService permissions and authorization.

This module tests the permission checking and authorization functionality:
- User permission validation
- Tool access control
- Edit permissions
- Authentication requirements
"""

import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

from backend.app.services.tool_service import ToolService
from backend.app.models.tool import Tool, ToolCategory
from backend.app.models.user import User, UserRole


class TestToolServicePermissions:
    """Test suite for ToolService permissions and authorization."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return MagicMock(spec=Session)

    @pytest.fixture
    def tool_service(self, mock_db):
        """Create a ToolService instance with mocked database."""
        return ToolService(db=mock_db)

    @pytest.fixture
    def mock_tool(self):
        """Create a mock Tool instance."""
        tool = MagicMock(spec=Tool)
        tool.id = "550e8400-e29b-41d4-a716-446655440000"
        tool.name = "Test Tool"
        tool.description = "A test tool"
        tool.version = "0.1.2-beta"
        tool.category = ToolCategory.SEARCH
        tool.function_name = "test_function"
        tool.is_enabled = True
        tool.requires_auth = False
        tool.required_permissions = []
        tool.is_builtin = False
        tool.creator_id = "user-123"
        tool.to_dict.return_value = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "Test Tool",
            "description": "A test tool",
            "version": "0.1.2-beta",
            "category": "search",
            "function_name": "test_function",
            "is_enabled": True,
            "requires_auth": False,
            "required_permissions": []
        }
        return tool

    @pytest.fixture
    def mock_user(self):
        """Create a mock User instance."""
        user = MagicMock(spec=User)
        user.id = "user-123"
        user.role = UserRole.USER
        user.permissions = ["read", "write"]
        return user

    @pytest.fixture
    def mock_admin_user(self):
        """Create a mock admin User instance."""
        admin = MagicMock(spec=User)
        admin.id = "admin-123"
        admin.role = UserRole.ADMIN
        admin.permissions = ["read", "write", "admin"]
        return admin

    # =============================================================================
    # FAST TESTS - Basic permission checks
    # =============================================================================

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_check_user_permission_no_auth_required(self, tool_service, mock_tool):
        """Fast test for permission check when no auth is required."""
        result = tool_service.check_user_permission(mock_tool, None)
        
        assert result is True

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_can_edit_tool_admin_user(self, tool_service, mock_tool, mock_admin_user):
        """Fast test for admin user edit permission."""
        tool_service.db.query.return_value.filter.return_value.first.return_value = mock_admin_user
        
        result = tool_service.can_edit_tool(mock_tool, "admin-123")
        
        assert result is True

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_can_edit_tool_creator(self, tool_service, mock_tool, mock_user):
        """Fast test for tool creator edit permission."""
        tool_service.db.query.return_value.filter.return_value.first.return_value = mock_user
        
        result = tool_service.can_edit_tool(mock_tool, "user-123")
        
        assert result is True

    # =============================================================================
    # COMPREHENSIVE TESTS - Advanced permission scenarios and edge cases
    # =============================================================================

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_check_user_permission_auth_required_no_user(self, tool_service, mock_tool):
        """Comprehensive test for auth required but no user provided."""
        mock_tool.requires_auth = True
        mock_tool.required_permissions = ["read"]
        
        result = tool_service.check_user_permission(mock_tool, None)
        
        assert result is False

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_check_user_permission_with_permissions(self, tool_service, mock_tool, mock_user):
        """Comprehensive test for permission check with user permissions."""
        mock_tool.requires_auth = True
        mock_tool.required_permissions = ["read"]
        
        result = tool_service.check_user_permission(mock_tool, mock_user)
        
        assert result is True

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_check_user_permission_insufficient_permissions(self, tool_service, mock_tool, mock_user):
        """Comprehensive test for insufficient user permissions."""
        mock_tool.requires_auth = True
        mock_tool.required_permissions = ["admin"]  # User doesn't have admin permission
        
        result = tool_service.check_user_permission(mock_tool, mock_user)
        
        assert result is False

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_can_edit_tool_no_permission(self, tool_service, mock_tool, mock_user):
        """Comprehensive test for user without edit permission."""
        # Tool belongs to different user
        mock_tool.creator_id = "other-user-456"
        tool_service.db.query.return_value.filter.return_value.first.return_value = mock_user
        
        result = tool_service.can_edit_tool(mock_tool, "user-123")
        
        assert result is False

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_can_edit_tool_builtin_tool(self, tool_service, mock_tool, mock_admin_user):
        """Comprehensive test for builtin tool edit restrictions."""
        mock_tool.is_builtin = True
        tool_service.db.query.return_value.filter.return_value.first.return_value = mock_admin_user
        
        result = tool_service.can_edit_tool(mock_tool, "admin-123")
        
        assert result is False

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_can_edit_tool_user_not_found(self, tool_service, mock_tool):
        """Comprehensive test for non-existent user."""
        tool_service.db.query.return_value.filter.return_value.first.return_value = None
        
        result = tool_service.can_edit_tool(mock_tool, "nonexistent-user")
        
        assert result is False

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_get_tool_by_id_with_user_permission(self, tool_service, mock_tool, mock_user):
        """Comprehensive test for getting tool with user permission check."""
        tool_service.db.query.return_value.filter.return_value.first.return_value = mock_tool
        
        result = tool_service.get_tool_by_id("550e8400-e29b-41d4-a716-446655440000", user=mock_user)
        
        assert result is not None
        assert result["id"] == "550e8400-e29b-41d4-a716-446655440000"

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_update_tool_permission_denied(self, tool_service, mock_tool, mock_user):
        """Comprehensive test for update permission denied."""
        # Tool belongs to different user
        mock_tool.creator_id = "other-user-456"
        tool_service.db.query.return_value.filter.return_value.first.return_value = mock_user
        
        result = tool_service.update_tool("550e8400-e29b-41d4-a716-446655440000", {"name": "Updated"}, "user-123")
        
        assert result is None

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_delete_tool_permission_denied(self, tool_service, mock_tool, mock_user):
        """Comprehensive test for delete permission denied."""
        # Tool belongs to different user
        mock_tool.creator_id = "other-user-456"
        tool_service.db.query.return_value.filter.return_value.first.return_value = mock_user
        
        result = tool_service.delete_tool("550e8400-e29b-41d4-a716-446655440000", "user-123")
        
        assert result is False

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_permission_check_with_empty_permissions(self, tool_service, mock_tool, mock_user):
        """Comprehensive test for permission check with empty required permissions."""
        mock_tool.requires_auth = True
        mock_tool.required_permissions = []
        
        result = tool_service.check_user_permission(mock_tool, mock_user)
        
        assert result is True

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_permission_check_with_multiple_permissions(self, tool_service, mock_tool, mock_user):
        """Comprehensive test for permission check with multiple required permissions."""
        mock_tool.requires_auth = True
        mock_tool.required_permissions = ["read", "write"]
        
        result = tool_service.check_user_permission(mock_tool, mock_user)
        
        assert result is True

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_permission_check_partial_permissions(self, tool_service, mock_tool, mock_user):
        """Comprehensive test for permission check with partial permissions."""
        mock_tool.requires_auth = True
        mock_tool.required_permissions = ["read", "admin"]  # User has read but not admin
        
        result = tool_service.check_user_permission(mock_tool, mock_user)
        
        assert result is False