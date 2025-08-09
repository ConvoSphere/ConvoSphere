"""
SSO Account Management endpoints.

This module provides SSO account linking, unlinking, and provisioning functionality.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from loguru import logger
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.dependencies import require_admin_role
from backend.app.models.user import User

router = APIRouter()


@router.post("/link/{provider}")
async def sso_link(
    provider: str,
    request: Request,
    current_user_id: str = Depends(require_admin_role),
    db: Session = Depends(get_db),
):
    """Link SSO account to existing user."""
    try:
        from backend.app.services.advanced_user_provisioning import (
            advanced_user_provisioning,
        )

        # Get user from database
        user = db.query(User).filter(User.id == current_user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        # Link SSO account
        result = await advanced_user_provisioning.link_sso_account(
            user_id=current_user_id,
            provider=provider,
            request=request,
            db=db,
        )

        logger.info(
            f"SSO account linked for user {current_user_id} with provider {provider}"
        )
        return result

    except Exception as e:
        logger.error(f"Failed to link SSO account for provider {provider}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to link SSO account",
        )


@router.get("/unlink/{provider}")
async def sso_unlink(
    provider: str,
    request: Request,
    current_user_id: str = Depends(require_admin_role),
    db: Session = Depends(get_db),
):
    """Unlink SSO account from user."""
    try:
        from backend.app.services.advanced_user_provisioning import (
            advanced_user_provisioning,
        )

        # Get user from database
        user = db.query(User).filter(User.id == current_user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        # Unlink SSO account
        result = await advanced_user_provisioning.unlink_sso_account(
            user_id=current_user_id,
            provider=provider,
            request=request,
            db=db,
        )

        logger.info(
            f"SSO account unlinked for user {current_user_id} with provider {provider}"
        )
        return result

    except Exception as e:
        logger.error(f"Failed to unlink SSO account for provider {provider}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unlink SSO account",
        )


@router.get("/provisioning/status/{user_id}")
async def get_user_provisioning_status(
    user_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Get user provisioning status for SSO providers."""
    try:
        from backend.app.services.advanced_user_provisioning import (
            advanced_user_provisioning,
        )

        # Get user from database
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        # Get provisioning status
        status_info = await advanced_user_provisioning.get_user_provisioning_status(
            user_id=user_id,
            request=request,
            db=db,
        )

        return status_info

    except Exception as e:
        logger.error(f"Failed to get provisioning status for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get provisioning status",
        )


@router.post("/bulk-sync/{provider}")
async def bulk_sync_users(
    provider: str,
    user_list: list[dict[str, Any]],
    request: Request,
    current_user: User = Depends(require_admin_role),
    db: Session = Depends(get_db),
):
    """Bulk sync users from SSO provider."""
    try:
        from backend.app.services.advanced_user_provisioning import (
            advanced_user_provisioning,
        )

        # Validate user list
        if not user_list:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User list cannot be empty",
            )

        # Perform bulk sync
        result = await advanced_user_provisioning.bulk_sync_users(
            provider=provider,
            user_list=user_list,
            request=request,
            db=db,
        )

        logger.info(
            f"Bulk sync completed for provider {provider} with {len(user_list)} users"
        )
        return result

    except Exception as e:
        logger.error(f"Failed to bulk sync users for provider {provider}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to bulk sync users",
        )
