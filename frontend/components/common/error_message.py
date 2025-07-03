"""
Error message component for the AI Assistant Platform.

This module provides a reusable error message component with
different styles and severity levels.
"""

from nicegui import ui
from typing import Optional, Callable
from enum import Enum


class ErrorSeverity(Enum):
    """Error severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorMessage:
    """Reusable error message component."""
    
    def __init__(
        self,
        message: str = "",
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        dismissible: bool = True,
        on_dismiss: Optional[Callable] = None
    ):
        """
        Initialize error message.
        
        Args:
            message: Error message
            severity: Error severity level
            dismissible: Whether message can be dismissed
            on_dismiss: Callback when message is dismissed
        """
        self.message = message
        self.severity = severity
        self.dismissible = dismissible
        self.on_dismiss = on_dismiss
        self.container = None
        self.message_label = None
        self.dismiss_button = None
        
        self.create_error_message()
    
    def create_error_message(self):
        """Create the error message UI."""
        self.container = ui.element("div").classes(
            f"rounded-md p-4 mb-4 {self._get_severity_classes()}"
        )
        
        with self.container:
            with ui.row().classes("flex items-start"):
                # Icon
                ui.icon(self._get_icon()).classes(
                    f"flex-shrink-0 w-5 h-5 mt-0.5 {self._get_icon_classes()}"
                )
                
                # Message
                with ui.element("div").classes("ml-3 flex-1"):
                    self.message_label = ui.label(self.message).classes(
                        f"text-sm font-medium {self._get_text_classes()}"
                    )
                
                # Dismiss button
                if self.dismissible:
                    self.dismiss_button = ui.button(
                        icon="close",
                        on_click=self.dismiss
                    ).classes(
                        f"ml-auto -mx-1.5 -my-1.5 rounded-lg p-1.5 inline-flex h-8 w-8 {self._get_dismiss_classes()}"
                    )
    
    def _get_severity_classes(self) -> str:
        """Get CSS classes for severity level."""
        severity_classes = {
            ErrorSeverity.INFO: "bg-blue-50 border border-blue-200",
            ErrorSeverity.WARNING: "bg-yellow-50 border border-yellow-200",
            ErrorSeverity.ERROR: "bg-red-50 border border-red-200",
            ErrorSeverity.CRITICAL: "bg-red-100 border border-red-300"
        }
        return severity_classes.get(self.severity, "bg-red-50 border border-red-200")
    
    def _get_icon(self) -> str:
        """Get icon for severity level."""
        icon_map = {
            ErrorSeverity.INFO: "info",
            ErrorSeverity.WARNING: "warning",
            ErrorSeverity.ERROR: "error",
            ErrorSeverity.CRITICAL: "error_outline"
        }
        return icon_map.get(self.severity, "error")
    
    def _get_icon_classes(self) -> str:
        """Get CSS classes for icon."""
        icon_classes = {
            ErrorSeverity.INFO: "text-blue-400",
            ErrorSeverity.WARNING: "text-yellow-400",
            ErrorSeverity.ERROR: "text-red-400",
            ErrorSeverity.CRITICAL: "text-red-500"
        }
        return icon_classes.get(self.severity, "text-red-400")
    
    def _get_text_classes(self) -> str:
        """Get CSS classes for text."""
        text_classes = {
            ErrorSeverity.INFO: "text-blue-800",
            ErrorSeverity.WARNING: "text-yellow-800",
            ErrorSeverity.ERROR: "text-red-800",
            ErrorSeverity.CRITICAL: "text-red-900"
        }
        return text_classes.get(self.severity, "text-red-800")
    
    def _get_dismiss_classes(self) -> str:
        """Get CSS classes for dismiss button."""
        dismiss_classes = {
            ErrorSeverity.INFO: "bg-blue-50 text-blue-500 hover:bg-blue-100",
            ErrorSeverity.WARNING: "bg-yellow-50 text-yellow-500 hover:bg-yellow-100",
            ErrorSeverity.ERROR: "bg-red-50 text-red-500 hover:bg-red-100",
            ErrorSeverity.CRITICAL: "bg-red-100 text-red-600 hover:bg-red-200"
        }
        return dismiss_classes.get(self.severity, "bg-red-50 text-red-500 hover:bg-red-100")
    
    def show(self):
        """Show the error message."""
        if self.container:
            self.container.classes("block")
    
    def hide(self):
        """Hide the error message."""
        if self.container:
            self.container.classes("hidden")
    
    def update_message(self, message: str, severity: Optional[ErrorSeverity] = None):
        """Update error message and optionally severity."""
        self.message = message
        if severity:
            self.severity = severity
        
        if self.message_label:
            self.message_label.text = message
            self.message_label.classes(f"text-sm font-medium {self._get_text_classes()}")
    
    def dismiss(self):
        """Dismiss the error message."""
        self.hide()
        if self.on_dismiss:
            self.on_dismiss()


def create_error_message(
    message: str,
    severity: ErrorSeverity = ErrorSeverity.ERROR,
    dismissible: bool = True,
    on_dismiss: Optional[Callable] = None
) -> ErrorMessage:
    """
    Create an error message.
    
    Args:
        message: Error message
        severity: Error severity level
        dismissible: Whether message can be dismissed
        on_dismiss: Callback when message is dismissed
        
    Returns:
        ErrorMessage instance
    """
    return ErrorMessage(message, severity, dismissible, on_dismiss)


def create_info_message(message: str, dismissible: bool = True) -> ErrorMessage:
    """
    Create an info message.
    
    Args:
        message: Info message
        dismissible: Whether message can be dismissed
        
    Returns:
        ErrorMessage instance
    """
    return ErrorMessage(message, ErrorSeverity.INFO, dismissible)


def create_warning_message(message: str, dismissible: bool = True) -> ErrorMessage:
    """
    Create a warning message.
    
    Args:
        message: Warning message
        dismissible: Whether message can be dismissed
        
    Returns:
        ErrorMessage instance
    """
    return ErrorMessage(message, ErrorSeverity.WARNING, dismissible)


def create_critical_message(message: str, dismissible: bool = False) -> ErrorMessage:
    """
    Create a critical error message.
    
    Args:
        message: Critical error message
        dismissible: Whether message can be dismissed
        
    Returns:
        ErrorMessage instance
    """
    return ErrorMessage(message, ErrorSeverity.CRITICAL, dismissible) 