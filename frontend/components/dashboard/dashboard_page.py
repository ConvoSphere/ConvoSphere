"""
Dashboard component for the main application overview.

This module provides a comprehensive dashboard with statistics,
quick actions, and recent activity monitoring.
"""

from typing import Dict, Any, List
from nicegui import ui

from services.api_client import api_client


class DashboardPage:
    """Dashboard page component with overview and statistics."""
    
    def __init__(self):
        """Initialize the dashboard page."""
        self.stats = {
            "total_conversations": 0,
            "active_assistants": 0,
            "total_tools": 0,
            "knowledge_documents": 0
        }
        self.recent_activity = []
        self.quick_actions = []
    
    def create_dashboard(self) -> ui.element:
        """
        Create the dashboard layout.
        
        Returns:
            ui.element: The dashboard container
        """
        with ui.element("div").classes("space-y-6") as dashboard:
            # Welcome section
            self._create_welcome_section()
            
            # Statistics cards
            self._create_stats_section()
            
            # Quick actions
            self._create_quick_actions_section()
            
            # Recent activity
            self._create_recent_activity_section()
            
            # System status
            self._create_system_status_section()
        
        return dashboard
    
    def _create_welcome_section(self):
        """Create the welcome section."""
        with ui.element("div").classes("bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6"):
            with ui.element("div").classes("flex items-center justify-between"):
                with ui.element("div"):
                    ui.html("<h1 style='font-size: 24px; font-weight: 700; color: var(--color-text); margin-bottom: 4px;'>Willkommen zu ConvoSphere</h1>")
                    ui.html("<p style='color: var(--color-text-secondary); font-size: 16px;'>Deine AI Assistant Platform</p>")
                
                with ui.element("div").classes("text-right"):
                    ui.html("<p style='color: var(--color-text-secondary); font-size: 14px;'>Letzter Login</p>")
                    ui.html("<p style='color: var(--color-text); font-size: 16px; font-weight: 600;'>Heute, 09:30</p>")
    
    def _create_stats_section(self):
        """Create the statistics section."""
        with ui.element("div").classes("grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"):
            # Total Conversations
            self._create_stat_card(
                title="Konversationen",
                value="24",
                change="+12%",
                change_type="positive",
                icon="chat",
                color="blue"
            )
            
            # Active Assistants
            self._create_stat_card(
                title="Aktive Assistenten",
                value="8",
                change="+2",
                change_type="positive",
                icon="smart_toy",
                color="green"
            )
            
            # Total Tools
            self._create_stat_card(
                title="Verfügbare Tools",
                value="15",
                change="+3",
                change_type="positive",
                icon="build",
                color="purple"
            )
            
            # Knowledge Documents
            self._create_stat_card(
                title="Wissensdokumente",
                value="42",
                change="+8",
                change_type="positive",
                icon="library_books",
                color="orange"
            )
    
    def _create_stat_card(self, title: str, value: str, change: str, change_type: str, icon: str, color: str):
        """Create a statistics card."""
        color_classes = {
            "blue": "bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-700",
            "green": "bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-700",
            "purple": "bg-purple-50 dark:bg-purple-900/20 border-purple-200 dark:border-purple-700",
            "orange": "bg-orange-50 dark:bg-orange-900/20 border-orange-200 dark:border-orange-700"
        }
        
        change_color = "text-green-600 dark:text-green-400" if change_type == "positive" else "text-red-600 dark:text-red-400"
        
        with ui.element("div").classes(f"bg-white dark:bg-gray-800 rounded-lg shadow-sm border {color_classes[color]} p-6"):
            with ui.element("div").classes("flex items-center justify-between"):
                with ui.element("div"):
                    ui.html(f"<p style='color: var(--color-text-secondary); font-size: 14px; margin-bottom: 4px;'>{title}</p>")
                    ui.html(f"<p style='font-size: 32px; font-weight: 700; color: var(--color-text); margin-bottom: 4px;'>{value}</p>")
                    ui.html(f"<p style='font-size: 14px; {change_color};'>{change} vs. letzter Monat</p>")
                
                with ui.element("div").classes(f"p-3 rounded-full bg-{color}-100 dark:bg-{color}-900/30"):
                    ui.icon(icon).classes(f"h-6 w-6 text-{color}-600 dark:text-{color}-400")
    
    def _create_quick_actions_section(self):
        """Create the quick actions section."""
        with ui.element("div").classes("bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6"):
            ui.html("<h2 style='font-size: 20px; font-weight: 600; color: var(--color-text); margin-bottom: 6px;'>Schnellaktionen</h2>")
            ui.html("<p style='color: var(--color-text-secondary); font-size: 14px; margin-bottom: 6px;'>Häufig verwendete Funktionen</p>")
            
            with ui.element("div").classes("grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-4"):
                self._create_quick_action_button(
                    "Neue Konversation",
                    "chat",
                    "Neue Chat-Sitzung starten",
                    lambda: self._handle_new_conversation()
                )
                
                self._create_quick_action_button(
                    "Assistent erstellen",
                    "smart_toy",
                    "Neuen AI-Assistenten konfigurieren",
                    lambda: self._handle_create_assistant()
                )
                
                self._create_quick_action_button(
                    "Dokument hochladen",
                    "upload_file",
                    "Neues Wissen zur Datenbank hinzufügen",
                    lambda: self._handle_upload_document()
                )
                
                self._create_quick_action_button(
                    "Tool hinzufügen",
                    "extension",
                    "Neues Tool zur Bibliothek hinzufügen",
                    lambda: self._handle_add_tool()
                )
    
    def _create_quick_action_button(self, title: str, icon: str, description: str, on_click):
        """Create a quick action button."""
        with ui.element("div").classes("group"):
            with ui.button(
                on_click=on_click
            ).classes("w-full p-4 text-left bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-lg border border-gray-200 dark:border-gray-600 transition-colors"):
                with ui.element("div").classes("flex items-center space-x-3"):
                    ui.icon(icon).classes("h-5 w-5 text-gray-600 dark:text-gray-400")
                    with ui.element("div"):
                        ui.html(f"<p style='font-size: 14px; font-weight: 600; color: var(--color-text); margin-bottom: 2px;'>{title}</p>")
                        ui.html(f"<p style='font-size: 12px; color: var(--color-text-secondary);'>{description}</p>")
    
    def _create_recent_activity_section(self):
        """Create the recent activity section."""
        with ui.element("div").classes("bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6"):
            ui.html("<h2 style='font-size: 20px; font-weight: 600; color: var(--color-text); margin-bottom: 6px;'>Letzte Aktivitäten</h2>")
            ui.html("<p style='color: var(--color-text-secondary); font-size: 14px; margin-bottom: 6px;'>Übersicht der letzten Aktionen</p>")
            
            with ui.element("div").classes("space-y-4 mt-4"):
                self._create_activity_item(
                    "Neue Konversation gestartet",
                    "Mit 'Code Assistant' begonnen",
                    "vor 5 Minuten",
                    "chat",
                    "blue"
                )
                
                self._create_activity_item(
                    "Dokument hochgeladen",
                    "API-Dokumentation.pdf zur Wissensdatenbank hinzugefügt",
                    "vor 15 Minuten",
                    "upload_file",
                    "green"
                )
                
                self._create_activity_item(
                    "Tool konfiguriert",
                    "GitHub Integration erfolgreich eingerichtet",
                    "vor 1 Stunde",
                    "extension",
                    "purple"
                )
                
                self._create_activity_item(
                    "Assistent aktualisiert",
                    "Konfiguration von 'Data Analyst' geändert",
                    "vor 2 Stunden",
                    "smart_toy",
                    "orange"
                )
    
    def _create_activity_item(self, title: str, description: str, time: str, icon: str, color: str):
        """Create an activity item."""
        color_classes = {
            "blue": "bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400",
            "green": "bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400",
            "purple": "bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400",
            "orange": "bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400"
        }
        
        with ui.element("div").classes("flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"):
            with ui.element("div").classes(f"p-2 rounded-full {color_classes[color]}"):
                ui.icon(icon).classes("h-4 w-4")
            
            with ui.element("div").classes("flex-1 min-w-0"):
                ui.html(f"<p style='font-size: 14px; font-weight: 600; color: var(--color-text); margin-bottom: 2px;'>{title}</p>")
                ui.html(f"<p style='font-size: 13px; color: var(--color-text-secondary); margin-bottom: 2px;'>{description}</p>")
                ui.html(f"<p style='font-size: 12px; color: var(--color-text-secondary);'>{time}</p>")
    
    def _create_system_status_section(self):
        """Create the system status section."""
        with ui.element("div").classes("bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6"):
            ui.html("<h2 style='font-size: 20px; font-weight: 600; color: var(--color-text); margin-bottom: 6px;'>System Status</h2>")
            ui.html("<p style='color: var(--color-text-secondary); font-size: 14px; margin-bottom: 6px;'>Aktuelle System-Informationen</p>")
            
            with ui.element("div").classes("grid grid-cols-1 md:grid-cols-2 gap-4 mt-4"):
                # Backend Status
                with ui.element("div").classes("flex items-center justify-between p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-700"):
                    with ui.element("div").classes("flex items-center space-x-3"):
                        ui.icon("check_circle").classes("h-5 w-5 text-green-600 dark:text-green-400")
                        with ui.element("div"):
                            ui.html("<p style='font-size: 14px; font-weight: 600; color: var(--color-text);'>Backend API</p>")
                            ui.html("<p style='font-size: 12px; color: var(--color-text-secondary);'>Online</p>")
                
                # Database Status
                with ui.element("div").classes("flex items-center justify-between p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-700"):
                    with ui.element("div").classes("flex items-center space-x-3"):
                        ui.icon("check_circle").classes("h-5 w-5 text-green-600 dark:text-green-400")
                        with ui.element("div"):
                            ui.html("<p style='font-size: 14px; font-weight: 600; color: var(--color-text);'>Datenbank</p>")
                            ui.html("<p style='font-size: 12px; color: var(--color-text-secondary);'>Verbunden</p>")
                
                # Vector DB Status
                with ui.element("div").classes("flex items-center justify-between p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-700"):
                    with ui.element("div").classes("flex items-center space-x-3"):
                        ui.icon("check_circle").classes("h-5 w-5 text-green-600 dark:text-green-400")
                        with ui.element("div"):
                            ui.html("<p style='font-size: 14px; font-weight: 600; color: var(--color-text);'>Vector DB</p>")
                            ui.html("<p style='font-size: 12px; color: var(--color-text-secondary);'>Aktiv</p>")
                
                # Cache Status
                with ui.element("div").classes("flex items-center justify-between p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-700"):
                    with ui.element("div").classes("flex items-center space-x-3"):
                        ui.icon("check_circle").classes("h-5 w-5 text-green-600 dark:text-green-400")
                        with ui.element("div"):
                            ui.html("<p style='font-size: 14px; font-weight: 600; color: var(--color-text);'>Cache</p>")
                            ui.html("<p style='font-size: 12px; color: var(--color-text-secondary);'>Verfügbar</p>")
    
    # Event handlers
    def _handle_new_conversation(self):
        """Handle new conversation action."""
        try:
            # Navigate to chat page
            from frontend.pages.chat import create_chat_page
            ui.clear()
            chat_page = create_chat_page()
            ui.add(chat_page)
        except Exception as e:
            ui.notify(f"Fehler beim Navigieren zur Chat-Seite: {str(e)}", type="negative")
    
    def _handle_create_assistant(self):
        """Handle create assistant action."""
        try:
            # Navigate to assistants page
            from frontend.pages.assistants import create_assistants_page
            ui.clear()
            assistants_page = create_assistants_page()
            ui.add(assistants_page)
        except Exception as e:
            ui.notify(f"Fehler beim Navigieren zur Assistenten-Seite: {str(e)}", type="negative")
    
    def _handle_upload_document(self):
        """Handle upload document action."""
        try:
            # Navigate to knowledge base page
            from frontend.pages.knowledge import create_knowledge_page
            ui.clear()
            knowledge_page = create_knowledge_page()
            ui.add(knowledge_page)
        except Exception as e:
            ui.notify(f"Fehler beim Navigieren zur Knowledge-Base-Seite: {str(e)}", type="negative")
    
    def _handle_add_tool(self):
        """Handle add tool action."""
        try:
            # Navigate to tools page
            from frontend.pages.tools import create_tools_page
            ui.clear()
            tools_page = create_tools_page()
            ui.add(tools_page)
        except Exception as e:
            ui.notify(f"Fehler beim Navigieren zur Tools-Seite: {str(e)}", type="negative")
    
    async def load_dashboard_data(self):
        """Load dashboard data from API."""
        try:
            # Load statistics from API
            stats_response = await api_client.get_dashboard_stats()
            if stats_response.get("success"):
                self.stats = stats_response.get("data", {})
            else:
                # Fallback to default values
                self.stats = {
                    "total_conversations": 0,
                    "active_assistants": 0,
                    "total_tools": 0,
                    "knowledge_documents": 0
                }
            
            # Load recent activity from API
            activity_response = await api_client.get_recent_activity()
            if activity_response.get("success"):
                self.recent_activity = activity_response.get("data", [])
            else:
                # Fallback to default values
                self.recent_activity = []
            
        except Exception as e:
            ui.notify(f"Fehler beim Laden der Dashboard-Daten: {str(e)}", type="negative")
            # Set fallback values
            self.stats = {
                "total_conversations": 0,
                "active_assistants": 0,
                "total_tools": 0,
                "knowledge_documents": 0
            }
            self.recent_activity = []


def create_dashboard_page() -> ui.element:
    """
    Create and return a dashboard page.
    
    Returns:
        ui.element: The dashboard page
    """
    dashboard = DashboardPage()
    return dashboard.create_dashboard() 