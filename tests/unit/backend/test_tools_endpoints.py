"""
Unit tests for Tools API endpoints.

This module contains comprehensive unit tests for the Tools API endpoints,
covering CRUD operations, authentication, authorization, input validation,
and error handling.
"""

import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.api.v1.endpoints.tools import (
    get_tools,
    get_tool,
    create_tool,
    update_tool,
    delete_tool,
    get_tool_categories,
    ToolCreate,
    ToolUpdate,
    ToolResponse,
)


@pytest.fixture
def mock_db():
    """Mock database session."""
    return MagicMock(spec=Session)


@pytest.fixture
def mock_tool():
    """Mock tool object."""
    mock = MagicMock()
    mock.id = "550e8400-e29b-41d4-a716-446655440000"
    mock.name = "Test Tool"
    mock.description = "A test tool for testing"
    mock.version = "1.0.0"
    mock.category = "search"
    mock.function_name = "test_function"
    mock.parameters_schema = {"type": "object", "properties": {}}
    mock.implementation_path = "tools.test_function"
    mock.is_builtin = False
    mock.is_enabled = True
    mock.requires_auth = False
    mock.required_permissions = []
    mock.rate_limit = "100/hour"
    mock.tags = ["test"]
    mock.tool_metadata = {}
    mock.creator_id = "user-123"
    mock.created_at = "2023-01-01T00:00:00Z"
    mock.updated_at = "2023-01-01T00:00:00Z"
    mock.can_use = True
    
    # Mock to_dict method to return the expected structure
    mock.to_dict.return_value = {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "Test Tool",
        "description": "A test tool for testing",
        "version": "1.0.0",
        "category": "search",
        "function_name": "test_function",
        "parameters_schema": {"type": "object", "properties": {}},
        "implementation_path": "tools.test_function",
        "is_builtin": False,
        "is_enabled": True,
        "requires_auth": False,
        "required_permissions": [],
        "rate_limit": "100/hour",
        "tags": ["test"],
        "metadata": {},
        "creator_id": "user-123",
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
        "can_use": True,
    }
    
    return mock


@pytest.fixture
def sample_tool_data():
    """Sample tool data for testing."""
    return {
        "name": "Test Tool",
        "description": "A test tool for testing",
        "version": "1.0.0",
        "category": "search",
        "function_name": "test_function",
        "parameters_schema": {"type": "object", "properties": {}},
        "implementation_path": "tools.test_function",
        "is_builtin": False,
        "is_enabled": True,
        "requires_auth": False,
        "required_permissions": [],
        "rate_limit": "100/hour",
        "tags": ["test"],
        "tool_metadata": {},
    }


class TestToolsEndpoints:
    """Test cases for Tools API endpoints."""

    @pytest.mark.unit
    @pytest.mark.endpoint
    @pytest.mark.asyncio
    async def test_get_tools_success(self, mock_db, mock_tool):
        """Test successful retrieval of tools."""
        mock_tool_service = MagicMock()
        mock_tool_service.get_available_tools.return_value = [mock_tool.to_dict()]

        with patch('backend.app.api.v1.endpoints.tools.ToolService', return_value=mock_tool_service):
            result = await get_tools(
                category=None,
                search=None,
                current_user_id="user-123",
                db=mock_db
            )

            assert len(result) == 1
            assert result[0].id == "550e8400-e29b-41d4-a716-446655440000"
            assert result[0].name == "Test Tool"
            mock_tool_service.get_available_tools.assert_called_once_with("user-123")

    @pytest.mark.unit
    @pytest.mark.endpoint
    @pytest.mark.asyncio
    async def test_get_tools_with_category_filter(self, mock_db, mock_tool):
        """Test retrieval of tools with category filter."""
        mock_tool_service = MagicMock()
        mock_tool_service.get_tools_by_category.return_value = [mock_tool.to_dict()]

        with patch('backend.app.api.v1.endpoints.tools.ToolService', return_value=mock_tool_service):
            result = await get_tools(
                category="search",
                search=None,
                current_user_id="user-123",
                db=mock_db
            )

            assert len(result) == 1
            assert result[0].category == "search"
            mock_tool_service.get_tools_by_category.assert_called_once_with("search", "user-123")

    @pytest.mark.unit
    @pytest.mark.endpoint
    @pytest.mark.asyncio
    async def test_get_tools_with_search(self, mock_db, mock_tool):
        """Test retrieval of tools with search query."""
        mock_tool_service = MagicMock()
        mock_tool_service.search_tools.return_value = [mock_tool.to_dict()]

        with patch('backend.app.api.v1.endpoints.tools.ToolService', return_value=mock_tool_service):
            result = await get_tools(
                category=None,
                search="test",
                current_user_id="user-123",
                db=mock_db
            )

            assert len(result) == 1
            assert result[0].name == "Test Tool"
            mock_tool_service.search_tools.assert_called_once_with("test", "user-123")

    @pytest.mark.unit
    @pytest.mark.endpoint
    @pytest.mark.asyncio
    async def test_get_tool_success(self, mock_db, mock_tool):
        """Test successful retrieval of a single tool."""
        mock_tool_service = MagicMock()
        mock_tool_service.get_tool_by_id.return_value = mock_tool.to_dict()

        with patch('backend.app.api.v1.endpoints.tools.ToolService', return_value=mock_tool_service):
            result = await get_tool(
                tool_id="550e8400-e29b-41d4-a716-446655440000",
                current_user_id="user-123",
                db=mock_db
            )

            assert result.id == "550e8400-e29b-41d4-a716-446655440000"
            assert result.name == "Test Tool"
            mock_tool_service.get_tool_by_id.assert_called_once_with("550e8400-e29b-41d4-a716-446655440000", "user-123")

    @pytest.mark.unit
    @pytest.mark.endpoint
    @pytest.mark.asyncio
    async def test_get_tool_not_found(self, mock_db):
        """Test retrieval of non-existent tool."""
        mock_tool_service = MagicMock()
        mock_tool_service.get_tool_by_id.return_value = None

        with patch('backend.app.api.v1.endpoints.tools.ToolService', return_value=mock_tool_service):
            with pytest.raises(HTTPException) as exc_info:
                await get_tool(
                    tool_id="non-existent",
                    current_user_id="user-123",
                    db=mock_db
                )

            assert exc_info.value.status_code == 404
            assert "Tool not found" in str(exc_info.value.detail)

    @pytest.mark.unit
    @pytest.mark.endpoint
    @pytest.mark.asyncio
    async def test_create_tool_success(self, mock_db, sample_tool_data):
        """Test successful tool creation."""
        mock_tool_service = MagicMock()
        created_tool = sample_tool_data.copy()
        created_tool["id"] = "550e8400-e29b-41d4-a716-446655440000"
        created_tool["creator_id"] = "user-123"
        created_tool["created_at"] = "2023-01-01T00:00:00Z"
        created_tool["updated_at"] = "2023-01-01T00:00:00Z"
        created_tool["can_use"] = True
        created_tool["metadata"] = {}
        mock_tool_service.create_tool.return_value = created_tool

        with patch('backend.app.api.v1.endpoints.tools.ToolService', return_value=mock_tool_service):
            tool_create = ToolCreate(**sample_tool_data)
            result = await create_tool(
                tool_data=tool_create,
                current_user_id="user-123",
                db=mock_db
            )

            assert result.id == "550e8400-e29b-41d4-a716-446655440000"
            assert result.name == "Test Tool"
            mock_tool_service.create_tool.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.endpoint
    @pytest.mark.asyncio
    async def test_create_tool_validation_error(self, mock_db):
        """Test tool creation with validation error."""
        mock_tool_service = MagicMock()
        mock_tool_service.create_tool.return_value = None

        with patch('backend.app.api.v1.endpoints.tools.ToolService', return_value=mock_tool_service):
            # Test with valid data but service returns None (validation error at service level)
            valid_data = {
                "name": "Test Tool",
                "description": "A test tool for testing",
                "version": "1.0.0",
                "category": "search",
                "function_name": "test_function",
                "parameters_schema": {"type": "object", "properties": {}},
                "implementation_path": "tools.test_function",
                "is_builtin": False,
                "is_enabled": True,
                "requires_auth": False,
                "required_permissions": [],
                "rate_limit": "100/hour",
                "tags": ["test"],
                "tool_metadata": {},
            }
            
            tool_create = ToolCreate(**valid_data)
            with pytest.raises(HTTPException) as exc_info:
                await create_tool(
                    tool_data=tool_create,
                    current_user_id="user-123",
                    db=mock_db
                )

            assert exc_info.value.status_code == 500
            assert "Failed to create tool" in str(exc_info.value.detail)

    @pytest.mark.unit
    @pytest.mark.endpoint
    @pytest.mark.asyncio
    async def test_create_tool_invalid_category(self, mock_db):
        """Test tool creation with invalid category."""
        mock_tool_service = MagicMock()
        mock_tool_service.create_tool.side_effect = ValueError("Invalid category")

        with patch('backend.app.api.v1.endpoints.tools.ToolService', return_value=mock_tool_service):
            sample_tool_data = {
                "name": "Test Tool",
                "description": "A test tool for testing",
                "version": "1.0.0",
                "category": "invalid_category",
                "function_name": "test_function",
                "parameters_schema": {"type": "object", "properties": {}},
                "implementation_path": "tools.test_function",
                "is_builtin": False,
                "is_enabled": True,
                "requires_auth": False,
                "required_permissions": [],
                "rate_limit": "100/hour",
                "tags": ["test"],
                "tool_metadata": {},
            }
            
            tool_create = ToolCreate(**sample_tool_data)
            with pytest.raises(HTTPException) as exc_info:
                await create_tool(
                    tool_data=tool_create,
                    current_user_id="user-123",
                    db=mock_db
                )

            assert exc_info.value.status_code == 400
            assert "Invalid category" in str(exc_info.value.detail)

    @pytest.mark.unit
    @pytest.mark.endpoint
    @pytest.mark.asyncio
    async def test_update_tool_success(self, mock_db, mock_tool):
        """Test successful tool update."""
        mock_tool_service = MagicMock()
        updated_tool = mock_tool.to_dict()
        updated_tool["name"] = "Updated Tool"
        mock_tool_service.update_tool.return_value = updated_tool

        with patch('backend.app.api.v1.endpoints.tools.ToolService', return_value=mock_tool_service):
            tool_update = ToolUpdate(name="Updated Tool")
            result = await update_tool(
                tool_id="550e8400-e29b-41d4-a716-446655440000",
                tool_data=tool_update,
                current_user_id="user-123",
                db=mock_db
            )

            assert result.name == "Updated Tool"
            mock_tool_service.update_tool.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.endpoint
    @pytest.mark.asyncio
    async def test_update_tool_not_found(self, mock_db):
        """Test tool update with non-existent tool."""
        mock_tool_service = MagicMock()
        mock_tool_service.update_tool.return_value = None

        with patch('backend.app.api.v1.endpoints.tools.ToolService', return_value=mock_tool_service):
            tool_update = ToolUpdate(name="Updated Tool")
            with pytest.raises(HTTPException) as exc_info:
                await update_tool(
                    tool_id="non-existent",
                    tool_data=tool_update,
                    current_user_id="user-123",
                    db=mock_db
                )

            assert exc_info.value.status_code == 404
            assert "Tool not found or insufficient permissions" in str(exc_info.value.detail)

    @pytest.mark.unit
    @pytest.mark.endpoint
    @pytest.mark.asyncio
    async def test_update_tool_permission_denied(self, mock_db):
        """Test tool update without permission."""
        mock_tool_service = MagicMock()
        mock_tool_service.update_tool.return_value = None

        with patch('backend.app.api.v1.endpoints.tools.ToolService', return_value=mock_tool_service):
            tool_update = ToolUpdate(name="Updated Tool")
            with pytest.raises(HTTPException) as exc_info:
                await update_tool(
                    tool_id="550e8400-e29b-41d4-a716-446655440000",
                    tool_data=tool_update,
                    current_user_id="user-123",
                    db=mock_db
                )

            assert exc_info.value.status_code == 404
            assert "Tool not found or insufficient permissions" in str(exc_info.value.detail)

    @pytest.mark.unit
    @pytest.mark.endpoint
    @pytest.mark.asyncio
    async def test_update_tool_invalid_data(self, mock_db):
        """Test tool update with invalid data."""
        mock_tool_service = MagicMock()
        mock_tool_service.update_tool.side_effect = ValueError("Invalid data")

        with patch('backend.app.api.v1.endpoints.tools.ToolService', return_value=mock_tool_service):
            tool_update = ToolUpdate(name="Valid Name")  # Valid name
            with pytest.raises(HTTPException) as exc_info:
                await update_tool(
                    tool_id="550e8400-e29b-41d4-a716-446655440000",
                    tool_data=tool_update,
                    current_user_id="user-123",
                    db=mock_db
                )

            assert exc_info.value.status_code == 400
            assert "Invalid data" in str(exc_info.value.detail)

    @pytest.mark.unit
    @pytest.mark.endpoint
    @pytest.mark.asyncio
    async def test_delete_tool_success(self, mock_db):
        """Test successful tool deletion."""
        mock_tool_service = MagicMock()
        mock_tool_service.delete_tool.return_value = True

        with patch('backend.app.api.v1.endpoints.tools.ToolService', return_value=mock_tool_service):
            result = await delete_tool(
                tool_id="550e8400-e29b-41d4-a716-446655440000",
                current_user_id="user-123",
                db=mock_db
            )

            assert result["message"] == "Tool deleted successfully"
            mock_tool_service.delete_tool.assert_called_once_with("550e8400-e29b-41d4-a716-446655440000", "user-123")

    @pytest.mark.unit
    @pytest.mark.endpoint
    @pytest.mark.asyncio
    async def test_delete_tool_not_found(self, mock_db):
        """Test tool deletion with non-existent tool."""
        mock_tool_service = MagicMock()
        mock_tool_service.delete_tool.return_value = False

        with patch('backend.app.api.v1.endpoints.tools.ToolService', return_value=mock_tool_service):
            with pytest.raises(HTTPException) as exc_info:
                await delete_tool(
                    tool_id="non-existent",
                    current_user_id="user-123",
                    db=mock_db
                )

            assert exc_info.value.status_code == 404
            assert "Tool not found or insufficient permissions" in str(exc_info.value.detail)

    @pytest.mark.unit
    @pytest.mark.endpoint
    @pytest.mark.asyncio
    async def test_delete_tool_permission_denied(self, mock_db):
        """Test tool deletion without permission."""
        mock_tool_service = MagicMock()
        mock_tool_service.delete_tool.return_value = False

        with patch('backend.app.api.v1.endpoints.tools.ToolService', return_value=mock_tool_service):
            with pytest.raises(HTTPException) as exc_info:
                await delete_tool(
                    tool_id="550e8400-e29b-41d4-a716-446655440000",
                    current_user_id="user-123",
                    db=mock_db
                )

            assert exc_info.value.status_code == 404
            assert "Tool not found or insufficient permissions" in str(exc_info.value.detail)

    @pytest.mark.unit
    @pytest.mark.endpoint
    @pytest.mark.asyncio
    async def test_get_tool_categories(self):
        """Test retrieval of tool categories."""
        result = await get_tool_categories()

        assert "categories" in result
        assert isinstance(result["categories"], list)
        # Verify all expected categories are present
        expected_categories = [
            "search", "file", "api", "database", "custom", "analysis", "communication", "automation"
        ]
        for category in expected_categories:
            assert category in result["categories"]

    @pytest.mark.unit
    @pytest.mark.endpoint
    @pytest.mark.asyncio
    async def test_get_tools_empty_result(self, mock_db):
        """Test retrieval of tools with empty result."""
        mock_tool_service = MagicMock()
        mock_tool_service.get_available_tools.return_value = []

        with patch('backend.app.api.v1.endpoints.tools.ToolService', return_value=mock_tool_service):
            result = await get_tools(
                category=None,
                search=None,
                current_user_id="user-123",
                db=mock_db
            )

            assert len(result) == 0
            mock_tool_service.get_available_tools.assert_called_once_with("user-123")

    @pytest.mark.unit
    @pytest.mark.endpoint
    @pytest.mark.asyncio
    async def test_get_tools_service_error(self, mock_db):
        """Test handling of service errors in get_tools."""
        mock_tool_service = MagicMock()
        mock_tool_service.get_available_tools.side_effect = Exception("Service error")

        with patch('backend.app.api.v1.endpoints.tools.ToolService', return_value=mock_tool_service):
            with pytest.raises(HTTPException) as exc_info:
                await get_tools(
                    category=None,
                    search=None,
                    current_user_id="user-123",
                    db=mock_db
                )

            assert exc_info.value.status_code == 500
            assert "Failed to retrieve tools" in str(exc_info.value.detail)

    @pytest.mark.unit
    @pytest.mark.endpoint
    @pytest.mark.asyncio
    async def test_create_tool_database_error(self, mock_db, sample_tool_data):
        """Test handling of database errors in create_tool."""
        mock_tool_service = MagicMock()
        mock_tool_service.create_tool.side_effect = Exception("Database error")

        with patch('backend.app.api.v1.endpoints.tools.ToolService', return_value=mock_tool_service):
            tool_create = ToolCreate(**sample_tool_data)
            with pytest.raises(HTTPException) as exc_info:
                await create_tool(
                    tool_data=tool_create,
                    current_user_id="user-123",
                    db=mock_db
                )

            assert exc_info.value.status_code == 500
            assert "Failed to create tool" in str(exc_info.value.detail)

    @pytest.mark.unit
    @pytest.mark.endpoint
    @pytest.mark.asyncio
    async def test_update_tool_database_error(self, mock_db):
        """Test handling of database errors in update_tool."""
        mock_tool_service = MagicMock()
        mock_tool_service.update_tool.side_effect = Exception("Database error")

        with patch('backend.app.api.v1.endpoints.tools.ToolService', return_value=mock_tool_service):
            tool_update = ToolUpdate(name="Updated Tool")
            with pytest.raises(HTTPException) as exc_info:
                await update_tool(
                    tool_id="550e8400-e29b-41d4-a716-446655440000",
                    tool_data=tool_update,
                    current_user_id="user-123",
                    db=mock_db
                )

            assert exc_info.value.status_code == 500
            assert "Failed to update tool" in str(exc_info.value.detail)

    @pytest.mark.unit
    @pytest.mark.endpoint
    @pytest.mark.asyncio
    async def test_delete_tool_database_error(self, mock_db):
        """Test handling of database errors in delete_tool."""
        mock_tool_service = MagicMock()
        mock_tool_service.delete_tool.side_effect = Exception("Database error")

        with patch('backend.app.api.v1.endpoints.tools.ToolService', return_value=mock_tool_service):
            with pytest.raises(HTTPException) as exc_info:
                await delete_tool(
                    tool_id="550e8400-e29b-41d4-a716-446655440000",
                    current_user_id="user-123",
                    db=mock_db
                )

            assert exc_info.value.status_code == 500
            assert "Failed to delete tool" in str(exc_info.value.detail)