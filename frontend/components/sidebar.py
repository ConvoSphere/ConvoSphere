"""
Sidebar component for navigation and menu items.

This module provides a reusable sidebar component with navigation
links and collapsible functionality.
"""

from collections.abc import Callable

from nicegui import ui
from pages import (
    create_assistants_page,
    create_chat_page,
    create_conversations_page,
    create_dashboard_page,
    create_knowledge_base_page,
    create_settings_page,
    create_tools_page,
)
from pages.mcp_tools import create_page as create_mcp_tools


def create_sidebar(
    collapsed: bool = False,
    current_page: str = "",
    on_navigation: Callable | None = None,
) -> ui.element:
    """
    Create a sidebar component.

    Args:
        collapsed: Whether the sidebar is collapsed
        current_page: Current active page
        on_navigation: Callback for navigation

    Returns:
        ui.element: The sidebar component
    """
    sidebar_class = "w-16" if collapsed else "w-64"

    with ui.element("aside").classes(
        f"{sidebar_class} bg-white dark:bg-gray-800 shadow-sm border-r border-gray-200 dark:border-gray-700 transition-all duration-300",
    ) as sidebar:
        with ui.element("div").classes("h-full flex flex-col"):
            # Navigation items
            with ui.element("nav").classes("flex-1 px-2 py-4 space-y-2"):
                _create_nav_items(collapsed, current_page, on_navigation)

            # Bottom section
            with ui.element("div").classes(
                "p-2 border-t border-gray-200 dark:border-gray-700",
            ):
                _create_bottom_section(collapsed)

    return sidebar


def _create_nav_items(
    collapsed: bool, current_page: str, on_navigation: Callable | None,
):
    """Create navigation menu items."""
    nav_items = [
        {
            "id": "dashboard",
            "label": "Dashboard",
            "icon": "dashboard",
            "href": "#dashboard",
        },
        {
            "id": "chat",
            "label": "Chat",
            "icon": "chat",
            "href": "#chat",
        },
        {
            "id": "conversations",
            "label": "Konversationen",
            "icon": "forum",
            "href": "#conversations",
        },
        {
            "id": "assistants",
            "label": "Assistenten",
            "icon": "smart_toy",
            "href": "#assistants",
        },
        {
            "id": "tools",
            "label": "Tools",
            "icon": "build",
            "href": "#tools",
        },
        {
            "id": "knowledge",
            "label": "Wissensdatenbank",
            "icon": "library_books",
            "href": "#knowledge",
        },
        {
            "id": "mcp",
            "label": "MCP Tools",
            "icon": "extension",
            "href": "#mcp",
        },
    ]

    for item in nav_items:
        is_active = current_page == item["id"]
        _create_nav_item(item, collapsed, is_active, on_navigation)


def _create_nav_item(
    item: dict, collapsed: bool, is_active: bool, on_navigation: Callable | None,
):
    """Create a single navigation item."""
    active_class = (
        "bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300"
        if is_active
        else "text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
    )

    with ui.element("div").classes("group"):
        with ui.element("a").classes(
            f"flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors {active_class}",
        ) as nav_link:
            # Icon
            ui.icon(item["icon"]).classes("mr-3 h-5 w-5")

            # Label (hidden when collapsed)
            if not collapsed:
                ui.label(item["label"])

            # Tooltip for collapsed state
            if collapsed:
                nav_link.tooltip(item["label"])

        # Click handler
        if on_navigation:
            nav_link.on("click", lambda: on_navigation(item["id"]))


def _create_bottom_section(collapsed: bool):
    """Create the bottom section of the sidebar."""
    # User info (only shown when not collapsed)
    if not collapsed:
        with ui.element("div").classes("flex items-center px-2 py-2"):
            # User avatar
            ui.element("div").classes(
                "h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center text-white text-sm font-medium",
            ).text = "U"

            # User info
            with ui.element("div").classes("ml-3"):
                ui.label("Benutzer").classes(
                    "text-sm font-medium text-gray-700 dark:text-gray-300",
                )
                ui.label("user@example.com").classes(
                    "text-xs text-gray-500 dark:text-gray-400",
                )

    # Collapse/expand button
    with ui.element("div").classes("mt-2"):
        ui.button(
            icon="chevron_left" if not collapsed else "chevron_right",
            on_click=lambda: _handle_sidebar_toggle(),
        ).classes(
            "w-full p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md",
        )


def _handle_sidebar_toggle():
    """Handle sidebar toggle."""
    # This would need to be implemented with proper state management
    ui.notify("Sidebar-Toggle wird implementiert", type="info")


# Navigation routes
routes = {
    "/": create_dashboard_page,
    "/assistants": create_assistants_page,
    "/conversations": create_conversations_page,
    "/chat": create_chat_page,
    "/tools": create_tools_page,
    "/mcp-tools": create_mcp_tools,
    "/knowledge-base": create_knowledge_base_page,
    "/settings": create_settings_page,
}
