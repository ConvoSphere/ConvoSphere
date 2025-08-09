"""Tool Middleware for AI Service."""

import json
import re
from typing import Any, Dict, List, Optional

from ..types.ai_types import ToolInfo, ToolCall


class ToolMiddleware:
    """Tool integration and execution middleware."""

    def __init__(self, tool_manager=None):
        self.tool_manager = tool_manager

    async def process(
        self,
        messages: List[Dict[str, str]],
        use_tools: bool = True,
    ) -> List[Dict[str, str]]:
        """Process messages with tool integration."""
        if not use_tools or not messages:
            return messages

        try:
            # Get available tools
            tools = await self._get_available_tools()
            if not tools:
                return messages

            # Add tool information to system message
            enhanced_messages = self._add_tool_information(messages, tools)
            return enhanced_messages

        except Exception as e:
            # Log error but continue without tool enhancement
            print(f"Tool processing failed: {str(e)}")
            return messages

    async def execute_tools_from_response(
        self, ai_response: str, user_id: str
    ) -> List[Dict[str, Any]]:
        """Execute tools based on AI response."""
        if not self.tool_manager:
            return []

        try:
            # Extract tool calls from AI response
            tool_calls = self._extract_tool_calls(ai_response)
            if not tool_calls:
                return []

            # Execute each tool call
            results = []
            for tool_call in tool_calls:
                result = await self._execute_tool_call(tool_call, user_id)
                if result:
                    results.append(result)

            return results

        except Exception as e:
            print(f"Tool execution failed: {str(e)}")
            return []

    async def _get_available_tools(self) -> List[ToolInfo]:
        """Get available tools from tool manager."""
        if not self.tool_manager:
            return []

        try:
            # Use existing tool manager to get tools
            tools_data = self.tool_manager.get_available_tools()
            
            tools = []
            for tool_data in tools_data:
                tool = ToolInfo(
                    name=tool_data.get("name", ""),
                    description=tool_data.get("description", ""),
                    parameters=tool_data.get("parameters", {}),
                    required=tool_data.get("required", False),
                )
                tools.append(tool)
            
            return tools

        except Exception as e:
            print(f"Failed to get available tools: {str(e)}")
            return []

    def _add_tool_information(
        self, messages: List[Dict[str, str]], tools: List[ToolInfo]
    ) -> List[Dict[str, str]]:
        """Add tool information to system message."""
        if not tools:
            return messages

        # Create tool prompt
        tool_prompt = self._create_tool_prompt(tools)

        # Add to system message or create new one
        enhanced_messages = []
        tool_info_added = False

        for message in messages:
            if message.get("role") == "system" and not tool_info_added:
                # Enhance existing system message
                enhanced_content = message.get("content", "") + "\n\n" + tool_prompt
                enhanced_messages.append({
                    "role": "system",
                    "content": enhanced_content
                })
                tool_info_added = True
            else:
                enhanced_messages.append(message)

        # If no system message found, add one at the beginning
        if not tool_info_added:
            enhanced_messages.insert(0, {
                "role": "system",
                "content": tool_prompt
            })

        return enhanced_messages

    def _create_tool_prompt(self, tools: List[ToolInfo]) -> str:
        """Create a prompt describing available tools."""
        prompt = "You have access to the following tools:\n\n"
        
        for tool in tools:
            prompt += f"Tool: {tool.name}\n"
            prompt += f"Description: {tool.description}\n"
            
            if tool.parameters:
                prompt += "Parameters:\n"
                for param_name, param_info in tool.parameters.items():
                    param_type = param_info.get("type", "string")
                    param_desc = param_info.get("description", "")
                    required = param_info.get("required", False)
                    
                    prompt += f"  - {param_name} ({param_type})"
                    if required:
                        prompt += " [required]"
                    if param_desc:
                        prompt += f": {param_desc}"
                    prompt += "\n"
            
            prompt += "\n"
        
        prompt += "To use a tool, respond with a JSON object in this format:\n"
        prompt += '{"tool": "tool_name", "arguments": {"param1": "value1", "param2": "value2"}}\n\n'
        prompt += "You can use multiple tools in sequence if needed."
        
        return prompt

    def _extract_tool_calls(self, ai_response: str) -> List[ToolCall]:
        """Extract tool calls from AI response."""
        tool_calls = []
        
        # Look for JSON tool calls in the response
        json_pattern = r'\{[^{}]*"tool"[^{}]*\}'
        matches = re.findall(json_pattern, ai_response)
        
        for match in matches:
            try:
                tool_data = json.loads(match)
                if "tool" in tool_data and "arguments" in tool_data:
                    tool_call = ToolCall(
                        tool_name=tool_data["tool"],
                        arguments=tool_data["arguments"],
                    )
                    tool_calls.append(tool_call)
            except json.JSONDecodeError:
                continue
        
        return tool_calls

    async def _execute_tool_call(
        self, tool_call: ToolCall, user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Execute a single tool call."""
        if not self.tool_manager:
            return None

        try:
            # Use existing tool manager to execute tool
            result = await self.tool_manager.execute_tool(
                tool_call.tool_name,
                tool_call.arguments,
                user_id
            )
            
            tool_call.result = result
            
            return {
                "tool": tool_call.tool_name,
                "arguments": tool_call.arguments,
                "result": result,
                "success": True,
            }

        except Exception as e:
            print(f"Tool execution failed for {tool_call.tool_name}: {str(e)}")
            return {
                "tool": tool_call.tool_name,
                "arguments": tool_call.arguments,
                "result": None,
                "success": False,
                "error": str(e),
            }

    def should_apply_tools(self, messages: List[Dict[str, str]], use_tools: bool) -> bool:
        """Determine if tools should be applied."""
        if not use_tools:
            return False
        
        if not messages:
            return False
        
        # Check if there's a user message that might need tools
        has_user_message = any(
            message.get("role") == "user" for message in messages
        )
        
        return has_user_message

    def get_tool_metrics(self, tool_calls: List[ToolCall]) -> Dict[str, Any]:
        """Get metrics about tool usage."""
        if not tool_calls:
            return {
                "tools_called": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "unique_tools": 0,
            }
        
        successful = sum(1 for call in tool_calls if call.result is not None)
        failed = len(tool_calls) - successful
        unique_tools = len(set(call.tool_name for call in tool_calls))
        
        return {
            "tools_called": len(tool_calls),
            "successful_executions": successful,
            "failed_executions": failed,
            "unique_tools": unique_tools,
        }

    def format_tools_for_prompt(self) -> str:
        """Format tools information for prompt inclusion."""
        if not self.tool_manager:
            return ""

        try:
            return self.tool_manager.format_tools_for_prompt()
        except Exception as e:
            print(f"Failed to format tools for prompt: {str(e)}")
            return ""