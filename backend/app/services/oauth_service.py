"""
OAuth2 service for handling SSO authentication flows.

This module provides OAuth2 client setup and authentication flows
for Google, Microsoft, and GitHub SSO providers.
"""

import json
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import httpx
from authlib.integrations.starlette_client import OAuth
from fastapi import HTTPException, Request, status
from loguru import logger
from starlette.config import Config
from starlette.responses import RedirectResponse

from app.core.config import get_settings
from app.core.security import create_access_token, create_refresh_token
from app.models.user import AuthProvider, User
from app.schemas.user import SSOUserCreate
from app.services.user_service import UserService
from datetime import datetime, UTC

class OAuthService:
    """Service for handling OAuth2 authentication flows."""

    def __init__(self):
        self.settings = get_settings()
        self.oauth = OAuth()
        self._setup_oauth_clients()

    def _setup_oauth_clients(self):
        """Setup OAuth clients for configured providers."""
        config = Config('.env')  # Load from environment variables

        # Google OAuth2
        if self.settings.sso_google_enabled and self.settings.sso_google_client_id:
            self.oauth.register(
                name='google',
                client_id=self.settings.sso_google_client_id,
                client_secret=self.settings.sso_google_client_secret,
                server_metadata_url='https://accounts.google.com/.well-known/openid_configuration',
                client_kwargs={
                    'scope': 'openid email profile'
                }
            )

        # Microsoft OAuth2
        if self.settings.sso_microsoft_enabled and self.settings.sso_microsoft_client_id:
            self.oauth.register(
                name='microsoft',
                client_id=self.settings.sso_microsoft_client_id,
                client_secret=self.settings.sso_microsoft_client_secret,
                server_metadata_url=f'https://login.microsoftonline.com/{self.settings.sso_microsoft_tenant_id}/v2.0/.well-known/openid_configuration',
                client_kwargs={
                    'scope': 'openid email profile'
                }
            )

        # GitHub OAuth2
        if self.settings.sso_github_enabled and self.settings.sso_github_client_id:
            self.oauth.register(
                name='github',
                client_id=self.settings.sso_github_client_id,
                client_secret=self.settings.sso_github_client_secret,
                access_token_url='https://github.com/login/oauth/access_token',
                access_token_params=None,
                authorize_url='https://github.com/login/oauth/authorize',
                authorize_params=None,
                api_base_url='https://api.github.com/',
                client_kwargs={
                    'scope': 'read:user user:email'
                }
            )

    async def get_authorization_url(self, provider: str, request: Request) -> RedirectResponse:
        """
        Get authorization URL for OAuth provider.

        Args:
            provider: OAuth provider name (google, microsoft, github)
            request: FastAPI request object

        Returns:
            RedirectResponse: Redirect to OAuth provider

        Raises:
            HTTPException: If provider is not configured
        """
        if not self._is_provider_enabled(provider):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{provider.title()} SSO is not configured"
            )

        try:
            client = self.oauth.create_client(provider)
            redirect_uri = self._get_redirect_uri(provider)
            return await client.authorize_redirect(request, redirect_uri)
        except Exception as e:
            logger.error(f"Failed to get authorization URL for {provider}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to initialize {provider} OAuth flow"
            )

    async def handle_callback(self, provider: str, request: Request) -> Dict[str, Any]:
        """
        Handle OAuth callback and return user info.

        Args:
            provider: OAuth provider name
            request: FastAPI request object

        Returns:
            Dict containing user info and tokens
        """
        if not self._is_provider_enabled(provider):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{provider.title()} SSO is not configured"
            )

        try:
            client = self.oauth.create_client(provider)
            token = await client.authorize_access_token(request)
            
            # Get user info from provider
            user_info = await self._get_user_info(provider, client, token)
            
            return {
                'user_info': user_info,
                'token': token,
                'provider': provider
            }
        except Exception as e:
            logger.error(f"OAuth callback failed for {provider}: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"OAuth authentication failed: {str(e)}"
            )

    async def _get_user_info(self, provider: str, client, token: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get user information from OAuth provider.

        Args:
            provider: OAuth provider name
            client: OAuth client
            token: Access token

        Returns:
            Dict containing user information
        """
        if provider == 'google':
            return await self._get_google_user_info(client, token)
        elif provider == 'microsoft':
            return await self._get_microsoft_user_info(client, token)
        elif provider == 'github':
            return await self._get_github_user_info(client, token)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    async def _get_google_user_info(self, client, token: Dict[str, Any]) -> Dict[str, Any]:
        """Get user info from Google."""
        resp = await client.get('userinfo', token=token)
        user_info = resp.json()
        
        return {
            'email': user_info.get('email'),
            'external_id': user_info.get('sub'),
            'first_name': user_info.get('given_name'),
            'last_name': user_info.get('family_name'),
            'display_name': user_info.get('name'),
            'avatar_url': user_info.get('picture'),
            'sso_attributes': user_info
        }

    async def _get_microsoft_user_info(self, client, token: Dict[str, Any]) -> Dict[str, Any]:
        """Get user info from Microsoft."""
        resp = await client.get('userinfo', token=token)
        user_info = resp.json()
        
        return {
            'email': user_info.get('email'),
            'external_id': user_info.get('sub'),
            'first_name': user_info.get('given_name'),
            'last_name': user_info.get('family_name'),
            'display_name': user_info.get('name'),
            'avatar_url': None,  # Microsoft doesn't provide avatar in userinfo
            'sso_attributes': user_info
        }

    async def _get_github_user_info(self, client, token: Dict[str, Any]) -> Dict[str, Any]:
        """Get user info from GitHub."""
        # Get basic user info
        resp = await client.get('user', token=token)
        user_info = resp.json()
        
        # Get email addresses
        email_resp = await client.get('user/emails', token=token)
        emails = email_resp.json()
        primary_email = next((email['email'] for email in emails if email['primary']), user_info.get('email'))
        
        return {
            'email': primary_email,
            'external_id': str(user_info.get('id')),
            'first_name': user_info.get('name', '').split()[0] if user_info.get('name') else None,
            'last_name': ' '.join(user_info.get('name', '').split()[1:]) if user_info.get('name') and len(user_info.get('name', '').split()) > 1 else None,
            'display_name': user_info.get('name'),
            'avatar_url': user_info.get('avatar_url'),
            'sso_attributes': {**user_info, 'emails': emails}
        }

    def _is_provider_enabled(self, provider: str) -> bool:
        """Check if OAuth provider is enabled and configured."""
        if provider == 'google':
            return (self.settings.sso_google_enabled and 
                   self.settings.sso_google_client_id and 
                   self.settings.sso_google_client_secret)
        elif provider == 'microsoft':
            return (self.settings.sso_microsoft_enabled and 
                   self.settings.sso_microsoft_client_id and 
                   self.settings.sso_microsoft_client_secret)
        elif provider == 'github':
            return (self.settings.sso_github_enabled and 
                   self.settings.sso_github_client_id and 
                   self.settings.sso_github_client_secret)
        return False

    def _get_redirect_uri(self, provider: str) -> str:
        """Get redirect URI for OAuth provider."""
        if provider == 'google':
            return self.settings.sso_google_redirect_uri
        elif provider == 'microsoft':
            return self.settings.sso_microsoft_redirect_uri
        elif provider == 'github':
            return self.settings.sso_github_redirect_uri
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def _get_auth_provider(self, provider: str) -> AuthProvider:
        """Convert provider string to AuthProvider enum."""
        provider_mapping = {
            'google': AuthProvider.OAUTH_GOOGLE,
            'microsoft': AuthProvider.OAUTH_MICROSOFT,
            'github': AuthProvider.OAUTH_GITHUB
        }
        return provider_mapping.get(provider, AuthProvider.LOCAL)

    async def process_sso_user(self, user_info: Dict[str, Any], provider: str, db) -> User:
        """
        Process SSO user and create/update user account.

        Args:
            user_info: User information from OAuth provider
            provider: OAuth provider name
            db: Database session

        Returns:
            User: Created or existing user
        """
        user_service = UserService(db)
        auth_provider = self._get_auth_provider(provider)
        
        # Check if user already exists by external ID
        existing_user = user_service.get_user_by_external_id(
            user_info['external_id'], 
            auth_provider
        )
        
        if existing_user:
            # Update existing user with latest SSO info
            logger.info(f"Updating existing SSO user: {existing_user.email}")
            existing_user.sso_attributes = user_info.get('sso_attributes', {})
            db.commit()
            return existing_user
        
        # Create new SSO user
        logger.info(f"Creating new SSO user: {user_info['email']}")
        sso_user_data = SSOUserCreate(
            email=user_info['email'],
            username=user_info.get('username') or user_info['email'].split('@')[0],
            first_name=user_info.get('first_name'),
            last_name=user_info.get('last_name'),
            display_name=user_info.get('display_name'),
            auth_provider=auth_provider,
            external_id=user_info['external_id'],
            sso_attributes=user_info.get('sso_attributes', {})
        )
        
        return user_service.create_sso_user(sso_user_data)

    async def create_sso_tokens(self, user: User) -> Dict[str, Any]:
        """
        Create JWT tokens for SSO user.

        Args:
            user: User object

        Returns:
            Dict containing access and refresh tokens
        """
        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=datetime.timedelta(minutes=self.settings.jwt_access_token_expire_minutes)
        )
        
        # Create refresh token
        refresh_token = create_refresh_token(
            data={"sub": str(user.id)}
        )
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'bearer',
            'expires_in': self.settings.jwt_access_token_expire_minutes * 60
        }


# Global OAuth service instance
oauth_service = OAuthService()