"""Tool Middleware for AI Service."""

import re
import time
from typing import Any, Dict, List

from ..types.ai_types import ToolCall
from ..utils.tool_manager import ToolManager


class ToolMiddleware:
    """Tool integration middleware for AI service."""

    def __init__(self, tool_manager=None):
        """Initialize tool middleware with optional tool manager."""
        self.tool_manager = tool_manager or ToolManager()

    async def process(
        self,
        messages: List[Dict[str, str]],
        use_tools: bool = True,
    ) -> List[Dict[str, str]]:
        """Process messages with tool integration."""
        if not use_tools:
            return messages

        try:
            # Get available tools
            available_tools = self.tool_manager.get_available_tools()
            if not available_tools:
                return messages

            # Add tool information to system message
            enhanced_messages = self._add_tool_information(messages, available_tools)
            return enhanced_messages

        except Exception as e:
            # Log error but continue without tool enhancement
            print(f"Tool processing failed: {str(e)}")
            return messages

    def _add_tool_information(
        self, messages: List[Dict[str, str]], available_tools: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """Add tool information to system message."""
        enhanced_messages = messages.copy()

        # Create tool prompt
        tool_prompt = self._create_tool_prompt(available_tools)

        # Find or create system message
        system_message_index = -1
        for i, message in enumerate(enhanced_messages):
            if message.get("role") == "system":
                system_message_index = i
                break

        if system_message_index >= 0:
            # Enhance existing system message
            existing_content = enhanced_messages[system_message_index].get(
                "content", ""
            )
            enhanced_content = existing_content + "\n\n" + tool_prompt
            enhanced_messages[system_message_index]["content"] = enhanced_content
        else:
            # Create new system message
            system_message = {"role": "system", "content": tool_prompt}
            enhanced_messages.insert(0, system_message)

        return enhanced_messages

    def _create_tool_prompt(self, available_tools: List[Dict[str, Any]]) -> str:
        """Create a prompt describing available tools."""
        if not available_tools:
            return ""

        prompt = "You have access to the following tools:\n\n"

        for tool in available_tools:
            name = tool.get("name", "Unknown")
            description = tool.get("description", "No description available")
            parameters = tool.get("parameters", {})

            prompt += f"**{name}**: {description}\n"

            if parameters:
                prompt += "Parameters:\n"
                for param_name, param_info in parameters.items():
                    param_type = param_info.get("type", "string")
                    param_desc = param_info.get("description", "")
                    required = param_info.get("required", False)
                    req_text = " (required)" if required else " (optional)"
                    prompt += (
                        f"  - {param_name}: {param_type}{req_text} - {param_desc}\n"
                    )

            prompt += "\n"

        prompt += """To use a tool, respond with the following format:

<tool_call>
<tool_name>tool_name</tool_name>
<parameters>
{"param1": "value1", "param2": "value2"}
</parameters>
</tool_call>

You can make multiple tool calls if needed. After making tool calls, wait for the results before providing your final response to the user."""

        return prompt

    async def execute_tools_from_response(
        self, ai_response: str, user_id: str
    ) -> List[Dict[str, Any]]:
        """Execute tools based on AI response."""
        try:
            # Extract tool calls from AI response
            tool_calls = self._extract_tool_calls(ai_response)
            if not tool_calls:
                return []

            # Execute each tool call with timing
            results = []
            for tool_call in tool_calls:
                try:
                    # Start timing
                    start_time = time.time()

                    result = await self.tool_manager.execute_tool(
                        tool_name=tool_call.tool_name,
                        parameters=tool_call.parameters,
                        user_id=user_id,
                    )

                    # Calculate execution time
                    execution_time = time.time() - start_time

                    results.append(
                        {
                            "tool": tool_call.tool_name,
                            "parameters": tool_call.parameters,
                            "result": result,
                            "success": True,
                            "execution_time": execution_time,
                        }
                    )
                except Exception as e:
                    # Calculate execution time even for failed executions
                    execution_time = (
                        time.time() - start_time if "start_time" in locals() else 0.0
                    )

                    results.append(
                        {
                            "tool": tool_call.tool_name,
                            "parameters": tool_call.parameters,
                            "result": str(e),
                            "success": False,
                            "execution_time": execution_time,
                        }
                    )

            return results

        except Exception as e:
            print(f"Tool execution failed: {str(e)}")
            return []

    def _extract_tool_calls(self, ai_response: str) -> List[ToolCall]:
        """Extract tool calls from AI response."""
        tool_calls = []

        # Pattern to match tool calls
        pattern = r"<tool_call>\s*<tool_name>(.*?)</tool_name>\s*<parameters>\s*(.*?)\s*</parameters>\s*</tool_call>"
        matches = re.findall(pattern, ai_response, re.DOTALL)

        for tool_name, parameters_str in matches:
            try:
                import json

                parameters = json.loads(parameters_str.strip())

                tool_call = ToolCall(
                    tool_name=tool_name.strip(),
                    parameters=parameters,
                )
                tool_calls.append(tool_call)
            except (json.JSONDecodeError, Exception) as e:
                print(f"Failed to parse tool call: {str(e)}")
                continue

        return tool_calls

    def should_apply_tools(
        self, messages: List[Dict[str, str]], use_tools: bool
    ) -> bool:
        """Determine if tools should be applied."""
        if not use_tools:
            return False

        if not messages:
            return False

        # Check if there are available tools
        available_tools = self.tool_manager.get_available_tools()
        if not available_tools:
            return False

        # Check if there's a user message that might benefit from tools
        has_user_message = any(message.get("role") == "user" for message in messages)

        return has_user_message

    def get_tool_metrics(self, tool_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get metrics about tool execution."""
        if not tool_results:
            return {
                "tools_executed": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "total_execution_time": 0.0,
                "avg_execution_time": 0.0,
            }

        successful = sum(1 for result in tool_results if result.get("success", False))
        failed = len(tool_results) - successful
        total_execution_time = sum(
            result.get("execution_time", 0.0) for result in tool_results
        )
        avg_execution_time = (
            total_execution_time / len(tool_results) if tool_results else 0.0
        )

        return {
            "tools_executed": len(tool_results),
            "successful_executions": successful,
            "failed_executions": failed,
            "total_execution_time": total_execution_time,
            "avg_execution_time": avg_execution_time,
        }
