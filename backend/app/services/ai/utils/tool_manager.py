"""Tool management utility for AI services."""

import json
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from backend.app.models.tool import Tool
from backend.app.tools.base import BaseTool


class ToolManager:
    """Manage AI tools and their execution."""

    def __init__(self, db: Session):
        self.db = db
        self._tools: Dict[str, BaseTool] = {}
        self._load_tools()

    def _load_tools(self) -> None:
        """Load available tools from database."""
        try:
            tools = self.db.query(Tool).filter(Tool.is_active == True).all()

            for tool in tools:
                # Import tool class dynamically
                try:
                    module_name, class_name = tool.class_path.rsplit(".", 1)
                    module = __import__(module_name, fromlist=[class_name])
                    tool_class = getattr(module, class_name)

                    # Initialize tool instance
                    tool_instance = tool_class(
                        name=tool.name,
                        description=tool.description,
                        parameters=tool.parameters,
                        db=self.db,
                    )

                    self._tools[tool.name] = tool_instance

                except Exception as e:
                    print(f"Failed to load tool {tool.name}: {str(e)}")
                    continue

        except Exception as e:
            print(f"Failed to load tools: {str(e)}")

    def get_available_tools(self) -> List[str]:
        """Get list of available tool names."""
        return list(self._tools.keys())

    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific tool."""
        if tool_name not in self._tools:
            return None

        tool = self._tools[tool_name]
        return {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.parameters,
            "required_parameters": tool.get_required_parameters(),
            "optional_parameters": tool.get_optional_parameters(),
        }

    def get_tools_for_prompt(self) -> List[Dict[str, Any]]:
        """Get tools formatted for inclusion in AI prompt."""
        tools_info = []

        for tool_name, tool in self._tools.items():
            tool_info = {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
            }
            tools_info.append(tool_info)

        return tools_info

    async def execute_tool(
        self, tool_name: str, parameters: Dict[str, Any], user_id: str
    ) -> Dict[str, Any]:
        """Execute a specific tool."""
        if tool_name not in self._tools:
            raise ValueError(f"Tool '{tool_name}' not found")

        tool = self._tools[tool_name]

        try:
            # Validate parameters
            tool.validate_parameters(parameters)

            # Execute tool
            result = await tool.execute(parameters, user_id)

            return {
                "success": True,
                "tool_name": tool_name,
                "result": result,
                "execution_time": result.get("execution_time", 0),
            }

        except Exception as e:
            return {
                "success": False,
                "tool_name": tool_name,
                "error": str(e),
                "execution_time": 0,
            }

    async def execute_tools_from_response(
        self, ai_response: str, user_id: str
    ) -> List[Dict[str, Any]]:
        """Execute tools based on AI response."""
        results = []

        try:
            # Parse tool calls from AI response
            tool_calls = self._parse_tool_calls(ai_response)

            for tool_call in tool_calls:
                tool_name = tool_call.get("tool")
                parameters = tool_call.get("parameters", {})

                if tool_name:
                    result = await self.execute_tool(tool_name, parameters, user_id)
                    results.append(result)

        except Exception as e:
            results.append(
                {"success": False, "error": f"Failed to parse tool calls: {str(e)}"}
            )

        return results

    def _parse_tool_calls(self, response: str) -> List[Dict[str, Any]]:
        """Parse tool calls from AI response."""
        tool_calls = []

        try:
            # Look for JSON blocks that might contain tool calls
            lines = response.split("\n")

            for line in lines:
                line = line.strip()

                # Check if line contains tool call
                if line.startswith("```json") or line.startswith("{"):
                    try:
                        # Remove markdown formatting
                        line = line.removeprefix("```json")
                        line = line.removesuffix("```")

                        # Parse JSON
                        data = json.loads(line)

                        # Check if it's a tool call
                        if isinstance(data, dict) and "tool" in data:
                            tool_calls.append(data)
                        elif isinstance(data, list):
                            for item in data:
                                if isinstance(item, dict) and "tool" in item:
                                    tool_calls.append(item)

                    except json.JSONDecodeError:
                        continue

        except Exception as e:
            print(f"Failed to parse tool calls: {str(e)}")

        return tool_calls

    def format_tools_for_prompt(self) -> str:
        """Format tools information for inclusion in prompt."""
        tools_info = self.get_tools_for_prompt()

        if not tools_info:
            return ""

        prompt = "Available tools:\n\n"

        for tool in tools_info:
            prompt += f"Tool: {tool['name']}\n"
            prompt += f"Description: {tool['description']}\n"
            prompt += f"Parameters: {json.dumps(tool['parameters'], indent=2)}\n\n"

        prompt += "To use a tool, respond with a JSON object containing 'tool' and 'parameters' fields.\n"
        prompt += (
            'Example: {"tool": "tool_name", "parameters": {"param1": "value1"}}\n\n'
        )

        return prompt

    def reload_tools(self) -> None:
        """Reload tools from database."""
        self._tools.clear()
        self._load_tools()

    def register_tool(self, tool_name: str, tool_instance: BaseTool) -> None:
        """Register a tool manually."""
        self._tools[tool_name] = tool_instance

    def unregister_tool(self, tool_name: str) -> None:
        """Unregister a tool."""
        if tool_name in self._tools:
            del self._tools[tool_name]
