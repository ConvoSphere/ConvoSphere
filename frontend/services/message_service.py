"""
Message service for handling chat messages and conversation state.

This module provides functionality for managing messages, conversations,
and real-time chat features.
"""

import asyncio
import base64
import json
from datetime import datetime
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass, field
from enum import Enum

from .api import api_client
from .error_handler import handle_api_error, handle_network_error
from utils.helpers import generate_id, format_timestamp
from utils.validators import validate_message_data, sanitize_input
from .websocket_service import websocket_service


class MessageType(Enum):
    """Message types enumeration."""
    TEXT = "text"
    FILE = "file"
    TOOL = "tool"
    SYSTEM = "system"
    ERROR = "error"
    TYPING = "typing"


class MessageStatus(Enum):
    """Message status enumeration."""
    SENDING = "sending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    PROCESSING = "processing"


class MessageRole(Enum):
    """Message roles."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class FileAttachment:
    """File attachment data model."""
    id: str
    filename: str
    file_type: str
    file_size: int
    url: Optional[str] = None
    content: Optional[bytes] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ToolResult:
    """Tool execution result data model."""
    tool_name: str
    tool_id: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    execution_time: float
    status: str  # success, error, timeout
    error_message: Optional[str] = None


@dataclass
class Message:
    """Chat message model."""
    id: Optional[int] = None
    conversation_id: Optional[int] = None
    content: str = ""
    role: MessageRole = MessageRole.USER
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Conversation:
    """Conversation model."""
    id: Optional[int] = None
    title: str = ""
    assistant_id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    messages: List[Message] = field(default_factory=list)


@dataclass
class AdvancedMessage:
    """Advanced message data model with support for different types."""
    id: str
    conversation_id: str
    content: str
    role: str  # user, assistant, system
    message_type: MessageType
    status: MessageStatus
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
    file_attachments: Optional[List[FileAttachment]] = None
    tool_results: Optional[List[ToolResult]] = None
    reply_to: Optional[str] = None
    is_edited: bool = False
    edit_history: Optional[List[Dict[str, Any]]] = None


class MessageService:
    """Service for managing messages and conversations."""
    
    def __init__(self):
        """Initialize message service."""
        self.conversations: Dict[int, Conversation] = {}
        self.current_conversation_id: Optional[int] = None
        self.message_handlers: List[callable] = []
        self.conversation_handlers: List[callable] = []
        
        # Register WebSocket handlers
        websocket_service.on_message("chat_message")(self._handle_chat_message)
        websocket_service.on_message("typing_indicator")(self._handle_typing_indicator)
    
    def on_message(self, handler: callable):
        """Register message handler."""
        self.message_handlers.append(handler)
    
    def on_conversation_update(self, handler: callable):
        """Register conversation update handler."""
        self.conversation_handlers.append(handler)
    
    async def load_conversations(self) -> List[Conversation]:
        """Load user conversations from API."""
        try:
            response = await api_client.get_conversations()
            conversations = []
            
            for conv_data in response.get("items", []):
                conversation = Conversation(
                    id=conv_data.get("id"),
                    title=conv_data.get("title", ""),
                    assistant_id=conv_data.get("assistant_id"),
                    created_at=datetime.fromisoformat(conv_data.get("created_at", "")),
                    updated_at=datetime.fromisoformat(conv_data.get("updated_at", ""))
                )
                conversations.append(conversation)
                self.conversations[conversation.id] = conversation
            
            return conversations
            
        except Exception as e:
            print(f"Error loading conversations: {e}")
            return []
    
    async def load_messages(self, conversation_id: int) -> List[Message]:
        """Load messages for a conversation."""
        try:
            response = await api_client.get_messages(conversation_id)
            messages = []
            
            for msg_data in response.get("items", []):
                message = Message(
                    id=msg_data.get("id"),
                    conversation_id=conversation_id,
                    content=msg_data.get("content", ""),
                    role=MessageRole(msg_data.get("role", "user")),
                    timestamp=datetime.fromisoformat(msg_data.get("created_at", "")),
                    metadata=msg_data.get("metadata", {})
                )
                messages.append(message)
            
            # Update conversation messages
            if conversation_id in self.conversations:
                self.conversations[conversation_id].messages = messages
            
            return messages
            
        except Exception as e:
            print(f"Error loading messages: {e}")
            return []
    
    async def create_conversation(self, title: str, assistant_id: Optional[int] = None) -> Optional[Conversation]:
        """Create new conversation."""
        try:
            response = await api_client.create_conversation(title, assistant_id)
            
            conversation = Conversation(
                id=response.get("id"),
                title=title,
                assistant_id=assistant_id,
                created_at=datetime.fromisoformat(response.get("created_at", "")),
                updated_at=datetime.fromisoformat(response.get("updated_at", ""))
            )
            
            self.conversations[conversation.id] = conversation
            self._notify_conversation_handlers()
            
            return conversation
            
        except Exception as e:
            print(f"Error creating conversation: {e}")
            return None
    
    async def send_message(self, content: str, conversation_id: Optional[int] = None) -> Optional[Message]:
        """Send message to conversation."""
        conv_id = conversation_id or self.current_conversation_id
        
        if not conv_id:
            print("No conversation selected")
            return None
        
        try:
            # Create message locally
            message = Message(
                conversation_id=conv_id,
                content=content,
                role=MessageRole.USER,
                timestamp=datetime.now()
            )
            
            # Add to conversation
            if conv_id in self.conversations:
                self.conversations[conv_id].messages.append(message)
                self.conversations[conv_id].updated_at = datetime.now()
            
            # Send via API
            response = await api_client.send_message(conv_id, content, "user")
            message.id = response.get("id")
            
            # Send via WebSocket for real-time
            if websocket_service.connected:
                await websocket_service.send_chat_message(conv_id, content, "user")
            
            # Notify handlers
            self._notify_message_handlers(message)
            
            return message
            
        except Exception as e:
            print(f"Error sending message: {e}")
            return None
    
    async def delete_conversation(self, conversation_id: int) -> bool:
        """Delete conversation."""
        try:
            await api_client.delete_conversation(conversation_id)
            
            if conversation_id in self.conversations:
                del self.conversations[conversation_id]
            
            if self.current_conversation_id == conversation_id:
                self.current_conversation_id = None
            
            self._notify_conversation_handlers()
            return True
            
        except Exception as e:
            print(f"Error deleting conversation: {e}")
            return False
    
    def set_current_conversation(self, conversation_id: int):
        """Set current conversation."""
        self.current_conversation_id = conversation_id
        
        # Join WebSocket room
        if websocket_service.connected:
            asyncio.create_task(websocket_service.join_conversation(conversation_id))
    
    def get_current_conversation(self) -> Optional[Conversation]:
        """Get current conversation."""
        if self.current_conversation_id and self.current_conversation_id in self.conversations:
            return self.conversations[self.current_conversation_id]
        return None
    
    def get_conversation_messages(self, conversation_id: int) -> List[Message]:
        """Get messages for conversation."""
        if conversation_id in self.conversations:
            return self.conversations[conversation_id].messages
        return []
    
    async def _handle_chat_message(self, data: Dict[str, Any]):
        """Handle incoming chat message from WebSocket."""
        conversation_id = data.get("conversation_id")
        content = data.get("content", "")
        role = data.get("role", "user")
        
        if conversation_id and conversation_id in self.conversations:
            message = Message(
                conversation_id=conversation_id,
                content=content,
                role=MessageRole(role),
                timestamp=datetime.now()
            )
            
            self.conversations[conversation_id].messages.append(message)
            self.conversations[conversation_id].updated_at = datetime.now()
            
            # Notify handlers
            self._notify_message_handlers(message)
    
    async def _handle_typing_indicator(self, data: Dict[str, Any]):
        """Handle typing indicator from WebSocket."""
        conversation_id = data.get("conversation_id")
        is_typing = data.get("is_typing", False)
        
        # Notify UI about typing status
        for handler in self.message_handlers:
            try:
                await handler({
                    "type": "typing_indicator",
                    "conversation_id": conversation_id,
                    "is_typing": is_typing
                })
            except Exception as e:
                print(f"Error in typing indicator handler: {e}")
    
    def _notify_message_handlers(self, message: Message):
        """Notify message handlers."""
        for handler in self.message_handlers:
            try:
                asyncio.create_task(handler(message))
            except Exception as e:
                print(f"Error in message handler: {e}")
    
    def _notify_conversation_handlers(self):
        """Notify conversation handlers."""
        for handler in self.conversation_handlers:
            try:
                asyncio.create_task(handler())
            except Exception as e:
                print(f"Error in conversation handler: {e}")


# Global message service instance
message_service = MessageService() 