"""
Advanced Admin Page for the AI Assistant Platform.

This module provides comprehensive administrative functionality including
user management, system statistics, and administrative controls.
"""

from typing import Any

from components.common.error_message import create_error_message
from components.common.loading_spinner import create_loading_spinner
from nicegui import ui
from services.user_service import UserProfile, UserRole, UserStatus, user_service


class AdvancedAdminPage:
    """Advanced admin management page component."""

    def __init__(self):
        """Initialize the advanced admin page."""
        self.users: list[UserProfile] = []
        self.system_stats: dict[str, Any] = {}
        self.is_loading = False
        self.error_message = None
        self.current_tab = "users"

        # UI components
        self.container = None
        self.users_container = None
        self.stats_container = None
        self.settings_container = None

        self.create_admin_page()
        self.load_admin_data()

    def create_admin_page(self):
        """Create the advanced admin page UI."""
        self.container = ui.element("div").classes("p-6")

        with self.container:
            # Header
            self.create_header()

            # Navigation tabs
            self.create_navigation()

            # Content area
            self.create_content_area()

    def create_header(self):
        """Create the page header."""
        with ui.element("div").classes("mb-6"):
            with ui.row().classes("items-center justify-between"):
                with ui.column():
                    ui.label("Admin-Bereich").classes("text-2xl font-bold text-red-800")
                    ui.label("System-Verwaltung und Benutzer-Management").classes(
                        "text-gray-600",
                    )

                with ui.row().classes("space-x-2"):
                    ui.button(
                        "Aktualisieren",
                        icon="refresh",
                        on_click=self.refresh_data,
                    ).classes("bg-blue-600 text-white")

                    ui.button(
                        "System-Export",
                        icon="download",
                        on_click=self.export_system_data,
                    ).classes("bg-green-600 text-white")

    def create_navigation(self):
        """Create navigation tabs."""
        with ui.element("div").classes("mb-6"):
            with ui.tabs().classes("w-full") as tabs:
                ui.tab("Benutzer", icon="people")
                ui.tab("Statistiken", icon="analytics")
                ui.tab("System", icon="settings")

            with ui.tab_panels(tabs, value=self.current_tab).classes(
                "w-full",
            ) as panels:
                # Users panel
                with ui.tab_panel("Benutzer"):
                    self.create_users_panel()

                # Statistics panel
                with ui.tab_panel("Statistiken"):
                    self.create_statistics_panel()

                # System panel
                with ui.tab_panel("System"):
                    self.create_system_panel()

    def create_users_panel(self):
        """Create users management panel."""
        self.users_container = ui.element("div").classes("space-y-6")

        with self.users_container:
            # Search and filters
            self.create_user_filters()

            # Users table
            self.create_users_table()

    def create_user_filters(self):
        """Create user search and filters."""
        with ui.element("div").classes("bg-white border rounded-lg p-4"):
            with ui.row().classes("items-center space-x-4"):
                # Search
                self.user_search_input = ui.input(
                    "Benutzer suchen...",
                    on_change=self.filter_users,
                ).classes("flex-1")

                # Role filter
                self.role_filter = ui.select(
                    "Rolle",
                    options=["Alle", "User", "Moderator", "Admin"],
                    value="Alle",
                    on_change=self.filter_users,
                ).classes("w-32")

                # Status filter
                self.status_filter = ui.select(
                    "Status",
                    options=["Alle", "Aktiv", "Inaktiv", "Gesperrt"],
                    value="Alle",
                    on_change=self.filter_users,
                ).classes("w-32")

                # Add user button
                ui.button(
                    "Benutzer hinzufügen",
                    icon="person_add",
                    on_click=self.show_add_user_dialog,
                ).classes("bg-green-600 text-white")

    def create_users_table(self):
        """Create users table."""
        with ui.element("div").classes("bg-white border rounded-lg overflow-hidden"):
            # Table header
            with ui.element("div").classes("bg-gray-50 px-6 py-3 border-b"):
                with ui.row().classes(
                    "grid grid-cols-12 gap-4 text-sm font-medium text-gray-700",
                ):
                    ui.label("Benutzer").classes("col-span-3")
                    ui.label("E-Mail").classes("col-span-3")
                    ui.label("Rolle").classes("col-span-2")
                    ui.label("Status").classes("col-span-2")
                    ui.label("Aktionen").classes("col-span-2")

            # Table body
            self.users_table_body = ui.element("div").classes("divide-y")
            with self.users_table_body:
                create_loading_spinner("Lade Benutzer...")

    def create_statistics_panel(self):
        """Create statistics panel."""
        self.stats_container = ui.element("div").classes("space-y-6")

        with self.stats_container:
            # System overview
            self.create_system_overview()

            # User statistics
            self.create_user_statistics()

            # Activity statistics
            self.create_activity_statistics()

    def create_system_overview(self):
        """Create system overview section."""
        with ui.element("div").classes("bg-white border rounded-lg p-6"):
            ui.label("System-Übersicht").classes("text-lg font-medium mb-4")

            with ui.row().classes("grid grid-cols-2 md:grid-cols-4 gap-4"):
                # Total users
                with ui.element("div").classes("bg-blue-50 border rounded-lg p-4"):
                    ui.label("Gesamt Benutzer").classes("text-sm text-gray-600")
                    ui.label("0").classes("text-2xl font-bold text-blue-600")

                # Active users
                with ui.element("div").classes("bg-green-50 border rounded-lg p-4"):
                    ui.label("Aktive Benutzer").classes("text-sm text-gray-600")
                    ui.label("0").classes("text-2xl font-bold text-green-600")

                # Total conversations
                with ui.element("div").classes("bg-purple-50 border rounded-lg p-4"):
                    ui.label("Gespräche").classes("text-sm text-gray-600")
                    ui.label("0").classes("text-2xl font-bold text-purple-600")

                # Storage used
                with ui.element("div").classes("bg-orange-50 border rounded-lg p-4"):
                    ui.label("Speicher").classes("text-sm text-gray-600")
                    ui.label("0 GB").classes("text-2xl font-bold text-orange-600")

    def create_user_statistics(self):
        """Create user statistics section."""
        with ui.element("div").classes("bg-white border rounded-lg p-6"):
            ui.label("Benutzer-Statistiken").classes("text-lg font-medium mb-4")

            with ui.row().classes("space-x-6"):
                # Role distribution
                with ui.column().classes("flex-1"):
                    ui.label("Rollen-Verteilung").classes("font-medium mb-2")
                    with ui.element("div").classes("space-y-2"):
                        with ui.row().classes("justify-between"):
                            ui.label("User").classes("text-sm")
                            ui.label("0").classes("text-sm font-medium")
                        with ui.row().classes("justify-between"):
                            ui.label("Moderator").classes("text-sm")
                            ui.label("0").classes("text-sm font-medium")
                        with ui.row().classes("justify-between"):
                            ui.label("Admin").classes("text-sm")
                            ui.label("0").classes("text-sm font-medium")

                # Status distribution
                with ui.column().classes("flex-1"):
                    ui.label("Status-Verteilung").classes("font-medium mb-2")
                    with ui.element("div").classes("space-y-2"):
                        with ui.row().classes("justify-between"):
                            ui.label("Aktiv").classes("text-sm")
                            ui.label("0").classes("text-sm font-medium")
                        with ui.row().classes("justify-between"):
                            ui.label("Inaktiv").classes("text-sm")
                            ui.label("0").classes("text-sm font-medium")
                        with ui.row().classes("justify-between"):
                            ui.label("Gesperrt").classes("text-sm")
                            ui.label("0").classes("text-sm font-medium")

    def create_activity_statistics(self):
        """Create activity statistics section."""
        with ui.element("div").classes("bg-white border rounded-lg p-6"):
            ui.label("Aktivitäts-Statistiken").classes("text-lg font-medium mb-4")

            with ui.column().classes("space-y-4"):
                # Recent registrations
                with ui.element("div"):
                    ui.label("Neue Registrierungen (letzte 30 Tage)").classes(
                        "font-medium mb-2",
                    )
                    ui.label("0 neue Benutzer").classes("text-sm text-gray-600")

                # Recent activity
                with ui.element("div"):
                    ui.label("Letzte Aktivität").classes("font-medium mb-2")
                    ui.label("Keine Aktivität").classes("text-sm text-gray-600")

    def create_system_panel(self):
        """Create system management panel."""
        self.settings_container = ui.element("div").classes("space-y-6")

        with self.settings_container:
            # System settings
            self.create_system_settings()

            # Maintenance
            self.create_maintenance_section()

            # Security
            self.create_security_section()

    def create_system_settings(self):
        """Create system settings section."""
        with ui.element("div").classes("bg-white border rounded-lg p-6"):
            ui.label("System-Einstellungen").classes("text-lg font-medium mb-4")

            with ui.column().classes("space-y-4"):
                # Registration settings
                with ui.row().classes("items-center justify-between"):
                    ui.label("Registrierung erlauben").classes("font-medium")
                    ui.switch(value=True).classes("w-full")

                # Email verification
                with ui.row().classes("items-center justify-between"):
                    ui.label("E-Mail-Verifizierung").classes("font-medium")
                    ui.switch(value=True).classes("w-full")

                # Storage limit
                with ui.row().classes("items-center justify-between"):
                    ui.label("Standard-Speicherlimit").classes("font-medium")
                    ui.number(value=1000, min=100, max=10000).classes("w-32")

                # Session timeout
                with ui.row().classes("items-center justify-between"):
                    ui.label("Session-Timeout (Minuten)").classes("font-medium")
                    ui.number(value=60, min=15, max=1440).classes("w-32")

    def create_maintenance_section(self):
        """Create maintenance section."""
        with ui.element("div").classes("bg-white border rounded-lg p-6"):
            ui.label("Wartung").classes("text-lg font-medium mb-4")

            with ui.column().classes("space-y-4"):
                # Database backup
                ui.button(
                    "Datenbank-Backup erstellen",
                    icon="backup",
                    on_click=self.create_backup,
                ).classes("bg-blue-600 text-white")

                # Cache clear
                ui.button(
                    "Cache leeren",
                    icon="cleaning_services",
                    on_click=self.clear_cache,
                ).classes("bg-orange-600 text-white")

                # System restart
                ui.button(
                    "System neu starten",
                    icon="restart_alt",
                    on_click=self.restart_system,
                ).classes("bg-red-600 text-white")

    def create_security_section(self):
        """Create security section."""
        with ui.element("div").classes("bg-white border rounded-lg p-6"):
            ui.label("Sicherheit").classes("text-lg font-medium mb-4")

            with ui.column().classes("space-y-4"):
                # Security audit
                ui.button(
                    "Sicherheits-Audit durchführen",
                    icon="security",
                    on_click=self.run_security_audit,
                ).classes("bg-purple-600 text-white")

                # Block IP
                ui.button(
                    "IP-Adresse blockieren",
                    icon="block",
                    on_click=self.block_ip_address,
                ).classes("bg-red-600 text-white")

                # View logs
                ui.button(
                    "System-Logs anzeigen",
                    icon="description",
                    on_click=self.view_system_logs,
                ).classes("bg-gray-600 text-white")

    def create_content_area(self):
        """Create main content area."""
        # Content is handled by tab panels

    async def load_admin_data(self):
        """Load admin data."""
        self.is_loading = True

        try:
            # Load users
            self.users = await user_service.get_all_users()

            # Load system stats
            self.system_stats = await user_service.get_system_stats()

            # Update UI
            self.update_users_table()
            self.update_statistics()

        except Exception as e:
            self.error_message = f"Fehler beim Laden der Admin-Daten: {str(e)}"
            self.display_error()
        finally:
            self.is_loading = False

    def update_users_table(self):
        """Update users table."""
        self.users_table_body.clear()

        with self.users_table_body:
            if not self.users:
                with ui.element("div").classes("px-6 py-8 text-center text-gray-500"):
                    ui.label("Keine Benutzer gefunden")
                return

            for user in self.users:
                self.create_user_row(user)

    def create_user_row(self, user: UserProfile):
        """Create a user table row."""
        with ui.element("div").classes("px-6 py-4 hover:bg-gray-50"):
            with ui.row().classes("grid grid-cols-12 gap-4 items-center"):
                # User info
                with ui.column().classes("col-span-3"):
                    ui.label(f"{user.first_name} {user.last_name}").classes(
                        "font-medium",
                    )
                    ui.label(f"@{user.username}").classes("text-sm text-gray-600")

                # Email
                ui.label(user.email).classes("col-span-3 text-sm")

                # Role
                role_config = {
                    UserRole.ADMIN: {"color": "text-red-600", "text": "Admin"},
                    UserRole.MODERATOR: {
                        "color": "text-orange-600",
                        "text": "Moderator",
                    },
                    UserRole.USER: {"color": "text-blue-600", "text": "User"},
                }
                config = role_config.get(user.role, role_config[UserRole.USER])
                ui.label(config["text"]).classes(
                    f"col-span-2 text-sm font-medium {config['color']}",
                )

                # Status
                status_config = {
                    UserStatus.ACTIVE: {"color": "text-green-600", "text": "Aktiv"},
                    UserStatus.INACTIVE: {"color": "text-gray-600", "text": "Inaktiv"},
                    UserStatus.SUSPENDED: {"color": "text-red-600", "text": "Gesperrt"},
                    UserStatus.PENDING: {
                        "color": "text-yellow-600",
                        "text": "Ausstehend",
                    },
                }
                config = status_config.get(
                    user.status, status_config[UserStatus.ACTIVE],
                )
                ui.label(config["text"]).classes(
                    f"col-span-2 text-sm font-medium {config['color']}",
                )

                # Actions
                with ui.row().classes("col-span-2 space-x-2"):
                    ui.button(
                        icon="edit",
                        on_click=lambda u=user: self.edit_user(u),
                    ).classes("w-8 h-8 bg-blue-500 text-white rounded")

                    ui.button(
                        icon="delete",
                        on_click=lambda u=user: self.delete_user(u),
                    ).classes("w-8 h-8 bg-red-500 text-white rounded")

    def update_statistics(self):
        """Update statistics display."""
        # Update system overview
        if self.system_stats:
            # This would update the statistics displays with real data
            pass

    def display_error(self):
        """Display error message."""
        self.container.clear()
        with self.container:
            create_error_message(self.error_message or "Unbekannter Fehler")

    def filter_users(self):
        """Filter users based on search and filters."""
        # This would implement user filtering logic

    def show_add_user_dialog(self):
        """Show add user dialog."""
        with ui.dialog() as dialog, ui.card().classes("w-96"):
            ui.label("Benutzer hinzufügen").classes("text-lg font-medium mb-4")

            with ui.column().classes("space-y-4"):
                first_name = ui.input("Vorname").classes("w-full")
                last_name = ui.input("Nachname").classes("w-full")
                username = ui.input("Benutzername").classes("w-full")
                email = ui.input("E-Mail").classes("w-full")
                password = ui.input("Passwort", password=True).classes("w-full")

                role_select = ui.select(
                    "Rolle",
                    options=["user", "moderator", "admin"],
                    value="user",
                ).classes("w-full")

                with ui.row().classes("justify-end space-x-2"):
                    ui.button("Abbrechen", on_click=dialog.close).classes(
                        "bg-gray-500 text-white",
                    )
                    ui.button(
                        "Hinzufügen",
                        on_click=lambda: self.add_user(
                            first_name.value,
                            last_name.value,
                            username.value,
                            email.value,
                            password.value,
                            role_select.value,
                            dialog,
                        ),
                    ).classes("bg-green-600 text-white")

    async def add_user(
        self,
        first_name: str,
        last_name: str,
        username: str,
        email: str,
        password: str,
        role: str,
        dialog,
    ):
        """Add new user."""
        # This would implement user creation logic
        ui.notify("Benutzer-Erstellung wird implementiert", type="info")
        dialog.close()

    async def edit_user(self, user: UserProfile):
        """Edit user."""
        # This would implement user editing logic
        ui.notify("Benutzer-Bearbeitung wird implementiert", type="info")

    async def delete_user(self, user: UserProfile):
        """Delete user."""
        # This would implement user deletion logic
        ui.notify("Benutzer-Löschung wird implementiert", type="info")

    async def refresh_data(self):
        """Refresh admin data."""
        await self.load_admin_data()
        ui.notify("Daten aktualisiert", type="positive")

    def export_system_data(self):
        """Export system data."""
        ui.notify("System-Export wird implementiert", type="info")

    def create_backup(self):
        """Create database backup."""
        ui.notify("Backup-Erstellung wird implementiert", type="info")

    def clear_cache(self):
        """Clear system cache."""
        ui.notify("Cache-Bereinigung wird implementiert", type="info")

    def restart_system(self):
        """Restart system."""
        ui.notify("System-Neustart wird implementiert", type="info")

    def run_security_audit(self):
        """Run security audit."""
        ui.notify("Sicherheits-Audit wird implementiert", type="info")

    def block_ip_address(self):
        """Block IP address."""
        ui.notify("IP-Blockierung wird implementiert", type="info")

    def view_system_logs(self):
        """View system logs."""
        ui.notify("System-Logs werden implementiert", type="info")


# Global advanced admin page instance
advanced_admin_page = AdvancedAdminPage()
