"""
Search-related API endpoints (search, advanced search, search history).
"""

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.knowledge import (
    AdvancedSearchRequest,
    AdvancedSearchResponse,
    SearchRequest,
    SearchResponse,
)
from app.services.knowledge_service import KnowledgeService
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

router = APIRouter()


# Search documents
@router.post("/search", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Search documents."""
    service = KnowledgeService(db)
    return await service.search_documents(request, current_user)


# Advanced search
@router.post("/search/advanced", response_model=AdvancedSearchResponse)
async def advanced_search(
    request: AdvancedSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Advanced search with filters."""
    service = KnowledgeService(db)
    return await service.advanced_search(request, current_user)


# Search history
@router.get("/search/history")
async def get_search_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get search history for the current user."""
    service = KnowledgeService(db)
    return await service.get_search_history(current_user, skip, limit)
