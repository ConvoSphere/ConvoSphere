"""
Enhanced input validation for the AI Assistant Platform.

This module provides comprehensive input validation functions to prevent
injection attacks, ensure data integrity, and maintain security.
"""

import re
import uuid
from typing import Any
from urllib.parse import urlparse

from loguru import logger
from pydantic import BaseModel, Field, field_validator


class SecurityValidationError(Exception):
    """Exception for security validation errors."""


def validate_uuid(uuid_string: str) -> bool:
    """Validate UUID format."""
    try:
        uuid.UUID(uuid_string)
        return True
    except ValueError:
        return False


def validate_sql_injection(text: str) -> bool:
    """Check for SQL injection patterns."""
    sql_patterns = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
        r"(\b(UNION|JOIN|WHERE|FROM|INTO|VALUES)\b)",
        r"(--|\b(OR|AND)\b\s+\d+\s*=\s*\d+)",
        r"(\b(WAITFOR|DELAY)\b)",
        r"(\b(SLEEP|BENCHMARK)\b)",
        r"(\b(LOAD_FILE|INTO\s+OUTFILE)\b)",
    ]

    return all(not re.search(pattern, text, re.IGNORECASE) for pattern in sql_patterns)


def validate_xss_injection(text: str) -> bool:
    """Check for XSS injection patterns."""
    xss_patterns = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>",
        r"<object[^>]*>",
        r"<embed[^>]*>",
        r"<form[^>]*>",
        r"<input[^>]*>",
        r"<textarea[^>]*>",
        r"<select[^>]*>",
        r"<button[^>]*>",
        r"<link[^>]*>",
        r"<meta[^>]*>",
        r"<style[^>]*>",
        r"<base[^>]*>",
        r"<bgsound[^>]*>",
        r"<link[^>]*>",
        r"<meta[^>]*>",
        r"<title[^>]*>",
        r"<xmp[^>]*>",
        r"<plaintext[^>]*>",
        r"<listing[^>]*>",
    ]

    return all(not re.search(pattern, text, re.IGNORECASE) for pattern in xss_patterns)


def validate_path_traversal(path: str) -> bool:
    """Check for path traversal attempts."""
    dangerous_patterns = [
        "..",
        "~",
        "/etc/",
        "/proc/",
        "/sys/",
        "/dev/",
        "cmd",
        "exec",
        "system",
        "\\",
        "//",
    ]

    return all(pattern not in path for pattern in dangerous_patterns)


def validate_url(url_string: str) -> bool:
    """Validate URL format and security."""
    try:
        parsed = urlparse(url_string)
        # Check for dangerous protocols
        if parsed.scheme in ["file", "data", "javascript"]:
            return False
        # Check for localhost in production
        return parsed.netloc not in ["localhost", "127.0.0.1", "::1"]
    except Exception:
        return False


def validate_email(email: str) -> bool:
    """Validate email format and security."""
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, email):
        return False

    # Check for dangerous patterns
    dangerous_patterns = [
        r"<script",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe",
        r"<object",
        r"<embed",
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, email, re.IGNORECASE):
            return False

    return True


def validate_json_structure(data: dict[str, Any], max_depth: int = 5) -> bool:
    """Validate JSON structure to prevent deep nesting attacks."""

    def check_depth(obj: Any, current_depth: int = 0) -> bool:
        if current_depth > max_depth:
            return False

        if isinstance(obj, dict):
            for value in obj.values():
                if not check_depth(value, current_depth + 1):
                    return False
        elif isinstance(obj, list):
            for item in obj:
                if not check_depth(item, current_depth + 1):
                    return False

        return True

    return check_depth(data)


def sanitize_text(text: str, max_length: int = 10000) -> str:
    """Sanitize text input."""
    if not text:
        return ""

    # Remove null bytes
    text = text.replace("\x00", "")

    # Normalize whitespace
    text = " ".join(text.split())

    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length]

    return text


class SecureChatMessageRequest(BaseModel):
    """Secure request model for chat messages."""

    message: str = Field(
        ..., min_length=1, max_length=10000, description="User message"
    )
    assistant_id: str | None = Field(None, description="Assistant ID")
    use_knowledge_base: bool = Field(
        default=True, description="Use knowledge base context"
    )
    use_tools: bool = Field(default=True, description="Enable tool usage")
    max_context_chunks: int = Field(
        default=5, ge=1, le=20, description="Maximum knowledge chunks"
    )
    temperature: float = Field(
        default=0.7, ge=0.0, le=2.0, description="AI temperature"
    )
    max_tokens: int | None = Field(None, ge=1, le=100000, description="Maximum tokens")
    model: str | None = Field(None, description="AI model to use")
    metadata: dict[str, Any] | None = Field(None, description="Additional metadata")

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Validate and sanitize message."""
        if not v or not v.strip():
            raise ValueError("Message cannot be empty")

        # Sanitize message
        v = sanitize_text(v)

        # Check for injection attacks
        if not validate_sql_injection(v):
            raise SecurityValidationError("Message contains SQL injection patterns")

        if not validate_xss_injection(v):
            raise SecurityValidationError("Message contains XSS injection patterns")

        return v

    @field_validator("assistant_id")
    @classmethod
    def validate_assistant_id(cls, v: str | None) -> str | None:
        """Validate assistant ID."""
        if v is not None and not validate_uuid(v):
            raise ValueError("Invalid assistant ID format")
        return v

    @field_validator("model")
    @classmethod
    def validate_model(cls, v: str | None) -> str | None:
        """Validate AI model name."""
        if v is not None:
            # Allow only alphanumeric, hyphens, and underscores
            if not re.match(r"^[a-zA-Z0-9_-]+$", v):
                raise ValueError("Invalid model name format")
        return v

    @field_validator("metadata")
    @classmethod
    def validate_metadata(cls, v: dict[str, Any] | None) -> dict[str, Any] | None:
        """Validate metadata structure."""
        if v is not None:
            if not validate_json_structure(v, max_depth=3):
                raise SecurityValidationError("Metadata structure too deep")

            # Check for dangerous keys
            dangerous_keys = ["__class__", "__dict__", "__module__", "eval", "exec"]
            for key in v:
                if key in dangerous_keys:
                    raise SecurityValidationError(f"Dangerous metadata key: {key}")

        return v


class SecureConversationCreateRequest(BaseModel):
    """Secure request model for creating conversations."""

    title: str = Field(
        ..., min_length=1, max_length=500, description="Conversation title"
    )
    assistant_id: str | None = Field(None, description="Assistant ID")
    description: str | None = Field(None, description="Conversation description")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate and sanitize title."""
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")

        v = sanitize_text(v, max_length=500)

        if not validate_sql_injection(v):
            raise SecurityValidationError("Title contains SQL injection patterns")

        if not validate_xss_injection(v):
            raise SecurityValidationError("Title contains XSS injection patterns")

        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        """Validate and sanitize description."""
        if v is not None:
            v = sanitize_text(v, max_length=1000)

            if not validate_sql_injection(v):
                raise SecurityValidationError(
                    "Description contains SQL injection patterns"
                )

            if not validate_xss_injection(v):
                raise SecurityValidationError(
                    "Description contains XSS injection patterns"
                )

        return v

    @field_validator("assistant_id")
    @classmethod
    def validate_assistant_id(cls, v: str | None) -> str | None:
        """Validate assistant ID."""
        if v is not None and not validate_uuid(v):
            raise ValueError("Invalid assistant ID format")
        return v


def validate_file_upload(filename: str, content_type: str, file_size: int) -> bool:
    """Validate file upload security."""
    # Check file extension
    allowed_extensions = {
        ".pdf",
        ".doc",
        ".docx",
        ".txt",
        ".md",
        ".html",
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".tiff",
    }

    file_ext = filename.lower().split(".")[-1] if "." in filename else ""
    if f".{file_ext}" not in allowed_extensions:
        return False

    # Check content type
    allowed_types = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
        "text/markdown",
        "text/html",
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/bmp",
        "image/tiff",
    }

    if content_type not in allowed_types:
        return False

    # Check file size (10MB limit)
    max_size = 10 * 1024 * 1024
    if file_size > max_size:
        return False

    # Check filename for path traversal
    return validate_path_traversal(filename)


def log_security_event(event_type: str, details: str, user_id: str | None = None):
    """Log security events."""
    logger.warning(
        f"Security event: {event_type} - {details} - User: {user_id or 'anonymous'}"
    )
