"""
Advanced Settings Page for the AI Assistant Platform.

This module provides comprehensive settings functionality including
user preferences, account management, and admin features.
"""

from nicegui import ui
from typing import Optional, List, Dict, Any
from datetime import datetime
import asyncio

from services.user_service import user_service, UserProfile, UserPreferences, UserStats, UserRole, UserStatus
from components.common.loading_spinner import create_loading_spinner
from components.common.error_message import create_error_message
from components.user.profile_card import create_profile_card
from utils.helpers import format_timestamp, format_file_size
from utils.validators import validate_user_data


class AdvancedSettingsPage:
    """Advanced settings management page component."""
    
    def __init__(self):
        """Initialize the advanced settings page."""
        self.current_user: Optional[UserProfile] = None
        self.user_preferences: Optional[UserPreferences] = None
        self.user_stats: Optional[UserStats] = None
        self.is_loading = False
        self.error_message = None
        
        # UI components
        self.container = None
        self.profile_card = None
        self.settings_container = None
        self.admin_container = None
        
        # Create UI components
        self.create_settings_page()
        
        # Load user data after UI setup
        ui.timer(0.1, self.load_user_data, once=True)
    
    def create_settings_page(self):
        """Create the advanced settings page UI."""
        self.container = ui.element("div").classes("p-6")
        
        with self.container:
            # Header
            self.create_header()
            
            # Main content
            with ui.row().classes("space-x-6"):
                # Left sidebar - Profile
                with ui.column().classes("w-1/3"):
                    self.create_profile_section()
                
                # Right content - Settings
                with ui.column().classes("flex-1"):
                    self.create_settings_sections()
    
    def create_header(self):
        """Create the page header."""
        with ui.element("div").classes("mb-6"):
            with ui.row().classes("items-center justify-between"):
                with ui.column():
                    ui.label("Einstellungen").classes("text-2xl font-bold")
                    ui.label("Verwalte dein Profil und deine Einstellungen").classes("text-gray-600")
                
                with ui.row().classes("space-x-2"):
                    ui.button(
                        "Speichern",
                        icon="save",
                        on_click=self.save_all_settings
                    ).classes("bg-blue-600 text-white")
                    
                    ui.button(
                        "Zurücksetzen",
                        icon="refresh",
                        on_click=self.reset_settings
                    ).classes("bg-gray-500 text-white")
    
    def create_profile_section(self):
        """Create profile section."""
        with ui.element("div").classes("bg-white border rounded-lg p-6"):
            ui.label("Profil").classes("text-lg font-medium mb-4")
            
            # Profile card placeholder
            self.profile_placeholder = ui.element("div").classes("text-center py-8")
            with self.profile_placeholder:
                create_loading_spinner("Lade Profil...")
    
    def create_settings_sections(self):
        """Create settings sections."""
        self.settings_container = ui.element("div").classes("space-y-6")
        
        with self.settings_container:
            # Account settings
            self.create_account_settings()
            
            # Appearance settings
            self.create_appearance_settings()
            
            # Notification settings
            self.create_notification_settings()
            
            # Chat settings
            self.create_chat_settings()
            
            # Privacy settings
            self.create_privacy_settings()
            
            # Admin section (if admin)
            self.create_admin_section()
    
    def create_account_settings(self):
        """Create account settings section."""
        with ui.element("div").classes("bg-white border rounded-lg p-6"):
            ui.label("Account-Einstellungen").classes("text-lg font-medium mb-4")
            
            with ui.column().classes("space-y-4"):
                # Basic info
                with ui.row().classes("space-x-4"):
                    self.first_name_input = ui.input("Vorname").classes("flex-1")
                    self.last_name_input = ui.input("Nachname").classes("flex-1")
                
                self.username_input = ui.input("Benutzername").classes("w-full")
                self.email_input = ui.input("E-Mail").classes("w-full")
                
                # Bio
                self.bio_input = ui.textarea("Über mich").classes("w-full")
                
                # Location and website
                with ui.row().classes("space-x-4"):
                    self.location_input = ui.input("Standort").classes("flex-1")
                    self.website_input = ui.input("Website").classes("flex-1")
                
                # Password change button
                ui.button(
                    "Passwort ändern",
                    icon="lock",
                    on_click=self.show_password_change_dialog
                ).classes("bg-gray-500 text-white")
    
    def create_appearance_settings(self):
        """Create appearance settings section."""
        with ui.element("div").classes("bg-white border rounded-lg p-6"):
            ui.label("Erscheinungsbild").classes("text-lg font-medium mb-4")
            
            with ui.column().classes("space-y-4"):
                # Theme selection
                with ui.row().classes("items-center justify-between"):
                    ui.label("Theme").classes("font-medium")
                    self.theme_select = ui.select(
                        options=["light", "dark", "auto"],
                        value="light"
                    ).classes("w-48")
                
                # Font size
                with ui.row().classes("items-center justify-between"):
                    ui.label("Schriftgröße").classes("font-medium")
                    self.font_size_select = ui.select(
                        options=["small", "medium", "large"],
                        value="medium"
                    ).classes("w-48")
                
                # UI options
                self.compact_mode_switch = ui.switch("Kompakter Modus").classes("w-full")
                self.high_contrast_switch = ui.switch("Hoher Kontrast").classes("w-full")
                self.accessibility_mode_switch = ui.switch("Barrierefreiheit").classes("w-full")
    
    def create_notification_settings(self):
        """Create notification settings section."""
        with ui.element("div").classes("bg-white border rounded-lg p-6"):
            ui.label("Benachrichtigungen").classes("text-lg font-medium mb-4")
            
            with ui.column().classes("space-y-4"):
                # General notifications
                self.notifications_enabled_switch = ui.switch("Benachrichtigungen aktivieren").classes("w-full")
                
                # Email notifications
                self.email_notifications_switch = ui.switch("E-Mail-Benachrichtigungen").classes("w-full")
                
                # Push notifications
                self.push_notifications_switch = ui.switch("Push-Benachrichtigungen").classes("w-full")
                
                # Sound
                self.sound_enabled_switch = ui.switch("Sound aktivieren").classes("w-full")
    
    def create_chat_settings(self):
        """Create chat settings section."""
        with ui.element("div").classes("bg-white border rounded-lg p-6"):
            ui.label("Chat-Einstellungen").classes("text-lg font-medium mb-4")
            
            with ui.column().classes("space-y-4"):
                # Chat history limit
                with ui.row().classes("items-center justify-between"):
                    ui.label("Chat-Verlauf-Limit").classes("font-medium")
                    self.chat_history_limit_input = ui.number(
                        value=100,
                        min=10,
                        max=1000
                    ).classes("w-32")
                
                # Auto-save
                self.auto_save_switch = ui.switch("Auto-Save aktivieren").classes("w-full")
                
                # Default assistant
                with ui.row().classes("items-center justify-between"):
                    ui.label("Standard-Assistant").classes("font-medium")
                    self.default_assistant_select = ui.select(
                        options=["Keiner", "Assistant 1", "Assistant 2"],
                        value="Keiner"
                    ).classes("w-48")
    
    def create_privacy_settings(self):
        """Create privacy settings section."""
        with ui.element("div").classes("bg-white border rounded-lg p-6"):
            ui.label("Datenschutz").classes("text-lg font-medium mb-4")
            
            with ui.column().classes("space-y-4"):
                # Data export
                ui.button(
                    "Daten exportieren",
                    icon="download",
                    on_click=self.export_user_data
                ).classes("bg-green-500 text-white")
                
                # Account deletion
                ui.button(
                    "Account löschen",
                    icon="delete_forever",
                    on_click=self.show_delete_account_dialog
                ).classes("bg-red-500 text-white")
    
    def create_admin_section(self):
        """Create admin section (only for admins)."""
        if not user_service.is_admin():
            return
        
        self.admin_container = ui.element("div").classes("bg-red-50 border border-red-200 rounded-lg p-6")
        
        with self.admin_container:
            ui.label("Admin-Bereich").classes("text-lg font-medium text-red-800 mb-4")
            
            with ui.column().classes("space-y-4"):
                # User management
                ui.button(
                    "Benutzer verwalten",
                    icon="people",
                    on_click=self.show_user_management
                ).classes("bg-red-600 text-white")
                
                # System statistics
                ui.button(
                    "System-Statistiken",
                    icon="analytics",
                    on_click=self.show_system_stats
                ).classes("bg-red-600 text-white")
                
                # System settings
                ui.button(
                    "System-Einstellungen",
                    icon="settings",
                    on_click=self.show_system_settings
                ).classes("bg-red-600 text-white")
    
    async def load_user_data(self):
        """Load user data."""
        self.is_loading = True
        
        try:
            # Load current user
            self.current_user = await user_service.get_current_user(force_refresh=True)
            
            if self.current_user:
                # Load preferences
                self.user_preferences = await user_service.get_user_preferences()
                
                # Load stats
                self.user_stats = await user_service.get_user_stats()
                
                # Update UI
                self.update_profile_section()
                self.update_settings_values()
            else:
                self.error_message = "Benutzer konnte nicht geladen werden"
                self.display_error()
                
        except Exception as e:
            self.error_message = f"Fehler beim Laden der Benutzerdaten: {str(e)}"
            self.display_error()
        finally:
            self.is_loading = False
    
    def update_profile_section(self):
        """Update profile section with user data."""
        self.profile_placeholder.clear()
        
        with self.profile_placeholder:
            self.profile_card = create_profile_card(
                user=self.current_user,
                on_edit=self.edit_profile,
                on_avatar_upload=self.upload_avatar,
                on_password_change=self.change_password,
                on_preferences_update=self.update_preferences,
                show_admin_actions=user_service.is_admin()
            )
    
    def update_settings_values(self):
        """Update settings input values."""
        if not self.current_user:
            return
        
        # Account settings
        self.first_name_input.value = self.current_user.first_name
        self.last_name_input.value = self.current_user.last_name
        self.username_input.value = self.current_user.username
        self.email_input.value = self.current_user.email
        self.bio_input.value = self.current_user.bio or ""
        self.location_input.value = self.current_user.location or ""
        self.website_input.value = self.current_user.website or ""
        
        # Appearance settings
        if self.user_preferences:
            self.theme_select.value = self.user_preferences.theme
            self.font_size_select.value = self.user_preferences.font_size
            self.compact_mode_switch.value = self.user_preferences.ui_compact_mode
            self.high_contrast_switch.value = self.user_preferences.high_contrast
            self.accessibility_mode_switch.value = self.user_preferences.accessibility_mode
        
        # Notification settings
        if self.user_preferences:
            self.notifications_enabled_switch.value = self.user_preferences.notifications_enabled
            self.email_notifications_switch.value = self.user_preferences.email_notifications
            self.push_notifications_switch.value = self.user_preferences.push_notifications
            self.sound_enabled_switch.value = self.user_preferences.sound_enabled
        
        # Chat settings
        if self.user_preferences:
            self.chat_history_limit_input.value = self.user_preferences.chat_history_limit
            self.auto_save_switch.value = self.user_preferences.auto_save
            if self.user_preferences.default_assistant_id:
                self.default_assistant_select.value = self.user_preferences.default_assistant_id
    
    def display_error(self):
        """Display error message."""
        self.settings_container.clear()
        with self.settings_container:
            create_error_message(self.error_message)
    
    async def save_all_settings(self):
        """Save all settings."""
        try:
            # Save profile
            await self.save_profile()
            
            # Save preferences
            await self.save_preferences()
            
            ui.notify("Einstellungen erfolgreich gespeichert", type="positive")
            
        except Exception as e:
            ui.notify(f"Fehler beim Speichern: {str(e)}", type="error")
    
    async def save_profile(self):
        """Save profile changes."""
        if not self.current_user:
            return
        
        profile_data = {
            "first_name": self.first_name_input.value,
            "last_name": self.last_name_input.value,
            "username": self.username_input.value,
            "email": self.email_input.value,
            "bio": self.bio_input.value,
            "location": self.location_input.value,
            "website": self.website_input.value
        }
        
        updated_user = await user_service.update_profile(profile_data)
        if updated_user:
            self.current_user = updated_user
            self.update_profile_section()
    
    async def save_preferences(self):
        """Save preference changes."""
        if not self.user_preferences:
            return
        
        # Update preferences from UI
        self.user_preferences.theme = self.theme_select.value
        self.user_preferences.font_size = self.font_size_select.value
        self.user_preferences.ui_compact_mode = self.compact_mode_switch.value
        self.user_preferences.high_contrast = self.high_contrast_switch.value
        self.user_preferences.accessibility_mode = self.accessibility_mode_switch.value
        
        self.user_preferences.notifications_enabled = self.notifications_enabled_switch.value
        self.user_preferences.email_notifications = self.email_notifications_switch.value
        self.user_preferences.push_notifications = self.push_notifications_switch.value
        self.user_preferences.sound_enabled = self.sound_enabled_switch.value
        
        self.user_preferences.chat_history_limit = self.chat_history_limit_input.value
        self.user_preferences.auto_save = self.auto_save_switch.value
        
        success = await user_service.update_user_preferences(self.user_preferences)
        if not success:
            raise Exception("Fehler beim Speichern der Einstellungen")
    
    def reset_settings(self):
        """Reset settings to defaults."""
        self.update_settings_values()
        ui.notify("Einstellungen zurückgesetzt", type="info")
    
    async def edit_profile(self, user: UserProfile):
        """Edit profile."""
        # This would open a profile edit dialog
        ui.notify("Profil-Bearbeitung wird implementiert", type="info")
    
    async def upload_avatar(self, avatar_data: bytes, filename: str):
        """Upload avatar."""
        try:
            avatar_url = await user_service.upload_avatar(avatar_data, filename)
            if avatar_url:
                ui.notify("Avatar erfolgreich hochgeladen", type="positive")
                await self.load_user_data()
            else:
                ui.notify("Fehler beim Hochladen des Avatars", type="error")
        except Exception as e:
            ui.notify(f"Fehler beim Hochladen: {str(e)}", type="error")
    
    async def change_password(self, current_password: str, new_password: str):
        """Change password."""
        try:
            success = await user_service.change_password(current_password, new_password)
            if success:
                ui.notify("Passwort erfolgreich geändert", type="positive")
            else:
                ui.notify("Fehler beim Ändern des Passworts", type="error")
        except Exception as e:
            ui.notify(f"Fehler beim Ändern: {str(e)}", type="error")
    
    async def update_preferences(self, preferences: UserPreferences):
        """Update preferences."""
        try:
            success = await user_service.update_user_preferences(preferences)
            if success:
                self.user_preferences = preferences
                ui.notify("Einstellungen aktualisiert", type="positive")
            else:
                ui.notify("Fehler beim Aktualisieren der Einstellungen", type="error")
        except Exception as e:
            ui.notify(f"Fehler beim Aktualisieren: {str(e)}", type="error")
    
    def show_password_change_dialog(self):
        """Show password change dialog."""
        with ui.dialog() as dialog, ui.card().classes("w-96"):
            ui.label("Passwort ändern").classes("text-lg font-medium mb-4")
            
            with ui.column().classes("space-y-4"):
                current_password = ui.input("Aktuelles Passwort", password=True).classes("w-full")
                new_password = ui.input("Neues Passwort", password=True).classes("w-full")
                confirm_password = ui.input("Passwort bestätigen", password=True).classes("w-full")
                
                with ui.row().classes("justify-end space-x-2"):
                    ui.button("Abbrechen", on_click=dialog.close).classes("bg-gray-500 text-white")
                    ui.button(
                        "Ändern",
                        on_click=lambda: self.handle_password_change(
                            current_password.value,
                            new_password.value,
                            confirm_password.value,
                            dialog
                        )
                    ).classes("bg-blue-600 text-white")
    
    async def handle_password_change(self, current: str, new: str, confirm: str, dialog):
        """Handle password change."""
        if new != confirm:
            ui.notify("Passwörter stimmen nicht überein", type="error")
            return
        
        await self.change_password(current, new)
        dialog.close()
    
    def export_user_data(self):
        """Export user data."""
        ui.notify("Datenexport wird implementiert", type="info")
    
    def show_delete_account_dialog(self):
        """Show delete account dialog."""
        with ui.dialog() as dialog, ui.card().classes("w-96"):
            ui.label("Account löschen").classes("text-lg font-medium mb-4")
            
            ui.label("Diese Aktion kann nicht rückgängig gemacht werden. Alle Daten werden permanent gelöscht.").classes("text-red-600 mb-4")
            
            with ui.column().classes("space-y-4"):
                confirm_text = ui.input("Geben Sie 'LÖSCHEN' ein, um zu bestätigen").classes("w-full")
                
                with ui.row().classes("justify-end space-x-2"):
                    ui.button("Abbrechen", on_click=dialog.close).classes("bg-gray-500 text-white")
                    ui.button(
                        "Account löschen",
                        on_click=lambda: self.handle_delete_account(confirm_text.value, dialog)
                    ).classes("bg-red-600 text-white")
    
    def handle_delete_account(self, confirm_text: str, dialog):
        """Handle account deletion."""
        if confirm_text != "LÖSCHEN":
            ui.notify("Bitte geben Sie 'LÖSCHEN' ein, um zu bestätigen", type="error")
            return
        
        ui.notify("Account-Löschung wird implementiert", type="info")
        dialog.close()
    
    def show_user_management(self):
        """Show user management."""
        ui.notify("Benutzer-Verwaltung wird implementiert", type="info")
    
    def show_system_stats(self):
        """Show system statistics."""
        ui.notify("System-Statistiken werden implementiert", type="info")
    
    def show_system_settings(self):
        """Show system settings."""
        ui.notify("System-Einstellungen werden implementiert", type="info")


# Global advanced settings page instance
advanced_settings_page = AdvancedSettingsPage()

SettingsPage = AdvancedSettingsPage

def create_page():
    """Create and return a settings page instance."""
    return AdvancedSettingsPage() 