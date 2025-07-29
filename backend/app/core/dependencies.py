"""
Dependencies for FastAPI endpoints.

This module provides common dependencies for authentication, authorization,
and other shared functionality across the API endpoints.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from loguru import logger
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user_id
from backend.app.models.user import User, UserRole


def get_current_user(
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Get current authenticated user."""
    user = db.query(User).filter(User.id == current_user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


def require_admin_role(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Require admin role for endpoint access."""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        logger.warning(
            f"Admin access denied for user {current_user.id} with role {current_user.role}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


def require_super_admin_role(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Require super admin role for endpoint access."""
    if current_user.role != UserRole.SUPER_ADMIN:
        logger.warning(
            f"Super admin access denied for user {current_user.id} with role {current_user.role}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required",
        )
    return current_user


def require_manager_role(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Require manager or higher role for endpoint access."""
    if current_user.role not in [
        UserRole.MANAGER,
        UserRole.ADMIN,
        UserRole.SUPER_ADMIN,
    ]:
        logger.warning(
            f"Manager access denied for user {current_user.id} with role {current_user.role}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager access required",
        )
    return current_user


def can_manage_user(
    current_user: Annotated[User, Depends(get_current_user)],
    target_user_id: str,
    db: Annotated[Session, Depends(get_db)],
) -> tuple[User, User]:
    """Check if current user can manage target user."""
    target_user = db.query(User).filter(User.id == target_user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target user not found",
        )

    # Super admins can manage anyone
    if current_user.role == UserRole.SUPER_ADMIN:
        return current_user, target_user

    # Admins can manage users except super admins
    if current_user.role == UserRole.ADMIN:
        if target_user.role == UserRole.SUPER_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot manage super admin users",
            )
        return current_user, target_user

    # Managers can manage regular users and guests
    if current_user.role == UserRole.MANAGER:
        if target_user.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MANAGER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot manage admin or manager users",
            )
        return current_user, target_user

    # Regular users can only manage themselves
    if current_user.id != target_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only manage own account",
        )

    return current_user, target_user


def require_permission(permission: str):
    """Decorator to require specific permission."""

    def permission_checker(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if not current_user.has_permission(permission):
            logger.warning(
                f"Permission '{permission}' denied for user {current_user.id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required",
            )
        return current_user

    return permission_checker
