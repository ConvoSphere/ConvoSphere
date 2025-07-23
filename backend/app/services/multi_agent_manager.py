"""
Multi-Agent Conversation Manager.

This module provides multi-agent conversation management with
agent handoff, collaboration, and performance monitoring.
"""

from datetime import datetime
from typing import Any

from loguru import logger
from pydantic import BaseModel, Field, field_validator

from app.core.exceptions import ConversationError
from app.schemas.agent import AgentConfig, AgentResponse, AgentState


class AgentHandoffRequest(BaseModel):
    """Request for agent handoff."""

    from_agent_id: str = Field(..., description="Current agent ID")
    to_agent_id: str = Field(..., description="Target agent ID")
    conversation_id: str = Field(..., description="Conversation ID")
    user_id: str = Field(..., description="User ID")
    reason: str = Field(..., min_length=1, max_length=500, description="Handoff reason")
    context: dict[str, Any] = Field(default_factory=dict, description="Handoff context")
    priority: int = Field(default=1, ge=1, le=10, description="Handoff priority")

    @field_validator("from_agent_id")
    @classmethod
    def validate_from_agent(cls, v: str) -> str:
        """Validate from agent ID."""
        if not v or not v.strip():
            raise ValueError("From agent ID cannot be empty")
        return v.strip()

    @field_validator("to_agent_id")
    @classmethod
    def validate_to_agent(cls, v: str) -> str:
        """Validate to agent ID."""
        if not v or not v.strip():
            raise ValueError("To agent ID cannot be empty")
        return v.strip()

    model_config = {
        "validate_assignment": True,
        "extra": "forbid",
    }


class AgentCollaborationRequest(BaseModel):
    """Request for agent collaboration."""

    agent_ids: list[str] = Field(..., min_length=2, max_length=5, description="Agent IDs to collaborate")
    conversation_id: str = Field(..., description="Conversation ID")
    user_id: str = Field(..., description="User ID")
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
    shared_context: dict[str, Any] = Field(default_factory=dict, description="Shared context")

    @field_validator("agent_ids")
    @classmethod
    def validate_agent_ids(cls, v: list[str]) -> list[str]:
        """Validate agent IDs."""
        if len(set(v)) != len(v):
            raise ValueError("Agent IDs must be unique")
        return [aid.strip() for aid in v if aid.strip()]

    model_config = {
        "validate_assignment": True,
        "extra": "forbid",
    }


class AgentPerformanceMetrics(BaseModel):
    """Agent performance metrics."""

    agent_id: str = Field(..., description="Agent ID")
    conversation_id: str = Field(..., description="Conversation ID")
    response_time: float = Field(..., ge=0, description="Average response time")
    success_rate: float = Field(..., ge=0, le=100, description="Success rate percentage")
    user_satisfaction: float = Field(default=0.0, ge=0, le=5, description="User satisfaction score")
    tool_usage_count: int = Field(default=0, ge=0, description="Number of tools used")
    tokens_used: int = Field(default=0, ge=0, description="Total tokens used")
    error_count: int = Field(default=0, ge=0, description="Number of errors")
    created_at: datetime = Field(default_factory=datetime.now, description="Metrics timestamp")

    model_config = {
        "validate_assignment": True,
        "extra": "forbid",
    }


class MultiAgentConversation(BaseModel):
    """Multi-agent conversation state."""

    conversation_id: str = Field(..., description="Conversation ID")
    user_id: str = Field(..., description="User ID")
    agents: list[str] = Field(..., min_length=1, description="Participating agent IDs")
    current_agent: str = Field(..., description="Currently active agent")
    conversation_flow: list[dict[str, Any]] = Field(default_factory=list, description="Conversation flow")
    collaboration_mode: bool = Field(default=False, description="Whether in collaboration mode")
    shared_context: dict[str, Any] = Field(default_factory=dict, description="Shared context")
    performance_metrics: list[AgentPerformanceMetrics] = Field(default_factory=list, description="Performance metrics")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")

    model_config = {
        "validate_assignment": True,
        "extra": "forbid",
    }


class MultiAgentManager:
    """Manager for multi-agent conversations."""

    def __init__(self):
        self.active_conversations: dict[str, MultiAgentConversation] = {}
        self.agent_states: dict[str, AgentState] = {}
        self.performance_history: list[AgentPerformanceMetrics] = []
        self.handoff_history: list[dict[str, Any]] = []
        self.collaboration_history: list[dict[str, Any]] = []

        # Agent registry (in a real implementation, this would come from database)
        self.agent_registry: dict[str, AgentConfig] = {}

        # Initialize with some example agents
        self._initialize_agent_registry()

    def _initialize_agent_registry(self) -> None:
        """Initialize agent registry with example agents."""
        self.agent_registry = {
            "general_assistant": AgentConfig(
                name="General Assistant",
                description="General purpose AI assistant",
                system_prompt="You are a helpful general assistant.",
                tools=["web_search", "calculator"],
                model="gpt-4",
                temperature=0.7,
            ),
            "code_expert": AgentConfig(
                name="Code Expert",
                description="Specialized in programming and code analysis",
                system_prompt="You are a programming expert. Help with code-related questions.",
                tools=["code_analyzer", "file_reader"],
                model="gpt-4",
                temperature=0.3,
            ),
            "data_analyst": AgentConfig(
                name="Data Analyst",
                description="Specialized in data analysis and visualization",
                system_prompt="You are a data analysis expert. Help with data-related questions.",
                tools=["data_analyzer", "chart_generator"],
                model="gpt-4",
                temperature=0.5,
            ),
            "creative_writer": AgentConfig(
                name="Creative Writer",
                description="Specialized in creative writing and content generation",
                system_prompt="You are a creative writing expert. Help with writing tasks.",
                tools=["text_generator", "style_analyzer"],
                model="gpt-4",
                temperature=0.9,
            ),
        }

    async def create_multi_agent_conversation(
        self,
        conversation_id: str,
        user_id: str,
        initial_agent: str,
        additional_agents: list[str] | None = None,
    ) -> MultiAgentConversation:
        """
        Create a new multi-agent conversation.

        Args:
            conversation_id: Conversation ID
            user_id: User ID
            initial_agent: Initial agent ID
            additional_agents: Additional agent IDs

        Returns:
            MultiAgentConversation: Created conversation

        Raises:
            ConversationError: If conversation creation fails
        """
        try:
            # Validate agents
            all_agents = [initial_agent] + (additional_agents or [])
            for agent_id in all_agents:
                if agent_id not in self.agent_registry:
                    raise ConversationError(f"Agent {agent_id} not found in registry")

            # Create conversation
            conversation = MultiAgentConversation(
                conversation_id=conversation_id,
                user_id=user_id,
                agents=all_agents,
                current_agent=initial_agent,
            )

            # Initialize agent states
            for agent_id in all_agents:
                self.agent_states[f"{conversation_id}:{agent_id}"] = AgentState(
                    agent_id=agent_id,
                    conversation_id=conversation_id,
                    current_step=0,
                    total_steps=1,
                    status="idle",
                    last_activity=datetime.now(),
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                )

            self.active_conversations[conversation_id] = conversation

            logger.info(f"Created multi-agent conversation {conversation_id} with agents: {all_agents}")
            return conversation

        except Exception as e:
            raise ConversationError(f"Failed to create multi-agent conversation: {str(e)}")

    async def handoff_agent(
        self,
        request: AgentHandoffRequest,
    ) -> MultiAgentConversation:
        """
        Handoff conversation to another agent.

        Args:
            request: Handoff request

        Returns:
            MultiAgentConversation: Updated conversation

        Raises:
            ConversationError: If handoff fails
        """
        try:
            conversation = self.active_conversations.get(request.conversation_id)
            if not conversation:
                raise ConversationError(f"Conversation {request.conversation_id} not found")

            # Validate agents
            if request.from_agent_id not in conversation.agents:
                raise ConversationError(f"From agent {request.from_agent_id} not in conversation")

            if request.to_agent_id not in conversation.agents:
                raise ConversationError(f"To agent {request.to_agent_id} not in conversation")

            # Update conversation
            old_agent = conversation.current_agent
            conversation.current_agent = request.to_agent_id
            conversation.updated_at = datetime.now()

            # Add to conversation flow
            handoff_event = {
                "type": "handoff",
                "from_agent": request.from_agent_id,
                "to_agent": request.to_agent_id,
                "reason": request.reason,
                "context": request.context,
                "timestamp": datetime.now().isoformat(),
            }
            conversation.conversation_flow.append(handoff_event)

            # Update agent states
            from_state_key = f"{request.conversation_id}:{request.from_agent_id}"
            to_state_key = f"{request.conversation_id}:{request.to_agent_id}"

            if from_state_key in self.agent_states:
                self.agent_states[from_state_key].status = "idle"
                self.agent_states[from_state_key].updated_at = datetime.now()

            if to_state_key in self.agent_states:
                self.agent_states[to_state_key].status = "active"
                self.agent_states[to_state_key].last_activity = datetime.now()
                self.agent_states[to_state_key].updated_at = datetime.now()

            # Record handoff
            self.handoff_history.append({
                "conversation_id": request.conversation_id,
                "from_agent": request.from_agent_id,
                "to_agent": request.to_agent_id,
                "reason": request.reason,
                "timestamp": datetime.now(),
            })

            logger.info(f"Handoff from {old_agent} to {request.to_agent_id} in conversation {request.conversation_id}")
            return conversation

        except Exception as e:
            raise ConversationError(f"Failed to handoff agent: {str(e)}")

    async def start_collaboration(
        self,
        request: AgentCollaborationRequest,
    ) -> MultiAgentConversation:
        """
        Start agent collaboration.

        Args:
            request: Collaboration request

        Returns:
            MultiAgentConversation: Updated conversation

        Raises:
            ConversationError: If collaboration fails
        """
        try:
            conversation = self.active_conversations.get(request.conversation_id)
            if not conversation:
                raise ConversationError(f"Conversation {request.conversation_id} not found")

            # Validate all agents are in conversation
            for agent_id in request.agent_ids:
                if agent_id not in conversation.agents:
                    raise ConversationError(f"Agent {agent_id} not in conversation")

            # Update conversation for collaboration
            conversation.collaboration_mode = True
            conversation.shared_context.update(request.shared_context)
            conversation.updated_at = datetime.now()

            # Add collaboration event to flow
            collaboration_event = {
                "type": "collaboration_start",
                "agents": request.agent_ids,
                "collaboration_type": request.collaboration_type,
                "coordination_strategy": request.coordination_strategy,
                "timestamp": datetime.now().isoformat(),
            }
            conversation.conversation_flow.append(collaboration_event)

            # Update agent states for collaboration
            for agent_id in request.agent_ids:
                state_key = f"{request.conversation_id}:{agent_id}"
                if state_key in self.agent_states:
                    self.agent_states[state_key].status = "collaborating"
                    self.agent_states[state_key].updated_at = datetime.now()

            # Record collaboration
            self.collaboration_history.append({
                "conversation_id": request.conversation_id,
                "agents": request.agent_ids,
                "collaboration_type": request.collaboration_type,
                "timestamp": datetime.now(),
            })

            logger.info(f"Started collaboration between {request.agent_ids} in conversation {request.conversation_id}")
            return conversation

        except Exception as e:
            raise ConversationError(f"Failed to start collaboration: {str(e)}")

    async def get_agent_response(
        self,
        conversation_id: str,
        user_message: str,
        user_id: str,
        target_agent: str | None = None,
    ) -> AgentResponse:
        """
        Get response from current or specified agent.

        Args:
            conversation_id: Conversation ID
            user_message: User message
            user_id: User ID
            target_agent: Specific agent to respond (optional)

        Returns:
            AgentResponse: Agent response

        Raises:
            ConversationError: If response generation fails
        """
        try:
            conversation = self.active_conversations.get(conversation_id)
            if not conversation:
                raise ConversationError(f"Conversation {conversation_id} not found")

            # Determine which agent should respond
            agent_id = target_agent or conversation.current_agent
            if agent_id not in conversation.agents:
                raise ConversationError(f"Agent {agent_id} not in conversation")

            # Get agent configuration
            agent_config = self.agent_registry.get(agent_id)
            if not agent_config:
                raise ConversationError(f"Agent {agent_id} configuration not found")

            # Update agent state
            state_key = f"{conversation_id}:{agent_id}"
            if state_key in self.agent_states:
                self.agent_states[state_key].status = "processing"
                self.agent_states[state_key].last_activity = datetime.now()
                self.agent_states[state_key].updated_at = datetime.now()

            # Generate response (simplified - in real implementation, this would call AI service)
            start_time = datetime.now()

            # Simulate AI response generation
            response_content = f"Response from {agent_config.name}: {user_message}"

            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()

            # Create response
            response = AgentResponse(
                content=response_content,
                model_used=agent_config.model,
                tokens_used=len(response_content.split()),  # Simplified token counting
                processing_time=processing_time,
                confidence=0.9,  # Simplified confidence
            )

            # Update agent state
            if state_key in self.agent_states:
                self.agent_states[state_key].status = "idle"
                self.agent_states[state_key].updated_at = datetime.now()

            # Record performance metrics
            metrics = AgentPerformanceMetrics(
                agent_id=agent_id,
                conversation_id=conversation_id,
                response_time=processing_time,
                success_rate=100.0,  # Simplified
                tokens_used=response.tokens_used,
                error_count=0,
            )
            conversation.performance_metrics.append(metrics)
            self.performance_history.append(metrics)

            # Add to conversation flow
            flow_event = {
                "type": "agent_response",
                "agent_id": agent_id,
                "user_message": user_message,
                "agent_response": response_content,
                "processing_time": processing_time,
                "timestamp": datetime.now().isoformat(),
            }
            conversation.conversation_flow.append(flow_event)

            return response

        except Exception as e:
            raise ConversationError(f"Failed to get agent response: {str(e)}")

    def get_conversation_state(self, conversation_id: str) -> MultiAgentConversation | None:
        """Get conversation state."""
        return self.active_conversations.get(conversation_id)

    def get_agent_state(self, conversation_id: str, agent_id: str) -> AgentState | None:
        """Get agent state for a conversation."""
        state_key = f"{conversation_id}:{agent_id}"
        return self.agent_states.get(state_key)

    def get_performance_metrics(
        self,
        agent_id: str | None = None,
        conversation_id: str | None = None,
        limit: int = 100,
    ) -> list[AgentPerformanceMetrics]:
        """Get performance metrics with optional filtering."""
        metrics = self.performance_history.copy()

        if agent_id:
            metrics = [m for m in metrics if m.agent_id == agent_id]

        if conversation_id:
            metrics = [m for m in metrics if m.conversation_id == conversation_id]

        # Sort by timestamp (most recent first)
        metrics.sort(key=lambda x: x.created_at, reverse=True)

        return metrics[:limit]

    def get_handoff_history(
        self,
        conversation_id: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Get handoff history with optional filtering."""
        history = self.handoff_history.copy()

        if conversation_id:
            history = [h for h in history if h["conversation_id"] == conversation_id]

        # Sort by timestamp (most recent first)
        history.sort(key=lambda x: x["timestamp"], reverse=True)

        return history[:limit]

    def get_collaboration_history(
        self,
        conversation_id: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Get collaboration history with optional filtering."""
        history = self.collaboration_history.copy()

        if conversation_id:
            history = [h for h in history if h["conversation_id"] == conversation_id]

        # Sort by timestamp (most recent first)
        history.sort(key=lambda x: x["timestamp"], reverse=True)

        return history[:limit]

    def get_available_agents(self) -> list[dict[str, Any]]:
        """Get list of available agents."""
        agents = []
        for agent_id, config in self.agent_registry.items():
            agents.append({
                "id": agent_id,
                "name": config.name,
                "description": config.description,
                "model": config.model,
                "temperature": config.temperature,
                "tools": config.tools,
            })
        return agents

    def add_agent_to_registry(self, agent_id: str, config: AgentConfig) -> None:
        """Add agent to registry."""
        self.agent_registry[agent_id] = config
        logger.info(f"Added agent {agent_id} to registry")

    def remove_agent_from_registry(self, agent_id: str) -> None:
        """Remove agent from registry."""
        if agent_id in self.agent_registry:
            del self.agent_registry[agent_id]
            logger.info(f"Removed agent {agent_id} from registry")

    def get_stats(self) -> dict[str, Any]:
        """Get multi-agent manager statistics."""
        total_conversations = len(self.active_conversations)
        total_agents = len(self.agent_registry)
        total_handoffs = len(self.handoff_history)
        total_collaborations = len(self.collaboration_history)

        return {
            "active_conversations": total_conversations,
            "registered_agents": total_agents,
            "total_handoffs": total_handoffs,
            "total_collaborations": total_collaborations,
            "performance_metrics_count": len(self.performance_history),
        }


# Global multi-agent manager instance
multi_agent_manager = MultiAgentManager()
