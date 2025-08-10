"""
Knowledge base API endpoints (aggregiert).

Importiert und registriert alle Teilrouter für Dokumente, Suche, Tags, Verarbeitung und Statistiken.
"""

from fastapi import APIRouter

from .document_endpoints import router as document_router
from .processing_endpoints import router as processing_router
from .search import router as search_router
from .tag_endpoints import router as tag_router

router = APIRouter()
router.include_router(document_router)
router.include_router(search_router)
router.include_router(tag_router)
router.include_router(processing_router)
