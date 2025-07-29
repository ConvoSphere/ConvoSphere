"""
Authentication module for the AI Assistant Platform.

This module re-exports authentication functions from the security module
to maintain compatibility with existing imports.
"""

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
    "create_access_token",
    "create_refresh_token",
    "get_current_user",
    "get_current_user_id",
    "get_current_user_optional",
    "get_password_hash",
    "log_security_event",
    "require_permission",
    "verify_password",
    "verify_token",
]
