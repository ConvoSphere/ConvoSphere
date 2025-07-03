"""
ConvoSphere Design System

This module implements the ConvoSphere brand guidelines including colors,
typography, spacing, and component styles with Light/Dark mode support.
"""

from typing import Dict, Any, Literal
from dataclasses import dataclass


@dataclass
class ConvoSphereLightPalette:
    """Light mode color palette according to brand guidelines."""
    
    # Primary Colors
    BACKGROUND = "#F7F9FB"         # White Smoke
    PRIMARY = "#23224A"            # Deep Indigo
    SECONDARY = "#5BC6E8"          # Soft Azure
    ACCENT = "#B6E74B"             # Accent Lime
    SURFACE = "#F5E9DD"            # Warm Sand
    TEXT = "#23224A"               # Deep Indigo
    TEXT_SECONDARY = "#7A869A"     # Slate Grey
    
    # Semantic Colors
    SUCCESS = "#10B981"            # Green for success states
    WARNING = "#F59E0B"            # Amber for warnings
    ERROR = "#EF4444"              # Red for errors
    INFO = "#3B82F6"               # Blue for information


@dataclass
class ConvoSphereDarkPalette:
    """Dark mode color palette according to brand guidelines."""
    
    # Primary Colors
    BACKGROUND = "#23224A"         # Deep Indigo
    BACKGROUND_SECONDARY = "#1A1A33"
    PRIMARY = "#5BC6E8"            # Soft Azure
    SECONDARY = "#5BC6E8"          # Soft Azure (same as primary in dark mode)
    ACCENT = "#B6E74B"             # Accent Lime (slightly desaturated)
    SURFACE = "#2D2D4D"
    TEXT = "#F7F9FB"               # White Smoke
    TEXT_SECONDARY = "#5BC6E8"     # Soft Azure
    
    # Semantic Colors
    SUCCESS = "#10B981"            # Green for success states
    WARNING = "#F59E0B"            # Amber for warnings
    ERROR = "#EF4444"              # Red for errors
    INFO = "#3B82F6"               # Blue for information


@dataclass
class ConvoSphereColors:
    """ConvoSphere color palette according to brand guidelines."""
    
    # Primary Colors
    DEEP_INDIGO = "#23224A"      # Intelligence, depth, trust
    SOFT_AZURE = "#5BC6E8"       # Dialogue, freshness, accessibility
    WARM_SAND = "#F5E9DD"        # Humanity, warmth, balance
    ACCENT_LIME = "#B6E74B"      # Innovation, energy, impulse
    
    # Secondary Colors
    SLATE_GREY = "#7A869A"       # Nuance, readability
    WHITE_SMOKE = "#F7F9FB"      # Purity, space
    
    # Semantic Colors
    SUCCESS = "#10B981"          # Green for success states
    WARNING = "#F59E0B"          # Amber for warnings
    ERROR = "#EF4444"            # Red for errors
    INFO = "#3B82F6"             # Blue for information


@dataclass
class ConvoSphereTypography:
    """Typography settings for ConvoSphere."""
    
    # Font Families
    PRIMARY_FONT = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    SECONDARY_FONT = "'IBM Plex Sans', sans-serif"
    MONO_FONT = "'Roboto Mono', 'Courier New', monospace"
    
    # Font Sizes
    XS = "0.75rem"      # 12px
    SM = "0.875rem"     # 14px
    BASE = "1rem"       # 16px
    LG = "1.125rem"     # 18px
    XL = "1.25rem"      # 20px
    XXL = "1.5rem"      # 24px
    XXXL = "1.875rem"   # 30px
    DISPLAY = "2.25rem" # 36px
    
    # Font Weights
    LIGHT = "300"
    REGULAR = "400"
    MEDIUM = "500"
    SEMIBOLD = "600"
    BOLD = "700"


@dataclass
class ConvoSphereSpacing:
    """Spacing system for consistent layout."""
    
    XS = "0.25rem"   # 4px
    SM = "0.5rem"    # 8px
    MD = "1rem"      # 16px
    LG = "1.5rem"    # 24px
    XL = "2rem"      # 32px
    XXL = "3rem"     # 48px
    XXXL = "4rem"    # 64px


@dataclass
class ConvoSphereShadows:
    """Shadow system for depth and elevation."""
    
    SM = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    MD = "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)"
    LG = "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"
    XL = "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)"


@dataclass
class ConvoSphereBorderRadius:
    """Border radius for rounded corners."""
    
    SM = "0.25rem"   # 4px
    MD = "0.375rem"  # 6px
    LG = "0.5rem"    # 8px
    XL = "0.75rem"   # 12px
    FULL = "9999px"  # Full circle


class ConvoSphereDesignSystem:
    """Main design system class that provides all brand elements."""
    
    def __init__(self):
        self.colors = ConvoSphereColors()
        self.light_palette = ConvoSphereLightPalette()
        self.dark_palette = ConvoSphereDarkPalette()
        self.typography = ConvoSphereTypography()
        self.spacing = ConvoSphereSpacing()
        self.shadows = ConvoSphereShadows()
        self.border_radius = ConvoSphereBorderRadius()
        self.current_theme = "light"
    
    def set_theme(self, theme: Literal["light", "dark"]):
        """Set the current theme and update CSS variables."""
        self.current_theme = theme
    
    def get_current_palette(self):
        """Get the current color palette based on theme."""
        return self.light_palette if self.current_theme == "light" else self.dark_palette
    
    def get_component_styles(self) -> Dict[str, str]:
        """Get component-specific styles."""
        palette = self.get_current_palette()
        
        return {
            "button_primary": f"""
                background: linear-gradient(135deg, {palette.SECONDARY} 0%, {palette.PRIMARY} 100%);
                color: {palette.TEXT if self.current_theme == "light" else palette.BACKGROUND};
                border: none;
                padding: {self.spacing.SM} {self.spacing.LG};
                border-radius: {self.border_radius.LG};
                font-family: {self.typography.PRIMARY_FONT};
                font-weight: {self.typography.SEMIBOLD};
                font-size: {self.typography.SM};
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: {self.shadows.MD};
            """,
            
            "button_secondary": f"""
                background: {palette.SURFACE};
                color: {palette.TEXT};
                border: 2px solid {palette.SECONDARY};
                padding: {self.spacing.SM} {self.spacing.LG};
                border-radius: {self.border_radius.LG};
                font-family: {self.typography.PRIMARY_FONT};
                font-weight: {self.typography.MEDIUM};
                font-size: {self.typography.SM};
                cursor: pointer;
                transition: all 0.3s ease;
            """,
            
            "card": f"""
                background: {palette.SURFACE};
                border-radius: {self.border_radius.XL};
                padding: {self.spacing.LG};
                box-shadow: {self.shadows.LG};
                border: 1px solid {getattr(palette, 'BACKGROUND_SECONDARY', palette.BACKGROUND)};
            """,
            
            "input": f"""
                background: {palette.BACKGROUND};
                border: 2px solid {palette.TEXT_SECONDARY};
                border-radius: {self.border_radius.MD};
                padding: {self.spacing.SM} {self.spacing.MD};
                font-family: {self.typography.PRIMARY_FONT};
                font-size: {self.typography.BASE};
                color: {palette.TEXT};
                transition: all 0.3s ease;
            """,
            
            "sidebar": f"""
                background: {palette.PRIMARY};
                color: {palette.TEXT if self.current_theme == "light" else palette.BACKGROUND};
                font-family: {self.typography.PRIMARY_FONT};
            """,
            
            "header": f"""
                background: {palette.BACKGROUND};
                border-bottom: 1px solid {palette.TEXT_SECONDARY};
                font-family: {self.typography.PRIMARY_FONT};
            """,
            
            "chat_user_bubble": f"""
                background: {palette.SECONDARY};
                color: {palette.TEXT if self.current_theme == "light" else palette.BACKGROUND};
                border-radius: {self.border_radius.LG};
                padding: {self.spacing.MD};
                margin: {self.spacing.SM} 0;
            """,
            
            "chat_ai_bubble": f"""
                background: {palette.SURFACE};
                color: {palette.TEXT};
                border-radius: {self.border_radius.LG};
                padding: {self.spacing.MD};
                margin: {self.spacing.SM} 0;
            """
        }
    
    def get_animation_styles(self) -> str:
        """Get animation and transition styles."""
        return """
        /* Smooth transitions */
        * {
            transition: all 0.3s ease;
        }
        
        /* Hover effects */
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(91, 198, 232, 0.4);
        }
        
        .btn-secondary:hover {
            background: var(--color-secondary);
            color: var(--color-background);
        }
        
        .card:hover {
            transform: translateY(-4px);
            box-shadow: var(--shadow-xl);
        }
        
        /* Loading animations */
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .loading {
            animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        
        /* Message animations */
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .message {
            animation: slideIn 0.3s ease-out;
        }
        
        /* Theme transition */
        * {
            transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
        }
        """


# Global design system instance
design_system = ConvoSphereDesignSystem() 