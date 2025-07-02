"""Tools endpoints for tool management."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_tools():
    """Get all tools."""
    return {"message": "Tools endpoint - to be implemented"} 