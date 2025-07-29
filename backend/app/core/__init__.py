"""
Core module for the AI Assistant Platform.

This module contains core functionality including configuration,
database management, security, and utility functions.
"""

from .config import get_settings
from .database import check_db_connection, get_db, get_db_info, init_db
from .redis_client import (
    check_redis_connection,
    clear_cache_pattern,
    close_redis,
    delete_cache,
    get_cache,
    get_redis,
    get_redis_info,
    init_redis,
    set_cache,
)
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
from .weaviate_client import (
    add_document,
    check_weaviate_connection,
    close_weaviate,
    create_schema_if_not_exists,
    delete_document,
    get_weaviate,
    get_weaviate_info,
    init_weaviate,
    search_documents,
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
