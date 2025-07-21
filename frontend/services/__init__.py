"""
Services package for the AI Assistant Platform frontend.

This package contains service modules for API communication,
state management, and business logic.
"""

from .api import APIClient, APIResponse, api_client
from .assistant_service import AssistantService
from .auth_service import AuthService
from .conversation_service import ConversationService

__all__ = [
    "api_client",
    "APIClient",
    "APIResponse",
    "AuthService",
    "AssistantService",
    "ConversationService",
]
