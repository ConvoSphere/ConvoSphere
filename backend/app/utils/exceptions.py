"""
Custom exceptions for the application.
"""


class ChatAssistantError(Exception):
    """Base exception for all application errors."""
    pass


class UserNotFoundError(ChatAssistantError):
    """Raised when a user is not found."""
    pass


class UserAlreadyExistsError(ChatAssistantError):
    """Raised when trying to create a user that already exists."""
    pass


class InvalidCredentialsError(ChatAssistantError):
    """Raised when authentication credentials are invalid."""
    pass


class PermissionDeniedError(ChatAssistantError):
    """Raised when user doesn't have required permissions."""
    pass


class UserLockedError(ChatAssistantError):
    """Raised when user account is locked."""
    pass


class GroupNotFoundError(ChatAssistantError):
    """Raised when a user group is not found."""
    pass


class AssistantNotFoundError(ChatAssistantError):
    """Raised when an assistant is not found."""
    pass


class ToolNotFoundError(ChatAssistantError):
    """Raised when a tool is not found."""
    pass


class ConversationNotFoundError(ChatAssistantError):
    """Raised when a conversation is not found."""
    pass


class MessageNotFoundError(ChatAssistantError):
    """Raised when a message is not found."""
    pass


class DatabaseError(ChatAssistantError):
    """Raised when there's a database-related error."""
    pass


class RedisError(ChatAssistantError):
    """Raised when there's a Redis-related error."""
    pass


class WeaviateError(ChatAssistantError):
    """Raised when there's a Weaviate-related error."""
    pass


class ValidationError(ChatAssistantError):
    """Raised when data validation fails."""
    pass


class ConfigurationError(ChatAssistantError):
    """Raised when there's a configuration error."""
    pass


class ExternalServiceError(ChatAssistantError):
    """Raised when an external service call fails."""
    pass


class RateLimitError(ChatAssistantError):
    """Raised when rate limit is exceeded."""
    pass


class FileUploadError(ChatAssistantError):
    """Raised when file upload fails."""
    pass


class ProcessingError(ChatAssistantError):
    """Raised when data processing fails."""
    pass 