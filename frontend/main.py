"""
Main application entry point for ConvoSphere.

This module provides the main application setup using modular components
for authentication, routing, layout, and theme management.
"""

import asyncio

from nicegui import ui
from services.auth_service import auth_service
from utils.router import router
from utils.theme_manager import theme_manager


class ConvoSphereApp:
    """Main ConvoSphere application class."""

    def __init__(self):
        """Initialize the application."""
        self.current_page = "login"
        self.is_initialized = False

        # Setup theme
        theme_manager.set_theme("light")

        # Setup router callbacks
        router.on_navigation(self._handle_navigation)

    def initialize(self):
        """Initialize the application."""
        if self.is_initialized:
            return

        # Setup page
        self._setup_page()

        # Check authentication status
        asyncio.create_task(self._check_auth_status())

        self.is_initialized = True

    def _setup_page(self):
        """Setup the main page."""
        # Set page title
        ui.page_title("ConvoSphere - AI Assistant Platform")

        # Add CSS
        ui.add_head_html("""
            <link rel="stylesheet" href="/static/css/themes.css">
        """)

        # Create main container
        with ui.element("div").classes("app-container"):
            # Content will be loaded by router
            pass

    async def _check_auth_status(self):
        """Check authentication status on startup."""
        try:
            # Check if user is authenticated
            if auth_service.is_user_authenticated():
                # Navigate to dashboard
                router.navigate_to("dashboard")
            else:
                # Navigate to login
                router.navigate_to("login")
        except Exception as e:
            print(f"Error checking auth status: {e}")
            router.navigate_to("login")

    def _handle_navigation(self, page_name: str):
        """Handle navigation events."""
        self.current_page = page_name
        print(f"Navigated to: {page_name}")


# Global app instance
app_instance = ConvoSphereApp()


@ui.page("/")
def main_page():
    """Main page handler."""
    app_instance.initialize()

    # Start with login page
    router.navigate_to("login")


def main():
    """Main application entry point."""
    ui.run(
        title="ConvoSphere",
        port=8080,
        reload=False,
        show=False,
        dark=False,
    )


# Development server configuration
if __name__ in {"__main__", "__mp_main__"}:
    main()
