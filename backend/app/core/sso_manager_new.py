"""
SSO Manager - New modular implementation.

This module provides a simplified interface to the new modular SSO system.
It serves as a replacement for the old monolithical sso_manager.py.
"""

import logging
from typing import Any, Dict

from sqlalchemy.orm import Session

from backend.app.core.sso import (
    SSOManager,
    load_sso_config_from_env,
    validate_sso_config,
)
from backend.app.models.user import User
from backend.app.utils.exceptions import (
    AuthenticationError,
    SSOConfigurationError,
    UserNotFoundError,
)

logger = logging.getLogger(__name__)

# Global SSO manager instance
_sso_manager: SSOManager | None = None


def init_sso_manager(config: Dict[str, Any] = None) -> SSOManager:
    """
    Initialize the SSO manager.
    
    Args:
        config: SSO configuration dictionary (optional, loads from env if not provided)
        
    Returns:
        Initialized SSOManager instance
        
    Raises:
        SSOConfigurationError: If configuration is invalid
    """
    global _sso_manager
    
    try:
        if config is None:
            config = load_sso_config_from_env()
        
        # Validate configuration
        validate_sso_config(config)
        
        # Initialize SSO manager
        _sso_manager = SSOManager(config)
        
        logger.info("SSO manager initialized successfully")
        return _sso_manager
        
    except Exception as e:
        logger.exception(f"Failed to initialize SSO manager: {str(e)}")
        raise SSOConfigurationError(f"SSO manager initialization failed: {str(e)}")


def get_sso_manager() -> SSOManager:
    """
    Get the global SSO manager instance.
    
    Returns:
        SSOManager instance
        
    Raises:
        SSOConfigurationError: If SSO manager is not initialized
    """
    global _sso_manager
    
    if _sso_manager is None:
        raise SSOConfigurationError("SSO manager not initialized. Call init_sso_manager() first.")
    
    return _sso_manager


# Convenience functions for backward compatibility
async def authenticate_user(
    provider_name: str,
    credentials: Dict[str, Any],
    db: Session,
) -> tuple[User, Dict[str, Any]]:
    """
    Authenticate user with specified provider.
    
    Args:
        provider_name: Name of the SSO provider
        credentials: Authentication credentials
        db: Database session
        
    Returns:
        Tuple of (User, additional_data)
        
    Raises:
        AuthenticationError: If authentication fails
        SSOConfigurationError: If provider is not configured
    """
    sso_manager = get_sso_manager()
    return await sso_manager.authenticate(provider_name, credentials, db)


async def get_user_info(
    provider_name: str,
    user_id: str,
    db: Session,
) -> Dict[str, Any]:
    """
    Get user information from specified provider.
    
    Args:
        provider_name: Name of the SSO provider
        user_id: User identifier
        db: Database session
        
    Returns:
        User information dictionary
        
    Raises:
        UserNotFoundError: If user is not found
        SSOConfigurationError: If provider is not configured
    """
    sso_manager = get_sso_manager()
    return await sso_manager.get_user_info(provider_name, user_id, db)


async def sync_user_groups(
    provider_name: str,
    user: User,
    db: Session,
) -> list[str]:
    """
    Synchronize user groups from specified provider.
    
    Args:
        provider_name: Name of the SSO provider
        user: User object
        db: Database session
        
    Returns:
        List of group names
        
    Raises:
        SSOConfigurationError: If provider is not configured
    """
    sso_manager = get_sso_manager()
    return await sso_manager.sync_user_groups(provider_name, user, db)


def get_available_providers() -> list[Dict[str, Any]]:
    """
    Get list of available SSO providers.
    
    Returns:
        List of provider information dictionaries
    """
    sso_manager = get_sso_manager()
    return sso_manager.get_available_providers()


def is_provider_available(provider_name: str) -> bool:
    """
    Check if provider is available and enabled.
    
    Args:
        provider_name: Name of the SSO provider
        
    Returns:
        True if provider is available and enabled
    """
    sso_manager = get_sso_manager()
    return sso_manager.is_provider_available(provider_name)


async def validate_token(provider_name: str, token: str) -> Dict[str, Any]:
    """
    Validate token with specified provider.
    
    Args:
        provider_name: Name of the SSO provider
        token: Token to validate
        
    Returns:
        Token validation result
        
    Raises:
        SSOConfigurationError: If provider is not configured
    """
    sso_manager = get_sso_manager()
    return await sso_manager.validate_token(provider_name, token)


# Legacy function names for backward compatibility
load_sso_config_from_env = load_sso_config_from_env