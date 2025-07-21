"""
Core module for the AI Assistant Platform.

This module contains core functionality including configuration,
database management, security, and utility functions.
"""

from .config import get_settings, settings
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
    # Configuration
    "settings",
    "get_settings",
    # Database
    "get_db",
    "init_db",
    "check_db_connection",
    "get_db_info",
    # Redis
    "get_redis",
    "init_redis",
    "close_redis",
    "check_redis_connection",
    "get_redis_info",
    "set_cache",
    "get_cache",
    "delete_cache",
    "clear_cache_pattern",
    # Weaviate
    "get_weaviate",
    "init_weaviate",
    "close_weaviate",
    "check_weaviate_connection",
    "get_weaviate_info",
    "create_schema_if_not_exists",
    "add_document",
    "search_documents",
    "delete_document",
    # Security
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    "get_password_hash",
    "verify_password",
    "get_current_user",
    "get_current_user_id",
    "require_permission",
    "log_security_event",
]
