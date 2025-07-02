"""
Health check endpoints.

This module provides health check and status endpoints for monitoring
the AI Assistant Platform.
"""

from fastapi import APIRouter, Depends
from loguru import logger

from app.core.config import settings

router = APIRouter()


@router.get("/")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "ai-assistant-platform",
        "version": settings.app_version,
        "environment": settings.environment
    }


@router.get("/detailed")
async def detailed_health_check():
    """Detailed health check with component status."""
    # TODO: Add actual health checks for database, Redis, Weaviate
    health_status = {
        "status": "healthy",
        "service": "ai-assistant-platform",
        "version": settings.app_version,
        "environment": settings.environment,
        "components": {
            "database": "healthy",  # TODO: Check PostgreSQL
            "cache": "healthy",     # TODO: Check Redis
            "vector_db": "healthy", # TODO: Check Weaviate
            "ai_providers": "healthy"  # TODO: Check AI providers
        }
    }
    
    logger.info("Health check requested")
    return health_status 