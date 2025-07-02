"""
Header component for the AI Assistant Platform.

This module provides the main header with navigation, user menu, and notifications.
"""

from nicegui import ui
from datetime import datetime


class Header:
    """Header component with navigation and user controls."""
    
    def __init__(self):
        """Initialize the header component."""
        self.setup_header()
    
    def setup_header(self):
        """Setup the header layout and content."""
        with ui.element("div").classes("w-full flex items-center justify-between"):
            # Left side - Logo and title
            with ui.element("div").classes("flex items-center gap-4"):
                ui.html("<div style='width: 40px; height: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; display: flex; align-items: center; justify-content: center;'>")
                ui.html("<span style='color: white; font-size: 20px; font-weight: bold;'>AI</span>")
                ui.html("</div>")
                
                ui.html("<div>")
                ui.html("<h1 style='margin: 0; font-size: 20px; font-weight: 700; color: white;'>AI Assistant Platform</h1>")
                ui.html("<p style='margin: 0; font-size: 12px; color: rgba(255, 255, 255, 0.7);'>v2.20.0</p>")
                ui.html("</div>")
            
            # Center - Search bar
            with ui.element("div").classes("flex-1 max-w-md mx-8"):
                with ui.input(placeholder="Suche nach Assistenten, Gesprächen...").classes("w-full bg-white bg-opacity-20 border border-white border-opacity-30 rounded-lg text-white placeholder-white placeholder-opacity-70"):
                    ui.html("<div style='position: absolute; right: 12px; top: 50%; transform: translateY(-50%);'>")
                    ui.html("<span style='color: rgba(255, 255, 255, 0.7);'>🔍</span>")
                    ui.html("</div>")
            
            # Right side - User menu and notifications
            with ui.element("div").classes("flex items-center gap-4"):
                # Notifications
                with ui.button(icon="notifications", on_click=self.show_notifications).classes("bg-white bg-opacity-20 border border-white border-opacity-30 text-white hover:bg-opacity-30"):
                    ui.badge("3").classes("absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center")
                
                # User menu
                with ui.button(on_click=self.show_user_menu).classes("bg-white bg-opacity-20 border border-white border-opacity-30 text-white hover:bg-opacity-30 flex items-center gap-2"):
                    ui.html("<div style='width: 32px; height: 32px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center;'>")
                    ui.html("<span style='color: white; font-size: 14px; font-weight: 600;'>JD</span>")
                    ui.html("</div>")
                    ui.html("<span style='font-size: 14px;'>Johannes Doe</span>")
                    ui.html("<span style='font-size: 12px;'>▼</span>")
    
    def show_notifications(self):
        """Show notifications dropdown."""
        with ui.dialog() as dialog, ui.card():
            ui.html("<h3 style='margin: 0 0 16px 0; font-size: 18px; font-weight: 600;'>Benachrichtigungen</h3>")
            
            notifications = [
                {"title": "Neuer Assistent erstellt", "message": "Business Assistant wurde erfolgreich erstellt", "time": "vor 5 Minuten"},
                {"title": "Gespräch beendet", "message": "Projektplanung Q1 2024 wurde abgeschlossen", "time": "vor 15 Minuten"},
                {"title": "System Update", "message": "Neue Tools sind verfügbar", "time": "vor 1 Stunde"},
            ]
            
            for notif in notifications:
                with ui.element("div").classes("p-3 border-b border-gray-100 last:border-b-0"):
                    ui.html(f"<p style='margin: 0; font-weight: 600; color: #1f2937;'>{notif['title']}</p>")
                    ui.html(f"<p style='margin: 4px 0 0 0; font-size: 14px; color: #6b7280;'>{notif['message']}</p>")
                    ui.html(f"<p style='margin: 4px 0 0 0; font-size: 12px; color: #9ca3af;'>{notif['time']}</p>")
            
            with ui.row().classes("w-full justify-end gap-2 mt-4"):
                ui.button("Alle markieren", on_click=dialog.close).classes("text-blue-600 hover:text-blue-700")
                ui.button("Schließen", on_click=dialog.close).classes("btn-primary")
        
        dialog.open()
    
    def show_user_menu(self):
        """Show user menu dropdown."""
        with ui.dialog() as dialog, ui.card():
            ui.html("<h3 style='margin: 0 0 16px 0; font-size: 18px; font-weight: 600;'>Benutzer-Menü</h3>")
            
            with ui.column().classes("gap-2"):
                ui.button("Profil bearbeiten", on_click=self.edit_profile).classes("w-full justify-start text-left")
                ui.button("Einstellungen", on_click=self.open_settings).classes("w-full justify-start text-left")
                ui.button("API-Schlüssel", on_click=self.manage_api_keys).classes("w-full justify-start text-left")
                ui.separator()
                ui.button("Abmelden", on_click=self.logout).classes("w-full justify-start text-left text-red-600 hover:text-red-700")
            
            ui.button("Schließen", on_click=dialog.close).classes("btn-primary w-full mt-4")
        
        dialog.open()
    
    def edit_profile(self):
        """Handle edit profile action."""
        ui.notify("Profil-Bearbeitung wird geöffnet...", type="info")
    
    def open_settings(self):
        """Handle open settings action."""
        ui.notify("Einstellungen werden geöffnet...", type="info")
    
    def manage_api_keys(self):
        """Handle manage API keys action."""
        ui.notify("API-Schlüssel-Verwaltung wird geöffnet...", type="info")
    
    def logout(self):
        """Handle logout action."""
        ui.notify("Abmeldung wird durchgeführt...", type="warning") 