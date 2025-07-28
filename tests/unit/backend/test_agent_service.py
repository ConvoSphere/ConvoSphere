"""
Unit tests for AgentService.

This module tests the agent service functionality including
agent management, handoffs, collaboration, and performance monitoring.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

from backend.app.schemas.agent import (
    AgentConfig,
    AgentCreate,
    AgentUpdate,
    AgentHandoffRequest,
    AgentCollaborationRequest,
    AgentPerformanceMetrics,
)
from backend.app.services.agent_service import AgentService


class TestAgentService:
    """Test agent service functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_db = MagicMock()
        self.service = AgentService(self.mock_db)

    @pytest.mark.asyncio
    async def test_get_available_agents(self):
        """Test retrieving available agents."""
        # Mock the multi_agent_manager
        mock_agents = [
            {
                "id": "general_assistant",
                "name": "General Assistant",
                "description": "General purpose AI assistant",
                "model": "gpt-4",
                "temperature": 0.7,
                "tools": ["web_search", "calculator"],
            }
        ]
        self.service.multi_agent_manager.get_available_agents.return_value = mock_agents

        result = await self.service.get_available_agents()

        assert result == mock_agents
        self.service.multi_agent_manager.get_available_agents.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_agent(self):
        """Test agent creation."""
        # Create test data
        agent_config = AgentConfig(
            name="Test Agent",
            description="A test agent",
            system_prompt="You are a test agent.",
            tools=["test_tool"],
            model="gpt-4",
            temperature=0.7,
        )
        agent_create = AgentCreate(
            config=agent_config,
            user_id=UUID("12345678-1234-5678-9abc-123456789abc"),
            is_public=False,
            is_template=False,
        )

        # Mock the registry
        self.service.multi_agent_manager.agent_registry = {}
        self.service.multi_agent_manager.add_agent_to_registry = MagicMock()

        result = await self.service.create_agent(agent_create)

        assert result.config.name == "Test Agent"
        assert result.user_id == agent_create.user_id
        assert result.is_public == False
        self.service.multi_agent_manager.add_agent_to_registry.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_agent(self):
        """Test agent update."""
        agent_id = "test_agent"
        agent_update = AgentUpdate(
            name="Updated Agent",
            description="Updated description",
            temperature=0.5,
        )

        # Mock existing agent config
        existing_config = AgentConfig(
            name="Original Agent",
            description="Original description",
            system_prompt="Original prompt",
            tools=[],
            model="gpt-4",
            temperature=0.7,
        )
        self.service.multi_agent_manager.agent_registry = {agent_id: existing_config}

        result = await self.service.update_agent(agent_id, agent_update)

        assert result is not None
        assert result.config.name == "Updated Agent"
        assert result.config.description == "Updated description"
        assert result.config.temperature == 0.5

    @pytest.mark.asyncio
    async def test_update_agent_not_found(self):
        """Test updating non-existent agent."""
        agent_id = "non_existent"
        agent_update = AgentUpdate(name="Updated Agent")

        self.service.multi_agent_manager.agent_registry = {}

        result = await self.service.update_agent(agent_id, agent_update)

        assert result is None

    @pytest.mark.asyncio
    async def test_delete_agent(self):
        """Test agent deletion."""
        agent_id = "test_agent"
        self.service.multi_agent_manager.agent_registry = {agent_id: MagicMock()}
        self.service.multi_agent_manager.remove_agent_from_registry = MagicMock()

        result = await self.service.delete_agent(agent_id)

        assert result is True
        self.service.multi_agent_manager.remove_agent_from_registry.assert_called_once_with(agent_id)

    @pytest.mark.asyncio
    async def test_delete_agent_not_found(self):
        """Test deleting non-existent agent."""
        agent_id = "non_existent"
        self.service.multi_agent_manager.agent_registry = {}

        result = await self.service.delete_agent(agent_id)

        assert result is False

    @pytest.mark.asyncio
    async def test_handoff_agent(self):
        """Test agent handoff."""
        handoff_request = AgentHandoffRequest(
            from_agent_id="agent1",
            to_agent_id="agent2",
            conversation_id="conv123",
            user_id="user123",
            reason="Test handoff",
            context={},
            priority=1,
        )

        # Mock the multi_agent_manager response
        mock_conversation = MagicMock()
        mock_conversation.dict.return_value = {"conversation_id": "conv123"}
        self.service.multi_agent_manager.handoff_agent = AsyncMock(return_value=mock_conversation)

        result = await self.service.handoff_agent(handoff_request)

        assert result["success"] is True
        assert result["handoff_info"]["from_agent"] == "agent1"
        assert result["handoff_info"]["to_agent"] == "agent2"
        self.service.multi_agent_manager.handoff_agent.assert_called_once_with(handoff_request)

    @pytest.mark.asyncio
    async def test_start_collaboration(self):
        """Test agent collaboration."""
        collaboration_request = AgentCollaborationRequest(
            agent_ids=["agent1", "agent2"],
            conversation_id="conv123",
            user_id="user123",
            collaboration_type="parallel",
            coordination_strategy="round_robin",
            shared_context={},
        )

        # Mock the multi_agent_manager response
        mock_conversation = MagicMock()
        mock_conversation.dict.return_value = {"conversation_id": "conv123"}
        self.service.multi_agent_manager.start_collaboration = AsyncMock(return_value=mock_conversation)

        result = await self.service.start_collaboration(collaboration_request)

        assert result["success"] is True
        assert result["collaboration_info"]["agents"] == ["agent1", "agent2"]
        assert result["collaboration_info"]["type"] == "parallel"
        self.service.multi_agent_manager.start_collaboration.assert_called_once_with(collaboration_request)

    @pytest.mark.asyncio
    async def test_get_agent_performance(self):
        """Test getting agent performance metrics."""
        agent_id = "test_agent"
        conversation_id = "conv123"

        # Mock performance metrics
        mock_metrics = [
            AgentPerformanceMetrics(
                agent_id=agent_id,
                conversation_id=conversation_id,
                response_time=1.5,
                success_rate=95.0,
                user_satisfaction=4.5,
                tool_usage_count=3,
                tokens_used=1500,
                error_count=0,
            )
        ]
        self.service.multi_agent_manager.get_performance_metrics.return_value = mock_metrics

        result = await self.service.get_agent_performance(agent_id, conversation_id)

        assert len(result) == 1
        assert result[0].agent_id == agent_id
        assert result[0].response_time == 1.5
        self.service.multi_agent_manager.get_performance_metrics.assert_called_once_with(
            agent_id=agent_id,
            conversation_id=conversation_id,
            limit=100
        )

    @pytest.mark.asyncio
    async def test_get_agent_state(self):
        """Test getting agent state."""
        conversation_id = "conv123"
        agent_id = "test_agent"

        # Mock agent state
        mock_state = MagicMock()
        mock_state.dict.return_value = {
            "agent_id": agent_id,
            "conversation_id": conversation_id,
            "status": "active"
        }
        self.service.multi_agent_manager.get_agent_state.return_value = mock_state

        result = await self.service.get_agent_state(conversation_id, agent_id)

        assert result["agent_id"] == agent_id
        assert result["status"] == "active"
        self.service.multi_agent_manager.get_agent_state.assert_called_once_with(conversation_id, agent_id)

    @pytest.mark.asyncio
    async def test_get_agent_state_not_found(self):
        """Test getting non-existent agent state."""
        conversation_id = "conv123"
        agent_id = "test_agent"

        self.service.multi_agent_manager.get_agent_state.return_value = None

        result = await self.service.get_agent_state(conversation_id, agent_id)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_conversation_state(self):
        """Test getting conversation state."""
        conversation_id = "conv123"

        # Mock conversation state
        mock_state = MagicMock()
        mock_state.dict.return_value = {
            "conversation_id": conversation_id,
            "current_agent": "agent1",
            "collaboration_mode": False
        }
        self.service.multi_agent_manager.get_conversation_state.return_value = mock_state

        result = await self.service.get_conversation_state(conversation_id)

        assert result["conversation_id"] == conversation_id
        assert result["current_agent"] == "agent1"
        self.service.multi_agent_manager.get_conversation_state.assert_called_once_with(conversation_id)

    def test_get_stats(self):
        """Test getting agent service statistics."""
        # Mock stats
        mock_stats = {
            "active_conversations": 5,
            "registered_agents": 10,
            "total_handoffs": 3,
            "total_collaborations": 2,
        }
        self.service.multi_agent_manager.get_stats.return_value = mock_stats

        result = self.service.get_stats()

        assert result == mock_stats
        self.service.multi_agent_manager.get_stats.assert_called_once()