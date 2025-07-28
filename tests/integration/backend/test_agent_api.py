"""
Integration tests for Agent API endpoints.

This module tests the agent API endpoints with database integration
and real service interactions.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch

from backend.app.main import app
from backend.app.schemas.agent import AgentConfig, AgentCreate, AgentUpdate


class TestAgentAPI:
    """Test agent API endpoints."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
        self.test_user_id = "test-user-123"
        self.test_conversation_id = "test-conv-123"

    @patch("backend.app.api.v1.endpoints.agents.get_current_user_id")
    @patch("backend.app.api.v1.endpoints.agents.AgentService")
    def test_get_available_agents(self, mock_service_class, mock_get_user):
        """Test getting available agents."""
        mock_get_user.return_value = self.test_user_id
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        
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
        mock_service.get_available_agents = AsyncMock(return_value=mock_agents)

        response = self.client.get("/api/v1/agents/")

        assert response.status_code == 200
        assert response.json() == mock_agents
        mock_service.get_available_agents.assert_called_once()

    @patch("backend.app.api.v1.endpoints.agents.get_current_user_id")
    @patch("backend.app.api.v1.endpoints.agents.AgentService")
    def test_create_agent(self, mock_service_class, mock_get_user):
        """Test creating a new agent."""
        mock_get_user.return_value = self.test_user_id
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service

        agent_data = {
            "config": {
                "name": "Test Agent",
                "description": "A test agent",
                "system_prompt": "You are a test agent.",
                "tools": ["test_tool"],
                "model": "gpt-4",
                "temperature": 0.7,
            },
            "user_id": "12345678-1234-5678-9abc-123456789abc",
            "is_public": False,
            "is_template": False,
        }

        mock_response = MagicMock()
        mock_response.dict.return_value = {
            "id": "custom_1",
            "config": agent_data["config"],
            "user_id": agent_data["user_id"],
            "is_public": False,
            "is_template": False,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        }
        mock_service.create_agent = AsyncMock(return_value=mock_response)

        response = self.client.post("/api/v1/agents/", json=agent_data)

        assert response.status_code == 200
        mock_service.create_agent.assert_called_once()

    @patch("backend.app.api.v1.endpoints.agents.get_current_user_id")
    @patch("backend.app.api.v1.endpoints.agents.AgentService")
    def test_update_agent(self, mock_service_class, mock_get_user):
        """Test updating an agent."""
        mock_get_user.return_value = self.test_user_id
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service

        agent_id = "test_agent"
        update_data = {
            "name": "Updated Agent",
            "description": "Updated description",
            "temperature": 0.5,
        }

        mock_response = MagicMock()
        mock_response.dict.return_value = {
            "id": agent_id,
            "config": {**update_data, "system_prompt": "Original prompt"},
            "user_id": "12345678-1234-5678-9abc-123456789abc",
            "is_public": False,
            "is_template": False,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        }
        mock_service.update_agent = AsyncMock(return_value=mock_response)

        response = self.client.put(f"/api/v1/agents/{agent_id}", json=update_data)

        assert response.status_code == 200
        mock_service.update_agent.assert_called_once()

    @patch("backend.app.api.v1.endpoints.agents.get_current_user_id")
    @patch("backend.app.api.v1.endpoints.agents.AgentService")
    def test_update_agent_not_found(self, mock_service_class, mock_get_user):
        """Test updating non-existent agent."""
        mock_get_user.return_value = self.test_user_id
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service

        agent_id = "non_existent"
        update_data = {"name": "Updated Agent"}
        mock_service.update_agent = AsyncMock(return_value=None)

        response = self.client.put(f"/api/v1/agents/{agent_id}", json=update_data)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    @patch("backend.app.api.v1.endpoints.agents.get_current_user_id")
    @patch("backend.app.api.v1.endpoints.agents.AgentService")
    def test_delete_agent(self, mock_service_class, mock_get_user):
        """Test deleting an agent."""
        mock_get_user.return_value = self.test_user_id
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service

        agent_id = "test_agent"
        mock_service.delete_agent = AsyncMock(return_value=True)

        response = self.client.delete(f"/api/v1/agents/{agent_id}")

        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]
        mock_service.delete_agent.assert_called_once_with(agent_id)

    @patch("backend.app.api.v1.endpoints.agents.get_current_user_id")
    @patch("backend.app.api.v1.endpoints.agents.AgentService")
    def test_delete_agent_not_found(self, mock_service_class, mock_get_user):
        """Test deleting non-existent agent."""
        mock_get_user.return_value = self.test_user_id
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service

        agent_id = "non_existent"
        mock_service.delete_agent = AsyncMock(return_value=False)

        response = self.client.delete(f"/api/v1/agents/{agent_id}")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    @patch("backend.app.api.v1.endpoints.agents.get_current_user_id")
    @patch("backend.app.api.v1.endpoints.agents.AgentService")
    def test_handoff_agent(self, mock_service_class, mock_get_user):
        """Test agent handoff."""
        mock_get_user.return_value = self.test_user_id
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service

        handoff_data = {
            "from_agent_id": "agent1",
            "to_agent_id": "agent2",
            "reason": "Test handoff",
            "context": {},
            "priority": 1,
        }

        mock_response = {
            "success": True,
            "conversation": {"conversation_id": self.test_conversation_id},
            "handoff_info": {
                "from_agent": "agent1",
                "to_agent": "agent2",
                "reason": "Test handoff"
            }
        }
        mock_service.handoff_agent = AsyncMock(return_value=mock_response)

        response = self.client.post(
            "/api/v1/agents/handoff",
            json=handoff_data,
            params={"conversation_id": self.test_conversation_id}
        )

        assert response.status_code == 200
        assert response.json()["success"] is True
        mock_service.handoff_agent.assert_called_once()

    @patch("backend.app.api.v1.endpoints.agents.get_current_user_id")
    @patch("backend.app.api.v1.endpoints.agents.AgentService")
    def test_start_collaboration(self, mock_service_class, mock_get_user):
        """Test starting agent collaboration."""
        mock_get_user.return_value = self.test_user_id
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service

        collaboration_data = {
            "agent_ids": ["agent1", "agent2"],
            "collaboration_type": "parallel",
            "coordination_strategy": "round_robin",
            "shared_context": {},
        }

        mock_response = {
            "success": True,
            "conversation": {"conversation_id": self.test_conversation_id},
            "collaboration_info": {
                "agents": ["agent1", "agent2"],
                "type": "parallel",
                "strategy": "round_robin"
            }
        }
        mock_service.start_collaboration = AsyncMock(return_value=mock_response)

        response = self.client.post(
            "/api/v1/agents/collaborate",
            json=collaboration_data,
            params={"conversation_id": self.test_conversation_id}
        )

        assert response.status_code == 200
        assert response.json()["success"] is True
        mock_service.start_collaboration.assert_called_once()

    @patch("backend.app.api.v1.endpoints.agents.get_current_user_id")
    @patch("backend.app.api.v1.endpoints.agents.AgentService")
    def test_get_agent_performance(self, mock_service_class, mock_get_user):
        """Test getting agent performance metrics."""
        mock_get_user.return_value = self.test_user_id
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service

        agent_id = "test_agent"
        mock_metrics = [
            {
                "agent_id": agent_id,
                "conversation_id": self.test_conversation_id,
                "response_time": 1.5,
                "success_rate": 95.0,
                "user_satisfaction": 4.5,
                "tool_usage_count": 3,
                "tokens_used": 1500,
                "error_count": 0,
                "created_at": "2024-01-01T00:00:00",
            }
        ]
        mock_service.get_agent_performance = AsyncMock(return_value=mock_metrics)

        response = self.client.get(
            f"/api/v1/agents/{agent_id}/performance",
            params={"conversation_id": self.test_conversation_id}
        )

        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["agent_id"] == agent_id
        mock_service.get_agent_performance.assert_called_once()

    @patch("backend.app.api.v1.endpoints.agents.get_current_user_id")
    @patch("backend.app.api.v1.endpoints.agents.AgentService")
    def test_get_agent_state(self, mock_service_class, mock_get_user):
        """Test getting agent state."""
        mock_get_user.return_value = self.test_user_id
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service

        agent_id = "test_agent"
        mock_state = {
            "agent_id": agent_id,
            "conversation_id": self.test_conversation_id,
            "status": "active",
            "current_step": 1,
            "total_steps": 3,
        }
        mock_service.get_agent_state = AsyncMock(return_value=mock_state)

        response = self.client.get(
            f"/api/v1/agents/{agent_id}/state",
            params={"conversation_id": self.test_conversation_id}
        )

        assert response.status_code == 200
        assert response.json()["agent_id"] == agent_id
        assert response.json()["status"] == "active"
        mock_service.get_agent_state.assert_called_once()

    @patch("backend.app.api.v1.endpoints.agents.get_current_user_id")
    @patch("backend.app.api.v1.endpoints.agents.AgentService")
    def test_get_agent_state_not_found(self, mock_service_class, mock_get_user):
        """Test getting non-existent agent state."""
        mock_get_user.return_value = self.test_user_id
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service

        agent_id = "test_agent"
        mock_service.get_agent_state = AsyncMock(return_value=None)

        response = self.client.get(
            f"/api/v1/agents/{agent_id}/state",
            params={"conversation_id": self.test_conversation_id}
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    @patch("backend.app.api.v1.endpoints.agents.get_current_user_id")
    @patch("backend.app.api.v1.endpoints.agents.AgentService")
    def test_get_conversation_state(self, mock_service_class, mock_get_user):
        """Test getting conversation state."""
        mock_get_user.return_value = self.test_user_id
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service

        mock_state = {
            "conversation_id": self.test_conversation_id,
            "current_agent": "agent1",
            "collaboration_mode": False,
            "agents": ["agent1", "agent2"],
        }
        mock_service.get_conversation_state = AsyncMock(return_value=mock_state)

        response = self.client.get(f"/api/v1/agents/conversation/{self.test_conversation_id}/state")

        assert response.status_code == 200
        assert response.json()["conversation_id"] == self.test_conversation_id
        assert response.json()["current_agent"] == "agent1"
        mock_service.get_conversation_state.assert_called_once()

    @patch("backend.app.api.v1.endpoints.agents.get_current_user_id")
    @patch("backend.app.api.v1.endpoints.agents.AgentService")
    def test_get_agent_stats(self, mock_service_class, mock_get_user):
        """Test getting agent service statistics."""
        mock_get_user.return_value = self.test_user_id
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service

        mock_stats = {
            "active_conversations": 5,
            "registered_agents": 10,
            "total_handoffs": 3,
            "total_collaborations": 2,
        }
        mock_service.get_stats.return_value = mock_stats

        response = self.client.get("/api/v1/agents/stats")

        assert response.status_code == 200
        assert response.json() == mock_stats
        mock_service.get_stats.assert_called_once()