"""
MCP Tools Management Page.

This page provides a user interface for managing MCP servers and tools.
"""

from dataclasses import dataclass
from typing import Any

from nicegui import ui
from services.api import api_client


@dataclass
class MCPServer:
    """MCP Server data model."""

    server_id: str
    server_name: str
    server_url: str
    is_connected: bool
    tool_count: int
    resource_count: int


@dataclass
class MCPTool:
    """MCP Tool data model."""

    id: str
    name: str
    description: str
    category: str
    server_name: str
    parameters: list[dict[str, Any]]


class MCPToolsPage:
    """MCP Tools management page."""

    def __init__(self):
        self.servers: list[MCPServer] = []
        self.tools: list[MCPTool] = []
        self.selected_server: MCPServer | None = None
        self.selected_tool: MCPTool | None = None

        # UI elements
        self.servers_grid = None
        self.tools_grid = None
        self.server_dialog = None
        self.tool_execute_dialog = None

        self.create_page()

    def create_page(self):
        """Create the MCP tools page."""
        with ui.column().classes("w-full h-full p-4 gap-4"):
            # Header
            with ui.row().classes("w-full justify-between items-center"):
                ui.label("MCP Tools Management").classes("text-2xl font-bold")

                with ui.row().classes("gap-2"):
                    ui.button(
                        "Add Server", on_click=self.show_add_server_dialog,
                    ).classes("bg-blue-500")
                    ui.button("Refresh", on_click=self.load_data).classes("bg-gray-500")

            # Main content
            with ui.row().classes("w-full h-full gap-4"):
                # Servers panel
                with ui.column().classes("w-1/3 bg-gray-50 p-4 rounded-lg"):
                    ui.label("MCP Servers").classes("text-lg font-semibold mb-4")

                    self.servers_grid = ui.grid(columns=1, rows=0).classes("w-full")

                    # Add server button
                    ui.button(
                        "+ Add New Server", on_click=self.show_add_server_dialog,
                    ).classes("w-full mt-4 bg-green-500")

                # Tools panel
                with ui.column().classes("w-2/3 bg-gray-50 p-4 rounded-lg"):
                    ui.label("Available Tools").classes("text-lg font-semibold mb-4")

                    self.tools_grid = ui.grid(columns=1, rows=0).classes("w-full")

            # Create dialogs
            self.create_add_server_dialog()
            self.create_tool_execute_dialog()

            # Load initial data - will be called when page is accessed
            # asyncio.create_task(self.load_data())

    def create_add_server_dialog(self):
        """Create the add server dialog."""
        with ui.dialog() as self.server_dialog, ui.card().classes("w-96"):
            ui.label("Add MCP Server").classes("text-lg font-semibold mb-4")

            server_id = ui.input("Server ID").classes("w-full mb-4")
            server_url = ui.input("Server URL").classes("w-full mb-4")
            server_name = ui.input("Server Name (Optional)").classes("w-full mb-4")

            with ui.row().classes("w-full justify-end gap-2"):
                ui.button("Cancel", on_click=self.server_dialog.close).classes(
                    "bg-gray-500",
                )
                ui.button(
                    "Add Server",
                    on_click=lambda: self.add_server(
                        server_id.value,
                        server_url.value,
                        server_name.value,
                    ),
                ).classes("bg-blue-500")

    def create_tool_execute_dialog(self):
        """Create the tool execution dialog."""
        with ui.dialog() as self.tool_execute_dialog, ui.card().classes("w-96"):
            ui.label("Execute MCP Tool").classes("text-lg font-semibold mb-4")

            self.tool_name_label = ui.label("").classes("text-sm text-gray-600 mb-4")
            self.tool_description_label = ui.label("").classes(
                "text-sm text-gray-600 mb-4",
            )

            self.arguments_container = ui.column().classes("w-full mb-4")

            with ui.row().classes("w-full justify-end gap-2"):
                ui.button("Cancel", on_click=self.tool_execute_dialog.close).classes(
                    "bg-gray-500",
                )
                ui.button("Execute", on_click=self.execute_tool).classes("bg-green-500")

    async def load_data(self):
        """Load MCP servers and tools data."""
        try:
            # Load servers
            servers_response = await api_client.get_mcp_servers()
            if servers_response.success:
                self.servers = [
                    MCPServer(**server_data) for server_data in servers_response.data
                ]
                self.update_servers_grid()

            # Load tools
            tools_response = await api_client.get_mcp_tools()
            if tools_response.success:
                self.tools = [MCPTool(**tool_data) for tool_data in tools_response.data]
                self.update_tools_grid()

        except Exception as e:
            ui.notify(f"Error loading MCP data: {e}", type="error")

    def update_servers_grid(self):
        """Update the servers grid."""
        if not self.servers_grid:
            return

        # Clear existing content
        self.servers_grid.clear()

        for server in self.servers:
            with self.servers_grid:
                with (
                    ui.card()
                    .classes("w-full p-4 cursor-pointer hover:bg-blue-50")
                    .on("click", lambda s=server: self.select_server(s))
                ):
                    with ui.row().classes("w-full justify-between items-start"):
                        with ui.column().classes("flex-1"):
                            ui.label(server.server_name).classes("font-semibold")
                            ui.label(server.server_url).classes("text-sm text-gray-600")

                            with ui.row().classes("gap-4 mt-2"):
                                status_color = (
                                    "text-green-600"
                                    if server.is_connected
                                    else "text-red-600"
                                )
                                status_text = (
                                    "Connected"
                                    if server.is_connected
                                    else "Disconnected"
                                )
                                ui.label(f"● {status_text}").classes(
                                    f"text-sm {status_color}",
                                )

                                ui.label(f"Tools: {server.tool_count}").classes(
                                    "text-sm text-gray-600",
                                )
                                ui.label(f"Resources: {server.resource_count}").classes(
                                    "text-sm text-gray-600",
                                )

                        with ui.column().classes("gap-1"):
                            ui.button(
                                "Remove",
                                on_click=lambda s=server: self.remove_server(
                                    s.server_id,
                                ),
                            ).classes("bg-red-500 text-white text-xs")

    def update_tools_grid(self):
        """Update the tools grid."""
        if not self.tools_grid:
            return

        # Clear existing content
        self.tools_grid.clear()

        for tool in self.tools:
            with self.tools_grid:
                with (
                    ui.card()
                    .classes("w-full p-4 cursor-pointer hover:bg-green-50")
                    .on("click", lambda t=tool: self.select_tool(t))
                ):
                    with ui.row().classes("w-full justify-between items-start"):
                        with ui.column().classes("flex-1"):
                            ui.label(tool.name).classes("font-semibold")
                            ui.label(tool.description).classes(
                                "text-sm text-gray-600 mt-1",
                            )

                            with ui.row().classes("gap-4 mt-2"):
                                ui.label(f"Server: {tool.server_name}").classes(
                                    "text-sm text-gray-600",
                                )
                                ui.label(f"Category: {tool.category}").classes(
                                    "text-sm text-gray-600",
                                )
                                ui.label(f"Parameters: {len(tool.parameters)}").classes(
                                    "text-sm text-gray-600",
                                )

                        with ui.column().classes("gap-1"):
                            ui.button(
                                "Execute",
                                on_click=lambda t=tool: self.show_execute_tool_dialog(
                                    t,
                                ),
                            ).classes("bg-blue-500 text-white text-xs")

    def select_server(self, server: MCPServer):
        """Select a server."""
        self.selected_server = server
        # Filter tools by server
        self.update_tools_grid()

    def select_tool(self, tool: MCPTool):
        """Select a tool."""
        self.selected_tool = tool

    def show_add_server_dialog(self):
        """Show the add server dialog."""
        self.server_dialog.open()

    async def add_server(self, server_id: str, server_url: str, server_name: str):
        """Add a new MCP server."""
        try:
            response = await api_client.add_mcp_server(
                {
                    "server_id": server_id,
                    "server_url": server_url,
                    "server_name": server_name or None,
                },
            )

            if response.success:
                ui.notify("MCP server added successfully", type="positive")
                self.server_dialog.close()
                await self.load_data()
            else:
                ui.notify(f"Failed to add server: {response.error}", type="error")

        except Exception as e:
            ui.notify(f"Error adding server: {e}", type="error")

    async def remove_server(self, server_id: str):
        """Remove an MCP server."""
        try:
            response = await api_client.remove_mcp_server(server_id)

            if response.success:
                ui.notify("MCP server removed successfully", type="positive")
                await self.load_data()
            else:
                ui.notify(f"Failed to remove server: {response.error}", type="error")

        except Exception as e:
            ui.notify(f"Error removing server: {e}", type="error")

    def show_execute_tool_dialog(self, tool: MCPTool):
        """Show the tool execution dialog."""
        self.selected_tool = tool

        # Update dialog content
        self.tool_name_label.text = f"Tool: {tool.name}"
        self.tool_description_label.text = tool.description

        # Clear and create argument inputs
        self.arguments_container.clear()

        for param in tool.parameters:
            param_name = param["name"]
            param_type = param["type"]
            param_description = param.get("description", "")
            param_required = param.get("required", False)

            label_text = f"{param_name}{'*' if param_required else ''}"
            if param_description:
                label_text += f" - {param_description}"

            if param_type == "string":
                ui.input(label_text).classes("w-full mb-2")
            elif param_type == "number":
                ui.number(label_text).classes("w-full mb-2")
            elif param_type == "boolean":
                ui.checkbox(label_text).classes("w-full mb-2")
            else:
                ui.input(label_text).classes("w-full mb-2")

        self.tool_execute_dialog.open()

    async def execute_tool(self):
        """Execute the selected tool."""
        if not self.selected_tool:
            return

        try:
            # Collect arguments from inputs
            arguments = {}
            for i, param in enumerate(self.selected_tool.parameters):
                input_element = self.arguments_container.children[i]
                if hasattr(input_element, "value"):
                    arguments[param["name"]] = input_element.value

            response = await api_client.execute_mcp_tool(
                self.selected_tool.id,
                arguments,
            )

            if response.success:
                ui.notify("Tool executed successfully", type="positive")
                self.tool_execute_dialog.close()

                # Show result in a dialog
                with ui.dialog() as result_dialog, ui.card().classes("w-96"):
                    ui.label("Tool Execution Result").classes(
                        "text-lg font-semibold mb-4",
                    )
                    ui.code(str(response.data)).classes("w-full text-xs")
                    ui.button("Close", on_click=result_dialog.close).classes("mt-4")
                result_dialog.open()
            else:
                ui.notify(f"Tool execution failed: {response.error}", type="error")

        except Exception as e:
            ui.notify(f"Error executing tool: {e}", type="error")


def create_page():
    """Create and return an MCP tools page instance."""
    return MCPToolsPage()
