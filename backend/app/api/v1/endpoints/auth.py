"""
Authentication endpoints - Facade for modular auth architecture.

This module provides backward compatibility for the original auth.py
by delegating to the new modular authentication implementation.
"""

from fastapi import APIRouter

# Import the new modular auth router
from backend.app.api.v1.endpoints.auth_new import router as auth_new_router

router = APIRouter()

# Include all routes from the new modular implementation
router.include_router(auth_new_router)

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
