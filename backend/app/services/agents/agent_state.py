"""
Agent State Manager Service.

This module provides agent state management functionality
extracted from the MultiAgentManager for better modularity.
"""

from datetime import UTC, datetime
from typing import Any

from loguru import logger
from pydantic import BaseModel

from backend.app.schemas.agent import AgentState


class AgentStateEntry(BaseModel):
    """Agent state entry with extended metadata."""

    agent_id: str
    conversation_id: str
    state: AgentState
    created_at: datetime
    updated_at: datetime
    last_activity: datetime
    status_history: list[dict[str, Any]] = []

    model_config = {
        "validate_assignment": True,
        "extra": "forbid",
    }


class AgentStateManager:
    """Manager for agent states across conversations."""

    def __init__(self):
        """Initialize the agent state manager."""
        self.agent_states: dict[str, AgentStateEntry] = {}
        self.state_history: list[dict[str, Any]] = []

    def _get_state_key(self, conversation_id: str, agent_id: str) -> str:
        """Generate state key for agent in conversation."""
        return f"{conversation_id}:{agent_id}"

    def create_agent_state(
        self,
        conversation_id: str,
        agent_id: str,
        initial_status: str = "idle",
    ) -> AgentStateEntry:
        """
        Create a new agent state for a conversation.

        Args:
            conversation_id: Conversation ID
            agent_id: Agent ID
            initial_status: Initial agent status

        Returns:
            AgentStateEntry: Created state entry
        """
        state_key = self._get_state_key(conversation_id, agent_id)

        if state_key in self.agent_states:
            logger.warning(f"Agent state already exists for {state_key}")
            return self.agent_states[state_key]

        now = datetime.now(UTC)
        agent_state = AgentState(
            agent_id=agent_id,
            conversation_id=conversation_id,
            current_step=0,
            total_steps=1,
            status=initial_status,
            last_activity=now,
            created_at=now,
            updated_at=now,
        )

        state_entry = AgentStateEntry(
            agent_id=agent_id,
            conversation_id=conversation_id,
            state=agent_state,
            created_at=now,
            updated_at=now,
            last_activity=now,
        )

        self.agent_states[state_key] = state_entry
        logger.info(f"Created agent state for {state_key}")
        return state_entry

    def get_agent_state(
        self,
        conversation_id: str,
        agent_id: str,
    ) -> AgentStateEntry | None:
        """
        Get agent state for a conversation.

        Args:
            conversation_id: Conversation ID
            agent_id: Agent ID

        Returns:
            Optional[AgentStateEntry]: Agent state if found
        """
        state_key = self._get_state_key(conversation_id, agent_id)
        return self.agent_states.get(state_key)

    def update_agent_state(
        self,
        conversation_id: str,
        agent_id: str,
        status: str | None = None,
        current_step: int | None = None,
        total_steps: int | None = None,
        context: dict[str, Any] | None = None,
    ) -> bool:
        """
        Update agent state.

        Args:
            conversation_id: Conversation ID
            agent_id: Agent ID
            status: New status
            current_step: Current step
            total_steps: Total steps
            context: Context data

        Returns:
            bool: True if updated, False if not found
        """
        state_entry = self.get_agent_state(conversation_id, agent_id)
        if not state_entry:
            return False

        now = datetime.now(UTC)
        old_status = state_entry.state.status

        # Update state fields
        if status is not None:
            state_entry.state.status = status
        if current_step is not None:
            state_entry.state.current_step = current_step
        if total_steps is not None:
            state_entry.state.total_steps = total_steps
        if context is not None:
            state_entry.state.context = context

        state_entry.state.last_activity = now
        state_entry.state.updated_at = now
        state_entry.updated_at = now
        state_entry.last_activity = now

        # Record status change in history
        if status != old_status:
            self._record_status_change(
                conversation_id, agent_id, old_status, status, now
            )

        logger.debug(f"Updated agent state for {conversation_id}:{agent_id}")
        return True

    def update_agent_context(
        self,
        conversation_id: str,
        agent_id: str,
        context: dict[str, Any],
    ) -> bool:
        """
        Update agent context.

        Args:
            conversation_id: Conversation ID
            agent_id: Agent ID
            context: New context data

        Returns:
            bool: True if updated, False if not found
        """
        return self.update_agent_state(
            conversation_id, agent_id, context=context
        )

    def set_agent_status(
        self,
        conversation_id: str,
        agent_id: str,
        status: str,
    ) -> bool:
        """
        Set agent status.

        Args:
            conversation_id: Conversation ID
            agent_id: Agent ID
            status: New status

        Returns:
            bool: True if updated, False if not found
        """
        return self.update_agent_state(conversation_id, agent_id, status=status)

    def increment_agent_step(
        self,
        conversation_id: str,
        agent_id: str,
    ) -> bool:
        """
        Increment agent current step.

        Args:
            conversation_id: Conversation ID
            agent_id: Agent ID

        Returns:
            bool: True if updated, False if not found
        """
        state_entry = self.get_agent_state(conversation_id, agent_id)
        if not state_entry:
            return False

        new_step = state_entry.state.current_step + 1
        return self.update_agent_state(
            conversation_id, agent_id, current_step=new_step
        )

    def set_agent_steps(
        self,
        conversation_id: str,
        agent_id: str,
        current_step: int,
        total_steps: int,
    ) -> bool:
        """
        Set agent step information.

        Args:
            conversation_id: Conversation ID
            agent_id: Agent ID
            current_step: Current step
            total_steps: Total steps

        Returns:
            bool: True if updated, False if not found
        """
        return self.update_agent_state(
            conversation_id, agent_id, current_step=current_step, total_steps=total_steps
        )

    def get_conversation_agent_states(
        self,
        conversation_id: str,
    ) -> list[AgentStateEntry]:
        """
        Get all agent states for a conversation.

        Args:
            conversation_id: Conversation ID

        Returns:
            List[AgentStateEntry]: List of agent states
        """
        states = []
        for state_entry in self.agent_states.values():
            if state_entry.conversation_id == conversation_id:
                states.append(state_entry)
        return states

    def get_active_agents(
        self,
        conversation_id: str,
    ) -> list[str]:
        """
        Get active agent IDs for a conversation.

        Args:
            conversation_id: Conversation ID

        Returns:
            List[str]: List of active agent IDs
        """
        active_agents = []
        for state_entry in self.agent_states.values():
            if (
                state_entry.conversation_id == conversation_id
                and state_entry.state.status == "active"
            ):
                active_agents.append(state_entry.agent_id)
        return active_agents

    def cleanup_conversation_states(
        self,
        conversation_id: str,
    ) -> int:
        """
        Clean up all agent states for a conversation.

        Args:
            conversation_id: Conversation ID

        Returns:
            int: Number of states removed
        """
        removed_count = 0
        keys_to_remove = []

        for state_key, state_entry in self.agent_states.items():
            if state_entry.conversation_id == conversation_id:
                keys_to_remove.append(state_key)
                removed_count += 1

        for key in keys_to_remove:
            del self.agent_states[key]

        logger.info(f"Cleaned up {removed_count} agent states for conversation {conversation_id}")
        return removed_count

    def get_agent_activity(
        self,
        agent_id: str,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Get agent activity history.

        Args:
            agent_id: Agent ID
            limit: Maximum number of entries

        Returns:
            List[dict]: Activity history
        """
        activity = []
        for state_entry in self.agent_states.values():
            if state_entry.agent_id == agent_id:
                activity.append({
                    "conversation_id": state_entry.conversation_id,
                    "status": state_entry.state.status,
                    "current_step": state_entry.state.current_step,
                    "total_steps": state_entry.state.total_steps,
                    "last_activity": state_entry.last_activity.isoformat(),
                    "created_at": state_entry.created_at.isoformat(),
                })

        # Sort by last activity (most recent first)
        activity.sort(key=lambda x: x["last_activity"], reverse=True)
        return activity[:limit]

    def _record_status_change(
        self,
        conversation_id: str,
        agent_id: str,
        old_status: str,
        new_status: str,
        timestamp: datetime,
    ) -> None:
        """Record status change in history."""
        change_record = {
            "conversation_id": conversation_id,
            "agent_id": agent_id,
            "old_status": old_status,
            "new_status": new_status,
            "timestamp": timestamp,
        }

        self.state_history.append(change_record)

        # Keep history size manageable
        if len(self.state_history) > 10000:
            self.state_history = self.state_history[-5000:]

    def get_status_history(
        self,
        conversation_id: str | None = None,
        agent_id: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Get status change history.

        Args:
            conversation_id: Filter by conversation ID
            agent_id: Filter by agent ID
            limit: Maximum number of entries

        Returns:
            List[dict]: Status change history
        """
        history = self.state_history.copy()

        if conversation_id:
            history = [h for h in history if h["conversation_id"] == conversation_id]

        if agent_id:
            history = [h for h in history if h["agent_id"] == agent_id]

        # Sort by timestamp (most recent first)
        history.sort(key=lambda x: x["timestamp"], reverse=True)
        return history[:limit]

    def get_stats(self) -> dict[str, Any]:
        """
        Get state manager statistics.

        Returns:
            dict: Statistics
        """
        total_states = len(self.agent_states)
        active_states = sum(
            1 for entry in self.agent_states.values()
            if entry.state.status == "active"
        )
        total_history = len(self.state_history)

        return {
            "total_agent_states": total_states,
            "active_agent_states": active_states,
            "inactive_agent_states": total_states - active_states,
            "status_history_entries": total_history,
        }


# Global agent state manager instance
agent_state_manager = AgentStateManager()