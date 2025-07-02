"""
Sidebar component for the AI Assistant Platform.

This module provides the main navigation sidebar with menu items and user controls.
"""

from nicegui import ui


class Sidebar:
    """Sidebar component with navigation menu."""
    
    def __init__(self, navigate_callback):
        """Initialize the sidebar component."""
        self.navigate_callback = navigate_callback
        self.current_page = "dashboard"
        self.setup_sidebar()
    
    def setup_sidebar(self):
        """Setup the sidebar layout and navigation."""
        # Logo and title
        with ui.element("div").classes("p-6 border-b border-white border-opacity-20"):
            ui.html("<div style='display: flex; align-items: center; gap-3;'>")
            ui.html("<div style='width: 40px; height: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; display: flex; align-items: center; justify-content: center;'>")
            ui.html("<span style='color: white; font-size: 20px; font-weight: bold;'>AI</span>")
            ui.html("</div>")
            ui.html("<div>")
            ui.html("<h2 style='margin: 0; font-size: 18px; font-weight: 700; color: white;'>Assistant</h2>")
            ui.html("<p style='margin: 0; font-size: 12px; color: rgba(255, 255, 255, 0.7);'>Platform</p>")
            ui.html("</div>")
            ui.html("</div>")
        
        # Navigation menu
        with ui.element("div").classes("flex-1 p-4"):
            nav_items = [
                {"id": "dashboard", "label": "Dashboard", "icon": "📊", "description": "Übersicht und Statistiken"},
                {"id": "assistants", "label": "Assistenten", "icon": "🤖", "description": "AI-Assistenten verwalten"},
                {"id": "chat", "label": "Chat", "icon": "💬", "description": "Chat mit AI-Assistenten"},
                {"id": "conversations", "label": "Gespräche", "icon": "💬", "description": "Chat-Verlauf und Nachrichten"},
                {"id": "tools", "label": "Tools", "icon": "🛠️", "description": "Tool-Bibliothek und Konfiguration"},
                {"id": "mcp_tools", "label": "MCP Tools", "icon": "🔌", "description": "MCP Server und Tools verwalten"},
                {"id": "analytics", "label": "Analytics", "icon": "📈", "description": "Nutzungsstatistiken und Berichte"},
                {"id": "settings", "label": "Einstellungen", "icon": "⚙️", "description": "System- und Benutzereinstellungen"},
            ]
            
            for item in nav_items:
                is_active = self.current_page == item["id"]
                with ui.element("div").classes(f"nav-item {'active' if is_active else ''}"):
                    ui.html(f"<div style='display: flex; align-items: center; gap-3; cursor: pointer;' onclick='window.navigateToPage(\"{item['id']}\")'>")
                    ui.html(f"<span style='font-size: 18px;'>{item['icon']}</span>")
                    ui.html(f"<div>")
                    ui.html(f"<p style='margin: 0; font-weight: 600;'>{item['label']}</p>")
                    ui.html(f"<p style='margin: 0; font-size: 12px; opacity: 0.7;'>{item['description']}</p>")
                    ui.html(f"</div>")
                    ui.html(f"</div>")
        
        # Bottom section - System status and quick actions
        with ui.element("div").classes("p-4 border-t border-white border-opacity-20"):
            # System status
            with ui.element("div").classes("mb-4"):
                ui.html("<p style='margin: 0 0 8px 0; font-size: 12px; color: rgba(255, 255, 255, 0.7); text-transform: uppercase; letter-spacing: 0.5px;'>System Status</p>")
                ui.html("<div style='display: flex; align-items: center; gap-2;'>")
                ui.html("<span class='status-indicator status-online'></span>")
                ui.html("<span style='font-size: 14px; color: white;'>Alle Systeme online</span>")
                ui.html("</div>")
            
            # Quick actions
            with ui.element("div"):
                ui.html("<p style='margin: 0 0 8px 0; font-size: 12px; color: rgba(255, 255, 255, 0.7); text-transform: uppercase; letter-spacing: 0.5px;'>Schnellaktionen</p>")
                
                with ui.column().classes("gap-2"):
                    ui.button("Neuer Assistent", on_click=self.create_assistant).classes("w-full bg-white bg-opacity-20 border border-white border-opacity-30 text-white hover:bg-opacity-30 text-sm")
                    ui.button("Gespräch starten", on_click=self.start_conversation).classes("w-full bg-white bg-opacity-20 border border-white border-opacity-30 text-white hover:bg-opacity-30 text-sm")
    
    def create_assistant(self):
        """Handle create assistant action."""
        ui.notify("Assistenten-Erstellung wird geöffnet...", type="info")
        self.navigate_callback("assistants")
    
    def start_conversation(self):
        """Handle start conversation action."""
        ui.notify("Gesprächsauswahl wird geöffnet...", type="info")
        self.navigate_callback("conversations") 