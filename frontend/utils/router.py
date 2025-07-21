"""
Router for handling page navigation and state management.

This module provides a centralized routing system for the application
with page transitions and state management.
"""

from collections.abc import Callable
from typing import Any

from nicegui import ui
from utils.logger import get_logger


class Router:
    """Centralized routing system."""

    def __init__(self):
        """Initialize the router."""
        self.current_page = "login"
        self.previous_page = ""
        self.page_handlers: dict[str, Callable] = {}
        self.navigation_callbacks: list[Callable] = []
        self.logger = get_logger(__name__)

        # Page state
        self.page_state: dict[str, Any] = {}

        # Initialize default routes
        self._setup_default_routes()

    def _setup_default_routes(self):
        """Setup default page routes."""
        self.register_page("login", self._handle_login_page)
        self.register_page("register", self._handle_register_page)
        self.register_page("dashboard", self._handle_dashboard_page)
        self.register_page("chat", self._handle_chat_page)
        self.register_page("conversations", self._handle_conversations_page)
        self.register_page("assistants", self._handle_assistants_page)
        self.register_page("tools", self._handle_tools_page)
        self.register_page("knowledge", self._handle_knowledge_page)
        self.register_page("mcp", self._handle_mcp_page)
        self.register_page("settings", self._handle_settings_page)
        self.register_page("profile", self._handle_profile_page)

    def register_page(self, page_name: str, handler: Callable):
        """Register a page handler."""
        self.page_handlers[page_name] = handler

    def navigate_to(self, page_name: str, **kwargs):
        """Navigate to a specific page."""
        if page_name not in self.page_handlers:
            ui.notify(f"Page '{page_name}' not found", type="error")
            return
        # Store previous page
        self.previous_page = self.current_page
        # Update current page
        self.current_page = page_name
        # Store page state
        if kwargs:
            self.page_state[page_name] = kwargs
        # Clear current content
        self._clear_content()
        # Call page handler
        try:
            self.page_handlers[page_name](**kwargs)
        except Exception as e:
            self.logger.error(f"Error loading page {page_name}: {e}")
            if page_name != "login":
                self.navigate_to("login")
            else:
                ui.notify(f"Fehler beim Laden der Login-Seite: {str(e)}", type="error")
        # Notify navigation callbacks
        self._notify_navigation_callbacks(page_name)

    def go_back(self):
        """Navigate back to the previous page."""
        if self.previous_page:
            self.navigate_to(self.previous_page)
        else:
            self.navigate_to("dashboard")

    def get_current_page(self) -> str:
        """Get the current page name."""
        return self.current_page

    def get_page_state(self, page_name: str | None = None) -> dict[str, Any]:
        """Get state for a specific page or current page."""
        target_page = page_name or self.current_page
        return self.page_state.get(target_page, {})

    def set_page_state(self, page_name: str, state: dict[str, Any]):
        """Set state for a specific page."""
        self.page_state[page_name] = state

    def on_navigation(self, callback: Callable[[str], None]):
        """Register a navigation callback."""
        self.navigation_callbacks.append(callback)

    def _clear_content(self):
        """Clear the current page content."""
        # This would clear the main content area
        # Implementation depends on the layout structure

    def _notify_navigation_callbacks(self, page_name: str):
        """Notify all navigation callbacks."""
        for callback in self.navigation_callbacks:
            try:
                callback(page_name)
            except Exception as e:
                self.logger.error(f"Error in navigation callback: {e}")

    def _clear_app_container(self):
        """Remove and recreate the main app container for exclusive layouts (e.g. AuthLayout)."""
        # Remove the existing .app-container if present
        containers = ui.query(".app-container").all()
        for el in containers:
            el.delete()
        # Create a new app-container for the next layout
        ui.element("div").classes("app-container")

    def _handle_login_page(self, **kwargs):
        """Handle login page."""
        from components.auth.auth_form import AuthForm
        from components.layout.page_layout import AuthLayout

        self._clear_app_container()
        layout = AuthLayout()
        layout.create_layout()
        auth_form = AuthForm(form_type="login")
        auth_form.on_success = lambda: self.navigate_to("dashboard")
        with layout.main_content:
            auth_form.create_form()

    def _handle_register_page(self, **kwargs):
        """Handle register page."""
        from components.auth.auth_form import AuthForm
        from components.layout.page_layout import AuthLayout

        self._clear_app_container()
        layout = AuthLayout()
        layout.create_layout()
        auth_form = AuthForm(form_type="register")
        auth_form.on_success = lambda: self.navigate_to("login")
        with layout.main_content:
            auth_form.create_form()

    def _handle_dashboard_page(self, **kwargs):
        """Handle dashboard page."""
        from components.dashboard.dashboard_page import create_dashboard_page
        from components.layout.page_layout import PageLayout

        layout = PageLayout()
        layout.create_layout(page_title="Dashboard")

        # Add dashboard content
        with layout.main_content:
            create_dashboard_page()

    def _handle_chat_page(self, **kwargs):
        """Handle chat page."""
        from components.chat.chat_interface import create_chat_interface
        from components.layout.page_layout import PageLayout

        layout = PageLayout()
        layout.create_layout(page_title="Chat", show_sidebar=False)

        # Add chat interface
        with layout.main_content:
            create_chat_interface()

    def _handle_conversations_page(self, **kwargs):
        """Handle conversations page."""
        from components.layout.page_layout import PageLayout

        layout = PageLayout()
        layout.create_layout(page_title="Konversationen")

        # Add conversations content
        with layout.main_content:
            ui.html("<h2>Konversationen</h2>")
            ui.html("<p>Konversationsverlauf wird implementiert.</p>")

    def _handle_assistants_page(self, **kwargs):
        """Handle assistants page."""
        from components.layout.page_layout import PageLayout

        layout = PageLayout()
        layout.create_layout(page_title="Assistenten")

        # Add assistants content
        with layout.main_content:
            ui.html("<h2>Assistenten</h2>")
            ui.html("<p>Assistenten-Verwaltung wird implementiert.</p>")

    def _handle_tools_page(self, **kwargs):
        """Handle tools page."""
        from components.layout.page_layout import PageLayout

        layout = PageLayout()
        layout.create_layout(page_title="Tools")

        # Add tools content
        with layout.main_content:
            ui.html("<h2>Tools</h2>")
            ui.html("<p>Tool-Verwaltung wird implementiert.</p>")

    def _handle_knowledge_page(self, **kwargs):
        """Handle knowledge page."""
        from components.layout.page_layout import PageLayout

        layout = PageLayout()
        layout.create_layout(page_title="Wissensdatenbank")

        # Add knowledge content
        with layout.main_content:
            ui.html("<h2>Wissensdatenbank</h2>")
            ui.html("<p>Wissensdatenbank wird implementiert.</p>")

    def _handle_mcp_page(self, **kwargs):
        """Handle MCP tools page."""
        from components.layout.page_layout import PageLayout

        layout = PageLayout()
        layout.create_layout(page_title="MCP Tools")

        # Add MCP content
        with layout.main_content:
            ui.html("<h2>MCP Tools</h2>")
            ui.html("<p>MCP-Tool-Verwaltung wird implementiert.</p>")

    def _handle_settings_page(self, **kwargs):
        """Handle settings page."""
        from components.layout.page_layout import PageLayout

        layout = PageLayout()
        layout.create_layout(page_title="Einstellungen")

        # Add settings content
        with layout.main_content:
            ui.html("<h2>Einstellungen</h2>")
            ui.html("<p>Einstellungen werden implementiert.</p>")

    def _handle_profile_page(self, **kwargs):
        """Handle profile page."""
        from components.layout.page_layout import PageLayout

        layout = PageLayout()
        layout.create_layout(page_title="Profil")

        # Add profile content
        with layout.main_content:
            ui.html("<h2>Profil</h2>")
            ui.html("<p>Profil-Verwaltung wird implementiert.</p>")


# Global router instance
router = Router()
