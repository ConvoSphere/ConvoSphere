"""
Advanced tools page for the AI Assistant Platform.

This module provides comprehensive tool management with MCP integration,
tool execution, and advanced configuration options.
"""

from nicegui import ui
from typing import Optional, List, Dict, Any
from datetime import datetime
import asyncio

from services.tool_service import tool_service, Tool, ToolType, ToolStatus, ToolExecutionResult
from services.message_service import message_service
from components.common.loading_spinner import create_loading_spinner
from components.common.error_message import create_error_message
from utils.helpers import generate_id, format_timestamp, format_relative_time
from utils.validators import validate_tool_data


class AdvancedToolsPage:
    """Advanced tools management page component."""
    
    def __init__(self):
        """Initialize the advanced tools page."""
        self.tools: List[Tool] = []
        self.is_loading = False
        self.error_message = None
        self.selected_category = "all"
        self.selected_type = "all"
        self.search_query = ""
        
        # UI components
        self.container = None
        self.tools_container = None
        self.stats_container = None
        self.create_tool_dialog = None
        self.execute_tool_dialog = None
        
        # Create UI components
        self.create_tools_page()
        
        # Lade Tools nach dem Rendern asynchron
        ui.timer(0.1, self.load_tools, once=True)
    
    def create_tools_page(self):
        """Create the advanced tools page UI."""
        self.container = ui.element("div").classes("p-6")
        
        with self.container:
            # Header
            self.create_header()
            
            # Statistics
            self.create_statistics()
            
            # Filters and search
            self.create_filters()
            
            # Tools list
            self.create_tools_list()
            
            # Dialogs
            self.create_tool_dialog = self.create_tool_dialog_ui()
            self.execute_tool_dialog = self.create_execute_tool_dialog_ui()
    
    def create_header(self):
        """Create the page header."""
        with ui.element("div").classes("mb-6"):
            with ui.row().classes("items-center justify-between"):
                with ui.column():
                    ui.label("Tools & MCP Integration").classes("text-2xl font-bold")
                    ui.label("Verwalte und konfiguriere Tools für deine Assistenten").classes("text-gray-600")
                
                with ui.row().classes("space-x-2"):
                    ui.button(
                        "MCP Server hinzufügen",
                        icon="add_circle",
                        on_click=self.show_mcp_server_dialog
                    ).classes("bg-green-600 text-white")
                    
                    ui.button(
                        "Neues Tool erstellen",
                        icon="add",
                        on_click=self.show_create_tool_dialog
                    ).classes("bg-blue-600 text-white")
    
    def create_statistics(self):
        """Create tools statistics display."""
        self.stats_container = ui.element("div").classes("mb-6")
        
        with self.stats_container:
            with ui.row().classes("grid grid-cols-1 md:grid-cols-4 gap-4"):
                # Total tools
                with ui.element("div").classes("bg-white border rounded-lg p-4"):
                    ui.label("Gesamt").classes("text-sm text-gray-600")
                    ui.label("0").classes("text-2xl font-bold text-blue-600")
                
                # Active tools
                with ui.element("div").classes("bg-white border rounded-lg p-4"):
                    ui.label("Aktiv").classes("text-sm text-gray-600")
                    ui.label("0").classes("text-2xl font-bold text-green-600")
                
                # MCP tools
                with ui.element("div").classes("bg-white border rounded-lg p-4"):
                    ui.label("MCP Tools").classes("text-sm text-gray-600")
                    ui.label("0").classes("text-2xl font-bold text-purple-600")
                
                # Recent executions
                with ui.element("div").classes("bg-white border rounded-lg p-4"):
                    ui.label("Ausführungen").classes("text-sm text-gray-600")
                    ui.label("0").classes("text-2xl font-bold text-orange-600")
    
    def create_filters(self):
        """Create filters and search."""
        with ui.element("div").classes("mb-6 bg-white border rounded-lg p-4"):
            with ui.row().classes("items-center space-x-4"):
                # Search
                self.search_input = ui.input(
                    placeholder="Tools durchsuchen...",
                    on_change=self.handle_search
                ).classes("flex-1")
                
                # Category filter
                self.category_select = ui.select(
                    options=["all"] + tool_service.get_tool_categories(),
                    value="all",
                    label="Kategorie",
                    on_change=self.handle_category_filter
                ).classes("w-48")
                
                # Type filter
                self.type_select = ui.select(
                    options=["all"] + [t.value for t in ToolType],
                    value="all",
                    label="Typ",
                    on_change=self.handle_type_filter
                ).classes("w-48")
                
                # Refresh button
                ui.button(
                    icon="refresh",
                    on_click=self.load_tools
                ).classes("w-10 h-10 bg-gray-100 text-gray-600")
    
    def create_tools_list(self):
        """Create the tools list display."""
        self.tools_container = ui.element("div").classes("grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6")
    
    def create_tool_dialog_ui(self):
        """Create the advanced tool creation dialog."""
        with ui.dialog() as dialog, ui.card().classes("w-full max-w-2xl"):
            ui.label("Neues Tool erstellen").classes("text-lg font-medium mb-4")
            
            # Tool form
            with ui.column().classes("space-y-4"):
                # Basic info
                with ui.row().classes("space-x-4"):
                    name_input = ui.input("Name *").classes("flex-1")
                    category_input = ui.input("Kategorie").classes("flex-1")
                
                description_input = ui.textarea("Beschreibung *").classes("w-full")
                
                # Type and status
                with ui.row().classes("space-x-4"):
                    type_select = ui.select(
                        options=[t.value for t in ToolType],
                        value=ToolType.FUNCTION.value,
                        label="Typ *"
                    ).classes("flex-1")
                    
                    status_select = ui.select(
                        options=[s.value for s in ToolStatus],
                        value=ToolStatus.ACTIVE.value,
                        label="Status"
                    ).classes("flex-1")
                
                # Version and author
                with ui.row().classes("space-x-4"):
                    version_input = ui.input("Version").classes("flex-1")
                    author_input = ui.input("Autor").classes("flex-1")
                
                # Tags
                tags_input = ui.input("Tags (kommagetrennt)").classes("w-full")
                
                # Parameters section
                with ui.expansion("Parameter", icon="settings"):
                    self.parameters_container = ui.element("div").classes("space-y-2")
                    
                    ui.button(
                        "Parameter hinzufügen",
                        icon="add",
                        on_click=self.add_parameter_field
                    ).classes("bg-gray-100 text-gray-700")
                
                # Buttons
                with ui.row().classes("justify-end space-x-2"):
                    ui.button(
                        "Abbrechen",
                        on_click=dialog.close
                    ).classes("bg-gray-500 text-white")
                    
                    ui.button(
                        "Erstellen",
                        on_click=lambda: self.create_tool(
                            name_input.value,
                            description_input.value,
                            category_input.value,
                            type_select.value,
                            status_select.value,
                            version_input.value,
                            author_input.value,
                            tags_input.value,
                            dialog
                        )
                    ).classes("bg-blue-600 text-white")
        
        return dialog
    
    def create_execute_tool_dialog_ui(self):
        """Create tool execution dialog."""
        with ui.dialog() as dialog, ui.card().classes("w-full max-w-2xl"):
            ui.label("Tool ausführen").classes("text-lg font-medium mb-4")
            
            with ui.column().classes("space-y-4"):
                # Tool info
                self.tool_info = ui.element("div").classes("bg-gray-50 p-4 rounded")
                
                # Input parameters
                self.input_parameters = ui.element("div").classes("space-y-4")
                
                # Execute button
                ui.button(
                    "Ausführen",
                    icon="play_arrow",
                    on_click=self.execute_tool
                ).classes("bg-green-600 text-white")
                
                # Results
                self.execution_results = ui.element("div").classes("hidden")
        
        return dialog
    
    def add_parameter_field(self):
        """Add a parameter input field."""
        with self.parameters_container:
            with ui.row().classes("items-center space-x-2"):
                ui.input("Name").classes("w-32")
                ui.select(
                    options=["string", "number", "boolean", "array", "object"],
                    label="Typ"
                ).classes("w-32")
                ui.input("Beschreibung").classes("flex-1")
                ui.switch("Erforderlich").classes("w-20")
                ui.button(
                    icon="remove",
                    on_click=lambda row=ui.row(): row.delete()
                ).classes("w-8 h-8 bg-red-500 text-white")
    
    async def load_tools(self):
        """Load tools from the API."""
        self.is_loading = True
        
        try:
            self.tools = await tool_service.get_tools(force_refresh=True)
            self.display_tools()
            self.update_statistics()
            
        except Exception as e:
            self.error_message = f"Fehler beim Laden der Tools: {str(e)}"
            self.display_error()
        finally:
            self.is_loading = False
    
    def display_tools(self):
        """Display tools in the grid."""
        self.tools_container.clear()
        
        # Apply filters
        filtered_tools = self.filter_tools()
        
        if not filtered_tools:
            with self.tools_container:
                ui.label("Keine Tools gefunden").classes("col-span-full text-center text-gray-500 py-8")
            return
        
        with self.tools_container:
            for tool in filtered_tools:
                self.create_tool_card(tool)
    
    def filter_tools(self) -> List[Tool]:
        """Filter tools based on current filters."""
        filtered = self.tools
        
        # Category filter
        if self.selected_category != "all":
            filtered = [t for t in filtered if t.category == self.selected_category]
        
        # Type filter
        if self.selected_type != "all":
            filtered = [t for t in filtered if t.tool_type.value == self.selected_type]
        
        # Search filter
        if self.search_query:
            query_lower = self.search_query.lower()
            filtered = [
                t for t in filtered
                if query_lower in t.name.lower() or query_lower in t.description.lower()
            ]
        
        return filtered
    
    def update_statistics(self):
        """Update statistics display."""
        stats = tool_service.get_tool_stats()
        
        self.stats_container.clear()
        with self.stats_container:
            with ui.row().classes("grid grid-cols-1 md:grid-cols-4 gap-4"):
                # Total tools
                with ui.element("div").classes("bg-white border rounded-lg p-4"):
                    ui.label("Gesamt").classes("text-sm text-gray-600")
                    ui.label(str(stats["total_tools"])).classes("text-2xl font-bold text-blue-600")
                
                # Active tools
                with ui.element("div").classes("bg-white border rounded-lg p-4"):
                    ui.label("Aktiv").classes("text-sm text-gray-600")
                    ui.label(str(stats["active_tools"])).classes("text-2xl font-bold text-green-600")
                
                # MCP tools
                with ui.element("div").classes("bg-white border rounded-lg p-4"):
                    ui.label("MCP Tools").classes("text-sm text-gray-600")
                    ui.label(str(stats["type_counts"].get("mcp", 0))).classes("text-2xl font-bold text-purple-600")
                
                # Recent executions
                with ui.element("div").classes("bg-white border rounded-lg p-4"):
                    ui.label("Ausführungen").classes("text-sm text-gray-600")
                    ui.label(str(stats["recent_executions"])).classes("text-2xl font-bold text-orange-600")
    
    def create_tool_card(self, tool: Tool):
        """Create an advanced tool card."""
        with ui.element("div").classes("bg-white border rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow"):
            # Header
            with ui.row().classes("items-center justify-between mb-3"):
                with ui.column():
                    ui.label(tool.name).classes("font-semibold text-lg")
                    ui.label(tool.description).classes("text-sm text-gray-600")
                
                # Status badge
                status_color = {
                    ToolStatus.ACTIVE: "bg-green-100 text-green-800",
                    ToolStatus.INACTIVE: "bg-gray-100 text-gray-800",
                    ToolStatus.ERROR: "bg-red-100 text-red-800",
                    ToolStatus.LOADING: "bg-yellow-100 text-yellow-800"
                }.get(tool.status, "bg-gray-100 text-gray-800")
                
                ui.label(tool.status.value.title()).classes(f"px-2 py-1 rounded text-xs {status_color}")
            
            # Metadata
            with ui.row().classes("items-center justify-between text-xs text-gray-500 mb-3"):
                ui.label(f"Typ: {tool.tool_type.value.title()}")
                ui.label(f"Kategorie: {tool.category}")
            
            # Version and author
            if tool.version or tool.author:
                with ui.row().classes("items-center justify-between text-xs text-gray-500 mb-3"):
                    if tool.version:
                        ui.label(f"v{tool.version}")
                    if tool.author:
                        ui.label(f"von {tool.author}")
            
            # Tags
            if tool.tags:
                with ui.row().classes("flex-wrap gap-1 mb-3"):
                    for tag in tool.tags[:3]:  # Show first 3 tags
                        ui.label(tag).classes("px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs")
                    if len(tool.tags) > 3:
                        ui.label(f"+{len(tool.tags) - 3}").classes("px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs")
            
            # Parameters info
            if tool.parameters:
                with ui.row().classes("items-center text-xs text-gray-500 mb-3"):
                    ui.icon("settings").classes("w-3 h-3 mr-1")
                    ui.label(f"{len(tool.parameters)} Parameter")
            
            # Actions
            with ui.row().classes("space-x-2"):
                ui.button(
                    "Ausführen",
                    icon="play_arrow",
                    on_click=lambda t=tool: self.show_execute_tool_dialog(t)
                ).classes("bg-green-500 text-white text-xs")
                
                ui.button(
                    "Bearbeiten",
                    icon="edit",
                    on_click=lambda t=tool: self.edit_tool(t)
                ).classes("bg-blue-500 text-white text-xs")
                
                ui.button(
                    "Details",
                    icon="info",
                    on_click=lambda t=tool: self.show_tool_details(t)
                ).classes("bg-gray-500 text-white text-xs")
                
                ui.button(
                    "Löschen",
                    icon="delete",
                    on_click=lambda t=tool: self.delete_tool(t)
                ).classes("bg-red-500 text-white text-xs")
    
    def display_error(self):
        """Display error message."""
        self.tools_container.clear()
        with self.tools_container:
            create_error_message(self.error_message)
    
    def handle_search(self, event):
        """Handle search input change."""
        self.search_query = event.value
        self.display_tools()
    
    def handle_category_filter(self, event):
        """Handle category filter change."""
        self.selected_category = event.value
        self.display_tools()
    
    def handle_type_filter(self, event):
        """Handle type filter change."""
        self.selected_type = event.value
        self.display_tools()
    
    def show_create_tool_dialog(self):
        """Show the create tool dialog."""
        self.create_tool_dialog.open()
    
    def show_mcp_server_dialog(self):
        """Show MCP server configuration dialog."""
        with ui.dialog() as dialog, ui.card().classes("w-full max-w-lg"):
            ui.label("MCP Server hinzufügen").classes("text-lg font-medium mb-4")
            
            with ui.column().classes("space-y-4"):
                ui.input("Server Name").classes("w-full")
                ui.input("Server URL").classes("w-full")
                ui.textarea("Beschreibung").classes("w-full")
                
                with ui.row().classes("justify-end space-x-2"):
                    ui.button("Abbrechen", on_click=dialog.close).classes("bg-gray-500 text-white")
                    ui.button("Hinzufügen", on_click=dialog.close).classes("bg-green-600 text-white")
    
    def show_execute_tool_dialog(self, tool: Tool):
        """Show tool execution dialog."""
        self.current_tool = tool
        
        # Update tool info
        self.tool_info.clear()
        with self.tool_info:
            ui.label(f"Tool: {tool.name}").classes("font-medium")
            ui.label(tool.description).classes("text-sm text-gray-600")
            ui.label(f"Typ: {tool.tool_type.value.title()}").classes("text-xs text-gray-500")
        
        # Create parameter inputs
        self.input_parameters.clear()
        self.parameter_inputs = {}
        
        with self.input_parameters:
            for param in tool.parameters:
                if param.type == "string":
                    input_field = ui.input(f"{param.name} {'*' if param.required else ''}")
                elif param.type == "number":
                    input_field = ui.number(f"{param.name} {'*' if param.required else ''}")
                elif param.type == "boolean":
                    input_field = ui.switch(f"{param.name} {'*' if param.required else ''}")
                else:
                    input_field = ui.textarea(f"{param.name} {'*' if param.required else ''}")
                
                self.parameter_inputs[param.name] = input_field
                
                if param.description:
                    ui.label(param.description).classes("text-xs text-gray-500 mb-2")
        
        self.execute_tool_dialog.open()
    
    async def execute_tool(self):
        """Execute the selected tool."""
        if not hasattr(self, 'current_tool'):
            return
        
        # Collect input parameters
        input_data = {}
        for param_name, input_field in self.parameter_inputs.items():
            input_data[param_name] = input_field.value
        
        try:
            # Execute tool
            result = await tool_service.execute_tool(
                self.current_tool.id,
                input_data
            )
            
            if result:
                # Show results
                self.execution_results.classes("block")
                self.execution_results.clear()
                
                with self.execution_results:
                    ui.label("Ausführungsergebnis").classes("font-medium mb-2")
                    
                    if result.status == "success":
                        ui.label("Status: Erfolgreich").classes("text-green-600 mb-2")
                        ui.label(f"Ausführungszeit: {result.execution_time:.2f}s").classes("text-sm text-gray-600 mb-2")
                        
                        # Show output
                        with ui.expansion("Ausgabe anzeigen"):
                            ui.json(result.output_data)
                    else:
                        ui.label(f"Status: Fehler - {result.error_message}").classes("text-red-600")
                
                ui.notify("Tool erfolgreich ausgeführt", type="positive")
            else:
                ui.notify("Fehler bei der Tool-Ausführung", type="error")
                
        except Exception as e:
            ui.notify(f"Fehler bei der Tool-Ausführung: {str(e)}", type="error")
    
    async def create_tool(
        self,
        name: str,
        description: str,
        category: str,
        tool_type: str,
        status: str,
        version: str,
        author: str,
        tags: str,
        dialog
    ):
        """Create a new tool."""
        try:
            # Validate input
            if not name or not description:
                ui.notify("Name und Beschreibung sind erforderlich", type="error")
                return
            
            # Parse tags
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []
            
            # Create tool data
            tool_data = {
                "name": name,
                "description": description,
                "category": category or "general",
                "type": tool_type,
                "status": status,
                "version": version or "1.0.0",
                "author": author,
                "tags": tag_list,
                "parameters": []  # Would be populated from parameter fields
            }
            
            # Validate tool data
            validation = validate_tool_data(tool_data)
            if not validation["valid"]:
                ui.notify(f"Tool-Validierung fehlgeschlagen: {validation['errors']}", type="error")
                return
            
            # Create tool
            tool = await tool_service.create_tool(tool_data)
            
            if tool:
                ui.notify("Tool erfolgreich erstellt", type="positive")
                dialog.close()
                await self.load_tools()
            else:
                ui.notify("Fehler beim Erstellen des Tools", type="error")
                
        except Exception as e:
            ui.notify(f"Fehler beim Erstellen des Tools: {str(e)}", type="error")
    
    async def edit_tool(self, tool: Tool):
        """Edit a tool."""
        ui.notify("Tool bearbeiten", type="info")
    
    def show_tool_details(self, tool: Tool):
        """Show detailed tool information."""
        with ui.dialog() as dialog, ui.card().classes("w-full max-w-2xl"):
            ui.label(f"Tool Details: {tool.name}").classes("text-lg font-medium mb-4")
            
            with ui.column().classes("space-y-4"):
                # Basic info
                with ui.row().classes("space-x-4"):
                    ui.label("Name:").classes("font-medium")
                    ui.label(tool.name)
                
                with ui.row().classes("space-x-4"):
                    ui.label("Beschreibung:").classes("font-medium")
                    ui.label(tool.description)
                
                with ui.row().classes("space-x-4"):
                    ui.label("Typ:").classes("font-medium")
                    ui.label(tool.tool_type.value.title())
                
                with ui.row().classes("space-x-4"):
                    ui.label("Status:").classes("font-medium")
                    ui.label(tool.status.value.title())
                
                # Parameters
                if tool.parameters:
                    with ui.expansion("Parameter", icon="settings"):
                        for param in tool.parameters:
                            with ui.row().classes("items-center space-x-4 p-2 bg-gray-50 rounded"):
                                ui.label(param.name).classes("font-medium w-24")
                                ui.label(param.type).classes("text-sm w-16")
                                ui.label(param.description).classes("flex-1 text-sm")
                                ui.label("✓" if param.required else "○").classes("w-8 text-center")
                
                # Metadata
                if tool.version or tool.author or tool.tags:
                    with ui.expansion("Metadaten", icon="info"):
                        if tool.version:
                            with ui.row().classes("space-x-4"):
                                ui.label("Version:").classes("font-medium")
                                ui.label(tool.version)
                        
                        if tool.author:
                            with ui.row().classes("space-x-4"):
                                ui.label("Autor:").classes("font-medium")
                                ui.label(tool.author)
                        
                        if tool.tags:
                            with ui.row().classes("space-x-4"):
                                ui.label("Tags:").classes("font-medium")
                                with ui.row().classes("flex-wrap gap-1"):
                                    for tag in tool.tags:
                                        ui.label(tag).classes("px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs")
                
                ui.button("Schließen", on_click=dialog.close).classes("bg-blue-600 text-white")
    
    async def delete_tool(self, tool: Tool):
        """Delete a tool."""
        try:
            success = await tool_service.delete_tool(tool.id)
            
            if success:
                ui.notify("Tool erfolgreich gelöscht", type="positive")
                await self.load_tools()
            else:
                ui.notify("Fehler beim Löschen des Tools", type="error")
                
        except Exception as e:
            ui.notify(f"Fehler beim Löschen des Tools: {str(e)}", type="error")


# Global advanced tools page instance
advanced_tools_page = AdvancedToolsPage() 