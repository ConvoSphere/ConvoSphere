"""
Hybrid Mode Management API endpoints.

This module provides API endpoints for managing hybrid chat/agent mode
switching, configuration, and status queries.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from loguru import logger
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.schemas.hybrid_mode import (
    ConversationMode,
    HybridModeConfig,
    HybridModeState,
    ModeChangeRequest,
    ModeChangeResponse,
    ModeDecision,
)
from app.services.hybrid_mode_manager import hybrid_mode_manager
from sqlalchemy.orm import Session

router = APIRouter()


class ModeChangeRequestModel(BaseModel):
    """Request model for mode change."""

    target_mode: ConversationMode = Field(..., description="Target conversation mode")
    reason: Optional[str] = Field(None, description="User-provided reason for mode change")
    force_change: bool = Field(default=False, description="Force mode change ignoring recommendations")


class HybridModeConfigModel(BaseModel):
    """Configuration model for hybrid mode."""

    auto_mode_enabled: bool = Field(default=True, description="Enable automatic mode switching")
    complexity_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Complexity threshold for agent mode")
    confidence_threshold: float = Field(default=0.8, ge=0.0, le=1.0, description="Confidence threshold for mode decisions")
    context_window_size: int = Field(default=10, ge=1, le=100, description="Context window size for memory")
    memory_retention_hours: int = Field(default=24, ge=1, le=168, description="Memory retention in hours")
    reasoning_steps_max: int = Field(default=5, ge=1, le=20, description="Maximum reasoning steps")
    tool_relevance_threshold: float = Field(default=0.6, ge=0.0, le=1.0, description="Tool relevance threshold")


class ConversationModeStatus(BaseModel):
    """Status model for conversation mode."""

    conversation_id: str = Field(..., description="Conversation ID")
    current_mode: ConversationMode = Field(..., description="Current conversation mode")
    last_mode_change: str = Field(..., description="Last mode change timestamp")
    mode_history: List[Dict[str, Any]] = Field(default_factory=list, description="Mode change history")
    config: HybridModeConfigModel = Field(..., description="Current configuration")


class ModeDecisionRequest(BaseModel):
    """Request model for mode decision."""

    user_message: str = Field(..., description="User message to analyze")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Conversation context")
    force_mode: Optional[ConversationMode] = Field(None, description="Force specific mode")


@router.post("/conversations/{conversation_id}/initialize", response_model=HybridModeState)
async def initialize_hybrid_mode(
    conversation_id: str,
    initial_mode: ConversationMode = ConversationMode.AUTO,
    config: Optional[HybridModeConfigModel] = None,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Initialize hybrid mode for a conversation.
    
    Args:
        conversation_id: Conversation ID
        initial_mode: Initial conversation mode
        config: Hybrid mode configuration
        current_user_id: Current user ID
        db: Database session
        
    Returns:
        HybridModeState: Initialized hybrid mode state
    """
    try:
        # Convert config model to schema
        config_schema = None
        if config:
            config_schema = HybridModeConfig(**config.dict())

        state = hybrid_mode_manager.initialize_conversation(
            conversation_id=conversation_id,
            user_id=current_user_id,
            initial_mode=initial_mode,
            config=config_schema,
        )

        logger.info(f"Initialized hybrid mode for conversation {conversation_id}")
        return state

    except Exception as e:
        logger.error(f"Error initializing hybrid mode: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize hybrid mode: {str(e)}",
        )


@router.post("/conversations/{conversation_id}/mode/change", response_model=ModeChangeResponse)
async def change_conversation_mode(
    conversation_id: str,
    request: ModeChangeRequestModel,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Change the mode for a conversation.
    
    Args:
        conversation_id: Conversation ID
        request: Mode change request
        current_user_id: Current user ID
        db: Database session
        
    Returns:
        ModeChangeResponse: Mode change response
    """
    try:
        mode_change_request = ModeChangeRequest(
            conversation_id=conversation_id,
            user_id=current_user_id,
            target_mode=request.target_mode,
            reason=request.reason,
            force_change=request.force_change,
        )

        response = await hybrid_mode_manager.change_mode(mode_change_request)
        
        logger.info(f"Changed mode for conversation {conversation_id}: {response.previous_mode} -> {response.new_mode}")
        return response

    except Exception as e:
        logger.error(f"Error changing conversation mode: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to change conversation mode: {str(e)}",
        )


@router.get("/conversations/{conversation_id}/mode/status", response_model=ConversationModeStatus)
async def get_conversation_mode_status(
    conversation_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Get the current mode status for a conversation.
    
    Args:
        conversation_id: Conversation ID
        current_user_id: Current user ID
        db: Database session
        
    Returns:
        ConversationModeStatus: Current mode status
    """
    try:
        state = hybrid_mode_manager.get_state(conversation_id)
        if not state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Hybrid mode not initialized for conversation {conversation_id}",
            )

        return ConversationModeStatus(
            conversation_id=conversation_id,
            current_mode=state.current_mode,
            last_mode_change=state.last_mode_change.isoformat(),
            mode_history=state.mode_history,
            config=HybridModeConfigModel(**state.config.dict()),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation mode status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversation mode status: {str(e)}",
        )


@router.post("/conversations/{conversation_id}/mode/decide", response_model=ModeDecision)
async def decide_conversation_mode(
    conversation_id: str,
    request: ModeDecisionRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Get mode decision for a user message.
    
    Args:
        conversation_id: Conversation ID
        request: Mode decision request
        current_user_id: Current user ID
        db: Database session
        
    Returns:
        ModeDecision: Mode decision with reasoning
    """
    try:
        # Ensure hybrid mode is initialized
        state = hybrid_mode_manager.get_state(conversation_id)
        if not state:
            # Initialize with default config
            hybrid_mode_manager.initialize_conversation(
                conversation_id=conversation_id,
                user_id=current_user_id,
                initial_mode=ConversationMode.AUTO,
            )

        decision = await hybrid_mode_manager.decide_mode(
            conversation_id=conversation_id,
            user_message=request.user_message,
            context=request.context or {},
            force_mode=request.force_mode,
        )

        return decision

    except Exception as e:
        logger.error(f"Error deciding conversation mode: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to decide conversation mode: {str(e)}",
        )


@router.put("/conversations/{conversation_id}/config", response_model=HybridModeConfigModel)
async def update_conversation_config(
    conversation_id: str,
    config: HybridModeConfigModel,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Update hybrid mode configuration for a conversation.
    
    Args:
        conversation_id: Conversation ID
        config: New configuration
        current_user_id: Current user ID
        db: Database session
        
    Returns:
        HybridModeConfigModel: Updated configuration
    """
    try:
        state = hybrid_mode_manager.get_state(conversation_id)
        if not state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Hybrid mode not initialized for conversation {conversation_id}",
            )

        # Update configuration
        config_schema = HybridModeConfig(**config.dict())
        state.config = config_schema
        state.updated_at = datetime.now()

        logger.info(f"Updated hybrid mode config for conversation {conversation_id}")
        return config

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating conversation config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update conversation config: {str(e)}",
        )


@router.get("/conversations/{conversation_id}/mode/history")
async def get_mode_history(
    conversation_id: str,
    limit: int = Query(default=20, ge=1, le=100, description="Number of history entries to return"),
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Get mode change history for a conversation.
    
    Args:
        conversation_id: Conversation ID
        limit: Number of history entries to return
        current_user_id: Current user ID
        db: Database session
        
    Returns:
        List[Dict]: Mode change history
    """
    try:
        state = hybrid_mode_manager.get_state(conversation_id)
        if not state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Hybrid mode not initialized for conversation {conversation_id}",
            )

        # Return recent history entries
        history = state.mode_history[-limit:] if state.mode_history else []
        return {"history": history, "total_entries": len(state.mode_history)}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting mode history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get mode history: {str(e)}",
        )


@router.delete("/conversations/{conversation_id}/cleanup")
async def cleanup_conversation_mode(
    conversation_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Clean up hybrid mode state for a conversation.
    
    Args:
        conversation_id: Conversation ID
        current_user_id: Current user ID
        db: Database session
        
    Returns:
        Dict: Cleanup result
    """
    try:
        hybrid_mode_manager.cleanup_conversation(conversation_id)
        
        logger.info(f"Cleaned up hybrid mode for conversation {conversation_id}")
        return {"success": True, "message": f"Cleaned up hybrid mode for conversation {conversation_id}"}

    except Exception as e:
        logger.error(f"Error cleaning up conversation mode: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cleanup conversation mode: {str(e)}",
        )


@router.get("/stats")
async def get_hybrid_mode_stats(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Get hybrid mode statistics.
    
    Args:
        current_user_id: Current user ID
        db: Database session
        
    Returns:
        Dict: Hybrid mode statistics
    """
    try:
        stats = hybrid_mode_manager.get_stats()
        return stats

    except Exception as e:
        logger.error(f"Error getting hybrid mode stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get hybrid mode stats: {str(e)}",
        )


@router.get("/modes")
async def get_available_modes(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Get available conversation modes.
    
    Args:
        current_user_id: Current user ID
        db: Database session
        
    Returns:
        Dict: Available modes with descriptions
    """
    try:
        modes = [
            {
                "mode": ConversationMode.CHAT,
                "name": "Chat Mode",
                "description": "Direct conversational responses without tool usage",
                "features": ["Simple responses", "No tool usage", "Fast processing"],
            },
            {
                "mode": ConversationMode.AGENT,
                "name": "Agent Mode",
                "description": "Tool-enabled responses with reasoning and actions",
                "features": ["Tool usage", "Step-by-step reasoning", "External actions"],
            },
            {
                "mode": ConversationMode.AUTO,
                "name": "Auto Mode",
                "description": "Automatic mode switching based on query analysis",
                "features": ["Smart switching", "Complexity analysis", "Context awareness"],
            },
        ]
        
        return {"modes": modes}

    except Exception as e:
        logger.error(f"Error getting available modes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get available modes: {str(e)}",
        ) 