"""
SSO (Single Sign-On) package.

This package provides comprehensive SSO management including
LDAP, SAML, OAuth, and OpenID Connect with advanced features like
role mapping, group synchronization, and session management.
"""

from backend.app.core.sso.manager import SSOManager
from backend.app.core.sso.configuration.config_loader import (
    load_sso_config_from_env,
    validate_sso_config,
    get_provider_config,
)
from backend.app.core.sso.providers import (
    BaseSSOProvider,
    LDAPProvider,
    SAMLProvider,
    OAuthProvider,
)

__all__ = [
    "SSOManager",
    "load_sso_config_from_env",
    "validate_sso_config",
    "get_provider_config",
    "BaseSSOProvider",
    "LDAPProvider",
    "SAMLProvider",
    "OAuthProvider",
]