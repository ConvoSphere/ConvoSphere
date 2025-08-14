"""
Agent Manager Service.

This module provides the main agent management service that coordinates
all agent-related functionality using the modular services.
"""

from typing import Any

from loguru import logger

from backend.app.core.exceptions import ConversationError
from backend.app.schemas.agent import (
    AgentCollaborationRequest,
    AgentCreate,
    AgentHandoffRequest,
    AgentPerformanceMetrics,
    AgentResponse,
    AgentUpdate,
)

from .agent_collaboration import agent_collaboration_service
from .agent_handoff import agent_handoff_service
from .agent_performance import agent_performance_service
from .agent_registry import agent_registry
from .agent_state import agent_state_manager
from .agent_runner import AssistantAgentAdapter


class AgentManager:
    """Main agent manager that coordinates all agent services."""

    def __init__(self):
        """Initialize the agent manager."""
        self.registry = agent_registry
        self.state_manager = agent_state_manager
        self.handoff_service = agent_handoff_service
        self.collaboration_service = agent_collaboration_service
        self.performance_service = agent_performance_service

    async def get_available_agents(self) -> list[dict[str, Any]]:
        """
        Get list of available agents.

        Returns:
            List[dict]: List of available agents
        """
        try:
            return self.registry.list_agents(active_only=True)
        except Exception as e:
            logger.error(f"Error getting available agents: {e}")
            raise

    async def create_agent(self, agent_data: AgentCreate) -> AgentResponse:
        """
        Create a new agent.

        Args:
            agent_data: Agent creation data

        Returns:
            AgentResponse: Created agent response
        """
        try:
            # Generate agent ID
            agent_id = f"custom_{len(self.registry.agents) + 1}"

            # Add to registry
            entry = self.registry.add_agent(agent_id, agent_data.config)

            # Create response
            response = AgentResponse(
                id=agent_id,
                config=agent_data.config,
                user_id=agent_data.user_id,
                is_public=agent_data.is_public,
                is_template=agent_data.is_template,
                created_at=entry.created_at,
                updated_at=entry.updated_at,
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
            # Get current agent
            entry = self.registry.get_agent(agent_id)
            if not entry:
                logger.warning(f"Agent {agent_id} not found in registry")
                return None

            # Update config fields
            update_data = agent_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(entry.config, field):
                    setattr(entry.config, field, value)

            # Update in registry
            self.registry.update_agent(agent_id, entry.config)

            # Create response
            response = AgentResponse(
                id=agent_id,
                config=entry.config,
                user_id=agent_data.user_id if hasattr(agent_data, "user_id") else None,
                is_public=getattr(agent_data, "is_public", entry.is_active),
                is_template=getattr(agent_data, "is_template", False),
                created_at=entry.created_at,
                updated_at=entry.updated_at,
            )

            logger.info(f"Updated agent: {agent_id}")
            return response

        except Exception as e:
            logger.error(f"Error updating agent {agent_id}: {e}")
            raise

    async def delete_agent(self, agent_id: str) -> bool:
        """
        Delete an agent.

        Args:
            agent_id: Agent ID

        Returns:
            bool: True if deleted, False if not found
        """
        try:
            success = self.registry.remove_agent(agent_id)
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
            return await self.handoff_service.perform_handoff(request)
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
            return await self.collaboration_service.start_collaboration(request)
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
            return self.performance_service.get_agent_performance(
                agent_id, conversation_id=conversation_id
            )
        except Exception as e:
            logger.error(f"Error getting performance metrics for agent {agent_id}: {e}")
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
            state_entry = self.state_manager.get_agent_state(conversation_id, agent_id)
            if state_entry:
                return state_entry.dict()
            return None

        except Exception as e:
            logger.error(f"Error retrieving agent state: {e}")
            raise

    async def create_multi_agent_conversation(
        self,
        conversation_id: str,
        user_id: str,
        initial_agent: str,
        additional_agents: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Create a new multi-agent conversation.

        Args:
            conversation_id: Conversation ID
            user_id: User ID
            initial_agent: Initial agent ID
            additional_agents: Additional agent IDs

        Returns:
            dict: Conversation creation result
        """
        try:
            # Validate agents exist in registry
            all_agents = [initial_agent] + (additional_agents or [])
            for agent_id in all_agents:
                if not self.registry.get_agent(agent_id):
                    raise ConversationError(f"Agent {agent_id} not found in registry")

            # Create agent states
            for agent_id in all_agents:
                self.state_manager.create_agent_state(
                    conversation_id, agent_id, initial_status="idle"
                )

            # Set initial agent as active
            self.state_manager.set_agent_status(
                conversation_id, initial_agent, "active"
            )

            # Record usage for initial agent
            self.registry.record_usage(initial_agent)

            logger.info(
                f"Created multi-agent conversation {conversation_id} with agents: {all_agents}"
            )

            return {
                "conversation_id": conversation_id,
                "user_id": user_id,
                "agents": all_agents,
                "current_agent": initial_agent,
                "status": "active",
            }

        except Exception as e:
            logger.error(f"Error creating multi-agent conversation: {e}")
            raise ConversationError(f"Failed to create conversation: {str(e)}")

    async def get_agent_response(
        self,
        conversation_id: str,
        user_message: str,
        user_id: str,
        target_agent: str | None = None,
    ) -> dict[str, Any]:
        """
        Get response from current or specified agent.

        Args:
            conversation_id: Conversation ID
            user_message: User message
            user_id: User ID
            target_agent: Specific agent to respond (optional)

        Returns:
            dict: Agent response
        """
        try:
            # Get current agent if not specified
            if not target_agent:
                active_agents = self.state_manager.get_active_agents(conversation_id)
                if not active_agents:
                    raise ConversationError("No active agent in conversation")
                target_agent = active_agents[0]

            # Validate agent exists and is in conversation
            agent_entry = self.registry.get_agent(target_agent)
            if not agent_entry:
                raise ConversationError(f"Agent {target_agent} not found")

            agent_state = self.state_manager.get_agent_state(
                conversation_id, target_agent
            )
            if not agent_state:
                raise ConversationError(f"Agent {target_agent} not in conversation")

            # Update agent state to processing
            self.state_manager.set_agent_status(
                conversation_id, target_agent, "processing"
            )

            # Record usage
            self.registry.record_usage(target_agent)

            # Generate response using adapter runner
            runner = AssistantAgentAdapter()
            run_result = await runner.process_message(
                conversation_id=conversation_id,
                user_id=user_id,
                message=user_message,
                model=agent_entry.config.model,
                temperature=agent_entry.config.temperature,
                use_tools=True,
            )

            response_content = run_result.get("content", "")
            model_used = run_result.get("model_used", agent_entry.config.model)
            tokens_used = int(run_result.get("tokens_used", 0) or 0)
            processing_time = float(run_result.get("processing_time", 0.0) or 0.0)

            # Update agent state back to active
            self.state_manager.set_agent_status(conversation_id, target_agent, "active")

            # Record performance metrics
            metrics = AgentPerformanceMetrics(
                agent_id=target_agent,
                conversation_id=conversation_id,
                response_time=processing_time or 0.0,
                success_rate=100.0 if run_result.get("success", True) else 0.0,
                tokens_used=tokens_used,
                error_count=0 if run_result.get("success", True) else 1,
            )
            self.performance_service.record_performance(metrics)

            return {
                "agent_id": target_agent,
                "response": response_content,
                "model_used": model_used,
                "tokens_used": metrics.tokens_used,
                "processing_time": metrics.response_time,
            }

        except Exception as e:
            logger.error(f"Error getting agent response: {e}")
            raise ConversationError(f"Failed to get agent response: {str(e)}")

    def get_conversation_state(self, conversation_id: str) -> dict[str, Any] | None:
        """
        Get multi-agent conversation state.

        Args:
            conversation_id: Conversation ID

        Returns:
            dict: Conversation state or None if not found
        """
        try:
            agent_states = self.state_manager.get_conversation_agent_states(
                conversation_id
            )
            if not agent_states:
                return None

            active_agents = self.state_manager.get_active_agents(conversation_id)
            current_agent = active_agents[0] if active_agents else None

            # Check for active collaboration
            collaboration_session = (
                self.collaboration_service.get_collaboration_session(conversation_id)
            )

            return {
                "conversation_id": conversation_id,
                "agents": [state.agent_id for state in agent_states],
                "current_agent": current_agent,
                "agent_states": [state.dict() for state in agent_states],
                "collaboration_active": collaboration_session is not None,
                "collaboration_info": (
                    collaboration_session.dict() if collaboration_session else None
                ),
            }

        except Exception as e:
            logger.error(f"Error retrieving conversation state: {e}")
            raise

    def get_stats(self) -> dict[str, Any]:
        """
        Get agent manager statistics.

        Returns:
            dict: Service statistics
        """
        try:
            registry_stats = self.registry.get_stats()
            state_stats = self.state_manager.get_stats()
            handoff_stats = self.handoff_service.get_stats()
            collaboration_stats = self.collaboration_service.get_stats()
            performance_stats = self.performance_service.get_stats()

            return {
                "registry": registry_stats,
                "state_management": state_stats,
                "handoff": handoff_stats,
                "collaboration": collaboration_stats,
                "performance": performance_stats,
            }

        except Exception as e:
            logger.error(f"Error retrieving agent stats: {e}")
            raise


# Global agent manager instance
agent_manager = AgentManager()
