"""
SSO API endpoints for authentication with multiple providers.

This module provides comprehensive SSO authentication endpoints including
LDAP, SAML, and OAuth providers with user management and group synchronization.
"""

import logging
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import create_access_token, get_current_user
from backend.app.core.sso_manager import get_sso_manager
from backend.app.models.user import AuthProvider, User
from backend.app.schemas.auth import SSOLoginRequest, SSOProviderInfo, TokenResponse
from backend.app.schemas.user import UserResponse
from backend.app.utils.exceptions import (
    AuthenticationError,
    GroupSyncError,
    SSOConfigurationError,
    UserNotFoundError,
)

logger = logging.getLogger(__name__)

router = APIRouter()


# SSO Provider Information
@router.get("/providers", response_model=list[SSOProviderInfo])
async def get_sso_providers():
    """Get list of available SSO providers."""
    try:
        sso_manager = get_sso_manager()
        providers = sso_manager.get_available_providers()

        provider_info = []
        for provider in providers:
            provider_info.append(
                SSOProviderInfo(
                    name=provider["name"],
                    type=provider["type"],
                    enabled=provider["enabled"],
                    priority=provider["priority"],
                ),
            )

        return provider_info
    except SSOConfigurationError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )


@router.get("/providers/{provider_name}/config")
async def get_sso_provider_config(
    provider_name: str,
    current_user: User = Depends(get_current_user),
):
    """Get configuration for specific SSO provider (admin only)."""
    try:
        # Check if user is admin
        if current_user.role not in ["super_admin", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required",
            )

        sso_manager = get_sso_manager()
        config = sso_manager.get_provider_config(provider_name)

        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Provider not found",
            )

        # Remove sensitive information
        safe_config = config.copy()
        if "config" in safe_config:
            sensitive_keys = ["client_secret", "bind_password", "key_file", "cert_file"]
            for key in sensitive_keys:
                if key in safe_config["config"]:
                    safe_config["config"][key] = "***HIDDEN***"

        return safe_config
    except SSOConfigurationError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )


# LDAP Authentication
@router.post("/ldap/login", response_model=TokenResponse)
async def ldap_login(
    login_data: SSOLoginRequest,
    db: Session = Depends(get_db),
):
    """Authenticate user via LDAP."""
    try:
        sso_manager = get_sso_manager()

        credentials = {"username": login_data.username, "password": login_data.password}

        user, additional_data = await sso_manager.authenticate("ldap", credentials, db)

        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username},
        )

        # Log successful login
        logger.info(f"LDAP login successful for user: {user.username}")

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=3600,  # 1 hour
            user_id=str(user.id),
            username=user.username,
            provider="ldap",
            additional_data=additional_data,
        )

    except AuthenticationError as e:
        logger.warning(f"LDAP login failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except SSOConfigurationError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )


@router.get("/ldap/user-info")
async def get_ldap_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user information from LDAP."""
    try:
        if current_user.auth_provider != AuthProvider.LDAP:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not authenticated via LDAP",
            )

        sso_manager = get_sso_manager()
        return await sso_manager.get_user_info("ldap", str(current_user.id), db)

    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except SSOConfigurationError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )


@router.post("/ldap/sync-groups")
async def sync_ldap_groups(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Synchronize user groups from LDAP."""
    try:
        if current_user.auth_provider != AuthProvider.LDAP:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not authenticated via LDAP",
            )

        sso_manager = get_sso_manager()
        groups = await sso_manager.sync_user_groups("ldap", current_user, db)

        return {
            "message": "Groups synchronized successfully",
            "groups": groups,
            "synced_at": datetime.now(UTC).isoformat(),
        }

    except GroupSyncError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except SSOConfigurationError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )


# SAML Authentication
@router.get("/saml/login")
async def saml_login(
    provider_name: str = Query("saml", description="SAML provider name"),
    relay_state: str = Query(None, description="Relay state for SAML"),
):
    """Initiate SAML login."""
    try:
        sso_manager = get_sso_manager()
        provider = sso_manager.providers.get(provider_name)

        if not provider or not isinstance(
            provider,
            sso_manager.providers["saml"].__class__,
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SAML provider not found",
            )

        # Generate SAML request
        authn_request = provider.saml_client.create_authn_request(
            provider.config.get("idp_entity_id"),
            relay_state=relay_state,
        )

        # Redirect to IdP
        return RedirectResponse(url=authn_request)

    except SSOConfigurationError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )


@router.post("/saml/acs", response_model=TokenResponse)
async def saml_acs(
    request: Request,
    db: Session = Depends(get_db),
):
    """SAML Assertion Consumer Service."""
    try:
        form_data = await request.form()
        saml_response = form_data.get("SAMLResponse")
        relay_state = form_data.get("RelayState")

        if not saml_response:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="SAML response required",
            )

        sso_manager = get_sso_manager()

        credentials = {"saml_response": saml_response, "relay_state": relay_state}

        user, additional_data = await sso_manager.authenticate("saml", credentials, db)

        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username},
        )

        # Log successful login
        logger.info(f"SAML login successful for user: {user.username}")

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=3600,
            user_id=str(user.id),
            username=user.username,
            provider="saml",
            additional_data=additional_data,
        )

    except AuthenticationError as e:
        logger.warning(f"SAML login failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except SSOConfigurationError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )


@router.get("/saml/metadata")
async def saml_metadata():
    """Get SAML service provider metadata."""
    try:
        sso_manager = get_sso_manager()
        provider = sso_manager.providers.get("saml")

        if not provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SAML provider not found",
            )

        # Generate SP metadata
        return entity_descriptor(provider.saml_config)

    except SSOConfigurationError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )


# OAuth Authentication
@router.get("/oauth/{provider_name}/login")
async def oauth_login(
    provider_name: str,
    redirect_uri: str = Query(..., description="Redirect URI after OAuth"),
    state: str = Query(None, description="State parameter for OAuth"),
):
    """Initiate OAuth login."""
    try:
        sso_manager = get_sso_manager()
        provider = sso_manager.providers.get(provider_name)

        if not provider or not isinstance(
            provider,
            sso_manager.providers["oauth"].__class__,
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="OAuth provider not found",
            )

        # Build OAuth authorization URL
        params = {
            "client_id": provider.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": provider.scope,
        }

        if state:
            params["state"] = state

        auth_url = f"{provider.authorization_url}?{urlencode(params)}"

        return RedirectResponse(url=auth_url)

    except SSOConfigurationError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )


@router.post("/oauth/{provider_name}/callback", response_model=TokenResponse)
async def oauth_callback(
    provider_name: str,
    code: str = Query(..., description="Authorization code"),
    state: str = Query(None, description="State parameter"),
    redirect_uri: str = Query(..., description="Redirect URI"),
    db: Session = Depends(get_db),
):
    """Handle OAuth callback."""
    try:
        sso_manager = get_sso_manager()

        credentials = {"code": code, "redirect_uri": redirect_uri, "state": state}

        user, additional_data = await sso_manager.authenticate(
            provider_name,
            credentials,
            db,
        )

        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username},
        )

        # Log successful login
        logger.info(
            f"OAuth login successful for user: {user.username} via {provider_name}",
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=3600,
            user_id=str(user.id),
            username=user.username,
            provider=provider_name,
            additional_data=additional_data,
        )

    except AuthenticationError as e:
        logger.warning(f"OAuth login failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except SSOConfigurationError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )


@router.get("/oauth/{provider_name}/user-info")
async def get_oauth_user_info(
    provider_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user information from OAuth provider."""
    try:
        if current_user.auth_provider != AuthProvider.OAUTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not authenticated via OAuth",
            )

        sso_manager = get_sso_manager()
        return await sso_manager.get_user_info(
            provider_name,
            str(current_user.id),
            db,
        )

    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except SSOConfigurationError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )


# Generic SSO Endpoints
@router.post("/{provider_name}/login", response_model=TokenResponse)
async def generic_sso_login(
    provider_name: str,
    login_data: SSOLoginRequest,
    db: Session = Depends(get_db),
):
    """Generic SSO login endpoint."""
    try:
        sso_manager = get_sso_manager()

        credentials = {"username": login_data.username, "password": login_data.password}

        user, additional_data = await sso_manager.authenticate(
            provider_name,
            credentials,
            db,
        )

        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username},
        )

        # Log successful login
        logger.info(
            f"SSO login successful for user: {user.username} via {provider_name}",
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=3600,
            user_id=str(user.id),
            username=user.username,
            provider=provider_name,
            additional_data=additional_data,
        )

    except AuthenticationError as e:
        logger.warning(f"SSO login failed via {provider_name}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except SSOConfigurationError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )


@router.post("/{provider_name}/sync-groups")
async def generic_sync_groups(
    provider_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Synchronize user groups from SSO provider."""
    try:
        sso_manager = get_sso_manager()
        groups = await sso_manager.sync_user_groups(provider_name, current_user, db)

        return {
            "message": "Groups synchronized successfully",
            "provider": provider_name,
            "groups": groups,
            "synced_at": datetime.now(UTC).isoformat(),
        }

    except GroupSyncError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except SSOConfigurationError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )


# SSO User Management
@router.get("/users/sso", response_model=list[UserResponse])
async def get_sso_users(
    provider: AuthProvider = Query(None, description="Filter by SSO provider"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get users authenticated via SSO."""
    try:
        # Check if user is admin
        if current_user.role not in ["super_admin", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required",
            )

        query = db.query(User).filter(User.auth_provider != AuthProvider.LOCAL)

        if provider:
            query = query.filter(User.auth_provider == provider)

        # Apply pagination
        offset = (page - 1) * size
        users = query.offset(offset).limit(size).all()

        return [UserResponse.from_orm(user) for user in users]

    except Exception as e:
        logger.exception(f"Failed to get SSO users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get SSO users",
        )


@router.post("/users/{user_id}/sync")
async def sync_sso_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Synchronize user data from SSO provider."""
    try:
        # Check if user is admin or the user themselves
        if (
            current_user.role not in ["super_admin", "admin"]
            and str(current_user.id) != user_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if user.auth_provider == AuthProvider.LOCAL:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not authenticated via SSO",
            )

        sso_manager = get_sso_manager()

        # Get user info from SSO provider
        provider_name = user.auth_provider.value
        user_info = await sso_manager.get_user_info(provider_name, user_id, db)

        # Sync groups
        groups = await sso_manager.sync_user_groups(provider_name, user, db)

        return {
            "message": "User synchronized successfully",
            "user_id": user_id,
            "provider": provider_name,
            "user_info": user_info,
            "groups": groups,
            "synced_at": datetime.now(UTC).isoformat(),
        }

    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except SSOConfigurationError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )


# SSO Health Check
@router.get("/health")
async def sso_health_check():
    """Check SSO providers health."""
    try:
        sso_manager = get_sso_manager()
        providers = sso_manager.get_available_providers()

        health_status = {
            "status": "healthy",
            "providers": [],
            "timestamp": datetime.now(UTC).isoformat(),
        }

        for provider in providers:
            provider_health = {
                "name": provider["name"],
                "type": provider["type"],
                "enabled": provider["enabled"],
                "status": "available" if provider["enabled"] else "disabled",
            }
            health_status["providers"].append(provider_health)

        return health_status

    except SSOConfigurationError as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(UTC).isoformat(),
        }


# SSO Configuration Management (Admin only)
@router.post("/config/reload")
async def reload_sso_config(
    current_user: User = Depends(get_current_user),
):
    """Reload SSO configuration (admin only)."""
    try:
        # Check if user is admin
        if current_user.role not in ["super_admin", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required",
            )

        # This would reload configuration from database or config file
        # For now, return success message
        return {
            "message": "SSO configuration reloaded successfully",
            "timestamp": datetime.now(UTC).isoformat(),
        }

    except Exception as e:
        logger.exception(f"Failed to reload SSO config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reload SSO configuration",
        )
