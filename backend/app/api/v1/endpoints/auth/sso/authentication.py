"""
SSO Authentication endpoints.

This module provides SSO login and callback functionality.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from loguru import logger
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security_hardening import (
    get_client_ip,
    sso_audit_logger,
    validate_sso_request,
)

router = APIRouter()


@router.get("/login/{provider}")
async def sso_login(provider: str, request: Request):
    """Initiate SSO login with the given provider."""
    try:
        # Security validation
        if not validate_sso_request(request, provider):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
            )

        # Log SSO login attempt
        client_ip = get_client_ip(request)
        sso_audit_logger.log_sso_event(
            event_type="sso_login_attempt",
            provider=provider,
            severity="info",
            ip_address=client_ip,
        )

        if provider == "saml":
            # Handle SAML login
            from backend.app.services.saml_service import saml_service

            login_url = await saml_service.get_login_url(request)
            from fastapi.responses import RedirectResponse

            return RedirectResponse(url=login_url)

        # Use OAuth service to get authorization URL
        from backend.app.services.oauth_service import oauth_service

        return await oauth_service.get_authorization_url(provider, request)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"SSO login failed for {provider}: {e}")
        sso_audit_logger.log_sso_event(
            event_type="sso_login_failure",
            provider=provider,
            severity="error",
            ip_address=get_client_ip(request),
            details={"error": str(e)},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SSO login failed",
        )


@router.get("/callback/{provider}")
async def sso_callback(provider: str, request: Request, db: Session = Depends(get_db)):
    """Handle SSO callback from the given provider."""
    try:
        # Log SSO callback attempt
        client_ip = get_client_ip(request)
        sso_audit_logger.log_sso_event(
            event_type="sso_callback_attempt",
            provider=provider,
            severity="info",
            ip_address=client_ip,
        )

        if provider == "saml":
            # Handle SAML callback
            from backend.app.services.saml_service import saml_service

            result = await saml_service.handle_callback(request, db)
        else:
            # Handle OAuth callback
            from backend.app.services.oauth_service import oauth_service

            result = await oauth_service.handle_callback(provider, request, db)

        # Log successful SSO callback
        sso_audit_logger.log_sso_event(
            event_type="sso_callback_success",
            provider=provider,
            severity="info",
            ip_address=client_ip,
            details={"user_id": result.get("user_id")},
        )

        return result

    except Exception as e:
        logger.error(f"SSO callback failed for {provider}: {e}")
        sso_audit_logger.log_sso_event(
            event_type="sso_callback_failure",
            provider=provider,
            severity="error",
            ip_address=get_client_ip(request),
            details={"error": str(e)},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SSO callback failed",
        )
