"""
Knowledge base statistics API endpoint.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.models.user import User
from backend.app.schemas.knowledge import KnowledgeBaseStats
from backend.app.services.knowledge_service import KnowledgeService

router = APIRouter()


# Get knowledge base stats
@router.get("/stats", response_model=KnowledgeBaseStats)
async def get_knowledge_base_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get knowledge base statistics for the current user."""
    service = KnowledgeService(db)
    return await service.get_knowledge_base_stats(current_user)
