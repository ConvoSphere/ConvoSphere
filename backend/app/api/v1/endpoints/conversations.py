"""Conversations endpoints for conversation management."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_conversations():
    """Get all conversations."""
    return {"message": "Conversations endpoint - to be implemented"} 