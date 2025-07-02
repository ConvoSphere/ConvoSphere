"""
Main NiceGUI application for the AI Assistant Platform.

This module serves as the entry point for the NiceGUI frontend application,
providing a modern web interface for managing AI assistants and conversations.
"""

import os
from typing import Optional
from nicegui import ui, app
from loguru import logger

# Import pages and components
from .pages.dashboard import DashboardPage
from .pages.assistants import AssistantsPage
from .pages.conversations import ConversationsPage
from .pages.tools import ToolsPage
from .pages.settings import SettingsPage
from .components.header import Header
from .components.sidebar import Sidebar


class AIAssistantApp:
    """Main application class for the AI Assistant Platform frontend."""
    
    def __init__(self):
        """Initialize the application."""
        self.current_page: Optional[str] = None
        self.user = None  # TODO: Add user authentication
        
        # Configure logging
        logger.add(
            "logs/frontend.log",
            rotation="10 MB",
            retention="7 days",
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}"
        )
    
    def setup_ui(self):
        """Setup the main user interface."""
        # Configure page
        ui.page_title("AI Assistant Platform")
        ui.page_meta("description", "AI Assistant Platform with multiple assistants and tools")
        ui.page_meta("viewport", "width=device-width, initial-scale=1")
        
        # Add CSS
        ui.add_head_html("""
        <style>
            .main-container {
                display: flex;
                height: 100vh;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            .sidebar {
                width: 250px;
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-right: 1px solid rgba(255, 255, 255, 0.2);
            }
            .content-area {
                flex: 1;
                display: flex;
                flex-direction: column;
            }
            .header {
                height: 60px;
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-bottom: 1px solid rgba(255, 255, 255, 0.2);
            }
            .main-content {
                flex: 1;
                padding: 20px;
                overflow-y: auto;
            }
            .card {
                background: rgba(255, 255, 255, 0.9);
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            .btn-primary {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border: none;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .btn-primary:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            }
        </style>
        """)
        
        # Create main layout
        with ui.element("div").classes("main-container"):
            # Sidebar
            with ui.element("div").classes("sidebar"):
                Sidebar(self.navigate_to_page)
            
            # Content area
            with ui.element("div").classes("content-area"):
                # Header
                with ui.element("div").classes("header"):
                    Header()
                
                # Main content
                with ui.element("div").classes("main-content"):
                    self.content_container = ui.element("div")
        
        # Set default page
        self.navigate_to_page("dashboard")
    
    def navigate_to_page(self, page_name: str):
        """Navigate to a specific page."""
        logger.info(f"Navigating to page: {page_name}")
        self.current_page = page_name
        
        # Clear current content
        self.content_container.clear()
        
        # Load page content
        with self.content_container:
            if page_name == "dashboard":
                DashboardPage()
            elif page_name == "assistants":
                AssistantsPage()
            elif page_name == "conversations":
                ConversationsPage()
            elif page_name == "tools":
                ToolsPage()
            elif page_name == "settings":
                SettingsPage()
            else:
                ui.label(f"Page '{page_name}' not found").classes("text-red-500")


def create_app() -> AIAssistantApp:
    """Create and configure the NiceGUI application."""
    app_instance = AIAssistantApp()
    app_instance.setup_ui()
    return app_instance


# Create application instance
app_instance = create_app()


if __name__ == "__main__":
    # Run the application
    ui.run(
        title="AI Assistant Platform",
        port=3000,
        reload=True,
        show=True
    ) 