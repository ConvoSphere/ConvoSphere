"""
Theme management system for the AI Assistant Platform.

This module provides comprehensive theme management including
light/dark mode, custom themes, and accessibility features.
"""

import json
import asyncio
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime

from nicegui import ui


class ThemeMode(Enum):
    """Theme mode enumeration."""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"


@dataclass
class ColorPalette:
    """Color palette for themes."""
    primary: str = "#3B82F6"
    primary_dark: str = "#1D4ED8"
    primary_light: str = "#93C5FD"
    secondary: str = "#6B7280"
    secondary_dark: str = "#374151"
    secondary_light: str = "#D1D5DB"
    success: str = "#10B981"
    warning: str = "#F59E0B"
    error: str = "#EF4444"
    info: str = "#3B82F6"
    
    # Background colors
    background: str = "#FFFFFF"
    background_secondary: str = "#F9FAFB"
    background_tertiary: str = "#F3F4F6"
    
    # Text colors
    text_primary: str = "#111827"
    text_secondary: str = "#6B7280"
    text_tertiary: str = "#9CA3AF"
    
    # Border colors
    border: str = "#E5E7EB"
    border_secondary: str = "#D1D5DB"
    
    # Shadow colors
    shadow: str = "rgba(0, 0, 0, 0.1)"
    shadow_dark: str = "rgba(0, 0, 0, 0.25)"


@dataclass
class DarkColorPalette:
    """Dark theme color palette."""
    primary: str = "#60A5FA"
    primary_dark: str = "#3B82F6"
    primary_light: str = "#93C5FD"
    secondary: str = "#9CA3AF"
    secondary_dark: str = "#6B7280"
    secondary_light: str = "#D1D5DB"
    success: str = "#34D399"
    warning: str = "#FBBF24"
    error: str = "#F87171"
    info: str = "#60A5FA"
    
    # Background colors
    background: str = "#111827"
    background_secondary: str = "#1F2937"
    background_tertiary: str = "#374151"
    
    # Text colors
    text_primary: str = "#F9FAFB"
    text_secondary: str = "#D1D5DB"
    text_tertiary: str = "#9CA3AF"
    
    # Border colors
    border: str = "#374151"
    border_secondary: str = "#4B5563"
    
    # Shadow colors
    shadow: str = "rgba(0, 0, 0, 0.3)"
    shadow_dark: str = "rgba(0, 0, 0, 0.5)"


@dataclass
class Theme:
    """Theme configuration."""
    name: str
    mode: ThemeMode
    colors: ColorPalette
    font_family: str = "Inter, system-ui, sans-serif"
    font_size_base: str = "16px"
    font_size_small: str = "14px"
    font_size_large: str = "18px"
    border_radius: str = "8px"
    border_radius_small: str = "4px"
    border_radius_large: str = "12px"
    spacing_unit: str = "4px"
    transition_duration: str = "0.2s"
    box_shadow: str = "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)"
    box_shadow_large: str = "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"
    
    # Accessibility
    high_contrast: bool = False
    reduced_motion: bool = False
    focus_ring_color: str = "#3B82F6"
    focus_ring_width: str = "2px"


class ThemeManager:
    """Theme management system."""
    
    def __init__(self):
        """Initialize theme manager."""
        self.current_theme: Optional[Theme] = None
        self.current_mode: ThemeMode = ThemeMode.LIGHT
        self.system_prefers_dark: bool = False
        self.theme_change_callbacks: List[Callable[[Theme], None]] = []
        
        # Default themes
        self.light_theme = Theme(
            name="Light",
            mode=ThemeMode.LIGHT,
            colors=ColorPalette()
        )
        
        self.dark_theme = Theme(
            name="Dark",
            mode=ThemeMode.DARK,
            colors=DarkColorPalette()
        )
        
        # High contrast themes
        self.light_high_contrast = Theme(
            name="Light High Contrast",
            mode=ThemeMode.LIGHT,
            colors=ColorPalette(
                primary="#000000",
                text_primary="#000000",
                text_secondary="#333333",
                background="#FFFFFF",
                border="#000000"
            ),
            high_contrast=True
        )
        
        self.dark_high_contrast = Theme(
            name="Dark High Contrast",
            mode=ThemeMode.DARK,
            colors=DarkColorPalette(
                primary="#FFFFFF",
                text_primary="#FFFFFF",
                text_secondary="#CCCCCC",
                background="#000000",
                border="#FFFFFF"
            ),
            high_contrast=True
        )
        
        # Initialize with light theme
        self.set_theme(self.light_theme)
        
        # Check system preference
        self.check_system_preference()
    
    def check_system_preference(self):
        """Check system dark mode preference."""
        try:
            # This would check the actual system preference
            # For now, we'll use a default value
            self.system_prefers_dark = False
        except Exception:
            self.system_prefers_dark = False
    
    def set_theme(self, theme: Theme):
        """Set current theme."""
        self.current_theme = theme
        self.current_mode = theme.mode
        
        # Apply theme to UI
        self.apply_theme(theme)
        
        # Notify callbacks
        for callback in self.theme_change_callbacks:
            try:
                callback(theme)
            except Exception as e:
                print(f"Error in theme change callback: {e}")
    
    def set_mode(self, mode: ThemeMode):
        """Set theme mode."""
        if mode == ThemeMode.AUTO:
            # Use system preference
            if self.system_prefers_dark:
                self.set_theme(self.dark_theme)
            else:
                self.set_theme(self.light_theme)
        elif mode == ThemeMode.DARK:
            self.set_theme(self.dark_theme)
        else:
            self.set_theme(self.light_theme)
    
    def toggle_mode(self):
        """Toggle between light and dark mode."""
        if self.current_mode == ThemeMode.LIGHT:
            self.set_mode(ThemeMode.DARK)
        else:
            self.set_mode(ThemeMode.LIGHT)
    
    def set_high_contrast(self, enabled: bool):
        """Enable or disable high contrast mode."""
        if enabled:
            if self.current_mode == ThemeMode.DARK:
                self.set_theme(self.dark_high_contrast)
            else:
                self.set_theme(self.light_high_contrast)
        else:
            if self.current_mode == ThemeMode.DARK:
                self.set_theme(self.dark_theme)
            else:
                self.set_theme(self.light_theme)
    
    def apply_theme(self, theme: Theme):
        """Apply theme to the UI."""
        try:
            # Generate CSS variables
            css_vars = self.generate_css_variables(theme)
            
            # Apply to document
            self.apply_css_variables(css_vars)
            
            # Apply accessibility features
            self.apply_accessibility_features(theme)
            
        except Exception as e:
            print(f"Error applying theme: {e}")
    
    def generate_css_variables(self, theme: Theme) -> Dict[str, str]:
        """Generate CSS variables from theme."""
        colors = theme.colors
        
        return {
            # Colors
            "--color-primary": colors.primary,
            "--color-primary-dark": colors.primary_dark,
            "--color-primary-light": colors.primary_light,
            "--color-secondary": colors.secondary,
            "--color-secondary-dark": colors.secondary_dark,
            "--color-secondary-light": colors.secondary_light,
            "--color-success": colors.success,
            "--color-warning": colors.warning,
            "--color-error": colors.error,
            "--color-info": colors.info,
            
            # Background colors
            "--color-background": colors.background,
            "--color-background-secondary": colors.background_secondary,
            "--color-background-tertiary": colors.background_tertiary,
            
            # Text colors
            "--color-text-primary": colors.text_primary,
            "--color-text-secondary": colors.text_secondary,
            "--color-text-tertiary": colors.text_tertiary,
            
            # Border colors
            "--color-border": colors.border,
            "--color-border-secondary": colors.border_secondary,
            
            # Shadow colors
            "--color-shadow": colors.shadow,
            "--color-shadow-dark": colors.shadow_dark,
            
            # Typography
            "--font-family": theme.font_family,
            "--font-size-base": theme.font_size_base,
            "--font-size-small": theme.font_size_small,
            "--font-size-large": theme.font_size_large,
            
            # Spacing and layout
            "--border-radius": theme.border_radius,
            "--border-radius-small": theme.border_radius_small,
            "--border-radius-large": theme.border_radius_large,
            "--spacing-unit": theme.spacing_unit,
            
            # Transitions
            "--transition-duration": theme.transition_duration,
            
            # Shadows
            "--box-shadow": theme.box_shadow,
            "--box-shadow-large": theme.box_shadow_large,
            
            # Focus
            "--focus-ring-color": theme.focus_ring_color,
            "--focus-ring-width": theme.focus_ring_width,
        }
    
    def apply_css_variables(self, css_vars: Dict[str, str]):
        """Apply CSS variables to document."""
        try:
            # Create CSS string
            css_string = ":root {\n"
            for var, value in css_vars.items():
                css_string += f"  {var}: {value};\n"
            css_string += "}\n"
            
            # Apply to document
            ui.add_head_html(f"<style>{css_string}</style>")
            
        except Exception as e:
            print(f"Error applying CSS variables: {e}")
    
    def apply_accessibility_features(self, theme: Theme):
        """Apply accessibility features."""
        try:
            # High contrast mode
            if theme.high_contrast:
                ui.add_head_html("""
                    <style>
                        * {
                            border-width: 2px !important;
                        }
                        .high-contrast {
                            filter: contrast(1.5) !important;
                        }
                    </style>
                """)
            
            # Reduced motion
            if theme.reduced_motion:
                ui.add_head_html("""
                    <style>
                        *, *::before, *::after {
                            animation-duration: 0.01ms !important;
                            animation-iteration-count: 1 !important;
                            transition-duration: 0.01ms !important;
                        }
                    </style>
                """)
            
        except Exception as e:
            print(f"Error applying accessibility features: {e}")
    
    def create_custom_theme(self, name: str, colors: ColorPalette, **kwargs) -> Theme:
        """Create a custom theme."""
        return Theme(
            name=name,
            mode=ThemeMode.LIGHT,
            colors=colors,
            **kwargs
        )
    
    def get_theme_preview(self, theme: Theme) -> Dict[str, Any]:
        """Get theme preview data."""
        return {
            "name": theme.name,
            "mode": theme.mode.value,
            "colors": asdict(theme.colors),
            "high_contrast": theme.high_contrast,
            "reduced_motion": theme.reduced_motion
        }
    
    def export_theme(self, theme: Theme) -> str:
        """Export theme as JSON."""
        return json.dumps(self.get_theme_preview(theme), indent=2)
    
    def import_theme(self, theme_json: str) -> Optional[Theme]:
        """Import theme from JSON."""
        try:
            data = json.loads(theme_json)
            
            # Create color palette
            colors_data = data.get("colors", {})
            colors = ColorPalette(**colors_data)
            
            # Create theme
            theme = Theme(
                name=data.get("name", "Imported Theme"),
                mode=ThemeMode(data.get("mode", "light")),
                colors=colors,
                high_contrast=data.get("high_contrast", False),
                reduced_motion=data.get("reduced_motion", False)
            )
            
            return theme
            
        except Exception as e:
            print(f"Error importing theme: {e}")
            return None
    
    def on_theme_change(self, callback: Callable[[Theme], None]):
        """Register theme change callback."""
        self.theme_change_callbacks.append(callback)
    
    def get_available_themes(self) -> List[Theme]:
        """Get list of available themes."""
        return [
            self.light_theme,
            self.dark_theme,
            self.light_high_contrast,
            self.dark_high_contrast
        ]
    
    def get_current_theme_info(self) -> Dict[str, Any]:
        """Get current theme information."""
        if not self.current_theme:
            return {}
        
        return {
            "name": self.current_theme.name,
            "mode": self.current_theme.mode.value,
            "high_contrast": self.current_theme.high_contrast,
            "reduced_motion": self.current_theme.reduced_motion,
            "system_prefers_dark": self.system_prefers_dark
        }


# Global theme manager instance
theme_manager = ThemeManager() 