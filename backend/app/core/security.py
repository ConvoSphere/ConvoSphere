"""
Security utilities for authentication and authorization.

This module provides JWT token management, password hashing,
and security utilities for the AI Assistant Platform.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from loguru import logger
from passlib.context import CryptContext

from .config import get_settings

# Password hashing context with optimized bcrypt settings
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,  # Increased rounds for better security
)

security = HTTPBearer()

BLACKLIST_PREFIX = "jwt_blacklist:"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password

    Returns:
        bool: True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password.

    Args:
        password: Plain text password

    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)


def create_access_token(
    subject: str | Any,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a JWT access token.

    Args:
        subject: Token subject (usually user ID)
        expires_delta: Token expiration time

    Returns:
        str: JWT access token
    """
    settings = get_settings()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.security.jwt_access_token_expire_minutes,
        )

    to_encode = {"exp": expire, "sub": str(subject)}
    return jwt.encode(
        to_encode,
        settings.security.secret_key,
        algorithm=settings.security.jwt_algorithm,
    )


def create_refresh_token(
    subject: str | Any,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a JWT refresh token.

    Args:
        subject: Token subject (usually user ID)
        expires_delta: Token expiration time

    Returns:
        str: JWT refresh token
    """
    settings = get_settings()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            days=settings.security.jwt_refresh_token_expire_days,
        )

    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    return jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.jwt_algorithm,
    )


async def verify_token(token: str) -> str | None:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token to verify

    Returns:
        Optional[str]: Token subject (user ID) if valid, None otherwise
    """
    try:
        # Check if token is blacklisted (only if Redis is available)
        try:
            from backend.app.core.redis_client import is_token_blacklisted

            is_blacklisted = await is_token_blacklisted(token)
            if is_blacklisted:
                logger.warning("JWT token is blacklisted")
                return None
        except Exception as e:
            # If Redis is not available, skip blacklist check but continue with token verification
            logger.debug(f"Redis not available for token blacklist check: {e}")
            # Continue without blacklist check - this is normal during startup

        settings = get_settings()
        payload = jwt.decode(
            token,
            settings.security.secret_key,
            algorithms=[settings.security.jwt_algorithm],
        )
        subject: str = payload.get("sub")
        if subject is None:
            return None
        return subject
    except JWTError as e:
        logger.warning(f"JWT token verification failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        return None


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    Get current user ID from JWT token.

    Args:
        credentials: HTTP authorization credentials

    Returns:
        str: Current user ID

    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    user_id = await verify_token(token)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> "User":
    """
    Get current user from JWT token.

    Args:
        credentials: HTTP authorization credentials

    Returns:
        User: Current user object

    Raises:
        HTTPException: If token is invalid or user not found
    """
    from backend.app.core.database import get_db
    from backend.app.models.user import User

    user_id = await get_current_user_id(credentials)

    # Get database session
    db = next(get_db())
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    finally:
        db.close()


async def get_current_active_user(
    current_user: "User" = Depends(get_current_user),
) -> "User":
    """
    Get current active user.

    Args:
        current_user: Current user from token

    Returns:
        User: Active user object

    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return current_user


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> "User | None":
    """
    Get current user from JWT token, but return None if no valid token provided.
    This is useful for endpoints that can work with or without authentication.

    Args:
        credentials: HTTP authorization credentials

    Returns:
        User | None: Current user object or None if no valid token
    """
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


def require_permission(permission: str):
    """
    Decorator to require specific permission.

    Args:
        permission: Required permission

    Returns:
        Callable: Decorated function
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Get current user from kwargs or request context
            current_user = kwargs.get("current_user")
            if not current_user:
                # Try to get from request context
                request = kwargs.get("request")
                if request and hasattr(request.state, "user"):
                    current_user = request.state.user

            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )

            # Check if user has the required permission
            user_permissions = getattr(current_user, "permissions", [])
            if permission not in user_permissions:
                log_security_event(
                    event_type="PERMISSION_DENIED",
                    user_id=str(current_user.id),
                    description=f"Access denied to {permission}",
                    severity="warning",
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required: {permission}",
                )

            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_security_event(
    event_type: str,
    user_id: str | None = None,
    description: str = "",
    severity: str = "info",
    details: dict | None = None,
) -> None:
    """
    Log a security event to the audit log table.
    """
    from backend.app.core.database import get_db
    from backend.app.models.audit import AuditEventType, AuditLog, AuditSeverity

    db = next(get_db())
    try:
        log = AuditLog(
            event_type=AuditEventType(event_type),
            severity=AuditSeverity(severity),
            user_id=user_id,
            description=description,
            details=details or {},
        )
        db.add(log)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to log security event: {e}")
    finally:
        db.close()


# Example usage for audit logging:
# log_security_event(
#     event_type="USER_LOGIN",
#     user_id=user.id,
#     description="User logged in successfully",
#     severity="info"
# )
