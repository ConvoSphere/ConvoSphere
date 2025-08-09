"""
SSO Manager for handling multiple authentication providers.

This module provides a centralized interface for managing different SSO providers
including LDAP, SAML, OAuth, and OpenID Connect.
"""

import logging
from typing import Any, Dict

from sqlalchemy.orm import Session

from backend.app.core.sso.providers.base import BaseSSOProvider
from backend.app.core.sso.providers.ldap_provider import LDAPProvider
from backend.app.core.sso.providers.saml_provider import SAMLProvider
from backend.app.core.sso.providers.oauth_provider import OAuthProvider
from backend.app.models.user import User
from backend.app.utils.exceptions import (
    AuthenticationError,
    SSOConfigurationError,
    UserNotFoundError,
)

logger = logging.getLogger(__name__)


class SSOManager:
    """Centralized SSO manager for multiple providers."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.providers: Dict[str, BaseSSOProvider] = {}
        self._init_providers()

    def _init_providers(self):
        """Initialize SSO providers from configuration."""
        try:
            providers_config = self.config.get("providers", {})

            # Initialize LDAP provider
            if "ldap" in providers_config:
                ldap_config = providers_config["ldap"]
                if ldap_config.get("enabled", False):
                    self.providers["ldap"] = LDAPProvider(ldap_config)

            # Initialize SAML provider
            if "saml" in providers_config:
                saml_config = providers_config["saml"]
                if saml_config.get("enabled", False):
                    self.providers["saml"] = SAMLProvider(saml_config)

            # Initialize OAuth provider
            if "oauth" in providers_config:
                oauth_config = providers_config["oauth"]
                if oauth_config.get("enabled", False):
                    self.providers["oauth"] = OAuthProvider(oauth_config)

            logger.info(f"Initialized {len(self.providers)} SSO providers: {list(self.providers.keys())}")

        except Exception as e:
            logger.exception(f"Failed to initialize SSO providers: {str(e)}")
            raise SSOConfigurationError(f"SSO provider initialization failed: {str(e)}")

    async def authenticate(
        self,
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
        if provider_name not in self.providers:
            raise SSOConfigurationError(f"SSO provider '{provider_name}' not configured")

        provider = self.providers[provider_name]
        
        if not provider.is_enabled():
            raise SSOConfigurationError(f"SSO provider '{provider_name}' is disabled")

        try:
            return await provider.authenticate(credentials, db)
        except Exception as e:
            logger.exception(f"Authentication failed for provider '{provider_name}': {str(e)}")
            raise AuthenticationError(f"Authentication failed: {str(e)}")

    async def get_user_info(
        self,
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
        if provider_name not in self.providers:
            raise SSOConfigurationError(f"SSO provider '{provider_name}' not configured")

        provider = self.providers[provider_name]
        
        if not provider.is_enabled():
            raise SSOConfigurationError(f"SSO provider '{provider_name}' is disabled")

        try:
            return await provider.get_user_info(user_id, db)
        except Exception as e:
            logger.exception(f"Failed to get user info from provider '{provider_name}': {str(e)}")
            raise UserNotFoundError(f"Failed to get user info: {str(e)}")

    async def sync_user_groups(
        self,
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
        if provider_name not in self.providers:
            raise SSOConfigurationError(f"SSO provider '{provider_name}' not configured")

        provider = self.providers[provider_name]
        
        if not provider.is_enabled():
            raise SSOConfigurationError(f"SSO provider '{provider_name}' is disabled")

        try:
            return await provider.sync_user_groups(user, db)
        except Exception as e:
            logger.exception(f"Failed to sync groups from provider '{provider_name}': {str(e)}")
            return []

    def get_available_providers(self) -> list[Dict[str, Any]]:
        """
        Get list of available SSO providers.
        
        Returns:
            List of provider information dictionaries
        """
        providers_info = []
        
        for name, provider in self.providers.items():
            providers_info.append({
                "name": name,
                "enabled": provider.is_enabled(),
                "priority": provider.get_priority(),
                "display_name": provider.get_name(),
            })
        
        # Sort by priority (higher priority first)
        providers_info.sort(key=lambda x: x["priority"], reverse=True)
        
        return providers_info

    def get_provider_config(self, provider_name: str) -> Dict[str, Any]:
        """
        Get configuration for specified provider.
        
        Args:
            provider_name: Name of the SSO provider
            
        Returns:
            Provider configuration dictionary
            
        Raises:
            SSOConfigurationError: If provider is not configured
        """
        if provider_name not in self.providers:
            raise SSOConfigurationError(f"SSO provider '{provider_name}' not configured")

        provider = self.providers[provider_name]
        
        return {
            "name": provider.get_name(),
            "enabled": provider.is_enabled(),
            "priority": provider.get_priority(),
            "type": provider.__class__.__name__,
        }

    async def validate_token(self, provider_name: str, token: str) -> Dict[str, Any]:
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
        if provider_name not in self.providers:
            raise SSOConfigurationError(f"SSO provider '{provider_name}' not configured")

        provider = self.providers[provider_name]
        
        if not provider.is_enabled():
            raise SSOConfigurationError(f"SSO provider '{provider_name}' is disabled")

        try:
            return await provider.validate_token(token)
        except Exception as e:
            logger.exception(f"Token validation failed for provider '{provider_name}': {str(e)}")
            return {"valid": False, "error": str(e)}

    def is_provider_available(self, provider_name: str) -> bool:
        """
        Check if provider is available and enabled.
        
        Args:
            provider_name: Name of the SSO provider
            
        Returns:
            True if provider is available and enabled
        """
        return (
            provider_name in self.providers and 
            self.providers[provider_name].is_enabled()
        )

    def get_enabled_providers(self) -> list[str]:
        """
        Get list of enabled provider names.
        
        Returns:
            List of enabled provider names
        """
        return [
            name for name, provider in self.providers.items()
            if provider.is_enabled()
        ]