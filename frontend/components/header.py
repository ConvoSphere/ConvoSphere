"""
Header component for consistent navigation and branding.

This module provides a reusable header component with navigation,
theme switching, and user menu functionality.
"""

from collections.abc import Callable

from nicegui import ui
from utils.i18n_manager import i18n_manager
from utils.theme_manager import theme_manager


def create_header(
    title: str = "",
    on_sidebar_toggle: Callable | None = None,
    on_theme_toggle: Callable | None = None,
) -> ui.element:
    """
    Create a header component.

    Args:
        title: Page title to display
        on_sidebar_toggle: Callback for sidebar toggle
        on_theme_toggle: Callback for theme toggle

    Returns:
        ui.element: The header component
    """
    with ui.element("header").classes(
        "bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700",
    ) as header:
        with ui.element("div").classes("max-w-7xl mx-auto px-4 sm:px-6 lg:px-8"):
            with ui.element("div").classes("flex justify-between items-center py-4"):
                # Left side - Logo and title
                with ui.element("div").classes("flex items-center space-x-4"):
                    # Sidebar toggle button
                    if on_sidebar_toggle:
                        ui.button(
                            icon="menu",
                            on_click=on_sidebar_toggle,
                        ).classes(
                            "p-2 rounded-md text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700",
                        )

                    # Logo
                    with ui.element("div").classes("flex items-center"):
                        ui.html(
                            "<h1 style='font-size: 24px; font-weight: 700; color: var(--color-text);'>ConvoSphere</h1>",
                        )

                    # Page title
                    if title:
                        with ui.element("div").classes(
                            "ml-4 pl-4 border-l border-gray-300 dark:border-gray-600",
                        ):
                            ui.html(
                                f"<span style='color: var(--color-text-secondary); font-size: 18px;'>{title}</span>",
                            )

                # Right side - Actions
                with ui.element("div").classes("flex items-center space-x-4"):
                    # Language switcher
                    ui.label(i18n_manager.t("common.language")).classes(
                        "text-gray-700 dark:text-gray-200",
                    )
                    ui.select(
                        options=i18n_manager.get_supported_languages(),
                        value=i18n_manager.get_current_language(),
                        on_change=lambda e: i18n_manager.set_language(e.value),
                    ).classes("w-28")
                    # Theme toggle
                    ui.button(
                        icon="dark_mode",
                        on_click=lambda: _handle_theme_toggle(on_theme_toggle),
                    ).classes(
                        "p-2 rounded-md text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700",
                    )

                    # Notifications
                    ui.button(
                        icon="notifications",
                        on_click=lambda: _handle_notifications(),
                    ).classes(
                        "p-2 rounded-md text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700",
                    )

                    # User menu
                    _create_user_menu()

    return header


def _handle_theme_toggle(callback: Callable | None = None):
    """Handle theme toggle."""
    theme_manager.toggle_theme()

    if callback:
        callback()


def _handle_notifications():
    """Handle notifications button click."""
    ui.notify("Benachrichtigungen werden noch implementiert", type="info")


def _create_user_menu():
    """Create the user menu dropdown."""
    with ui.element("div").classes("relative"):
        # User avatar button
        ui.button(
            icon="account_circle",
            on_click=lambda: _toggle_user_menu(),
        ).classes(
            "p-2 rounded-md text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700",
        )

        # User menu dropdown (hidden by default)
        with ui.element("div").classes(
            "absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-md shadow-lg py-1 z-50 hidden",
        ) as user_menu:
            # Profile link
            ui.link(
                "Profil",
                "#profile",
                on_click=lambda: _handle_menu_item("profile"),
            ).classes(
                "block px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700",
            )

            # Settings link
            ui.link(
                "Einstellungen",
                "#settings",
                on_click=lambda: _handle_menu_item("settings"),
            ).classes(
                "block px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700",
            )

            # Divider
            ui.element("hr").classes("my-1 border-gray-200 dark:border-gray-600")

            # Logout link
            ui.link(
                "Abmelden",
                "#logout",
                on_click=lambda: _handle_menu_item("logout"),
            ).classes(
                "block px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700",
            )


def _toggle_user_menu():
    """Toggle the user menu visibility."""
    # This would need to be implemented with proper state management


def _handle_menu_item(item: str):
    """Handle user menu item clicks."""
    if item == "logout":
        # Handle logout
        ui.notify("Abmeldung wird implementiert", type="info")
    elif item == "profile":
        # Navigate to profile
        ui.notify("Profil wird implementiert", type="info")
    elif item == "settings":
        # Navigate to settings
        ui.notify("Einstellungen werden implementiert", type="info")
