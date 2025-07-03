"""
Error handler for consistent error management.

This module provides centralized error handling with proper
logging, user feedback, and error recovery strategies.
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


class ErrorType(Enum):
    """Error types for categorization."""
    NETWORK = "network"
    AUTHENTICATION = "authentication"
    VALIDATION = "validation"
    PERMISSION = "permission"
    SERVER = "server"
    CLIENT = "client"
    UNKNOWN = "unknown"


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
    """Centralized error handler."""
    
    def __init__(self):
        """Initialize error handler."""
        self.error_handlers: Dict[ErrorType, List[Callable]] = {
            error_type: [] for error_type in ErrorType
        }
        self.global_handlers: List[Callable] = []
        self.error_notifications: List[Dict[str, Any]] = []
        self.max_notifications = 5
    
    def register_handler(self, error_type: ErrorType, handler: Callable):
        """Register error handler for specific error type."""
        if error_type not in self.error_handlers:
            self.error_handlers[error_type] = []
        self.error_handlers[error_type].append(handler)
    
    def register_global_handler(self, handler: Callable):
        """Register global error handler."""
        self.global_handlers.append(handler)
    
    async def handle_error(
        self,
        error: Exception,
        error_type: ErrorType = ErrorType.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Handle an error with proper logging and user feedback.
        
        Args:
            error: The exception that occurred
            error_type: Type of error for categorization
            severity: Severity level of the error
            context: Additional context information
        """
        error_info = {
            "error": error,
            "type": error_type,
            "severity": severity,
            "context": context or {},
            "timestamp": asyncio.get_event_loop().time()
        }
        
        # Log error
        self._log_error(error_info)
        
        # Call type-specific handlers
        if error_type in self.error_handlers:
            for handler in self.error_handlers[error_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(error_info)
                    else:
                        handler(error_info)
                except Exception as e:
                    print(f"Error in error handler: {e}")
        
        # Call global handlers
        for handler in self.global_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(error_info)
                else:
                    handler(error_info)
            except Exception as e:
                print(f"Error in global error handler: {e}")
        
        # Show user notification
        await self._show_error_notification(error_info)
    
    def _log_error(self, error_info: Dict[str, Any]):
        """Log error information."""
        error = error_info["error"]
        error_type = error_info["type"]
        severity = error_info["severity"]
        context = error_info["context"]
        
        log_message = f"[{severity.value.upper()}] {error_type.value}: {str(error)}"
        if context:
            log_message += f" | Context: {context}"
        
        print(log_message)
    
    async def _show_error_notification(self, error_info: Dict[str, Any]):
        """Show error notification to user."""
        error = error_info["error"]
        severity = error_info["severity"]
        context = error_info["context"]
        
        # Create user-friendly message
        if severity == ErrorSeverity.INFO:
            message = str(error)
            color = "info"
        elif severity == ErrorSeverity.WARNING:
            message = f"Warnung: {str(error)}"
            color = "warning"
        elif severity == ErrorSeverity.ERROR:
            message = f"Fehler: {str(error)}"
            color = "negative"
        else:  # CRITICAL
            message = f"Kritischer Fehler: {str(error)}"
            color = "negative"
        
        # Add context if available
        if context.get("action"):
            message = f"{context['action']} - {message}"
        
        # Create notification
        notification = {
            "message": message,
            "color": color,
            "timeout": 5000 if severity in [ErrorSeverity.INFO, ErrorSeverity.WARNING] else 10000,
            "timestamp": error_info["timestamp"]
        }
        
        # Add to notifications list
        self.error_notifications.append(notification)
        
        # Limit number of notifications
        if len(self.error_notifications) > self.max_notifications:
            self.error_notifications.pop(0)
        
        # Show notification using NiceGUI
        try:
            ui.notify(
                message,
                type=color,
                timeout=notification["timeout"]
            )
        except Exception as e:
            print(f"Failed to show notification: {e}")
    
    async def handle_network_error(self, error: Exception, action: str = ""):
        """Handle network-related errors."""
        await self.handle_error(
            error,
            ErrorType.NETWORK,
            ErrorSeverity.ERROR,
            {"action": action}
        )
    
    async def handle_auth_error(self, error: Exception, action: str = ""):
        """Handle authentication errors."""
        await self.handle_error(
            error,
            ErrorType.AUTHENTICATION,
            ErrorSeverity.ERROR,
            {"action": action}
        )
    
    async def handle_validation_error(self, error: Exception, action: str = ""):
        """Handle validation errors."""
        await self.handle_error(
            error,
            ErrorType.VALIDATION,
            ErrorSeverity.WARNING,
            {"action": action}
        )
    
    async def handle_permission_error(self, error: Exception, action: str = ""):
        """Handle permission errors."""
        await self.handle_error(
            error,
            ErrorType.PERMISSION,
            ErrorSeverity.ERROR,
            {"action": action}
        )
    
    async def handle_server_error(self, error: Exception, action: str = ""):
        """Handle server errors."""
        await self.handle_error(
            error,
            ErrorType.SERVER,
            ErrorSeverity.ERROR,
            {"action": action}
        )
    
    def get_error_notifications(self) -> List[Dict[str, Any]]:
        """Get current error notifications."""
        return self.error_notifications.copy()
    
    def clear_notifications(self):
        """Clear all error notifications."""
        self.error_notifications.clear()
    
    def create_error_boundary(self, fallback_ui=None):
        """Create error boundary for UI components."""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    await self.handle_error(e, ErrorType.CLIENT, ErrorSeverity.ERROR)
                    if fallback_ui:
                        return fallback_ui()
                    return None
            return wrapper
        return decorator


# Global error handler instance
error_handler = ErrorHandler()


# Convenience functions
async def handle_network_error(error: Exception, action: str = ""):
    """Handle network error."""
    await error_handler.handle_network_error(error, action)


async def handle_auth_error(error: Exception, action: str = ""):
    """Handle authentication error."""
    await error_handler.handle_auth_error(error, action)


async def handle_validation_error(error: Exception, action: str = ""):
    """Handle validation error."""
    await error_handler.handle_validation_error(error, action)


async def handle_permission_error(error: Exception, action: str = ""):
    """Handle permission error."""
    await error_handler.handle_permission_error(error, action)


async def handle_server_error(error: Exception, action: str = ""):
    """Handle server error."""
    await error_handler.handle_server_error(error, action)


async def handle_api_error(error: Exception, action: str = ""):
    """Handle API error."""
    await error_handler.handle_error(
        error,
        ErrorType.SERVER,
        ErrorSeverity.ERROR,
        {"action": action}
    ) 