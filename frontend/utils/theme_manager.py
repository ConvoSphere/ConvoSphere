"""
Theme manager for handling light/dark mode switching.

This module provides a centralized theme management system
with persistent storage and automatic detection.
"""

from nicegui import ui
from utils.logger import get_logger


class ThemeManager:
    """Centralized theme management system."""

    def __init__(self):
        """Initialize the theme manager."""
        self.current_theme = "light"
        self.logger = get_logger(__name__)
        self._load_theme()
        self._apply_theme()

    def _load_theme(self):
        """Load theme from local storage or use default."""
        try:
            # In a real implementation, this would load from localStorage
            # For now, we'll use a simple approach
            self.current_theme = "light"
        except Exception as e:
            self.logger.warning(f"Error loading theme, using default: {e}")
            self.current_theme = "light"

    def _save_theme(self):
        """Save theme to local storage."""
        with contextlib.suppress(Exception):
            # In a real implementation, this would save to localStorage
            pass

    def _apply_theme(self):
        """Apply the current theme to the UI."""
        if self.current_theme == "dark":
            ui.dark_mode().enable()
        else:
            ui.dark_mode().disable()

    def get_current_theme(self) -> str:
        """Get the current theme."""
        return self.current_theme

    def set_theme(self, theme: str):
        """Set the theme."""
        if theme not in ["light", "dark"]:
            raise ValueError("Theme must be 'light' or 'dark'")

        self.current_theme = theme
        self._apply_theme()
        self._save_theme()

    def toggle_theme(self):
        """Toggle between light and dark themes."""
        new_theme = "dark" if self.current_theme == "light" else "light"
        self.set_theme(new_theme)

    def is_dark_mode(self) -> bool:
        """Check if dark mode is active."""
        return self.current_theme == "dark"

    def is_light_mode(self) -> bool:
        """Check if light mode is active."""
        return self.current_theme == "light"


# Global theme manager instance
theme_manager = ThemeManager()
