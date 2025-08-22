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
    mock.version = "0.1.2-beta"
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
        "version": "0.1.2-beta",
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
        "version": "0.1.2-beta",
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
    """Test suite for Tools API endpoints."""

    # =============================================================================
    # FAST TESTS - Basic functionality
    # =============================================================================

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.tools
    @pytest.mark.asyncio
    async def test_get_tools_success(self, mock_db, mock_tool):
        """Fast test for successful tools retrieval."""
        with patch("backend.app.api.v1.endpoints.tools.ToolService") as mock_service:
            mock_service_instance = MagicMock()
            mock_service_instance.get_tools.return_value = [mock_tool]
            mock_service.return_value = mock_service_instance

            result = await get_tools(db=mock_db, skip=0, limit=10)

            assert result is not None
            assert len(result) == 1
            assert result[0]["name"] == "Test Tool"

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.tools
    @pytest.mark.asyncio
    async def test_get_tool_success(self, mock_db, mock_tool):
        """Fast test for successful tool retrieval by ID."""
        with patch("backend.app.api.v1.endpoints.tools.ToolService") as mock_service:
            mock_service_instance = MagicMock()
            mock_service_instance.get_tool_by_id.return_value = mock_tool
            mock_service.return_value = mock_service_instance

            result = await get_tool(tool_id="550e8400-e29b-41d4-a716-446655440000", db=mock_db)

            assert result is not None
            assert result["name"] == "Test Tool"

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.tools
    @pytest.mark.asyncio
    async def test_get_tool_categories(self):
        """Fast test for tool categories retrieval."""
        result = await get_tool_categories()

        assert result is not None
        assert isinstance(result, list)
        assert len(result) > 0

    # =============================================================================
    # COMPREHENSIVE TESTS - Advanced functionality and edge cases
    # =============================================================================

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.tools
    @pytest.mark.asyncio
    async def test_get_tools_with_category_filter(self, mock_db, mock_tool):
        """Comprehensive test for tools retrieval with category filter."""
        with patch("backend.app.api.v1.endpoints.tools.ToolService") as mock_service:
            mock_service_instance = MagicMock()
            mock_service_instance.get_tools.return_value = [mock_tool]
            mock_service.return_value = mock_service_instance

            result = await get_tools(db=mock_db, skip=0, limit=10, category="search")

            assert result is not None
            assert len(result) == 1
            assert result[0]["category"] == "search"

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.tools
    @pytest.mark.asyncio
    async def test_get_tools_with_search(self, mock_db, mock_tool):
        """Comprehensive test for tools retrieval with search."""
        with patch("backend.app.api.v1.endpoints.tools.ToolService") as mock_service:
            mock_service_instance = MagicMock()
            mock_service_instance.get_tools.return_value = [mock_tool]
            mock_service.return_value = mock_service_instance

            result = await get_tools(db=mock_db, skip=0, limit=10, search="test")

            assert result is not None
            assert len(result) == 1

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.tools
    @pytest.mark.asyncio
    async def test_create_tool_success(self, mock_db, sample_tool_data):
        """Comprehensive test for successful tool creation."""
        with patch("backend.app.api.v1.endpoints.tools.ToolService") as mock_service:
            mock_service_instance = MagicMock()
            mock_tool = MagicMock()
            mock_tool.to_dict.return_value = {**sample_tool_data, "id": "new-tool-id"}
            mock_service_instance.create_tool.return_value = mock_tool
            mock_service.return_value = mock_service_instance

            tool_create = ToolCreate(**sample_tool_data)
            result = await create_tool(tool=tool_create, db=mock_db)

            assert result is not None
            assert result["name"] == "Test Tool"

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.tools
    @pytest.mark.asyncio
    async def test_update_tool_success(self, mock_db, mock_tool):
        """Comprehensive test for successful tool update."""
        with patch("backend.app.api.v1.endpoints.tools.ToolService") as mock_service:
            mock_service_instance = MagicMock()
            updated_tool = MagicMock()
            updated_tool.to_dict.return_value = {
                **mock_tool.to_dict.return_value,
                "name": "Updated Tool"
            }
            mock_service_instance.update_tool.return_value = updated_tool
            mock_service.return_value = mock_service_instance

            tool_update = ToolUpdate(name="Updated Tool")
            result = await update_tool(
                tool_id="550e8400-e29b-41d4-a716-446655440000",
                tool=tool_update,
                db=mock_db
            )

            assert result is not None
            assert result["name"] == "Updated Tool"

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.tools
    @pytest.mark.asyncio
    async def test_delete_tool_success(self, mock_db):
        """Comprehensive test for successful tool deletion."""
        with patch("backend.app.api.v1.endpoints.tools.ToolService") as mock_service:
            mock_service_instance = MagicMock()
            mock_service_instance.delete_tool.return_value = True
            mock_service.return_value = mock_service_instance

            result = await delete_tool(
                tool_id="550e8400-e29b-41d4-a716-446655440000",
                db=mock_db
            )

            assert result is True

    # =============================================================================
    # ERROR HANDLING TESTS - Exception scenarios
    # =============================================================================

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.tools
    @pytest.mark.asyncio
    async def test_get_tool_not_found(self, mock_db):
        """Comprehensive test for tool not found error."""
        with patch("backend.app.api.v1.endpoints.tools.ToolService") as mock_service:
            mock_service_instance = MagicMock()
            mock_service_instance.get_tool_by_id.return_value = None
            mock_service.return_value = mock_service_instance

            with pytest.raises(HTTPException) as exc_info:
                await get_tool(tool_id="nonexistent-id", db=mock_db)

            assert exc_info.value.status_code == 404

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.tools
    @pytest.mark.asyncio
    async def test_create_tool_validation_error(self, mock_db):
        """Comprehensive test for tool creation validation error."""
        with patch("backend.app.api.v1.endpoints.tools.ToolService") as mock_service:
            mock_service_instance = MagicMock()
            mock_service_instance.create_tool.side_effect = ValueError("Invalid data")
            mock_service.return_value = mock_service_instance

            invalid_data = {"name": ""}  # Invalid data
            tool_create = ToolCreate(**invalid_data)

            with pytest.raises(ValueError):
                await create_tool(tool=tool_create, db=mock_db)

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.tools
    @pytest.mark.asyncio
    async def test_create_tool_invalid_category(self, mock_db):
        """Comprehensive test for tool creation with invalid category."""
        with patch("backend.app.api.v1.endpoints.tools.ToolService") as mock_service:
            mock_service_instance = MagicMock()
            mock_service_instance.create_tool.side_effect = ValueError("Invalid category")
            mock_service.return_value = mock_service_instance

            invalid_data = {
                "name": "Test Tool",
                "description": "A test tool",
                "version": "0.1.0",
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
            tool_create = ToolCreate(**invalid_data)

            with pytest.raises(ValueError):
                await create_tool(tool=tool_create, db=mock_db)

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.tools
    @pytest.mark.asyncio
    async def test_update_tool_not_found(self, mock_db):
        """Comprehensive test for tool update not found error."""
        with patch("backend.app.api.v1.endpoints.tools.ToolService") as mock_service:
            mock_service_instance = MagicMock()
            mock_service_instance.update_tool.return_value = None
            mock_service.return_value = mock_service_instance

            tool_update = ToolUpdate(name="Updated Tool")

            with pytest.raises(HTTPException) as exc_info:
                await update_tool(
                    tool_id="nonexistent-id",
                    tool=tool_update,
                    db=mock_db
                )

            assert exc_info.value.status_code == 404

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.tools
    @pytest.mark.asyncio
    async def test_update_tool_permission_denied(self, mock_db):
        """Comprehensive test for tool update permission denied."""
        with patch("backend.app.api.v1.endpoints.tools.ToolService") as mock_service:
            mock_service_instance = MagicMock()
            mock_service_instance.update_tool.side_effect = PermissionError("Permission denied")
            mock_service.return_value = mock_service_instance

            tool_update = ToolUpdate(name="Updated Tool")

            with pytest.raises(PermissionError):
                await update_tool(
                    tool_id="550e8400-e29b-41d4-a716-446655440000",
                    tool=tool_update,
                    db=mock_db
                )

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.tools
    @pytest.mark.asyncio
    async def test_update_tool_invalid_data(self, mock_db):
        """Comprehensive test for tool update with invalid data."""
        with patch("backend.app.api.v1.endpoints.tools.ToolService") as mock_service:
            mock_service_instance = MagicMock()
            mock_service_instance.update_tool.side_effect = ValueError("Invalid data")
            mock_service.return_value = mock_service_instance

            invalid_update = ToolUpdate(name="")  # Invalid data

            with pytest.raises(ValueError):
                await update_tool(
                    tool_id="550e8400-e29b-41d4-a716-446655440000",
                    tool=invalid_update,
                    db=mock_db
                )

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.tools
    @pytest.mark.asyncio
    async def test_delete_tool_not_found(self, mock_db):
        """Comprehensive test for tool deletion not found error."""
        with patch("backend.app.api.v1.endpoints.tools.ToolService") as mock_service:
            mock_service_instance = MagicMock()
            mock_service_instance.delete_tool.return_value = False
            mock_service.return_value = mock_service_instance

            with pytest.raises(HTTPException) as exc_info:
                await delete_tool(tool_id="nonexistent-id", db=mock_db)

            assert exc_info.value.status_code == 404

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.tools
    @pytest.mark.asyncio
    async def test_delete_tool_permission_denied(self, mock_db):
        """Comprehensive test for tool deletion permission denied."""
        with patch("backend.app.api.v1.endpoints.tools.ToolService") as mock_service:
            mock_service_instance = MagicMock()
            mock_service_instance.delete_tool.side_effect = PermissionError("Permission denied")
            mock_service.return_value = mock_service_instance

            with pytest.raises(PermissionError):
                await delete_tool(
                    tool_id="550e8400-e29b-41d4-a716-446655440000",
                    db=mock_db
                )

    # =============================================================================
    # EDGE CASE TESTS - Special scenarios
    # =============================================================================

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.tools
    @pytest.mark.asyncio
    async def test_get_tools_empty_result(self, mock_db):
        """Comprehensive test for empty tools result."""
        with patch("backend.app.api.v1.endpoints.tools.ToolService") as mock_service:
            mock_service_instance = MagicMock()
            mock_service_instance.get_tools.return_value = []
            mock_service.return_value = mock_service_instance

            result = await get_tools(db=mock_db, skip=0, limit=10)

            assert result is not None
            assert len(result) == 0

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.tools
    @pytest.mark.asyncio
    async def test_get_tools_service_error(self, mock_db):
        """Comprehensive test for service error during tools retrieval."""
        with patch("backend.app.api.v1.endpoints.tools.ToolService") as mock_service:
            mock_service_instance = MagicMock()
            mock_service_instance.get_tools.side_effect = Exception("Service error")
            mock_service.return_value = mock_service_instance

            with pytest.raises(Exception):
                await get_tools(db=mock_db, skip=0, limit=10)

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.tools
    @pytest.mark.asyncio
    async def test_create_tool_database_error(self, mock_db, sample_tool_data):
        """Comprehensive test for database error during tool creation."""
        with patch("backend.app.api.v1.endpoints.tools.ToolService") as mock_service:
            mock_service_instance = MagicMock()
            mock_service_instance.create_tool.side_effect = Exception("Database error")
            mock_service.return_value = mock_service_instance

            tool_create = ToolCreate(**sample_tool_data)

            with pytest.raises(Exception):
                await create_tool(tool=tool_create, db=mock_db)

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.tools
    @pytest.mark.asyncio
    async def test_update_tool_database_error(self, mock_db):
        """Comprehensive test for database error during tool update."""
        with patch("backend.app.api.v1.endpoints.tools.ToolService") as mock_service:
            mock_service_instance = MagicMock()
            mock_service_instance.update_tool.side_effect = Exception("Database error")
            mock_service.return_value = mock_service_instance

            tool_update = ToolUpdate(name="Updated Tool")

            with pytest.raises(Exception):
                await update_tool(
                    tool_id="550e8400-e29b-41d4-a716-446655440000",
                    tool=tool_update,
                    db=mock_db
                )

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.tools
    @pytest.mark.asyncio
    async def test_delete_tool_database_error(self, mock_db):
        """Comprehensive test for database error during tool deletion."""
        with patch("backend.app.api.v1.endpoints.tools.ToolService") as mock_service:
            mock_service_instance = MagicMock()
            mock_service_instance.delete_tool.side_effect = Exception("Database error")
            mock_service.return_value = mock_service_instance

            with pytest.raises(Exception):
                await delete_tool(
                    tool_id="550e8400-e29b-41d4-a716-446655440000",
                    db=mock_db
                )