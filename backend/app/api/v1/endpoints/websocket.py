"""
WebSocket endpoints for real-time chat functionality.

This module provides WebSocket endpoints for real-time messaging,
typing indicators, and chat state management.
"""

import asyncio
import json

from fastapi import Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....core.security import get_current_user_ws
from ....models.conversation import Conversation
from ....models.user import User
from ....services.ai_service import AIService
from ....services.conversation_service import ConversationService


class ConnectionManager:
    """Manages WebSocket connections for real-time chat."""

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
        self.conversation_connections: dict[str, set[str]] = {}
        self.user_connections: dict[str, set[str]] = {}

    async def connect(self, websocket: WebSocket, user_id: str, conversation_id: str):
        """Connect a user to a conversation WebSocket."""
        await websocket.accept()

        connection_id = f"{user_id}_{conversation_id}"
        self.active_connections[connection_id] = websocket

        # Track conversation connections
        if conversation_id not in self.conversation_connections:
            self.conversation_connections[conversation_id] = set()
        self.conversation_connections[conversation_id].add(connection_id)

        # Track user connections
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(connection_id)

        # Send connection confirmation
        await websocket.send_text(
            json.dumps(
                {
                    "type": "connection_established",
                    "data": {
                        "user_id": user_id,
                        "conversation_id": conversation_id,
                        "message": "Connected to chat",
                    },
                },
            ),
        )

    def disconnect(self, user_id: str, conversation_id: str):
        """Disconnect a user from a conversation."""
        connection_id = f"{user_id}_{conversation_id}"

        if connection_id in self.active_connections:
            del self.active_connections[connection_id]

        # Remove from conversation tracking
        if conversation_id in self.conversation_connections:
            self.conversation_connections[conversation_id].discard(connection_id)
            if not self.conversation_connections[conversation_id]:
                del self.conversation_connections[conversation_id]

        # Remove from user tracking
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(connection_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]

    async def send_personal_message(
        self, message: str, user_id: str, conversation_id: str,
    ):
        """Send a message to a specific user in a conversation."""
        connection_id = f"{user_id}_{conversation_id}"
        if connection_id in self.active_connections:
            await self.active_connections[connection_id].send_text(message)

    async def broadcast_to_conversation(
        self, message: str, conversation_id: str, exclude_user: str | None = None,
    ):
        """Broadcast a message to all users in a conversation."""
        if conversation_id in self.conversation_connections:
            for connection_id in self.conversation_connections[conversation_id]:
                # Skip excluded user
                if exclude_user and connection_id.startswith(f"{exclude_user}_"):
                    continue

                if connection_id in self.active_connections:
                    try:
                        await self.active_connections[connection_id].send_text(message)
                    except Exception:
                        # Remove broken connection
                        del self.active_connections[connection_id]
                        self.conversation_connections[conversation_id].discard(
                            connection_id,
                        )

    async def send_typing_indicator(
        self, conversation_id: str, user_id: str, is_typing: bool,
    ):
        """Send typing indicator to conversation participants."""
        message = json.dumps(
            {
                "type": "typing",
                "data": {
                    "conversation_id": conversation_id,
                    "user_id": user_id,
                    "is_typing": is_typing,
                },
            },
        )

        await self.broadcast_to_conversation(
            message, conversation_id, exclude_user=user_id,
        )


# Global connection manager
manager = ConnectionManager()


async def websocket_endpoint(
    websocket: WebSocket,
    conversation_id: str,
    token: str,
    db: Session = Depends(get_db),
):
    """WebSocket endpoint for real-time chat."""
    try:
        # Authenticate user
        user = await get_current_user_ws(token, db)
        if not user:
            await websocket.close(code=4001, reason="Authentication failed")
            return

        # Validate conversation access
        conversation = (
            db.query(Conversation)
            .filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user.id,
            )
            .first()
        )

        if not conversation:
            await websocket.close(
                code=4002, reason="Conversation not found or access denied",
            )
            return

        # Connect to WebSocket
        await manager.connect(websocket, str(user.id), conversation_id)

        # Initialize services
        conversation_service = ConversationService(db)
        ai_service = AIService()

        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                message_data = json.loads(data)

                message_type = message_data.get("type")

                if message_type == "message":
                    # Handle new message
                    content = message_data.get("data", {}).get("content", "")

                    if not content.strip():
                        continue

                    # Save message to database
                    message = conversation_service.add_message(
                        conversation_id=conversation_id,
                        user_id=str(user.id),
                        content=content,
                        role="user",
                    )

                    # Broadcast message to conversation
                    broadcast_message = json.dumps(
                        {
                            "type": "message",
                            "data": {
                                "id": str(message.id),
                                "conversation_id": conversation_id,
                                "user_id": str(user.id),
                                "content": content,
                                "role": "user",
                                "timestamp": message.timestamp.isoformat(),
                            },
                        },
                    )

                    await manager.broadcast_to_conversation(
                        broadcast_message, conversation_id,
                    )

                    # Generate AI response
                    try:
                        # Get conversation context
                        messages = conversation_service.get_messages(
                            conversation_id, limit=10,
                        )

                        # Generate response
                        ai_response = await ai_service.generate_response(
                            messages=messages,
                            assistant_id=str(conversation.assistant_id),
                        )

                        if ai_response:
                            # Save AI response
                            ai_message = conversation_service.add_message(
                                conversation_id=conversation_id,
                                user_id=str(conversation.assistant_id),
                                content=ai_response,
                                role="assistant",
                            )

                            # Broadcast AI response
                            ai_broadcast = json.dumps(
                                {
                                    "type": "message",
                                    "data": {
                                        "id": str(ai_message.id),
                                        "conversation_id": conversation_id,
                                        "user_id": str(conversation.assistant_id),
                                        "content": ai_response,
                                        "role": "assistant",
                                        "timestamp": ai_message.timestamp.isoformat(),
                                    },
                                },
                            )

                            await manager.broadcast_to_conversation(
                                ai_broadcast, conversation_id,
                            )

                    except Exception as e:
                        # Send error message
                        error_message = json.dumps(
                            {
                                "type": "error",
                                "data": {
                                    "message": "Failed to generate AI response",
                                    "error": str(e),
                                },
                            },
                        )
                        await manager.send_personal_message(
                            error_message, str(user.id), conversation_id,
                        )

                elif message_type == "typing":
                    # Handle typing indicator
                    is_typing = message_data.get("data", {}).get("is_typing", False)
                    await manager.send_typing_indicator(
                        conversation_id, str(user.id), is_typing,
                    )

                elif message_type == "ping":
                    # Handle ping for connection health
                    pong_message = json.dumps(
                        {
                            "type": "pong",
                            "data": {"timestamp": asyncio.get_event_loop().time()},
                        },
                    )
                    await manager.send_personal_message(
                        pong_message, str(user.id), conversation_id,
                    )

        except WebSocketDisconnect:
            manager.disconnect(str(user.id), conversation_id)

        except Exception as e:
            # Send error and disconnect
            error_message = json.dumps(
                {
                    "type": "error",
                    "data": {
                        "message": "WebSocket error",
                        "error": str(e),
                    },
                },
            )
            try:
                await manager.send_personal_message(
                    error_message, str(user.id), conversation_id,
                )
            except:
                pass
            manager.disconnect(str(user.id), conversation_id)

    except Exception as e:
        # Handle connection errors
        try:
            await websocket.close(code=4000, reason=f"Connection error: {str(e)}")
        except:
            pass


async def get_current_user_ws(token: str, db: Session) -> User | None:
    """Get current user from WebSocket token."""
    try:
        if not token:
            return None

        # Proper JWT validation for WebSocket
        from app.core.security import verify_token

        user_id = verify_token(token)
        if not user_id:
            return None

        # Get user from database
        user = db.query(User).filter(User.id == user_id).first()
        return user

    except Exception as e:
        logger.error(f"WebSocket JWT validation error: {e}")
        return None
