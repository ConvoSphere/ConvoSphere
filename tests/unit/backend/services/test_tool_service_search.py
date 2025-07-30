"""
Unit tests for ToolService search and filtering functionality.

This module tests the search and filtering capabilities:
- Tool search by query
- Category filtering
- Tag-based filtering
- Advanced search options
"""

import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

from backend.app.services.tool_service import ToolService
from backend.app.models.tool import Tool, ToolCategory
from backend.app.models.user import User, UserRole


class TestToolServiceSearch:
    """Test suite for ToolService search and filtering functionality."""

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
        tool.description = "A test tool for testing"
        tool.version = "0.1.0-beta"
        tool.category = ToolCategory.SEARCH
        tool.function_name = "test_function"
        tool.is_enabled = True
        tool.requires_auth = False
        tool.required_permissions = []
        tool.is_builtin = False
        tool.creator_id = "user-123"
        tool.tags = ["test", "search", "utility"]
        tool.to_dict.return_value = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "Test Tool",
            "description": "A test tool for testing",
            "version": "0.1.0-beta",
            "category": "search",
            "function_name": "test_function",
            "is_enabled": True,
            "requires_auth": False,
            "required_permissions": [],
            "tags": ["test", "search", "utility"]
        }
        return tool

    @pytest.fixture
    def mock_tool2(self):
        """Create a second mock Tool instance."""
        tool = MagicMock(spec=Tool)
        tool.id = "550e8400-e29b-41d4-a716-446655440001"
        tool.name = "Another Tool"
        tool.description = "Another test tool"
        tool.version = "1.0.0"
        tool.category = ToolCategory.UTILITY
        tool.function_name = "another_function"
        tool.is_enabled = True
        tool.requires_auth = False
        tool.required_permissions = []
        tool.is_builtin = False
        tool.creator_id = "user-456"
        tool.tags = ["utility", "helper"]
        tool.to_dict.return_value = {
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "name": "Another Tool",
            "description": "Another test tool",
            "version": "1.0.0",
            "category": "utility",
            "function_name": "another_function",
            "is_enabled": True,
            "requires_auth": False,
            "required_permissions": [],
            "tags": ["utility", "helper"]
        }
        return tool

    # =============================================================================
    # FAST TESTS - Basic search functionality
    # =============================================================================

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_search_tools_success(self, tool_service, mock_tool):
        """Fast test for successful tool search."""
        tool_service.db.query.return_value.filter.return_value.all.return_value = [mock_tool]
        
        result = tool_service.search_tools("test")
        
        assert len(result) == 1
        assert result[0]["name"] == "Test Tool"

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_search_tools_empty_query(self, tool_service):
        """Fast test for empty search query."""
        result = tool_service.search_tools("")
        
        assert result == []

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_get_tools_by_category_success(self, tool_service, mock_tool):
        """Fast test for getting tools by category."""
        tool_service.db.query.return_value.filter.return_value.all.return_value = [mock_tool]
        
        result = tool_service.get_tools_by_category("search")
        
        assert len(result) == 1
        assert result[0]["category"] == "search"

    # =============================================================================
    # COMPREHENSIVE TESTS - Advanced search and filtering scenarios
    # =============================================================================

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_search_tools_multiple_results(self, tool_service, mock_tool, mock_tool2):
        """Comprehensive test for search with multiple results."""
        tool_service.db.query.return_value.filter.return_value.all.return_value = [mock_tool, mock_tool2]
        
        result = tool_service.search_tools("tool")
        
        assert len(result) == 2
        assert any(t["name"] == "Test Tool" for t in result)
        assert any(t["name"] == "Another Tool" for t in result)

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_search_tools_case_insensitive(self, tool_service, mock_tool):
        """Comprehensive test for case-insensitive search."""
        tool_service.db.query.return_value.filter.return_value.all.return_value = [mock_tool]
        
        result = tool_service.search_tools("TEST")
        
        assert len(result) == 1
        assert result[0]["name"] == "Test Tool"

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_search_tools_by_description(self, tool_service, mock_tool):
        """Comprehensive test for searching by description."""
        tool_service.db.query.return_value.filter.return_value.all.return_value = [mock_tool]
        
        result = tool_service.search_tools("testing")
        
        assert len(result) == 1
        assert "testing" in result[0]["description"].lower()

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_search_tools_by_tags(self, tool_service, mock_tool):
        """Comprehensive test for searching by tags."""
        tool_service.db.query.return_value.filter.return_value.all.return_value = [mock_tool]
        
        result = tool_service.search_tools("utility")
        
        assert len(result) == 1
        assert "utility" in result[0]["tags"]

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_search_tools_no_results(self, tool_service):
        """Comprehensive test for search with no results."""
        tool_service.db.query.return_value.filter.return_value.all.return_value = []
        
        result = tool_service.search_tools("nonexistent")
        
        assert result == []

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_search_tools_with_category_filter(self, tool_service, mock_tool):
        """Comprehensive test for search with category filter."""
        tool_service.db.query.return_value.filter.return_value.all.return_value = [mock_tool]
        
        result = tool_service.search_tools("test", category="search")
        
        assert len(result) == 1
        assert result[0]["category"] == "search"

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_search_tools_with_user_filter(self, tool_service, mock_tool):
        """Comprehensive test for search with user filter."""
        tool_service.db.query.return_value.filter.return_value.all.return_value = [mock_tool]
        
        result = tool_service.search_tools("test", user_id="user-123")
        
        assert len(result) == 1
        assert result[0]["id"] == "550e8400-e29b-41d4-a716-446655440000"

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_get_tools_by_category_invalid_category(self, tool_service):
        """Comprehensive test for invalid category handling."""
        result = tool_service.get_tools_by_category("invalid_category")
        
        assert result == []

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_get_tools_by_category_multiple_categories(self, tool_service, mock_tool, mock_tool2):
        """Comprehensive test for getting tools from multiple categories."""
        tool_service.db.query.return_value.filter.return_value.all.return_value = [mock_tool, mock_tool2]
        
        result = tool_service.get_tools_by_category("search")
        
        assert len(result) == 2
        assert all(t["category"] == "search" for t in result)

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_search_tools_with_limit(self, tool_service, mock_tool, mock_tool2):
        """Comprehensive test for search with result limit."""
        tool_service.db.query.return_value.filter.return_value.limit.return_value.all.return_value = [mock_tool]
        
        result = tool_service.search_tools("tool", limit=1)
        
        assert len(result) == 1
        tool_service.db.query.return_value.filter.return_value.limit.assert_called_once_with(1)

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_search_tools_with_offset(self, tool_service, mock_tool2):
        """Comprehensive test for search with offset."""
        tool_service.db.query.return_value.filter.return_value.offset.return_value.all.return_value = [mock_tool2]
        
        result = tool_service.search_tools("tool", offset=1)
        
        assert len(result) == 1
        tool_service.db.query.return_value.filter.return_value.offset.assert_called_once_with(1)

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_search_tools_with_sorting(self, tool_service, mock_tool, mock_tool2):
        """Comprehensive test for search with sorting."""
        tool_service.db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_tool, mock_tool2]
        
        result = tool_service.search_tools("tool", sort_by="name")
        
        assert len(result) == 2
        tool_service.db.query.return_value.filter.return_value.order_by.assert_called_once()

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_search_tools_database_error(self, tool_service):
        """Comprehensive test for database error during search."""
        tool_service.db.query.return_value.filter.return_value.all.side_effect = Exception("DB Error")
        
        with pytest.raises(Exception):
            tool_service.search_tools("test")

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_search_tools_with_special_characters(self, tool_service, mock_tool):
        """Comprehensive test for search with special characters."""
        tool_service.db.query.return_value.filter.return_value.all.return_value = [mock_tool]
        
        result = tool_service.search_tools("test-tool")
        
        assert len(result) == 1
        assert result[0]["name"] == "Test Tool"

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_search_tools_with_very_long_query(self, tool_service):
        """Comprehensive test for search with very long query."""
        long_query = "a" * 1000
        tool_service.db.query.return_value.filter.return_value.all.return_value = []
        
        result = tool_service.search_tools(long_query)
        
        assert result == []

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.tools
    def test_get_tools_by_category_with_user_filter(self, tool_service, mock_tool):
        """Comprehensive test for category filter with user filter."""
        tool_service.db.query.return_value.filter.return_value.all.return_value = [mock_tool]
        
        result = tool_service.get_tools_by_category("search", user_id="user-123")
        
        assert len(result) == 1
        assert result[0]["category"] == "search"