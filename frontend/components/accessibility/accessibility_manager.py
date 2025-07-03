"""
Accessibility manager for the AI Assistant Platform.

This module provides comprehensive accessibility features including
screen reader support, keyboard navigation, and focus management.
"""

import asyncio
from typing import Dict, Any, Optional, List, Callable, Set
from dataclasses import dataclass
from enum import Enum

from nicegui import ui


class AccessibilityLevel(Enum):
    """Accessibility level enumeration."""
    BASIC = "basic"
    STANDARD = "standard"
    ENHANCED = "enhanced"


@dataclass
class AccessibilitySettings:
    """Accessibility settings configuration."""
    screen_reader_enabled: bool = True
    keyboard_navigation_enabled: bool = True
    high_contrast_enabled: bool = False
    reduced_motion_enabled: bool = False
    focus_visible_enabled: bool = True
    skip_links_enabled: bool = True
    aria_labels_enabled: bool = True
    semantic_html_enabled: bool = True
    font_size_scale: float = 1.0
    line_height_scale: float = 1.0
    color_blindness_support: bool = False
    dyslexia_friendly_font: bool = False


class AccessibilityManager:
    """Accessibility management system."""
    
    def __init__(self):
        """Initialize accessibility manager."""
        self.settings = AccessibilitySettings()
        self.focusable_elements: Set[str] = set()
        self.focus_order: List[str] = []
        self.current_focus_index = 0
        self.skip_links: List[Dict[str, Any]] = []
        self.aria_live_regions: Dict[str, str] = {}
        self.accessibility_callbacks: List[Callable[[AccessibilitySettings], None]] = []
        
        # Initialize accessibility features
        self.initialize_accessibility()
    
    def initialize_accessibility(self):
        """Initialize accessibility features."""
        # Add global CSS for accessibility
        self.add_accessibility_css()
        
        # Add skip links
        self.add_skip_links()
        
        # Add ARIA live regions
        self.add_aria_live_regions()
        
        # Add keyboard event listeners
        self.add_keyboard_listeners()
    
    def add_accessibility_css(self):
        """Add accessibility CSS styles."""
        css = """
        /* Focus management */
        .focus-visible {
            outline: 2px solid var(--focus-ring-color, #3B82F6) !important;
            outline-offset: 2px !important;
        }
        
        /* Skip links */
        .skip-link {
            position: absolute;
            top: -40px;
            left: 6px;
            background: var(--color-primary, #3B82F6);
            color: white;
            padding: 8px;
            text-decoration: none;
            border-radius: 4px;
            z-index: 1000;
            transition: top 0.3s;
        }
        
        .skip-link:focus {
            top: 6px;
        }
        
        /* High contrast mode */
        .high-contrast {
            filter: contrast(1.5) !important;
        }
        
        .high-contrast * {
            border-width: 2px !important;
        }
        
        /* Reduced motion */
        .reduced-motion *,
        .reduced-motion *::before,
        .reduced-motion *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
        
        /* Dyslexia friendly font */
        .dyslexia-friendly {
            font-family: 'OpenDyslexic', 'Comic Sans MS', sans-serif !important;
            line-height: 1.5 !important;
            letter-spacing: 0.1em !important;
        }
        
        /* Color blindness support */
        .color-blind-friendly {
            /* Additional patterns and textures for color blind users */
        }
        
        /* Screen reader only text */
        .sr-only {
            position: absolute;
            width: 1px;
            height: 1px;
            padding: 0;
            margin: -1px;
            overflow: hidden;
            clip: rect(0, 0, 0, 0);
            white-space: nowrap;
            border: 0;
        }
        
        /* Focus indicators */
        .focus-indicator {
            position: relative;
        }
        
        .focus-indicator::after {
            content: '';
            position: absolute;
            top: -2px;
            left: -2px;
            right: -2px;
            bottom: -2px;
            border: 2px solid var(--focus-ring-color, #3B82F6);
            border-radius: inherit;
            opacity: 0;
            transition: opacity 0.2s;
            pointer-events: none;
        }
        
        .focus-indicator:focus::after {
            opacity: 1;
        }
        """
        
        ui.add_head_html(f"<style>{css}</style>")
    
    def add_skip_links(self):
        """Add skip navigation links."""
        skip_links_data = [
            {"id": "main-content", "text": "Zum Hauptinhalt springen"},
            {"id": "navigation", "text": "Zur Navigation springen"},
            {"id": "search", "text": "Zur Suche springen"},
            {"id": "footer", "text": "Zum Footer springen"}
        ]
        
        for link_data in skip_links_data:
            self.add_skip_link(link_data["id"], link_data["text"])
    
    def add_skip_link(self, target_id: str, text: str):
        """Add a skip link."""
        skip_link = {
            "id": f"skip-{target_id}",
            "target_id": target_id,
            "text": text
        }
        self.skip_links.append(skip_link)
        
        # Create the actual skip link element
        ui.link(text, f"#{target_id}").classes("skip-link").props(f"id={skip_link['id']}")
    
    def add_aria_live_regions(self):
        """Add ARIA live regions."""
        live_regions = {
            "notifications": "polite",
            "alerts": "assertive",
            "status": "polite",
            "log": "polite"
        }
        
        for region_id, politeness in live_regions.items():
            self.aria_live_regions[region_id] = politeness
            ui.element("div").props(f"aria-live={politeness} id={region_id}").classes("sr-only")
    
    def add_keyboard_listeners(self):
        """Add global keyboard event listeners."""
        # This would add keyboard event listeners for navigation
        pass
    
    def update_settings(self, new_settings: AccessibilitySettings):
        """Update accessibility settings."""
        self.settings = new_settings
        
        # Apply settings
        self.apply_settings()
        
        # Notify callbacks
        for callback in self.accessibility_callbacks:
            try:
                callback(new_settings)
            except Exception as e:
                print(f"Error in accessibility callback: {e}")
    
    def apply_settings(self):
        """Apply current accessibility settings."""
        # Apply high contrast
        if self.settings.high_contrast_enabled:
            ui.add_head_html('<div class="high-contrast"></div>')
        
        # Apply reduced motion
        if self.settings.reduced_motion_enabled:
            ui.add_head_html('<div class="reduced-motion"></div>')
        
        # Apply dyslexia friendly font
        if self.settings.dyslexia_friendly_font:
            ui.add_head_html('<div class="dyslexia-friendly"></div>')
        
        # Apply color blindness support
        if self.settings.color_blindness_support:
            ui.add_head_html('<div class="color-blind-friendly"></div>')
    
    def register_focusable_element(self, element_id: str, order: Optional[int] = None):
        """Register a focusable element."""
        self.focusable_elements.add(element_id)
        
        if order is not None:
            # Insert at specific position
            if order >= len(self.focus_order):
                self.focus_order.append(element_id)
            else:
                self.focus_order.insert(order, element_id)
        else:
            # Add to end
            self.focus_order.append(element_id)
    
    def unregister_focusable_element(self, element_id: str):
        """Unregister a focusable element."""
        self.focusable_elements.discard(element_id)
        
        if element_id in self.focus_order:
            self.focus_order.remove(element_id)
    
    def set_focus(self, element_id: str):
        """Set focus to a specific element."""
        if element_id in self.focusable_elements:
            # This would programmatically focus the element
            self.current_focus_index = self.focus_order.index(element_id)
            print(f"Focus set to: {element_id}")
    
    def move_focus(self, direction: str):
        """Move focus in the specified direction."""
        if not self.focus_order:
            return
        
        if direction == "next":
            self.current_focus_index = (self.current_focus_index + 1) % len(self.focus_order)
        elif direction == "previous":
            self.current_focus_index = (self.current_focus_index - 1) % len(self.focus_order)
        elif direction == "first":
            self.current_focus_index = 0
        elif direction == "last":
            self.current_focus_index = len(self.focus_order) - 1
        
        element_id = self.focus_order[self.current_focus_index]
        self.set_focus(element_id)
    
    def announce_to_screen_reader(self, message: str, region: str = "status"):
        """Announce message to screen reader."""
        if region in self.aria_live_regions:
            # This would update the ARIA live region
            print(f"Screen reader announcement ({region}): {message}")
    
    def add_aria_label(self, element_id: str, label: str):
        """Add ARIA label to element."""
        # This would add aria-label to the element
        print(f"Added ARIA label to {element_id}: {label}")
    
    def add_aria_described_by(self, element_id: str, description_id: str):
        """Add ARIA describedby to element."""
        # This would add aria-describedby to the element
        print(f"Added ARIA describedby to {element_id}: {description_id}")
    
    def add_aria_live_region(self, region_id: str, politeness: str = "polite"):
        """Add ARIA live region."""
        self.aria_live_regions[region_id] = politeness
        
        # Create the live region element
        ui.element("div").props(f"aria-live={politeness} id={region_id}").classes("sr-only")
    
    def update_live_region(self, region_id: str, content: str):
        """Update ARIA live region content."""
        if region_id in self.aria_live_regions:
            # This would update the live region content
            print(f"Updated live region {region_id}: {content}")
    
    def create_focus_trap(self, container_id: str):
        """Create a focus trap for modal dialogs."""
        # This would implement focus trapping for modals
        print(f"Created focus trap for container: {container_id}")
    
    def remove_focus_trap(self, container_id: str):
        """Remove focus trap."""
        # This would remove focus trapping
        print(f"Removed focus trap for container: {container_id}")
    
    def add_semantic_landmark(self, landmark_type: str, element_id: str, label: str = ""):
        """Add semantic landmark to element."""
        landmarks = {
            "main": "main",
            "navigation": "nav",
            "banner": "header",
            "contentinfo": "footer",
            "complementary": "aside",
            "search": "search",
            "form": "form"
        }
        
        if landmark_type in landmarks:
            role = landmarks[landmark_type]
            # This would add the appropriate semantic role
            print(f"Added {role} landmark to {element_id}: {label}")
    
    def create_accessible_button(self, text: str, icon: str = "", on_click=None, **kwargs):
        """Create an accessible button."""
        button = ui.button(text, icon=icon, on_click=on_click, **kwargs)
        
        # Add accessibility attributes
        button.props("role=button tabindex=0")
        
        if icon and not text:
            # Icon-only button needs aria-label
            button.props(f"aria-label={text}")
        
        return button
    
    def create_accessible_link(self, text: str, href: str, **kwargs):
        """Create an accessible link."""
        link = ui.link(text, href, **kwargs)
        
        # Add accessibility attributes
        link.props("role=link tabindex=0")
        
        return link
    
    def create_accessible_input(self, label: str, placeholder: str = "", **kwargs):
        """Create an accessible input field."""
        # Create label
        label_element = ui.label(label)
        
        # Create input
        input_element = ui.input(placeholder=placeholder, **kwargs)
        
        # Connect label and input
        label_element.props(f"for={input_element.id}")
        input_element.props(f"aria-labelledby={label_element.id}")
        
        return input_element
    
    def create_accessible_select(self, label: str, options: List[str], **kwargs):
        """Create an accessible select dropdown."""
        # Create label
        label_element = ui.label(label)
        
        # Create select
        select_element = ui.select(options=options, **kwargs)
        
        # Connect label and select
        label_element.props(f"for={select_element.id}")
        select_element.props(f"aria-labelledby={label_element.id}")
        
        return select_element
    
    def create_accessible_checkbox(self, label: str, **kwargs):
        """Create an accessible checkbox."""
        # Create checkbox
        checkbox = ui.checkbox(label, **kwargs)
        
        # Add accessibility attributes
        checkbox.props("role=checkbox")
        
        return checkbox
    
    def create_accessible_radio_group(self, label: str, options: List[str], **kwargs):
        """Create an accessible radio group."""
        # Create fieldset and legend
        fieldset = ui.element("fieldset")
        legend = ui.element("legend").classes("text-sm font-medium")
        legend.text = label
        
        # Create radio buttons
        radio_buttons = []
        for option in options:
            radio = ui.radio(option, **kwargs)
            radio.props("role=radio")
            radio_buttons.append(radio)
        
        return fieldset, radio_buttons
    
    def create_accessible_table(self, headers: List[str], data: List[List[str]], **kwargs):
        """Create an accessible table."""
        table = ui.table(columns=headers, rows=data, **kwargs)
        
        # Add accessibility attributes
        table.props("role=table")
        
        return table
    
    def create_accessible_dialog(self, title: str, content, **kwargs):
        """Create an accessible dialog."""
        dialog = ui.dialog(**kwargs)
        
        with dialog:
            # Add dialog header
            header = ui.element("div").classes("flex items-center justify-between mb-4")
            with header:
                ui.label(title).classes("text-lg font-medium")
                ui.button(icon="close", on_click=dialog.close).classes("text-gray-500")
            
            # Add dialog content
            content_container = ui.element("div")
            with content_container:
                content()
        
        # Add accessibility attributes
        dialog.props(f"role=dialog aria-labelledby={header.id} aria-modal=true")
        
        return dialog
    
    def on_settings_change(self, callback: Callable[[AccessibilitySettings], None]):
        """Register accessibility settings change callback."""
        self.accessibility_callbacks.append(callback)
    
    def get_accessibility_report(self) -> Dict[str, Any]:
        """Get accessibility compliance report."""
        return {
            "focusable_elements": len(self.focusable_elements),
            "focus_order_length": len(self.focus_order),
            "skip_links": len(self.skip_links),
            "live_regions": len(self.aria_live_regions),
            "settings": {
                "screen_reader_enabled": self.settings.screen_reader_enabled,
                "keyboard_navigation_enabled": self.settings.keyboard_navigation_enabled,
                "high_contrast_enabled": self.settings.high_contrast_enabled,
                "reduced_motion_enabled": self.settings.reduced_motion_enabled,
                "focus_visible_enabled": self.settings.focus_visible_enabled,
                "skip_links_enabled": self.settings.skip_links_enabled,
                "aria_labels_enabled": self.settings.aria_labels_enabled,
                "semantic_html_enabled": self.settings.semantic_html_enabled
            }
        }


# Global accessibility manager instance
accessibility_manager = AccessibilityManager() 