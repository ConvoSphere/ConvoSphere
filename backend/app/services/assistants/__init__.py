"""
Assistant Services Package.

This package contains all assistant-related services with a modular architecture
for better maintainability and extensibility.
"""

from .assistant_context import AssistantContextManager, assistant_context_manager
from .assistant_engine import AssistantEngine, assistant_engine
from .assistant_memory import AssistantMemoryManager, assistant_memory_manager
from .assistant_processor import AssistantProcessor, assistant_processor
from .assistant_response import AssistantResponseGenerator, assistant_response_generator
from .assistant_tools import AssistantToolsManager, assistant_tools_manager

__all__ = [
    "AssistantEngine",
    "AssistantContextManager",
    "AssistantResponseGenerator",
    "AssistantToolsManager",
    "AssistantMemoryManager",
    "AssistantProcessor",
    "assistant_engine",
    "assistant_context_manager",
    "assistant_response_generator",
    "assistant_tools_manager",
    "assistant_memory_manager",
    "assistant_processor",
]