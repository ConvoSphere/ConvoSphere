"""
Base Tool Executor for common functionality.

This module provides the base classes and interfaces for tool execution
to eliminate code duplication between different tool executor implementations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any

from loguru import logger


class ToolExecutionStatus(Enum):
    """Tool execution status enumeration."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class ToolType(Enum):
    """Tool type enumeration."""

    MCP = "mcp"
    FUNCTION = "function"
    API = "api"
    CUSTOM = "custom"


@dataclass
class ToolParameter:
    """Tool parameter definition."""

    name: str
    type: str
    description: str
    required: bool = False
    default: Any = None
    enum: list[str] | None = None
    min_value: float | None = None
    max_value: float | None = None


@dataclass
class ToolDefinition:
    """Tool definition."""

    id: str
    name: str
    description: str
    type: ToolType
    parameters: list[ToolParameter] = field(default_factory=list)
    returns: str | None = None
    timeout: int = 30
    enabled: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolExecution:
    """Tool execution instance."""

    id: str
    tool_id: str
    user_id: str
    conversation_id: str | None
    parameters: dict[str, Any]
    status: ToolExecutionStatus
    start_time: datetime
    result: Any = None
    error: str | None = None
    end_time: datetime | None = None
    execution_time: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseToolExecutor(ABC):
    """Base class for tool executors with common functionality."""

    def __init__(self):
        """Initialize the base tool executor."""
        self.executions: dict[str, ToolExecution] = {}
        self.tools: dict[str, ToolDefinition] = {}
        self.max_concurrent_executions = 10
        self.default_timeout = 30

    @abstractmethod
    async def execute_tool(
        self,
        tool_id: str,
        parameters: dict[str, Any],
        user_id: str,
        conversation_id: str | None = None,
        timeout: int | None = None,
    ) -> ToolExecution:
        """Execute a tool."""

    @abstractmethod
    def get_tool_definition(self, tool_id: str) -> ToolDefinition | None:
        """Get tool definition by ID."""

    @abstractmethod
    def get_available_tools(self) -> list[ToolDefinition]:
        """Get list of available tools."""

    def get_execution(self, execution_id: str) -> ToolExecution | None:
        """Get execution by ID."""
        return self.executions.get(execution_id)

    def get_user_executions(
        self,
        user_id: str,
        limit: int = 100,
    ) -> list[ToolExecution]:
        """Get executions for a user."""
        user_executions = [
            exec for exec in self.executions.values()
            if exec.user_id == user_id
        ]
        return sorted(
            user_executions,
            key=lambda x: x.start_time,
            reverse=True
        )[:limit]

    def cancel_execution(self, execution_id: str) -> bool:
        """Cancel an execution."""
        execution = self.executions.get(execution_id)
        if execution and execution.status == ToolExecutionStatus.RUNNING:
            execution.status = ToolExecutionStatus.CANCELLED
            execution.end_time = datetime.now(UTC)
            logger.info(f"Cancelled execution: {execution_id}")
            return True
        return False

    def get_execution_stats(self) -> dict[str, Any]:
        """Get execution statistics."""
        total_executions = len(self.executions)
        completed = sum(
            1 for exec in self.executions.values()
            if exec.status == ToolExecutionStatus.COMPLETED
        )
        failed = sum(
            1 for exec in self.executions.values()
            if exec.status == ToolExecutionStatus.FAILED
        )
        running = sum(
            1 for exec in self.executions.values()
            if exec.status == ToolExecutionStatus.RUNNING
        )

        return {
            "total_executions": total_executions,
            "completed": completed,
            "failed": failed,
            "running": running,
            "success_rate": (completed / total_executions * 100) if total_executions > 0 else 0,
        }

    def _validate_parameters(
        self,
        tool_def: ToolDefinition,
        parameters: dict[str, Any],
    ) -> dict[str, Any]:
        """Validate tool parameters."""
        validated_params = {}

        for param in tool_def.parameters:
            param_name = param.name

            # Check required parameters
            if param.required and param_name not in parameters:
                raise ValueError(f"Required parameter '{param_name}' is missing")

            # Get parameter value
            value = parameters.get(param_name, param.default)

            # Validate enum values
            if param.enum and value not in param.enum:
                raise ValueError(
                    f"Parameter '{param_name}' must be one of: {param.enum}"
                )

            # Validate numeric ranges
            if param.min_value is not None and value < param.min_value:
                raise ValueError(
                    f"Parameter '{param_name}' must be >= {param.min_value}"
                )

            if param.max_value is not None and value > param.max_value:
                raise ValueError(
                    f"Parameter '{param_name}' must be <= {param.max_value}"
                )

            validated_params[param_name] = value

        return validated_params

    def _create_execution(
        self,
        tool_id: str,
        user_id: str,
        conversation_id: str | None,
        parameters: dict[str, Any],
    ) -> ToolExecution:
        """Create a new execution instance."""
        execution_id = f"{tool_id}_{user_id}_{datetime.now(UTC).timestamp()}"

        execution = ToolExecution(
            id=execution_id,
            tool_id=tool_id,
            user_id=user_id,
            conversation_id=conversation_id,
            parameters=parameters,
            status=ToolExecutionStatus.PENDING,
            start_time=datetime.now(UTC),
        )

        self.executions[execution_id] = execution
        return execution

    def _update_execution(
        self,
        execution: ToolExecution,
        status: ToolExecutionStatus,
        result: Any = None,
        error: str | None = None,
    ) -> None:
        """Update execution status and result."""
        execution.status = status
        execution.end_time = datetime.now(UTC)

        if execution.start_time and execution.end_time:
            execution.execution_time = (
                execution.end_time - execution.start_time
            ).total_seconds()

        if result is not None:
            execution.result = result

        if error is not None:
            execution.error = error

    def cleanup_old_executions(self, max_age_hours: int = 24) -> int:
        """Clean up old executions."""
        cutoff_time = datetime.now(UTC) - timedelta(hours=max_age_hours)
        old_executions = [
            exec_id for exec_id, execution in self.executions.items()
            if execution.start_time < cutoff_time
        ]

        for exec_id in old_executions:
            del self.executions[exec_id]

        logger.info(f"Cleaned up {len(old_executions)} old executions")
        return len(old_executions)
