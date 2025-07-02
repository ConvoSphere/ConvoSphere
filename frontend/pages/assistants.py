"""
Assistants page for the AI Assistant Platform.

This module provides the assistants management interface.
"""

from nicegui import ui


class AssistantsPage:
    """Assistants management page."""
    
    def __init__(self):
        """Initialize the assistants page."""
        self.setup_assistants_page()
    
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
        
        # Assistants grid
        assistants = [
            {
                "id": "1",
                "name": "Business Assistant",
                "description": "Hilft bei Geschäftsentscheidungen und Strategieplanung",
                "personality": "Professionell und analytisch",
                "status": "active",
                "tools": ["web_search", "data_analysis", "email"],
                "model": "gpt-4",
                "created": "2024-01-15"
            },
            {
                "id": "2", 
                "name": "Developer Assistant",
                "description": "Unterstützt bei der Softwareentwicklung und Code-Reviews",
                "personality": "Technisch und präzise",
                "status": "active",
                "tools": ["code_generation", "git_integration", "documentation"],
                "model": "gpt-4",
                "created": "2024-01-10"
            },
            {
                "id": "3",
                "name": "Marketing Assistant", 
                "description": "Hilft bei Marketingstrategien und Kampagnenplanung",
                "personality": "Kreativ und kommunikativ",
                "status": "inactive",
                "tools": ["social_media", "analytics", "content_creation"],
                "model": "gpt-3.5-turbo",
                "created": "2024-01-05"
            }
        ]
        
        with ui.row().classes("w-full gap-6"):
            for assistant in assistants:
                with ui.element("div").classes("card flex-1"):
                    # Header
                    ui.html(f"<div style='display: flex; justify-content: space-between; align-items: start; margin-bottom: 16px;'>")
                    ui.html(f"<div>")
                    ui.html(f"<h3 style='margin: 0; font-size: 20px; font-weight: 600; color: #1f2937;'>{assistant['name']}</h3>")
                    ui.html(f"<p style='margin: 4px 0 0 0; font-size: 14px; color: #6b7280;'>{assistant['description']}</p>")
                    ui.html(f"</div>")
                    
                    # Status badge
                    status_color = "#10b981" if assistant['status'] == 'active' else "#6b7280"
                    ui.html(f"<span style='background: {status_color}; color: white; padding: 4px 8px; border-radius: 6px; font-size: 12px; font-weight: 500;'>{assistant['status']}</span>")
                    ui.html(f"</div>")
                    
                    # Personality
                    ui.html(f"<p style='margin: 0 0 12px 0; font-size: 14px; color: #374151;'><strong>Persönlichkeit:</strong> {assistant['personality']}</p>")
                    
                    # Tools
                    ui.html(f"<p style='margin: 0 0 12px 0; font-size: 14px; color: #374151;'><strong>Tools:</strong></p>")
                    with ui.row().classes("gap-2 mb-4"):
                        for tool in assistant['tools'][:3]:
                            ui.html(f"<span style='background: #f3f4f6; color: #374151; padding: 2px 8px; border-radius: 4px; font-size: 12px;'>{tool}</span>")
                        if len(assistant['tools']) > 3:
                            ui.html(f"<span style='background: #f3f4f6; color: #374151; padding: 2px 8px; border-radius: 4px; font-size: 12px;'>+{len(assistant['tools']) - 3}</span>")
                    
                    # Model and created date
                    ui.html(f"<p style='margin: 0 0 8px 0; font-size: 12px; color: #6b7280;'><strong>Model:</strong> {assistant['model']}</p>")
                    ui.html(f"<p style='margin: 0 0 16px 0; font-size: 12px; color: #6b7280;'><strong>Erstellt:</strong> {assistant['created']}</p>")
                    
                    # Action buttons
                    with ui.row().classes("gap-2"):
                        ui.button("Bearbeiten", on_click=lambda a=assistant: self.edit_assistant(a)).classes("flex-1 bg-blue-600 text-white hover:bg-blue-700")
                        ui.button("Testen", on_click=lambda a=assistant: self.test_assistant(a)).classes("flex-1 bg-green-600 text-white hover:bg-green-700")
                        ui.button("Löschen", on_click=lambda a=assistant: self.delete_assistant(a)).classes("flex-1 bg-red-600 text-white hover:bg-red-700")
    
    def create_assistant(self):
        """Handle create assistant action."""
        ui.notify("Assistenten-Erstellung wird geöffnet...", type="info")
    
    def import_assistant(self):
        """Handle import assistant action."""
        ui.notify("Assistenten-Import wird geöffnet...", type="info")
    
    def export_assistants(self):
        """Handle export assistants action."""
        ui.notify("Assistenten-Export wird gestartet...", type="info")
    
    def edit_assistant(self, assistant):
        """Handle edit assistant action."""
        ui.notify(f"Bearbeite Assistent: {assistant['name']}", type="info")
    
    def test_assistant(self, assistant):
        """Handle test assistant action."""
        ui.notify(f"Teste Assistent: {assistant['name']}", type="info")
    
    def delete_assistant(self, assistant):
        """Handle delete assistant action."""
        ui.notify(f"Lösche Assistent: {assistant['name']}", type="warning") 