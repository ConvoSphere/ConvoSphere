"""
Responsive layout system for the AI Assistant Platform.

This module provides comprehensive responsive design features including
mobile optimization, tablet support, and adaptive layouts.
"""

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any

from nicegui import ui


class Breakpoint(Enum):
    """CSS breakpoint enumeration."""

    XS = "xs"  # 0-639px
    SM = "sm"  # 640-767px
    MD = "md"  # 768-1023px
    LG = "lg"  # 1024-1279px
    XL = "xl"  # 1280-1535px
    XXL = "2xl"  # 1536px+


@dataclass
class ResponsiveConfig:
    """Responsive configuration for a component."""

    xs: dict[str, Any] = None
    sm: dict[str, Any] = None
    md: dict[str, Any] = None
    lg: dict[str, Any] = None
    xl: dict[str, Any] = None
    xxl: dict[str, Any] = None

    def __post_init__(self):
        """Initialize default values."""
        if self.xs is None:
            self.xs = {}
        if self.sm is None:
            self.sm = {}
        if self.md is None:
            self.md = {}
        if self.lg is None:
            self.lg = {}
        if self.xl is None:
            self.xl = {}
        if self.xxl is None:
            self.xxl = {}


class ResponsiveLayout:
    """Responsive layout management system."""

    def __init__(self):
        """Initialize responsive layout system."""
        self.current_breakpoint = Breakpoint.LG
        self.breakpoint_callbacks: list[Callable[[Breakpoint], None]] = []
        self.touch_enabled = False
        self.orientation = "landscape"

        # Initialize responsive features
        self.initialize_responsive()

    def initialize_responsive(self):
        """Initialize responsive features."""
        # Add responsive CSS
        self.add_responsive_css()

        # Add viewport meta tag
        self.add_viewport_meta()

        # Add touch detection
        self.detect_touch_support()

    def add_responsive_css(self):
        """Add responsive CSS styles."""
        css = """
        /* Responsive breakpoints */
        .responsive-container {
            width: 100%;
            max-width: 100%;
            margin: 0 auto;
            padding: 0 1rem;
        }
        
        /* Mobile-first responsive grid */
        .responsive-grid {
            display: grid;
            gap: 1rem;
            grid-template-columns: 1fr;
        }
        
        @media (min-width: 640px) {
            .responsive-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        
        @media (min-width: 768px) {
            .responsive-grid {
                grid-template-columns: repeat(3, 1fr);
            }
        }
        
        @media (min-width: 1024px) {
            .responsive-grid {
                grid-template-columns: repeat(4, 1fr);
            }
        }
        
        @media (min-width: 1280px) {
            .responsive-grid {
                grid-template-columns: repeat(5, 1fr);
            }
        }
        
        /* Responsive typography */
        .responsive-text-xs {
            font-size: 0.75rem;
        }
        
        .responsive-text-sm {
            font-size: 0.875rem;
        }
        
        .responsive-text-base {
            font-size: 1rem;
        }
        
        .responsive-text-lg {
            font-size: 1.125rem;
        }
        
        .responsive-text-xl {
            font-size: 1.25rem;
        }
        
        .responsive-text-2xl {
            font-size: 1.5rem;
        }
        
        @media (min-width: 768px) {
            .responsive-text-lg {
                font-size: 1.25rem;
            }
            
            .responsive-text-xl {
                font-size: 1.5rem;
            }
            
            .responsive-text-2xl {
                font-size: 2rem;
            }
        }
        
        /* Responsive spacing */
        .responsive-p-xs { padding: 0.25rem; }
        .responsive-p-sm { padding: 0.5rem; }
        .responsive-p-md { padding: 1rem; }
        .responsive-p-lg { padding: 1.5rem; }
        .responsive-p-xl { padding: 2rem; }
        
        @media (min-width: 768px) {
            .responsive-p-md { padding: 1.5rem; }
            .responsive-p-lg { padding: 2rem; }
            .responsive-p-xl { padding: 3rem; }
        }
        
        /* Touch-friendly elements */
        .touch-friendly {
            min-height: 44px;
            min-width: 44px;
            touch-action: manipulation;
        }
        
        /* Mobile navigation */
        .mobile-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: white;
            border-top: 1px solid #e5e7eb;
            z-index: 1000;
            padding: 0.5rem;
        }
        
        .mobile-nav-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 0.5rem;
            text-decoration: none;
            color: #6b7280;
            font-size: 0.75rem;
        }
        
        .mobile-nav-item.active {
            color: #3b82f6;
        }
        
        /* Tablet optimizations */
        @media (min-width: 768px) and (max-width: 1023px) {
            .tablet-optimized {
                max-width: 90%;
                margin: 0 auto;
            }
        }
        
        /* Desktop optimizations */
        @media (min-width: 1024px) {
            .desktop-optimized {
                max-width: 1200px;
                margin: 0 auto;
            }
        }
        
        /* Landscape orientation */
        @media (orientation: landscape) and (max-height: 500px) {
            .landscape-optimized {
                padding: 0.5rem;
            }
        }
        
        /* Portrait orientation */
        @media (orientation: portrait) {
            .portrait-optimized {
                padding: 1rem;
            }
        }
        
        /* High DPI displays */
        @media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
            .high-dpi {
                image-rendering: -webkit-optimize-contrast;
                image-rendering: crisp-edges;
            }
        }
        
        /* Reduced motion */
        @media (prefers-reduced-motion: reduce) {
            .reduced-motion {
                animation: none !important;
                transition: none !important;
            }
        }
        
        /* Dark mode support */
        @media (prefers-color-scheme: dark) {
            .dark-mode-auto {
                background-color: #1f2937;
                color: #f9fafb;
            }
        }
        """

        ui.add_head_html(f"<style>{css}</style>")

    def add_viewport_meta(self):
        """Add viewport meta tag for responsive design."""
        viewport_meta = """
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <meta name="mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="default">
        """

        ui.add_head_html(viewport_meta)

    def detect_touch_support(self):
        """Detect touch support."""
        # This would detect actual touch support
        # For now, we'll assume touch is available on mobile
        self.touch_enabled = True

    def get_current_breakpoint(self) -> Breakpoint:
        """Get current breakpoint based on screen size."""
        # This would get actual screen size
        # For now, return a default
        return self.current_breakpoint

    def set_breakpoint(self, breakpoint: Breakpoint):
        """Set current breakpoint."""
        if self.current_breakpoint != breakpoint:
            self.current_breakpoint = breakpoint

            # Notify callbacks
            for callback in self.breakpoint_callbacks:
                try:
                    callback(breakpoint)
                except Exception as e:
                    print(f"Error in breakpoint callback: {e}")

    def on_breakpoint_change(self, callback: Callable[[Breakpoint], None]):
        """Register breakpoint change callback."""
        self.breakpoint_callbacks.append(callback)

    def create_responsive_container(
        self, config: ResponsiveConfig = None,
    ) -> ui.element:
        """Create a responsive container."""
        if config is None:
            config = ResponsiveConfig()

        container = ui.element("div").classes("responsive-container")

        # Apply responsive classes
        self.apply_responsive_config(container, config)

        return container

    def create_responsive_grid(
        self, columns: dict[Breakpoint, int] = None,
    ) -> ui.element:
        """Create a responsive grid."""
        if columns is None:
            columns = {
                Breakpoint.XS: 1,
                Breakpoint.SM: 2,
                Breakpoint.MD: 3,
                Breakpoint.LG: 4,
                Breakpoint.XL: 5,
                Breakpoint.XXL: 6,
            }

        grid = ui.element("div").classes("responsive-grid")

        # Apply column configuration
        for breakpoint, column_count in columns.items():
            if breakpoint == Breakpoint.XS:
                grid.style(f"grid-template-columns: repeat({column_count}, 1fr)")
            else:
                # Add media query styles
                min_width = self.get_breakpoint_width(breakpoint)
                grid.style(
                    f"@media (min-width: {min_width}px) {{ grid-template-columns: repeat({column_count}, 1fr); }}",
                )

        return grid

    def get_breakpoint_width(self, breakpoint: Breakpoint) -> int:
        """Get minimum width for breakpoint."""
        widths = {
            Breakpoint.XS: 0,
            Breakpoint.SM: 640,
            Breakpoint.MD: 768,
            Breakpoint.LG: 1024,
            Breakpoint.XL: 1280,
            Breakpoint.XXL: 1536,
        }
        return widths.get(breakpoint, 0)

    def apply_responsive_config(self, element: ui.element, config: ResponsiveConfig):
        """Apply responsive configuration to element."""
        # Apply classes for each breakpoint
        if config.xs:
            self.apply_breakpoint_classes(element, config.xs, "xs")
        if config.sm:
            self.apply_breakpoint_classes(element, config.sm, "sm")
        if config.md:
            self.apply_breakpoint_classes(element, config.md, "md")
        if config.lg:
            self.apply_breakpoint_classes(element, config.lg, "lg")
        if config.xl:
            self.apply_breakpoint_classes(element, config.xl, "xl")
        if config.xxl:
            self.apply_breakpoint_classes(element, config.xxl, "2xl")

    def apply_breakpoint_classes(
        self, element: ui.element, config: dict[str, Any], breakpoint: str,
    ):
        """Apply breakpoint-specific classes."""
        for key, value in config.items():
            if key == "classes":
                if isinstance(value, str):
                    element.classes(f"{breakpoint}:{value}")
                elif isinstance(value, list):
                    for cls in value:
                        element.classes(f"{breakpoint}:{cls}")
            elif key == "style":
                if isinstance(value, str):
                    element.style(
                        f"@media (min-width: {self.get_breakpoint_width(Breakpoint(breakpoint))}px) {{ {value} }}",
                    )

    def create_mobile_navigation(self, items: list[dict[str, Any]]) -> ui.element:
        """Create mobile navigation bar."""
        nav = ui.element("nav").classes("mobile-nav")

        with nav:
            for item in items:
                nav_item = ui.link(
                    item["text"],
                    item["href"],
                    icon=item.get("icon", ""),
                ).classes("mobile-nav-item")

                if item.get("active", False):
                    nav_item.classes("active")

        return nav

    def create_responsive_card(
        self, title: str, content, config: ResponsiveConfig = None,
    ) -> ui.element:
        """Create a responsive card."""
        if config is None:
            config = ResponsiveConfig(
                xs={"classes": "p-2"},
                sm={"classes": "p-3"},
                md={"classes": "p-4"},
                lg={"classes": "p-6"},
            )

        card = ui.card().classes("responsive-card")
        self.apply_responsive_config(card, config)

        with card:
            ui.label(title).classes("text-lg font-medium mb-2")
            content_container = ui.element("div")
            with content_container:
                content()

        return card

    def create_responsive_table(
        self, headers: list[str], data: list[list[str]], config: ResponsiveConfig = None,
    ) -> ui.element:
        """Create a responsive table."""
        if config is None:
            config = ResponsiveConfig(
                xs={"classes": "text-xs"},
                sm={"classes": "text-sm"},
                md={"classes": "text-base"},
            )

        table = ui.table(columns=headers, rows=data)
        self.apply_responsive_config(table, config)

        return table

    def create_responsive_form(
        self, fields: list[dict[str, Any]], config: ResponsiveConfig = None,
    ) -> ui.element:
        """Create a responsive form."""
        if config is None:
            config = ResponsiveConfig(
                xs={"classes": "space-y-2"},
                sm={"classes": "space-y-3"},
                md={"classes": "space-y-4"},
            )

        form = ui.element("form").classes("responsive-form")
        self.apply_responsive_config(form, config)

        with form:
            for field in fields:
                field_type = field.get("type", "input")

                if field_type == "input":
                    ui.input(
                        field.get("label", ""),
                        placeholder=field.get("placeholder", ""),
                        **field.get("props", {}),
                    ).classes("w-full")
                elif field_type == "textarea":
                    ui.textarea(
                        field.get("label", ""),
                        placeholder=field.get("placeholder", ""),
                        **field.get("props", {}),
                    ).classes("w-full")
                elif field_type == "select":
                    ui.select(
                        field.get("label", ""),
                        options=field.get("options", []),
                        **field.get("props", {}),
                    ).classes("w-full")

        return form

    def create_responsive_sidebar(
        self, items: list[dict[str, Any]], config: ResponsiveConfig = None,
    ) -> ui.element:
        """Create a responsive sidebar."""
        if config is None:
            config = ResponsiveConfig(
                xs={"classes": "hidden"},
                md={"classes": "block w-64"},
            )

        sidebar = ui.element("aside").classes("responsive-sidebar")
        self.apply_responsive_config(sidebar, config)

        with sidebar:
            for item in items:
                if item.get("type") == "header":
                    ui.label(item["text"]).classes(
                        "text-sm font-medium text-gray-500 uppercase tracking-wider px-3 py-2",
                    )
                elif item.get("type") == "link":
                    ui.link(
                        item["text"],
                        item["href"],
                        icon=item.get("icon", ""),
                    ).classes(
                        "flex items-center px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-md",
                    )
                elif item.get("type") == "divider":
                    ui.element("hr").classes("border-gray-200 my-2")

        return sidebar

    def create_responsive_header(
        self,
        title: str,
        actions: list[dict[str, Any]] = None,
        config: ResponsiveConfig = None,
    ) -> ui.element:
        """Create a responsive header."""
        if config is None:
            config = ResponsiveConfig(
                xs={"classes": "p-2"},
                sm={"classes": "p-3"},
                md={"classes": "p-4"},
            )

        header = ui.element("header").classes(
            "responsive-header bg-white border-b border-gray-200",
        )
        self.apply_responsive_config(header, config)

        with header:
            with ui.row().classes("items-center justify-between"):
                ui.label(title).classes("text-lg font-medium")

                if actions:
                    with ui.row().classes("space-x-2"):
                        for action in actions:
                            ui.button(
                                action["text"],
                                icon=action.get("icon", ""),
                                on_click=action.get("on_click"),
                            ).classes("touch-friendly")

        return header

    def create_responsive_dialog(
        self, title: str, content, config: ResponsiveConfig = None,
    ) -> ui.dialog:
        """Create a responsive dialog."""
        if config is None:
            config = ResponsiveConfig(
                xs={"classes": "w-full h-full"},
                sm={"classes": "w-96"},
                md={"classes": "w-lg"},
                lg={"classes": "w-xl"},
            )

        dialog = ui.dialog()

        with dialog:
            card = ui.card().classes("responsive-dialog")
            self.apply_responsive_config(card, config)

            with card:
                # Header
                with ui.row().classes("items-center justify-between mb-4"):
                    ui.label(title).classes("text-lg font-medium")
                    ui.button(icon="close", on_click=dialog.close).classes(
                        "touch-friendly",
                    )

                # Content
                content_container = ui.element("div")
                with content_container:
                    content()

        return dialog

    def is_mobile(self) -> bool:
        """Check if current viewport is mobile."""
        return self.current_breakpoint in [Breakpoint.XS, Breakpoint.SM]

    def is_tablet(self) -> bool:
        """Check if current viewport is tablet."""
        return self.current_breakpoint == Breakpoint.MD

    def is_desktop(self) -> bool:
        """Check if current viewport is desktop."""
        return self.current_breakpoint in [Breakpoint.LG, Breakpoint.XL, Breakpoint.XXL]

    def is_touch_device(self) -> bool:
        """Check if device supports touch."""
        return self.touch_enabled

    def get_orientation(self) -> str:
        """Get current device orientation."""
        return self.orientation

    def optimize_for_touch(self, element: ui.element):
        """Optimize element for touch interaction."""
        element.classes("touch-friendly")

    def optimize_for_mobile(self, element: ui.element):
        """Optimize element for mobile viewport."""
        element.classes("mobile-optimized")

    def optimize_for_tablet(self, element: ui.element):
        """Optimize element for tablet viewport."""
        element.classes("tablet-optimized")

    def optimize_for_desktop(self, element: ui.element):
        """Optimize element for desktop viewport."""
        element.classes("desktop-optimized")


# Global responsive layout instance
responsive_layout = ResponsiveLayout()
