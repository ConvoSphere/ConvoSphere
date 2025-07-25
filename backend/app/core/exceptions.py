"""
Standardized exception handling for the AI Assistant Platform.

This module provides consistent error handling across all services
with structured error responses and proper logging.
"""

from typing import Any


class ChatError(Exception):
    """Base exception for chat and agent related errors."""

    def __init__(
        self,
        message: str,
        error_code: str,
        details: dict[str, Any] | None = None,
        status_code: int = 500,
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary for API response."""
        return {
            "error": {
                "code": self.error_code,
                "message": self.message,
                "details": self.details,
            },
        }


class ValidationError(ChatError):
    """Exception for validation errors."""

    def __init__(self, field: str, message: str, value: Any = None):
        details = {"field": field, "message": message}
        if value is not None:
            details["value"] = str(value)

        super().__init__(
            f"Validation error in field '{field}': {message}",
            "VALIDATION_ERROR",
            details,
            status_code=400,
        )


class AuthenticationError(ChatError):
    """Exception for authentication errors."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message,
            "AUTHENTICATION_ERROR",
            status_code=401,
        )


class AuthorizationError(ChatError):
    """Exception for authorization errors."""

    def __init__(self, message: str = "Access denied"):
        super().__init__(
            message,
            "AUTHORIZATION_ERROR",
            status_code=403,
        )


class NotFoundError(ChatError):
    """Exception for resource not found errors."""

    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            f"{resource} with id '{resource_id}' not found",
            "NOT_FOUND_ERROR",
            {"resource": resource, "resource_id": resource_id},
            status_code=404,
        )


class ConversationError(ChatError):
    """Exception for conversation related errors."""

    def __init__(self, message: str, conversation_id: str | None = None):
        details = {}
        if conversation_id:
            details["conversation_id"] = conversation_id

        super().__init__(
            message,
            "CONVERSATION_ERROR",
            details,
            status_code=400,
        )


class AssistantError(ChatError):
    """Exception for assistant related errors."""

    def __init__(self, message: str, assistant_id: str | None = None):
        details = {}
        if assistant_id:
            details["assistant_id"] = assistant_id

        super().__init__(
            message,
            "ASSISTANT_ERROR",
            details,
            status_code=400,
        )


class AIError(ChatError):
    """Exception for AI service errors."""

    def __init__(
        self,
        message: str,
        model: str | None = None,
        provider: str | None = None,
    ):
        details = {}
        if model:
            details["model"] = model
        if provider:
            details["provider"] = provider

        super().__init__(
            message,
            "AI_ERROR",
            details,
            status_code=500,
        )


class ToolError(ChatError):
    """Exception for tool execution errors."""

    def __init__(
        self,
        message: str,
        tool_name: str | None = None,
        tool_input: dict[str, Any] | None = None,
    ):
        details = {}
        if tool_name:
            details["tool_name"] = tool_name
        if tool_input:
            details["tool_input"] = tool_input

        super().__init__(
            message,
            "TOOL_ERROR",
            details,
            status_code=500,
        )


class RateLimitError(ChatError):
    """Exception for rate limiting errors."""

    def __init__(
        self, message: str = "Rate limit exceeded", retry_after: int | None = None,
    ):
        details = {}
        if retry_after:
            details["retry_after"] = retry_after

        super().__init__(
            message,
            "RATE_LIMIT_ERROR",
            details,
            status_code=429,
        )


class DatabaseError(ChatError):
    """Exception for database errors."""

    def __init__(self, message: str, operation: str | None = None):
        details = {}
        if operation:
            details["operation"] = operation

        super().__init__(
            message,
            "DATABASE_ERROR",
            details,
            status_code=500,
        )


class ConfigurationError(ChatError):
    """Exception for configuration errors."""

    def __init__(self, message: str, config_key: str | None = None):
        details = {}
        if config_key:
            details["config_key"] = config_key

        super().__init__(
            message,
            "CONFIGURATION_ERROR",
            details,
            status_code=500,
        )


class WebSocketError(ChatError):
    """Exception for WebSocket related errors."""

    def __init__(self, message: str, connection_id: str | None = None):
        details = {}
        if connection_id:
            details["connection_id"] = connection_id

        super().__init__(
            message,
            "WEBSOCKET_ERROR",
            details,
            status_code=400,
        )


# Error code constants for consistent usage
ERROR_CODES = {
    "VALIDATION_ERROR": "VALIDATION_ERROR",
    "AUTHENTICATION_ERROR": "AUTHENTICATION_ERROR",
    "AUTHORIZATION_ERROR": "AUTHORIZATION_ERROR",
    "NOT_FOUND_ERROR": "NOT_FOUND_ERROR",
    "CONVERSATION_ERROR": "CONVERSATION_ERROR",
    "ASSISTANT_ERROR": "ASSISTANT_ERROR",
    "AI_ERROR": "AI_ERROR",
    "TOOL_ERROR": "TOOL_ERROR",
    "RATE_LIMIT_ERROR": "RATE_LIMIT_ERROR",
    "DATABASE_ERROR": "DATABASE_ERROR",
    "CONFIGURATION_ERROR": "CONFIGURATION_ERROR",
    "WEBSOCKET_ERROR": "WEBSOCKET_ERROR",
}
