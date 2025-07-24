"""
Assistants API endpoints (aggregiert).

Importiert und registriert alle Teilrouter für Management und Tools.
"""
from fastapi import APIRouter
from .assistants_management import router as management_router
from .assistants_tools import router as tools_router

router = APIRouter()
router.include_router(management_router)
router.include_router(tools_router)
