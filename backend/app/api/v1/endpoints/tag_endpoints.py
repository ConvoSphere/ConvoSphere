"""
Tag-related API endpoints (get tags, search tags).
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.knowledge import TagList, TagResponse
from app.services.knowledge_service import KnowledgeService

router = APIRouter()

# Get tags
@router.get("/tags", response_model=TagList)
async def get_tags(
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ... existing code ...

# Search tags
@router.get("/tags/search", response_model=TagList)
async def search_tags(
    query: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ... existing code ...