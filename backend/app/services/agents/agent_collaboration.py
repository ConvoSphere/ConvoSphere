"""
Agent Collaboration Service.

This module provides agent collaboration functionality
extracted from the MultiAgentManager for better modularity.
"""

from datetime import UTC, datetime
from typing import Any

from loguru import logger
from pydantic import BaseModel

from backend.app.core.exceptions import ConversationError
from backend.app.schemas.agent import AgentCollaborationRequest

from .agent_state import agent_state_manager


class CollaborationEvent(BaseModel):
    """Agent collaboration event record."""

    conversation_id: str
    agent_ids: list[str]
    collaboration_type: str
    coordination_strategy: str
    shared_context: dict[str, Any]
    timestamp: datetime
    success: bool
    error_message: str | None = None
    duration_seconds: float | None = None

    model_config = {
        "validate_assignment": True,
        "extra": "forbid",
    }


class CollaborationSession(BaseModel):
    """Active collaboration session."""

    conversation_id: str
    agent_ids: list[str]
    collaboration_type: str
    coordination_strategy: str
    shared_context: dict[str, Any]
    start_time: datetime
    is_active: bool = True
    current_agent_index: int = 0
    round_count: int = 0

    model_config = {
        "validate_assignment": True,
        "extra": "forbid",
    }


class AgentCollaborationService:
    """Service for managing agent collaborations."""

    def __init__(self):
        """Initialize the collaboration service."""
        self.collaboration_history: list[CollaborationEvent] = []
        self.active_sessions: dict[str, CollaborationSession] = {}
        self.state_manager = agent_state_manager

    async def start_collaboration(
        self,
        request: AgentCollaborationRequest,
    ) -> dict[str, Any]:
        """
        Start agent collaboration.

        Args:
            request: Collaboration request

        Returns:
            dict: Collaboration result

        Raises:
            ConversationError: If collaboration fails
        """
        try:
            # Validate all agents exist in conversation
            for agent_id in request.agent_ids:
                state = self.state_manager.get_agent_state(
                    request.conversation_id, agent_id
                )
                if not state:
                    raise ConversationError(
                        f"Agent {agent_id} not found in conversation"
                    )

            # Create collaboration session
            session = CollaborationSession(
                conversation_id=request.conversation_id,
                agent_ids=request.agent_ids,
                collaboration_type=request.collaboration_type,
                coordination_strategy=request.coordination_strategy,
                shared_context=request.shared_context,
                start_time=datetime.now(UTC),
            )

            self.active_sessions[request.conversation_id] = session

            # Update agent states for collaboration
            for agent_id in request.agent_ids:
                self.state_manager.set_agent_status(
                    request.conversation_id, agent_id, "collaborating"
                )

            # Record collaboration event
            collaboration_event = CollaborationEvent(
                conversation_id=request.conversation_id,
                agent_ids=request.agent_ids,
                collaboration_type=request.collaboration_type,
                coordination_strategy=request.coordination_strategy,
                shared_context=request.shared_context,
                timestamp=datetime.now(UTC),
                success=True,
            )

            self.collaboration_history.append(collaboration_event)

            # Keep history size manageable
            if len(self.collaboration_history) > 10000:
                self.collaboration_history = self.collaboration_history[-5000:]

            logger.info(
                f"Started collaboration between {request.agent_ids} "
                f"in conversation {request.conversation_id}"
            )

            return {
                "success": True,
                "collaboration_info": {
                    "agents": request.agent_ids,
                    "type": request.collaboration_type,
                    "strategy": request.coordination_strategy,
                    "session_id": request.conversation_id,
                },
            }

        except Exception as e:
            # Record failed collaboration
            collaboration_event = CollaborationEvent(
                conversation_id=request.conversation_id,
                agent_ids=request.agent_ids,
                collaboration_type=request.collaboration_type,
                coordination_strategy=request.coordination_strategy,
                shared_context=request.shared_context,
                timestamp=datetime.now(UTC),
                success=False,
                error_message=str(e),
            )

            self.collaboration_history.append(collaboration_event)

            logger.error(f"Collaboration failed: {e}")
            raise ConversationError(f"Failed to start collaboration: {str(e)}")

    def end_collaboration(
        self,
        conversation_id: str,
    ) -> bool:
        """
        End collaboration session.

        Args:
            conversation_id: Conversation ID

        Returns:
            bool: True if ended, False if not found
        """
        session = self.active_sessions.get(conversation_id)
        if not session:
            return False

        # Update agent states
        for agent_id in session.agent_ids:
            self.state_manager.set_agent_status(conversation_id, agent_id, "idle")

        # Calculate duration
        duration = (datetime.now(UTC) - session.start_time).total_seconds()

        # Update collaboration event with duration
        for event in reversed(self.collaboration_history):
            if (
                event.conversation_id == conversation_id
                and event.success
                and event.duration_seconds is None
            ):
                event.duration_seconds = duration
                break

        # Remove from active sessions
        del self.active_sessions[conversation_id]

        logger.info(f"Ended collaboration for conversation {conversation_id}")
        return True

    def get_next_agent(
        self,
        conversation_id: str,
    ) -> str | None:
        """
        Get next agent based on coordination strategy.

        Args:
            conversation_id: Conversation ID

        Returns:
            Optional[str]: Next agent ID
        """
        session = self.active_sessions.get(conversation_id)
        if not session or not session.is_active:
            return None

        if session.coordination_strategy == "round_robin":
            agent_id = session.agent_ids[session.current_agent_index]
            session.current_agent_index = (session.current_agent_index + 1) % len(
                session.agent_ids
            )
            if session.current_agent_index == 0:
                session.round_count += 1
            return agent_id

        elif session.coordination_strategy == "priority":
            # Return first agent (highest priority)
            return session.agent_ids[0]

        elif session.coordination_strategy == "expertise":
            # For now, use round-robin for expertise
            # In the future, this could be based on agent expertise matching
            agent_id = session.agent_ids[session.current_agent_index]
            session.current_agent_index = (session.current_agent_index + 1) % len(
                session.agent_ids
            )
            return agent_id

        return None

    def update_shared_context(
        self,
        conversation_id: str,
        context_updates: dict[str, Any],
    ) -> bool:
        """
        Update shared context for collaboration.

        Args:
            conversation_id: Conversation ID
            context_updates: Context updates

        Returns:
            bool: True if updated, False if not found
        """
        session = self.active_sessions.get(conversation_id)
        if not session:
            return False

        session.shared_context.update(context_updates)
        return True

    def get_collaboration_session(
        self,
        conversation_id: str,
    ) -> CollaborationSession | None:
        """
        Get active collaboration session.

        Args:
            conversation_id: Conversation ID

        Returns:
            Optional[CollaborationSession]: Active session if found
        """
        return self.active_sessions.get(conversation_id)

    def get_collaboration_history(
        self,
        conversation_id: str | None = None,
        agent_id: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Get collaboration history.

        Args:
            conversation_id: Filter by conversation ID
            agent_id: Filter by agent ID
            limit: Maximum number of entries

        Returns:
            List[dict]: Collaboration history
        """
        history = self.collaboration_history.copy()

        if conversation_id:
            history = [h for h in history if h.conversation_id == conversation_id]

        if agent_id:
            history = [h for h in history if agent_id in h.agent_ids]

        # Sort by timestamp (most recent first)
        history.sort(key=lambda x: x.timestamp, reverse=True)

        # Convert to dict format
        result = []
        for event in history[:limit]:
            result.append(
                {
                    "conversation_id": event.conversation_id,
                    "agent_ids": event.agent_ids,
                    "collaboration_type": event.collaboration_type,
                    "coordination_strategy": event.coordination_strategy,
                    "shared_context": event.shared_context,
                    "timestamp": event.timestamp.isoformat(),
                    "success": event.success,
                    "error_message": event.error_message,
                    "duration_seconds": event.duration_seconds,
                }
            )

        return result

    def get_collaboration_stats(
        self,
        time_period_hours: int = 24,
    ) -> dict[str, Any]:
        """
        Get collaboration statistics.

        Args:
            time_period_hours: Time period for statistics

        Returns:
            dict: Collaboration statistics
        """
        cutoff_time = datetime.now(UTC) - datetime.timedelta(hours=time_period_hours)

        recent_collaborations = [
            h for h in self.collaboration_history if h.timestamp >= cutoff_time
        ]

        successful_collaborations = [h for h in recent_collaborations if h.success]
        failed_collaborations = [h for h in recent_collaborations if not h.success]

        # Calculate average duration
        durations = [
            h.duration_seconds
            for h in successful_collaborations
            if h.duration_seconds is not None
        ]
        avg_duration = sum(durations) / len(durations) if durations else 0

        # Get collaboration type distribution
        type_counts = {}
        for collab in recent_collaborations:
            collab_type = collab.collaboration_type
            type_counts[collab_type] = type_counts.get(collab_type, 0) + 1

        return {
            "time_period_hours": time_period_hours,
            "total_collaborations": len(recent_collaborations),
            "successful_collaborations": len(successful_collaborations),
            "failed_collaborations": len(failed_collaborations),
            "success_rate": (
                len(successful_collaborations) / len(recent_collaborations) * 100
                if recent_collaborations
                else 0
            ),
            "average_duration_seconds": avg_duration,
            "collaboration_type_distribution": type_counts,
            "active_sessions": len(self.active_sessions),
        }

    def get_agent_collaboration_stats(
        self,
        agent_id: str,
        time_period_hours: int = 24,
    ) -> dict[str, Any]:
        """
        Get collaboration statistics for an agent.

        Args:
            agent_id: Agent ID
            time_period_hours: Time period for statistics

        Returns:
            dict: Agent collaboration statistics
        """
        cutoff_time = datetime.now(UTC) - datetime.timedelta(hours=time_period_hours)

        agent_collaborations = [
            h
            for h in self.collaboration_history
            if h.timestamp >= cutoff_time and agent_id in h.agent_ids
        ]

        successful_collaborations = [h for h in agent_collaborations if h.success]

        # Get collaboration partners
        partners = set()
        for collab in agent_collaborations:
            for partner_id in collab.agent_ids:
                if partner_id != agent_id:
                    partners.add(partner_id)

        return {
            "agent_id": agent_id,
            "time_period_hours": time_period_hours,
            "total_collaborations": len(agent_collaborations),
            "successful_collaborations": len(successful_collaborations),
            "success_rate": (
                len(successful_collaborations) / len(agent_collaborations) * 100
                if agent_collaborations
                else 0
            ),
            "collaboration_partners": list(partners),
            "partner_count": len(partners),
        }

    def get_stats(self) -> dict[str, Any]:
        """
        Get collaboration service statistics.

        Returns:
            dict: Service statistics
        """
        total_collaborations = len(self.collaboration_history)
        successful_collaborations = len(
            [h for h in self.collaboration_history if h.success]
        )
        failed_collaborations = len(
            [h for h in self.collaboration_history if not h.success]
        )

        # Get unique conversations and agents
        conversations = set(h.conversation_id for h in self.collaboration_history)
        agents = set()
        for collab in self.collaboration_history:
            agents.update(collab.agent_ids)

        return {
            "total_collaborations": total_collaborations,
            "successful_collaborations": successful_collaborations,
            "failed_collaborations": failed_collaborations,
            "success_rate": (
                successful_collaborations / total_collaborations * 100
                if total_collaborations
                else 0
            ),
            "unique_conversations": len(conversations),
            "unique_agents": len(agents),
            "active_sessions": len(self.active_sessions),
            "history_size": len(self.collaboration_history),
        }


# Global agent collaboration service instance
agent_collaboration_service = AgentCollaborationService()
