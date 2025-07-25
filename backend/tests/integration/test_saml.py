"""
Unit tests for SAML service functionality.

This module tests the SAML authentication flows, metadata generation,
and user information extraction.
"""

import base64
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.services.saml_service import MockSamlSettings, SAMLService
from fastapi import HTTPException


class TestSAMLService:
    """Test cases for SAMLService."""

    @pytest.fixture
    def saml_service(self):
        """Create a SAML service instance for testing."""
        return SAMLService()

    @pytest.fixture
    def mock_settings(self):
        """Create mock SAML settings."""
        settings = MockSamlSettings()
        settings.sso_saml_enabled = True
        settings.sso_saml_metadata_url = "https://idp.example.com/metadata"
        settings.sso_saml_entity_id = "http://localhost:8000"
        settings.sso_saml_acs_url = (
            "http://localhost:8000/api/v1/auth/sso/callback/saml"
        )
        return settings

    @pytest.fixture
    def mock_saml_client(self):
        """Create a mock SAML client."""
        client = MagicMock()
        client.config = MagicMock()
        return client

    def test_saml_service_initialization(self, saml_service):
        """Test SAML service initialization."""
        assert saml_service is not None
        assert saml_service.settings is not None
        assert isinstance(saml_service.settings, MockSamlSettings)

    def test_is_enabled_disabled(self, saml_service):
        """Test SAML service when disabled."""
        saml_service.settings.sso_saml_enabled = False
        assert not saml_service.is_enabled()

    def test_is_enabled_no_metadata(self, saml_service):
        """Test SAML service when no metadata URL is configured."""
        saml_service.settings.sso_saml_enabled = True
        saml_service.settings.sso_saml_metadata_url = None
        assert not saml_service.is_enabled()

    def test_is_enabled_no_client(self, saml_service):
        """Test SAML service when client is not initialized."""
        saml_service.settings.sso_saml_enabled = True
        saml_service.settings.sso_saml_metadata_url = "https://example.com"
        saml_service.saml_client = None
        assert not saml_service.is_enabled()

    @patch("app.services.saml_service.get_xmlsec_binary")
    def test_setup_saml_client_success(self, mock_xmlsec, saml_service, mock_settings):
        """Test successful SAML client setup."""
        saml_service.settings = mock_settings
        mock_xmlsec.return_value = "/usr/bin/xmlsec1"

        # Mock certificate creation
        with patch.object(saml_service, "_create_temp_certificates") as mock_cert:
            mock_cert.return_value = ("/tmp/test.crt", "/tmp/test.key")

            # Mock Saml2Config and Saml2Client
            with patch("app.services.saml_service.Saml2Config") as mock_config_class:
                with patch(
                    "app.services.saml_service.Saml2Client",
                ) as mock_client_class:
                    mock_config = MagicMock()
                    mock_config_class.return_value = mock_config
                    mock_client = MagicMock()
                    mock_client_class.return_value = mock_client

                    saml_service._setup_saml_client()

                    assert saml_service.saml_client is not None
                    mock_config.load.assert_called_once()
                    mock_client_class.assert_called_once_with(mock_config)

    def test_setup_saml_client_disabled(self, saml_service):
        """Test SAML client setup when disabled."""
        saml_service.settings.sso_saml_enabled = False
        saml_service._setup_saml_client()
        assert saml_service.saml_client is None

    @patch("app.services.saml_service.get_xmlsec_binary")
    def test_setup_saml_client_failure(self, mock_xmlsec, saml_service, mock_settings):
        """Test SAML client setup failure."""
        saml_service.settings = mock_settings
        mock_xmlsec.side_effect = Exception("xmlsec not found")

        saml_service._setup_saml_client()
        assert saml_service.saml_client is None

    def test_get_certificate_files_provided(self, saml_service):
        """Test getting certificate files when provided."""
        saml_service.settings.sso_saml_cert_file = "/path/to/cert.crt"
        saml_service.settings.sso_saml_key_file = "/path/to/key.key"

        cert_file, key_file = saml_service._get_certificate_files()

        assert cert_file == "/path/to/cert.crt"
        assert key_file == "/path/to/key.key"

    @patch("app.services.saml_service.tempfile.NamedTemporaryFile")
    def test_create_temp_certificates(self, mock_tempfile, saml_service):
        """Test temporary certificate creation."""
        # Mock temporary files
        mock_cert_file = MagicMock()
        mock_key_file = MagicMock()
        mock_tempfile.side_effect = [mock_cert_file, mock_key_file]

        # Mock cryptography components
        with patch("app.services.saml_service.x509") as mock_x509:
            with patch("app.services.saml_service.rsa") as mock_rsa:
                with patch(
                    "app.services.saml_service.serialization",
                ) as mock_serialization:
                    # Mock private key
                    mock_private_key = MagicMock()
                    mock_rsa.generate_private_key.return_value = mock_private_key
                    mock_private_key.public_key.return_value = MagicMock()

                    # Mock certificate
                    mock_cert = MagicMock()
                    mock_x509.CertificateBuilder.return_value.subject_name.return_value.issuer_name.return_value.public_key.return_value.serial_number.return_value.not_valid_before.return_value.not_valid_after.return_value.add_extension.return_value.sign.return_value = (
                        mock_cert
                    )

                    # Mock serialization
                    mock_cert.public_bytes.return_value = b"mock_cert_data"
                    mock_private_key.private_bytes.return_value = b"mock_key_data"

                    cert_file, key_file = saml_service._create_temp_certificates()

                    assert cert_file is not None
                    assert key_file is not None
                    mock_cert_file.write.assert_called()
                    mock_key_file.write.assert_called()

    @pytest.mark.asyncio
    async def test_get_login_url_disabled(self, saml_service):
        """Test getting login URL when SAML is disabled."""
        saml_service.settings.sso_saml_enabled = False

        with pytest.raises(HTTPException) as exc_info:
            await saml_service.get_login_url(MagicMock())

        assert exc_info.value.status_code == 400
        assert "SAML SSO is not configured" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_login_url_success(
        self,
        saml_service,
        mock_settings,
        mock_saml_client,
    ):
        """Test successful login URL generation."""
        saml_service.settings = mock_settings
        saml_service.saml_client = mock_saml_client

        # Mock the IdP entity ID method
        saml_service._get_idp_entity_id = MagicMock(
            return_value="http://idp.example.com",
        )

        # Mock authentication request creation
        mock_authn_req = MagicMock()
        mock_saml_client.create_authn_request.return_value = mock_authn_req

        # Mock binding application
        mock_saml_client.apply_binding.return_value = (
            "POST",
            "https://idp.example.com/login",
        )

        request = MagicMock()
        login_url = await saml_service.get_login_url(request)

        assert login_url == "https://idp.example.com/login"
        mock_saml_client.create_authn_request.assert_called_once()
        mock_saml_client.apply_binding.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_login_url_failure(
        self,
        saml_service,
        mock_settings,
        mock_saml_client,
    ):
        """Test login URL generation failure."""
        saml_service.settings = mock_settings
        saml_service.saml_client = mock_saml_client

        # Mock the IdP entity ID method to raise an exception
        saml_service._get_idp_entity_id = MagicMock(
            side_effect=Exception("IdP not found"),
        )

        request = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            await saml_service.get_login_url(request)

        assert exc_info.value.status_code == 500

    def test_get_idp_entity_id(self, saml_service):
        """Test getting IdP entity ID."""
        entity_id = saml_service._get_idp_entity_id()
        assert entity_id == "http://idp.example.com"

    @pytest.mark.asyncio
    async def test_handle_saml_response_disabled(self, saml_service):
        """Test handling SAML response when disabled."""
        saml_service.settings.sso_saml_enabled = False

        with pytest.raises(HTTPException) as exc_info:
            await saml_service.handle_saml_response(MagicMock())

        assert exc_info.value.status_code == 400
        assert "SAML SSO is not configured" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_handle_saml_response_success(
        self,
        saml_service,
        mock_settings,
        mock_saml_client,
    ):
        """Test successful SAML response handling."""
        saml_service.settings = mock_settings
        saml_service.saml_client = mock_saml_client

        # Mock request with SAML response
        request = MagicMock()
        mock_form = {"SAMLResponse": base64.b64encode(b"mock_saml_response").decode()}
        request.form = AsyncMock(return_value=mock_form)

        # Mock SAML response parsing
        mock_authn_response = MagicMock()
        mock_saml_client.parse_authn_request_response.return_value = mock_authn_response

        # Mock user info extraction
        mock_user_info = {
            "email": "test@example.com",
            "external_id": "user123",
            "first_name": "Test",
            "last_name": "User",
        }
        saml_service._extract_user_info = MagicMock(return_value=mock_user_info)

        result = await saml_service.handle_saml_response(request)

        assert result["user_info"] == mock_user_info
        assert result["saml_response"] == mock_authn_response
        assert result["provider"] == "saml"

    @pytest.mark.asyncio
    async def test_extract_saml_response_success(self, saml_service):
        """Test successful SAML response extraction."""
        request = MagicMock()
        mock_form = {"SAMLResponse": base64.b64encode(b"mock_saml_response").decode()}
        request.form = AsyncMock(return_value=mock_form)

        response = await saml_service._extract_saml_response(request)
        assert response == "mock_saml_response"

    @pytest.mark.asyncio
    async def test_extract_saml_response_missing(self, saml_service):
        """Test SAML response extraction when missing."""
        request = MagicMock()
        mock_form = {}
        request.form = AsyncMock(return_value=mock_form)

        with pytest.raises(HTTPException) as exc_info:
            await saml_service._extract_saml_response(request)

        assert exc_info.value.status_code == 400
        assert "Invalid SAML response" in str(exc_info.value.detail)

    def test_extract_user_info_with_attributes(self, saml_service):
        """Test user info extraction with SAML attributes."""
        # Create mock assertion with attributes
        mock_assertion = MagicMock()
        mock_assertion.attribute_statement = MagicMock()

        # Create mock attributes
        mock_email_attr = MagicMock()
        mock_email_attr.name = "email"
        mock_email_attr.attribute_value = [MagicMock(text="test@example.com")]

        mock_name_attr = MagicMock()
        mock_name_attr.name = "givenName"
        mock_name_attr.attribute_value = [MagicMock(text="Test")]

        mock_assertion.attribute_statement.attribute = [mock_email_attr, mock_name_attr]

        # Mock name ID
        mock_assertion.subject.name_id = MagicMock()
        mock_assertion.subject.name_id.text = "user123"

        # Create mock authn response
        mock_authn_response = MagicMock()
        mock_authn_response.assertions = [mock_assertion]

        user_info = saml_service._extract_user_info(mock_authn_response)

        assert user_info["email"] == "test@example.com"
        assert user_info["first_name"] == "Test"
        assert user_info["external_id"] == "user123"
        assert "email" in user_info["sso_attributes"]
        assert "givenName" in user_info["sso_attributes"]

    def test_extract_user_info_no_attributes(self, saml_service):
        """Test user info extraction without attributes."""
        # Create mock assertion without attributes
        mock_assertion = MagicMock()
        mock_assertion.attribute_statement = None

        # Mock name ID with email
        mock_assertion.subject.name_id = MagicMock()
        mock_assertion.subject.name_id.text = "test@example.com"

        # Create mock authn response
        mock_authn_response = MagicMock()
        mock_authn_response.assertions = [mock_assertion]

        user_info = saml_service._extract_user_info(mock_authn_response)

        assert user_info["email"] == "test@example.com"
        assert user_info["external_id"] == "test@example.com"

    def test_extract_user_info_no_identifiers(self, saml_service):
        """Test user info extraction with no email or external ID."""
        # Create mock assertion without identifiers
        mock_assertion = MagicMock()
        mock_assertion.attribute_statement = None
        mock_assertion.subject.name_id = None

        # Create mock authn response
        mock_authn_response = MagicMock()
        mock_authn_response.assertions = [mock_assertion]

        with pytest.raises(HTTPException) as exc_info:
            saml_service._extract_user_info(mock_authn_response)

        assert exc_info.value.status_code == 400
        assert "Failed to extract user information" in str(exc_info.value.detail)

    def test_get_metadata_no_client(self, saml_service):
        """Test metadata generation when client is not initialized."""
        saml_service.saml_client = None

        with pytest.raises(HTTPException) as exc_info:
            saml_service.get_metadata()

        assert exc_info.value.status_code == 400
        assert "SAML client not initialized" in str(exc_info.value.detail)

    def test_get_metadata_success(self, saml_service, mock_saml_client):
        """Test successful metadata generation."""
        saml_service.saml_client = mock_saml_client

        # Mock metadata creation
        with patch(
            "app.services.saml_service.create_metadata_string",
        ) as mock_create_metadata:
            mock_create_metadata.return_value = "<xml>metadata</xml>"

            metadata = saml_service.get_metadata()

            assert metadata == "<xml>metadata</xml>"
            mock_create_metadata.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_saml_user(self, saml_service):
        """Test SAML user processing."""
        user_info = {"email": "test@example.com", "external_id": "user123"}

        user = await saml_service.process_saml_user(user_info, MagicMock())

        assert user["id"] == "mock-saml-user-id"
        assert user["email"] == "test@example.com"
        assert user["external_id"] == "user123"
        assert user["auth_provider"] == "saml"

    @pytest.mark.asyncio
    async def test_create_saml_tokens(self, saml_service):
        """Test SAML token creation."""
        user = {"id": "user123", "email": "test@example.com"}

        tokens = await saml_service.create_saml_tokens(user)

        assert tokens["access_token"] == "mock-saml-access-token"
        assert tokens["refresh_token"] == "mock-saml-refresh-token"
        assert tokens["token_type"] == "bearer"
        assert tokens["expires_in"] == 1800


class TestMockSamlSettings:
    """Test cases for MockSamlSettings."""

    def test_mock_settings_initialization(self):
        """Test MockSamlSettings initialization."""
        settings = MockSamlSettings()

        assert settings.sso_saml_enabled is False
        assert settings.sso_saml_metadata_url is None
        assert settings.sso_saml_entity_id == "http://localhost:8000"
        assert (
            settings.sso_saml_acs_url
            == "http://localhost:8000/api/v1/auth/sso/callback/saml"
        )
        assert settings.sso_saml_cert_file is None
        assert settings.sso_saml_key_file is None
