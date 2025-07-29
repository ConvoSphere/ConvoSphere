"""
Authentication endpoints for user login, registration, and token management.

This module provides the authentication API endpoints for the AI Assistant Platform.
"""

import uuid
from typing import Any

from backend.app.core.config import get_settings
from backend.app.core.database import get_db
from backend.app.core.dependencies import require_admin_role
from backend.app.core.security import security
from backend.app.core.config import get_settings
from backend.app.core.security import (
    create_access_token,
    create_refresh_token,
    get_current_user_id,
    get_password_hash,
    log_security_event,
    verify_password,
    verify_token,
)
from backend.app.core.security_hardening import (
    get_client_ip,
    sso_audit_logger,
    sso_security_validator,
    validate_sso_request,
)
from backend.app.models.user import User, UserRole
from backend.app.services.advanced_user_provisioning import advanced_user_provisioning
from backend.app.services.oauth_service import oauth_service
from backend.app.services.saml_service import saml_service
from backend.app.services.user_service import UserService
from backend.app.services.audit_service import audit_service
from backend.app.models.audit import AuditEventType, AuditSeverity
from fastapi import APIRouter, Depends, HTTPException, Request, status

# Workaround gegen Import-Zyklen: security wird erst hier importiert
from fastapi.security import HTTPAuthorizationCredentials
from loguru import logger
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

router = APIRouter()


# Pydantic models for request/response
class UserLogin(BaseModel):
    email: EmailStr | None = None
    username: str | None = None
    password: str


class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str
    first_name: str | None = None
    last_name: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    first_name: str | None
    last_name: str | None
    display_name: str | None
    role: str
    is_active: bool
    is_verified: bool


@router.post("/login", response_model=TokenResponse)
async def login(
    user_credentials: UserLogin,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Authenticate user and return access token.

    Args:
        user_credentials: User login credentials (email or username)
        db: Database session

    Returns:
        TokenResponse: Access and refresh tokens

    Raises:
        HTTPException: If credentials are invalid
    """
    # Get client information
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "")
    session_id = str(uuid.uuid4())

    # Find user by email or username
    if user_credentials.email:
        user = db.query(User).filter(User.email == user_credentials.email).first()
        identifier = user_credentials.email
    elif user_credentials.username:
        user = db.query(User).filter(User.username == user_credentials.username).first()
        identifier = user_credentials.username
    else:
        # Log failed login attempt
        await audit_service.log_user_login(
            user_id=None,
            ip_address=client_ip,
            user_agent=user_agent,
            session_id=session_id,
            success=False,
            details={"error": "Missing email or username"}
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either email or username must be provided",
        )

    if not user or not verify_password(user_credentials.password, user.hashed_password):
        # Log failed login attempt
        await audit_service.log_user_login(
            user_id=str(user.id) if user else None,
            ip_address=client_ip,
            user_agent=user_agent,
            session_id=session_id,
            success=False,
            details={"error": "Invalid credentials", "identifier": identifier}
        )
        logger.warning(f"Failed login attempt for identifier: {identifier}")
        log_security_event(
            event_type="user_login",
            user_id=None,
            description=f"Failed login attempt for {identifier}",
            severity="warning",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        # Log failed login attempt
        await audit_service.log_user_login(
            user_id=str(user.id),
            ip_address=client_ip,
            user_agent=user_agent,
            session_id=session_id,
            success=False,
            details={"error": "Account disabled", "identifier": identifier}
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create tokens
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)

    # Update last login
    from datetime import UTC, datetime

    user.last_login = datetime.now(UTC)
    db.commit()

    # Log successful login
    await audit_service.log_user_login(
        user_id=str(user.id),
        ip_address=client_ip,
        user_agent=user_agent,
        session_id=session_id,
        success=True,
        details={"identifier": identifier}
    )

    log_security_event(
        event_type="user_login",
        user_id=user.id,
        description=f"User {user.email} logged in successfully",
        severity="info",
    )

    logger.info(f"User logged in successfully: {user.email}")

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=get_settings().jwt_access_token_expire_minutes * 60,
    )


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db),
):
    settings = get_settings()
    if not settings.registration_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Registration is disabled. Please contact the administrator.",
        )
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Check if username already exists
    existing_username = (
        db.query(User).filter(User.username == user_data.username).first()
    )
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        role=UserRole.USER,  # Default role
        is_verified=False,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info(f"New user registered: {new_user.email}")

    return UserResponse(
        id=str(new_user.id),
        email=new_user.email,
        username=new_user.username,
        first_name=new_user.first_name,
        last_name=new_user.last_name,
        display_name=new_user.display_name,
        role=new_user.role.value,
        is_active=new_user.is_active,
        is_verified=new_user.is_verified,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db),
):
    """
    Refresh access token using refresh token.

    Args:
        refresh_token: Refresh token
        db: Database session

    Returns:
        TokenResponse: New access and refresh tokens

    Raises:
        HTTPException: If refresh token is invalid
    """
    user_id = verify_token(refresh_token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify user exists and is active
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create new tokens
    new_access_token = create_access_token(subject=user.id)
    new_refresh_token = create_refresh_token(subject=user.id)

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=get_settings().jwt_access_token_expire_minutes * 60,
    )


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    settings=Depends(get_settings),
):
    """
    Logout user (invalidate tokens).

    Args:
        current_user_id: Current user ID from token
        credentials: HTTP authorization credentials

    Returns:
        dict: Logout confirmation
    """
    try:
        # Add token to blacklist
        from backend.app.core.redis_client import get_redis
        from backend.app.core.security import BLACKLIST_PREFIX

        redis = await get_redis()
        token = credentials.credentials

        # Calculate token expiration time
        from jose import jwt

        try:
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=[settings.jwt_algorithm],
            )
            exp = payload.get("exp")
            if exp:
                # Calculate time until expiration
                import time

                ttl = int(exp - time.time())
                if ttl > 0:
                    await redis.set(f"{BLACKLIST_PREFIX}{token}", "1", ex=ttl)
        except Exception as e:
            logger.error(f"Token blacklisting error: {e}")

        # Log security event
        from backend.app.core.security import log_security_event

        log_security_event(
            event_type="user_logout",
            user_id=get_current_user_id(),
            description="User logged out successfully",
            severity="info",
        )

        logger.info(f"User logged out: {get_current_user_id()}")
        return {"message": "Successfully logged out"}

    except Exception as e:
        logger.error(f"Logout error: {e}")
        return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Get current user information.

    Args:
        current_user_id: Current user ID from token
        db: Database session

    Returns:
        UserResponse: Current user information
    """
    user = db.query(User).filter(User.id == current_user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserResponse(
        id=str(user.id),
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        display_name=user.display_name,
        role=user.role.value,
        is_active=user.is_active,
        is_verified=user.is_verified,
    )


@router.get("/sso/providers")
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

    return {"providers": providers}


@router.get("/sso/login/{provider}")
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
            login_url = await saml_service.get_login_url(request)
            from fastapi.responses import RedirectResponse

            return RedirectResponse(url=login_url)
        # Use OAuth service to get authorization URL
        return await oauth_service.get_authorization_url(provider, request)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"SSO login failed for {provider}: {e}")
        sso_audit_logger.log_sso_event(
            event_type="sso_login_failure",
            provider=provider,
            details={"error": str(e)},
            severity="error",
            ip_address=get_client_ip(request),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate {provider} SSO login",
        )


@router.get("/sso/callback/{provider}")
async def sso_callback(provider: str, request: Request, db: Session = Depends(get_db)):
    """Handle SSO callback and user provisioning/account-linking."""
    try:
        # Security validation
        if not validate_sso_request(request, provider):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
            )

        client_ip = get_client_ip(request)

        if provider == "saml":
            # Validate SAML response
            form_data = await request.form()
            saml_response = form_data.get("SAMLResponse")
            if saml_response and not sso_security_validator.validate_saml_response(
                saml_response,
            ):
                sso_audit_logger.log_sso_event(
                    event_type="suspicious_saml_response",
                    provider=provider,
                    severity="warning",
                    ip_address=client_ip,
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid SAML response",
                )

            # Handle SAML callback
            callback_result = await saml_service.handle_saml_response(request)
            user_info = callback_result["user_info"]

            # Validate and sanitize user attributes
            is_valid, error_msg = sso_security_validator.validate_user_attributes(
                user_info,
            )
            if not is_valid:
                sso_audit_logger.log_sso_event(
                    event_type="invalid_user_attributes",
                    provider=provider,
                    details={"error": error_msg},
                    severity="warning",
                    ip_address=client_ip,
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid user attributes: {error_msg}",
                )

            # Sanitize user data
            user_info = sso_security_validator.sanitize_user_data(user_info)

            # Process SAML user (create or update)
            user = await saml_service.process_saml_user(user_info, db)

            # Create JWT tokens
            tokens = await saml_service.create_saml_tokens(user)
        else:
            # Handle OAuth callback
            callback_result = await oauth_service.handle_callback(provider, request)
            user_info = callback_result["user_info"]

            # Validate and sanitize user attributes
            is_valid, error_msg = sso_security_validator.validate_user_attributes(
                user_info,
            )
            if not is_valid:
                sso_audit_logger.log_sso_event(
                    event_type="invalid_user_attributes",
                    provider=provider,
                    details={"error": error_msg},
                    severity="warning",
                    ip_address=client_ip,
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid user attributes: {error_msg}",
                )

            # Sanitize user data
            user_info = sso_security_validator.sanitize_user_data(user_info)

            # Process SSO user (create or update)
            user = await oauth_service.process_sso_user(user_info, provider, db)

            # Create JWT tokens
            tokens = await oauth_service.create_sso_tokens(user)

        # Log successful SSO event
        log_security_event(
            event_type="sso_login",
            user_id=user.id,
            description=f"User {user.email} logged in via SSO ({provider})",
            severity="info",
        )

        sso_audit_logger.log_sso_event(
            event_type="sso_login_success",
            user_id=str(user.id),
            provider=provider,
            severity="info",
            ip_address=client_ip,
        )

        logger.info(f"SSO login successful for {user.email} via {provider}")

        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=tokens["expires_in"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"SSO callback failed for {provider}: {e}")
        sso_audit_logger.log_sso_event(
            event_type="sso_callback_failure",
            provider=provider,
            details={"error": str(e)},
            severity="error",
            ip_address=get_client_ip(request),
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"SSO authentication failed: {str(e)}",
        )


@router.post("/sso/link/{provider}")
async def sso_link(
    provider: str,
    request: Request,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Link SSO account to existing user account."""
    # Pseudo-code: Extract SSO info and link to current user
    user_service = UserService(db)
    user = user_service.get_user_by_id(current_user_id)
    # Example: user.external_id = ...; user.auth_provider = provider
    # db.commit()
    log_security_event(
        event_type="sso_link",
        user_id=user.id,
        description=f"User {user.email} linked SSO account ({provider})",
        severity="info",
    )
    return {"message": f"SSO account linked for {provider}"}


@router.get("/sso/metadata")
async def get_saml_metadata():
    """Get SAML metadata for this service provider."""
    try:
        metadata = saml_service.get_metadata()
        from fastapi.responses import Response

        return Response(content=metadata, media_type="application/xml")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get SAML metadata: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get SAML metadata",
        )


@router.post("/sso/link/{provider}")
async def link_sso_account(
    provider: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Link current user account with SSO provider."""
    try:
        # Security validation
        if not validate_sso_request(request, provider):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
            )

        # Get current user
        current_user_id = get_current_user_id(request)
        if not current_user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )

        # Log account linking attempt
        client_ip = get_client_ip(request)
        sso_audit_logger.log_sso_event(
            event_type="account_linking_attempt",
            user_id=str(current_user_id),
            provider=provider,
            severity="info",
            ip_address=client_ip,
        )

        # Redirect to SSO provider for linking
        if provider == "saml":
            login_url = await saml_service.get_login_url(request)
        else:
            login_url = await oauth_service.get_authorization_url(provider, request)

        from fastapi.responses import RedirectResponse

        return RedirectResponse(url=login_url)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"SSO account linking failed for {provider}: {e}")
        sso_audit_logger.log_sso_event(
            event_type="account_linking_failure",
            user_id=str(current_user_id) if "current_user_id" in locals() else None,
            provider=provider,
            details={"error": str(e)},
            severity="error",
            ip_address=get_client_ip(request),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to link account with {provider}",
        )


@router.get("/sso/unlink/{provider}")
async def unlink_sso_account(
    provider: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Unlink current user account from SSO provider."""
    try:
        # Get current user
        current_user_id = get_current_user_id(request)
        if not current_user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )

        user_service = UserService(db)
        user = user_service.get_user_by_id(current_user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        # Remove SSO attributes for the specific provider
        if user.sso_attributes:
            user.sso_attributes.pop(provider, None)
            db.commit()

        # Log account unlinking
        client_ip = get_client_ip(request)
        sso_audit_logger.log_sso_event(
            event_type="account_unlinked",
            user_id=str(current_user_id),
            provider=provider,
            severity="info",
            ip_address=client_ip,
        )

        return {"message": f"Successfully unlinked account from {provider}"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"SSO account unlinking failed for {provider}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to unlink account from {provider}",
        )


@router.get("/sso/provisioning/status/{user_id}")
async def get_user_provisioning_status(
    user_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Get advanced provisioning status for a user."""
    try:
        # Check if user has admin permissions
        current_user_id = get_current_user_id(request)
        if not current_user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )

        # For now, allow any authenticated user to view their own status
        # In production, add proper authorization checks
        if current_user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        return await advanced_user_provisioning.get_user_provisioning_status(
            user_id,
            db,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get provisioning status for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get provisioning status",
        )


@router.post("/sso/bulk-sync/{provider}")
async def bulk_sync_users(
    provider: str,
    user_list: list[dict[str, Any]],
    request: Request,
    current_user: User = Depends(require_admin_role),
    db: Session = Depends(get_db),
):
    """Bulk sync users from SSO provider (Admin only)."""
    try:

        # Security validation
        if not validate_sso_request(request, provider):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
            )

        # Perform bulk sync
        results = await advanced_user_provisioning.bulk_sync_users(
            provider,
            user_list,
            db,
        )

        # Log bulk sync event
        client_ip = get_client_ip(request)
        sso_audit_logger.log_sso_event(
            event_type="bulk_sync_completed",
            user_id=str(current_user.id),
            provider=provider,
            details=results,
            severity="info",
            ip_address=client_ip,
        )

        return results

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Bulk sync failed for {provider}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk sync failed: {str(e)}",
        )


# Example for permission denied:
# log_security_event(
#     event_type="PERMISSION_DENIED",
#     user_id=user.id if user else None,
#     description="Permission denied for endpoint X",
#     severity="warning"
# )
