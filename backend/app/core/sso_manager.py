"""
SSO Manager - Facade for modular SSO architecture.

This module provides backward compatibility for the original sso_manager.py
by delegating to the new modular SSO implementation.
"""

import logging
from typing import Any, Dict

from backend.app.core.sso import (
    SSOManager,
    authenticate_user,
    get_available_providers,
    get_sso_manager,
    get_user_info,
    init_sso_manager,
    is_provider_available,
    load_sso_config_from_env,
    load_sso_config_from_settings,
    sync_user_groups,
    validate_sso_config,
    validate_token,
)

logger = logging.getLogger(__name__)

# Re-export all functions for backward compatibility
__all__ = [
    "SSOManager",
    "load_sso_config_from_env",
    "load_sso_config_from_settings",
    "validate_sso_config",
    "init_sso_manager",
    "get_sso_manager",
    "authenticate_user",
    "get_user_info",
    "sync_user_groups",
    "get_available_providers",
    "is_provider_available",
    "validate_token",
]


# Legacy class names for backward compatibility
class SSOProvider:
    """
    Legacy SSOProvider class for backward compatibility.

    This class is deprecated. Use the new modular providers instead:
    - backend.app.core.sso.providers.LDAPProvider
    - backend.app.core.sso.providers.SAMLProvider
    - backend.app.core.sso.providers.OAuthProvider
    - backend.app.core.sso.providers.GoogleOAuthProvider
    - backend.app.core.sso.providers.MicrosoftOAuthProvider
    - backend.app.core.sso.providers.GitHubOAuthProvider
    - backend.app.core.sso.providers.OIDCProvider
    """

    def __init__(self, config: Dict[str, Any]):
        logger.warning(
            "SSOProvider is deprecated. Use the new modular providers instead. "
            "See backend.app.core.sso.providers for available options."
        )
        raise NotImplementedError(
            "SSOProvider is deprecated. Use the new modular providers instead."
        )


class LDAPProvider(SSOProvider):
    """
    Legacy LDAPProvider class for backward compatibility.

    This class is deprecated. Use backend.app.core.sso.providers.LDAPProvider instead.
    """


class SAMLProvider(SSOProvider):
    """
    Legacy SAMLProvider class for backward compatibility.

    This class is deprecated. Use backend.app.core.sso.providers.SAMLProvider instead.
    """


class OAuthProvider(SSOProvider):
    """
    Legacy OAuthProvider class for backward compatibility.

    This class is deprecated. Use backend.app.core.sso.providers.OAuthProvider instead.
    """
