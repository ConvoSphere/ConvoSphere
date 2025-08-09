"""
SSO Providers package.

This package contains all SSO provider implementations.
"""

from backend.app.core.sso.providers.base import BaseSSOProvider
from backend.app.core.sso.providers.github_oauth_provider import GitHubOAuthProvider
from backend.app.core.sso.providers.google_oauth_provider import GoogleOAuthProvider
from backend.app.core.sso.providers.ldap_provider import LDAPProvider
from backend.app.core.sso.providers.microsoft_oauth_provider import (
    MicrosoftOAuthProvider,
)
from backend.app.core.sso.providers.oauth_provider import OAuthProvider
from backend.app.core.sso.providers.oidc_provider import OIDCProvider
from backend.app.core.sso.providers.saml_provider import SAMLProvider

__all__ = [
    "BaseSSOProvider",
    "LDAPProvider",
    "SAMLProvider",
    "OAuthProvider",
    "GoogleOAuthProvider",
    "MicrosoftOAuthProvider",
    "GitHubOAuthProvider",
    "OIDCProvider",
]
