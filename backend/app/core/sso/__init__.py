"""
SSO (Single Sign-On) package.

This package provides comprehensive SSO management including
LDAP, SAML, OAuth, and OpenID Connect with advanced features like
role mapping, group synchronization, and session management.
"""

from backend.app.core.sso.manager import SSOManager
from backend.app.core.sso.configuration.config_loader import (
    load_sso_config_from_env,
    load_sso_config_from_settings,
    validate_sso_config,
    get_provider_config,
)
from backend.app.core.sso.providers import (
    BaseSSOProvider,
    LDAPProvider,
    SAMLProvider,
    OAuthProvider,
    GoogleOAuthProvider,
    MicrosoftOAuthProvider,
    GitHubOAuthProvider,
    OIDCProvider,
)
from backend.app.core.sso.global_manager import (
    init_sso_manager,
    get_sso_manager,
    authenticate_user,
    get_user_info,
    sync_user_groups,
    get_available_providers,
    is_provider_available,
    validate_token,
)

__all__ = [
    "SSOManager",
    "load_sso_config_from_env",
    "load_sso_config_from_settings",
    "validate_sso_config",
    "get_provider_config",
    "BaseSSOProvider",
    "LDAPProvider",
    "SAMLProvider",
    "OAuthProvider",
    "GoogleOAuthProvider",
    "MicrosoftOAuthProvider",
    "GitHubOAuthProvider",
    "OIDCProvider",
    "init_sso_manager",
    "get_sso_manager",
    "authenticate_user",
    "get_user_info",
    "sync_user_groups",
    "get_available_providers",
    "is_provider_available",
    "validate_token",
]