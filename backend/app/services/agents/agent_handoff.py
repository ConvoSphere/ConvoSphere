"""
Agent Handoff Service.

This module provides agent handoff functionality
extracted from the MultiAgentManager for better modularity.
"""

from datetime import UTC, datetime
from typing import Any

from loguru import logger
from pydantic import BaseModel

from backend.app.core.exceptions import ConversationError
from backend.app.schemas.agent import AgentHandoffRequest

from .agent_state import agent_state_manager


class HandoffEvent(BaseModel):
    """Agent handoff event record."""

    conversation_id: str
    from_agent_id: str
    to_agent_id: str
    reason: str
    context: dict[str, Any]
    priority: int
    timestamp: datetime
    success: bool
    error_message: str | None = None

    model_config = {
        "validate_assignment": True,
        "extra": "forbid",
    }


class AgentHandoffService:
    """Service for managing agent handoffs."""

    def __init__(self):
        """Initialize the handoff service."""
        self.handoff_history: list[HandoffEvent] = []
        self.state_manager = agent_state_manager

    async def perform_handoff(
        self,
        request: AgentHandoffRequest,
    ) -> dict[str, Any]:
        """
        Perform agent handoff.

        Args:
            request: Handoff request

        Returns:
            dict: Handoff result

        Raises:
            ConversationError: If handoff fails
        """
        try:
            # Validate agents exist in conversation
            from_state = self.state_manager.get_agent_state(
                request.conversation_id, request.from_agent_id
            )
            to_state = self.state_manager.get_agent_state(
                request.conversation_id, request.to_agent_id
            )

            if not from_state:
                raise ConversationError(
                    f"From agent {request.from_agent_id} not found in conversation"
                )

            if not to_state:
                raise ConversationError(
                    f"To agent {request.to_agent_id} not found in conversation"
                )

            # Update agent states
            self.state_manager.set_agent_status(
                request.conversation_id, request.from_agent_id, "idle"
            )
            self.state_manager.set_agent_status(
                request.conversation_id, request.to_agent_id, "active"
            )

            # Record handoff event
            handoff_event = HandoffEvent(
                conversation_id=request.conversation_id,
                from_agent_id=request.from_agent_id,
                to_agent_id=request.to_agent_id,
                reason=request.reason,
                context=request.context,
                priority=request.priority,
                timestamp=datetime.now(UTC),
                success=True,
            )

            self.handoff_history.append(handoff_event)

            # Keep history size manageable
            if len(self.handoff_history) > 10000:
                self.handoff_history = self.handoff_history[-5000:]

            logger.info(
                f"Handoff completed: {request.from_agent_id} -> {request.to_agent_id} "
                f"in conversation {request.conversation_id}"
            )

            return {
                "success": True,
                "handoff_info": {
                    "from_agent": request.from_agent_id,
                    "to_agent": request.to_agent_id,
                    "reason": request.reason,
                    "priority": request.priority,
                    "timestamp": handoff_event.timestamp.isoformat(),
                },
            }

        except Exception as e:
            # Record failed handoff
            handoff_event = HandoffEvent(
                conversation_id=request.conversation_id,
                from_agent_id=request.from_agent_id,
                to_agent_id=request.to_agent_id,
                reason=request.reason,
                context=request.context,
                priority=request.priority,
                timestamp=datetime.now(UTC),
                success=False,
                error_message=str(e),
            )

            self.handoff_history.append(handoff_event)

            logger.error(f"Handoff failed: {e}")
            raise ConversationError(f"Failed to perform handoff: {str(e)}")

    def get_handoff_history(
        self,
        conversation_id: str | None = None,
        agent_id: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Get handoff history.

        Args:
            conversation_id: Filter by conversation ID
            agent_id: Filter by agent ID
            limit: Maximum number of entries

        Returns:
            List[dict]: Handoff history
        """
        history = self.handoff_history.copy()

        if conversation_id:
            history = [h for h in history if h.conversation_id == conversation_id]

        if agent_id:
            history = [
                h
                for h in history
                if agent_id in (h.from_agent_id, h.to_agent_id)
            ]

        # Sort by timestamp (most recent first)
        history.sort(key=lambda x: x.timestamp, reverse=True)

        # Convert to dict format
        result = []
        for event in history[:limit]:
            result.append(
                {
                    "conversation_id": event.conversation_id,
                    "from_agent": event.from_agent_id,
                    "to_agent": event.to_agent_id,
                    "reason": event.reason,
                    "context": event.context,
                    "priority": event.priority,
                    "timestamp": event.timestamp.isoformat(),
                    "success": event.success,
                    "error_message": event.error_message,
                }
            )

        return result

    def get_agent_handoff_stats(
        self,
        agent_id: str,
        time_period_hours: int = 24,
    ) -> dict[str, Any]:
        """
        Get handoff statistics for an agent.

        Args:
            agent_id: Agent ID
            time_period_hours: Time period for statistics

        Returns:
            dict: Handoff statistics
        """
        cutoff_time = datetime.now(UTC) - datetime.timedelta(hours=time_period_hours)

        recent_handoffs = [
            h
            for h in self.handoff_history
            if h.timestamp >= cutoff_time
            and (agent_id in (h.from_agent_id, h.to_agent_id))
        ]

        handoffs_from = [h for h in recent_handoffs if h.from_agent_id == agent_id]
        handoffs_to = [h for h in recent_handoffs if h.to_agent_id == agent_id]

        successful_handoffs = [h for h in recent_handoffs if h.success]
        failed_handoffs = [h for h in recent_handoffs if not h.success]

        return {
            "agent_id": agent_id,
            "time_period_hours": time_period_hours,
            "total_handoffs": len(recent_handoffs),
            "handoffs_from": len(handoffs_from),
            "handoffs_to": len(handoffs_to),
            "successful_handoffs": len(successful_handoffs),
            "failed_handoffs": len(failed_handoffs),
            "success_rate": (
                len(successful_handoffs) / len(recent_handoffs) * 100
                if recent_handoffs
                else 0
            ),
            "most_common_reason": self._get_most_common_reason(recent_handoffs),
        }

    def _get_most_common_reason(
        self,
        handoffs: list[HandoffEvent],
    ) -> str | None:
        """Get the most common handoff reason."""
        if not handoffs:
            return None

        reason_counts = {}
        for handoff in handoffs:
            reason = handoff.reason
            reason_counts[reason] = reason_counts.get(reason, 0) + 1

        return max(reason_counts.items(), key=lambda x: x[1])[0]

    def get_conversation_handoff_summary(
        self,
        conversation_id: str,
    ) -> dict[str, Any]:
        """
        Get handoff summary for a conversation.

        Args:
            conversation_id: Conversation ID

        Returns:
            dict: Handoff summary
        """
        conversation_handoffs = [
            h for h in self.handoff_history if h.conversation_id == conversation_id
        ]

        if not conversation_handoffs:
            return {
                "conversation_id": conversation_id,
                "total_handoffs": 0,
                "agents_involved": [],
                "handoff_flow": [],
            }

        # Get unique agents involved
        agents_involved = set()
        for handoff in conversation_handoffs:
            agents_involved.add(handoff.from_agent_id)
            agents_involved.add(handoff.to_agent_id)

        # Create handoff flow
        handoff_flow = []
        for handoff in conversation_handoffs:
            handoff_flow.append(
                {
                    "from_agent": handoff.from_agent_id,
                    "to_agent": handoff.to_agent_id,
                    "reason": handoff.reason,
                    "timestamp": handoff.timestamp.isoformat(),
                    "success": handoff.success,
                }
            )

        return {
            "conversation_id": conversation_id,
            "total_handoffs": len(conversation_handoffs),
            "agents_involved": list(agents_involved),
            "handoff_flow": handoff_flow,
            "successful_handoffs": len([h for h in conversation_handoffs if h.success]),
            "failed_handoffs": len([h for h in conversation_handoffs if not h.success]),
        }

    def get_stats(self) -> dict[str, Any]:
        """
        Get handoff service statistics.

        Returns:
            dict: Service statistics
        """
        total_handoffs = len(self.handoff_history)
        successful_handoffs = len([h for h in self.handoff_history if h.success])
        failed_handoffs = len([h for h in self.handoff_history if not h.success])

        # Get unique conversations and agents
        conversations = {h.conversation_id for h in self.handoff_history}
        agents = set()
        for handoff in self.handoff_history:
            agents.add(handoff.from_agent_id)
            agents.add(handoff.to_agent_id)

        return {
            "total_handoffs": total_handoffs,
            "successful_handoffs": successful_handoffs,
            "failed_handoffs": failed_handoffs,
            "success_rate": (
                successful_handoffs / total_handoffs * 100 if total_handoffs else 0
            ),
            "unique_conversations": len(conversations),
            "unique_agents": len(agents),
            "history_size": len(self.handoff_history),
        }


# Global agent handoff service instance
agent_handoff_service = AgentHandoffService()
