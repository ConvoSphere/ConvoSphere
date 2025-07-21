"""
Authentication form component for login and registration.

This module provides reusable authentication forms with validation
and error handling.
"""

import asyncio
from collections.abc import Callable

from nicegui import ui
from services.auth_service import auth_service


class AuthForm:
    """Reusable authentication form component."""

    def __init__(self, form_type: str = "login"):
        """
        Initialize the authentication form.

        Args:
            form_type: Type of form ("login" or "register")
        """
        self.form_type = form_type
        self.email = ""
        self.password = ""
        self.confirm_password = ""
        self.username = ""
        self.first_name = ""
        self.last_name = ""
        self.error_message = ""
        self.is_loading = False

        # Form validation callbacks
        self.on_success: Callable | None = None
        self.on_error: Callable | None = None

    def create_form(self) -> ui.card:
        """
        Create the authentication form UI.

        Returns:
            ui.card: The form card component
        """
        with ui.card().classes("w-full max-w-md p-8 shadow-xl") as form_card:
            # Header
            self._create_header()

            # Form fields
            with ui.element("form").classes("space-y-6"):
                self._create_form_fields()

                # Error message
                self.error_label = ui.label("").classes("text-red-600 text-sm hidden")

                # Submit button
                self.submit_button = ui.button(
                    self._get_submit_text(),
                    on_click=self._handle_submit,
                ).classes(
                    "w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors",
                )

                # Loading spinner
                self.loading_spinner = ui.spinner("dots").classes("hidden")

            # Footer links
            self._create_footer()

        return form_card

    def _create_header(self):
        """Create the form header."""
        with ui.element("div").classes("text-center mb-8"):
            if self.form_type == "login":
                ui.html(
                    "<h1 style='font-size: 28px; font-weight: 700; color: var(--color-text); margin-bottom: 8px;'>Willkommen zu ConvoSphere</h1>",
                )
                ui.html(
                    "<p style='color: var(--color-text-secondary); font-size: 16px;'>Melde dich in deinem Konto an</p>",
                )
            else:
                ui.html(
                    "<h1 style='font-size: 28px; font-weight: 700; color: var(--color-text); margin-bottom: 8px;'>Konto erstellen</h1>",
                )
                ui.html(
                    "<p style='color: var(--color-text-secondary); font-size: 16px;'>Erstelle dein ConvoSphere-Konto</p>",
                )

    def _create_form_fields(self):
        """Create form input fields."""
        # Email input
        with ui.element("div"):
            ui.label("E-Mail-Adresse").classes(
                "block text-sm font-medium text-gray-700 mb-2",
            )
            self.email_input = ui.input(
                placeholder="deine@email.com",
                on_change=self._on_email_change,
            ).classes(
                "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent",
            )

        # Username input (only for registration)
        if self.form_type == "register":
            with ui.element("div"):
                ui.label("Benutzername").classes(
                    "block text-sm font-medium text-gray-700 mb-2",
                )
                self.username_input = ui.input(
                    placeholder="dein_benutzername",
                    on_change=self._on_username_change,
                ).classes(
                    "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                )

        # Name fields (only for registration)
        if self.form_type == "register":
            with ui.row().classes("space-x-4"):
                with ui.element("div").classes("flex-1"):
                    ui.label("Vorname").classes(
                        "block text-sm font-medium text-gray-700 mb-2",
                    )
                    self.first_name_input = ui.input(
                        placeholder="Vorname",
                        on_change=self._on_first_name_change,
                    ).classes(
                        "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                    )

                with ui.element("div").classes("flex-1"):
                    ui.label("Nachname").classes(
                        "block text-sm font-medium text-gray-700 mb-2",
                    )
                    self.last_name_input = ui.input(
                        placeholder="Nachname",
                        on_change=self._on_last_name_change,
                    ).classes(
                        "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                    )

        # Password input
        with ui.element("div"):
            ui.label("Passwort").classes("block text-sm font-medium text-gray-700 mb-2")
            self.password_input = ui.input(
                placeholder="Dein Passwort",
                password=True,
                on_change=self._on_password_change,
            ).classes(
                "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent",
            )

        # Confirm password input (only for registration)
        if self.form_type == "register":
            with ui.element("div"):
                ui.label("Passwort bestätigen").classes(
                    "block text-sm font-medium text-gray-700 mb-2",
                )
                self.confirm_password_input = ui.input(
                    placeholder="Passwort wiederholen",
                    password=True,
                    on_change=self._on_confirm_password_change,
                ).classes(
                    "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                )

    def _create_footer(self):
        """Create the form footer with links."""
        # Divider
        with ui.element("div").classes("my-6"):
            with ui.element("div").classes("relative"):
                with ui.element("div").classes("absolute inset-0 flex items-center"):
                    ui.element("div").classes("w-full border-t border-gray-300")
                with ui.element("div").classes("relative flex justify-center text-sm"):
                    ui.label("oder").classes("px-2 bg-white text-gray-500")

        # Links
        with ui.element("div").classes("text-center"):
            if self.form_type == "login":
                ui.html(
                    "<span style='color: var(--color-text-secondary);'>Noch kein Konto? </span>",
                )
                ui.link("Jetzt registrieren", "#register").classes(
                    "text-blue-600 hover:text-blue-500 font-medium",
                )
            else:
                ui.html(
                    "<span style='color: var(--color-text-secondary);'>Bereits ein Konto? </span>",
                )
                ui.link("Jetzt anmelden", "#login").classes(
                    "text-blue-600 hover:text-blue-500 font-medium",
                )

    def _get_submit_text(self) -> str:
        """Get the submit button text."""
        return "Anmelden" if self.form_type == "login" else "Registrieren"

    def _on_email_change(self, e):
        """Handle email input change."""
        self.email = e.value
        self._clear_error()

    def _on_username_change(self, e):
        """Handle username input change."""
        self.username = e.value
        self._clear_error()

    def _on_first_name_change(self, e):
        """Handle first name input change."""
        self.first_name = e.value
        self._clear_error()

    def _on_last_name_change(self, e):
        """Handle last name input change."""
        self.last_name = e.value
        self._clear_error()

    def _on_password_change(self, e):
        """Handle password input change."""
        self.password = e.value
        self._clear_error()

    def _on_confirm_password_change(self, e):
        """Handle confirm password input change."""
        self.confirm_password = e.value
        self._clear_error()

    def _clear_error(self):
        """Clear error message."""
        self.error_message = ""
        if hasattr(self, "error_label"):
            self.error_label.text = ""
            self.error_label.classes("hidden")

    def _show_error(self, message: str):
        """Show error message."""
        self.error_message = message
        if hasattr(self, "error_label"):
            self.error_label.text = message
            self.error_label.classes("text-red-600 text-sm")

    def _set_loading(self, loading: bool):
        """Set loading state."""
        self.is_loading = loading
        if loading:
            self.submit_button.classes("hidden")
            self.loading_spinner.classes("flex justify-center")
            self._disable_inputs()
        else:
            self.submit_button.classes(
                "w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors",
            )
            self.loading_spinner.classes("hidden")
            self._enable_inputs()

    def _disable_inputs(self):
        """Disable all input fields."""
        self.email_input.disable()
        self.password_input.disable()
        if self.form_type == "register":
            if hasattr(self, "username_input"):
                self.username_input.disable()
            if hasattr(self, "first_name_input"):
                self.first_name_input.disable()
            if hasattr(self, "last_name_input"):
                self.last_name_input.disable()
            if hasattr(self, "confirm_password_input"):
                self.confirm_password_input.disable()

    def _enable_inputs(self):
        """Enable all input fields."""
        self.email_input.enable()
        self.password_input.enable()
        if self.form_type == "register":
            if hasattr(self, "username_input"):
                self.username_input.enable()
            if hasattr(self, "first_name_input"):
                self.first_name_input.enable()
            if hasattr(self, "last_name_input"):
                self.last_name_input.enable()
            if hasattr(self, "confirm_password_input"):
                self.confirm_password_input.enable()

    def _validate_inputs(self) -> bool:
        """Validate form inputs."""
        # Email validation
        if not self.email:
            self._show_error("E-Mail-Adresse ist erforderlich")
            return False

        if "@" not in self.email or "." not in self.email:
            self._show_error("Bitte gib eine gültige E-Mail-Adresse ein")
            return False

        # Password validation
        if not self.password:
            self._show_error("Passwort ist erforderlich")
            return False

        if len(self.password) < 6:
            self._show_error("Passwort muss mindestens 6 Zeichen lang sein")
            return False

        # Registration-specific validation
        if self.form_type == "register":
            if not self.username:
                self._show_error("Benutzername ist erforderlich")
                return False

            if len(self.username) < 3:
                self._show_error("Benutzername muss mindestens 3 Zeichen lang sein")
                return False

            if self.password != self.confirm_password:
                self._show_error("Passwörter stimmen nicht überein")
                return False

        return True

    async def _handle_submit(self):
        """Handle form submission."""
        if not self._validate_inputs():
            return

        self._set_loading(True)

        try:
            if self.form_type == "login":
                success = await self._handle_login()
            else:
                success = await self._handle_register()

            if success and self.on_success:
                await self.on_success()
            elif not success and self.on_error:
                await self.on_error(self.error_message)

        except Exception as e:
            self._show_error(f"Ein Fehler ist aufgetreten: {str(e)}")
            if self.on_error:
                await self.on_error(str(e))

        finally:
            self._set_loading(False)

    async def _handle_login(self) -> bool:
        """Handle login submission."""
        success = await auth_service.login(self.email, self.password)

        if success:
            ui.notify("Erfolgreich angemeldet!", type="positive")
            await asyncio.sleep(1)
            return True
        self._show_error("Ungültige E-Mail oder Passwort")
        return False

    async def _handle_register(self) -> bool:
        """Handle registration submission."""
        user_data = {
            "email": self.email,
            "username": self.username,
            "password": self.password,
            "first_name": self.first_name,
            "last_name": self.last_name,
        }

        success = await auth_service.register(user_data)

        if success:
            ui.notify(
                "Registrierung erfolgreich! Du kannst dich jetzt anmelden.",
                type="positive",
            )
            await asyncio.sleep(2)
            return True
        self._show_error("Registrierung fehlgeschlagen. Bitte versuche es erneut.")
        return False
