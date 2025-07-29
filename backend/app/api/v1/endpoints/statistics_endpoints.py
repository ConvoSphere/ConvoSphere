from __future__ import annotations

"""Statistics API endpoints.

Provides aggregated overview statistics, system health, recent activity and user stats required by the React dashboard.
"""

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from loguru import logger

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.models.assistant import Assistant
from backend.app.models.conversation import Conversation, Message
from backend.app.models.knowledge import Document
from backend.app.models.tool import Tool

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from backend.app.models.user import User

router = APIRouter()


# Helpers ---------------------------------------------------------------------


def _safe_count(db: Session, model) -> int:
    """Return count for model, swallowing errors."""
    try:
        return db.query(model).count()
    except Exception as exc:  # pragma: no cover – defensive
        logger.warning(f"Count failed for {model}: {exc}")
        return 0


# Endpoints -------------------------------------------------------------------


@router.get("/overview", response_model=dict[str, Any])
async def get_overview_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return system-wide overview stats plus recent activity stubs."""
    try:
        system_stats = {
            "totalConversations": _safe_count(db, Conversation),
            "totalMessages": _safe_count(db, Message),
            "totalDocuments": _safe_count(db, Document),
            "totalAssistants": _safe_count(db, Assistant),
            "totalTools": _safe_count(db, Tool),
            # naive active users: users with conversation in last 24h
            "activeUsers": db.query(Conversation.user_id)
            .filter(Conversation.created_at >= datetime.utcnow() - timedelta(days=1))
            .distinct()
            .count(),
            # Basic health & performance placeholders
            "systemHealth": "healthy",
            "performance": {
                "cpuUsage": 0,
                "memoryUsage": 0,
                "responseTime": 0,
                "uptime": 0,
            },
        }

        recent_activity: list[dict[str, Any]] = (
            db.query(Message).order_by(Message.created_at.desc()).limit(10).all()
        )
        recent_activity_data = [
            {
                "id": str(msg.id),
                "type": "message",
                "title": msg.content[:50],
                "timestamp": msg.created_at.isoformat() if msg.created_at else "",
                "user": str(msg.user_id) if getattr(msg, "user_id", None) else "",
            }
            for msg in recent_activity
        ]

        user_stats = {
            "conversationsThisWeek": db.query(Conversation)
            .filter(
                Conversation.user_id == current_user.id,
                Conversation.created_at >= datetime.utcnow() - timedelta(days=7),
            )
            .count(),
            "messagesThisWeek": db.query(Message)
            .join(Conversation, Message.conversation_id == Conversation.id)
            .filter(
                Conversation.user_id == current_user.id,
                Message.created_at >= datetime.utcnow() - timedelta(days=7),
            )
            .count(),
            "documentsUploaded": 0,
            "favoriteAssistant": "",
        }

        return {
            "systemStats": system_stats,
            "recentActivity": recent_activity_data,
            "userStats": user_stats,
        }
    except Exception as exc:  # pragma: no cover – log and propagate
        logger.exception("Error computing overview statistics: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to compute statistics")


@router.get("/system-health", response_model=dict[str, Any])
async def get_system_health():
    """Placeholder system health endpoint."""
    return {
        "status": "healthy",
        "performance": {
            "cpuUsage": 0,
            "memoryUsage": 0,
            "responseTime": 0,
            "uptime": 0,
        },
    }


@router.get("/recent-activity", response_model=list[dict[str, Any]])
async def get_recent_activity(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return recent activity items."""
    msgs = db.query(Message).order_by(Message.created_at.desc()).limit(limit).all()
    return [
        {
            "id": str(msg.id),
            "type": "message",
            "title": msg.content[:50],
            "timestamp": msg.created_at.isoformat() if msg.created_at else "",
            "user": str(msg.user_id) if getattr(msg, "user_id", None) else "",
        }
        for msg in msgs
    ]


@router.get("/user", response_model=dict[str, Any])
async def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return statistics specific to the current user."""
    return {
        "conversations": db.query(Conversation)
        .filter(Conversation.user_id == current_user.id)
        .count(),
        "messages": db.query(Message)
        .join(Conversation, Message.conversation_id == Conversation.id)
        .filter(Conversation.user_id == current_user.id)
        .count(),
        "documents": 0,
    }
