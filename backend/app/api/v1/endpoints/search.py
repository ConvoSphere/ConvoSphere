"""
Search API endpoints for semantic search and RAG.

This module provides endpoints for:
- Semantic search in chat conversations
- Knowledge base search (RAG)
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from loguru import logger

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.services.weaviate_service import weaviate_service

router = APIRouter()


class SemanticSearchRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None
    limit: int = 5

class KnowledgeSearchRequest(BaseModel):
    query: str
    limit: int = 5


@router.post("/conversation", response_model=List[Dict[str, Any]])
async def semantic_search_conversation(
    search: SemanticSearchRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Semantic search in chat conversation messages.
    """
    try:
        results = weaviate_service.semantic_search_messages(
            query=search.query,
            conversation_id=search.conversation_id,
            limit=search.limit
        )
        return results
    except Exception as e:
        logger.error(f"Semantic search error: {e}")
        raise HTTPException(status_code=500, detail="Semantic search failed")


@router.post("/knowledge", response_model=List[Dict[str, Any]])
async def semantic_search_knowledge(
    search: KnowledgeSearchRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Semantic search in knowledge base (RAG).
    """
    try:
        results = weaviate_service.semantic_search_knowledge(
            query=search.query,
            limit=search.limit
        )
        return results
    except Exception as e:
        logger.error(f"Knowledge search error: {e}")
        raise HTTPException(status_code=500, detail="Knowledge search failed") 