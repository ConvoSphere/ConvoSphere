"""
Unit tests for ToolService CRUD operations.

This module tests the basic CRUD functionality of the ToolService:
- Create tools
- Read tools (get by ID, get available)
- Update tools
- Delete tools
"""

import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

from backend.app.services.tool_service import ToolService
from backend.app.models.tool import Tool, ToolCategory
from backend.app.models.user import User, UserRole


class TestToolServiceCRUD:
    """Test suite for ToolService CRUD operations."""

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
            "version": "0.1.0-beta",
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
        tool.id = "550e8400-e29b-41d4-a716-446655440000"
        tool.name = "Test Tool"
        tool.description = "A test tool"
        tool.version = "0.1.0-beta"
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
            "version": "0.1.0-beta",
            "category": "search",
            "function_name": "test_function",
            "is_enabled": True,
            "requires_auth": False,
            "required_permissions": []
        }
        return tool

    # =============================================================================
    # FAST TESTS - Basic CRUD operations
    # =============================================================================

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_get_available_tools_success(self, tool_service, mock_tool):
        """Fast test for successful retrieval of available tools."""
        tool_service.db.query.return_value.filter.return_value.all.return_value = [mock_tool]
        
        result = tool_service.get_available_tools()
        
        assert len(result) == 1
        assert result[0]["id"] == "550e8400-e29b-41d4-a716-446655440000"
        assert result[0]["name"] == "Test Tool"

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_get_tool_by_id_success(self, tool_service, mock_tool):
        """Fast test for successful tool retrieval by ID."""
        tool_service.db.query.return_value.filter.return_value.first.return_value = mock_tool
        
        result = tool_service.get_tool_by_id("550e8400-e29b-41d4-a716-446655440000")
        
        assert result is not None
        assert result["id"] == "550e8400-e29b-41d4-a716-446655440000"
        assert result["name"] == "Test Tool"

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_create_tool_success(self, tool_service, sample_tool_data):
        """Fast test for successful tool creation."""
        mock_tool = MagicMock(spec=Tool)
        mock_tool.id = "new-tool-id"
        mock_tool.to_dict.return_value = {**sample_tool_data, "id": "new-tool-id"}
        
        tool_service.db.add.return_value = None
        tool_service.db.commit.return_value = None
        tool_service.db.refresh.return_value = None
        
        with patch('backend.app.services.tool_service.Tool', return_value=mock_tool):
            result = tool_service.create_tool(sample_tool_data, "user-123")
            
            assert result is not None
            assert result["id"] == "new-tool-id"
            tool_service.db.add.assert_called_once()
            tool_service.db.commit.assert_called_once()

    # =============================================================================
    # COMPREHENSIVE TESTS - Advanced CRUD operations and edge cases
    # =============================================================================

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_get_available_tools_with_user_id(self, tool_service, mock_tool):
        """Comprehensive test for getting available tools with user ID."""
        tool_service.db.query.return_value.filter.return_value.all.return_value = [mock_tool]
        
        result = tool_service.get_available_tools(user_id="user-123")
        
        assert len(result) == 1
        assert result[0]["id"] == "550e8400-e29b-41d4-a716-446655440000"

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_get_available_tools_with_category_filter(self, tool_service, mock_tool):
        """Comprehensive test for getting available tools with category filter."""
        tool_service.db.query.return_value.filter.return_value.all.return_value = [mock_tool]
        
        result = tool_service.get_available_tools(category="search")
        
        assert len(result) == 1
        assert result[0]["category"] == "search"

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_get_available_tools_invalid_category(self, tool_service):
        """Comprehensive test for getting tools with invalid category."""
        result = tool_service.get_available_tools(category="invalid_category")
        
        assert result == []

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_get_available_tools_database_error(self, tool_service):
        """Comprehensive test for database error handling."""
        tool_service.db.query.return_value.filter.return_value.all.side_effect = Exception("DB Error")
        
        with pytest.raises(Exception):
            tool_service.get_available_tools()

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_get_tool_by_id_not_found(self, tool_service):
        """Comprehensive test for tool not found."""
        tool_service.db.query.return_value.filter.return_value.first.return_value = None
        
        result = tool_service.get_tool_by_id("nonexistent-id")
        
        assert result is None

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_get_tool_by_id_invalid_uuid(self, tool_service):
        """Comprehensive test for invalid UUID handling."""
        result = tool_service.get_tool_by_id("invalid-uuid")
        
        assert result is None

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_create_tool_validation_error(self, tool_service, sample_tool_data):
        """Comprehensive test for tool creation validation error."""
        invalid_data = {**sample_tool_data}
        del invalid_data["name"]  # Remove required field
        
        with pytest.raises(ValueError):
            tool_service.create_tool(invalid_data, "user-123")

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_update_tool_success(self, tool_service, mock_tool):
        """Comprehensive test for successful tool update."""
        update_data = {"name": "Updated Tool", "description": "Updated description"}
        
        tool_service.db.query.return_value.filter.return_value.first.return_value = mock_tool
        tool_service.db.commit.return_value = None
        tool_service.db.refresh.return_value = None
        
        mock_tool.to_dict.return_value = {**mock_tool.to_dict.return_value, **update_data}
        
        result = tool_service.update_tool("550e8400-e29b-41d4-a716-446655440000", update_data, "user-123")
        
        assert result is not None
        assert result["name"] == "Updated Tool"
        tool_service.db.commit.assert_called_once()

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_update_tool_not_found(self, tool_service):
        """Comprehensive test for updating non-existent tool."""
        tool_service.db.query.return_value.filter.return_value.first.return_value = None
        
        result = tool_service.update_tool("nonexistent-id", {"name": "Updated"}, "user-123")
        
        assert result is None

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_delete_tool_success(self, tool_service, mock_tool):
        """Comprehensive test for successful tool deletion."""
        tool_service.db.query.return_value.filter.return_value.first.return_value = mock_tool
        tool_service.db.delete.return_value = None
        tool_service.db.commit.return_value = None
        
        result = tool_service.delete_tool("550e8400-e29b-41d4-a716-446655440000", "user-123")
        
        assert result is True
        tool_service.db.delete.assert_called_once_with(mock_tool)
        tool_service.db.commit.assert_called_once()

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_delete_tool_not_found(self, tool_service):
        """Comprehensive test for deleting non-existent tool."""
        tool_service.db.query.return_value.filter.return_value.first.return_value = None
        
        result = tool_service.delete_tool("nonexistent-id", "user-123")
        
        assert result is False

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_get_tools_by_category_success(self, tool_service, mock_tool):
        """Comprehensive test for getting tools by category."""
        tool_service.db.query.return_value.filter.return_value.all.return_value = [mock_tool]
        
        result = tool_service.get_tools_by_category("search")
        
        assert len(result) == 1
        assert result[0]["category"] == "search"

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_get_tools_by_category_invalid_category(self, tool_service):
        """Comprehensive test for invalid category handling."""
        result = tool_service.get_tools_by_category("invalid_category")
        
        assert result == []