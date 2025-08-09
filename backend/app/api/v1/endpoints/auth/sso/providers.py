"""
SSO Provider endpoints.

This module provides SSO provider information and metadata endpoints.
"""

from fastapi import APIRouter
from loguru import logger

from backend.app.core.config import get_settings

router = APIRouter()


@router.get("/providers")
async def get_sso_providers():
    """Get list of configured SSO providers."""
    settings = get_settings()
    providers = []

    if settings.sso_google_enabled and settings.sso_google_client_id:
        providers.append(
            {
                "id": "google",
                "name": "Google",
                "type": "oauth2",
                "icon": "google",
                "login_url": "/api/v1/auth/sso/login/google",
            },
        )

    if settings.sso_microsoft_enabled and settings.sso_microsoft_client_id:
        providers.append(
            {
                "id": "microsoft",
                "name": "Microsoft",
                "type": "oauth2",
                "icon": "microsoft",
                "login_url": "/api/v1/auth/sso/login/microsoft",
            },
        )

    if settings.sso_github_enabled and settings.sso_github_client_id:
        providers.append(
            {
                "id": "github",
                "name": "GitHub",
                "type": "oauth2",
                "icon": "github",
                "login_url": "/api/v1/auth/sso/login/github",
            },
        )

    if settings.sso_saml_enabled and settings.sso_saml_metadata_url:
        providers.append(
            {
                "id": "saml",
                "name": "SAML",
                "type": "saml",
                "icon": "saml",
                "login_url": "/api/v1/auth/sso/login/saml",
                "metadata_url": "/api/v1/auth/sso/metadata",
            },
        )

    if settings.sso_oidc_enabled and settings.sso_oidc_issuer_url:
        providers.append(
            {
                "id": "oidc",
                "name": "OIDC",
                "type": "oidc",
                "icon": "oidc",
                "login_url": "/api/v1/auth/sso/login/oidc",
            },
        )

    logger.info(f"Returning {len(providers)} SSO providers")
    return {"providers": providers}


@router.get("/metadata")
async def get_saml_metadata():
    """Get SAML metadata for the service provider."""
    try:
        from backend.app.services.saml_service import saml_service

        metadata = saml_service.get_metadata()
        return metadata

    except Exception as e:
        logger.error(f"Failed to get SAML metadata: {e}")
        return {"error": "SAML metadata not available"}
