"""
Dashboard page for the AI Assistant Platform.

This module provides the main dashboard view with statistics,
recent conversations, and quick actions.
"""

from nicegui import ui
from datetime import datetime, timedelta


class DashboardPage:
    """Dashboard page component."""
    
    def __init__(self):
        """Initialize the dashboard page."""
        self.setup_dashboard()
    
    def setup_dashboard(self):
        """Setup the dashboard layout and content."""
        # Welcome section
        with ui.element("div").classes("card"):
            ui.html("<h1 style='margin: 0 0 8px 0; font-size: 28px; font-weight: 700; color: #1f2937;'>Willkommen bei der AI Assistant Platform</h1>")
            ui.html("<p style='margin: 0; color: #6b7280; font-size: 16px;'>Verwalte deine Assistenten und starte neue Gespräche</p>")
        
        # Statistics cards
        with ui.row().classes("w-full gap-4"):
            with ui.element("div").classes("card flex-1"):
                ui.html("<div style='display: flex; align-items: center; justify-content: space-between;'>")
                ui.html("<div>")
                ui.html("<h3 style='margin: 0; font-size: 14px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px;'>Aktive Assistenten</h3>")
                ui.html("<p style='margin: 8px 0 0 0; font-size: 32px; font-weight: 700; color: #1f2937;'>12</p>")
                ui.html("</div>")
                ui.html("<div style='width: 48px; height: 48px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; display: flex; align-items: center; justify-content: center;'>")
                ui.html("<span style='color: white; font-size: 20px;'>🤖</span>")
                ui.html("</div>")
                ui.html("</div>")
            
            with ui.element("div").classes("card flex-1"):
                ui.html("<div style='display: flex; align-items: center; justify-content: space-between;'>")
                ui.html("<div>")
                ui.html("<h3 style='margin: 0; font-size: 14px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px;'>Gespräche heute</h3>")
                ui.html("<p style='margin: 8px 0 0 0; font-size: 32px; font-weight: 700; color: #1f2937;'>47</p>")
                ui.html("</div>")
                ui.html("<div style='width: 48px; height: 48px; background: linear-gradient(135deg, #10b981 0%, #059669 100%); border-radius: 12px; display: flex; align-items: center; justify-content: center;'>")
                ui.html("<span style='color: white; font-size: 20px;'>💬</span>")
                ui.html("</div>")
                ui.html("</div>")
            
            with ui.element("div").classes("card flex-1"):
                ui.html("<div style='display: flex; align-items: center; justify-content: space-between;'>")
                ui.html("<div>")
                ui.html("<h3 style='margin: 0; font-size: 14px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px;'>Verfügbare Tools</h3>")
                ui.html("<p style='margin: 8px 0 0 0; font-size: 32px; font-weight: 700; color: #1f2937;'>50+</p>")
                ui.html("</div>")
                ui.html("<div style='width: 48px; height: 48px; background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); border-radius: 12px; display: flex; align-items: center; justify-content: center;'>")
                ui.html("<span style='color: white; font-size: 20px;'>🛠️</span>")
                ui.html("</div>")
                ui.html("</div>")
            
            with ui.element("div").classes("card flex-1"):
                ui.html("<div style='display: flex; align-items: center; justify-content: space-between;'>")
                ui.html("<div>")
                ui.html("<h3 style='margin: 0; font-size: 14px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px;'>System Status</h3>")
                ui.html("<p style='margin: 8px 0 0 0; font-size: 16px; font-weight: 600; color: #10b981;'>Online</p>")
                ui.html("</div>")
                ui.html("<div style='width: 48px; height: 48px; background: linear-gradient(135deg, #10b981 0%, #059669 100%); border-radius: 12px; display: flex; align-items: center; justify-content: center;'>")
                ui.html("<span style='color: white; font-size: 20px;'>✅</span>")
                ui.html("</div>")
                ui.html("</div>")
        
        # Quick actions and recent conversations
        with ui.row().classes("w-full gap-6"):
            # Quick actions
            with ui.element("div").classes("card flex-1"):
                ui.html("<h2 style='margin: 0 0 20px 0; font-size: 20px; font-weight: 600; color: #1f2937;'>Schnellaktionen</h2>")
                
                with ui.column().classes("gap-3"):
                    ui.button("Neuen Assistenten erstellen", on_click=self.create_assistant).classes("btn-primary w-full")
                    ui.button("Gespräch starten", on_click=self.start_conversation).classes("bg-white border border-gray-300 text-gray-700 hover:bg-gray-50 w-full")
                    ui.button("Tools verwalten", on_click=self.manage_tools).classes("bg-white border border-gray-300 text-gray-700 hover:bg-gray-50 w-full")
                    ui.button("Einstellungen", on_click=self.open_settings).classes("bg-white border border-gray-300 text-gray-700 hover:bg-gray-50 w-full")
            
            # Recent conversations
            with ui.element("div").classes("card flex-1"):
                ui.html("<h2 style='margin: 0 0 20px 0; font-size: 20px; font-weight: 600; color: #1f2937;'>Letzte Gespräche</h2>")
                
                conversations = [
                    {"title": "Projektplanung Q1 2024", "assistant": "Business Assistant", "time": "vor 2 Stunden"},
                    {"title": "Code Review Request", "assistant": "Developer Assistant", "time": "vor 4 Stunden"},
                    {"title": "Marketing Strategie", "assistant": "Marketing Assistant", "time": "vor 6 Stunden"},
                    {"title": "Kundenanfrage Support", "assistant": "Support Assistant", "time": "vor 1 Tag"},
                ]
                
                for conv in conversations:
                    with ui.element("div").classes("p-3 border-b border-gray-100 last:border-b-0 hover:bg-gray-50 rounded-lg cursor-pointer"):
                        ui.html(f"<div style='display: flex; justify-content: space-between; align-items: center;'>")
                        ui.html(f"<div>")
                        ui.html(f"<p style='margin: 0; font-weight: 600; color: #1f2937;'>{conv['title']}</p>")
                        ui.html(f"<p style='margin: 4px 0 0 0; font-size: 14px; color: #6b7280;'>{conv['assistant']}</p>")
                        ui.html(f"</div>")
                        ui.html(f"<span style='font-size: 12px; color: #9ca3af;'>{conv['time']}</span>")
                        ui.html(f"</div>")
    
    def create_assistant(self):
        """Handle create assistant action."""
        ui.notify("Assistenten-Erstellung wird geöffnet...", type="info")
    
    def start_conversation(self):
        """Handle start conversation action."""
        ui.notify("Gesprächsauswahl wird geöffnet...", type="info")
    
    def manage_tools(self):
        """Handle manage tools action."""
        ui.notify("Tool-Verwaltung wird geöffnet...", type="info")
    
    def open_settings(self):
        """Handle open settings action."""
        ui.notify("Einstellungen werden geöffnet...", type="info")


# Create page instance
dashboard_page = DashboardPage()


def create_page():
    """Create and return the dashboard page."""
    return dashboard_page 