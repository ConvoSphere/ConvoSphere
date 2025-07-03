"""
Page layout component for consistent UI structure.

This module provides reusable layout components for pages
with header, sidebar, and main content areas.
"""

from typing import Optional, Callable
from nicegui import ui

from components.header import create_header
from components.sidebar import create_sidebar


class PageLayout:
    """Reusable page layout component."""
    
    def __init__(self):
        """Initialize the page layout."""
        self.header = None
        self.sidebar = None
        self.main_content = None
        self.footer = None
        
        # Layout state
        self.sidebar_collapsed = False
        self.current_page = ""
        
        # Callbacks
        self.on_sidebar_toggle: Optional[Callable] = None
        self.on_navigation: Optional[Callable] = None
    
    def create_layout(self, page_title: str = "", show_sidebar: bool = True) -> ui.element:
        """
        Create the main page layout.
        
        Args:
            page_title: Title for the page
            show_sidebar: Whether to show the sidebar
            
        Returns:
            ui.element: The main layout container
        """
        with ui.element("div").classes("min-h-screen bg-gray-50 dark:bg-gray-900") as layout:
            # Header
            self.header = self._create_header(page_title)
            
            # Main content area
            with ui.element("div").classes("flex"):
                # Sidebar
                if show_sidebar:
                    self.sidebar = self._create_sidebar()
                
                # Main content
                self.main_content = self._create_main_content()
            
            # Footer
            self.footer = self._create_footer()
        
        return layout
    
    def _create_header(self, page_title: str) -> ui.element:
        """Create the page header."""
        return create_header(
            title=page_title,
            on_sidebar_toggle=self._handle_sidebar_toggle,
            on_theme_toggle=self._handle_theme_toggle
        )
    
    def _create_sidebar(self) -> ui.element:
        """Create the sidebar navigation."""
        return create_sidebar(
            collapsed=self.sidebar_collapsed,
            current_page=self.current_page,
            on_navigation=self._handle_navigation
        )
    
    def _create_main_content(self) -> ui.element:
        """Create the main content area."""
        sidebar_class = "ml-64" if not self.sidebar_collapsed else "ml-16"
        
        with ui.element("main").classes(f"flex-1 {sidebar_class} transition-all duration-300") as main:
            with ui.element("div").classes("p-6"):
                # Content will be added here by child components
                pass
        
        return main
    
    def _create_footer(self) -> ui.element:
        """Create the page footer."""
        with ui.element("footer").classes("bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700") as footer:
            with ui.element("div").classes("max-w-7xl mx-auto py-4 px-6"):
                with ui.element("div").classes("flex justify-between items-center"):
                    with ui.element("div").classes("text-sm text-gray-500 dark:text-gray-400"):
                        ui.html("© 2024 ConvoSphere. Alle Rechte vorbehalten.")
                    
                    with ui.element("div").classes("flex space-x-6"):
                        ui.link("Datenschutz", "#privacy").classes("text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200")
                        ui.link("Impressum", "#imprint").classes("text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200")
                        ui.link("Hilfe", "#help").classes("text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200")
        
        return footer
    
    def _handle_sidebar_toggle(self):
        """Handle sidebar toggle."""
        self.sidebar_collapsed = not self.sidebar_collapsed
        
        # Update sidebar state
        if self.sidebar:
            # Update sidebar classes
            pass
        
        # Update main content margin
        if self.main_content:
            if self.sidebar_collapsed:
                self.main_content.classes("ml-16")
            else:
                self.main_content.classes("ml-64")
        
        # Call callback if provided
        if self.on_sidebar_toggle:
            self.on_sidebar_toggle(self.sidebar_collapsed)
    
    def _handle_theme_toggle(self):
        """Handle theme toggle."""
        # Theme toggle is handled by the header component
        pass
    
    def _handle_navigation(self, page: str):
        """Handle navigation to a new page."""
        self.current_page = page
        
        # Call callback if provided
        if self.on_navigation:
            self.on_navigation(page)
    
    def set_page_title(self, title: str):
        """Set the page title."""
        if self.header:
            # Update header title
            pass
    
    def add_content(self, content: ui.element):
        """Add content to the main content area."""
        if self.main_content:
            # Find the content container and add the content
            pass
    
    def show_loading(self, show: bool = True):
        """Show or hide loading state."""
        if show:
            with self.main_content:
                ui.spinner("dots").classes("flex justify-center items-center h-64")
        else:
            # Remove loading spinner
            pass
    
    def show_error(self, message: str):
        """Show error message in main content."""
        with self.main_content:
            with ui.element("div").classes("bg-red-50 border border-red-200 rounded-md p-4"):
                with ui.element("div").classes("flex"):
                    with ui.element("div").classes("flex-shrink-0"):
                        ui.icon("error").classes("h-5 w-5 text-red-400")
                    with ui.element("div").classes("ml-3"):
                        ui.html(f"<p class='text-sm text-red-800'>{message}</p>")


class AuthLayout:
    """Layout for authentication pages (login/register)."""
    
    def __init__(self):
        """Initialize the auth layout."""
        self.header = None
        self.main_content = None
    
    def create_layout(self) -> ui.element:
        """Create the authentication page layout."""
        with ui.element("div").classes("min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800") as layout:
            # Simple header
            self.header = self._create_header()
            
            # Main content
            self.main_content = self._create_main_content()
        
        return layout
    
    def _create_header(self) -> ui.element:
        """Create a simple header for auth pages."""
        with ui.element("header").classes("bg-white dark:bg-gray-800 shadow-sm") as header:
            with ui.element("div").classes("max-w-7xl mx-auto px-4 sm:px-6 lg:px-8"):
                with ui.element("div").classes("flex justify-between items-center py-4"):
                    # Logo
                    with ui.element("div").classes("flex items-center"):
                        ui.html("<h1 style='font-size: 24px; font-weight: 700; color: var(--color-text);'>ConvoSphere</h1>")
                    
                    # Theme toggle
                    ui.button(
                        icon="dark_mode",
                        on_click=self._handle_theme_toggle
                    ).classes("p-2 rounded-md text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200")
        
        return header
    
    def _create_main_content(self) -> ui.element:
        """Create the main content area for auth pages."""
        with ui.element("main").classes("flex-1 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8") as main:
            # Content will be added here by auth forms
            pass
        
        return main
    
    def _handle_theme_toggle(self):
        """Handle theme toggle."""
        # Theme toggle is handled by the theme manager
        pass
    
    def add_content(self, content: ui.element):
        """Add content to the main content area."""
        if self.main_content:
            # Add content to the main container
            pass 