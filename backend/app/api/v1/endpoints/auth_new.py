"""
Authentication endpoints - New modular implementation.

This module provides a unified interface to all authentication endpoints
using the new modular architecture.
"""

from fastapi import APIRouter

from backend.app.api.v1.endpoints.auth.authentication import router as auth_router
from backend.app.api.v1.endpoints.auth.password import router as password_router
from backend.app.api.v1.endpoints.auth.registration import router as registration_router
from backend.app.api.v1.endpoints.auth.sso.account_management import (
    router as sso_account_router,
)
from backend.app.api.v1.endpoints.auth.sso.authentication import (
    router as sso_auth_router,
)
from backend.app.api.v1.endpoints.auth.sso.providers import (
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
