"""
Assistant Tools Manager Service.

This module provides tool management functionality for assistant processing,
including tool preparation, execution, and result handling.
"""

from typing import Any

from loguru import logger

from backend.app.services.tool_executor_v2 import (
    enhanced_tool_executor as tool_executor,
    ToolExecutionRequest,
)
from backend.app.services.tool_service import tool_service


class ProcessingRequest:
    """Request for message processing."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class AIResponse:
    """AI response with structured output."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class AssistantToolsManager:
    """Manager for assistant tools and tool execution."""

    def __init__(self):
        """Initialize the tools manager."""
        self.tool_executor = tool_executor
        self.tool_service = tool_service

    async def prepare_tools(self, user_message: str) -> list[dict[str, Any]]:
        """
        Prepare available tools for the request.

        Args:
            user_message: User message

        Returns:
            List[dict]: Available tools
        """
        try:
            # Get available tools
            available_tools = await self.tool_service.get_available_tools()

            # Filter tools based on user message (basic relevance check)
            relevant_tools = self._filter_relevant_tools(user_message, available_tools)

            # Format tools for AI
            formatted_tools = []
            for tool in relevant_tools:
                formatted_tool = {
                    "id": tool.get("id"),
                    "name": tool.get("name"),
                    "description": tool.get("description"),
                    "category": tool.get("category"),
                    "parameters_schema": tool.get("parameters_schema"),
                }
                formatted_tools.append(formatted_tool)

            logger.debug(f"Prepared {len(formatted_tools)} tools for request")
            return formatted_tools

        except Exception as e:
            logger.error(f"Error preparing tools: {e}")
            return []

    def _filter_relevant_tools(
        self, user_message: str, available_tools: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Filter tools based on relevance to user message.

        Args:
            user_message: User message
            available_tools: Available tools

        Returns:
            List[dict]: Relevant tools
        """
        user_message_lower = user_message.lower()
        relevant_tools = []

        # Define tool keywords for relevance matching
        tool_keywords = {
            "search": ["suchen", "finden", "recherchieren", "search", "find"],
            "calculator": ["berechnen", "rechnen", "calculate", "compute", "math"],
            "file": ["datei", "file", "lesen", "read", "schreiben", "write"],
            "api": ["api", "daten", "data", "abrufen", "fetch"],
            "analysis": ["analysieren", "analyze", "auswerten", "evaluate"],
        }

        for tool in available_tools:
            tool_name = tool.get("name", "").lower()
            tool_description = tool.get("description", "").lower()
            tool_category = tool.get("category", "").lower()

            # Check if tool is relevant based on keywords
            is_relevant = False

            # Check tool name and description
            for keywords in tool_keywords.values():
                if any(
                    keyword in tool_name or keyword in tool_description
                    for keyword in keywords
                ) and any(keyword in user_message_lower for keyword in keywords):
                    is_relevant = True
                    break

            # Check tool category
            if tool_category in user_message_lower:
                is_relevant = True

            # Check for specific tool mentions
            if tool_name in user_message_lower:
                is_relevant = True

            if is_relevant:
                relevant_tools.append(tool)

        # If no relevant tools found, return all tools (fallback)
        if not relevant_tools:
            relevant_tools = available_tools

        return relevant_tools

    async def execute_tools(
        self, tool_calls: list[dict[str, Any]], user_id: str | None = None, conversation_id: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Execute tool calls.

        Args:
            tool_calls: List of tool calls to execute
            user_id: User ID for RBAC and auditing
            conversation_id: Conversation ID for context

        Returns:
            List[dict]: Tool execution results
        """
        try:
            results = []

            for tool_call in tool_calls:
                tool_id = tool_call.get("id")
                tool_name = tool_call.get("name")
                arguments = tool_call.get("arguments", {})

                logger.debug(f"Executing tool: {tool_name} with arguments: {arguments}")

                try:
                    # Build validated execution request
                    exec_request = ToolExecutionRequest(
                        tool_name=tool_name,
                        arguments=arguments,
                        user_id=user_id or "anonymous",
                        conversation_id=conversation_id or "unknown",
                    )

                    # Execute tool via enhanced executor
                    result = await self.tool_executor.execute_tool(exec_request)

                    # Format result
                    formatted_result = {
                        "tool_id": tool_id,
                        "tool_name": tool_name,
                        "success": result.status == "completed",
                        "result": result.result,
                        "error": result.error,
                        "execution_time": result.execution_time or 0.0,
                        "execution_id": result.execution_id,
                        "cache_hit": result.cache_hit,
                    }

                    results.append(formatted_result)

                    logger.debug(f"Tool {tool_name} executed successfully")

                except Exception as e:
                    logger.error(f"Tool {tool_name} execution failed: {e}")
                    results.append(
                        {
                            "tool_id": tool_id,
                            "tool_name": tool_name,
                            "success": False,
                            "result": None,
                            "error": str(e),
                            "execution_time": 0.0,
                        }
                    )

            return results

        except Exception as e:
            logger.error(f"Error executing tools: {e}")
            return []

    async def validate_tool_call(
        self, tool_call: dict[str, Any]
    ) -> tuple[bool, str | None]:
        """
        Validate tool call before execution.

        Args:
            tool_call: Tool call to validate

        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            tool_name = tool_call.get("name")
            arguments = tool_call.get("arguments", {})

            if not tool_name:
                return False, "Tool name is required"

            # Check if tool exists
            tool = await self.tool_service.get_tool_by_name(tool_name)
            if not tool:
                return False, f"Tool '{tool_name}' not found"

            # Validate arguments against schema
            if tool.get("parameters_schema"):
                schema = tool["parameters_schema"]
                validation_result = self._validate_arguments(arguments, schema)
                if not validation_result[0]:
                    return validation_result

            return True, None

        except Exception as e:
            return False, f"Validation error: {str(e)}"

    def _validate_arguments(
        self, arguments: dict[str, Any], schema: dict[str, Any]
    ) -> tuple[bool, str | None]:
        """
        Validate arguments against JSON schema.

        Args:
            arguments: Arguments to validate
            schema: JSON schema

        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            # Basic validation - in production, use proper JSON schema validation
            required_properties = schema.get("required", [])
            properties = schema.get("properties", {})

            # Check required properties
            for prop in required_properties:
                if prop not in arguments:
                    return False, f"Required argument '{prop}' is missing"

            # Check argument types (basic)
            for arg_name, arg_value in arguments.items():
                if arg_name in properties:
                    expected_type = properties[arg_name].get("type")
                    if expected_type:
                        if expected_type == "string" and not isinstance(arg_value, str):
                            return False, f"Argument '{arg_name}' must be a string"
                        if expected_type == "number" and not isinstance(
                            arg_value, int | float
                        ):
                            return False, f"Argument '{arg_name}' must be a number"
                        if expected_type == "boolean" and not isinstance(
                            arg_value, bool
                        ):
                            return False, f"Argument '{arg_name}' must be a boolean"

            return True, None

        except Exception as e:
            return False, f"Schema validation error: {str(e)}"

    async def get_tool_usage_stats(self, time_period_hours: int = 24) -> dict[str, Any]:
        """
        Get tool usage statistics.

        Args:
            time_period_hours: Time period for statistics

        Returns:
            dict: Tool usage statistics
        """
        try:
            # Get tool execution history
            tool_stats = await self.tool_service.get_tool_usage_stats(time_period_hours)

            return {
                "time_period_hours": time_period_hours,
                "total_tool_executions": tool_stats.get("total_executions", 0),
                "successful_executions": tool_stats.get("successful_executions", 0),
                "failed_executions": tool_stats.get("failed_executions", 0),
                "most_used_tools": tool_stats.get("most_used_tools", []),
                "average_execution_time": tool_stats.get("average_execution_time", 0.0),
            }

        except Exception as e:
            logger.error(f"Error getting tool usage stats: {e}")
            return {"error": str(e)}

    async def get_available_tool_categories(self) -> list[str]:
        """
        Get available tool categories.

        Returns:
            List[str]: Available tool categories
        """
        try:
            tools = await self.tool_service.get_available_tools()
            categories = {
                tool.get("category") for tool in tools if tool.get("category")
            }
            return list(categories)

        except Exception as e:
            logger.error(f"Error getting tool categories: {e}")
            return []

    def get_tools_stats(self) -> dict[str, Any]:
        """
        Get tools manager statistics.

        Returns:
            dict: Tools manager statistics
        """
        try:
            return {
                "total_available_tools": 0,  # Will be populated by tool service
                "tool_categories": [],  # Will be populated by tool service
                "execution_stats": {
                    "total_executions": 0,
                    "successful_executions": 0,
                    "failed_executions": 0,
                },
            }

        except Exception as e:
            logger.error(f"Error getting tools stats: {e}")
            return {"error": str(e)}


# Global tools manager instance
assistant_tools_manager = AssistantToolsManager()
