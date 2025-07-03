"""
Assistants page for the AI Assistant Platform.

This module provides assistant management functionality including
CRUD operations, tool assignment, and assistant configuration.
"""

import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional

from nicegui import ui, app
from nicegui.events import ValueChangeEventArguments

from services.auth_service import auth_service
from services.assistant_service import assistant_service
from services.error_handler import handle_api_error, handle_network_error
from components.common.loading_spinner import create_loading_spinner
from components.common.error_message import create_error_message, ErrorSeverity
from utils.helpers import format_timestamp, format_relative_time
from utils.validators import validate_assistant_data
from utils.constants import API_BASE_URL


class AssistantsPage:
    """Assistants management page."""
    
    def __init__(self):
        """Initialize assistants page."""
        self.assistants = []
        self.is_loading = False
        self.search_query = ""
        self.filter_status = "all"
        
        # UI Components
        self.assistants_container = None
        self.loading_spinner = None
        self.error_component = None
        self.create_dialog = None
        self.edit_dialog = None
        
        # Form data
        self.current_assistant = None
        self.form_data = {
            "name": "",
            "description": "",
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 4096,
            "tools": []
        }
        
        self.create_assistants_page()
        self.load_assistants()
    
    def create_assistants_page(self):
        """Create the assistants page UI."""
        with ui.column().classes("w-full max-w-7xl mx-auto p-6 space-y-6"):
            # Header
            with ui.row().classes("items-center justify-between"):
                ui.label("Assistenten").classes("text-2xl font-bold text-gray-900")
                
                with ui.row().classes("space-x-2"):
                    ui.button(
                        "Aktualisieren",
                        icon="refresh",
                        on_click=self.load_assistants
                    ).classes("bg-blue-600 text-white")
                    
                    ui.button(
                        "Neuer Assistent",
                        icon="add",
                        on_click=self.show_create_dialog
                    ).classes("bg-green-600 text-white")
            
            # Search and Filter
            with ui.row().classes("items-center space-x-4"):
                # Search input
                ui.input(
                    placeholder="Assistenten suchen...",
                    on_change=self.on_search_change
                ).classes("flex-1 max-w-md")
                
                # Status filter
                ui.select(
                    options=[
                        ("all", "Alle"),
                        ("active", "Aktiv"),
                        ("inactive", "Inaktiv")
                    ],
                    value="all",
                    on_change=self.on_filter_change
                ).classes("w-32")
            
            # Loading and Error States
            self.loading_spinner = create_loading_spinner("Lade Assistenten...", size="lg")
            self.error_component = create_error_message("", dismissible=True)
            
            # Assistants Grid
            self.assistants_container = ui.element("div").classes("grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6")
            
            # Create dialogs
            self.create_dialogs()
    
    def create_dialogs(self):
        """Create assistant creation and editing dialogs."""
        # Create Assistant Dialog
        with ui.dialog() as self.create_dialog, ui.card().classes("w-96 p-6"):
            ui.label("Neuer Assistent").classes("text-lg font-semibold mb-4")
            
            with ui.column().classes("space-y-4"):
                # Name
                ui.input(
                    label="Name",
                    placeholder="Assistenten-Name",
                    on_change=lambda e: self.update_form_data("name", e.value)
                ).classes("w-full")
                
                # Description
                ui.textarea(
                    label="Beschreibung",
                    placeholder="Beschreibung des Assistenten",
                    rows=3,
                    on_change=lambda e: self.update_form_data("description", e.value)
                ).classes("w-full")
                
                # Model
                ui.select(
                    label="AI-Modell",
                    options=[
                        ("gpt-4", "GPT-4"),
                        ("gpt-3.5-turbo", "GPT-3.5 Turbo"),
                        ("claude-3", "Claude-3"),
                        ("gemini-pro", "Gemini Pro")
                    ],
                    value="gpt-4",
                    on_change=lambda e: self.update_form_data("model", e.value)
                ).classes("w-full")
                
                # Temperature
                with ui.row().classes("items-center space-x-2"):
                    ui.label("Kreativität (Temperature)").classes("text-sm")
                    ui.slider(
                        min=0, max=2, step=0.1, value=0.7,
                        on_change=lambda e: self.update_form_data("temperature", e.value)
                    ).classes("flex-1")
                    ui.label("0.7").classes("text-sm text-gray-500 w-8")
                
                # Max Tokens
                ui.number(
                    label="Max Tokens",
                    min=100, max=8000, value=4096,
                    on_change=lambda e: self.update_form_data("max_tokens", e.value)
                ).classes("w-full")
                
                # Buttons
                with ui.row().classes("justify-end space-x-2"):
                    ui.button(
                        "Abbrechen",
                        on_click=self.create_dialog.close
                    ).classes("bg-gray-500 text-white")
                    
                    ui.button(
                        "Erstellen",
                        on_click=self.create_assistant
                    ).classes("bg-green-600 text-white")
        
        # Edit Assistant Dialog
        with ui.dialog() as self.edit_dialog, ui.card().classes("w-96 p-6"):
            ui.label("Assistent bearbeiten").classes("text-lg font-semibold mb-4")
            
            with ui.column().classes("space-y-4"):
                # Name
                ui.input(
                    label="Name",
                    placeholder="Assistenten-Name",
                    on_change=lambda e: self.update_form_data("name", e.value)
                ).classes("w-full")
                
                # Description
                ui.textarea(
                    label="Beschreibung",
                    placeholder="Beschreibung des Assistenten",
                    rows=3,
                    on_change=lambda e: self.update_form_data("description", e.value)
                ).classes("w-full")
                
                # Model
                ui.select(
                    label="AI-Modell",
                    options=[
                        ("gpt-4", "GPT-4"),
                        ("gpt-3.5-turbo", "GPT-3.5 Turbo"),
                        ("claude-3", "Claude-3"),
                        ("gemini-pro", "Gemini Pro")
                    ],
                    value="gpt-4",
                    on_change=lambda e: self.update_form_data("model", e.value)
                ).classes("w-full")
                
                # Temperature
                with ui.row().classes("items-center space-x-2"):
                    ui.label("Kreativität (Temperature)").classes("text-sm")
                    ui.slider(
                        min=0, max=2, step=0.1, value=0.7,
                        on_change=lambda e: self.update_form_data("temperature", e.value)
                    ).classes("flex-1")
                    ui.label("0.7").classes("text-sm text-gray-500 w-8")
                
                # Max Tokens
                ui.number(
                    label="Max Tokens",
                    min=100, max=8000, value=4096,
                    on_change=lambda e: self.update_form_data("max_tokens", e.value)
                ).classes("w-full")
                
                # Status
                ui.select(
                    label="Status",
                    options=[
                        ("active", "Aktiv"),
                        ("inactive", "Inaktiv")
                    ],
                    value="active",
                    on_change=lambda e: self.update_form_data("status", e.value)
                ).classes("w-full")
                
                # Buttons
                with ui.row().classes("justify-end space-x-2"):
                    ui.button(
                        "Abbrechen",
                        on_click=self.edit_dialog.close
                    ).classes("bg-gray-500 text-white")
                    
                    ui.button(
                        "Speichern",
                        on_click=self.update_assistant
                    ).classes("bg-blue-600 text-white")
    
    async def load_assistants(self):
        """Load assistants from API."""
        self.is_loading = True
        self.loading_spinner.show()
        self.error_component.hide()
        
        try:
            self.assistants = await assistant_service.get_assistants(force_refresh=True)
            self.display_assistants()
            
        except Exception as e:
            handle_network_error(e, "Laden der Assistenten")
            self.error_component.update_message(
                f"Fehler beim Laden der Assistenten: {str(e)}",
                ErrorSeverity.ERROR
            )
            self.error_component.show()
        
        finally:
            self.is_loading = False
            self.loading_spinner.hide()
    
    def display_assistants(self):
        """Display assistants in the grid."""
        self.assistants_container.clear()
        
        # Filter assistants
        filtered_assistants = self.filter_assistants()
        
        if not filtered_assistants:
            with self.assistants_container:
                with ui.element("div").classes("col-span-full text-center py-8"):
                    ui.icon("smart_toy").classes("w-12 h-12 text-gray-400 mx-auto mb-2")
                    ui.label("Keine Assistenten gefunden").classes("text-gray-500")
                    ui.button(
                        "Ersten Assistenten erstellen",
                        on_click=self.show_create_dialog
                    ).classes("mt-2 bg-green-600 text-white")
            return
        
        with self.assistants_container:
            for assistant in filtered_assistants:
                self.create_assistant_card(assistant)
    
    def filter_assistants(self) -> List:
        """Filter assistants based on search and status."""
        filtered = self.assistants
        
        # Status filter
        if self.filter_status != "all":
            filtered = [a for a in filtered if a.status == self.filter_status]
        
        # Search filter
        if self.search_query:
            query_lower = self.search_query.lower()
            filtered = [
                a for a in filtered
                if query_lower in a.name.lower() or query_lower in a.description.lower()
            ]
        
        return filtered
    
    def create_assistant_card(self, assistant):
        """Create an assistant card."""
        with ui.card().classes("p-4 hover:shadow-md transition-shadow"):
            with ui.column().classes("space-y-3"):
                # Header
                with ui.row().classes("items-center justify-between"):
                    with ui.element("div"):
                        ui.label(assistant.name).classes("font-semibold text-gray-900")
                        ui.label(assistant.description).classes("text-sm text-gray-600")
                    
                    # Status badge
                    status_color = "bg-green-100 text-green-800" if assistant.status == "active" else "bg-gray-100 text-gray-800"
                    ui.label(assistant.status.title()).classes(f"px-2 py-1 rounded-full text-xs font-medium {status_color}")
                
                # Model and settings
                with ui.row().classes("items-center space-x-4 text-sm text-gray-500"):
                    ui.label(f"Modell: {assistant.model}")
                    ui.label(f"Temp: {assistant.temperature}")
                    ui.label(f"Tokens: {assistant.max_tokens}")
                
                # Tools count
                tools_count = len(assistant.tools)
                ui.label(f"{tools_count} Tools zugewiesen").classes("text-xs text-gray-500")
                
                # Actions
                with ui.row().classes("space-x-2"):
                    ui.button(
                        "Bearbeiten",
                        icon="edit",
                        on_click=lambda: self.show_edit_dialog(assistant)
                    ).classes("flex-1 bg-blue-600 text-white")
                    
                    if assistant.status == "active":
                        ui.button(
                            "Deaktivieren",
                            icon="pause",
                            on_click=lambda: self.toggle_assistant_status(assistant)
                        ).classes("flex-1 bg-yellow-600 text-white")
                    else:
                        ui.button(
                            "Aktivieren",
                            icon="play_arrow",
                            on_click=lambda: self.toggle_assistant_status(assistant)
                        ).classes("flex-1 bg-green-600 text-white")
                    
                    ui.button(
                        "Löschen",
                        icon="delete",
                        on_click=lambda: self.delete_assistant(assistant)
                    ).classes("flex-1 bg-red-600 text-white")
    
    def show_create_dialog(self):
        """Show create assistant dialog."""
        self.reset_form_data()
        self.create_dialog.open()
    
    def show_edit_dialog(self, assistant):
        """Show edit assistant dialog."""
        self.current_assistant = assistant
        self.form_data = {
            "name": assistant.name,
            "description": assistant.description,
            "model": assistant.model,
            "temperature": assistant.temperature,
            "max_tokens": assistant.max_tokens,
            "tools": assistant.tools,
            "status": assistant.status
        }
        self.edit_dialog.open()
    
    def reset_form_data(self):
        """Reset form data to defaults."""
        self.form_data = {
            "name": "",
            "description": "",
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 4096,
            "tools": []
        }
        self.current_assistant = None
    
    def update_form_data(self, key: str, value):
        """Update form data."""
        self.form_data[key] = value
    
    async def create_assistant(self):
        """Create a new assistant."""
        try:
            # Validate form data
            validation_result = validate_assistant_data(self.form_data)
            if not validation_result["valid"]:
                self.error_component.update_message(
                    f"Validierungsfehler: {validation_result['errors']}",
                    ErrorSeverity.ERROR
                )
                self.error_component.show()
                return
            
            # Create assistant
            assistant = await assistant_service.create_assistant(self.form_data)
            
            if assistant:
                self.create_dialog.close()
                await self.load_assistants()
                
                # Show success message
                self.error_component.update_message(
                    f"Assistent '{assistant.name}' erfolgreich erstellt",
                    ErrorSeverity.INFO
                )
                self.error_component.show()
            else:
                self.error_component.update_message(
                    "Fehler beim Erstellen des Assistenten",
                    ErrorSeverity.ERROR
                )
                self.error_component.show()
        
        except Exception as e:
            handle_network_error(e, "Erstellen des Assistenten")
            self.error_component.update_message(
                f"Fehler beim Erstellen des Assistenten: {str(e)}",
                ErrorSeverity.ERROR
            )
            self.error_component.show()
    
    async def update_assistant(self):
        """Update an existing assistant."""
        if not self.current_assistant:
            return
        
        try:
            # Validate form data
            validation_result = validate_assistant_data(self.form_data)
            if not validation_result["valid"]:
                self.error_component.update_message(
                    f"Validierungsfehler: {validation_result['errors']}",
                    ErrorSeverity.ERROR
                )
                self.error_component.show()
                return
            
            # Update assistant
            assistant = await assistant_service.update_assistant(
                self.current_assistant.id,
                self.form_data
            )
            
            if assistant:
                self.edit_dialog.close()
                await self.load_assistants()
                
                # Show success message
                self.error_component.update_message(
                    f"Assistent '{assistant.name}' erfolgreich aktualisiert",
                    ErrorSeverity.INFO
                )
                self.error_component.show()
            else:
                self.error_component.update_message(
                    "Fehler beim Aktualisieren des Assistenten",
                    ErrorSeverity.ERROR
                )
                self.error_component.show()
        
        except Exception as e:
            handle_network_error(e, "Aktualisieren des Assistenten")
            self.error_component.update_message(
                f"Fehler beim Aktualisieren des Assistenten: {str(e)}",
                ErrorSeverity.ERROR
            )
            self.error_component.show()
    
    async def toggle_assistant_status(self, assistant):
        """Toggle assistant status between active and inactive."""
        try:
            new_status = "inactive" if assistant.status == "active" else "active"
            success = await assistant_service.update_assistant(
                assistant.id,
                {"status": new_status}
            )
            
            if success:
                await self.load_assistants()
                
                # Show success message
                status_text = "deaktiviert" if new_status == "inactive" else "aktiviert"
                self.error_component.update_message(
                    f"Assistent '{assistant.name}' erfolgreich {status_text}",
                    ErrorSeverity.INFO
                )
                self.error_component.show()
            else:
                self.error_component.update_message(
                    "Fehler beim Ändern des Assistenten-Status",
                    ErrorSeverity.ERROR
                )
                self.error_component.show()
        
        except Exception as e:
            handle_network_error(e, "Ändern des Assistenten-Status")
            self.error_component.update_message(
                f"Fehler beim Ändern des Assistenten-Status: {str(e)}",
                ErrorSeverity.ERROR
            )
            self.error_component.show()
    
    async def delete_assistant(self, assistant):
        """Delete an assistant."""
        try:
            success = await assistant_service.delete_assistant(assistant.id)
            
            if success:
                await self.load_assistants()
                
                # Show success message
                self.error_component.update_message(
                    f"Assistent '{assistant.name}' erfolgreich gelöscht",
                    ErrorSeverity.INFO
                )
                self.error_component.show()
            else:
                self.error_component.update_message(
                    "Fehler beim Löschen des Assistenten",
                    ErrorSeverity.ERROR
                )
                self.error_component.show()
        
        except Exception as e:
            handle_network_error(e, "Löschen des Assistenten")
            self.error_component.update_message(
                f"Fehler beim Löschen des Assistenten: {str(e)}",
                ErrorSeverity.ERROR
            )
            self.error_component.show()
    
    def on_search_change(self, event):
        """Handle search input change."""
        self.search_query = event.value
        self.display_assistants()
    
    def on_filter_change(self, event):
        """Handle status filter change."""
        self.filter_status = event.value
        self.display_assistants()


def create_assistants_page():
    """Create and return the assistants page."""
    return AssistantsPage()


# Register the page
@ui.page("/assistants")
def assistants_page():
    """Assistants page route."""
    return create_assistants_page() 