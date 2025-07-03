"""
User profile page for the AI Assistant Platform.

This module provides user profile management and settings.
"""

import asyncio
from typing import Optional, Dict, Any
from nicegui import ui

from services.auth_service import auth_service
from services.api import api_client


class ProfilePage:
    """User profile page component."""
    
    def __init__(self):
        """Initialize the profile page."""
        self.user_data = {
            "username": "",
            "email": "",
            "first_name": "",
            "last_name": "",
            "bio": "",
            "language": "de",
            "theme": "light"
        }
        self.is_loading = False
        self.is_saving = False
        self.error_message = ""
        self.success_message = ""
        
        self.create_profile_page()
        # self.load_user_data()
    
    def create_profile_page(self):
        """Create the profile page layout."""
        with ui.element("div").classes("w-full max-w-4xl mx-auto p-6"):
            # Header
            with ui.element("div").classes("mb-8"):
                ui.html("<h1 style='font-size: 32px; font-weight: 700; color: #1f2937; margin-bottom: 8px;'>Profil bearbeiten</h1>")
                ui.html("<p style='color: #6b7280; font-size: 16px;'>Verwalte deine persönlichen Einstellungen</p>")
            
            # Profile form
            with ui.element("div").classes("grid grid-cols-1 lg:grid-cols-3 gap-8"):
                # Main profile section
                with ui.element("div").classes("lg:col-span-2"):
                    with ui.card().classes("p-6"):
                        ui.html("<h2 style='font-size: 20px; font-weight: 600; color: #1f2937; margin-bottom: 6px;'>Persönliche Informationen</h2>")
                        ui.html("<p style='color: #6b7280; font-size: 14px; margin-bottom: 24px;'>Aktualisiere deine persönlichen Daten</p>")
                        
                        # Username
                        with ui.element("div").classes("mb-4"):
                            ui.label("Benutzername").classes("block text-sm font-medium text-gray-700 mb-2")
                            self.username_input = ui.input(
                                placeholder="dein_benutzername",
                                on_change=self.on_username_change
                            ).classes("w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent")
                        
                        # Email
                        with ui.element("div").classes("mb-4"):
                            ui.label("E-Mail-Adresse").classes("block text-sm font-medium text-gray-700 mb-2")
                            self.email_input = ui.input(
                                placeholder="deine@email.com",
                                on_change=self.on_email_change
                            ).classes("w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent")
                        
                        # First and Last Name
                        with ui.row().classes("gap-4"):
                            with ui.element("div").classes("flex-1"):
                                ui.label("Vorname").classes("block text-sm font-medium text-gray-700 mb-2")
                                self.first_name_input = ui.input(
                                    placeholder="Max",
                                    on_change=self.on_first_name_change
                                ).classes("w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent")
                            
                            with ui.element("div").classes("flex-1"):
                                ui.label("Nachname").classes("block text-sm font-medium text-gray-700 mb-2")
                                self.last_name_input = ui.input(
                                    placeholder="Mustermann",
                                    on_change=self.on_last_name_change
                                ).classes("w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent")
                        
                        # Bio
                        with ui.element("div").classes("mb-6"):
                            ui.label("Über mich").classes("block text-sm font-medium text-gray-700 mb-2")
                            self.bio_input = ui.textarea(
                                placeholder="Erzähle etwas über dich...",
                                on_change=self.on_bio_change
                            ).classes("w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent")
                        
                        # Save button
                        self.save_button = ui.button(
                            "Änderungen speichern",
                            on_click=self.save_profile
                        ).classes("bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors")
                        
                        # Loading spinner
                        self.loading_spinner = ui.spinner("dots").classes("hidden")
                
                # Settings sidebar
                with ui.element("div"):
                    with ui.card().classes("p-6"):
                        ui.html("<h2 style='font-size: 20px; font-weight: 600; color: #1f2937; margin-bottom: 6px;'>Einstellungen</h2>")
                        ui.html("<p style='color: #6b7280; font-size: 14px; margin-bottom: 24px;'>Anpassen der Anwendung</p>")
                        
                        # Language selection
                        with ui.element("div").classes("mb-6"):
                            ui.label("Sprache").classes("block text-sm font-medium text-gray-700 mb-2")
                            self.language_select = ui.select(
                                options=[
                                    ("de", "Deutsch"),
                                    ("en", "English")
                                ],
                                on_change=self.on_language_change
                            ).classes("w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent")
                        
                        # Theme selection
                        with ui.element("div").classes("mb-6"):
                            ui.label("Design").classes("block text-sm font-medium text-gray-700 mb-2")
                            self.theme_select = ui.select(
                                options=[
                                    ("light", "Hell"),
                                    ("dark", "Dunkel"),
                                    ("auto", "Automatisch")
                                ],
                                on_change=self.on_theme_change
                            ).classes("w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent")
                        
                        # Notifications
                        with ui.element("div").classes("mb-6"):
                            ui.label("Benachrichtigungen").classes("block text-sm font-medium text-gray-700 mb-2")
                            self.email_notifications = ui.checkbox("E-Mail-Benachrichtigungen").classes("text-sm text-gray-600 mb-2")
                            self.push_notifications = ui.checkbox("Push-Benachrichtigungen").classes("text-sm text-gray-600")
                        
                        # Danger zone
                        with ui.element("div").classes("border-t border-gray-200 pt-6"):
                            ui.html("<h3 style='font-size: 16px; font-weight: 600; color: #dc2626; margin-bottom: 12px;'>Gefahrenbereich</h3>")
                            
                            ui.button(
                                "Passwort ändern",
                                on_click=self.change_password
                            ).classes("w-full bg-gray-100 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors mb-2")
                            
                            ui.button(
                                "Konto löschen",
                                on_click=self.delete_account
                            ).classes("w-full bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-colors")
            
            # Messages
            self.error_label = ui.label("").classes("text-red-600 text-sm hidden mt-4")
            self.success_label = ui.label("").classes("text-green-600 text-sm hidden mt-4")
    
    def on_username_change(self, e):
        """Handle username input change."""
        self.user_data["username"] = e.value
        self.clear_messages()
    
    def on_email_change(self, e):
        """Handle email input change."""
        self.user_data["email"] = e.value
        self.clear_messages()
    
    def on_first_name_change(self, e):
        """Handle first name input change."""
        self.user_data["first_name"] = e.value
        self.clear_messages()
    
    def on_last_name_change(self, e):
        """Handle last name input change."""
        self.user_data["last_name"] = e.value
        self.clear_messages()
    
    def on_bio_change(self, e):
        """Handle bio input change."""
        self.user_data["bio"] = e.value
        self.clear_messages()
    
    def on_language_change(self, e):
        """Handle language selection change."""
        self.user_data["language"] = e.value
        self.clear_messages()
    
    def on_theme_change(self, e):
        """Handle theme selection change."""
        self.user_data["theme"] = e.value
        self.clear_messages()
    
    def clear_messages(self):
        """Clear error and success messages."""
        self.error_message = ""
        self.success_message = ""
        self.error_label.text = ""
        self.success_label.text = ""
        self.error_label.classes("hidden")
        self.success_label.classes("hidden")
    
    def show_error(self, message: str):
        """Show error message."""
        self.error_message = message
        self.error_label.text = message
        self.error_label.classes("text-red-600 text-sm")
    
    def show_success(self, message: str):
        """Show success message."""
        self.success_message = message
        self.success_label.text = message
        self.success_label.classes("text-green-600 text-sm")
    
    def set_loading(self, loading: bool):
        """Set loading state."""
        self.is_loading = loading
        if loading:
            self.save_button.classes("hidden")
            self.loading_spinner.classes("flex justify-center")
        else:
            self.save_button.classes("bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors")
            self.loading_spinner.classes("hidden")
    
    async def load_user_data(self):
        """Load user data from API."""
        self.set_loading(True)
        
        try:
            # Get current user data
            response = await api_client.get_current_user()
            
            if response.success and response.data:
                self.user_data.update(response.data)
                self.update_form_fields()
            else:
                self.show_error("Fehler beim Laden der Benutzerdaten")
                
        except Exception as e:
            self.show_error(f"Fehler beim Laden der Daten: {str(e)}")
            
        finally:
            self.set_loading(False)
    
    def update_form_fields(self):
        """Update form fields with user data."""
        self.username_input.value = self.user_data.get("username", "")
        self.email_input.value = self.user_data.get("email", "")
        self.first_name_input.value = self.user_data.get("first_name", "")
        self.last_name_input.value = self.user_data.get("last_name", "")
        self.bio_input.value = self.user_data.get("bio", "")
        self.language_select.value = self.user_data.get("language", "de")
        self.theme_select.value = self.user_data.get("theme", "light")
    
    async def save_profile(self):
        """Save profile changes."""
        self.set_loading(True)
        
        try:
            # Update user data
            response = await api_client.update_user_profile(self.user_data)
            
            if response.success:
                self.show_success("Profil erfolgreich aktualisiert!")
            else:
                self.show_error("Fehler beim Speichern der Änderungen")
                
        except Exception as e:
            self.show_error(f"Fehler beim Speichern: {str(e)}")
            
        finally:
            self.set_loading(False)
    
    def change_password(self):
        """Open password change dialog."""
        # TODO: Implement password change dialog
        ui.notify("Passwort-Änderung wird implementiert...", type="info")
    
    def delete_account(self):
        """Open account deletion dialog."""
        # TODO: Implement account deletion dialog
        ui.notify("Konto-Löschung wird implementiert...", type="warning")


# Create page instance
profile_page = ProfilePage()


def create_page():
    """Create and return the profile page."""
    return profile_page 