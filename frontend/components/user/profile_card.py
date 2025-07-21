"""
Advanced profile card component for the AI Assistant Platform.

This module provides comprehensive user profile display and editing functionality
including avatar management, statistics, and settings.
"""

from collections.abc import Callable

from nicegui import ui
from services.user_service import (
    UserPreferences,
    UserProfile,
    UserRole,
    UserStats,
    UserStatus,
)
from utils.helpers import format_file_size, format_relative_time, format_timestamp


class ProfileCard:
    """Advanced profile card component."""

    def __init__(
        self,
        user: UserProfile,
        on_edit: Callable[[UserProfile], None] | None = None,
        on_avatar_upload: Callable[[bytes, str], None] | None = None,
        on_password_change: Callable[[str, str], None] | None = None,
        on_preferences_update: Callable[[UserPreferences], None] | None = None,
        show_admin_actions: bool = False,
    ):
        """
        Initialize profile card.

        Args:
            user: User profile to display
            on_edit: Edit callback
            on_avatar_upload: Avatar upload callback
            on_password_change: Password change callback
            on_preferences_update: Preferences update callback
            show_admin_actions: Show admin actions
        """
        self.user = user
        self.on_edit = on_edit
        self.on_avatar_upload = on_avatar_upload
        self.on_password_change = on_password_change
        self.on_preferences_update = on_preferences_update
        self.show_admin_actions = show_admin_actions

        # UI components
        self.container = None
        self.avatar_container = None
        self.stats_container = None

        self.create_profile_card()

    def create_profile_card(self):
        """Create the profile card UI."""
        self.container = ui.element("div").classes(
            "bg-white border rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow",
        )

        with self.container:
            # Header with avatar and basic info
            self.create_header()

            # User statistics
            self.create_statistics()

            # Profile details
            self.create_profile_details()

            # Actions
            self.create_actions()

    def create_header(self):
        """Create profile header with avatar and basic info."""
        with ui.row().classes("items-start space-x-6 mb-6"):
            # Avatar section
            self.create_avatar_section()

            # Basic info
            with ui.column().classes("flex-1"):
                with ui.row().classes("items-center space-x-4 mb-2"):
                    ui.label(f"{self.user.first_name} {self.user.last_name}").classes(
                        "text-2xl font-bold",
                    )

                    # Role badge
                    role_config = {
                        UserRole.ADMIN: {
                            "color": "bg-red-100 text-red-800",
                            "text": "Admin",
                        },
                        UserRole.MODERATOR: {
                            "color": "bg-orange-100 text-orange-800",
                            "text": "Moderator",
                        },
                        UserRole.USER: {
                            "color": "bg-blue-100 text-blue-800",
                            "text": "User",
                        },
                    }

                    config = role_config.get(self.user.role, role_config[UserRole.USER])
                    ui.label(config["text"]).classes(
                        f"px-3 py-1 rounded-full text-xs font-medium {config['color']}",
                    )

                # Username and email
                ui.label(f"@{self.user.username}").classes("text-lg text-gray-600")
                ui.label(self.user.email).classes("text-gray-500")

                # Status
                status_config = {
                    UserStatus.ACTIVE: {
                        "color": "text-green-600",
                        "icon": "check_circle",
                        "text": "Aktiv",
                    },
                    UserStatus.INACTIVE: {
                        "color": "text-gray-600",
                        "icon": "pause_circle",
                        "text": "Inaktiv",
                    },
                    UserStatus.SUSPENDED: {
                        "color": "text-red-600",
                        "icon": "block",
                        "text": "Gesperrt",
                    },
                    UserStatus.PENDING: {
                        "color": "text-yellow-600",
                        "icon": "schedule",
                        "text": "Ausstehend",
                    },
                }

                config = status_config.get(
                    self.user.status, status_config[UserStatus.ACTIVE],
                )
                with ui.row().classes("items-center space-x-2"):
                    ui.icon(config["icon"]).classes(f"w-4 h-4 {config['color']}")
                    ui.label(config["text"]).classes(f"text-sm {config['color']}")

    def create_avatar_section(self):
        """Create avatar section."""
        self.avatar_container = ui.element("div").classes("relative")

        with self.avatar_container:
            # Avatar image
            if self.user.avatar_url:
                ui.image(self.user.avatar_url).classes(
                    "w-24 h-24 rounded-full object-cover",
                )
            else:
                # Default avatar
                with ui.element("div").classes(
                    "w-24 h-24 rounded-full bg-gray-200 flex items-center justify-center",
                ):
                    ui.icon("person").classes("w-12 h-12 text-gray-400")

            # Upload button
            ui.button(
                icon="camera_alt",
                on_click=self.show_avatar_upload,
            ).classes(
                "absolute bottom-0 right-0 w-8 h-8 bg-blue-500 text-white rounded-full",
            )

    def create_statistics(self):
        """Create user statistics section."""
        self.stats_container = ui.element("div").classes("mb-6")

        with self.stats_container:
            with ui.row().classes("grid grid-cols-2 md:grid-cols-4 gap-4"):
                # Conversations
                with ui.element("div").classes("bg-blue-50 border rounded-lg p-4"):
                    ui.label("Gespräche").classes("text-sm text-gray-600")
                    ui.label("0").classes("text-2xl font-bold text-blue-600")

                # Messages
                with ui.element("div").classes("bg-green-50 border rounded-lg p-4"):
                    ui.label("Nachrichten").classes("text-sm text-gray-600")
                    ui.label("0").classes("text-2xl font-bold text-green-600")

                # Documents
                with ui.element("div").classes("bg-purple-50 border rounded-lg p-4"):
                    ui.label("Dokumente").classes("text-sm text-gray-600")
                    ui.label("0").classes("text-2xl font-bold text-purple-600")

                # Storage
                with ui.element("div").classes("bg-orange-50 border rounded-lg p-4"):
                    ui.label("Speicher").classes("text-sm text-gray-600")
                    ui.label("0 MB").classes("text-2xl font-bold text-orange-600")

    def create_profile_details(self):
        """Create profile details section."""
        with ui.element("div").classes("mb-6"):
            # Bio
            if self.user.bio:
                with ui.element("div").classes("mb-4"):
                    ui.label("Über mich").classes("font-medium text-gray-700 mb-2")
                    ui.label(self.user.bio).classes("text-gray-600")

            # Additional info
            with ui.row().classes("space-x-6"):
                # Location
                if self.user.location:
                    with ui.column():
                        ui.label("Standort").classes(
                            "text-sm font-medium text-gray-700",
                        )
                        ui.label(self.user.location).classes("text-sm text-gray-600")

                # Website
                if self.user.website:
                    with ui.column():
                        ui.label("Website").classes("text-sm font-medium text-gray-700")
                        ui.link(self.user.website, self.user.website).classes(
                            "text-sm text-blue-600",
                        )

            # Account info
            with ui.expansion("Account-Informationen", icon="info").classes("mt-4"):
                with ui.column().classes("space-y-2"):
                    with ui.row().classes("justify-between"):
                        ui.label("Mitglied seit:").classes("text-sm text-gray-600")
                        ui.label(format_timestamp(self.user.created_at)).classes(
                            "text-sm",
                        )

                    with ui.row().classes("justify-between"):
                        ui.label("Letzte Aktivität:").classes("text-sm text-gray-600")
                        if self.user.last_login:
                            ui.label(
                                format_relative_time(self.user.last_login),
                            ).classes("text-sm")
                        else:
                            ui.label("Nie").classes("text-sm text-gray-400")

                    with ui.row().classes("justify-between"):
                        ui.label("Zuletzt aktualisiert:").classes(
                            "text-sm text-gray-600",
                        )
                        ui.label(format_relative_time(self.user.updated_at)).classes(
                            "text-sm",
                        )

    def create_actions(self):
        """Create action buttons."""
        with ui.row().classes("space-x-2"):
            # Edit profile
            ui.button(
                "Profil bearbeiten",
                icon="edit",
                on_click=lambda: self.handle_edit(),
            ).classes("bg-blue-500 text-white")

            # Change password
            ui.button(
                "Passwort ändern",
                icon="lock",
                on_click=self.show_password_change_dialog,
            ).classes("bg-gray-500 text-white")

            # Settings
            ui.button(
                "Einstellungen",
                icon="settings",
                on_click=self.show_settings_dialog,
            ).classes("bg-green-500 text-white")

            # Admin actions
            if self.show_admin_actions:
                ui.button(
                    "Admin-Aktionen",
                    icon="admin_panel_settings",
                    on_click=self.show_admin_actions_dialog,
                ).classes("bg-red-500 text-white")

    def show_avatar_upload(self):
        """Show avatar upload dialog."""
        with ui.dialog() as dialog, ui.card().classes("w-96"):
            ui.label("Avatar hochladen").classes("text-lg font-medium mb-4")

            with ui.column().classes("space-y-4"):
                # File upload
                avatar_upload = ui.upload(
                    label="Avatar auswählen",
                    multiple=False,
                    on_upload=self.handle_avatar_upload,
                ).props("accept=image/*")

                # Preview
                ui.label("Vorschau:").classes("font-medium")
                preview_container = ui.element("div").classes(
                    "w-32 h-32 border rounded-lg overflow-hidden",
                )

                # Buttons
                with ui.row().classes("justify-end space-x-2"):
                    ui.button("Abbrechen", on_click=dialog.close).classes(
                        "bg-gray-500 text-white",
                    )
                    ui.button("Hochladen", on_click=dialog.close).classes(
                        "bg-blue-600 text-white",
                    )

    def handle_avatar_upload(self, event):
        """Handle avatar upload."""
        if self.on_avatar_upload:
            self.on_avatar_upload(event.content, event.name)

    def show_password_change_dialog(self):
        """Show password change dialog."""
        with ui.dialog() as dialog, ui.card().classes("w-96"):
            ui.label("Passwort ändern").classes("text-lg font-medium mb-4")

            with ui.column().classes("space-y-4"):
                current_password = ui.input(
                    "Aktuelles Passwort", password=True,
                ).classes("w-full")
                new_password = ui.input("Neues Passwort", password=True).classes(
                    "w-full",
                )
                confirm_password = ui.input(
                    "Passwort bestätigen", password=True,
                ).classes("w-full")

                with ui.row().classes("justify-end space-x-2"):
                    ui.button("Abbrechen", on_click=dialog.close).classes(
                        "bg-gray-500 text-white",
                    )
                    ui.button(
                        "Ändern",
                        on_click=lambda: self.handle_password_change(
                            current_password.value,
                            new_password.value,
                            confirm_password.value,
                            dialog,
                        ),
                    ).classes("bg-blue-600 text-white")

    def handle_password_change(self, current: str, new: str, confirm: str, dialog):
        """Handle password change."""
        if new != confirm:
            ui.notify("Passwörter stimmen nicht überein", type="error")
            return

        if self.on_password_change:
            self.on_password_change(current, new)
            dialog.close()

    def show_settings_dialog(self):
        """Show settings dialog."""
        with ui.dialog() as dialog, ui.card().classes("w-full max-w-2xl"):
            ui.label("Benutzereinstellungen").classes("text-lg font-medium mb-4")

            with ui.column().classes("space-y-6"):
                # Appearance
                with ui.expansion("Erscheinungsbild", icon="palette"):
                    with ui.column().classes("space-y-4"):
                        theme_select = ui.select(
                            "Theme",
                            options=["light", "dark", "auto"],
                            value=self.user.preferences.theme
                            if self.user.preferences
                            else "light",
                        ).classes("w-full")

                        font_size_select = ui.select(
                            "Schriftgröße",
                            options=["small", "medium", "large"],
                            value=self.user.preferences.font_size
                            if self.user.preferences
                            else "medium",
                        ).classes("w-full")

                        ui.switch(
                            "Kompakter Modus",
                            value=self.user.preferences.ui_compact_mode
                            if self.user.preferences
                            else False,
                        ).classes("w-full")

                        ui.switch(
                            "Hoher Kontrast",
                            value=self.user.preferences.high_contrast
                            if self.user.preferences
                            else False,
                        ).classes("w-full")

                # Notifications
                with ui.expansion("Benachrichtigungen", icon="notifications"):
                    with ui.column().classes("space-y-4"):
                        ui.switch(
                            "Benachrichtigungen aktivieren",
                            value=self.user.preferences.notifications_enabled
                            if self.user.preferences
                            else True,
                        ).classes("w-full")

                        ui.switch(
                            "E-Mail-Benachrichtigungen",
                            value=self.user.preferences.email_notifications
                            if self.user.preferences
                            else True,
                        ).classes("w-full")

                        ui.switch(
                            "Push-Benachrichtigungen",
                            value=self.user.preferences.push_notifications
                            if self.user.preferences
                            else False,
                        ).classes("w-full")

                # Chat settings
                with ui.expansion("Chat-Einstellungen", icon="chat"):
                    with ui.column().classes("space-y-4"):
                        history_limit = ui.number(
                            "Chat-Verlauf-Limit",
                            value=self.user.preferences.chat_history_limit
                            if self.user.preferences
                            else 100,
                            min=10,
                            max=1000,
                        ).classes("w-full")

                        ui.switch(
                            "Auto-Save",
                            value=self.user.preferences.auto_save
                            if self.user.preferences
                            else True,
                        ).classes("w-full")

                        ui.switch(
                            "Sound aktivieren",
                            value=self.user.preferences.sound_enabled
                            if self.user.preferences
                            else True,
                        ).classes("w-full")

                # Buttons
                with ui.row().classes("justify-end space-x-2"):
                    ui.button("Abbrechen", on_click=dialog.close).classes(
                        "bg-gray-500 text-white",
                    )
                    ui.button(
                        "Speichern",
                        on_click=lambda: self.save_settings(dialog),
                    ).classes("bg-blue-600 text-white")

    def save_settings(self, dialog):
        """Save user settings."""
        if self.on_preferences_update and self.user.preferences:
            # Update preferences based on dialog values
            # This would collect values from the dialog and update preferences
            self.on_preferences_update(self.user.preferences)
            dialog.close()

    def show_admin_actions_dialog(self):
        """Show admin actions dialog."""
        with ui.dialog() as dialog, ui.card().classes("w-96"):
            ui.label("Admin-Aktionen").classes("text-lg font-medium mb-4")

            with ui.column().classes("space-y-4"):
                # Role change
                role_select = ui.select(
                    "Rolle ändern",
                    options=["user", "moderator", "admin"],
                    value=self.user.role.value,
                ).classes("w-full")

                # Status change
                status_select = ui.select(
                    "Status ändern",
                    options=["active", "inactive", "suspended"],
                    value=self.user.status.value,
                ).classes("w-full")

                # Delete user
                ui.button(
                    "Benutzer löschen",
                    icon="delete",
                    on_click=lambda: self.handle_delete_user(dialog),
                ).classes("bg-red-500 text-white w-full")

                with ui.row().classes("justify-end space-x-2"):
                    ui.button("Abbrechen", on_click=dialog.close).classes(
                        "bg-gray-500 text-white",
                    )
                    ui.button("Speichern", on_click=dialog.close).classes(
                        "bg-blue-600 text-white",
                    )

    def handle_delete_user(self, dialog):
        """Handle user deletion."""
        # This would implement user deletion logic
        ui.notify("Benutzer-Löschung wird implementiert", type="info")
        dialog.close()

    def handle_edit(self):
        """Handle edit action."""
        if self.on_edit:
            self.on_edit(self.user)

    def update_user(self, user: UserProfile):
        """Update user data."""
        self.user = user
        # Recreate the card with new data
        self.container.clear()
        self.create_profile_card()

    def update_stats(self, stats: UserStats):
        """Update user statistics."""
        self.stats_container.clear()
        with self.stats_container:
            with ui.row().classes("grid grid-cols-2 md:grid-cols-4 gap-4"):
                # Conversations
                with ui.element("div").classes("bg-blue-50 border rounded-lg p-4"):
                    ui.label("Gespräche").classes("text-sm text-gray-600")
                    ui.label(str(stats.total_conversations)).classes(
                        "text-2xl font-bold text-blue-600",
                    )

                # Messages
                with ui.element("div").classes("bg-green-50 border rounded-lg p-4"):
                    ui.label("Nachrichten").classes("text-sm text-gray-600")
                    ui.label(str(stats.total_messages)).classes(
                        "text-2xl font-bold text-green-600",
                    )

                # Documents
                with ui.element("div").classes("bg-purple-50 border rounded-lg p-4"):
                    ui.label("Dokumente").classes("text-sm text-gray-600")
                    ui.label(str(stats.total_documents)).classes(
                        "text-2xl font-bold text-purple-600",
                    )

                # Storage
                with ui.element("div").classes("bg-orange-50 border rounded-lg p-4"):
                    ui.label("Speicher").classes("text-sm text-gray-600")
                    ui.label(format_file_size(stats.storage_used)).classes(
                        "text-2xl font-bold text-orange-600",
                    )


def create_profile_card(
    user: UserProfile,
    on_edit: Callable[[UserProfile], None] | None = None,
    on_avatar_upload: Callable[[bytes, str], None] | None = None,
    on_password_change: Callable[[str, str], None] | None = None,
    on_preferences_update: Callable[[UserPreferences], None] | None = None,
    show_admin_actions: bool = False,
) -> ProfileCard:
    """
    Create a profile card component.

    Args:
        user: User profile to display
        on_edit: Edit callback
        on_avatar_upload: Avatar upload callback
        on_password_change: Password change callback
        on_preferences_update: Preferences update callback
        show_admin_actions: Show admin actions

    Returns:
        ProfileCard instance
    """
    return ProfileCard(
        user=user,
        on_edit=on_edit,
        on_avatar_upload=on_avatar_upload,
        on_password_change=on_password_change,
        on_preferences_update=on_preferences_update,
        show_admin_actions=show_admin_actions,
    )
