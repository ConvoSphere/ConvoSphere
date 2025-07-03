"""
Dashboard page for the AI Assistant Platform.

This module provides the main dashboard with overview statistics,
recent conversations, and quick actions.
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from nicegui import ui, app
from nicegui.events import ValueChangeEventArguments

from services.auth_service import auth_service
from services.assistant_service import assistant_service
from services.conversation_service import conversation_service
from services.error_handler import handle_api_error, handle_network_error
from components.common.loading_spinner import create_loading_spinner, show_loading_overlay
from components.common.error_message import create_error_message, ErrorSeverity
from utils.helpers import format_timestamp, format_relative_time, format_number
from utils.constants import API_BASE_URL


class DashboardPage:
    """Dashboard page with overview and statistics."""
    
    def __init__(self):
        """Initialize dashboard page."""
        self.is_loading = True
        self.error_message = None
        self.stats_container = None
        self.recent_conversations_container = None
        self.quick_actions_container = None
        
        # Statistics
        self.assistant_stats = {}
        self.conversation_stats = {}
        self.recent_conversations = []
        
        # UI Components
        self.loading_spinner = None
        self.error_component = None
        
        self.create_dashboard()
        # Defer async call to avoid blocking
        ui.timer(0.1, lambda: asyncio.create_task(self.load_dashboard_data()))
    
    def create_dashboard(self):
        """Create the dashboard UI."""
        with ui.column().classes("w-full max-w-7xl mx-auto p-6 space-y-6"):
            # Header
            with ui.row().classes("items-center justify-between"):
                ui.label("Dashboard").classes("text-2xl font-bold text-gray-900")
                
                with ui.row().classes("space-x-2"):
                    ui.button(
                        "Aktualisieren",
                        icon="refresh",
                        on_click=lambda: asyncio.create_task(self.load_dashboard_data())
                    ).classes("bg-blue-600 text-white")
                    
                    ui.button(
                        "Neue Konversation",
                        icon="add",
                        on_click=self.create_new_conversation
                    ).classes("bg-green-600 text-white")
            
            # Loading and Error States
            self.loading_spinner = create_loading_spinner("Lade Dashboard...", size="lg")
            self.error_component = create_error_message("", dismissible=True)
            
            # Main Content
            with ui.element("div").classes("grid grid-cols-1 lg:grid-cols-3 gap-6"):
                # Statistics Cards
                self.stats_container = ui.element("div").classes("lg:col-span-2")
                
                # Quick Actions
                self.quick_actions_container = ui.element("div").classes("lg:col-span-1")
            
            # Recent Conversations
            self.recent_conversations_container = ui.element("div").classes("mt-6")
    
    async def load_dashboard_data(self):
        """Load dashboard data from APIs."""
        self.is_loading = True
        self.loading_spinner.show()
        self.error_component.hide()
        
        try:
            # Load data concurrently
            tasks = [
                self.load_assistant_stats(),
                self.load_conversation_stats(),
                self.load_recent_conversations()
            ]
            
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Update UI
            self.update_dashboard_ui()
            
        except Exception as e:
            handle_network_error(e, "Laden der Dashboard-Daten")
            self.error_component.update_message(
                f"Fehler beim Laden der Dashboard-Daten: {str(e)}",
                ErrorSeverity.ERROR
            )
            self.error_component.show()
        
        finally:
            self.is_loading = False
            self.loading_spinner.hide()
    
    async def load_assistant_stats(self):
        """Load assistant statistics."""
        try:
            assistants = await assistant_service.get_assistants(force_refresh=True)
            self.assistant_stats = assistant_service.get_assistant_stats()
        except Exception as e:
            handle_network_error(e, "Laden der Assistenten-Statistiken")
            self.assistant_stats = {"total": 0, "active": 0, "inactive": 0, "models": []}
    
    async def load_conversation_stats(self):
        """Load conversation statistics."""
        try:
            conversations = await conversation_service.get_conversations(force_refresh=True)
            self.conversation_stats = conversation_service.get_conversation_stats()
        except Exception as e:
            handle_network_error(e, "Laden der Konversations-Statistiken")
            self.conversation_stats = {
                "total_conversations": 0,
                "active_conversations": 0,
                "archived_conversations": 0,
                "total_messages": 0,
                "average_messages_per_conversation": 0
            }
    
    async def load_recent_conversations(self):
        """Load recent conversations."""
        try:
            conversations = await conversation_service.get_conversations(force_refresh=True)
            self.recent_conversations = conversations[:5]  # Get last 5
        except Exception as e:
            handle_network_error(e, "Laden der letzten Konversationen")
            self.recent_conversations = []
    
    def update_dashboard_ui(self):
        """Update dashboard UI with loaded data."""
        # Clear existing content
        if self.stats_container:
            self.stats_container.clear()
        
        if self.quick_actions_container:
            self.quick_actions_container.clear()
        
        if self.recent_conversations_container:
            self.recent_conversations_container.clear()
        
        # Create statistics cards
        self.create_statistics_cards()
        
        # Create quick actions
        self.create_quick_actions()
        
        # Create recent conversations
        self.create_recent_conversations()
    
    def create_statistics_cards(self):
        """Create statistics cards."""
        with self.stats_container:
            ui.label("Übersicht").classes("text-lg font-semibold text-gray-900 mb-4")
            
            with ui.element("div").classes("grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4"):
                # Assistant Stats
                self.create_stat_card(
                    "Assistenten",
                    format_number(self.assistant_stats.get("total", 0)),
                    f"{format_number(self.assistant_stats.get('active', 0))} aktiv",
                    "smart_toy",
                    "bg-blue-500"
                )
                
                # Conversation Stats
                self.create_stat_card(
                    "Konversationen",
                    format_number(self.conversation_stats.get("total_conversations", 0)),
                    f"{format_number(self.conversation_stats.get('active_conversations', 0))} aktiv",
                    "chat",
                    "bg-green-500"
                )
                
                # Message Stats
                self.create_stat_card(
                    "Nachrichten",
                    format_number(self.conversation_stats.get("total_messages", 0)),
                    f"{format_number(self.conversation_stats.get('average_messages_per_conversation', 0))} pro Konversation",
                    "message",
                    "bg-purple-500"
                )
                
                # Model Stats
                model_count = len(self.assistant_stats.get("models", []))
                self.create_stat_card(
                    "Modelle",
                    format_number(model_count),
                    "verschiedene AI-Modelle",
                    "psychology",
                    "bg-orange-500"
                )
    
    def create_stat_card(self, title: str, value: str, subtitle: str, icon: str, color_class: str):
        """Create a statistics card.
        Args:
            title: Card title
            value: Formatted value as string
            subtitle: Subtitle
            icon: Icon name
            color_class: Tailwind color class
        """
        with ui.card().classes("p-4"):
            with ui.row().classes("items-center justify-between"):
                with ui.element("div"):
                    ui.label(title).classes("text-sm font-medium text-gray-600")
                    ui.label(value).classes("text-2xl font-bold text-gray-900")
                    ui.label(subtitle).classes("text-xs text-gray-500")
                
                ui.icon(icon).classes(f"w-8 h-8 {color_class} text-white rounded-lg p-1")
    
    def create_quick_actions(self):
        """Create quick actions panel."""
        with self.quick_actions_container:
            ui.label("Schnellaktionen").classes("text-lg font-semibold text-gray-900 mb-4")
            
            with ui.card().classes("p-4 space-y-3"):
                ui.button(
                    "Neue Konversation",
                    icon="add",
                    on_click=self.create_new_conversation
                ).classes("w-full bg-blue-600 text-white")
                
                ui.button(
                    "Assistent erstellen",
                    icon="smart_toy",
                    on_click=self.create_new_assistant
                ).classes("w-full bg-green-600 text-white")
                
                ui.button(
                    "Wissensdatenbank",
                    icon="library_books",
                    on_click=self.open_knowledge_base
                ).classes("w-full bg-purple-600 text-white")
                
                ui.button(
                    "Tools verwalten",
                    icon="build",
                    on_click=self.manage_tools
                ).classes("w-full bg-orange-600 text-white")
    
    def create_recent_conversations(self):
        """Create recent conversations list."""
        with self.recent_conversations_container:
            ui.label("Letzte Konversationen").classes("text-lg font-semibold text-gray-900 mb-4")
            
            if not self.recent_conversations:
                with ui.card().classes("p-6 text-center"):
                    ui.icon("chat_bubble_outline").classes("w-12 h-12 text-gray-400 mx-auto mb-2")
                    ui.label("Keine Konversationen vorhanden").classes("text-gray-500")
                    ui.button(
                        "Erste Konversation starten",
                        on_click=self.create_new_conversation
                    ).classes("mt-2 bg-blue-600 text-white")
            else:
                with ui.element("div").classes("space-y-3"):
                    for conversation in self.recent_conversations:
                        self.create_conversation_card(conversation)
    
    def create_conversation_card(self, conversation):
        """Create a conversation card."""
        with ui.card().classes("p-4 hover:shadow-md transition-shadow cursor-pointer"):
            with ui.row().classes("items-center justify-between"):
                with ui.element("div").classes("flex-1"):
                    ui.label(conversation.title).classes("font-medium text-gray-900")
                    ui.label(f"mit {conversation.assistant_name}").classes("text-sm text-gray-600")
                    
                    if conversation.last_message:
                        ui.label(conversation.last_message[:100] + "..." if len(conversation.last_message) > 100 else conversation.last_message).classes("text-sm text-gray-500 mt-1")
                    
                    ui.label(format_relative_time(conversation.updated_at)).classes("text-xs text-gray-400 mt-1")
                
                with ui.element("div").classes("text-right"):
                    ui.label(f"{format_number(conversation.message_count)} Nachrichten").classes("text-xs text-gray-500")
                    
                    with ui.row().classes("space-x-1 mt-2"):
                        ui.button(
                            icon="open_in_new",
                            on_click=lambda: self.open_conversation(conversation.id)
                        ).classes("w-8 h-8 bg-blue-100 text-blue-600")
                        
                        ui.button(
                            icon="archive",
                            on_click=lambda: self.archive_conversation(conversation.id)
                        ).classes("w-8 h-8 bg-gray-100 text-gray-600")
    
    async def create_new_conversation(self):
        """Create a new conversation."""
        try:
            # Get first available assistant
            assistants = assistant_service.get_active_assistants()
            if not assistants:
                self.error_component.update_message(
                    "Keine aktiven Assistenten verfügbar. Bitte erstellen Sie zuerst einen Assistenten.",
                    ErrorSeverity.WARNING
                )
                self.error_component.show()
                return
            
            assistant = assistants[0]
            conversation = await conversation_service.create_conversation(assistant.id)
            
            if conversation:
                # Navigate to chat page
                app.storage.user["current_conversation_id"] = conversation.id
                ui.navigate.to("/chat")
            else:
                self.error_component.update_message(
                    "Fehler beim Erstellen der Konversation",
                    ErrorSeverity.ERROR
                )
                self.error_component.show()
        
        except Exception as e:
            handle_network_error(e, "Erstellen der Konversation")
            self.error_component.update_message(
                f"Fehler beim Erstellen der Konversation: {str(e)}",
                ErrorSeverity.ERROR
            )
            self.error_component.show()
    
    def create_new_assistant(self):
        """Navigate to assistant creation."""
        ui.navigate.to("/assistants")
    
    def open_knowledge_base(self):
        """Navigate to knowledge base."""
        ui.navigate.to("/knowledge")
    
    def manage_tools(self):
        """Navigate to tools management."""
        ui.navigate.to("/tools")
    
    def open_conversation(self, conversation_id: str):
        """Open a conversation."""
        app.storage.user["current_conversation_id"] = conversation_id
        ui.navigate.to("/chat")
    
    async def archive_conversation(self, conversation_id: str):
        """Archive a conversation."""
        try:
            success = await conversation_service.archive_conversation(conversation_id)
            if success:
                # Refresh dashboard
                await self.load_dashboard_data()
            else:
                self.error_component.update_message(
                    "Fehler beim Archivieren der Konversation",
                    ErrorSeverity.ERROR
                )
                self.error_component.show()
        
        except Exception as e:
            handle_network_error(e, "Archivieren der Konversation")
            self.error_component.update_message(
                f"Fehler beim Archivieren der Konversation: {str(e)}",
                ErrorSeverity.ERROR
            )
            self.error_component.show()


def create_dashboard_page():
    """Create and return the dashboard page."""
    return DashboardPage()


# Register the page
@ui.page("/dashboard")
def dashboard_page():
    """Dashboard page route."""
    return create_dashboard_page()


def create_page():
    """Create and return a dashboard page instance."""
    return DashboardPage() 