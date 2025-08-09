"""Validation utilities for CLI commands."""

import re
from typing import Optional


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_username(username: str) -> bool:
    """Validate username format."""
    # Username should be 3-30 characters, alphanumeric and underscores only
    pattern = r'^[a-zA-Z0-9_]{3,30}$'
    return bool(re.match(pattern, username))


def validate_revision(revision: str) -> bool:
    """Validate Alembic revision format."""
    if not revision or not isinstance(revision, str):
        return False
    # Basic validation - revision should be alphanumeric
    return bool(re.match(r'^[a-zA-Z0-9]+$', revision))


def validate_password(password: str) -> bool:
    """Validate password strength."""
    if len(password) < 8:
        return False
    # At least one uppercase, one lowercase, one digit
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    return has_upper and has_lower and has_digit


def validate_role(role: str) -> bool:
    """Validate user role."""
    valid_roles = ["user", "admin", "super_admin", "moderator"]
    return role in valid_roles


def validate_status(status: str) -> bool:
    """Validate user status."""
    valid_statuses = ["active", "inactive", "suspended"]
    return status in valid_statuses