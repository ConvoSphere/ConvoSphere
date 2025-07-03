"""
Registration page for the AI Assistant Platform.

This module provides a user registration interface with form validation
and error handling.
"""

import asyncio
from typing import Optional
from nicegui import ui

from services.auth_service import auth_service
from services.api import api_client


class RegisterPage:
    """Registration page component."""
    
    def __init__(self):
        """Initialize the registration page."""
        self.email = ""
        self.username = ""
        self.password = ""
        self.confirm_password = ""
        self.is_loading = False
        self.error_message = ""
        
        self.create_register_page()
    
    def create_register_page(self):
        """Create the registration page layout."""
        # Center the registration form
        with ui.element("div").classes("min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 to-emerald-100"):
            with ui.card().classes("w-full max-w-md p-8 shadow-xl"):
                # Header
                with ui.element("div").classes("text-center mb-8"):
                    ui.html("<h1 style='font-size: 28px; font-weight: 700; color: #1f2937; margin-bottom: 8px;'>Konto erstellen</h1>")
                    ui.html("<p style='color: #6b7280; font-size: 16px;'>Erstelle dein neues Konto</p>")
                
                # Registration form
                with ui.element("form").classes("space-y-6"):
                    # Username input
                    with ui.element("div"):
                        ui.label("Benutzername").classes("block text-sm font-medium text-gray-700 mb-2")
                        self.username_input = ui.input(
                            placeholder="dein_benutzername",
                            on_change=self.on_username_change
                        ).classes("w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent")
                    
                    # Email input
                    with ui.element("div"):
                        ui.label("E-Mail-Adresse").classes("block text-sm font-medium text-gray-700 mb-2")
                        self.email_input = ui.input(
                            placeholder="deine@email.com",
                            on_change=self.on_email_change
                        ).classes("w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent")
                    
                    # Password input
                    with ui.element("div"):
                        ui.label("Passwort").classes("block text-sm font-medium text-gray-700 mb-2")
                        self.password_input = ui.input(
                            placeholder="Mindestens 8 Zeichen",
                            password=True,
                            on_change=self.on_password_change
                        ).classes("w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent")
                    
                    # Confirm password input
                    with ui.element("div"):
                        ui.label("Passwort bestätigen").classes("block text-sm font-medium text-gray-700 mb-2")
                        self.confirm_password_input = ui.input(
                            placeholder="Passwort wiederholen",
                            password=True,
                            on_change=self.on_confirm_password_change
                        ).classes("w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent")
                    
                    # Terms and conditions
                    with ui.element("div").classes("flex items-start"):
                        self.terms_checkbox = ui.checkbox("Ich akzeptiere die Nutzungsbedingungen").classes("text-sm text-gray-600")
                    
                    # Error message
                    self.error_label = ui.label("").classes("text-red-600 text-sm hidden")
                    
                    # Register button
                    self.register_button = ui.button(
                        "Konto erstellen",
                        on_click=self.handle_register
                    ).classes("w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition-colors")
                    
                    # Loading spinner
                    self.loading_spinner = ui.spinner("dots").classes("hidden")
                
                # Divider
                with ui.element("div").classes("my-6"):
                    with ui.element("div").classes("relative"):
                        with ui.element("div").classes("absolute inset-0 flex items-center"):
                            ui.element("div").classes("w-full border-t border-gray-300")
                        with ui.element("div").classes("relative flex justify-center text-sm"):
                            ui.label("oder").classes("px-2 bg-white text-gray-500")
                
                # Login link
                with ui.element("div").classes("text-center"):
                    ui.html("<span style='color: #6b7280;'>Bereits ein Konto? </span>")
                    ui.link("Jetzt anmelden", "#login").classes("text-green-600 hover:text-green-500 font-medium")
    
    def on_username_change(self, e):
        """Handle username input change."""
        self.username = e.value
        self.clear_error()
    
    def on_email_change(self, e):
        """Handle email input change."""
        self.email = e.value
        self.clear_error()
    
    def on_password_change(self, e):
        """Handle password input change."""
        self.password = e.value
        self.clear_error()
    
    def on_confirm_password_change(self, e):
        """Handle confirm password input change."""
        self.confirm_password = e.value
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
            self.register_button.classes("hidden")
            self.loading_spinner.classes("flex justify-center")
            self.username_input.disable()
            self.email_input.disable()
            self.password_input.disable()
            self.confirm_password_input.disable()
        else:
            self.register_button.classes("w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition-colors")
            self.loading_spinner.classes("hidden")
            self.username_input.enable()
            self.email_input.enable()
            self.password_input.enable()
            self.confirm_password_input.enable()
    
    def validate_form(self) -> bool:
        """Validate registration form."""
        # Check required fields
        if not self.username:
            self.show_error("Benutzername ist erforderlich")
            return False
        
        if not self.email:
            self.show_error("E-Mail-Adresse ist erforderlich")
            return False
        
        if not self.password:
            self.show_error("Passwort ist erforderlich")
            return False
        
        if not self.confirm_password:
            self.show_error("Passwort-Bestätigung ist erforderlich")
            return False
        
        # Validate email format
        if "@" not in self.email or "." not in self.email:
            self.show_error("Bitte gib eine gültige E-Mail-Adresse ein")
            return False
        
        # Validate password length
        if len(self.password) < 8:
            self.show_error("Passwort muss mindestens 8 Zeichen lang sein")
            return False
        
        # Validate password match
        if self.password != self.confirm_password:
            self.show_error("Passwörter stimmen nicht überein")
            return False
        
        # Validate username format
        if len(self.username) < 3:
            self.show_error("Benutzername muss mindestens 3 Zeichen lang sein")
            return False
        
        # Check terms acceptance
        if not self.terms_checkbox.value:
            self.show_error("Bitte akzeptiere die Nutzungsbedingungen")
            return False
        
        return True
    
    async def handle_register(self):
        """Handle registration form submission."""
        # Validate form
        if not self.validate_form():
            return
        
        # Set loading state
        self.set_loading(True)
        
        try:
            # Attempt registration
            success = await auth_service.register({
                "username": self.username,
                "email": self.email,
                "password": self.password
            })
            
            if success:
                # Show success and redirect to login
                ui.notify("Konto erfolgreich erstellt!", type="positive")
                await asyncio.sleep(2)
                # TODO: Navigate to login page
                ui.notify("Weiterleitung zur Anmeldung...", type="info")
            else:
                self.show_error("Registrierung fehlgeschlagen. Bitte versuche es erneut.")
                
        except Exception as e:
            self.show_error(f"Registrierung fehlgeschlagen: {str(e)}")
            
        finally:
            self.set_loading(False)


# Create page instance
register_page = RegisterPage()


def create_page():
    """Create and return the registration page."""
    return register_page 