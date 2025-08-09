"""
Global SSO Manager for backward compatibility.

This module provides global SSO manager functions for backward compatibility
with the original sso_manager.py implementation.
"""

import logging
from typing import Any, Dict

from backend.app.core.sso.configuration.config_loader import (
    load_sso_config_from_env,
    load_sso_config_from_settings,
)
from backend.app.core.sso.manager import SSOManager

logger = logging.getLogger(__name__)

# Global SSO manager instance
_sso_manager: SSOManager | None = None


def init_sso_manager(config: Dict[str, Any] = None) -> SSOManager:
    """
    Initialize global SSO manager (backward compatibility).

    Args:
        config: Optional SSO configuration dictionary

    Returns:
        Initialized SSOManager instance
    """
    global _sso_manager

    if config is None:
        # Try to load from settings first (backward compatibility)
        try:
            config = load_sso_config_from_settings()
        except Exception as e:
            logger.warning(f"Failed to load SSO config from settings: {e}")
            # Fall back to environment variables
            config = load_sso_config_from_env()

    _sso_manager = SSOManager(config)
    logger.info(
        f"Global SSO Manager initialized with {len(config.get('providers', {}))} providers"
    )

    return _sso_manager


def get_sso_manager() -> SSOManager:
    """
    Get global SSO manager instance (backward compatibility).

    Returns:
        SSOManager instance

    Raises:
        RuntimeError: If SSO manager is not initialized
    """
    global _sso_manager

    if _sso_manager is None:
        # Auto-initialize if not already done
        init_sso_manager()

    return _sso_manager


def load_sso_config_from_env() -> Dict[str, Any]:
    """
    Load SSO configuration from environment variables (backward compatibility).

    Returns:
        SSO configuration dictionary
    """
    return load_sso_config_from_env()


# Convenience functions for backward compatibility
async def authenticate_user(
    provider_name: str, credentials: Dict[str, Any], db
) -> tuple[Any, Dict[str, Any]]:
    """
    Authenticate user with specified provider (backward compatibility).

    Args:
        provider_name: Name of the SSO provider
        credentials: User credentials
        db: Database session

    Returns:
        Tuple of (User, additional_data)
    """
    sso_manager = get_sso_manager()
    return await sso_manager.authenticate(provider_name, credentials, db)


async def get_user_info(provider_name: str, user_id: str, db) -> Dict[str, Any]:
    """
    Get user information from specified provider (backward compatibility).

    Args:
        provider_name: Name of the SSO provider
        user_id: User ID
        db: Database session

    Returns:
        User information dictionary
    """
    sso_manager = get_sso_manager()
    return await sso_manager.get_user_info(provider_name, user_id, db)


async def sync_user_groups(provider_name: str, user: Any, db) -> list[str]:
    """
    Synchronize user groups from specified provider (backward compatibility).

    Args:
        provider_name: Name of the SSO provider
        user: User object
        db: Database session

    Returns:
        List of synchronized group names
    """
    sso_manager = get_sso_manager()
    return await sso_manager.sync_user_groups(provider_name, user, db)


def get_available_providers() -> list[Dict[str, Any]]:
    """
    Get list of available SSO providers (backward compatibility).

    Returns:
        List of provider configurations
    """
    sso_manager = get_sso_manager()
    return sso_manager.get_available_providers()


def is_provider_available(provider_name: str) -> bool:
    """
    Check if provider is available and enabled (backward compatibility).

    Args:
        provider_name: Name of the SSO provider

    Returns:
        True if provider is available and enabled
    """
    sso_manager = get_sso_manager()
    return sso_manager.is_provider_available(provider_name)


async def validate_token(provider_name: str, token: str) -> Dict[str, Any]:
    """
    Validate token with specified provider (backward compatibility).

    Args:
        provider_name: Name of the SSO provider
        token: Token to validate

    Returns:
        Token validation result
    """
    sso_manager = get_sso_manager()
    return await sso_manager.validate_token(provider_name, token)
