"""
Tests for SSO functionality.

This module contains tests for OAuth2 authentication flows,
user provisioning, and SSO integration.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.app.models.user import AuthProvider
from backend.app.schemas.user import SSOUserCreate
from backend.app.services.oauth_service import OAuthService
from backend.app.services.user_service import UserService


class TestOAuthService:
    """Test OAuth service functionality."""

    @pytest.fixture
    def oauth_service(self):
        """Create OAuth service instance for testing."""
        return OAuthService()

    @pytest.fixture
    def mock_user_info(self):
        """Mock user info from OAuth provider."""
        return {
            "email": "test@example.com",
            "external_id": "12345",
            "first_name": "Test",
            "last_name": "User",
            "display_name": "Test User",
            "avatar_url": "https://example.com/avatar.jpg",
            "sso_attributes": {
                "sub": "12345",
                "email": "test@example.com",
                "name": "Test User",
                "given_name": "Test",
                "family_name": "User",
                "picture": "https://example.com/avatar.jpg",
            },
        }

    def test_oauth_service_initialization(self, oauth_service):
        """Test OAuth service initialization."""
        assert oauth_service is not None
        assert hasattr(oauth_service, "oauth")
        assert hasattr(oauth_service, "settings")

    def test_is_provider_enabled(self, oauth_service):
        """Test provider enabled check."""
        # Test with disabled provider
        assert not oauth_service._is_provider_enabled("google")

        # Test with enabled provider (would need proper config)
        with patch.object(oauth_service.settings, "sso_google_enabled", True):
            with patch.object(
                oauth_service.settings,
                "sso_google_client_id",
                "test-id",
            ):
                with patch.object(
                    oauth_service.settings,
                    "sso_google_client_secret",
                    "test-secret",
                ):
                    assert oauth_service._is_provider_enabled("google")

    def test_get_auth_provider(self, oauth_service):
        """Test auth provider mapping."""
        assert oauth_service._get_auth_provider("google") == AuthProvider.OAUTH_GOOGLE
        assert (
            oauth_service._get_auth_provider("microsoft")
            == AuthProvider.OAUTH_MICROSOFT
        )
        assert oauth_service._get_auth_provider("github") == AuthProvider.OAUTH_GITHUB
        assert oauth_service._get_auth_provider("unknown") == AuthProvider.LOCAL

    def test_get_redirect_uri(self, oauth_service):
        """Test redirect URI retrieval."""
        with patch.object(
            oauth_service.settings,
            "sso_google_redirect_uri",
            "http://localhost/callback",
        ):
            assert (
                oauth_service._get_redirect_uri("google") == "http://localhost/callback"
            )

    @pytest.mark.asyncio
    async def test_get_authorization_url_google(self, oauth_service):
        """Test Google authorization URL generation."""
        mock_request = MagicMock()

        with patch.object(oauth_service, "_is_provider_enabled", return_value=True):
            with patch.object(
                oauth_service.oauth,
                "create_client",
            ) as mock_create_client:
                mock_client = AsyncMock()
                mock_client.authorize_redirect = AsyncMock(
                    return_value="http://google.com/auth",
                )
                mock_create_client.return_value = mock_client

                result = await oauth_service.get_authorization_url(
                    "google",
                    mock_request,
                )
                assert result == "http://google.com/auth"

    @pytest.mark.asyncio
    async def test_get_authorization_url_disabled_provider(self, oauth_service):
        """Test authorization URL with disabled provider."""
        mock_request = MagicMock()

        with patch.object(oauth_service, "_is_provider_enabled", return_value=False):
            with pytest.raises(Exception):
                await oauth_service.get_authorization_url("google", mock_request)

    @pytest.mark.asyncio
    async def test_handle_callback_google(self, oauth_service, mock_user_info):
        """Test Google OAuth callback handling."""
        mock_request = MagicMock()
        mock_client = AsyncMock()
        mock_token = {"access_token": "test-token"}

        with patch.object(oauth_service, "_is_provider_enabled", return_value=True):
            with patch.object(
                oauth_service.oauth,
                "create_client",
                return_value=mock_client,
            ):
                mock_client.authorize_access_token = AsyncMock(return_value=mock_token)

                with patch.object(
                    oauth_service,
                    "_get_google_user_info",
                    return_value=mock_user_info,
                ):
                    result = await oauth_service.handle_callback("google", mock_request)

                    assert "user_info" in result
                    assert "token" in result
                    assert "provider" in result
                    assert result["provider"] == "google"
                    assert result["user_info"] == mock_user_info

    @pytest.mark.asyncio
    async def test_get_google_user_info(self, oauth_service):
        """Test Google user info extraction."""
        mock_client = AsyncMock()
        mock_token = {"access_token": "test-token"}
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "sub": "12345",
            "email": "test@example.com",
            "given_name": "Test",
            "family_name": "User",
            "name": "Test User",
            "picture": "https://example.com/avatar.jpg",
        }
        mock_client.get = AsyncMock(return_value=mock_response)

        result = await oauth_service._get_google_user_info(mock_client, mock_token)

        assert result["email"] == "test@example.com"
        assert result["external_id"] == "12345"
        assert result["first_name"] == "Test"
        assert result["last_name"] == "User"
        assert result["display_name"] == "Test User"
        assert result["avatar_url"] == "https://example.com/avatar.jpg"

    @pytest.mark.asyncio
    async def test_get_github_user_info(self, oauth_service):
        """Test GitHub user info extraction."""
        mock_client = AsyncMock()
        mock_token = {"access_token": "test-token"}

        # Mock user info response
        mock_user_response = MagicMock()
        mock_user_response.json.return_value = {
            "id": 12345,
            "name": "Test User",
            "avatar_url": "https://example.com/avatar.jpg",
            "email": "test@example.com",
        }

        # Mock emails response
        mock_emails_response = MagicMock()
        mock_emails_response.json.return_value = [
            {"email": "test@example.com", "primary": True, "verified": True},
            {"email": "secondary@example.com", "primary": False, "verified": True},
        ]

        mock_client.get = AsyncMock(
            side_effect=[mock_user_response, mock_emails_response],
        )

        result = await oauth_service._get_github_user_info(mock_client, mock_token)

        assert result["email"] == "test@example.com"
        assert result["external_id"] == "12345"
        assert result["first_name"] == "Test"
        assert result["last_name"] == "User"
        assert result["display_name"] == "Test User"
        assert result["avatar_url"] == "https://example.com/avatar.jpg"

    @pytest.mark.asyncio
    async def test_process_sso_user_new_user(
        self,
        oauth_service,
        mock_user_info,
        db_session,
    ):
        """Test processing new SSO user."""
        with (
            patch.object(
                oauth_service,
                "_get_auth_provider",
                return_value=AuthProvider.OAUTH_GOOGLE,
            ),
            patch.object(
                UserService,
                "get_user_by_external_id",
                return_value=None,
            ),
            patch.object(UserService, "create_sso_user") as mock_create,
        ):
            mock_user = MagicMock()
            mock_user.id = "test-user-id"
            mock_create.return_value = mock_user

            result = await oauth_service.process_sso_user(
                mock_user_info,
                "google",
                db_session,
            )
            assert result == mock_user

    @pytest.mark.asyncio
    async def test_process_sso_user_existing_user(
        self,
        oauth_service,
        mock_user_info,
        db_session,
    ):
        """Test processing existing SSO user."""
        mock_user = MagicMock()
        mock_user.id = "test-user-id"

        with (
            patch.object(
                oauth_service,
                "_get_auth_provider",
                return_value=AuthProvider.OAUTH_GOOGLE,
            ),
            patch.object(
                UserService,
                "get_user_by_external_id",
                return_value=mock_user,
            ),
        ):
            result = await oauth_service.process_sso_user(
                mock_user_info,
                "google",
                db_session,
            )
            assert result == mock_user

    @pytest.mark.asyncio
    async def test_create_sso_tokens(self, oauth_service):
        """Test SSO token creation."""
        mock_user = MagicMock()
        mock_user.id = "test-user-id"

        with patch.object(
            oauth_service.settings,
            "jwt_access_token_expire_minutes",
            30,
        ):
            result = await oauth_service.create_sso_tokens(mock_user)

            assert "access_token" in result
            assert "refresh_token" in result
            assert "token_type" in result
            assert "expires_in" in result
            assert result["token_type"] == "bearer"
            assert result["expires_in"] == 1800  # 30 minutes * 60 seconds


class TestSSOEndpoints:
    """Test SSO API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from backend.main import app

        return TestClient(app)

    def test_get_sso_providers(self, client):
        """Test SSO providers endpoint."""
        response = client.get("/api/v1/auth/sso/providers")
        assert response.status_code == 200
        data = response.json()
        assert "providers" in data
        assert isinstance(data["providers"], list)

    @pytest.mark.asyncio
    async def test_sso_login_google(self, client):
        """Test Google SSO login endpoint."""
        with patch(
            "app.services.oauth_service.oauth_service.get_authorization_url",
        ) as mock_auth:
            mock_auth.return_value = "http://google.com/auth"
            response = client.get("/api/v1/auth/sso/login/google")
            assert response.status_code == 200

    def test_sso_login_disabled_provider(self, client):
        """Test SSO login with disabled provider."""
        response = client.get("/api/v1/auth/sso/login/disabled-provider")
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_sso_callback_success(self, client, db_session):
        """Test successful SSO callback."""
        mock_user_info = {
            "email": "test@example.com",
            "external_id": "12345",
            "first_name": "Test",
            "last_name": "User",
            "display_name": "Test User",
            "avatar_url": "https://example.com/avatar.jpg",
            "sso_attributes": {},
        }

        mock_user = MagicMock()
        mock_user.id = "test-user-id"
        mock_user.email = "test@example.com"

        mock_tokens = {
            "access_token": "test-access-token",
            "refresh_token": "test-refresh-token",
            "token_type": "bearer",
            "expires_in": 1800,
        }

        with (
            patch(
                "app.services.oauth_service.oauth_service.handle_callback",
            ) as mock_callback,
            patch(
                "app.services.oauth_service.oauth_service.process_sso_user",
            ) as mock_process,
            patch(
                "app.services.oauth_service.oauth_service.create_sso_tokens",
            ) as mock_tokens_func,
        ):
            mock_callback.return_value = {
                "user_info": mock_user_info,
                "token": {},
                "provider": "google",
            }
            mock_process.return_value = mock_user
            mock_tokens_func.return_value = mock_tokens

            response = client.get("/api/v1/auth/sso/callback/google")
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data

    def test_sso_callback_error(self, client):
        """Test SSO callback with error."""
        with patch(
            "app.services.oauth_service.oauth_service.handle_callback",
            side_effect=Exception("OAuth error"),
        ):
            response = client.get("/api/v1/auth/sso/callback/google")
            assert response.status_code == 400


class TestSSOUserService:
    """Test SSO user service functionality."""

    @pytest.fixture
    def user_service(self, db_session):
        """Create user service instance."""
        return UserService(db_session)

    def test_create_sso_user(self, user_service, db_session):
        """Test SSO user creation."""
        sso_data = SSOUserCreate(
            email="test@example.com",
            username=None,
            first_name="Test",
            last_name="User",
            display_name="Test User",
            avatar_url="https://example.com/avatar.jpg",
            auth_provider=AuthProvider.OAUTH_GOOGLE,
            external_id="12345",
            sso_attributes={"sub": "12345", "email": "test@example.com"},
        )

        user = user_service.create_sso_user(sso_data)

        assert user.email == "test@example.com"
        assert user.auth_provider == AuthProvider.OAUTH_GOOGLE
        assert user.external_id == "12345"
        assert user.is_verified is True
        assert user.is_active is True

    def test_get_user_by_external_id(self, user_service, db_session):
        """Test getting user by external ID."""
        # Create test user
        sso_data = SSOUserCreate(
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            auth_provider=AuthProvider.OAUTH_GOOGLE,
            external_id="12345",
            sso_attributes={},
        )
        user_service.create_sso_user(sso_data)

        # Test retrieval
        user = user_service.get_user_by_external_id("12345", AuthProvider.OAUTH_GOOGLE)
        assert user is not None
        assert user.email == "test@example.com"
        assert user.external_id == "12345"

    def test_get_user_by_external_id_not_found(self, user_service, db_session):
        """Test getting user by external ID when not found."""
        user = user_service.get_user_by_external_id(
            "nonexistent",
            AuthProvider.OAUTH_GOOGLE,
        )
        assert user is None


@pytest.mark.asyncio
async def test_oauth_integration_flow():
    """Test complete OAuth integration flow."""
    # This test would require a more complex setup with actual OAuth providers
    # For now, we'll test the individual components
    oauth_service = OAuthService()

    # Test service initialization
    assert oauth_service is not None

    # Test provider mapping
    assert oauth_service._get_auth_provider("google") == AuthProvider.OAUTH_GOOGLE
    assert oauth_service._get_auth_provider("microsoft") == AuthProvider.OAUTH_MICROSOFT
    assert oauth_service._get_auth_provider("github") == AuthProvider.OAUTH_GITHUB
