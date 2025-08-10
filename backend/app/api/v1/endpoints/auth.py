"""
Authentication endpoints - Facade for modular auth architecture.

This module provides backward compatibility for the original auth.py
by delegating to the new modular authentication implementation.
"""

from fastapi import APIRouter

# Import directly from the auth subdirectory
from .auth.authentication import router as auth_router
from .auth.password import router as password_router
from .auth.registration import router as registration_router
from .auth.sso.account_management import (
    router as sso_account_router,
)
from .auth.sso.authentication import (
    router as sso_auth_router,
)
from .auth.sso.providers import (
    router as sso_providers_router,
)

router = APIRouter()

# Include all authentication sub-routers
router.include_router(auth_router, tags=["authentication"])
router.include_router(registration_router, tags=["registration"])
router.include_router(password_router, tags=["password"])

# Include SSO routers
router.include_router(sso_providers_router, prefix="/sso", tags=["sso"])
router.include_router(sso_auth_router, prefix="/sso", tags=["sso"])
router.include_router(sso_account_router, prefix="/sso", tags=["sso"])

# Re-export all routes for backward compatibility
__all__ = ["router"]

# Legacy imports for backward compatibility
# These are now handled by the new modular implementation

# Re-export models for backward compatibility
__all__.extend(
    [
        "UserLogin",
        "UserRegister",
        "RefreshTokenRequest",
        "TokenResponse",
        "UserResponse",
        "PasswordResetRequest",
        "PasswordResetConfirm",
    ]
)
