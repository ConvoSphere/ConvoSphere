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

    # =============================================================================
    # FAST TESTS - Basic agent operations
    # =============================================================================

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_get_available_agents(self):
        """Fast test for retrieving available agents."""
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

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_create_agent(self):
        """Fast test for agent creation."""
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

        self.service.multi_agent_manager.agent_registry = {}
        self.service.multi_agent_manager.add_agent_to_registry = MagicMock()

        result = await self.service.create_agent(agent_create)

        assert result.config.name == "Test Agent"
        assert result.user_id == agent_create.user_id
        assert result.is_public == False
        self.service.multi_agent_manager.add_agent_to_registry.assert_called_once()

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_get_agent_state(self):
        """Fast test for getting agent state."""
        agent_id = "test_agent"
        mock_state = {
            "agent_id": agent_id,
            "status": "active",
            "current_task": "processing",
            "memory": {"context": "test context"}
        }
        self.service.multi_agent_manager.get_agent_state.return_value = mock_state

        result = await self.service.get_agent_state(agent_id)

        assert result == mock_state
        self.service.multi_agent_manager.get_agent_state.assert_called_once_with(agent_id)

    # =============================================================================
    # COMPREHENSIVE TESTS - Advanced agent operations and edge cases
    # =============================================================================

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_update_agent(self):
        """Comprehensive test for agent update."""
        agent_id = "test_agent"
        agent_update = AgentUpdate(
            name="Updated Agent",
            description="Updated description",
            temperature=0.5,
        )

        existing_config = AgentConfig(
            name="Original Agent",
            description="Original description",
            system_prompt="Original prompt",
            tools=[],
            model="gpt-4",
            temperature=0.7,
        )
        self.service.multi_agent_manager.get_agent_config.return_value = existing_config
        self.service.multi_agent_manager.update_agent_config = MagicMock()

        result = await self.service.update_agent(agent_id, agent_update)

        assert result is not None
        self.service.multi_agent_manager.update_agent_config.assert_called_once()

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_update_agent_not_found(self):
        """Comprehensive test for updating non-existent agent."""
        agent_id = "nonexistent_agent"
        agent_update = AgentUpdate(name="Updated Agent")
        
        self.service.multi_agent_manager.get_agent_config.return_value = None

        result = await self.service.update_agent(agent_id, agent_update)

        assert result is None

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_delete_agent(self):
        """Comprehensive test for agent deletion."""
        agent_id = "test_agent"
        self.service.multi_agent_manager.remove_agent_from_registry = MagicMock()
        self.service.multi_agent_manager.remove_agent_from_registry.return_value = True

        result = await self.service.delete_agent(agent_id)

        assert result is True
        self.service.multi_agent_manager.remove_agent_from_registry.assert_called_once_with(agent_id)

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_delete_agent_not_found(self):
        """Comprehensive test for deleting non-existent agent."""
        agent_id = "nonexistent_agent"
        self.service.multi_agent_manager.remove_agent_from_registry.return_value = False

        result = await self.service.delete_agent(agent_id)

        assert result is False

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_handoff_agent(self):
        """Comprehensive test for agent handoff."""
        handoff_request = AgentHandoffRequest(
            from_agent_id="agent_1",
            to_agent_id="agent_2",
            conversation_id="conv_123",
            reason="Specialized task",
            context="Current conversation context"
        )
        
        self.service.multi_agent_manager.handoff_conversation = MagicMock()
        self.service.multi_agent_manager.handoff_conversation.return_value = {
            "status": "handoff_completed",
            "new_agent_id": "agent_2"
        }

        result = await self.service.handoff_agent(handoff_request)

        assert result is not None
        assert result["status"] == "handoff_completed"
        self.service.multi_agent_manager.handoff_conversation.assert_called_once()

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_start_collaboration(self):
        """Comprehensive test for starting agent collaboration."""
        collaboration_request = AgentCollaborationRequest(
            agent_ids=["agent_1", "agent_2", "agent_3"],
            conversation_id="conv_123",
            collaboration_type="parallel",
            shared_context="Shared task context"
        )
        
        self.service.multi_agent_manager.start_collaboration = MagicMock()
        self.service.multi_agent_manager.start_collaboration.return_value = {
            "collaboration_id": "collab_456",
            "status": "started"
        }

        result = await self.service.start_collaboration(collaboration_request)

        assert result is not None
        assert result["collaboration_id"] == "collab_456"
        self.service.multi_agent_manager.start_collaboration.assert_called_once()

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_get_agent_performance(self):
        """Comprehensive test for getting agent performance metrics."""
        agent_id = "test_agent"
        mock_metrics = AgentPerformanceMetrics(
            agent_id=agent_id,
            total_conversations=100,
            successful_conversations=95,
            average_response_time=2.5,
            user_satisfaction_score=4.2,
            error_rate=0.05,
            tools_used=["web_search", "calculator"],
            model_usage={"gpt-4": 80, "gpt-3.5-turbo": 20}
        )
        
        self.service.multi_agent_manager.get_agent_performance.return_value = mock_metrics

        result = await self.service.get_agent_performance(agent_id)

        assert result == mock_metrics
        self.service.multi_agent_manager.get_agent_performance.assert_called_once_with(agent_id)

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_get_agent_state_not_found(self):
        """Comprehensive test for getting non-existent agent state."""
        agent_id = "nonexistent_agent"
        self.service.multi_agent_manager.get_agent_state.return_value = None

        result = await self.service.get_agent_state(agent_id)

        assert result is None

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_get_conversation_state(self):
        """Comprehensive test for getting conversation state."""
        conversation_id = "conv_123"
        mock_state = {
            "conversation_id": conversation_id,
            "current_agent": "agent_1",
            "agent_history": ["agent_1", "agent_2"],
            "status": "active",
            "context": "Conversation context"
        }
        
        self.service.multi_agent_manager.get_conversation_state.return_value = mock_state

        result = await self.service.get_conversation_state(conversation_id)

        assert result == mock_state
        self.service.multi_agent_manager.get_conversation_state.assert_called_once_with(conversation_id)

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_stats(self):
        """Fast test for getting agent statistics."""
        mock_stats = {
            "total_agents": 10,
            "active_agents": 8,
            "total_conversations": 150,
            "active_conversations": 25,
            "average_response_time": 2.1,
            "success_rate": 0.95
        }
        
        self.service.multi_agent_manager.get_stats.return_value = mock_stats

        result = self.service.get_stats()

        assert result == mock_stats
        self.service.multi_agent_manager.get_stats.assert_called_once()

    # =============================================================================
    # ERROR HANDLING TESTS
    # =============================================================================

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_create_agent_validation_error(self):
        """Comprehensive test for agent creation validation error."""
        invalid_agent_create = AgentCreate(
            config=None,  # Invalid config
            user_id=UUID("12345678-1234-5678-9abc-123456789abc"),
            is_public=False,
            is_template=False,
        )

        with pytest.raises(ValueError):
            await self.service.create_agent(invalid_agent_create)

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_handoff_agent_invalid_request(self):
        """Comprehensive test for invalid handoff request."""
        invalid_handoff = AgentHandoffRequest(
            from_agent_id="",  # Invalid empty ID
            to_agent_id="agent_2",
            conversation_id="conv_123",
            reason="Test",
            context="Context"
        )

        with pytest.raises(ValueError):
            await self.service.handoff_agent(invalid_handoff)

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_start_collaboration_empty_agents(self):
        """Comprehensive test for collaboration with empty agent list."""
        invalid_collaboration = AgentCollaborationRequest(
            agent_ids=[],  # Empty list
            conversation_id="conv_123",
            collaboration_type="parallel",
            shared_context="Context"
        )

        with pytest.raises(ValueError):
            await self.service.start_collaboration(invalid_collaboration)

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_get_agent_performance_not_found(self):
        """Comprehensive test for getting performance of non-existent agent."""
        agent_id = "nonexistent_agent"
        self.service.multi_agent_manager.get_agent_performance.return_value = None

        result = await self.service.get_agent_performance(agent_id)

        assert result is None