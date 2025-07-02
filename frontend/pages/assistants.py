"""
Assistants page for the AI Assistant Platform.

This module provides the assistants management interface with tool assignment capabilities.
"""

from typing import List, Dict, Any, Optional
from nicegui import ui
import asyncio

from ..services.api import api_client


class AssistantsPage:
    """Assistants management page."""
    
    def __init__(self):
        """Initialize the assistants page."""
        self.assistants: List[Dict[str, Any]] = []
        self.all_tools: List[Dict[str, Any]] = []
        self.selected_assistant: Optional[Dict[str, Any]] = None
        
        # UI elements
        self.tool_assignment_dialog = None
        self.assistant_edit_dialog = None
        
        self.setup_assistants_page()
        self.create_dialogs()
        self.load_data()
    
    def setup_assistants_page(self):
        """Setup the assistants page layout."""
        # Page header
        with ui.element("div").classes("card"):
            ui.html("<h1 style='margin: 0 0 8px 0; font-size: 28px; font-weight: 700; color: #1f2937;'>Assistenten verwalten</h1>")
            ui.html("<p style='margin: 0; color: #6b7280; font-size: 16px;'>Erstelle und konfiguriere deine AI-Assistenten</p>")
        
        # Action buttons
        with ui.row().classes("w-full gap-4 mb-6"):
            ui.button("Neuen Assistenten erstellen", on_click=self.create_assistant).classes("btn-primary")
            ui.button("Importieren", on_click=self.import_assistant).classes("bg-white border border-gray-300 text-gray-700 hover:bg-gray-50")
            ui.button("Exportieren", on_click=self.export_assistants).classes("bg-white border border-gray-300 text-gray-700 hover:bg-gray-50")
        
        # Assistants container
        self.assistants_container = ui.column().classes("w-full gap-6")
    
    def create_dialogs(self):
        """Create dialogs for assistant management."""
        self.create_tool_assignment_dialog()
        self.create_assistant_edit_dialog()
    
    def create_tool_assignment_dialog(self):
        """Create dialog for assigning tools to assistants."""
        with ui.dialog() as self.tool_assignment_dialog, ui.card().classes("w-2xl"):
            ui.label("Tools zuweisen").classes("text-lg font-semibold mb-4")
            
            # Assistant info
            self.assistant_info_label = ui.label("").classes("text-sm text-gray-600 mb-4")
            
            # Available tools section
            ui.label("Verfügbare Tools").classes("font-medium mb-2")
            self.available_tools_list = ui.column().classes("w-full max-h-64 overflow-y-auto mb-4")
            
            # Assigned tools section
            ui.label("Zugewiesene Tools").classes("font-medium mb-2")
            self.assigned_tools_list = ui.column().classes("w-full max-h-64 overflow-y-auto mb-4")
            
            with ui.row().classes("w-full justify-end gap-2"):
                ui.button("Abbrechen", on_click=self.tool_assignment_dialog.close).classes("bg-gray-500")
                ui.button("Speichern", on_click=self.save_tool_assignment).classes("bg-blue-500")
    
    def create_assistant_edit_dialog(self):
        """Create dialog for editing assistant details."""
        with ui.dialog() as self.assistant_edit_dialog, ui.card().classes("w-xl"):
            ui.label("Assistent bearbeiten").classes("text-lg font-semibold mb-4")
            
            # Form fields
            self.edit_name_input = ui.input("Name").classes("w-full mb-4")
            self.edit_description_input = ui.textarea("Beschreibung").classes("w-full mb-4")
            self.edit_personality_input = ui.textarea("Persönlichkeit").classes("w-full mb-4")
            self.edit_system_prompt_input = ui.textarea("System Prompt").classes("w-full mb-4")
            
            # Model selection
            self.edit_model_select = ui.select(
                "AI Model",
                options=["gpt-4", "gpt-3.5-turbo", "claude-3", "gemini-pro"],
                value="gpt-4"
            ).classes("w-full mb-4")
            
            # Temperature
            self.edit_temperature_slider = ui.slider(
                min=0, max=2, step=0.1, value=0.7
            ).classes("w-full mb-4")
            ui.label("Kreativität (Temperature)").classes("text-sm text-gray-600 mb-4")
            
            with ui.row().classes("w-full justify-end gap-2"):
                ui.button("Abbrechen", on_click=self.assistant_edit_dialog.close).classes("bg-gray-500")
                ui.button("Speichern", on_click=self.save_assistant_edit).classes("bg-blue-500")
    
    async def load_data(self):
        """Load assistants and tools data."""
        try:
            # Load assistants
            assistants_response = await api_client.get_assistants()
            if assistants_response.success:
                self.assistants = assistants_response.data
                self.update_assistants_display()
            
            # Load all tools (regular + MCP)
            await self.load_all_tools()
            
        except Exception as e:
            ui.notify(f"Error loading data: {e}", type="error")
    
    async def load_all_tools(self):
        """Load all available tools including MCP tools."""
        try:
            all_tools = []
            
            # Regular tools
            tools_response = await api_client.get_tools()
            if tools_response.success:
                all_tools.extend(tools_response.data)
            
            # MCP tools
            mcp_tools_response = await api_client.get_mcp_tools()
            if mcp_tools_response.success:
                all_tools.extend(mcp_tools_response.data)
            
            self.all_tools = all_tools
            
        except Exception as e:
            ui.notify(f"Error loading tools: {e}", type="error")
    
    def update_assistants_display(self):
        """Update the assistants display."""
        if not self.assistants_container:
            return
        
        # Clear existing content
        self.assistants_container.clear()
        
        for assistant in self.assistants:
            with self.assistants_container:
                with ui.element("div").classes("card flex-1"):
                    # Header
                    ui.html(f"<div style='display: flex; justify-content: space-between; align-items: start; margin-bottom: 16px;'>")
                    ui.html(f"<div>")
                    ui.html(f"<h3 style='margin: 0; font-size: 20px; font-weight: 600; color: #1f2937;'>{assistant['name']}</h3>")
                    ui.html(f"<p style='margin: 4px 0 0 0; font-size: 14px; color: #6b7280;'>{assistant.get('description', '')}</p>")
                    ui.html(f"</div>")
                    
                    # Status badge
                    status = assistant.get('status', 'inactive')
                    status_color = "#10b981" if status == 'active' else "#6b7280"
                    ui.html(f"<span style='background: {status_color}; color: white; padding: 4px 8px; border-radius: 6px; font-size: 12px; font-weight: 500;'>{status}</span>")
                    ui.html(f"</div>")
                    
                    # Personality
                    personality = assistant.get('personality', 'Nicht definiert')
                    ui.html(f"<p style='margin: 0 0 12px 0; font-size: 14px; color: #374151;'><strong>Persönlichkeit:</strong> {personality}</p>")
                    
                    # Tools
                    tools_config = assistant.get('tools_config', [])
                    ui.html(f"<p style='margin: 0 0 12px 0; font-size: 14px; color: #374151;'><strong>Tools ({len(tools_config)}):</strong></p>")
                    with ui.row().classes("gap-2 mb-4"):
                        for tool_config in tools_config[:3]:
                            tool_name = tool_config.get('name', tool_config.get('id', 'Unknown'))
                            ui.html(f"<span style='background: #f3f4f6; color: #374151; padding: 2px 8px; border-radius: 4px; font-size: 12px;'>{tool_name}</span>")
                        if len(tools_config) > 3:
                            ui.html(f"<span style='background: #f3f4f6; color: #374151; padding: 2px 8px; border-radius: 4px; font-size: 12px;'>+{len(tools_config) - 3}</span>")
                    
                    # Model and created date
                    model = assistant.get('model', 'Unknown')
                    ui.html(f"<p style='margin: 0 0 8px 0; font-size: 12px; color: #6b7280;'><strong>Model:</strong> {model}</p>")
                    
                    # Action buttons
                    with ui.row().classes("gap-2"):
                        ui.button("Bearbeiten", on_click=lambda a=assistant: self.edit_assistant(a)).classes("flex-1 bg-blue-600 text-white hover:bg-blue-700")
                        ui.button("Tools", on_click=lambda a=assistant: self.manage_tools(a)).classes("flex-1 bg-purple-600 text-white hover:bg-purple-700")
                        ui.button("Testen", on_click=lambda a=assistant: self.test_assistant(a)).classes("flex-1 bg-green-600 text-white hover:bg-green-700")
                        ui.button("Löschen", on_click=lambda a=assistant: self.delete_assistant(a)).classes("flex-1 bg-red-600 text-white hover:bg-red-700")
    
    def manage_tools(self, assistant: Dict[str, Any]):
        """Open tool assignment dialog for an assistant."""
        self.selected_assistant = assistant
        self.assistant_info_label.text = f"Assistent: {assistant['name']}"
        self.update_tool_lists()
        self.tool_assignment_dialog.open()
    
    def update_tool_lists(self):
        """Update available and assigned tools lists."""
        if not self.selected_assistant:
            return
        
        # Clear lists
        self.available_tools_list.clear()
        self.assigned_tools_list.clear()
        
        # Get assigned tool IDs
        assigned_tool_ids = {
            tool_config.get('id', tool_config.get('name'))
            for tool_config in self.selected_assistant.get('tools_config', [])
        }
        
        # Separate available and assigned tools
        available_tools = []
        assigned_tools = []
        
        for tool in self.all_tools:
            tool_id = tool.get('id', tool.get('name'))
            if tool_id in assigned_tool_ids:
                assigned_tools.append(tool)
            else:
                available_tools.append(tool)
        
        # Display available tools
        for tool in available_tools:
            with self.available_tools_list:
                with ui.card().classes("w-full p-3 mb-2 cursor-pointer hover:bg-green-50").on("click", lambda t=tool: self.assign_tool(t)):
                    with ui.row().classes("w-full justify-between items-start"):
                        with ui.column().classes("flex-1"):
                            ui.label(tool["name"]).classes("font-semibold")
                            ui.label(tool["description"]).classes("text-sm text-gray-600")
                            category = tool.get("category", "unknown")
                            ui.label(f"Category: {category}").classes("text-xs text-gray-500")
                        
                        ui.button("+", on_click=lambda t=tool: self.assign_tool(t)).classes("bg-green-500 text-white text-xs px-2")
        
        # Display assigned tools
        for tool in assigned_tools:
            with self.assigned_tools_list:
                with ui.card().classes("w-full p-3 mb-2 cursor-pointer hover:bg-red-50").on("click", lambda t=tool: self.unassign_tool(t)):
                    with ui.row().classes("w-full justify-between items-start"):
                        with ui.column().classes("flex-1"):
                            ui.label(tool["name"]).classes("font-semibold")
                            ui.label(tool["description"]).classes("text-sm text-gray-600")
                            category = tool.get("category", "unknown")
                            ui.label(f"Category: {category}").classes("text-xs text-gray-500")
                        
                        ui.button("×", on_click=lambda t=tool: self.unassign_tool(t)).classes("bg-red-500 text-white text-xs px-2")
    
    def assign_tool(self, tool: Dict[str, Any]):
        """Assign a tool to the selected assistant."""
        if not self.selected_assistant:
            return
        
        # Add tool to assistant's tools_config
        if 'tools_config' not in self.selected_assistant:
            self.selected_assistant['tools_config'] = []
        
        tool_config = {
            "id": tool.get('id', tool.get('name')),
            "name": tool.get('name'),
            "category": tool.get('category', 'unknown')
        }
        
        self.selected_assistant['tools_config'].append(tool_config)
        self.update_tool_lists()
    
    def unassign_tool(self, tool: Dict[str, Any]):
        """Unassign a tool from the selected assistant."""
        if not self.selected_assistant:
            return
        
        tool_id = tool.get('id', tool.get('name'))
        tools_config = self.selected_assistant.get('tools_config', [])
        
        # Remove tool from tools_config
        self.selected_assistant['tools_config'] = [
            tc for tc in tools_config 
            if tc.get('id', tc.get('name')) != tool_id
        ]
        
        self.update_tool_lists()
    
    async def save_tool_assignment(self):
        """Save tool assignment to backend."""
        if not self.selected_assistant:
            return
        
        try:
            response = await api_client.update_assistant(
                self.selected_assistant['id'],
                {"tools_config": self.selected_assistant['tools_config']}
            )
            
            if response.success:
                ui.notify("Tool-Zuordnung gespeichert", type="positive")
                self.tool_assignment_dialog.close()
                await self.load_data()  # Refresh data
            else:
                ui.notify(f"Fehler beim Speichern: {response.error}", type="error")
                
        except Exception as e:
            ui.notify(f"Error saving tool assignment: {e}", type="error")
    
    def edit_assistant(self, assistant: Dict[str, Any]):
        """Open edit dialog for an assistant."""
        self.selected_assistant = assistant
        
        # Populate form fields
        self.edit_name_input.value = assistant.get('name', '')
        self.edit_description_input.value = assistant.get('description', '')
        self.edit_personality_input.value = assistant.get('personality', '')
        self.edit_system_prompt_input.value = assistant.get('system_prompt', '')
        self.edit_model_select.value = assistant.get('model', 'gpt-4')
        self.edit_temperature_slider.value = float(assistant.get('temperature', 0.7))
        
        self.assistant_edit_dialog.open()
    
    async def save_assistant_edit(self):
        """Save assistant edits to backend."""
        if not self.selected_assistant:
            return
        
        try:
            update_data = {
                "name": self.edit_name_input.value,
                "description": self.edit_description_input.value,
                "personality": self.edit_personality_input.value,
                "system_prompt": self.edit_system_prompt_input.value,
                "model": self.edit_model_select.value,
                "temperature": str(self.edit_temperature_slider.value)
            }
            
            response = await api_client.update_assistant(
                self.selected_assistant['id'],
                update_data
            )
            
            if response.success:
                ui.notify("Assistent gespeichert", type="positive")
                self.assistant_edit_dialog.close()
                await self.load_data()  # Refresh data
            else:
                ui.notify(f"Fehler beim Speichern: {response.error}", type="error")
                
        except Exception as e:
            ui.notify(f"Error saving assistant: {e}", type="error")
    
    def create_assistant(self):
        """Handle create assistant action."""
        ui.notify("Assistenten-Erstellung wird geöffnet...", type="info")
    
    def import_assistant(self):
        """Handle import assistant action."""
        ui.notify("Assistenten-Import wird geöffnet...", type="info")
    
    def export_assistants(self):
        """Handle export assistants action."""
        ui.notify("Assistenten-Export wird gestartet...", type="info")
    
    def test_assistant(self, assistant):
        """Handle test assistant action."""
        ui.notify(f"Teste Assistent: {assistant['name']}", type="info")
    
    async def delete_assistant(self, assistant):
        """Handle delete assistant action."""
        try:
            response = await api_client.delete_assistant(assistant['id'])
            
            if response.success:
                ui.notify(f"Assistent {assistant['name']} gelöscht", type="positive")
                await self.load_data()  # Refresh data
            else:
                ui.notify(f"Fehler beim Löschen: {response.error}", type="error")
                
        except Exception as e:
            ui.notify(f"Error deleting assistant: {e}", type="error") 