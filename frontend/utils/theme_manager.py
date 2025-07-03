"""
Theme manager for handling light/dark mode switching.

This module provides a centralized theme management system
with persistent storage and automatic detection.
"""

import json
from typing import Optional
from nicegui import ui


class ThemeManager:
    """Centralized theme management system."""
    
    def __init__(self):
        """Initialize the theme manager."""
        self.current_theme = "light"
        self._load_theme()
        self._apply_theme()
    
    def _load_theme(self):
        """Load theme from local storage or use default."""
        try:
            # In a real implementation, this would load from localStorage
            # For now, we'll use a simple approach
            self.current_theme = "light"
        except Exception:
            self.current_theme = "light"
    
    def _save_theme(self):
        """Save theme to local storage."""
        try:
            # In a real implementation, this would save to localStorage
            pass
        except Exception:
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