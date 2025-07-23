"""
Example MCP Server for testing.

This module provides a simple MCP server implementation for testing
the MCP integration in the AI Assistant Platform.
"""

import asyncio
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from aiohttp import web
from loguru import logger


@dataclass
class ExampleTool:
    """Example tool definition."""

    name: str
    description: str
    input_schema: dict[str, Any]


class ExampleMCPServer:
    """Example MCP server implementation."""

    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
        self.app = web.Application()
        self.setup_routes()

        # Define example tools
        self.tools = [
            ExampleTool(
                name="get_weather",
                description="Get current weather information for a location",
                input_schema={
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "City name or coordinates",
                        },
                        "units": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                            "default": "celsius",
                            "description": "Temperature units",
                        },
                    },
                    "required": ["location"],
                },
            ),
            ExampleTool(
                name="calculate",
                description="Perform mathematical calculations",
                input_schema={
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Mathematical expression to evaluate",
                        },
                    },
                    "required": ["expression"],
                },
            ),
            ExampleTool(
                name="translate_text",
                description="Translate text between languages",
                input_schema={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Text to translate",
                        },
                        "source_lang": {
                            "type": "string",
                            "description": "Source language code",
                            "default": "auto",
                        },
                        "target_lang": {
                            "type": "string",
                            "description": "Target language code",
                        },
                    },
                    "required": ["text", "target_lang"],
                },
            ),
            ExampleTool(
                name="get_time",
                description="Get current time for a timezone",
                input_schema={
                    "type": "object",
                    "properties": {
                        "timezone": {
                            "type": "string",
                            "description": "Timezone name (e.g., 'UTC', 'Europe/Berlin')",
                            "default": "UTC",
                        },
                    },
                },
            ),
        ]

        # Define example resources
        self.resources = [
            {
                "uri": "example://docs/api",
                "name": "API Documentation",
                "description": "API documentation for the example server",
                "mimeType": "text/markdown",
            },
            {
                "uri": "example://config/settings",
                "name": "Server Settings",
                "description": "Current server configuration",
                "mimeType": "application/json",
            },
        ]

    def setup_routes(self):
        """Setup HTTP routes for the MCP server."""
        self.app.router.add_post("/", self.handle_request)
        self.app.router.add_get("/health", self.health_check)

    async def handle_request(self, request: web.Request) -> web.Response:
        """Handle MCP protocol requests."""
        try:
            data = await request.json()
            method = data.get("method")
            request_id = data.get("id", 1)

            logger.info(f"MCP request: {method}")

            if method == "initialize":
                return await self.handle_initialize(data, request_id)
            if method == "tools/list":
                return await self.handle_list_tools(data, request_id)
            if method == "tools/call":
                return await self.handle_call_tool(data, request_id)
            if method == "resources/list":
                return await self.handle_list_resources(data, request_id)
            if method == "resources/read":
                return await self.handle_read_resource(data, request_id)
            return self.create_error_response(request_id, -32601, "Method not found")

        except Exception as e:
            logger.error(f"Error handling MCP request: {e}")
            return self.create_error_response(1, -32603, "Internal error")

    async def handle_initialize(
        self, data: dict[str, Any], request_id: int,
    ) -> web.Response:
        """Handle initialize request."""
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "resources": {},
                    "promises": {},
                },
                "serverInfo": {
                    "name": "example-mcp-server",
                    "version": "1.0.0",
                },
            },
        }

        return web.json_response(response)

    async def handle_list_tools(
        self, data: dict[str, Any], request_id: int,
    ) -> web.Response:
        """Handle tools/list request."""
        tools_data = [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.input_schema,
            }
            for tool in self.tools
        ]

        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": tools_data,
            },
        }

        return web.json_response(response)

    async def handle_call_tool(
        self, data: dict[str, Any], request_id: int,
    ) -> web.Response:
        """Handle tools/call request."""
        params = data.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        # Find the tool
        tool = None
        for t in self.tools:
            if t.name == tool_name:
                tool = t
                break

        if not tool:
            return self.create_error_response(
                request_id, -32602, f"Tool '{tool_name}' not found",
            )

        # Execute the tool
        try:
            result = await self.execute_tool(tool_name, arguments)

            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": result,
                },
            }

            return web.json_response(response)

        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return self.create_error_response(
                request_id, -32603, f"Tool execution failed: {str(e)}",
            )

    async def handle_list_resources(
        self, data: dict[str, Any], request_id: int,
    ) -> web.Response:
        """Handle resources/list request."""
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "resources": self.resources,
            },
        }

        return web.json_response(response)

    async def handle_read_resource(
        self, data: dict[str, Any], request_id: int,
    ) -> web.Response:
        """Handle resources/read request."""
        params = data.get("params", {})
        uri = params.get("uri")

        # Find the resource
        resource = None
        for r in self.resources:
            if r["uri"] == uri:
                resource = r
                break

        if not resource:
            return self.create_error_response(
                request_id, -32602, f"Resource '{uri}' not found",
            )

        # Return resource content
        if uri == "example://docs/api":
            content = (
                "# Example MCP Server API\n\nThis is an example MCP server for testing."
            )
        elif uri == "example://config/settings":
            content = json.dumps(
                {
                    "server_name": "example-mcp-server",
                    "version": "1.0.0",
                    "tools_count": len(self.tools),
                    "resources_count": len(self.resources),
                },
                indent=2,
            )
        else:
            content = "Resource content not available"

        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": resource["mimeType"],
                        "text": content,
                    },
                ],
            },
        }

        return web.json_response(response)

    async def execute_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """Execute a tool with given arguments."""
        if tool_name == "get_weather":
            location = arguments.get("location", "Unknown")
            units = arguments.get("units", "celsius")

            # Simulate weather data
            weather_data = {
                "location": location,
                "temperature": 22 if units == "celsius" else 72,
                "units": units,
                "condition": "sunny",
                "humidity": 65,
                "wind_speed": 12,
            }

            return f"Weather in {location}: {weather_data['temperature']}°{units[0].upper()}, {weather_data['condition']}"

        if tool_name == "calculate":
            expression = arguments.get("expression", "")

            try:
                # Safe evaluation (in production, use a proper math library)
                import ast
                result = ast.literal_eval(expression)
                return f"Result: {result}"
            except Exception as e:
                return f"Calculation error: {str(e)}"

        elif tool_name == "translate_text":
            text = arguments.get("text", "")
            arguments.get("source_lang", "auto")
            target_lang = arguments.get("target_lang", "en")

            # Simulate translation
            translations = {
                "hello": {"de": "hallo", "es": "hola", "fr": "bonjour"},
                "world": {"de": "welt", "es": "mundo", "fr": "monde"},
            }

            if (
                text.lower() in translations
                and target_lang in translations[text.lower()]
            ):
                translated = translations[text.lower()][target_lang]
            else:
                translated = f"[{target_lang.upper()}] {text}"

            return f"Translation: {translated}"

        elif tool_name == "get_time":
            timezone = arguments.get("timezone", "UTC")
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            return f"Current time in {timezone}: {current_time}"

        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    def create_error_response(
        self, request_id: int, code: int, message: str,
    ) -> web.Response:
        """Create an error response."""
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message,
            },
        }

        return web.json_response(response)

    async def health_check(self, request: web.Request) -> web.Response:
        """Health check endpoint."""
        return web.json_response(
            {
                "status": "healthy",
                "server": "example-mcp-server",
                "version": "1.0.0",
                "tools_count": len(self.tools),
                "resources_count": len(self.resources),
            },
        )

    async def start(self):
        """Start the MCP server."""
        runner = web.AppRunner(self.app)
        await runner.setup()

        site = web.TCPSite(runner, self.host, self.port)
        await site.start()

        logger.info(f"Example MCP server running on http://{self.host}:{self.port}")
        logger.info(f"Health check: http://{self.host}:{self.port}/health")

        return runner

    async def stop(self, runner: web.AppRunner):
        """Stop the MCP server."""
        await runner.cleanup()


async def main():
    """Main function to run the example MCP server."""
    server = ExampleMCPServer()
    runner = await server.start()

    try:
        # Keep the server running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down example MCP server...")
        await server.stop(runner)


if __name__ == "__main__":
    asyncio.run(main())
