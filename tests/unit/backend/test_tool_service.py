"""
Comprehensive tests for ToolService.

This module tests all tool management functionality including:
- Tool CRUD operations
- Permission checking
- Category filtering
- Search functionality
- Error handling
"""

import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

from backend.app.services.tool_service import ToolService
from backend.app.models.tool import Tool, ToolCategory
from backend.app.models.user import User, UserRole


class TestToolService:
    """Test suite for ToolService."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return MagicMock(spec=Session)

    @pytest.fixture
    def tool_service(self, mock_db):
        """Create a ToolService instance with mocked database."""
        return ToolService(db=mock_db)

    @pytest.fixture
    def sample_tool_data(self):
        """Sample tool data for testing."""
        return {
            "name": "Test Tool",
            "description": "A test tool for testing",
            "version": "1.0.0",
            "category": "search",
            "function_name": "test_function",
            "parameters_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"]
            },
            "implementation_path": "tools.test_function",
            "is_builtin": False,
            "is_enabled": True,
            "requires_auth": False,
            "required_permissions": [],
            "rate_limit": "100/hour",
            "tags": ["test", "search"],
            "tool_metadata": {"test": True}
        }

    @pytest.fixture
    def mock_tool(self):
        """Create a mock Tool instance."""
        tool = MagicMock(spec=Tool)
        tool.id = "550e8400-e29b-41d4-a716-446655440000"  # Valid UUID
        tool.name = "Test Tool"
        tool.description = "A test tool"
        tool.version = "1.0.0"
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
            "version": "1.0.0",
            "category": "search",
            "function_name": "test_function",
            "is_enabled": True,
            "requires_auth": False,
            "required_permissions": []
        }
        return tool

    @pytest.mark.unit
    @pytest.mark.service
    def test_get_available_tools_success(self, tool_service, mock_tool):
        """Test successful retrieval of available tools."""
        # Setup mock
        tool_service.db.query.return_value.filter.return_value.all.return_value = [mock_tool]
        
        # Test without user_id
        result = tool_service.get_available_tools()
        
        assert len(result) == 1
        assert result[0]["id"] == "550e8400-e29b-41d4-a716-446655440000"
        assert result[0]["name"] == "Test Tool"
        assert result[0]["can_use"] is True  # No auth required
        
        # Verify database query was called
        tool_service.db.query.assert_called_once_with(Tool)
        tool_service.db.query.return_value.filter.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.service
    def test_get_available_tools_with_user_id(self, tool_service, mock_tool):
        """Test retrieval of available tools with user permission checking."""
        # Setup mock
        tool_service.db.query.return_value.filter.return_value.all.return_value = [mock_tool]
        
        # Mock permission check
        with patch.object(tool_service, '_check_user_permission', return_value=True):
            result = tool_service.get_available_tools(user_id="user-123")
            
            assert len(result) == 1
            assert result[0]["can_use"] is True
            tool_service._check_user_permission.assert_called_once_with(mock_tool, "user-123")

    @pytest.mark.unit
    @pytest.mark.service
    def test_get_available_tools_with_category_filter(self, tool_service, mock_tool):
        """Test retrieval of available tools with category filtering."""
        # Setup mock
        tool_service.db.query.return_value.filter.return_value.filter.return_value.all.return_value = [mock_tool]
        
        result = tool_service.get_available_tools(category="search")
        
        assert len(result) == 1
        assert result[0]["category"] == "search"
        
        # Verify category filter was applied
        tool_service.db.query.return_value.filter.return_value.filter.assert_called()

    @pytest.mark.unit
    @pytest.mark.service
    def test_get_available_tools_invalid_category(self, tool_service):
        """Test retrieval with invalid category."""
        result = tool_service.get_available_tools(category="invalid_category")
        
        assert result == []

    @pytest.mark.unit
    @pytest.mark.service
    def test_get_available_tools_database_error(self, tool_service):
        """Test handling of database errors."""
        # Setup mock to raise exception
        tool_service.db.query.side_effect = Exception("Database error")
        
        result = tool_service.get_available_tools()
        
        assert result == []

    @pytest.mark.unit
    @pytest.mark.service
    def test_get_tool_by_id_success(self, tool_service, mock_tool):
        """Test successful retrieval of tool by ID."""
        # Setup mock
        tool_service.db.query.return_value.filter.return_value.first.return_value = mock_tool
        
        result = tool_service.get_tool_by_id("550e8400-e29b-41d4-a716-446655440000")
        
        assert result is not None
        assert result["id"] == "550e8400-e29b-41d4-a716-446655440000"
        assert result["name"] == "Test Tool"
        
        # Verify database query was called
        tool_service.db.query.assert_called_once_with(Tool)

    @pytest.mark.unit
    @pytest.mark.service
    def test_get_tool_by_id_not_found(self, tool_service):
        """Test retrieval of non-existent tool."""
        # Setup mock
        tool_service.db.query.return_value.filter.return_value.first.return_value = None
        
        result = tool_service.get_tool_by_id("tool-123")
        
        assert result is None

    @pytest.mark.unit
    @pytest.mark.service
    def test_get_tool_by_id_invalid_uuid(self, tool_service):
        """Test retrieval with invalid UUID format."""
        result = tool_service.get_tool_by_id("invalid-uuid")
        
        assert result is None

    @pytest.mark.unit
    @pytest.mark.service
    def test_get_tool_by_id_with_user_permission(self, tool_service, mock_tool):
        """Test retrieval of tool with user permission checking."""
        # Setup mock
        tool_service.db.query.return_value.filter.return_value.first.return_value = mock_tool
        
        # Mock permission check
        with patch.object(tool_service, '_check_user_permission', return_value=True):
            result = tool_service.get_tool_by_id("550e8400-e29b-41d4-a716-446655440000", user_id="user-123")
            
            assert result is not None
            assert result["can_use"] is True
            tool_service._check_user_permission.assert_called_once_with(mock_tool, "user-123")

    @pytest.mark.unit
    @pytest.mark.service
    def test_create_tool_success(self, tool_service, sample_tool_data):
        """Test successful tool creation."""
        # Setup mock
        mock_tool = MagicMock(spec=Tool)
        mock_tool.id = "new-tool-123"
        mock_tool.to_dict.return_value = {
            "id": "new-tool-123",
            "name": "Test Tool",
            "description": "A test tool for testing",
            "category": "search",
            "function_name": "test_function",
            "creator_id": "user-123"
        }
        
        tool_service.db.add.return_value = None
        tool_service.db.commit.return_value = None
        tool_service.db.refresh.return_value = None
        
        # Mock existing tool check to return None (no existing tool)
        tool_service.db.query.return_value.filter.return_value.first.return_value = None
        
        # Mock Tool constructor
        with patch('backend.app.services.tool_service.Tool', return_value=mock_tool):
            result = tool_service.create_tool(sample_tool_data, "user-123")
            
            assert result is not None
            assert result["id"] == "new-tool-123"
            assert result["name"] == "Test Tool"
            
            # Verify database operations
            tool_service.db.add.assert_called_once()
            tool_service.db.commit.assert_called_once()
            tool_service.db.refresh.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.service
    def test_create_tool_validation_error(self, tool_service, sample_tool_data):
        """Test tool creation with validation error."""
        # Setup mock to raise exception
        tool_service.db.add.side_effect = Exception("Validation error")
        tool_service.db.rollback.return_value = None
        
        result = tool_service.create_tool(sample_tool_data, "user-123")
        
        assert result is None
        tool_service.db.rollback.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.service
    def test_update_tool_success(self, tool_service, mock_tool):
        """Test successful tool update."""
        # Setup mock
        tool_service.db.query.return_value.filter.return_value.first.return_value = mock_tool
        tool_service.db.commit.return_value = None
        tool_service.db.refresh.return_value = None
        
        # Mock permission check
        with patch.object(tool_service, '_can_edit_tool', return_value=True):
            update_data = {
                "name": "Updated Tool",
                "description": "Updated description"
            }
            
            result = tool_service.update_tool("tool-123", update_data, "user-123")
            
            assert result is not None
            assert result["name"] == "Test Tool"  # From mock_tool.to_dict()
            
            # Verify database operations
            tool_service.db.commit.assert_called_once()
            tool_service.db.refresh.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.service
    def test_update_tool_not_found(self, tool_service):
        """Test update of non-existent tool."""
        # Setup mock
        tool_service.db.query.return_value.filter.return_value.first.return_value = None
        
        update_data = {"name": "Updated Tool"}
        result = tool_service.update_tool("tool-123", update_data, "user-123")
        
        assert result is None

    @pytest.mark.unit
    @pytest.mark.service
    def test_update_tool_permission_denied(self, tool_service, mock_tool):
        """Test tool update without permission."""
        # Setup mock
        tool_service.db.query.return_value.filter.return_value.first.return_value = mock_tool
        
        # Mock permission check
        with patch.object(tool_service, '_can_edit_tool', return_value=False):
            update_data = {"name": "Updated Tool"}
            result = tool_service.update_tool("tool-123", update_data, "user-123")
            
            assert result is None

    @pytest.mark.unit
    @pytest.mark.service
    def test_delete_tool_success(self, tool_service, mock_tool):
        """Test successful tool deletion."""
        # Setup mock
        tool_service.db.query.return_value.filter.return_value.first.return_value = mock_tool
        tool_service.db.delete.return_value = None
        tool_service.db.commit.return_value = None
        
        # Mock permission check
        with patch.object(tool_service, '_can_edit_tool', return_value=True):
            result = tool_service.delete_tool("550e8400-e29b-41d4-a716-446655440000", "user-123")
            
            assert result is True
            
            # Verify database operations
            tool_service.db.delete.assert_called_once_with(mock_tool)
            tool_service.db.commit.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.service
    def test_delete_tool_not_found(self, tool_service):
        """Test deletion of non-existent tool."""
        # Setup mock
        tool_service.db.query.return_value.filter.return_value.first.return_value = None
        
        result = tool_service.delete_tool("tool-123", "user-123")
        
        assert result is False

    @pytest.mark.unit
    @pytest.mark.service
    def test_delete_tool_permission_denied(self, tool_service, mock_tool):
        """Test tool deletion without permission."""
        # Setup mock
        tool_service.db.query.return_value.filter.return_value.first.return_value = mock_tool
        
        # Mock permission check
        with patch.object(tool_service, '_can_edit_tool', return_value=False):
            result = tool_service.delete_tool("tool-123", "user-123")
            
            assert result is False

    @pytest.mark.unit
    @pytest.mark.service
    def test_get_tools_by_category_success(self, tool_service, mock_tool):
        """Test successful retrieval of tools by category."""
        # Setup mock for get_available_tools call
        with patch.object(tool_service, 'get_available_tools', return_value=[mock_tool.to_dict()]):
            result = tool_service.get_tools_by_category("search", "user-123")
            
            assert len(result) == 1
            assert result[0]["category"] == "search"

    @pytest.mark.unit
    @pytest.mark.service
    def test_get_tools_by_category_invalid_category(self, tool_service):
        """Test retrieval with invalid category."""
        result = tool_service.get_tools_by_category("invalid_category", "user-123")
        
        assert result == []

    @pytest.mark.unit
    @pytest.mark.service
    def test_search_tools_success(self, tool_service, mock_tool):
        """Test successful tool search."""
        # Setup mock
        tool_service.db.query.return_value.filter.return_value.all.return_value = [mock_tool]
        
        result = tool_service.search_tools("test", "user-123")
        
        assert len(result) == 1
        assert result[0]["name"] == "Test Tool"

    @pytest.mark.unit
    @pytest.mark.service
    def test_search_tools_empty_query(self, tool_service):
        """Test search with empty query."""
        result = tool_service.search_tools("", "user-123")
        
        assert result == []

    @pytest.mark.unit
    @pytest.mark.service
    def test_check_user_permission_no_auth_required(self, tool_service, mock_tool):
        """Test permission check for tool that doesn't require auth."""
        mock_tool.requires_auth = False
        
        result = tool_service._check_user_permission(mock_tool, "user-123")
        
        assert result is True

    @pytest.mark.unit
    @pytest.mark.service
    def test_check_user_permission_auth_required_no_user(self, tool_service, mock_tool):
        """Test permission check for tool that requires auth but no user provided."""
        mock_tool.requires_auth = True
        
        # Mock database query to return None (no user found)
        tool_service.db.query.return_value.filter.return_value.first.return_value = None
        
        result = tool_service._check_user_permission(mock_tool, "user-123")
        
        assert result is False

    @pytest.mark.unit
    @pytest.mark.service
    def test_check_user_permission_with_permissions(self, tool_service, mock_tool):
        """Test permission check for tool with specific permissions."""
        mock_tool.requires_auth = True
        mock_tool.required_permissions = ["admin", "tool_edit"]
        
        # Mock user with permissions
        mock_user = MagicMock(spec=User)
        mock_user.role = UserRole.ADMIN
        mock_user.permissions = ["admin", "tool_edit"]
        
        tool_service.db.query.return_value.filter.return_value.first.return_value = mock_user
        
        result = tool_service._check_user_permission(mock_tool, "user-123")
        
        assert result is True

    @pytest.mark.unit
    @pytest.mark.service
    def test_check_user_permission_insufficient_permissions(self, tool_service, mock_tool):
        """Test permission check with insufficient permissions."""
        mock_tool.requires_auth = True
        mock_tool.required_permissions = ["admin"]
        
        # Mock user without required permissions
        mock_user = MagicMock(spec=User)
        mock_user.role = UserRole.USER
        mock_user.is_active = True
        mock_user.has_permission.return_value = False
        
        tool_service.db.query.return_value.filter.return_value.first.return_value = mock_user
        
        result = tool_service._check_user_permission(mock_tool, "user-123")
        
        assert result is False

    @pytest.mark.unit
    @pytest.mark.service
    def test_can_edit_tool_admin_user(self, tool_service, mock_tool):
        """Test edit permission for admin user."""
        # Mock user as admin
        mock_user = MagicMock(spec=User)
        mock_user.role = UserRole.ADMIN
        
        tool_service.db.query.return_value.filter.return_value.first.return_value = mock_user
        
        result = tool_service._can_edit_tool(mock_tool, "user-123")
        
        assert result is True

    @pytest.mark.unit
    @pytest.mark.service
    def test_can_edit_tool_creator(self, tool_service, mock_tool):
        """Test edit permission for tool creator."""
        # Mock user as regular user but creator of tool
        mock_user = MagicMock(spec=User)
        mock_user.role = UserRole.USER
        mock_tool.creator_id = "user-123"
        
        tool_service.db.query.return_value.filter.return_value.first.return_value = mock_user
        
        result = tool_service._can_edit_tool(mock_tool, "user-123")
        
        assert result is True

    @pytest.mark.unit
    @pytest.mark.service
    def test_can_edit_tool_no_permission(self, tool_service, mock_tool):
        """Test edit permission for user without permission."""
        # Mock user as regular user, not creator
        mock_user = MagicMock(spec=User)
        mock_user.role = UserRole.USER
        mock_tool.creator_id = "other-user"
        
        tool_service.db.query.return_value.filter.return_value.first.return_value = mock_user
        
        result = tool_service._can_edit_tool(mock_tool, "user-123")
        
        assert result is False

    @pytest.mark.unit
    @pytest.mark.service
    def test_can_edit_tool_builtin_tool(self, tool_service, mock_tool):
        """Test edit permission for builtin tool."""
        mock_tool.is_builtin = True
        
        # Mock user as admin
        mock_user = MagicMock(spec=User)
        mock_user.role.value = "admin"
        mock_user.is_active = True
        
        tool_service.db.query.return_value.filter.return_value.first.return_value = mock_user
        
        result = tool_service._can_edit_tool(mock_tool, "user-123")
        
        assert result is True  # Admin can edit any tool, including builtin

    @pytest.mark.unit
    @pytest.mark.service
    def test_can_edit_tool_user_not_found(self, tool_service, mock_tool):
        """Test edit permission when user not found."""
        tool_service.db.query.return_value.filter.return_value.first.return_value = None
        
        result = tool_service._can_edit_tool(mock_tool, "user-123")
        
        assert result is False