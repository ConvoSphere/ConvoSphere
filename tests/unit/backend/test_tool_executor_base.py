"""
Unit tests for the base tool executor functionality.
"""

import pytest
from datetime import UTC, datetime, timedelta
from unittest.mock import Mock, patch

from backend.app.services.tool_executor_base import (
    BaseToolExecutor,
    ToolDefinition,
    ToolExecution,
    ToolExecutionStatus,
    ToolParameter,
    ToolType,
)


class TestBaseToolExecutor:
    """Test cases for BaseToolExecutor."""

    def setup_method(self):
        """Set up test fixtures."""
        self.executor = BaseToolExecutor()
        self.sample_tool = ToolDefinition(
            id="test_tool",
            name="Test Tool",
            description="A test tool",
            type=ToolType.FUNCTION,
            parameters=[
                ToolParameter(
                    name="param1",
                    type="string",
                    description="Test parameter",
                    required=True,
                ),
                ToolParameter(
                    name="param2",
                    type="integer",
                    description="Optional parameter",
                    required=False,
                    default=42,
                    min_value=0,
                    max_value=100,
                ),
            ],
        )
        self.executor.tools["test_tool"] = self.sample_tool

    def test_init(self):
        """Test executor initialization."""
        assert self.executor.executions == {}
        assert self.executor.tools == {}
        assert self.executor.max_concurrent_executions == 10
        assert self.executor.default_timeout == 30

    def test_get_tool_definition(self):
        """Test getting tool definition."""
        # Test with existing tool
        tool = self.executor.get_tool_definition("test_tool")
        assert tool is not None
        assert tool.id == "test_tool"
        assert tool.name == "Test Tool"

        # Test with non-existing tool
        tool = self.executor.get_tool_definition("non_existing")
        assert tool is None

    def test_get_available_tools(self):
        """Test getting available tools."""
        tools = self.executor.get_available_tools()
        assert len(tools) == 1
        assert tools[0].id == "test_tool"

    def test_get_execution(self):
        """Test getting execution by ID."""
        # Test with non-existing execution
        execution = self.executor.get_execution("non_existing")
        assert execution is None

        # Test with existing execution
        test_execution = ToolExecution(
            id="test_exec",
            tool_id="test_tool",
            user_id="user1",
            conversation_id="conv1",
            parameters={},
            status=ToolExecutionStatus.COMPLETED,
            start_time=datetime.now(UTC),
        )
        self.executor.executions["test_exec"] = test_execution

        execution = self.executor.get_execution("test_exec")
        assert execution is not None
        assert execution.id == "test_exec"

    def test_get_user_executions(self):
        """Test getting user executions."""
        # Create test executions
        exec1 = ToolExecution(
            id="exec1",
            tool_id="test_tool",
            user_id="user1",
            conversation_id="conv1",
            parameters={},
            status=ToolExecutionStatus.COMPLETED,
            start_time=datetime.now(UTC) - timedelta(hours=1),
        )
        exec2 = ToolExecution(
            id="exec2",
            tool_id="test_tool",
            user_id="user1",
            conversation_id="conv1",
            parameters={},
            status=ToolExecutionStatus.COMPLETED,
            start_time=datetime.now(UTC),
        )
        exec3 = ToolExecution(
            id="exec3",
            tool_id="test_tool",
            user_id="user2",
            conversation_id="conv1",
            parameters={},
            status=ToolExecutionStatus.COMPLETED,
            start_time=datetime.now(UTC),
        )

        self.executor.executions.update({
            "exec1": exec1,
            "exec2": exec2,
            "exec3": exec3,
        })

        # Test getting user1 executions
        user_executions = self.executor.get_user_executions("user1")
        assert len(user_executions) == 2
        assert user_executions[0].id == "exec2"  # Newest first
        assert user_executions[1].id == "exec1"

        # Test with limit
        user_executions = self.executor.get_user_executions("user1", limit=1)
        assert len(user_executions) == 1
        assert user_executions[0].id == "exec2"

    def test_cancel_execution(self):
        """Test canceling execution."""
        # Create a running execution
        running_execution = ToolExecution(
            id="running_exec",
            tool_id="test_tool",
            user_id="user1",
            conversation_id="conv1",
            parameters={},
            status=ToolExecutionStatus.RUNNING,
            start_time=datetime.now(UTC),
        )
        self.executor.executions["running_exec"] = running_execution

        # Test canceling running execution
        result = self.executor.cancel_execution("running_exec")
        assert result is True
        assert running_execution.status == ToolExecutionStatus.CANCELLED
        assert running_execution.end_time is not None

        # Test canceling non-running execution
        completed_execution = ToolExecution(
            id="completed_exec",
            tool_id="test_tool",
            user_id="user1",
            conversation_id="conv1",
            parameters={},
            status=ToolExecutionStatus.COMPLETED,
            start_time=datetime.now(UTC),
        )
        self.executor.executions["completed_exec"] = completed_execution

        result = self.executor.cancel_execution("completed_exec")
        assert result is False

        # Test canceling non-existing execution
        result = self.executor.cancel_execution("non_existing")
        assert result is False

    def test_get_execution_stats(self):
        """Test getting execution statistics."""
        # Create test executions
        exec1 = ToolExecution(
            id="exec1",
            tool_id="test_tool",
            user_id="user1",
            conversation_id="conv1",
            parameters={},
            status=ToolExecutionStatus.COMPLETED,
            start_time=datetime.now(UTC),
        )
        exec2 = ToolExecution(
            id="exec2",
            tool_id="test_tool",
            user_id="user1",
            conversation_id="conv1",
            parameters={},
            status=ToolExecutionStatus.FAILED,
            start_time=datetime.now(UTC),
        )
        exec3 = ToolExecution(
            id="exec3",
            tool_id="test_tool",
            user_id="user1",
            conversation_id="conv1",
            parameters={},
            status=ToolExecutionStatus.RUNNING,
            start_time=datetime.now(UTC),
        )

        self.executor.executions.update({
            "exec1": exec1,
            "exec2": exec2,
            "exec3": exec3,
        })

        stats = self.executor.get_execution_stats()
        assert stats["total_executions"] == 3
        assert stats["completed"] == 1
        assert stats["failed"] == 1
        assert stats["running"] == 1
        assert stats["success_rate"] == pytest.approx(33.33, rel=0.1)

    def test_validate_parameters(self):
        """Test parameter validation."""
        # Test valid parameters
        valid_params = {"param1": "test_value", "param2": 50}
        validated = self.executor._validate_parameters(self.sample_tool, valid_params)
        assert validated["param1"] == "test_value"
        assert validated["param2"] == 50

        # Test missing required parameter
        with pytest.raises(ValueError, match="Required parameter 'param1' is missing"):
            self.executor._validate_parameters(self.sample_tool, {"param2": 50})

        # Test parameter with default value
        params_with_default = {"param1": "test_value"}
        validated = self.executor._validate_parameters(self.sample_tool, params_with_default)
        assert validated["param1"] == "test_value"
        assert validated["param2"] == 42  # Default value

        # Test parameter out of range
        with pytest.raises(ValueError, match="Parameter 'param2' must be <= 100"):
            self.executor._validate_parameters(self.sample_tool, {"param1": "test", "param2": 150})

        with pytest.raises(ValueError, match="Parameter 'param2' must be >= 0"):
            self.executor._validate_parameters(self.sample_tool, {"param1": "test", "param2": -1})

    def test_validate_parameters_with_enum(self):
        """Test parameter validation with enum values."""
        enum_tool = ToolDefinition(
            id="enum_tool",
            name="Enum Tool",
            description="Tool with enum parameter",
            type=ToolType.FUNCTION,
            parameters=[
                ToolParameter(
                    name="choice",
                    type="string",
                    description="Choice parameter",
                    required=True,
                    enum=["option1", "option2", "option3"],
                ),
            ],
        )

        # Test valid enum value
        valid_params = {"choice": "option1"}
        validated = self.executor._validate_parameters(enum_tool, valid_params)
        assert validated["choice"] == "option1"

        # Test invalid enum value
        with pytest.raises(ValueError, match="Parameter 'choice' must be one of"):
            self.executor._validate_parameters(enum_tool, {"choice": "invalid_option"})

    def test_create_execution(self):
        """Test creating execution instance."""
        execution = self.executor._create_execution(
            tool_id="test_tool",
            user_id="user1",
            conversation_id="conv1",
            parameters={"param1": "value1"},
        )

        assert execution.tool_id == "test_tool"
        assert execution.user_id == "user1"
        assert execution.conversation_id == "conv1"
        assert execution.parameters == {"param1": "value1"}
        assert execution.status == ToolExecutionStatus.PENDING
        assert execution.start_time is not None
        assert execution.id in self.executor.executions

    def test_update_execution(self):
        """Test updating execution."""
        execution = ToolExecution(
            id="test_exec",
            tool_id="test_tool",
            user_id="user1",
            conversation_id="conv1",
            parameters={},
            status=ToolExecutionStatus.PENDING,
            start_time=datetime.now(UTC),
        )

        # Test updating with success
        self.executor._update_execution(
            execution,
            ToolExecutionStatus.COMPLETED,
            result="success_result",
        )

        assert execution.status == ToolExecutionStatus.COMPLETED
        assert execution.result == "success_result"
        assert execution.end_time is not None
        assert execution.execution_time is not None

        # Test updating with error
        execution2 = ToolExecution(
            id="test_exec2",
            tool_id="test_tool",
            user_id="user1",
            conversation_id="conv1",
            parameters={},
            status=ToolExecutionStatus.PENDING,
            start_time=datetime.now(UTC),
        )

        self.executor._update_execution(
            execution2,
            ToolExecutionStatus.FAILED,
            error="test error",
        )

        assert execution2.status == ToolExecutionStatus.FAILED
        assert execution2.error == "test error"
        assert execution2.end_time is not None

    def test_cleanup_old_executions(self):
        """Test cleaning up old executions."""
        # Create old and new executions
        old_execution = ToolExecution(
            id="old_exec",
            tool_id="test_tool",
            user_id="user1",
            conversation_id="conv1",
            parameters={},
            status=ToolExecutionStatus.COMPLETED,
            start_time=datetime.now(UTC) - timedelta(hours=25),
        )
        new_execution = ToolExecution(
            id="new_exec",
            tool_id="test_tool",
            user_id="user1",
            conversation_id="conv1",
            parameters={},
            status=ToolExecutionStatus.COMPLETED,
            start_time=datetime.now(UTC),
        )

        self.executor.executions.update({
            "old_exec": old_execution,
            "new_exec": new_execution,
        })

        # Clean up executions older than 24 hours
        cleaned_count = self.executor.cleanup_old_executions(max_age_hours=24)
        assert cleaned_count == 1
        assert "old_exec" not in self.executor.executions
        assert "new_exec" in self.executor.executions

    def test_cleanup_old_executions_custom_age(self):
        """Test cleaning up executions with custom age."""
        # Create execution from 2 hours ago
        recent_execution = ToolExecution(
            id="recent_exec",
            tool_id="test_tool",
            user_id="user1",
            conversation_id="conv1",
            parameters={},
            status=ToolExecutionStatus.COMPLETED,
            start_time=datetime.now(UTC) - timedelta(hours=2),
        )

        self.executor.executions["recent_exec"] = recent_execution

        # Clean up executions older than 1 hour
        cleaned_count = self.executor.cleanup_old_executions(max_age_hours=1)
        assert cleaned_count == 1
        assert "recent_exec" not in self.executor.executions

        # Clean up executions older than 3 hours (should not clean recent_exec)
        self.executor.executions["recent_exec"] = recent_execution
        cleaned_count = self.executor.cleanup_old_executions(max_age_hours=3)
        assert cleaned_count == 0
        assert "recent_exec" in self.executor.executions


class TestToolDefinition:
    """Test cases for ToolDefinition."""

    def test_tool_definition_creation(self):
        """Test creating tool definition."""
        tool = ToolDefinition(
            id="test_tool",
            name="Test Tool",
            description="A test tool",
            type=ToolType.FUNCTION,
            parameters=[
                ToolParameter(
                    name="param1",
                    type="string",
                    description="Test parameter",
                    required=True,
                ),
            ],
            returns="string",
            timeout=60,
            enabled=True,
            metadata={"version": "1.0"},
        )

        assert tool.id == "test_tool"
        assert tool.name == "Test Tool"
        assert tool.description == "A test tool"
        assert tool.type == ToolType.FUNCTION
        assert len(tool.parameters) == 1
        assert tool.returns == "string"
        assert tool.timeout == 60
        assert tool.enabled is True
        assert tool.metadata["version"] == "1.0"

    def test_tool_definition_defaults(self):
        """Test tool definition default values."""
        tool = ToolDefinition(
            id="test_tool",
            name="Test Tool",
            description="A test tool",
            type=ToolType.FUNCTION,
        )

        assert tool.parameters == []
        assert tool.returns is None
        assert tool.timeout == 30
        assert tool.enabled is True
        assert tool.metadata == {}


class TestToolParameter:
    """Test cases for ToolParameter."""

    def test_tool_parameter_creation(self):
        """Test creating tool parameter."""
        param = ToolParameter(
            name="test_param",
            type="string",
            description="A test parameter",
            required=True,
            default="default_value",
            enum=["option1", "option2"],
            min_value=0,
            max_value=100,
        )

        assert param.name == "test_param"
        assert param.type == "string"
        assert param.description == "A test parameter"
        assert param.required is True
        assert param.default == "default_value"
        assert param.enum == ["option1", "option2"]
        assert param.min_value == 0
        assert param.max_value == 100

    def test_tool_parameter_defaults(self):
        """Test tool parameter default values."""
        param = ToolParameter(
            name="test_param",
            type="string",
            description="A test parameter",
        )

        assert param.required is False
        assert param.default is None
        assert param.enum is None
        assert param.min_value is None
        assert param.max_value is None