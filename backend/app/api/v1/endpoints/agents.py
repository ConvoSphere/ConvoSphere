"""
Agent management API endpoints.

This module provides API endpoints for managing AI agents, including
agent creation, handoffs, collaboration, and performance monitoring.
"""

from typing import Any, List

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user_id
from backend.app.schemas.agent import (
    AgentCreate,
    AgentUpdate,
    AgentResponse,
    AgentHandoffRequest,
    AgentCollaborationRequest,
    AgentPerformanceMetrics,
)
from backend.app.services.agent_service import AgentService
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from loguru import logger
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

router = APIRouter()


class AgentHandoffRequestModel(BaseModel):
    """Request model for agent handoff."""

    from_agent_id: str = Field(..., description="Current agent ID")
    to_agent_id: str = Field(..., description="Target agent ID")
    reason: str = Field(..., min_length=1, max_length=500, description="Handoff reason")
    context: dict[str, Any] = Field(default_factory=dict, description="Handoff context")
    priority: int = Field(default=1, ge=1, le=10, description="Handoff priority")


class AgentCollaborationRequestModel(BaseModel):
    """Request model for agent collaboration."""

    agent_ids: list[str] = Field(
        ...,
        min_length=2,
        max_length=5,
        description="Agent IDs to collaborate",
    )
    collaboration_type: str = Field(
        default="parallel",
        pattern="^(parallel|sequential|hierarchical)$",
        description="Collaboration type",
    )
    coordination_strategy: str = Field(
        default="round_robin",
        pattern="^(round_robin|priority|expertise)$",
        description="Coordination strategy",
    )
    shared_context: dict[str, Any] = Field(
        default_factory=dict,
        description="Shared context",
    )


# Get all available agents
@router.get("/", response_model=List[dict[str, Any]])
async def get_available_agents(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Get all available agents from the registry."""
    try:
        service = AgentService(db)
        return await service.get_available_agents()
    except Exception as e:
        logger.error(f"Error getting available agents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get available agents: {str(e)}",
        )


# Create new agent
@router.post("/", response_model=AgentResponse)
async def create_agent(
    agent_data: AgentCreate,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Create a new agent."""
    try:
        service = AgentService(db)
        return await service.create_agent(agent_data)
    except Exception as e:
        logger.error(f"Error creating agent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create agent: {str(e)}",
        )


# Update agent
@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    agent_data: AgentUpdate,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Update an existing agent."""
    try:
        service = AgentService(db)
        result = await service.update_agent(agent_id, agent_data)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_id} not found",
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating agent {agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update agent: {str(e)}",
        )


# Delete agent
@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Delete an agent."""
    try:
        service = AgentService(db)
        success = await service.delete_agent(agent_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_id} not found",
            )
        return {"message": f"Agent {agent_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting agent {agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete agent: {str(e)}",
        )


# Agent handoff
@router.post("/handoff")
async def handoff_agent(
    request: AgentHandoffRequestModel,
    conversation_id: str = Query(..., description="Conversation ID"),
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Perform agent handoff."""
    try:
        service = AgentService(db)
        handoff_request = AgentHandoffRequest(
            from_agent_id=request.from_agent_id,
            to_agent_id=request.to_agent_id,
            conversation_id=conversation_id,
            user_id=current_user_id,
            reason=request.reason,
            context=request.context,
            priority=request.priority,
        )
        return await service.handoff_agent(handoff_request)
    except Exception as e:
        logger.error(f"Error during agent handoff: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform agent handoff: {str(e)}",
        )


# Start agent collaboration
@router.post("/collaborate")
async def start_collaboration(
    request: AgentCollaborationRequestModel,
    conversation_id: str = Query(..., description="Conversation ID"),
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Start agent collaboration."""
    try:
        service = AgentService(db)
        collaboration_request = AgentCollaborationRequest(
            agent_ids=request.agent_ids,
            conversation_id=conversation_id,
            user_id=current_user_id,
            collaboration_type=request.collaboration_type,
            coordination_strategy=request.coordination_strategy,
            shared_context=request.shared_context,
        )
        return await service.start_collaboration(collaboration_request)
    except Exception as e:
        logger.error(f"Error starting agent collaboration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start agent collaboration: {str(e)}",
        )


# Get agent performance metrics
@router.get("/{agent_id}/performance", response_model=List[AgentPerformanceMetrics])
async def get_agent_performance(
    agent_id: str,
    conversation_id: str = Query(None, description="Filter by conversation ID"),
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Get performance metrics for an agent."""
    try:
        service = AgentService(db)
        return await service.get_agent_performance(agent_id, conversation_id)
    except Exception as e:
        logger.error(f"Error getting performance metrics for agent {agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent performance: {str(e)}",
        )


# Get agent state
@router.get("/{agent_id}/state")
async def get_agent_state(
    agent_id: str,
    conversation_id: str = Query(..., description="Conversation ID"),
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Get current state of an agent in a conversation."""
    try:
        service = AgentService(db)
        state = await service.get_agent_state(conversation_id, agent_id)
        if not state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent state not found for agent {agent_id} in conversation {conversation_id}",
            )
        return state
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent state: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent state: {str(e)}",
        )


# Get conversation state
@router.get("/conversation/{conversation_id}/state")
async def get_conversation_state(
    conversation_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Get multi-agent conversation state."""
    try:
        service = AgentService(db)
        state = await service.get_conversation_state(conversation_id)
        if not state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation state not found for {conversation_id}",
            )
        return state
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation state: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversation state: {str(e)}",
        )


# Get agent service statistics
@router.get("/stats")
async def get_agent_stats(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Get agent service statistics."""
    try:
        service = AgentService(db)
        return service.get_stats()
    except Exception as e:
        logger.error(f"Error getting agent stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent stats: {str(e)}",
        )