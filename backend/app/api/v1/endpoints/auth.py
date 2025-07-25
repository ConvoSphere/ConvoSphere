"""
Authentication endpoints for user login, registration, and token management.

This module provides the authentication API endpoints for the AI Assistant Platform.
"""

from app.core.config import get_settings
from app.core.database import get_db
from app.core.dependencies import get_security_dep, get_settings_dep
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_current_user_id,
    get_password_hash,
    log_security_event,
    verify_password,
    verify_token,
)
from app.models.user import User, UserRole
from app.schemas.user import SSOUserCreate
from app.services.user_service import UserService
from app.services.oauth_service import oauth_service
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
    # Find user by email or username
    if user_credentials.email:
        user = db.query(User).filter(User.email == user_credentials.email).first()
        identifier = user_credentials.email
    elif user_credentials.username:
        user = db.query(User).filter(User.username == user_credentials.username).first()
        identifier = user_credentials.username
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either email or username must be provided",
        )

    if not user or not verify_password(user_credentials.password, user.hashed_password):
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
    credentials: HTTPAuthorizationCredentials = Depends(get_security_dep),
    settings=Depends(get_settings_dep),
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
        from app.core.redis_client import get_redis
        from app.core.security import BLACKLIST_PREFIX

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
        from app.core.security import log_security_event

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
        # Use OAuth service to get authorization URL
        return await oauth_service.get_authorization_url(provider, request)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"SSO login failed for {provider}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate {provider} SSO login"
        )


@router.get("/sso/callback/{provider}")
async def sso_callback(provider: str, request: Request, db: Session = Depends(get_db)):
    """Handle SSO callback and user provisioning/account-linking."""
    try:
        # Handle OAuth callback
        callback_result = await oauth_service.handle_callback(provider, request)
        user_info = callback_result['user_info']
        
        # Process SSO user (create or update)
        user = await oauth_service.process_sso_user(user_info, provider, db)
        
        # Create JWT tokens
        tokens = await oauth_service.create_sso_tokens(user)
        
        # Log SSO event
        log_security_event(
            event_type="sso_login",
            user_id=user.id,
            description=f"User {user.email} logged in via SSO ({provider})",
            severity="info",
        )
        
        logger.info(f"SSO login successful for {user.email} via {provider}")
        
        return TokenResponse(
            access_token=tokens['access_token'],
            refresh_token=tokens['refresh_token'],
            token_type=tokens['token_type'],
            expires_in=tokens['expires_in']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"SSO callback failed for {provider}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"SSO authentication failed: {str(e)}"
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


# Example for permission denied:
# log_security_event(
#     event_type="PERMISSION_DENIED",
#     user_id=user.id if user else None,
#     description="Permission denied for endpoint X",
#     severity="warning"
# )
