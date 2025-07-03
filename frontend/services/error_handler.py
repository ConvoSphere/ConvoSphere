"""
Error handling service for the AI Assistant Platform.

This module provides centralized error handling and user-friendly
error messages for the frontend application.
"""

import asyncio
from typing import Optional, Dict, Any, Callable, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from nicegui import ui


class ErrorSeverity(Enum):
    """Error severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ErrorInfo:
    """Error information."""
    message: str
    severity: ErrorSeverity
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class ErrorHandler:
    """Centralized error handling service."""
    
    def __init__(self):
        """Initialize the error handler."""
        self.error_handlers: List[Callable[[ErrorInfo], None]] = []
        self.error_history: List[ErrorInfo] = []
        self.max_history = 100
        
    def handle_error(
        self,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        show_notification: bool = True
    ):
        """
        Handle an error.
        
        Args:
            message: Error message
            severity: Error severity level
            error_code: Optional error code
            details: Optional error details
            show_notification: Whether to show notification
        """
        error_info = ErrorInfo(
            message=message,
            severity=severity,
            error_code=error_code,
            details=details
        )
        
        # Add to history
        self.error_history.append(error_info)
        if len(self.error_history) > self.max_history:
            self.error_history.pop(0)
        
        # Notify handlers
        for handler in self.error_handlers:
            try:
                handler(error_info)
            except Exception as e:
                print(f"Error handler failed: {e}")
        
        # Show notification if requested
        if show_notification:
            self._show_notification(error_info)
    
    def handle_api_error(self, response, context: str = ""):
        """
        Handle API error response.
        
        Args:
            response: API response object
            context: Context where the error occurred
        """
        if not response.success:
            message = response.error or "Unknown API error"
            if context:
                message = f"{context}: {message}"
            
            # Determine severity based on status code
            if response.status_code >= 500:
                severity = ErrorSeverity.CRITICAL
            elif response.status_code >= 400:
                severity = ErrorSeverity.ERROR
            else:
                severity = ErrorSeverity.WARNING
            
            self.handle_error(
                message=message,
                severity=severity,
                error_code=f"API_{response.status_code}",
                details={
                    "status_code": response.status_code,
                    "context": context
                }
            )
    
    def handle_network_error(self, error: Exception, context: str = ""):
        """
        Handle network-related errors.
        
        Args:
            error: Network error exception
            context: Context where the error occurred
        """
        message = f"Network error: {str(error)}"
        if context:
            message = f"{context}: {message}"
        
        self.handle_error(
            message=message,
            severity=ErrorSeverity.ERROR,
            error_code="NETWORK_ERROR",
            details={
                "error_type": type(error).__name__,
                "context": context
            }
        )
    
    def handle_validation_error(self, field: str, message: str):
        """
        Handle validation errors.
        
        Args:
            field: Field that failed validation
            message: Validation message
        """
        self.handle_error(
            message=f"Validation error in {field}: {message}",
            severity=ErrorSeverity.WARNING,
            error_code="VALIDATION_ERROR",
            details={"field": field}
        )
    
    def handle_authentication_error(self, message: str = "Authentication failed"):
        """
        Handle authentication errors.
        
        Args:
            message: Authentication error message
        """
        self.handle_error(
            message=message,
            severity=ErrorSeverity.ERROR,
            error_code="AUTH_ERROR"
        )
    
    def handle_permission_error(self, resource: str = "resource"):
        """
        Handle permission errors.
        
        Args:
            resource: Resource that requires permission
        """
        self.handle_error(
            message=f"You don't have permission to access this {resource}",
            severity=ErrorSeverity.ERROR,
            error_code="PERMISSION_ERROR",
            details={"resource": resource}
        )
    
    def _show_notification(self, error_info: ErrorInfo):
        """Show error notification to user."""
        notification_type = error_info.severity.value
        
        # Map severity to notification type
        if error_info.severity == ErrorSeverity.INFO:
            ui.notify(error_info.message, type="info")
        elif error_info.severity == ErrorSeverity.WARNING:
            ui.notify(error_info.message, type="warning")
        elif error_info.severity == ErrorSeverity.ERROR:
            ui.notify(error_info.message, type="negative")
        elif error_info.severity == ErrorSeverity.CRITICAL:
            ui.notify(error_info.message, type="negative")
    
    def add_error_handler(self, handler: Callable[[ErrorInfo], None]):
        """Add error handler."""
        self.error_handlers.append(handler)
    
    def remove_error_handler(self, handler: Callable[[ErrorInfo], None]):
        """Remove error handler."""
        if handler in self.error_handlers:
            self.error_handlers.remove(handler)
    
    def get_error_history(self, severity: Optional[ErrorSeverity] = None) -> List[ErrorInfo]:
        """
        Get error history.
        
        Args:
            severity: Filter by severity level
            
        Returns:
            List of error information
        """
        if severity:
            return [error for error in self.error_history if error.severity == severity]
        return self.error_history.copy()
    
    def clear_error_history(self):
        """Clear error history."""
        self.error_history.clear()
    
    def get_error_summary(self) -> Dict[str, int]:
        """
        Get error summary by severity.
        
        Returns:
            Dictionary with error counts by severity
        """
        summary = {}
        for severity in ErrorSeverity:
            summary[severity.value] = len([
                error for error in self.error_history 
                if error.severity == severity
            ])
        return summary


# Global error handler instance
error_handler = ErrorHandler()


# Convenience functions
def handle_error(message: str, severity: ErrorSeverity = ErrorSeverity.ERROR, **kwargs):
    """Convenience function to handle errors."""
    error_handler.handle_error(message, severity, **kwargs)


def handle_api_error(response, context: str = ""):
    """Convenience function to handle API errors."""
    error_handler.handle_api_error(response, context)


def handle_network_error(error: Exception, context: str = ""):
    """Convenience function to handle network errors."""
    error_handler.handle_network_error(error, context)


def handle_validation_error(field: str, message: str):
    """Convenience function to handle validation errors."""
    error_handler.handle_validation_error(field, message)


def handle_authentication_error(message: str = "Authentication failed"):
    """Convenience function to handle authentication errors."""
    error_handler.handle_authentication_error(message)


def handle_permission_error(resource: str = "resource"):
    """Convenience function to handle permission errors."""
    error_handler.handle_permission_error(resource) 