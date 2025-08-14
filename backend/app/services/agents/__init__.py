"""
Agent Services Package.

This package contains all agent-related services with a modular architecture
for better maintainability and extensibility.
"""

from .agent_collaboration import AgentCollaborationService
from .agent_handoff import AgentHandoffService
from .agent_manager import AgentManager
from .agent_performance import AgentPerformanceService
from .agent_registry import AgentRegistry
from .agent_state import AgentStateManager




agent_manager = AgentManager()

__all__ = [
    "AgentRegistry",
    "AgentManager",
    "AgentHandoffService",
    "AgentCollaborationService",
    "AgentPerformanceService",
    "AgentStateManager",
]
