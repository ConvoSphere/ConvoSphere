"""
Health check endpoints.

This module provides health check and status endpoints for monitoring
the AI Assistant Platform.
"""

from fastapi import APIRouter, Depends
from loguru import logger

from app.core.config import settings
from app.core.database import check_db_connection, get_db_info
from app.core.redis_client import check_redis_connection, get_redis_info
from app.core.weaviate_client import check_weaviate_connection, get_weaviate_info

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
    try:
        # Check all components
        db_healthy = check_db_connection()
        redis_healthy = await check_redis_connection()
        weaviate_healthy = check_weaviate_connection()
        
        # Get detailed component information
        db_info = get_db_info()
        redis_info = await get_redis_info()
        weaviate_info = get_weaviate_info()
        
        # Determine overall status
        all_healthy = db_healthy and redis_healthy and weaviate_healthy
        overall_status = "healthy" if all_healthy else "degraded"
        
        health_status = {
            "status": overall_status,
            "service": "ai-assistant-platform",
            "version": settings.app_version,
            "environment": settings.environment,
            "components": {
                "database": {
                    "status": "healthy" if db_healthy else "unhealthy",
                    "details": db_info
                },
                "cache": {
                    "status": "healthy" if redis_healthy else "unhealthy",
                    "details": redis_info
                },
                "vector_db": {
                    "status": "healthy" if weaviate_healthy else "unhealthy",
                    "details": weaviate_info
                }
            },
            "timestamp": "2024-01-01T00:00:00Z"  # TODO: Use actual timestamp
        }
        
        logger.info(f"Health check completed - Status: {overall_status}")
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "ai-assistant-platform",
            "version": settings.app_version,
            "environment": settings.environment,
            "error": str(e)
        }


@router.get("/database")
async def database_health():
    """Database-specific health check."""
    try:
        healthy = check_db_connection()
        info = get_db_info()
        
        return {
            "status": "healthy" if healthy else "unhealthy",
            "component": "database",
            "details": info
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "component": "database",
            "error": str(e)
        }


@router.get("/redis")
async def redis_health():
    """Redis-specific health check."""
    try:
        healthy = await check_redis_connection()
        info = await get_redis_info()
        
        return {
            "status": "healthy" if healthy else "unhealthy",
            "component": "cache",
            "details": info
        }
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return {
            "status": "unhealthy",
            "component": "cache",
            "error": str(e)
        }


@router.get("/weaviate")
async def weaviate_health():
    """Weaviate-specific health check."""
    try:
        healthy = check_weaviate_connection()
        info = get_weaviate_info()
        
        return {
            "status": "healthy" if healthy else "unhealthy",
            "component": "vector_db",
            "details": info
        }
    except Exception as e:
        logger.error(f"Weaviate health check failed: {e}")
        return {
            "status": "unhealthy",
            "component": "vector_db",
            "error": str(e)
        } 