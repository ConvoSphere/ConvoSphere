"""
Agent service for managing AI agents.

This module provides business logic for managing AI agents, including
agent creation, handoffs, collaboration, and performance monitoring.
It integrates with the MultiAgentManager and follows the existing service patterns.
"""

from typing import Any
from uuid import UUID

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
from backend.app.services.multi_agent_manager import multi_agent_manager


class AgentService:
    """Service for managing AI agents."""

    def __init__(self, db: Session | None = None):
        """Initialize the agent service."""
        self.db = db or get_db()
        self.multi_agent_manager = multi_agent_manager

    async def get_available_agents(self) -> list[dict[str, Any]]:
        """
        Get list of available agents from the registry.

        Returns:
            List[dict]: List of available agents with their configurations
        """
        try:
            agents = self.multi_agent_manager.get_available_agents()
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
            # Add agent to registry
            agent_id = f"custom_{len(self.multi_agent_manager.agent_registry) + 1}"
            self.multi_agent_manager.add_agent_to_registry(agent_id, agent_data.config)

            # Create response
            response = AgentResponse(
                id=UUID(agent_id),
                config=agent_data.config,
                user_id=agent_data.user_id,
                is_public=agent_data.is_public,
                is_template=agent_data.is_template,
                created_at=(
                    agent_data.config.created_at
                    if hasattr(agent_data.config, "created_at")
                    else None
                ),
                updated_at=(
                    agent_data.config.updated_at
                    if hasattr(agent_data.config, "updated_at")
                    else None
                ),
            )

            logger.info(f"Created agent: {agent_data.config.name} with ID {agent_id}")
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
            # Get current agent config
            current_config = self.multi_agent_manager.agent_registry.get(agent_id)
            if not current_config:
                logger.warning(f"Agent {agent_id} not found in registry")
                return None

            # Update config fields
            update_data = agent_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(current_config, field):
                    setattr(current_config, field, value)

            # Create response
            response = AgentResponse(
                id=UUID(agent_id),
                config=current_config,
                user_id=UUID("00000000-0000-0000-0000-000000000000"),  # Placeholder
                is_public=getattr(agent_data, "is_public", False),
                is_template=getattr(agent_data, "is_template", False),
                created_at=None,
                updated_at=None,
            )

            logger.info(f"Updated agent: {agent_id}")
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
            if agent_id in self.multi_agent_manager.agent_registry:
                self.multi_agent_manager.remove_agent_from_registry(agent_id)
                logger.info(f"Deleted agent: {agent_id}")
                return True
            logger.warning(f"Agent {agent_id} not found in registry")
            return False

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
            result = await self.multi_agent_manager.handoff_agent(request)
            logger.info(
                f"Agent handoff completed: {request.from_agent_id} -> {request.to_agent_id}"
            )
            return {
                "success": True,
                "conversation": result.dict(),
                "handoff_info": {
                    "from_agent": request.from_agent_id,
                    "to_agent": request.to_agent_id,
                    "reason": request.reason,
                },
            }

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
            result = await self.multi_agent_manager.start_collaboration(request)
            logger.info(f"Agent collaboration started: {request.agent_ids}")
            return {
                "success": True,
                "conversation": result.dict(),
                "collaboration_info": {
                    "agents": request.agent_ids,
                    "type": request.collaboration_type,
                    "strategy": request.coordination_strategy,
                },
            }

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
            metrics = self.multi_agent_manager.get_performance_metrics(
                agent_id=agent_id, conversation_id=conversation_id, limit=100
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
            state = self.multi_agent_manager.get_agent_state(conversation_id, agent_id)
            if state:
                return state.dict()
            return None

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
            state = self.multi_agent_manager.get_conversation_state(conversation_id)
            if state:
                return state.dict()
            return None

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
            return self.multi_agent_manager.get_stats()
        except Exception as e:
            logger.error(f"Error retrieving agent stats: {e}")
            raise
