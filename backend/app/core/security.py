"""
Security utilities for authentication and authorization.

This module provides JWT token management, password hashing,
and security utilities for the AI Assistant Platform.
"""

from datetime import datetime, timedelta
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from loguru import logger
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.jwt_access_token_expire_minutes,
        )

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.jwt_algorithm,
    )
    return encoded_jwt


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
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=settings.jwt_refresh_token_expire_days,
        )

    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.jwt_algorithm,
    )
    return encoded_jwt


async def verify_token(token: str) -> str | None:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token to verify

    Returns:
        Optional[str]: Token subject (user ID) if valid, None otherwise
    """
    try:
        # Check if token is blacklisted
        from app.utils.redis import get_redis

        redis = await get_redis()
        is_blacklisted = await redis.get(f"{BLACKLIST_PREFIX}{token}")
        if is_blacklisted:
            logger.warning("JWT token is blacklisted")
            return None

        settings = get_settings()
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
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
    from app.core.database import get_db
    from app.models.user import User

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
    from app.core.database import get_db
    from app.models.audit import AuditEventType, AuditLog, AuditSeverity

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
