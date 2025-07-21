"""
Page factory for consistent page creation and management.
"""

from collections.abc import Callable
from typing import Any

from .assistants import AssistantsPage
from .chat import ChatPage
from .conversations import ConversationsPage
from .dashboard import DashboardPage
from .knowledge_base import AdvancedKnowledgeBasePage
from .settings import AdvancedSettingsPage
from .tools import AdvancedToolsPage


# Page factory functions
def create_dashboard_page() -> DashboardPage:
    """Create dashboard page instance."""
    return DashboardPage()


def create_assistants_page() -> AssistantsPage:
    """Create assistants page instance."""
    return AssistantsPage()


def create_conversations_page() -> ConversationsPage:
    """Create conversations page instance."""
    return ConversationsPage()


def create_tools_page() -> AdvancedToolsPage:
    """Create tools page instance."""
    return AdvancedToolsPage()


def create_knowledge_base_page() -> AdvancedKnowledgeBasePage:
    """Create knowledge base page instance."""
    return AdvancedKnowledgeBasePage()


def create_settings_page() -> AdvancedSettingsPage:
    """Create settings page instance."""
    return AdvancedSettingsPage()


def create_chat_page() -> ChatPage:
    """Create chat page instance."""
    return ChatPage()


# Export all page creation functions
__all__ = [
    "create_dashboard_page",
    "create_assistants_page",
    "create_conversations_page",
    "create_tools_page",
    "create_knowledge_base_page",
    "create_settings_page",
    "create_chat_page",
]
