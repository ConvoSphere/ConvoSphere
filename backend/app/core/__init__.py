"""
Core module for the AI Assistant Platform.

This module contains core functionality including configuration,
database management, security, and utility functions.
"""

from .config import settings, get_settings
from .database import get_db, init_db, check_db_connection, get_db_info
from .redis_client import (
    get_redis, init_redis, close_redis, 
    check_redis_connection, get_redis_info,
    set_cache, get_cache, delete_cache, clear_cache_pattern
)
from .weaviate_client import (
    get_weaviate, init_weaviate, close_weaviate,
    check_weaviate_connection, get_weaviate_info,
    create_schema_if_not_exists, add_document, search_documents, delete_document
)
from .security import (
    create_access_token, create_refresh_token, verify_token,
    get_password_hash, verify_password, get_current_user,
    get_current_user_id, require_permission, log_security_event
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