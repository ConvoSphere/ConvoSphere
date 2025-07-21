"""
Message service for chat functionality.

This module provides message management, AI integration, and real-time
chat capabilities using WebSocket connections.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from .api_client import api_client
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
    url: str | None = None
    content: bytes | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class ToolResult:
    """Tool execution result data model."""

    tool_name: str
    tool_id: str
    input_data: dict[str, Any]
    output_data: dict[str, Any]
    execution_time: float
    status: str  # success, error, timeout
    error_message: str | None = None


@dataclass
class Message:
    """Message data model."""

    id: str
    content: str
    role: str  # "user" or "assistant"
    message_type: str = "text"
    timestamp: datetime | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class Conversation:
    """Conversation model."""

    id: int | None = None
    title: str = ""
    assistant_id: int | None = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    messages: list[Message] = field(default_factory=list)


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
    metadata: dict[str, Any] | None = None
    file_attachments: list[FileAttachment] | None = None
    tool_results: list[ToolResult] | None = None
    reply_to: str | None = None
    is_edited: bool = False
    edit_history: list[dict[str, Any]] | None = None


class MessageService:
    """Service for managing chat messages and AI interactions."""

    def __init__(self):
        """Initialize the message service."""
        self.current_conversation_id: str | None = None
        self.messages: list[Message] = []
        self.is_connected = False
        self.is_typing = False

        # Event system for UI updates
        self._event_listeners = {
            "message_received": [],
            "message_sent": [],
            "typing_changed": [],
            "connection_changed": [],
            "error": [],
        }

        # Setup WebSocket handlers
        self._setup_websocket_handlers()

    def _setup_websocket_handlers(self):
        """Setup WebSocket message handlers."""

        @websocket_service.on_message("message")
        async def handle_message(data: dict[str, Any]):
            """Handle incoming message."""
            message = Message(
                id=data.get("id", ""),
                content=data.get("content", ""),
                role=data.get("role", "user"),
                message_type=data.get("message_type", "text"),
                timestamp=datetime.fromisoformat(
                    data.get("timestamp", datetime.now().isoformat()),
                ),
                metadata=data.get("metadata"),
            )

            # Add message to local list
            self.messages.append(message)

            # Notify listeners
            await self._notify_message_received(message)

        @websocket_service.on_message("typing")
        async def handle_typing(data: dict[str, Any]):
            """Handle typing indicator."""
            user_id = data.get("user_id")
            is_typing = data.get("is_typing", False)

            if user_id and user_id != "assistant":  # Don't show typing for assistant
                await self._notify_typing_changed(str(user_id), is_typing)

        @websocket_service.on_message("ai_response")
        async def handle_ai_response(data: dict[str, Any]):
            """Handle AI response."""
            message = Message(
                id=data.get("id", ""),
                content=data.get("content", ""),
                role="assistant",
                message_type=data.get("message_type", "text"),
                timestamp=datetime.fromisoformat(
                    data.get("timestamp", datetime.now().isoformat()),
                ),
                metadata=data.get("metadata"),
            )

            # Add message to local list
            self.messages.append(message)

            # Notify listeners
            await self._notify_message_received(message)

        websocket_service.on_connect(self._on_websocket_connect)
        websocket_service.on_disconnect(self._on_websocket_disconnect)

    async def _on_websocket_connect(self):
        """Handle WebSocket connection."""
        self.is_connected = True
        await self._notify_connection_changed(True)

    async def _on_websocket_disconnect(self):
        """Handle WebSocket disconnection."""
        self.is_connected = False
        await self._notify_connection_changed(False)

    async def connect_to_conversation(self, conversation_id: str) -> bool:
        """
        Connect to a conversation for real-time chat.

        Args:
            conversation_id: Conversation ID

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.current_conversation_id = conversation_id

            # Connect to WebSocket
            await websocket_service.connect(f"/api/v1/chat/ws/{conversation_id}")

            # Load existing messages
            await self.load_messages(conversation_id)

            return True

        except Exception as e:
            print(f"Failed to connect to conversation: {e}")
            return False

    async def disconnect_from_conversation(self):
        """Disconnect from current conversation."""
        if self.current_conversation_id:
            try:
                await websocket_service.leave_conversation(
                    int(self.current_conversation_id),
                )
                await websocket_service.disconnect()
            except Exception as e:
                print(f"Error disconnecting: {e}")
            finally:
                self.current_conversation_id = None
                self.messages.clear()

    async def send_message(
        self, content: str, message_type: str = "text",
    ) -> Message | None:
        """
        Send a message to the current conversation.

        Args:
            content: Message content
            message_type: Type of message

        Returns:
            Message: Sent message or None if failed
        """
        if not self.current_conversation_id:
            raise ValueError("No active conversation")

        if not content.strip():
            return None

        try:
            # Create message object
            message = Message(
                id=f"temp_{datetime.now().timestamp()}",
                content=content,
                role="user",
                message_type=message_type,
                timestamp=datetime.now(),
            )

            # Add to local list immediately for UI responsiveness
            self.messages.append(message)

            # Send via WebSocket if connected
            if self.is_connected:
                await websocket_service.send_chat_message(
                    conversation_id=int(self.current_conversation_id),
                    content=content,
                    role="user",
                )
            else:
                # Fallback to REST API
                response = await api_client.send_message(
                    conversation_id=int(self.current_conversation_id),
                    content=content,
                    role="user",
                )

                if response.get("success"):
                    # Update message with server response
                    message.id = response.get("data", {}).get("id", message.id)
                    message.timestamp = datetime.fromisoformat(
                        response.get("data", {}).get(
                            "timestamp", datetime.now().isoformat(),
                        ),
                    )

            # Notify listeners
            await self._notify_message_sent(message)

            return message

        except Exception as e:
            print(f"Failed to send message: {e}")
            # Remove message from local list if failed
            if message in self.messages:
                self.messages.remove(message)
            return None

    async def load_messages(
        self, conversation_id: str, limit: int = 50,
    ) -> list[Message]:
        """
        Load messages for a conversation.

        Args:
            conversation_id: Conversation ID
            limit: Maximum number of messages to load

        Returns:
            List[Message]: List of messages
        """
        try:
            response = await api_client.get_messages(int(conversation_id), limit=limit)

            if response.get("success"):
                messages_data = response.get("data", [])
                self.messages = []

                for msg_data in messages_data:
                    message = Message(
                        id=msg_data.get("id", ""),
                        content=msg_data.get("content", ""),
                        role=msg_data.get("role", "user"),
                        message_type=msg_data.get("message_type", "text"),
                        timestamp=datetime.fromisoformat(
                            msg_data.get("timestamp", datetime.now().isoformat()),
                        ),
                        metadata=msg_data.get("metadata"),
                    )
                    self.messages.append(message)

                return self.messages
            print(f"Failed to load messages: {response.get('error')}")
            return []

        except Exception as e:
            print(f"Error loading messages: {e}")
            return []

    async def start_typing(self):
        """Send typing indicator."""
        if self.current_conversation_id and self.is_connected:
            try:
                await websocket_service.send_typing_indicator(
                    conversation_id=int(self.current_conversation_id),
                    is_typing=True,
                )
                self.is_typing = True
            except Exception as e:
                print(f"Failed to send typing indicator: {e}")

    async def stop_typing(self):
        """Stop typing indicator."""
        if self.current_conversation_id and self.is_connected:
            try:
                await websocket_service.send_typing_indicator(
                    conversation_id=int(self.current_conversation_id),
                    is_typing=False,
                )
                self.is_typing = False
            except Exception as e:
                print(f"Failed to stop typing indicator: {e}")

    def get_messages(self) -> list[Message]:
        """Get all messages in current conversation."""
        return self.messages.copy()

    def get_message_by_id(self, message_id: str) -> Message | None:
        """Get message by ID."""
        for message in self.messages:
            if message.id == message_id:
                return message
        return None

    def clear_messages(self):
        """Clear all messages."""
        self.messages.clear()

    # Event system for UI updates

    def add_event_listener(self, event_type: str, callback):
        """Add event listener for UI updates."""
        if event_type in self._event_listeners:
            self._event_listeners[event_type].append(callback)

    def remove_event_listener(self, event_type: str, callback):
        """Remove event listener."""
        if event_type in self._event_listeners:
            try:
                self._event_listeners[event_type].remove(callback)
            except ValueError:
                pass

    async def _notify_event(self, event_type: str, data: Any):
        """Notify all listeners of an event."""
        if event_type in self._event_listeners:
            for callback in self._event_listeners[event_type]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(data)
                    else:
                        callback(data)
                except Exception as e:
                    print(f"Error in event listener {event_type}: {e}")

    # Event notification methods
    async def _notify_message_received(self, message: Message):
        """Notify that a message was received."""
        await self._notify_event("message_received", message)

    async def _notify_message_sent(self, message: Message):
        """Notify that a message was sent."""
        await self._notify_event("message_sent", message)

    async def _notify_typing_changed(self, user_id: str, is_typing: bool):
        """Notify typing status change."""
        await self._notify_event(
            "typing_changed",
            {
                "user_id": user_id,
                "is_typing": is_typing,
            },
        )

    async def _notify_connection_changed(self, connected: bool):
        """Notify connection status change."""
        await self._notify_event(
            "connection_changed",
            {
                "connected": connected,
            },
        )

    async def _notify_error(self, error: str):
        """Notify error event."""
        await self._notify_event("error", error)


# Global message service instance
message_service = MessageService()
