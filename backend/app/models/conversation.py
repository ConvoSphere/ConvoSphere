"""
Conversation and Message models for chat functionality.

This module defines the Conversation and Message models for managing
chat conversations between users and AI assistants.
"""

from enum import Enum
from typing import Optional, Dict, Any
from sqlalchemy import Column, String, Text, Boolean, JSON, Enum as SQLEnum, ForeignKey, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from .base import Base


class MessageRole(str, Enum):
    """Message role enumeration."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class MessageType(str, Enum):
    """Message type enumeration."""
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    AUDIO = "audio"
    VIDEO = "video"


class Conversation(Base):
    """Conversation model for chat sessions."""
    
    __tablename__ = "conversations"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic information
    title = Column(String(500), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Relationships
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="conversations")
    
    assistant_id = Column(UUID(as_uuid=True), ForeignKey("assistants.id"), nullable=False)
    assistant = relationship("Assistant", back_populates="conversations")
    
    # Status and metadata
    is_active = Column(Boolean, default=True, nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)
    archived_at = Column(DateTime, nullable=True)
    
    # Statistics
    message_count = Column(Integer, default=0, nullable=False)
    total_tokens = Column(Integer, default=0, nullable=False)
    
    # Metadata
    conversation_metadata = Column(JSON, default=dict)  # Additional metadata including context
    
    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        """String representation of the conversation."""
        return f"<Conversation(id={self.id}, title='{self.title}')>"
    
    @property
    def last_message(self) -> Optional["Message"]:
        """Get the last message in the conversation."""
        if self.messages:
            return max(self.messages, key=lambda m: m.created_at)
        return None
    
    def update_title_from_messages(self):
        """Update conversation title from first user message."""
        if not self.messages:
            return
        
        first_user_message = next(
            (msg for msg in self.messages if msg.role == MessageRole.USER),
            None
        )
        
        if first_user_message:
            # Generate title from first message (first 100 characters)
            title = first_user_message.content[:100]
            if len(first_user_message.content) > 100:
                title += "..."
            self.title = title
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert conversation to dictionary."""
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "user_id": str(self.user_id),
            "assistant_id": str(self.assistant_id),
            "is_active": self.is_active,
            "is_archived": self.is_archived,
            "archived_at": self.archived_at.isoformat() if self.archived_at else None,
            "message_count": self.message_count,
            "total_tokens": self.total_tokens,
            "metadata": self.conversation_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Message(Base):
    """Message model for individual chat messages."""
    
    __tablename__ = "messages"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Content
    content = Column(Text, nullable=False)
    role = Column(SQLEnum(MessageRole), nullable=False)
    message_type = Column(SQLEnum(MessageType), default=MessageType.TEXT, nullable=False)
    
    # Relationships
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    conversation = relationship("Conversation", back_populates="messages")
    
    # Tool information (for tool messages)
    tool_name = Column(String(200), nullable=True)
    tool_input = Column(JSON, nullable=True)
    tool_output = Column(JSON, nullable=True)
    
    # Token information
    tokens_used = Column(Integer, default=0, nullable=False)
    model_used = Column(String(100), nullable=True)
    
    # Metadata
    message_metadata = Column(JSON, default=dict)  # Additional metadata
    
    # Relationships
    reactions = relationship("MessageReaction", back_populates="message", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        """String representation of the message."""
        return f"<Message(id={self.id}, role='{self.role}', content='{self.content[:50]}...')>"
    
    @property
    def is_from_user(self) -> bool:
        """Check if message is from user."""
        return self.role == MessageRole.USER
    
    @property
    def is_from_assistant(self) -> bool:
        """Check if message is from assistant."""
        return self.role == MessageRole.ASSISTANT
    
    @property
    def is_tool_message(self) -> bool:
        """Check if message is a tool message."""
        return self.role == MessageRole.TOOL
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "id": str(self.id),
            "content": self.content,
            "role": self.role.value,
            "message_type": self.message_type.value,
            "conversation_id": str(self.conversation_id),
            "tool_name": self.tool_name,
            "tool_input": self.tool_input,
            "tool_output": self.tool_output,
            "tokens_used": self.tokens_used,
            "model_used": self.model_used,
            "metadata": self.message_metadata,
            "reactions": [reaction.to_dict() for reaction in self.reactions],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class MessageReaction(Base):
    """Message reaction model for emoji reactions on messages."""
    
    __tablename__ = "message_reactions"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Reaction details
    emoji = Column(String(10), nullable=False)  # Emoji character
    
    # Relationships
    message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id"), nullable=False)
    message = relationship("Message", back_populates="reactions")
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user = relationship("User")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        """String representation of the message reaction."""
        return f"<MessageReaction(id={self.id}, emoji='{self.emoji}', message_id={self.message_id})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message reaction to dictionary."""
        return {
            "id": str(self.id),
            "emoji": self.emoji,
            "message_id": str(self.message_id),
            "user_id": str(self.user_id),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        } 