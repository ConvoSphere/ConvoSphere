"""
API v1 router configuration.

This module configures the main API v1 router and includes all endpoint routers.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    ai,
    assistants_management,
    audit,
    auth,
    chat,
    conversations,
    domain_groups,
    health,
    hybrid_mode,
    intelligence,
    knowledge,
    mcp,
    rag,
    search,
    tools,
    users,
    websocket,
)

# Main API v1 router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["User Management"])
api_router.include_router(assistants_management.router, prefix="/assistants", tags=["Assistant Management"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["Conversations"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["Knowledge Base"])
api_router.include_router(tools.router, prefix="/tools", tags=["Tools"])
api_router.include_router(mcp.router, prefix="/mcp", tags=["MCP Tools"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI"])
api_router.include_router(rag.router, prefix="/rag", tags=["RAG"])
api_router.include_router(search.router, prefix="/search", tags=["Search"])
api_router.include_router(intelligence.router, prefix="/intelligence", tags=["Conversation Intelligence"])
api_router.include_router(domain_groups.router, prefix="/domain-groups", tags=["Domain Groups"])
api_router.include_router(audit.router, prefix="/audit", tags=["Audit"])
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(hybrid_mode.router, prefix="/hybrid-mode", tags=["Hybrid Mode"])
