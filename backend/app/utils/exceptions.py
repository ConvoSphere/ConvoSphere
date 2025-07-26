"""
Custom exceptions for the application.
"""


class ConvoSphereError(Exception):
    """Base exception for all application errors."""


class UserNotFoundError(ConvoSphereError):
    """Raised when a user is not found."""


class UserAlreadyExistsError(ConvoSphereError):
    """Raised when trying to create a user that already exists."""


class InvalidCredentialsError(ConvoSphereError):
    """Raised when authentication credentials are invalid."""


class PermissionDeniedError(ConvoSphereError):
    """Raised when user doesn't have required permissions."""


class UserLockedError(ConvoSphereError):
    """Raised when user account is locked."""


class GroupNotFoundError(ConvoSphereError):
    """Raised when a user group is not found."""


class AssistantNotFoundError(ConvoSphereError):
    """Raised when an assistant is not found."""


class ToolNotFoundError(ConvoSphereError):
    """Raised when a tool is not found."""


class ConversationNotFoundError(ConvoSphereError):
    """Raised when a conversation is not found."""


class MessageNotFoundError(ConvoSphereError):
    """Raised when a message is not found."""


class DatabaseError(ConvoSphereError):
    """Raised when there's a database-related error."""


class RedisError(ConvoSphereError):
    """Raised when there's a Redis-related error."""


class WeaviateError(ConvoSphereError):
    """Raised when there's a Weaviate-related error."""


class ValidationError(ConvoSphereError):
    """Raised when data validation fails."""


class ConfigurationError(ConvoSphereError):
    """Raised when there's a configuration error."""


class ExternalServiceError(ConvoSphereError):
    """Raised when an external service call fails."""


class RateLimitError(ConvoSphereError):
    """Raised when rate limit is exceeded."""


class FileUploadError(ConvoSphereError):
    """Raised when file upload fails."""


class ProcessingError(ConvoSphereError):
    """Raised when data processing fails."""


class AuthenticationError(ConvoSphereError):
    """Raised when authentication fails."""


class SSOConfigurationError(ConvoSphereError):
    """Raised when SSO configuration is invalid."""


class GroupSyncError(ConvoSphereError):
    """Raised when group synchronization fails."""


class DomainGroupNotFoundError(ConvoSphereError):
    """Raised when domain group is not found."""


class ResourceNotFoundError(ConvoSphereError):
    """Raised when resource is not found."""


class InvitationNotFoundError(ConvoSphereError):
    """Raised when invitation is not found."""


class InvalidAccessLevelError(ConvoSphereError):
    """Raised when access level is invalid."""


class SessionError(ConvoSphereError):
    """Raised when session operation fails."""


class SecurityError(ConvoSphereError):
    """Raised when security check fails."""


class AuditError(ConvoSphereError):
    """Raised when audit operation fails."""


class ComplianceError(ConvoSphereError):
    """Raised when compliance operation fails."""


class RetentionError(ConvoSphereError):
    """Raised when retention operation fails."""


class ArchiveError(ConvoSphereError):
    """Raised when archive operation fails."""


class AlertError(ConvoSphereError):
    """Raised when alert operation fails."""
