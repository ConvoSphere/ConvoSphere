"""
ConvoSphere Logo Component

This module provides the ConvoSphere logo and branding elements
according to the brand guidelines.
"""

from nicegui import ui
from utils.design_system import design_system


class ConvoSphereLogo:
    """ConvoSphere logo component with different variants."""
    
    def __init__(self):
        self.colors = design_system.colors
        self.typography = design_system.typography
    
    def create_full_logo(self, size: str = "medium") -> ui.element:
        """Create the full ConvoSphere logo with text and icon."""
        size_classes = {
            "small": "text-lg",
            "medium": "text-2xl", 
            "large": "text-3xl"
        }
        
        with ui.element("div").classes(f"flex items-center gap-3 {size_classes.get(size, 'text-2xl')}"):
            # Icon (stylized sphere/dialogue bubble)
            with ui.element("div").classes("relative"):
                # Main sphere
                ui.element("div").classes(
                    "w-10 h-10 rounded-full bg-gradient-to-br from-soft-azure to-deep-indigo "
                    "flex items-center justify-center shadow-lg"
                ).style(f"""
                    background: linear-gradient(135deg, {self.colors.SOFT_AZURE} 0%, {self.colors.DEEP_INDIGO} 100%);
                    box-shadow: 0 4px 15px rgba(91, 198, 232, 0.3);
                """)
                
                # Accent dot
                ui.element("div").classes(
                    "absolute top-2 right-2 w-2 h-2 rounded-full bg-accent-lime"
                ).style(f"background: {self.colors.ACCENT_LIME};")
            
            # Text
            with ui.element("div").classes("flex flex-col"):
                ui.element("span").classes(
                    "font-bold text-deep-indigo leading-tight"
                ).style(f"""
                    font-family: {self.typography.PRIMARY_FONT};
                    font-weight: {self.typography.BOLD};
                    color: {self.colors.DEEP_INDIGO};
                """).text("Convo")
                
                ui.element("span").classes(
                    "font-light text-slate-grey leading-tight"
                ).style(f"""
                    font-family: {self.typography.PRIMARY_FONT};
                    font-weight: {self.typography.LIGHT};
                    color: {self.colors.SLATE_GREY};
                """).text("Sphere")
    
    def create_icon_only(self, size: str = "medium") -> ui.element:
        """Create icon-only version of the logo."""
        size_classes = {
            "small": "w-8 h-8",
            "medium": "w-10 h-10",
            "large": "w-12 h-12"
        }
        
        with ui.element("div").classes("relative"):
            # Main sphere
            ui.element("div").classes(
                f"{size_classes.get(size, 'w-10 h-10')} rounded-full "
                "bg-gradient-to-br from-soft-azure to-deep-indigo "
                "flex items-center justify-center shadow-lg"
            ).style(f"""
                background: linear-gradient(135deg, {self.colors.SOFT_AZURE} 0%, {self.colors.DEEP_INDIGO} 100%);
                box-shadow: 0 4px 15px rgba(91, 198, 232, 0.3);
            """)
            
            # Accent dot
            ui.element("div").classes(
                "absolute top-1 right-1 w-1.5 h-1.5 rounded-full bg-accent-lime"
            ).style(f"background: {self.colors.ACCENT_LIME};")
    
    def create_favicon(self) -> str:
        """Generate favicon HTML."""
        return f"""
        <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'>
            <defs>
                <linearGradient id='grad' x1='0%' y1='0%' x2='100%' y2='100%'>
                    <stop offset='0%' style='stop-color:{self.colors.SOFT_AZURE};stop-opacity:1' />
                    <stop offset='100%' style='stop-color:{self.colors.DEEP_INDIGO};stop-opacity:1' />
                </linearGradient>
            </defs>
            <circle cx='50' cy='50' r='45' fill='url(#grad)'/>
            <circle cx='75' cy='25' r='8' fill='{self.colors.ACCENT_LIME}'/>
        </svg>">
        """
    
    def create_brand_header(self) -> ui.element:
        """Create a complete brand header with logo and tagline."""
        with ui.element("div").classes("text-center py-8"):
            # Logo
            self.create_full_logo("large")
            
            # Tagline
            ui.element("p").classes(
                "mt-4 text-slate-grey text-lg font-light"
            ).style(f"""
                font-family: {self.typography.PRIMARY_FONT};
                font-weight: {self.typography.LIGHT};
                color: {self.colors.SLATE_GREY};
            """).text("Intelligente, empathische Kommunikation")


# Global logo instance
logo = ConvoSphereLogo() 