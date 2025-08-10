"""
Authentication endpoints for user login, logout, and token management.

This module provides the core authentication API endpoints.
"""

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials
from loguru import logger
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError

from backend.app.core.config import get_settings
from backend.app.core.database import get_db
from backend.app.core.security import (
    create_access_token,
    create_refresh_token,
    get_current_user_id,
    log_security_event,
    security,
    verify_password,
)
from backend.app.models.user import User
from backend.app.services.audit_service import audit_service

router = APIRouter()


from backend.app.api.v1.endpoints.auth.models import (
    RefreshTokenRequest,
    TokenResponse,
    UserLogin,
    UserResponse,
    PasswordResetRequest,
    PasswordResetConfirm,
)


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
            details={"error": "Missing email or username"},
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
            details={"error": "Invalid credentials", "identifier": identifier},
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
            details={"error": "Account disabled", "identifier": identifier},
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
    user.last_login = datetime.now(UTC)
    db.commit()

    # Log successful login
    await audit_service.log_user_login(
        user_id=str(user.id),
        ip_address=client_ip,
        user_agent=user_agent,
        session_id=session_id,
        success=True,
        details={"identifier": identifier},
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


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    """
    Refresh access token using refresh token.

    Args:
        refresh_token_data: Refresh token data
        db: Database session

    Returns:
        TokenResponse: New access and refresh tokens

    Raises:
        HTTPException: If refresh token is invalid
    """
    try:
        # Verify refresh token
        user_id = verify_token(refresh_token_data.refresh_token)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create new tokens
        access_token = create_access_token(subject=user.id)
        new_refresh_token = create_refresh_token(subject=user.id)

        logger.info(f"Token refreshed for user: {user.email}")

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=get_settings().jwt_access_token_expire_minutes * 60,
        )

    except Exception as e:
        logger.exception(f"Token refresh failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    settings=Depends(get_settings),
):
    """
    Logout user and invalidate tokens.

    Args:
        credentials: HTTP authorization credentials
        settings: Application settings

    Returns:
        dict: Logout confirmation
    """
    try:
        # Verify token
        user_id = verify_token(credentials.credentials)
        if user_id:
            # Log logout event
            log_security_event(
                event_type="user_logout",
                user_id=user_id,
                description="User logged out successfully",
                severity="info",
            )
            logger.info(f"User logged out: {user_id}")

        return {"message": "Logout successful"}

    except Exception as e:
        logger.exception(f"Logout failed: {str(e)}")
        # Still return success to avoid exposing internal errors
        return {"message": "Logout successful"}


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

    Raises:
        HTTPException: If user not found
    """
    user = db.query(User).filter(User.id == current_user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        display_name=user.display_name,
        role=user.role.value,
        is_active=user.is_active,
        is_verified=user.email_verified,
    )


@router.post("/forgot-password")
async def forgot_password(request_data: PasswordResetRequest, db: Session = Depends(get_db)):
    """Initiate password reset flow; always return success message."""
    from backend.app.services.email_service import email_service
    from backend.app.services.token_service import token_service
    from backend.app.core.security_hardening import SSOSecurityValidator

    validator = SSOSecurityValidator()

    client_ip = "unknown"

    if not validator.rate_limit_password_reset_by_email(request_data.email):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many password reset requests for this email. Please try again later.",
        )

    if not validator.rate_limit_password_reset_by_ip(client_ip or request_data.email):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many password reset requests. Please try again later.",
        )

    try:
        user = db.query(User).filter(User.email == request_data.email.lower()).first()
        if user:
            token = token_service.create_password_reset_token(user, db)
            reset_url = f"{get_settings().backend_url}/reset-password?token={token}"
            try:
                email_service.send_password_reset_email(
                    user.email, token, reset_url, language=get_settings().default_language
                )
            except Exception:
                pass
    except OperationalError:
        # DB not initialized in some test contexts; still return generic success
        pass

    return {
        "status": "success",
        "message": "If the email address exists, a password reset link has been sent.",
    }


@router.post("/reset-password")
async def reset_password(data: PasswordResetConfirm, db: Session = Depends(get_db)):
    """Reset password given a valid token."""
    from backend.app.services.token_service import token_service

    try:
        user = token_service.validate_password_reset_token(data.token, db, return_user=True)
    except OperationalError:
        user = None

    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    if not data.new_password or len(data.new_password) < 6:
        raise HTTPException(status_code=422, detail="Password too short")

    user.hashed_password = get_password_hash(data.new_password)
    user.password_reset_token = None
    user.password_reset_expires_at = None
    db.commit()

    return {"status": "success", "message": "Password reset successfully"}


@router.post("/validate-reset-token")
async def validate_reset_token(payload: dict, db: Session = Depends(get_db)):
    """Validate reset token and return validity info."""
    from backend.app.services.token_service import token_service

    token = payload.get("token", "")
    try:
        user = token_service.validate_password_reset_token(token, db, return_user=True)
    except OperationalError:
        user = None

    if user:
        return {"valid": True, "message": "Token is valid"}
    return {"valid": False, "message": "Token is invalid or expired"}
