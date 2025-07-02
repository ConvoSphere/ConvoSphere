"""Users endpoints for user management."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_users():
    """Get all users (admin only)."""
    return {"message": "Users endpoint - to be implemented"} 