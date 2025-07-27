"""
Unit tests for ToolExecutor service.

This module contains comprehensive unit tests for the ToolExecutor service,
covering tool execution, parameter validation, and execution management.
"""

import asyncio
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.app.services.tool_executor import (
    ToolDefinition,
    ToolExecution,
    ToolExecutionStatus,
    ToolExecutor,
    ToolParameter,
    ToolType,
)


@pytest.fixture
def mock_tool_service():
    """Mock tool service."""
    mock_service = MagicMock()
    
    # Mock available tools
    mock_service.get_available_tools.return_value = [
        {
            "id": "test-tool-123",
            "name": "Test Tool",
            "description": "A test tool for testing",
            "type": "mcp",
            "parameters": [
                {
                    "name": "query",
                    "type": "string",
                    "description": "Search query",
                    "required": True,
                },
                {
                    "name": "limit",
                    "type": "integer",
                    "description": "Result limit",
                    "required": False,
                    "default": 10,
                },
            ],
            "returns": "string",
            "timeout": 30,
            "enabled": True,
            "metadata": {"test": True},
        }
    ]
    
    # Mock specific tool getters
    mock_service.get_mcp_tool.return_value = AsyncMock()
    mock_service.get_function_tool.return_value = MagicMock()
    mock_service.get_api_tool.return_value = AsyncMock()
    mock_service.get_custom_tool.return_value = AsyncMock()
    
    return mock_service


@pytest.fixture
def tool_executor(mock_tool_service):
    """Create ToolExecutor instance with mocked dependencies."""
    with patch("backend.app.services.tool_executor.tool_service", mock_tool_service):
        executor = ToolExecutor()
        return executor


@pytest.fixture
def sample_tool_definition():
    """Sample tool definition for testing."""
    return ToolDefinition(
        id="test-tool-123",
        name="Test Tool",
        description="A test tool for testing",
        type=ToolType.MCP,
        parameters=[
            ToolParameter(
                name="query",
                type="string",
                description="Search query",
                required=True,
            ),
            ToolParameter(
                name="limit",
                type="integer",
                description="Result limit",
                required=False,
                default=10,
            ),
        ],
        returns="string",
        timeout=30,
        enabled=True,
        metadata={"test": True},
    )


@pytest.fixture
def sample_execution():
    """Sample tool execution for testing."""
    return ToolExecution(
        id="exec-123",
        tool_id="test-tool-123",
        user_id="user-123",
        conversation_id="conv-123",
        parameters={"query": "test query", "limit": 5},
        status=ToolExecutionStatus.COMPLETED,
        start_time=datetime.now(UTC),
        result="test result",
        end_time=datetime.now(UTC),
        execution_time=1.5,
        metadata={"test": True},
    )


class TestToolExecutor:
    """Test cases for ToolExecutor."""

    @pytest.mark.unit
    @pytest.mark.service
    def test_init(self, mock_tool_service):
        """Test ToolExecutor initialization."""
        with patch("backend.app.services.tool_executor.tool_service", mock_tool_service):
            executor = ToolExecutor()
            
            assert executor.executions == {}
            assert len(executor.tools) == 1
            assert "test-tool-123" in executor.tools
            assert len(executor.execution_handlers) == 1
            assert executor.max_concurrent_executions == 10
            assert executor.default_timeout == 30

    @pytest.mark.unit
    @pytest.mark.service
    def test_load_tools_error(self):
        """Test tool loading with error."""
        mock_service = MagicMock()
        mock_service.get_available_tools.side_effect = Exception("Service error")
        
        with patch("backend.app.services.tool_executor.tool_service", mock_service):
            executor = ToolExecutor()
            
            assert executor.tools == {}
            assert executor.execution_handlers == {}

    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_execute_tool_success(self, tool_executor, sample_tool_definition):
        """Test successful tool execution."""
        # Mock execution handler
        async def mock_handler(tool_def, parameters, user_id):
            return "success result"
        
        tool_executor.execution_handlers["test-tool-123"] = mock_handler
        
        result = await tool_executor.execute_tool(
            "test-tool-123",
            {"query": "test query", "limit": 5},
            "user-123",
        )
        
        assert result.status == ToolExecutionStatus.COMPLETED
        assert result.result == "success result"
        assert result.tool_id == "test-tool-123"
        assert result.user_id == "user-123"
        assert result.parameters == {"query": "test query", "limit": 5}

    @pytest.mark.unit
    @pytest.mark.service
    def test_execute_tool_not_found(self, tool_executor):
        """Test tool execution with non-existent tool."""
        with pytest.raises(ValueError, match="Tool non-existent-tool not found"):
            asyncio.run(tool_executor.execute_tool(
                "non-existent-tool",
                {"query": "test"},
                "user-123",
            ))

    @pytest.mark.unit
    @pytest.mark.service
    def test_execute_tool_disabled(self, tool_executor):
        """Test tool execution with disabled tool."""
        tool_executor.tools["test-tool-123"].enabled = False
        
        with pytest.raises(ValueError, match="Tool test-tool-123 is disabled"):
            asyncio.run(tool_executor.execute_tool(
                "test-tool-123",
                {"query": "test"},
                "user-123",
            ))

    @pytest.mark.unit
    @pytest.mark.service
    def test_execute_tool_parameter_validation_error(self, tool_executor):
        """Test tool execution with parameter validation error."""
        with pytest.raises(ValueError, match="Parameter validation failed"):
            asyncio.run(tool_executor.execute_tool(
                "test-tool-123",
                {"limit": 5},  # Missing required 'query' parameter
                "user-123",
            ))

    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_execute_tool_timeout(self, tool_executor):
        """Test tool execution timeout."""
        # Mock execution handler that takes too long
        async def slow_handler(tool_def, parameters, user_id):
            await asyncio.sleep(2)  # Longer than timeout
            return "result"
        
        tool_executor.execution_handlers["test-tool-123"] = slow_handler
        tool_executor.tools["test-tool-123"].timeout = 1  # 1 second timeout
        
        result = await tool_executor.execute_tool(
            "test-tool-123",
            {"query": "test query"},
            "user-123",
        )
        
        assert result.status == ToolExecutionStatus.TIMEOUT
        assert "timed out" in result.error

    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_execute_tool_execution_error(self, tool_executor):
        """Test tool execution with execution error."""
        # Mock execution handler that raises an error
        async def error_handler(tool_def, parameters, user_id):
            raise ValueError("Execution error")
        
        tool_executor.execution_handlers["test-tool-123"] = error_handler
        
        result = await tool_executor.execute_tool(
            "test-tool-123",
            {"query": "test query"},
            "user-123",
        )
        
        assert result.status == ToolExecutionStatus.FAILED
        assert "Execution error" in result.error

    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_execute_mcp_tool(self, tool_executor):
        """Test MCP tool execution."""
        mock_mcp_tool = AsyncMock()
        mock_mcp_tool.execute.return_value = "mcp result"
        
        with patch("backend.app.services.tool_executor.tool_service") as mock_service:
            mock_service.get_mcp_tool.return_value = mock_mcp_tool
            
            result = await tool_executor._execute_mcp_tool(
                tool_executor.tools["test-tool-123"],
                {"query": "test"},
                "user-123",
            )
            
            assert result == "mcp result"
            mock_mcp_tool.execute.assert_called_once_with({"query": "test"})

    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_execute_function_tool(self, tool_executor):
        """Test function tool execution."""
        mock_function = MagicMock()
        mock_function.return_value = "function result"
        
        with patch("backend.app.services.tool_executor.tool_service") as mock_service:
            mock_service.get_function_tool.return_value = mock_function
            
            result = await tool_executor._execute_function_tool(
                tool_executor.tools["test-tool-123"],
                {"query": "test"},
                "user-123",
            )
            
            assert result == "function result"
            mock_function.assert_called_once_with(query="test")

    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_execute_api_tool(self, tool_executor):
        """Test API tool execution."""
        mock_api_tool = AsyncMock()
        mock_api_tool.call.return_value = "api result"
        
        with patch("backend.app.services.tool_executor.tool_service") as mock_service:
            mock_service.get_api_tool.return_value = mock_api_tool
            
            result = await tool_executor._execute_api_tool(
                tool_executor.tools["test-tool-123"],
                {"url": "/test"},
                "user-123",
            )
            
            assert result == "api result"
            mock_api_tool.call.assert_called_once_with({"url": "/test"})

    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_execute_custom_tool(self, tool_executor):
        """Test custom tool execution."""
        mock_custom_tool = AsyncMock()
        mock_custom_tool.execute.return_value = "custom result"
        
        with patch("backend.app.services.tool_executor.tool_service") as mock_service:
            mock_service.get_custom_tool.return_value = mock_custom_tool
            
            result = await tool_executor._execute_custom_tool(
                tool_executor.tools["test-tool-123"],
                {"input": "test data"},
                "user-123",
            )
            
            assert result == "custom result"
            mock_custom_tool.execute.assert_called_once_with({"input": "test data"}, "user-123")

    @pytest.mark.unit
    @pytest.mark.service
    def test_validate_parameters_success(self, tool_executor, sample_tool_definition):
        """Test successful parameter validation."""
        parameters = {"query": "test query", "limit": 5}
        
        result = tool_executor._validate_parameters(sample_tool_definition, parameters)
        
        assert result["valid"] is True
        assert result["errors"] == []

    @pytest.mark.unit
    @pytest.mark.service
    def test_validate_parameters_missing_required(self, tool_executor, sample_tool_definition):
        """Test parameter validation with missing required parameter."""
        parameters = {"limit": 5}  # Missing 'query'
        
        result = tool_executor._validate_parameters(sample_tool_definition, parameters)
        
        assert result["valid"] is False
        assert "Required parameter 'query' is missing" in result["errors"]

    @pytest.mark.unit
    @pytest.mark.service
    def test_validate_parameters_invalid_type(self, tool_executor, sample_tool_definition):
        """Test parameter validation with invalid type."""
        parameters = {"query": "test query", "limit": "invalid"}  # limit should be integer
        
        result = tool_executor._validate_parameters(sample_tool_definition, parameters)
        
        assert result["valid"] is False
        assert "Parameter 'limit' must be an integer" in result["errors"]

    @pytest.mark.unit
    @pytest.mark.service
    def test_validate_parameters_enum_validation(self, tool_executor):
        """Test parameter validation with enum values."""
        tool_def = ToolDefinition(
            id="enum-tool-123",
            name="Enum Tool",
            description="A tool with enum parameters",
            type=ToolType.MCP,
            parameters=[
                ToolParameter(
                    name="status",
                    type="string",
                    description="Status",
                    required=True,
                    enum=["active", "inactive", "pending"]
                )
            ]
        )
        
        # Valid enum value
        parameters = {"status": "active"}
        result = tool_executor._validate_parameters(tool_def, parameters)
        assert result["valid"] is True
        
        # Invalid enum value
        parameters = {"status": "invalid"}
        result = tool_executor._validate_parameters(tool_def, parameters)
        assert result["valid"] is False
        assert "Parameter 'status' must be one of" in result["errors"][0]

    @pytest.mark.unit
    @pytest.mark.service
    def test_validate_parameters_range_validation(self, tool_executor):
        """Test parameter validation with range constraints."""
        tool_def = ToolDefinition(
            id="range-tool-123",
            name="Range Tool",
            description="A tool with range parameters",
            type=ToolType.MCP,
            parameters=[
                ToolParameter(
                    name="count",
                    type="integer",
                    description="Count",
                    required=True,
                    min_value=1,
                    max_value=100
                )
            ]
        )
        
        # Valid range value
        parameters = {"count": 50}
        result = tool_executor._validate_parameters(tool_def, parameters)
        assert result["valid"] is True
        
        # Value too low
        parameters = {"count": 0}
        result = tool_executor._validate_parameters(tool_def, parameters)
        assert result["valid"] is False
        assert "Parameter 'count' must be >=" in result["errors"][0]
        
        # Value too high
        parameters = {"count": 150}
        result = tool_executor._validate_parameters(tool_def, parameters)
        assert result["valid"] is False
        assert "Parameter 'count' must be <=" in result["errors"][0]

    @pytest.mark.unit
    @pytest.mark.service
    def test_get_tool_definition(self, tool_executor):
        """Test getting tool definition."""
        tool_def = tool_executor.get_tool_definition("test-tool-123")
        
        assert tool_def is not None
        assert tool_def.id == "test-tool-123"
        assert tool_def.name == "Test Tool"
        
        # Non-existent tool
        tool_def = tool_executor.get_tool_definition("non-existent")
        assert tool_def is None

    @pytest.mark.unit
    @pytest.mark.service
    def test_get_available_tools(self, tool_executor):
        """Test getting available tools."""
        tools = tool_executor.get_available_tools()
        
        assert len(tools) == 1
        assert tools[0].id == "test-tool-123"

    @pytest.mark.unit
    @pytest.mark.service
    def test_get_tool_schema(self, tool_executor, sample_tool_definition):
        """Test getting tool schema."""
        tool_executor.tools["test-tool-123"] = sample_tool_definition
        
        schema = tool_executor.get_tool_schema("test-tool-123")
        
        assert schema["type"] == "function"
        assert schema["function"]["name"] == "Test Tool"
        assert schema["function"]["description"] == "A test tool for testing"
        assert "query" in schema["function"]["parameters"]["properties"]
        assert "limit" in schema["function"]["parameters"]["properties"]
        assert "query" in schema["function"]["parameters"]["required"]

    @pytest.mark.unit
    @pytest.mark.service
    def test_get_tool_schema_not_found(self, tool_executor):
        """Test getting tool schema for non-existent tool."""
        schema = tool_executor.get_tool_schema("non-existent")
        assert schema is None

    @pytest.mark.unit
    @pytest.mark.service
    def test_get_execution(self, tool_executor, sample_execution):
        """Test getting execution by ID."""
        tool_executor.executions["exec-123"] = sample_execution
        
        execution = tool_executor.get_execution("exec-123")
        assert execution is not None
        assert execution.id == "exec-123"
        
        # Non-existent execution
        execution = tool_executor.get_execution("non-existent")
        assert execution is None

    @pytest.mark.unit
    @pytest.mark.service
    def test_get_user_executions(self, tool_executor, sample_execution):
        """Test getting user executions."""
        # Add multiple executions for different users
        execution1 = ToolExecution(
            id="exec-1",
            tool_id="test-tool-123",
            user_id="user-123",
            conversation_id="conv-123",
            parameters={"query": "test"},
            status=ToolExecutionStatus.COMPLETED,
            start_time=datetime.now(UTC),
        )
        
        execution2 = ToolExecution(
            id="exec-2",
            tool_id="test-tool-123",
            user_id="user-456",
            conversation_id="conv-456",
            parameters={"query": "test"},
            status=ToolExecutionStatus.COMPLETED,
            start_time=datetime.now(UTC),
        )
        
        tool_executor.executions["exec-1"] = execution1
        tool_executor.executions["exec-2"] = execution2
        
        user_executions = tool_executor.get_user_executions("user-123")
        assert len(user_executions) == 1
        assert user_executions[0].user_id == "user-123"

    @pytest.mark.unit
    @pytest.mark.service
    def test_cancel_execution(self, tool_executor):
        """Test canceling execution."""
        execution = ToolExecution(
            id="exec-123",
            tool_id="test-tool-123",
            user_id="user-123",
            conversation_id="conv-123",
            parameters={"query": "test"},
            status=ToolExecutionStatus.RUNNING,
            start_time=datetime.now(UTC),
        )
        
        tool_executor.executions["exec-123"] = execution
        
        # Cancel running execution
        result = tool_executor.cancel_execution("exec-123")
        assert result is True
        assert execution.status == ToolExecutionStatus.CANCELLED
        
        # Try to cancel non-existent execution
        result = tool_executor.cancel_execution("non-existent")
        assert result is False
        
        # Try to cancel completed execution
        execution.status = ToolExecutionStatus.COMPLETED
        result = tool_executor.cancel_execution("exec-123")
        assert result is False

    @pytest.mark.unit
    @pytest.mark.service
    def test_get_execution_stats(self, tool_executor, sample_execution):
        """Test getting execution statistics."""
        # Add multiple executions with different statuses
        sample_execution.status = ToolExecutionStatus.COMPLETED
        sample_execution.execution_time = 1.5
        
        failed_execution = ToolExecution(
            id="exec-456",
            tool_id="test-tool-123",
            user_id="user-123",
            conversation_id="conv-123",
            parameters={"query": "test"},
            status=ToolExecutionStatus.FAILED,
            start_time=datetime.now(UTC),
            error="Test error"
        )
        
        tool_executor.executions["exec-123"] = sample_execution
        tool_executor.executions["exec-456"] = failed_execution
        
        stats = tool_executor.get_execution_stats()
        
        assert stats["total_executions"] == 2
        assert stats["completed"] == 1
        assert stats["failed"] == 1
        assert stats["timeout"] == 0
        assert stats["success_rate"] == 50.0
        assert stats["average_execution_time"] == 1.5
        assert stats["available_tools"] == 1