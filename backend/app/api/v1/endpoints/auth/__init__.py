"""Auth endpoints package.

Exports a unified `router` that aggregates all auth-related subrouters.
"""

from fastapi import APIRouter

from .authentication import router as auth_router
from .registration import router as registration_router
from .sso.account_management import router as sso_account_router
from .sso.authentication import router as sso_auth_router
from .sso.providers import router as sso_providers_router

router = APIRouter()
router.include_router(auth_router, tags=["authentication"])
router.include_router(registration_router, tags=["registration"])
router.include_router(sso_providers_router, prefix="/sso", tags=["sso"])
router.include_router(sso_auth_router, prefix="/sso", tags=["sso"])
router.include_router(sso_account_router, prefix="/sso", tags=["sso"])
