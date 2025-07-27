"""
AI service endpoints.

This module provides endpoints for AI model management and configuration.
"""

from backend.app.core.security import get_current_user_id
from backend.app.services.ai_service import ai_service
from fastapi import APIRouter, Depends

router = APIRouter()


@router.get("/models")
async def get_available_models():
    """Get available AI models."""
    try:
        models = ai_service.get_available_models()
        return {"models": models}
    except Exception as e:
        return {"error": str(e), "models": {}}


@router.get("/providers")
async def get_available_providers():
    """Get available AI providers."""
    try:
        providers = ai_service.get_available_providers()
        return {"providers": providers}
    except Exception as e:
        return {"error": str(e), "providers": {}}


@router.get("/health")
async def ai_health_check():
    """Check AI service health."""
    try:
        return ai_service.health_check()
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


@router.get("/costs")
async def get_cost_summary(current_user_id: str = Depends(get_current_user_id)):
    """Get cost summary for AI usage."""
    try:
        return ai_service.get_cost_summary()
    except Exception as e:
        return {"error": str(e), "costs": {}}
