"""
Search API endpoints for semantic search and RAG.

This module provides endpoints for:
- Semantic search in chat conversations
- Knowledge base search (RAG)
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.services.weaviate_service import weaviate_service

router = APIRouter()


class SemanticSearchRequest(BaseModel):
    query: str
    conversation_id: str | None = None
    limit: int = 5


class KnowledgeSearchRequest(BaseModel):
    query: str
    limit: int = 5


@router.post("/conversation", response_model=list[dict[str, Any]])
async def semantic_search_conversation(
    search: SemanticSearchRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Semantic search in chat conversation messages.
    """
    try:
        return weaviate_service.semantic_search_messages(
            query=search.query,
            conversation_id=search.conversation_id,
            limit=search.limit,
        )
    except Exception as e:
        logger.error(f"Semantic search error: {e}")
        raise HTTPException(status_code=500, detail="Semantic search failed")


@router.post("/knowledge", response_model=list[dict[str, Any]])
async def semantic_search_knowledge(
    search: KnowledgeSearchRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Semantic search in knowledge base (RAG).
    """
    try:
        return weaviate_service.semantic_search_knowledge(
            query=search.query,
            limit=search.limit,
        )
    except Exception as e:
        logger.error(f"Knowledge search error: {e}")
        raise HTTPException(status_code=500, detail="Knowledge search failed")
