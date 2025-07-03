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
from .pages import (
    create_dashboard_page,
    create_assistants_page,
    create_conversations_page,
    create_tools_page,
    create_knowledge_base_page,
    create_settings_page,
    create_chat_page
)
from .pages.mcp_tools import create_page as create_mcp_tools
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
        
        # Add CSS with improved styling for NiceGUI 2.20.0
        ui.add_head_html("""
        <style>
            .main-container {
                display: flex;
                height: 100vh;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            }
            .sidebar {
                width: 280px;
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-right: 1px solid rgba(255, 255, 255, 0.2);
                transition: all 0.3s ease;
            }
            .content-area {
                flex: 1;
                display: flex;
                flex-direction: column;
                overflow: hidden;
            }
            .header {
                height: 70px;
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-bottom: 1px solid rgba(255, 255, 255, 0.2);
                display: flex;
                align-items: center;
                padding: 0 20px;
            }
            .main-content {
                flex: 1;
                padding: 24px;
                overflow-y: auto;
                scroll-behavior: smooth;
            }
            .card {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 16px;
                padding: 24px;
                margin-bottom: 24px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                transition: all 0.3s ease;
            }
            .card:hover {
                transform: translateY(-2px);
                box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
            }
            .btn-primary {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border: none;
                color: white;
                padding: 12px 24px;
                border-radius: 12px;
                cursor: pointer;
                transition: all 0.3s ease;
                font-weight: 600;
                font-size: 14px;
            }
            .btn-primary:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
            }
            .nav-item {
                padding: 12px 20px;
                margin: 4px 12px;
                border-radius: 12px;
                cursor: pointer;
                transition: all 0.3s ease;
                color: rgba(255, 255, 255, 0.8);
            }
            .nav-item:hover {
                background: rgba(255, 255, 255, 0.1);
                color: white;
            }
            .nav-item.active {
                background: rgba(255, 255, 255, 0.2);
                color: white;
                font-weight: 600;
            }
            .status-indicator {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                display: inline-block;
                margin-right: 8px;
            }
            .status-online { background: #10b981; }
            .status-offline { background: #ef4444; }
            .status-maintenance { background: #f59e0b; }
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
                create_dashboard_page()
            elif page_name == "assistants":
                create_assistants_page()
            elif page_name == "chat":
                create_chat_page()
            elif page_name == "conversations":
                create_conversations_page()
            elif page_name == "tools":
                create_tools_page()
            elif page_name == "mcp_tools":
                create_mcp_tools()
            elif page_name == "knowledge_base":
                create_knowledge_base_page()
            elif page_name == "settings":
                create_settings_page()
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