"""
Loading spinner component for the AI Assistant Platform.

This module provides a reusable loading spinner component with
different styles and sizes.
"""

from nicegui import ui


class LoadingSpinner:
    """Reusable loading spinner component."""

    def __init__(
        self,
        text: str = "Laden...",
        size: str = "md",
        color: str = "primary",
        full_screen: bool = False,
    ):
        """
        Initialize loading spinner.

        Args:
            text: Loading text
            size: Spinner size (sm, md, lg, xl)
            color: Spinner color
            full_screen: Whether to show as full screen overlay
        """
        self.text = text
        self.size = size
        self.color = color
        self.full_screen = full_screen
        self.container = None
        self.spinner = None
        self.text_label = None

        self.create_spinner()

    def create_spinner(self):
        """Create the spinner UI."""
        if self.full_screen:
            self.container = ui.element("div").classes(
                "fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50",
            )
        else:
            self.container = ui.element("div").classes(
                "flex items-center justify-center",
            )

        with self.container:
            with ui.element("div").classes("text-center"):
                # Spinner
                self.spinner = ui.spinner("dots").classes(self._get_size_classes())

                # Text
                if self.text:
                    self.text_label = ui.label(self.text).classes(
                        "mt-2 text-sm text-gray-600",
                    )

    def _get_size_classes(self) -> str:
        """Get CSS classes for spinner size."""
        size_classes = {
            "sm": "w-4 h-4",
            "md": "w-6 h-6",
            "lg": "w-8 h-8",
            "xl": "w-12 h-12",
        }
        return size_classes.get(self.size, "w-6 h-6")

    def show(self):
        """Show the spinner."""
        if self.container:
            self.container.classes("flex")

    def hide(self):
        """Hide the spinner."""
        if self.container:
            self.container.classes("hidden")

    def update_text(self, text: str):
        """Update loading text."""
        self.text = text
        if self.text_label:
            self.text_label.text = text


def create_loading_spinner(
    text: str = "Laden...",
    size: str = "md",
    color: str = "primary",
    full_screen: bool = False,
) -> LoadingSpinner:
    """
    Create a loading spinner.

    Args:
        text: Loading text
        size: Spinner size
        color: Spinner color
        full_screen: Whether to show as full screen overlay

    Returns:
        LoadingSpinner instance
    """
    return LoadingSpinner(text, size, color, full_screen)


def show_loading_overlay(text: str = "Laden...") -> LoadingSpinner:
    """
    Show a full screen loading overlay.

    Args:
        text: Loading text

    Returns:
        LoadingSpinner instance
    """
    return LoadingSpinner(text, size="lg", full_screen=True)


def create_button_loading_spinner() -> LoadingSpinner:
    """
    Create a small spinner for buttons.

    Returns:
        LoadingSpinner instance
    """
    return LoadingSpinner(text="", size="sm")


def create_card_loading_spinner() -> LoadingSpinner:
    """
    Create a medium spinner for cards.

    Returns:
        LoadingSpinner instance
    """
    return LoadingSpinner(text="Laden...", size="md")
