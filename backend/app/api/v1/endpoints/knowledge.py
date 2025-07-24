"""
Knowledge base API endpoints (aggregiert).

Importiert und registriert alle Teilrouter für Dokumente, Suche, Tags, Verarbeitung und Statistiken.
"""
from fastapi import APIRouter
from .document_endpoints import router as document_router
from .search_endpoints import router as search_router
from .tag_endpoints import router as tag_router
from .processing_endpoints import router as processing_router
from .stats_endpoints import router as stats_router

router = APIRouter()
router.include_router(document_router)
router.include_router(search_router)
router.include_router(tag_router)
router.include_router(processing_router)
router.include_router(stats_router)
