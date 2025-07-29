"""
MCP (Model Context Protocol) tool integration.

This module provides MCP client functionality to connect to MCP servers
and use their tools within the AI Assistant Platform.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any

import aiohttp
from loguru import logger

from .base import BaseTool, ToolParameter, ToolResult


class MCPMessageType(str, Enum):
    """MCP message types."""

    HELLO = "hello"
    LIST_TOOLS = "list_tools"
    CALL_TOOL = "call_tool"
    LIST_RESOURCES = "list_resources"
    READ_RESOURCE = "read_resource"
    LIST_PROMISES = "list_promises"
    CANCEL_PROMISE = "cancel_promise"
    NOTIFY = "notify"


@dataclass
class MCPTool:
    """MCP tool definition."""

    name: str
    description: str
    input_schema: dict[str, Any]
    server_name: str
    server_version: str


@dataclass
class MCPResource:
    """MCP resource definition."""

    uri: str
    name: str
    description: str
    mime_type: str


class MCPClient:
    """MCP client for connecting to MCP servers."""

    def __init__(self, server_url: str, server_name: str = "mcp-server"):
        self.server_url = server_url
        self.server_name = server_name
        self.session: aiohttp.ClientSession | None = None
        self.tools: list[MCPTool] = []
        self.resources: list[MCPResource] = []
        self.is_connected = False

    async def connect(self) -> bool:
        """
        Connect to MCP server.

        Returns:
            bool: True if connection successful
        """
        try:
            self.session = aiohttp.ClientSession()

            # Send hello message
            hello_message = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {},
                        "promises": {},
                    },
                    "clientInfo": {
                        "name": "ai-assistant-platform",
                        "version": "0.1.0-beta",
                    },
                },
            }

            async with self.session.post(
                self.server_url,
                json=hello_message,
                headers={"Content-Type": "application/json"},
            ) as response:
                if response.status == 200:
                    await response.json()
                    logger.info(f"Connected to MCP server: {self.server_name}")
                    self.is_connected = True

                    # Load available tools and resources
                    await self._load_tools()
                    await self._load_resources()

                    return True
                logger.error(f"Failed to connect to MCP server: {response.status}")
                return False

        except Exception as e:
            logger.error(f"Error connecting to MCP server: {e}")
            return False

    async def disconnect(self):
        """Disconnect from MCP server."""
        if self.session:
            await self.session.close()
            self.session = None
        self.is_connected = False

    async def _load_tools(self):
        """Load available tools from MCP server."""
        try:
            message = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
            }

            async with self.session.post(
                self.server_url,
                json=message,
                headers={"Content-Type": "application/json"},
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    tools_data = result.get("result", {}).get("tools", [])

                    self.tools = [
                        MCPTool(
                            name=tool["name"],
                            description=tool.get("description", ""),
                            input_schema=tool.get("inputSchema", {}),
                            server_name=self.server_name,
                            server_version=tool.get("version", "0.1.0-beta"),
                        )
                        for tool in tools_data
                    ]

                    logger.info(f"Loaded {len(self.tools)} tools from MCP server")

        except Exception as e:
            logger.error(f"Error loading tools from MCP server: {e}")

    async def _load_resources(self):
        """Load available resources from MCP server."""
        try:
            message = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "resources/list",
            }

            async with self.session.post(
                self.server_url,
                json=message,
                headers={"Content-Type": "application/json"},
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    resources_data = result.get("result", {}).get("resources", [])

                    self.resources = [
                        MCPResource(
                            uri=resource["uri"],
                            name=resource.get("name", ""),
                            description=resource.get("description", ""),
                            mime_type=resource.get("mimeType", "text/plain"),
                        )
                        for resource in resources_data
                    ]

                    logger.info(
                        f"Loaded {len(self.resources)} resources from MCP server",
                    )

        except Exception as e:
            logger.error(f"Error loading resources from MCP server: {e}")

    async def call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Call a tool on the MCP server.

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            Dict[str, Any]: Tool result
        """
        try:
            message = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments,
                },
            }

            async with self.session.post(
                self.server_url,
                json=message,
                headers={"Content-Type": "application/json"},
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("result", {})
                logger.error(f"Failed to call tool {tool_name}: {response.status}")
                return {"error": f"HTTP {response.status}"}

        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return {"error": str(e)}

    async def read_resource(self, uri: str) -> dict[str, Any]:
        """
        Read a resource from the MCP server.

        Args:
            uri: Resource URI

        Returns:
            Dict[str, Any]: Resource content
        """
        try:
            message = {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "resources/read",
                "params": {
                    "uri": uri,
                },
            }

            async with self.session.post(
                self.server_url,
                json=message,
                headers={"Content-Type": "application/json"},
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("result", {})
                logger.error(f"Failed to read resource {uri}: {response.status}")
                return {"error": f"HTTP {response.status}"}

        except Exception as e:
            logger.error(f"Error reading resource {uri}: {e}")
            return {"error": str(e)}

    def get_tool_schema(self, tool_name: str) -> dict[str, Any] | None:
        """
        Get tool schema by name.

        Args:
            tool_name: Name of the tool

        Returns:
            Optional[Dict[str, Any]]: Tool schema
        """
        for tool in self.tools:
            if tool.name == tool_name:
                return tool.input_schema
        return None

    def list_tools(self) -> list[dict[str, Any]]:
        """
        Get list of available tools.

        Returns:
            List[Dict[str, Any]]: List of tool information
        """
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema,
                "server_name": tool.server_name,
                "server_version": tool.server_version,
            }
            for tool in self.tools
        ]

    def list_resources(self) -> list[dict[str, Any]]:
        """
        Get list of available resources.

        Returns:
            List[Dict[str, Any]]: List of resource information
        """
        return [
            {
                "uri": resource.uri,
                "name": resource.name,
                "description": resource.description,
                "mime_type": resource.mime_type,
            }
            for resource in self.resources
        ]


class MCPToolWrapper(BaseTool):
    """Wrapper for MCP tools to integrate with the platform."""

    def __init__(self, mcp_client: MCPClient, tool_name: str):
        super().__init__()

        self.mcp_client = mcp_client
        self.tool_name = tool_name
        self.tool_info = None

        # Get tool information
        for tool in mcp_client.tools:
            if tool.name == tool_name:
                self.tool_info = tool
                break

        if self.tool_info:
            self.name = f"mcp_{tool_name}"
            self.description = self.tool_info.description
            self.category = "mcp"

            # Convert MCP schema to tool parameters
            self.parameters = self._convert_schema_to_parameters(
                self.tool_info.input_schema,
            )

    def _convert_schema_to_parameters(
        self,
        schema: dict[str, Any],
    ) -> list[ToolParameter]:
        """
        Convert MCP JSON schema to tool parameters.

        Args:
            schema: MCP input schema

        Returns:
            List[ToolParameter]: List of tool parameters
        """
        parameters = []

        if "properties" in schema:
            for prop_name, prop_schema in schema["properties"].items():
                param = ToolParameter(
                    name=prop_name,
                    type=prop_schema.get("type", "string"),
                    description=prop_schema.get("description", ""),
                    required=prop_name in schema.get("required", []),
                    default=prop_schema.get("default"),
                )
                parameters.append(param)

        return parameters

    async def execute(self, **kwargs) -> ToolResult:
        """
        Execute MCP tool.

        Args:
            **kwargs: Tool arguments

        Returns:
            ToolResult: Execution result
        """
        try:
            if not self.mcp_client.is_connected:
                return ToolResult(
                    success=False,
                    error="MCP client not connected",
                )

            # Call tool on MCP server
            result = await self.mcp_client.call_tool(self.tool_name, kwargs)

            if "error" in result:
                return ToolResult(
                    success=False,
                    error=result["error"],
                )

            return ToolResult(
                success=True,
                data=result.get("content", result),
                metadata={
                    "tool_name": self.tool_name,
                    "server_name": self.mcp_client.server_name,
                    "mcp_result": result,
                },
            )

        except Exception as e:
            logger.error(f"Error executing MCP tool {self.tool_name}: {e}")
            return ToolResult(
                success=False,
                error=str(e),
            )


class MCPServerManager:
    """Manager for multiple MCP server connections."""

    def __init__(self):
        self.servers: dict[str, MCPClient] = {}
        self.tools: dict[str, MCPToolWrapper] = {}

    async def add_server(
        self,
        server_id: str,
        server_url: str,
        server_name: str = None,
    ) -> bool:
        """
        Add and connect to MCP server.

        Args:
            server_id: Unique server identifier
            server_url: Server URL
            server_name: Server name (optional)

        Returns:
            bool: True if connection successful
        """
        try:
            client = MCPClient(server_url, server_name or server_id)

            if await client.connect():
                self.servers[server_id] = client

                # Create tool wrappers for all available tools
                for tool_info in client.list_tools():
                    tool_name = tool_info["name"]
                    tool_id = f"{server_id}_{tool_name}"

                    tool_wrapper = MCPToolWrapper(client, tool_name)
                    self.tools[tool_id] = tool_wrapper

                logger.info(
                    f"Added MCP server {server_id} with {len(client.tools)} tools",
                )
                return True
            return False

        except Exception as e:
            logger.error(f"Error adding MCP server {server_id}: {e}")
            return False

    async def remove_server(self, server_id: str) -> bool:
        """
        Remove MCP server connection.

        Args:
            server_id: Server identifier

        Returns:
            bool: True if removed successfully
        """
        if server_id in self.servers:
            client = self.servers[server_id]
            await client.disconnect()
            del self.servers[server_id]

            # Remove associated tools
            tools_to_remove = [
                tool_id
                for tool_id in list(self.tools)
                if tool_id.startswith(f"{server_id}_")
            ]
            for tool_id in tools_to_remove:
                del self.tools[tool_id]

            logger.info(f"Removed MCP server {server_id}")
            return True

        return False

    def get_all_tools(self) -> list[dict[str, Any]]:
        """
        Get all available MCP tools.

        Returns:
            List[Dict[str, Any]]: List of tool information
        """
        tools_info = []

        for tool_id, tool in self.tools.items():
            tools_info.append(
                {
                    "id": tool_id,
                    "name": tool.name,
                    "description": tool.description,
                    "category": tool.category,
                    "server_name": tool.mcp_client.server_name,
                    "parameters": [param.dict() for param in tool.parameters],
                },
            )

        return tools_info

    def get_tool(self, tool_id: str) -> MCPToolWrapper | None:
        """
        Get tool by ID.

        Args:
            tool_id: Tool identifier

        Returns:
            Optional[MCPToolWrapper]: Tool wrapper if found
        """
        return self.tools.get(tool_id)

    async def execute_tool(self, tool_id: str, **kwargs) -> ToolResult:
        """
        Execute MCP tool by ID.

        Args:
            tool_id: Tool identifier
            **kwargs: Tool arguments

        Returns:
            ToolResult: Execution result
        """
        tool = self.get_tool(tool_id)
        if tool:
            return await tool.execute(**kwargs)
        return ToolResult(
            success=False,
            error=f"Tool {tool_id} not found",
        )

    async def disconnect_all(self):
        """Disconnect from all MCP servers."""
        for server_id in list(self.servers.keys()):
            await self.remove_server(server_id)


# Global MCP server manager instance
mcp_manager = MCPServerManager()
