"""
Configuration endpoints for frontend.

This module provides configuration endpoints that the frontend needs
to initialize properly.
"""

from fastapi import APIRouter
from app.core.config import get_settings

router = APIRouter()


@router.get("/")
async def get_config():
    """Get application configuration for frontend."""
    settings = get_settings()
    return {
        "apiUrl": "/api",
        "wsUrl": settings.ws_url,
        "isDevelopment": settings.debug,
        "isProduction": not settings.debug,
        "enableDebug": settings.debug,
        "wsEndpoints": {
            "chat": "/api/v1/ws/",
            "notifications": "/api/v1/ws/notifications"
        },
        "apiEndpoints": {
            "auth": "/api/v1/auth",
            "users": "/api/v1/users",
            "conversations": "/api/v1/conversations",
            "chat": "/api/v1/chat",
            "tools": "/api/v1/tools",
            "assistants": "/api/v1/assistants",
            "knowledge": "/api/v1/knowledge",
            "health": "/api/v1/health"
        }
    } 