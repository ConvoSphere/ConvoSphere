"""
AI service endpoints.

This module provides endpoints for AI model management and configuration.
"""

from fastapi import APIRouter, Depends
from app.services.ai_service import ai_service
from app.core.security import get_current_user_id

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
        health = ai_service.health_check()
        return health
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


@router.get("/costs")
async def get_cost_summary(current_user_id: str = Depends(get_current_user_id)):
    """Get cost summary for AI usage."""
    try:
        costs = ai_service.get_cost_summary()
        return costs
    except Exception as e:
        return {"error": str(e), "costs": {}} 