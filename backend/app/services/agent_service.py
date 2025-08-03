"""
Agent service for managing AI agents.

This module provides business logic for managing AI agents, including
agent creation, handoffs, collaboration, and performance monitoring.
It integrates with the new modular AgentManager and follows the existing service patterns.
"""

from typing import Any

from loguru import logger
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.schemas.agent import (
    AgentCollaborationRequest,
    AgentCreate,
    AgentHandoffRequest,
    AgentPerformanceMetrics,
    AgentResponse,
    AgentUpdate,
)
from backend.app.services.agents import agent_manager


class AgentService:
    """Service for managing AI agents."""

    def __init__(self, db: Session | None = None):
        """Initialize the agent service."""
        self.db = db or get_db()
        self.agent_manager = agent_manager

    async def get_available_agents(self) -> list[dict[str, Any]]:
        """
        Get list of available agents from the registry.

        Returns:
            List[dict]: List of available agents with their configurations
        """
        try:
            agents = await self.agent_manager.get_available_agents()
            logger.info(f"Retrieved {len(agents)} available agents")
            return agents
        except Exception as e:
            logger.error(f"Error retrieving available agents: {e}")
            raise

    async def create_agent(self, agent_data: AgentCreate) -> AgentResponse:
        """
        Create a new agent and add it to the registry.

        Args:
            agent_data: Agent creation data

        Returns:
            AgentResponse: Created agent response
        """
        try:
            response = await self.agent_manager.create_agent(agent_data)
            logger.info(f"Created agent: {agent_data.config.name}")
            return response

        except Exception as e:
            logger.error(f"Error creating agent: {e}")
            raise

    async def update_agent(
        self, agent_id: str, agent_data: AgentUpdate
    ) -> AgentResponse | None:
        """
        Update an existing agent.

        Args:
            agent_id: Agent ID
            agent_data: Agent update data

        Returns:
            AgentResponse: Updated agent response or None if not found
        """
        try:
            response = await self.agent_manager.update_agent(agent_id, agent_data)
            if response:
                logger.info(f"Updated agent: {agent_id}")
            else:
                logger.warning(f"Agent {agent_id} not found")
            return response

        except Exception as e:
            logger.error(f"Error updating agent {agent_id}: {e}")
            raise

    async def delete_agent(self, agent_id: str) -> bool:
        """
        Delete an agent from the registry.

        Args:
            agent_id: Agent ID

        Returns:
            bool: True if deleted, False if not found
        """
        try:
            success = await self.agent_manager.delete_agent(agent_id)
            if success:
                logger.info(f"Deleted agent: {agent_id}")
            else:
                logger.warning(f"Agent {agent_id} not found in registry")
            return success

        except Exception as e:
            logger.error(f"Error deleting agent {agent_id}: {e}")
            raise

    async def handoff_agent(self, request: AgentHandoffRequest) -> dict[str, Any]:
        """
        Perform agent handoff.

        Args:
            request: Handoff request

        Returns:
            dict: Handoff result
        """
        try:
            result = await self.agent_manager.handoff_agent(request)
            logger.info(
                f"Agent handoff completed: {request.from_agent_id} -> {request.to_agent_id}"
            )
            return result

        except Exception as e:
            logger.error(f"Error during agent handoff: {e}")
            raise

    async def start_collaboration(
        self, request: AgentCollaborationRequest
    ) -> dict[str, Any]:
        """
        Start agent collaboration.

        Args:
            request: Collaboration request

        Returns:
            dict: Collaboration result
        """
        try:
            result = await self.agent_manager.start_collaboration(request)
            logger.info(f"Agent collaboration started: {request.agent_ids}")
            return result

        except Exception as e:
            logger.error(f"Error starting agent collaboration: {e}")
            raise

    async def get_agent_performance(
        self, agent_id: str, conversation_id: str | None = None
    ) -> list[AgentPerformanceMetrics]:
        """
        Get performance metrics for an agent.

        Args:
            agent_id: Agent ID
            conversation_id: Optional conversation ID to filter by

        Returns:
            List[AgentPerformanceMetrics]: Performance metrics
        """
        try:
            metrics = await self.agent_manager.get_agent_performance(
                agent_id, conversation_id=conversation_id
            )
            logger.info(
                f"Retrieved {len(metrics)} performance metrics for agent {agent_id}"
            )
            return metrics

        except Exception as e:
            logger.error(
                f"Error retrieving performance metrics for agent {agent_id}: {e}"
            )
            raise

    async def get_agent_state(
        self, conversation_id: str, agent_id: str
    ) -> dict[str, Any] | None:
        """
        Get current state of an agent in a conversation.

        Args:
            conversation_id: Conversation ID
            agent_id: Agent ID

        Returns:
            dict: Agent state or None if not found
        """
        try:
            state = await self.agent_manager.get_agent_state(conversation_id, agent_id)
            return state

        except Exception as e:
            logger.error(f"Error retrieving agent state: {e}")
            raise

    async def get_conversation_state(
        self, conversation_id: str
    ) -> dict[str, Any] | None:
        """
        Get multi-agent conversation state.

        Args:
            conversation_id: Conversation ID

        Returns:
            dict: Conversation state or None if not found
        """
        try:
            state = self.agent_manager.get_conversation_state(conversation_id)
            return state

        except Exception as e:
            logger.error(f"Error retrieving conversation state: {e}")
            raise

    def get_stats(self) -> dict[str, Any]:
        """
        Get agent service statistics.

        Returns:
            dict: Service statistics
        """
        try:
            return self.agent_manager.get_stats()
        except Exception as e:
            logger.error(f"Error retrieving agent stats: {e}")
            raise
