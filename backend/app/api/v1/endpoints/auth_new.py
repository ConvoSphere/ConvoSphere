"""
Authentication endpoints - New modular implementation.

This module provides a unified interface to all authentication endpoints
using the new modular architecture.
"""

from fastapi import APIRouter

from backend.app.api.v1.endpoints.auth.authentication import router as auth_router
from backend.app.api.v1.endpoints.auth.registration import router as registration_router

router = APIRouter()

# Include all authentication sub-routers
router.include_router(auth_router, tags=["authentication"])
router.include_router(registration_router, tags=["registration"])

# TODO: Add SSO and password reset routers when implemented
# router.include_router(sso_router, prefix="/sso", tags=["sso"])
# router.include_router(password_router, tags=["password"])