"""
Main API router for v1 endpoints.

This module combines all API routers into a single router for the v1 API.
"""

from fastapi import APIRouter

from .endpoints import auth, users, assistants, conversations, tools, health, chat

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(assistants.router, prefix="/assistants", tags=["assistants"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
api_router.include_router(tools.router, prefix="/tools", tags=["tools"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(health.router, prefix="/health", tags=["health"]) 