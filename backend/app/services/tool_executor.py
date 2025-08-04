"""
Tool Executor for MCP (Model Context Protocol) tool execution.

This module provides a comprehensive tool execution framework for
MCP tools with validation, error handling, and result processing.
"""

import asyncio
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from loguru import logger

from backend.app.services.tool_executor_base import (
    BaseToolExecutor,
    ToolDefinition,
    ToolExecution,
    ToolExecutionStatus,
    ToolParameter,
    ToolType,
)
from backend.app.services.tool_service import tool_service

if TYPE_CHECKING:
    from collections.abc import Callable


class ToolExecutor(BaseToolExecutor):
    """MCP tool execution framework."""

    def __init__(self):
        """Initialize the tool executor."""
        super().__init__()
        self.execution_handlers: Dict[str, Callable] = {}
        self._load_tools()

    def _load_tools(self):
        """Load available tools from tool service."""
        try:
            available_tools = tool_service.get_available_tools()
            for tool_data in available_tools:
                tool_def = self._create_tool_definition(tool_data)
                self.tools[tool_def.id] = tool_def
                logger.info(f"Loaded tool: {tool_def.name} ({tool_def.id})")
        except Exception as e:
            logger.error(f"Failed to load tools: {e}")

    def _create_tool_definition(self, tool_data: Dict[str, Any]) -> ToolDefinition:
        """Create tool definition from tool data."""
        parameters = []
        for param_data in tool_data.get("parameters", []):
            param = ToolParameter(
                name=param_data.get("name", ""),
                type=param_data.get("type", "string"),
                description=param_data.get("description", ""),
                required=param_data.get("required", False),
                default=param_data.get("default"),
                enum=param_data.get("enum"),
                min_value=param_data.get("min_value"),
                max_value=param_data.get("max_value"),
            )
            parameters.append(param)

        return ToolDefinition(
            id=tool_data.get("id", ""),
            name=tool_data.get("name", ""),
            description=tool_data.get("description", ""),
            type=ToolType(tool_data.get("type", "custom")),
            parameters=parameters,
            returns=tool_data.get("returns"),
            timeout=tool_data.get("timeout", 30),
            enabled=tool_data.get("enabled", True),
            metadata=tool_data.get("metadata", {}),
        )

    async def execute_tool(
        self,
        tool_id: str,
        parameters: Dict[str, Any],
        user_id: str,
        conversation_id: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> ToolExecution:
        """Execute a tool."""
        # Get tool definition
        tool_def = self.get_tool_definition(tool_id)
        if not tool_def:
            raise ValueError(f"Tool not found: {tool_id}")

        if not tool_def.enabled:
            raise ValueError(f"Tool is disabled: {tool_id}")

        # Create execution
        execution = self._create_execution(tool_id, user_id, conversation_id, parameters)

        try:
            # Validate parameters
            validated_params = self._validate_parameters(tool_def, parameters)
            execution.parameters = validated_params

            # Update status to running
            self._update_execution(execution, ToolExecutionStatus.RUNNING)

            # Execute based on tool type
            if tool_def.type == ToolType.MCP:
                result = await self._execute_mcp_tool(tool_def, validated_params, user_id)
            elif tool_def.type == ToolType.FUNCTION:
                result = await self._execute_function_tool(tool_def, validated_params, user_id)
            elif tool_def.type == ToolType.API:
                result = await self._execute_api_tool(tool_def, validated_params, user_id)
            else:
                result = await self._execute_custom_tool(tool_def, validated_params, user_id)

            # Update execution with success
            self._update_execution(execution, ToolExecutionStatus.COMPLETED, result=result)

        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            self._update_execution(execution, ToolExecutionStatus.FAILED, error=str(e))

        return execution

    async def _execute_mcp_tool(
        self,
        tool_def: ToolDefinition,
        parameters: Dict[str, Any],
        user_id: str,
    ) -> Any:
        """Execute MCP tool."""
        from backend.app.tools.mcp_tool import mcp_manager

        try:
            result = await mcp_manager.execute_tool(tool_def.name, parameters)
            return result
        except Exception as e:
            logger.error(f"MCP tool execution failed: {e}")
            raise

    async def _execute_function_tool(
        self,
        tool_def: ToolDefinition,
        parameters: Dict[str, Any],
        user_id: str,
    ) -> Any:
        """Execute function tool."""
        handler = self.execution_handlers.get(tool_def.id)
        if not handler:
            raise ValueError(f"No handler found for tool: {tool_def.id}")

        try:
            if asyncio.iscoroutinefunction(handler):
                result = await handler(parameters, user_id)
            else:
                result = handler(parameters, user_id)
            return result
        except Exception as e:
            logger.error(f"Function tool execution failed: {e}")
            raise

    async def _execute_api_tool(
        self,
        tool_def: ToolDefinition,
        parameters: Dict[str, Any],
        user_id: str,
    ) -> Any:
        """Execute API tool."""
        # Implementation for API tools
        raise NotImplementedError("API tool execution not implemented")

    async def _execute_custom_tool(
        self,
        tool_def: ToolDefinition,
        parameters: Dict[str, Any],
        user_id: str,
    ) -> Any:
        """Execute custom tool."""
        # Implementation for custom tools
        raise NotImplementedError("Custom tool execution not implemented")

    def get_tool_definition(self, tool_id: str) -> Optional[ToolDefinition]:
        """Get tool definition by ID."""
        return self.tools.get(tool_id)

    def get_available_tools(self) -> List[ToolDefinition]:
        """Get list of available tools."""
        return list(self.tools.values())

    def get_tool_schema(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Get tool schema for API documentation."""
        tool_def = self.get_tool_definition(tool_id)
        if not tool_def:
            return None

        schema = {
            "id": tool_def.id,
            "name": tool_def.name,
            "description": tool_def.description,
            "type": tool_def.type.value,
            "parameters": [
                {
                    "name": param.name,
                    "type": param.type,
                    "description": param.description,
                    "required": param.required,
                    "default": param.default,
                    "enum": param.enum,
                    "min_value": param.min_value,
                    "max_value": param.max_value,
                }
                for param in tool_def.parameters
            ],
            "returns": tool_def.returns,
            "timeout": tool_def.timeout,
            "enabled": tool_def.enabled,
            "metadata": tool_def.metadata,
        }

        return schema

    def register_handler(self, tool_id: str, handler: Callable) -> None:
        """Register a handler for a function tool."""
        self.execution_handlers[tool_id] = handler
        logger.info(f"Registered handler for tool: {tool_id}")

    def unregister_handler(self, tool_id: str) -> None:
        """Unregister a handler for a function tool."""
        if tool_id in self.execution_handlers:
            del self.execution_handlers[tool_id]
            logger.info(f"Unregistered handler for tool: {tool_id}")


# Global tool executor instance
tool_executor = ToolExecutor()
