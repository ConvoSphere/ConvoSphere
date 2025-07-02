"""
Models package for the AI Assistant Platform.

This package contains all database models for the platform.
"""

from .base import Base
from .user import User, UserRole
from .assistant import Assistant, AssistantStatus
from .conversation import Conversation, Message, MessageRole, MessageType
from .tool import Tool, ToolCategory
from .audit import AuditLog, AuditEventType, AuditSeverity
from .knowledge import Document, DocumentChunk, SearchQuery

__all__ = [
    "Base",
    "User",
    "UserRole",
    "Assistant",
    "AssistantStatus",
    "Conversation",
    "Message",
    "MessageRole",
    "MessageType",
    "Tool",
    "ToolCategory",
    "AuditLog",
    "AuditEventType",
    "AuditSeverity",
    "Document",
    "DocumentChunk",
    "SearchQuery",
] 