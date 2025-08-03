"""
Core module for the AI Assistant Platform.

This module contains core functionality including configuration,
database management, security, and utility functions.
"""

from .config import get_settings
from .security import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    get_current_user_id,
    get_current_user_optional,
    get_password_hash,
    log_security_event,
    require_permission,
    verify_password,
    verify_token,
)

__all__ = [
    "get_settings",
    "get_current_user",
    "get_current_user_id",
    "get_current_user_optional",
    "create_access_token",
    "create_refresh_token",
    "verify_password",
    "get_password_hash",
    "verify_token",
    "log_security_event",
    "require_permission",
]
