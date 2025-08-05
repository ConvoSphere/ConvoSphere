"""Helper utilities for the AI Assistant Platform."""

import re
import uuid
from datetime import UTC, datetime


def generate_uuid() -> str:
    """
    Generate a UUID string.

    Returns:
        str: UUID string
    """
    return str(uuid.uuid4())


def utc_now() -> datetime:
    """
    Get current UTC datetime.

    Returns:
        datetime: Current UTC datetime
    """
    return datetime.now(UTC)


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime to string.

    Args:
        dt: Datetime object
        format_str: Format string

    Returns:
        str: Formatted datetime string
    """
    return dt.strftime(format_str)


def parse_datetime(
    date_string: str,
    format_str: str = "%Y-%m-%d %H:%M:%S",
) -> datetime | None:
    """
    Parse datetime string to datetime object.

    Args:
        date_string: Date string to parse
        format_str: Format string

    Returns:
        Optional[datetime]: Parsed datetime or None if invalid
    """
    try:
        # Parse the datetime string
        dt = datetime.strptime(date_string, format_str)
        
        # If the datetime is naive (no timezone info), assume UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        
        return dt
    except ValueError:
        return None


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to specified length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage.

    Args:
        filename: Original filename

    Returns:
        str: Sanitized filename
    """
    if not filename or not filename.strip():
        return "unnamed"

    # Remove or replace unsafe characters and spaces
    sanitized = re.sub(r"[^a-zA-Z0-9._-]", "_", filename)
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(". ")
    # Limit length
    if len(sanitized) > 255:
        name, ext = sanitized.rsplit(".", 1) if "." in sanitized else (sanitized, "")
        sanitized = name[: 255 - len(ext) - 1] + ("." + ext if ext else "")

    return sanitized or "unnamed"


def validate_email(email: str) -> bool:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        bool: True if email is valid, False otherwise
    """
    if not isinstance(email, str) or not email:
        return False
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_password_strength(password: str, min_length: int = 8) -> bool:
    """
    Validate password strength.
    Args:
        password: Password string
        min_length: Minimum length required
    Returns:
        bool: True if password is strong, False otherwise
    """
    if not isinstance(password, str) or len(password) < min_length:
        return False
    if not any(c.isupper() for c in password):
        return False
    if not any(c.islower() for c in password):
        return False
    return any(c.isdigit() for c in password)
