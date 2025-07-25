"""
Custom exceptions for the application.
"""


class ChatAssistantError(Exception):
    """Base exception for all application errors."""


class UserNotFoundError(ChatAssistantError):
    """Raised when a user is not found."""


class UserAlreadyExistsError(ChatAssistantError):
    """Raised when trying to create a user that already exists."""


class InvalidCredentialsError(ChatAssistantError):
    """Raised when authentication credentials are invalid."""


class PermissionDeniedError(ChatAssistantError):
    """Raised when user doesn't have required permissions."""


class UserLockedError(ChatAssistantError):
    """Raised when user account is locked."""


class GroupNotFoundError(ChatAssistantError):
    """Raised when a user group is not found."""


class AssistantNotFoundError(ChatAssistantError):
    """Raised when an assistant is not found."""


class ToolNotFoundError(ChatAssistantError):
    """Raised when a tool is not found."""


class ConversationNotFoundError(ChatAssistantError):
    """Raised when a conversation is not found."""


class MessageNotFoundError(ChatAssistantError):
    """Raised when a message is not found."""


class DatabaseError(ChatAssistantError):
    """Raised when there's a database-related error."""


class RedisError(ChatAssistantError):
    """Raised when there's a Redis-related error."""


class WeaviateError(ChatAssistantError):
    """Raised when there's a Weaviate-related error."""


class ValidationError(ChatAssistantError):
    """Raised when data validation fails."""


class ConfigurationError(ChatAssistantError):
    """Raised when there's a configuration error."""


class ExternalServiceError(ChatAssistantError):
    """Raised when an external service call fails."""


class RateLimitError(ChatAssistantError):
    """Raised when rate limit is exceeded."""


class FileUploadError(ChatAssistantError):
    """Raised when file upload fails."""


class ProcessingError(ChatAssistantError):
    """Raised when data processing fails."""


class AuthenticationError(ChatAssistantError):
    """Raised when authentication fails."""


class SSOConfigurationError(ChatAssistantError):
    """Raised when SSO configuration is invalid."""


class GroupSyncError(ChatAssistantError):
    """Raised when group synchronization fails."""


class DomainGroupNotFoundError(ChatAssistantError):
    """Raised when domain group is not found."""


class ResourceNotFoundError(ChatAssistantError):
    """Raised when resource is not found."""


class InvitationNotFoundError(ChatAssistantError):
    """Raised when invitation is not found."""


class InvalidAccessLevelError(ChatAssistantError):
    """Raised when access level is invalid."""


class SessionError(ChatAssistantError):
    """Raised when session operation fails."""


class SecurityError(ChatAssistantError):
    """Raised when security check fails."""
