"""
Main API router for v1 endpoints.

This module combines all API routers into a single router for the v1 API.
"""

from fastapi import APIRouter

from .endpoints import (
    ai,
    assistants,
    auth,
    chat,
    config,
    conversation_intelligence,
    conversations,
    health,
    knowledge,
    mcp,
    rag,
    search,
    tools,
    users,
    websocket,
)

# Create main API router
api_router = APIRouter()  # Temporarily disabled rate_limiter dependency

# Include all endpoint routers
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(assistants.router, prefix="/assistants", tags=["assistants"])
api_router.include_router(
    conversations.router,
    prefix="/conversations",
    tags=["conversations"],
)
api_router.include_router(tools.router, prefix="/tools", tags=["tools"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(mcp.router, prefix="/mcp", tags=["mcp"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])
api_router.include_router(rag.router, prefix="/rag", tags=["rag"])
api_router.include_router(
    conversation_intelligence.router,
    prefix="/intelligence",
    tags=["conversation_intelligence"],
)
api_router.include_router(websocket.router, prefix="/ws", tags=["websocket"])
api_router.include_router(config.router, prefix="/config", tags=["config"])
