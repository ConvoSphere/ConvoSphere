"""
Search-related API endpoints (search, advanced search, search history).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.knowledge import SearchRequest, SearchResponse, AdvancedSearchRequest, AdvancedSearchResponse
from app.services.knowledge_service import KnowledgeService
from fastapi import Query

router = APIRouter()

# Search documents
@router.post("/search", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ... existing code ...

# Advanced search
@router.post("/search/advanced", response_model=AdvancedSearchResponse)
async def advanced_search(
    request: AdvancedSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ... existing code ...

# Search history
@router.get("/search/history")
async def get_search_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ... existing code ...