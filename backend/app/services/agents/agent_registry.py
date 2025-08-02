"""
Agent Registry Service.

This module provides agent registration and management functionality
extracted from the MultiAgentManager for better modularity.
"""

from datetime import UTC, datetime
from typing import Any

from loguru import logger
from pydantic import BaseModel

from backend.app.schemas.agent import AgentConfig


class AgentRegistryEntry(BaseModel):
    """Agent registry entry with metadata."""

    agent_id: str
    config: AgentConfig
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    usage_count: int = 0
    last_used: datetime | None = None

    model_config = {
        "validate_assignment": True,
        "extra": "forbid",
    }


class AgentRegistry:
    """Registry for managing available agents."""

    def __init__(self):
        """Initialize the agent registry."""
        self.agents: dict[str, AgentRegistryEntry] = {}
        self._initialize_default_agents()

    def _initialize_default_agents(self) -> None:
        """Initialize registry with default agents."""
        default_agents = {
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

        for agent_id, config in default_agents.items():
            self.add_agent(agent_id, config)

    def add_agent(self, agent_id: str, config: AgentConfig) -> AgentRegistryEntry:
        """
        Add an agent to the registry.

        Args:
            agent_id: Unique agent identifier
            config: Agent configuration

        Returns:
            AgentRegistryEntry: Created registry entry
        """
        if agent_id in self.agents:
            logger.warning(f"Agent {agent_id} already exists in registry")
            return self.agents[agent_id]

        entry = AgentRegistryEntry(
            agent_id=agent_id,
            config=config,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        self.agents[agent_id] = entry
        logger.info(f"Added agent {agent_id} to registry")
        return entry

    def remove_agent(self, agent_id: str) -> bool:
        """
        Remove an agent from the registry.

        Args:
            agent_id: Agent ID to remove

        Returns:
            bool: True if removed, False if not found
        """
        if agent_id in self.agents:
            del self.agents[agent_id]
            logger.info(f"Removed agent {agent_id} from registry")
            return True
        return False

    def get_agent(self, agent_id: str) -> AgentRegistryEntry | None:
        """
        Get an agent from the registry.

        Args:
            agent_id: Agent ID

        Returns:
            Optional[AgentRegistryEntry]: Agent entry if found
        """
        return self.agents.get(agent_id)

    def get_agent_config(self, agent_id: str) -> AgentConfig | None:
        """
        Get agent configuration.

        Args:
            agent_id: Agent ID

        Returns:
            Optional[AgentConfig]: Agent configuration if found
        """
        entry = self.get_agent(agent_id)
        return entry.config if entry else None

    def update_agent(self, agent_id: str, config: AgentConfig) -> bool:
        """
        Update an agent configuration.

        Args:
            agent_id: Agent ID
            config: New configuration

        Returns:
            bool: True if updated, False if not found
        """
        entry = self.get_agent(agent_id)
        if not entry:
            return False

        entry.config = config
        entry.updated_at = datetime.now(UTC)
        logger.info(f"Updated agent {agent_id} configuration")
        return True

    def list_agents(self, active_only: bool = True) -> list[dict[str, Any]]:
        """
        List all agents in the registry.

        Args:
            active_only: Whether to return only active agents

        Returns:
            List[dict]: List of agent information
        """
        agents = []
        for agent_id, entry in self.agents.items():
            if active_only and not entry.is_active:
                continue

            agents.append({
                "id": agent_id,
                "name": entry.config.name,
                "description": entry.config.description,
                "model": entry.config.model,
                "temperature": entry.config.temperature,
                "tools": entry.config.tools,
                "is_active": entry.is_active,
                "usage_count": entry.usage_count,
                "last_used": entry.last_used.isoformat() if entry.last_used else None,
                "created_at": entry.created_at.isoformat(),
                "updated_at": entry.updated_at.isoformat(),
            })

        return agents

    def activate_agent(self, agent_id: str) -> bool:
        """
        Activate an agent.

        Args:
            agent_id: Agent ID

        Returns:
            bool: True if activated, False if not found
        """
        entry = self.get_agent(agent_id)
        if not entry:
            return False

        entry.is_active = True
        entry.updated_at = datetime.now(UTC)
        logger.info(f"Activated agent {agent_id}")
        return True

    def deactivate_agent(self, agent_id: str) -> bool:
        """
        Deactivate an agent.

        Args:
            agent_id: Agent ID

        Returns:
            bool: True if deactivated, False if not found
        """
        entry = self.get_agent(agent_id)
        if not entry:
            return False

        entry.is_active = False
        entry.updated_at = datetime.now(UTC)
        logger.info(f"Deactivated agent {agent_id}")
        return True

    def record_usage(self, agent_id: str) -> bool:
        """
        Record agent usage.

        Args:
            agent_id: Agent ID

        Returns:
            bool: True if recorded, False if not found
        """
        entry = self.get_agent(agent_id)
        if not entry:
            return False

        entry.usage_count += 1
        entry.last_used = datetime.now(UTC)
        entry.updated_at = datetime.now(UTC)
        return True

    def get_stats(self) -> dict[str, Any]:
        """
        Get registry statistics.

        Returns:
            dict: Registry statistics
        """
        total_agents = len(self.agents)
        active_agents = sum(1 for entry in self.agents.values() if entry.is_active)
        total_usage = sum(entry.usage_count for entry in self.agents.values())

        return {
            "total_agents": total_agents,
            "active_agents": active_agents,
            "inactive_agents": total_agents - active_agents,
            "total_usage": total_usage,
            "most_used_agent": self._get_most_used_agent(),
        }

    def _get_most_used_agent(self) -> str | None:
        """Get the most used agent ID."""
        if not self.agents:
            return None

        return max(self.agents.items(), key=lambda x: x[1].usage_count)[0]


# Global agent registry instance
agent_registry = AgentRegistry()