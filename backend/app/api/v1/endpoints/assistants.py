"""Assistants endpoints for assistant management."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_assistants():
    """Get all assistants."""
    return {"message": "Assistants endpoint - to be implemented"} 