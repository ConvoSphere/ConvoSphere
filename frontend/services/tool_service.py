"""
Tool service for the AI Assistant Platform.

This module provides tool management and execution functionality including
MCP (Model Context Protocol) integration and tool discovery.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from utils.helpers import generate_id
from utils.validators import validate_tool_data

from .api import api_client
from .error_handler import handle_api_error, handle_network_error


class ToolType(Enum):
    """Tool types enumeration."""

    FUNCTION = "function"
    MCP = "mcp"
    API = "api"
    CUSTOM = "custom"


class ToolStatus(Enum):
    """Tool status enumeration."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    LOADING = "loading"


@dataclass
class ToolParameter:
    """Tool parameter data model."""

    name: str
    type: str
    description: str
    required: bool = False
    default: Any | None = None
    enum: list[str] | None = None


@dataclass
class Tool:
    """Tool data model."""

    id: str
    name: str
    description: str
    tool_type: ToolType
    status: ToolStatus
    category: str
    parameters: list[ToolParameter]
    created_at: datetime
    updated_at: datetime
    version: str = "1.0.0"
    author: str | None = None
    tags: list[str] | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class ToolExecutionResult:
    """Tool execution result data model."""

    tool_id: str
    tool_name: str
    input_data: dict[str, Any]
    output_data: dict[str, Any]
    execution_time: float
    status: str  # success, error, timeout
    error_message: str | None = None
    metadata: dict[str, Any] | None = None


class ToolService:
    """Service for tool management and execution."""

    def __init__(self):
        """Initialize the tool service."""
        self.tools: list[Tool] = []
        self.mcp_servers: dict[str, dict[str, Any]] = {}
        self.execution_history: list[ToolExecutionResult] = []
        self.is_loading = False

    async def get_tools(self, force_refresh: bool = False) -> list[Tool]:
        """
        Get all available tools.

        Args:
            force_refresh: Force refresh from API

        Returns:
            List of tools
        """
        if not force_refresh and self.tools:
            return self.tools

        self.is_loading = True

        try:
            # Get regular tools
            tools_response = await api_client.get_tools()
            tools = []

            if tools_response.success and tools_response.data:
                for tool_data in tools_response.data:
                    tool = self._create_tool_from_data(tool_data)
                    tools.append(tool)

            # Get MCP tools
            mcp_tools_response = await api_client.get_mcp_tools()
            if mcp_tools_response.success and mcp_tools_response.data:
                for tool_data in mcp_tools_response.data:
                    tool = self._create_tool_from_data(tool_data, ToolType.MCP)
                    tools.append(tool)

            self.tools = tools
            return tools

        except Exception as e:
            handle_network_error(e, "Laden der Tools")
            return []
        finally:
            self.is_loading = False

    async def get_tool(self, tool_id: str) -> Tool | None:
        """
        Get specific tool by ID.

        Args:
            tool_id: Tool ID

        Returns:
            Tool or None if not found
        """
        try:
            response = await api_client.get_tool(tool_id)

            if response.success and response.data:
                return self._create_tool_from_data(response.data)
            handle_api_error(response, f"Laden des Tools {tool_id}")
            return None

        except Exception as e:
            handle_network_error(e, f"Laden des Tools {tool_id}")
            return None

    async def create_tool(self, tool_data: dict[str, Any]) -> Tool | None:
        """
        Create new tool.

        Args:
            tool_data: Tool data

        Returns:
            Created tool or None if failed
        """
        try:
            # Validate tool data
            validation = validate_tool_data(tool_data)
            if not validation["valid"]:
                raise ValueError(f"Tool validation failed: {validation['errors']}")

            response = await api_client.create_tool(tool_data)

            if response.success and response.data:
                tool = self._create_tool_from_data(response.data)
                self.tools.append(tool)
                return tool
            handle_api_error(response, "Erstellen des Tools")
            return None

        except Exception as e:
            handle_network_error(e, "Erstellen des Tools")
            return None

    async def update_tool(self, tool_id: str, tool_data: dict[str, Any]) -> Tool | None:
        """
        Update tool.

        Args:
            tool_id: Tool ID
            tool_data: Updated tool data

        Returns:
            Updated tool or None if failed
        """
        try:
            response = await api_client.update_tool(tool_id, tool_data)

            if response.success and response.data:
                tool = self._create_tool_from_data(response.data)

                # Update in local list
                for i, existing_tool in enumerate(self.tools):
                    if existing_tool.id == tool_id:
                        self.tools[i] = tool
                        break

                return tool
            handle_api_error(response, f"Aktualisieren des Tools {tool_id}")
            return None

        except Exception as e:
            handle_network_error(e, f"Aktualisieren des Tools {tool_id}")
            return None

    async def delete_tool(self, tool_id: str) -> bool:
        """
        Delete tool.

        Args:
            tool_id: Tool ID

        Returns:
            True if successful, False otherwise
        """
        try:
            response = await api_client.delete_tool(tool_id)

            if response.success:
                # Remove from local list
                self.tools = [t for t in self.tools if t.id != tool_id]
                return True
            handle_api_error(response, f"Löschen des Tools {tool_id}")
            return False

        except Exception as e:
            handle_network_error(e, f"Löschen des Tools {tool_id}")
            return False

    async def execute_tool(
        self,
        tool_id: str,
        input_data: dict[str, Any],
        conversation_id: str | None = None,
    ) -> ToolExecutionResult | None:
        """
        Execute a tool.

        Args:
            tool_id: Tool ID to execute
            input_data: Input data for the tool
            conversation_id: Optional conversation ID for context

        Returns:
            Tool execution result or None if failed
        """
        try:
            # Find tool
            tool = next((t for t in self.tools if t.id == tool_id), None)
            if not tool:
                tool = await self.get_tool(tool_id)
                if not tool:
                    raise ValueError(f"Tool {tool_id} not found")

            # Validate input parameters
            validation_result = self._validate_tool_input(tool, input_data)
            if not validation_result["valid"]:
                raise ValueError(
                    f"Tool input validation failed: {validation_result['errors']}",
                )

            # Execute tool
            start_time = datetime.now()

            if tool.tool_type == ToolType.MCP:
                result = await self._execute_mcp_tool(tool, input_data)
            else:
                result = await self._execute_regular_tool(tool, input_data)

            execution_time = (datetime.now() - start_time).total_seconds()

            # Create execution result
            execution_result = ToolExecutionResult(
                tool_id=tool_id,
                tool_name=tool.name,
                input_data=input_data,
                output_data=result.get("output", {}),
                execution_time=execution_time,
                status=result.get("status", "success"),
                error_message=result.get("error"),
                metadata={
                    "conversation_id": conversation_id,
                    "tool_type": tool.tool_type.value,
                    "tool_category": tool.category,
                },
            )

            # Add to history
            self.execution_history.append(execution_result)

            return execution_result

        except Exception as e:
            handle_network_error(e, f"Ausführung des Tools {tool_id}")
            return None

    async def _execute_regular_tool(
        self, tool: Tool, input_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute a regular tool via API."""
        try:
            response = await api_client.execute_tool(tool.id, input_data)

            if response.success and response.data:
                return {
                    "status": "success",
                    "output": response.data.get("result", {}),
                }
            return {
                "status": "error",
                "error": response.error
                if hasattr(response, "error")
                else "Unknown error",
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }

    async def _execute_mcp_tool(
        self, tool: Tool, input_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute an MCP tool."""
        try:
            # Get MCP server info from tool metadata
            server_id = tool.metadata.get("mcp_server_id") if tool.metadata else None
            if not server_id:
                return {
                    "status": "error",
                    "error": "MCP server ID not found in tool metadata",
                }

            # Execute via MCP endpoint
            response = await api_client.execute_mcp_tool(server_id, tool.id, input_data)

            if response.success and response.data:
                return {
                    "status": "success",
                    "output": response.data.get("result", {}),
                }
            return {
                "status": "error",
                "error": response.error
                if hasattr(response, "error")
                else "Unknown error",
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }

    def _validate_tool_input(
        self, tool: Tool, input_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Validate tool input parameters.

        Args:
            tool: Tool to validate input for
            input_data: Input data to validate

        Returns:
            Validation result
        """
        errors = []

        for param in tool.parameters:
            param_name = param.name

            # Check if required parameter is present
            if param.required and param_name not in input_data:
                errors.append(f"Required parameter '{param_name}' is missing")
                continue

            # Skip validation if parameter is not provided and not required
            if param_name not in input_data:
                continue

            value = input_data[param_name]

            # Type validation
            if param.type == "string" and not isinstance(value, str):
                errors.append(f"Parameter '{param_name}' must be a string")
            elif param.type == "number" and not isinstance(value, (int, float)):
                errors.append(f"Parameter '{param_name}' must be a number")
            elif param.type == "boolean" and not isinstance(value, bool):
                errors.append(f"Parameter '{param_name}' must be a boolean")
            elif param.type == "array" and not isinstance(value, list):
                errors.append(f"Parameter '{param_name}' must be an array")
            elif param.type == "object" and not isinstance(value, dict):
                errors.append(f"Parameter '{param_name}' must be an object")

            # Enum validation
            if param.enum and value not in param.enum:
                errors.append(
                    f"Parameter '{param_name}' must be one of: {', '.join(param.enum)}",
                )

        return {
            "valid": len(errors) == 0,
            "errors": errors,
        }

    def get_tools_by_category(self, category: str) -> list[Tool]:
        """
        Get tools by category.

        Args:
            category: Category to filter by

        Returns:
            List of tools in category
        """
        return [t for t in self.tools if t.category == category]

    def get_tools_by_type(self, tool_type: ToolType) -> list[Tool]:
        """
        Get tools by type.

        Args:
            tool_type: Tool type to filter by

        Returns:
            List of tools of specified type
        """
        return [t for t in self.tools if t.tool_type == tool_type]

    def search_tools(self, query: str) -> list[Tool]:
        """
        Search tools by name or description.

        Args:
            query: Search query

        Returns:
            List of matching tools
        """
        query_lower = query.lower()
        return [
            t
            for t in self.tools
            if query_lower in t.name.lower() or query_lower in t.description.lower()
        ]

    def get_active_tools(self) -> list[Tool]:
        """
        Get only active tools.

        Returns:
            List of active tools
        """
        return [t for t in self.tools if t.status == ToolStatus.ACTIVE]

    def get_tool_categories(self) -> list[str]:
        """
        Get all tool categories.

        Returns:
            List of unique categories
        """
        return list(set(t.category for t in self.tools))

    def get_tool_stats(self) -> dict[str, Any]:
        """
        Get tool statistics.

        Returns:
            Dictionary with statistics
        """
        total = len(self.tools)
        active = len(self.get_active_tools())

        categories = self.get_tool_categories()
        type_counts = {}
        for tool_type in ToolType:
            type_counts[tool_type.value] = len(self.get_tools_by_type(tool_type))

        return {
            "total_tools": total,
            "active_tools": active,
            "inactive_tools": total - active,
            "categories": categories,
            "category_count": len(categories),
            "type_counts": type_counts,
            "recent_executions": len(
                [r for r in self.execution_history if r.execution_time > 0],
            ),
        }

    def get_execution_history(self, limit: int = 50) -> list[ToolExecutionResult]:
        """
        Get recent tool execution history.

        Args:
            limit: Maximum number of results

        Returns:
            List of recent executions
        """
        return sorted(
            self.execution_history,
            key=lambda x: x.execution_time,
            reverse=True,
        )[:limit]

    def _create_tool_from_data(
        self, data: dict[str, Any], tool_type: ToolType = ToolType.FUNCTION,
    ) -> Tool:
        """
        Create Tool object from API data.

        Args:
            data: API response data
            tool_type: Tool type (defaults to FUNCTION)

        Returns:
            Tool object
        """
        # Parse parameters
        parameters = []
        for param_data in data.get("parameters", []):
            param = ToolParameter(
                name=param_data.get("name", ""),
                type=param_data.get("type", "string"),
                description=param_data.get("description", ""),
                required=param_data.get("required", False),
                default=param_data.get("default"),
                enum=param_data.get("enum"),
            )
            parameters.append(param)

        return Tool(
            id=data.get("id", generate_id("tool_")),
            name=data.get("name", ""),
            description=data.get("description", ""),
            tool_type=tool_type,
            status=ToolStatus(data.get("status", "active")),
            category=data.get("category", "general"),
            parameters=parameters,
            created_at=datetime.fromisoformat(data["created_at"])
            if data.get("created_at")
            else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"])
            if data.get("updated_at")
            else datetime.now(),
            version=data.get("version", "1.0.0"),
            author=data.get("author"),
            tags=data.get("tags", []),
            metadata=data.get("metadata"),
        )


# Global tool service instance
tool_service = ToolService()
