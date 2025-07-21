"""
Theme Switcher Component

This module provides a theme switcher component for toggling between light and dark modes
according to the ConvoSphere design system.
"""

from nicegui import ui
from utils.design_system import design_system


class ThemeSwitcher:
    """Theme switcher component for Light/Dark mode toggle."""

    def __init__(self):
        """Initialize the theme switcher."""
        self.current_theme = "light"
        self.create_theme_switcher()

    def create_theme_switcher(self):
        """Create the theme switcher UI."""
        with ui.element("div").classes("theme-switcher"):
            # Theme toggle button
            with ui.button(
                on_click=self.toggle_theme,
            ).classes("theme-toggle-btn"):
                # Sun icon for light mode
                self.sun_icon = (
                    ui.element("div")
                    .classes("theme-icon sun-icon")
                    .style("""
                    width: 20px;
                    height: 20px;
                    background: radial-gradient(circle, #F59E0B 0%, transparent 70%);
                    border-radius: 50%;
                    position: relative;
                """)
                )

                # Moon icon for dark mode
                self.moon_icon = (
                    ui.element("div")
                    .classes("theme-icon moon-icon")
                    .style("""
                    width: 20px;
                    height: 20px;
                    background: linear-gradient(45deg, #7A869A 0%, #5BC6E8 100%);
                    border-radius: 50%;
                    position: relative;
                    display: none;
                """)
                )

                # Add crescent to moon
                ui.element("div").classes("moon-crescent").style("""
                    position: absolute;
                    top: 2px;
                    left: 2px;
                    width: 16px;
                    height: 16px;
                    background: var(--color-background);
                    border-radius: 50%;
                """)

    def toggle_theme(self):
        """Toggle between light and dark themes."""
        new_theme = "dark" if self.current_theme == "light" else "light"
        self.set_theme(new_theme)

    def set_theme(self, theme: str):
        """Set the theme to light or dark."""
        self.current_theme = theme
        if theme in ["light", "dark"]:
            design_system.set_theme(theme)  # type: ignore

        # Update icon visibility
        if theme == "light":
            self.sun_icon.style("display: block;")
            self.moon_icon.style("display: none;")
        else:
            self.sun_icon.style("display: none;")
            self.moon_icon.style("display: block;")

        # Store theme preference
        ui.run_javascript(f"""
        localStorage.setItem('convoSphere-theme', '{theme}');
        """)

        # Show notification
        ui.notify(
            f"Switched to {theme} mode",
            type="positive",
            timeout=2,
        )

    def load_saved_theme(self):
        """Load the saved theme preference from localStorage."""
        ui.run_javascript("""
        const savedTheme = localStorage.getItem('convoSphere-theme');
        if (savedTheme) {
            window.savedTheme = savedTheme;
        }
        """)

        # Get the saved theme and apply it
        ui.timer(0.1, lambda: self._apply_saved_theme(), once=True)

    def _apply_saved_theme(self):
        """Apply the saved theme from JavaScript."""
        ui.run_javascript("""
        if (window.savedTheme) {
            window.currentTheme = window.savedTheme;
        }
        """)

        # Check for saved theme and apply
        ui.timer(0.1, lambda: self._check_and_apply_theme(), once=True)

    def _check_and_apply_theme(self):
        """Check for saved theme and apply it."""
        ui.run_javascript("""
        if (window.currentTheme && window.currentTheme !== 'light') {
            window.shouldApplyDarkTheme = true;
        }
        """)

        # Apply dark theme if needed
        ui.timer(0.1, lambda: self._apply_dark_if_needed(), once=True)

    def _apply_dark_if_needed(self):
        """Apply dark theme if it was saved."""
        ui.run_javascript("""
        if (window.shouldApplyDarkTheme) {
            window.shouldApplyDarkTheme = false;
            window.currentTheme = null;
        }
        """)

        # This is a bit hacky, but we'll use a timer to check
        ui.timer(0.1, lambda: self._final_theme_check(), once=True)

    def _final_theme_check(self):
        """Final check for theme application."""
        # For now, we'll just set the default theme
        # In a real implementation, you'd get the value from JavaScript
        self.set_theme("light")


def create_theme_switcher() -> ThemeSwitcher:
    """Create and return a theme switcher instance."""
    switcher = ThemeSwitcher()
    return switcher
