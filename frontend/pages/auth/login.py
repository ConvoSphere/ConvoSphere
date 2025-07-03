"""
Login page for the AI Assistant Platform.

This module provides a modern login interface with form validation
and error handling.
"""

import asyncio
from typing import Optional
from nicegui import ui

from services.auth_service import auth_service
from services.api import api_client


class LoginPage:
    """Login page component."""
    
    def __init__(self):
        """Initialize the login page."""
        self.email = ""
        self.password = ""
        self.is_loading = False
        self.error_message = ""
        
        self.create_login_page()
    
    def create_login_page(self):
        """Create the login page layout."""
        # Center the login form
        with ui.element("div").classes("min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100"):
            with ui.card().classes("w-full max-w-md p-8 shadow-xl"):
                # Header
                with ui.element("div").classes("text-center mb-8"):
                    ui.html("<h1 style='font-size: 28px; font-weight: 700; color: #1f2937; margin-bottom: 8px;'>Willkommen zurück</h1>")
                    ui.html("<p style='color: #6b7280; font-size: 16px;'>Melde dich in deinem Konto an</p>")
                
                # Login form
                with ui.element("form").classes("space-y-6"):
                    # Email input
                    with ui.element("div"):
                        ui.label("E-Mail-Adresse").classes("block text-sm font-medium text-gray-700 mb-2")
                        self.email_input = ui.input(
                            placeholder="deine@email.com",
                            on_change=self.on_email_change
                        ).classes("w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent")
                    
                    # Password input
                    with ui.element("div"):
                        ui.label("Passwort").classes("block text-sm font-medium text-gray-700 mb-2")
                        self.password_input = ui.input(
                            placeholder="Dein Passwort",
                            password=True,
                            on_change=self.on_password_change
                        ).classes("w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent")
                    
                    # Remember me and forgot password
                    with ui.row().classes("flex items-center justify-between"):
                        ui.checkbox("Angemeldet bleiben").classes("text-sm text-gray-600")
                        ui.link("Passwort vergessen?", "#").classes("text-sm text-blue-600 hover:text-blue-500")
                    
                    # Error message
                    self.error_label = ui.label("").classes("text-red-600 text-sm hidden")
                    
                    # Login button
                    self.login_button = ui.button(
                        "Anmelden",
                        on_click=self.handle_login
                    ).classes("w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors")
                    
                    # Loading spinner
                    self.loading_spinner = ui.spinner("dots").classes("hidden")
                
                # Divider
                with ui.element("div").classes("my-6"):
                    with ui.element("div").classes("relative"):
                        with ui.element("div").classes("absolute inset-0 flex items-center"):
                            ui.element("div").classes("w-full border-t border-gray-300")
                        with ui.element("div").classes("relative flex justify-center text-sm"):
                            ui.label("oder").classes("px-2 bg-white text-gray-500")
                
                # Register link
                with ui.element("div").classes("text-center"):
                    ui.html("<span style='color: #6b7280;'>Noch kein Konto? </span>")
                    ui.link("Jetzt registrieren", "#register").classes("text-blue-600 hover:text-blue-500 font-medium")
    
    def on_email_change(self, e):
        """Handle email input change."""
        self.email = e.value
        self.clear_error()
    
    def on_password_change(self, e):
        """Handle password input change."""
        self.password = e.value
        self.clear_error()
    
    def clear_error(self):
        """Clear error message."""
        self.error_message = ""
        self.error_label.text = ""
        self.error_label.classes("hidden")
    
    def show_error(self, message: str):
        """Show error message."""
        self.error_message = message
        self.error_label.text = message
        self.error_label.classes("text-red-600 text-sm")
    
    def set_loading(self, loading: bool):
        """Set loading state."""
        self.is_loading = loading
        if loading:
            self.login_button.classes("hidden")
            self.loading_spinner.classes("flex justify-center")
            self.email_input.disable()
            self.password_input.disable()
        else:
            self.login_button.classes("w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors")
            self.loading_spinner.classes("hidden")
            self.email_input.enable()
            self.password_input.enable()
    
    async def handle_login(self):
        """Handle login form submission."""
        # Validate inputs
        if not self.email:
            self.show_error("E-Mail-Adresse ist erforderlich")
            return
        
        if not self.password:
            self.show_error("Passwort ist erforderlich")
            return
        
        # Validate email format
        if "@" not in self.email or "." not in self.email:
            self.show_error("Bitte gib eine gültige E-Mail-Adresse ein")
            return
        
        # Set loading state
        self.set_loading(True)
        
        try:
            # Attempt login
            success = await auth_service.login(self.email, self.password)
            
            if success:
                # Show success message
                ui.notify("Erfolgreich angemeldet!", type="positive")
                await asyncio.sleep(1)
                
                # Reload the application to show authenticated layout
                ui.refresh()
            else:
                self.show_error("Ungültige E-Mail oder Passwort")
                
        except Exception as e:
            self.show_error(f"Anmeldung fehlgeschlagen: {str(e)}")
            
        finally:
            self.set_loading(False)


# Create page instance
login_page = LoginPage()


def create_page():
    """Create and return the login page."""
    return login_page 