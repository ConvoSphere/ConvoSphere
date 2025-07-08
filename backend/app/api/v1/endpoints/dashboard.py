"""
Dashboard endpoints for user statistics and overview data.

This module provides endpoints for dashboard statistics and user overview data.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.conversation import Conversation, Message
from app.models.assistant import Assistant

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get dashboard statistics for the current user.
    
    Returns:
        Dict containing various statistics
    """
    try:
        # Get user's conversations
        user_conversations = db.query(Conversation).filter(
            Conversation.user_id == str(current_user.id)
        ).all()
        
        # Get total messages for user's conversations
        conversation_ids = [str(conv.id) for conv in user_conversations]
        total_messages = 0
        if conversation_ids:
            total_messages = db.query(func.count(Message.id)).filter(
                Message.conversation_id.in_(conversation_ids)
            ).scalar()
        
        # Get active assistants (for now, return a placeholder)
        active_assistants = db.query(func.count(Assistant.id)).filter(
            Assistant.is_active == True
        ).scalar()
        
        # Get recent activity (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_conversations = db.query(Conversation).filter(
            Conversation.user_id == str(current_user.id),
            Conversation.created_at >= week_ago
        ).order_by(Conversation.created_at.desc()).limit(5).all()
        
        recent_activity = []
        for conv in recent_conversations:
            recent_activity.append({
                "id": str(conv.id),
                "type": "conversation",
                "description": f"Started conversation: {conv.title}",
                "created_at": conv.created_at.isoformat()
            })
        
        return {
            "total_conversations": len(user_conversations),
            "total_messages": total_messages,
            "active_assistants": active_assistants,
            "recent_activity": recent_activity
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch dashboard stats: {str(e)}"
        )


@router.get("/overview")
async def get_dashboard_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get dashboard overview data.
    
    Returns:
        Dict containing overview information
    """
    try:
        # Get user's recent conversations
        recent_conversations = db.query(Conversation).filter(
            Conversation.user_id == str(current_user.id)
        ).order_by(Conversation.updated_at.desc()).limit(10).all()
        
        # Get system status
        system_status = {
            "status": "online",
            "last_check": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }
        
        return {
            "recent_conversations": [
                {
                    "id": str(conv.id),
                    "title": conv.title,
                    "created_at": conv.created_at.isoformat(),
                    "updated_at": conv.updated_at.isoformat(),
                    "message_count": conv.message_count if hasattr(conv, 'message_count') else 0
                }
                for conv in recent_conversations
            ],
            "system_status": system_status
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch dashboard overview: {str(e)}"
        ) 