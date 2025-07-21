"""
Chat API endpoints for real-time conversations.

This module provides WebSocket endpoints for real-time chat functionality
and REST endpoints for chat management.
"""

import json
from typing import Any

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from loguru import logger
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.services.ai_service import AIResponse, ai_service
from app.services.conversation_service import ConversationService

router = APIRouter()


# WebSocket connection manager
class ConnectionManager:
    """Manage WebSocket connections for real-time chat."""

    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, conversation_id: str):
        """Connect a WebSocket to a conversation."""
        await websocket.accept()

        if conversation_id not in self.active_connections:
            self.active_connections[conversation_id] = []

        self.active_connections[conversation_id].append(websocket)
        logger.info(f"WebSocket connected to conversation {conversation_id}")

    def disconnect(self, websocket: WebSocket, conversation_id: str):
        """Disconnect a WebSocket from a conversation."""
        if conversation_id in self.active_connections:
            self.active_connections[conversation_id].remove(websocket)
            if not self.active_connections[conversation_id]:
                del self.active_connections[conversation_id]
        logger.info(f"WebSocket disconnected from conversation {conversation_id}")

    async def send_message(self, conversation_id: str, message: dict[str, Any]):
        """Send a message to all connections in a conversation."""
        if conversation_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[conversation_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error sending message to WebSocket: {e}")
                    disconnected.append(connection)

            # Remove disconnected connections
            for connection in disconnected:
                self.disconnect(connection, conversation_id)


# Global connection manager
manager = ConnectionManager()


# Pydantic models
class MessageCreate(BaseModel):
    """Create message request model."""

    content: str
    message_type: str = "text"


class MessageResponse(BaseModel):
    """Message response model."""

    id: str
    content: str
    role: str
    message_type: str
    timestamp: str
    metadata: dict[str, Any] | None = None


class ConversationCreate(BaseModel):
    """Create conversation request model."""

    assistant_id: str
    title: str | None = None


class ConversationResponse(BaseModel):
    """Conversation response model."""

    id: str
    title: str
    assistant_id: str
    assistant_name: str
    created_at: str
    updated_at: str
    message_count: int


@router.websocket("/ws/{conversation_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    conversation_id: str,
    token: str = Query(None, description="Optional JWT token for authentication"),
    db: Session = Depends(get_db),
):
    """
    WebSocket endpoint for real-time chat.
    - Optional JWT-Token-Authentifizierung (token-Query-Parameter)
    - Sende nach erfolgreichem Connect eine Bestätigungsnachricht
    - Unterstützt Nachrichten, Typing-Indikator, Fehlerbehandlung
    """
    # Optional: Authentifizierung via Token (Backward-compatible)
    user_id = None
    if token:
        try:
            # Echte JWT-Validierung
            from app.core.security import verify_token

            user_id = verify_token(token)
            if not user_id:
                await websocket.close(code=4001, reason="Invalid token")
                return
        except Exception as e:
            logger.error(f"JWT validation error: {e}")
            await websocket.close(code=4001, reason="Token validation failed")
            return

    await manager.connect(websocket, conversation_id)
    # Sende Connection-Confirmation
    await websocket.send_text(
        json.dumps(
            {
                "type": "connection_established",
                "data": {
                    "conversation_id": conversation_id,
                    "message": "Connected to chat",
                },
            },
        ),
    )
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            await process_websocket_message(
                websocket, conversation_id, message_data, db, user_id,
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket, conversation_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, conversation_id)


async def process_websocket_message(
    websocket: WebSocket,
    conversation_id: str,
    message_data: dict[str, Any],
    db: Session,
    user_id: str = "",
):
    """
    Process incoming WebSocket message.
    Unterstützt:
    - type: "message" (Chatnachricht)
    - type: "typing" (Typing-Indikator)
    - type: "join" (User joined)
    """
    try:
        message_type = message_data.get("type")
        if message_type == "message":
            content = message_data.get("content", "")
            sender_id = message_data.get("user_id") or user_id or ""
            if not sender_id:
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "error",
                            "message": "User ID required",
                        },
                    ),
                )
                return
            conversation_service = ConversationService(db)
            user_message = await conversation_service.add_message(
                conversation_id=conversation_id,
                user_id=sender_id,
                content=content,
                role="user",
            )
            await manager.send_message(
                conversation_id,
                {
                    "type": "message",
                    "message": {
                        "id": str(user_message.id),
                        "content": user_message.content,
                        "role": user_message.role,
                        "message_type": getattr(user_message, "message_type", "text"),
                        "timestamp": user_message.created_at.isoformat()
                        if hasattr(user_message, "created_at")
                        else "",
                        "metadata": getattr(user_message, "metadata", None),
                    },
                },
            )
            ai_response: AIResponse = await ai_service.get_response(
                conversation_id=conversation_id,
                user_message=content,
                user_id=sender_id,
                db=db,
                use_rag=True,
                use_tools=True,
                max_context_chunks=5,
            )
            assistant_message = await conversation_service.add_message(
                conversation_id=conversation_id,
                user_id=sender_id,
                content=ai_response.content,
                role="assistant",
                message_type=ai_response.message_type,
                metadata=ai_response.metadata,
            )
            await manager.send_message(
                conversation_id,
                {
                    "type": "message",
                    "message": {
                        "id": str(assistant_message.id),
                        "content": assistant_message.content,
                        "role": assistant_message.role,
                        "message_type": getattr(
                            assistant_message, "message_type", "text",
                        ),
                        "timestamp": assistant_message.created_at.isoformat()
                        if hasattr(assistant_message, "created_at")
                        else "",
                        "metadata": getattr(assistant_message, "metadata", None),
                        "tool_calls": ai_response.tool_calls,
                        "context_used": ai_response.context_used,
                    },
                },
            )
        elif message_type == "typing":
            sender_id = message_data.get("user_id") or user_id or ""
            is_typing = message_data.get("typing", False)
            await manager.send_message(
                conversation_id,
                {
                    "type": "typing",
                    "user_id": sender_id,
                    "typing": is_typing,
                },
            )
        elif message_type == "join":
            sender_id = message_data.get("user_id") or user_id or ""
            await manager.send_message(
                conversation_id,
                {
                    "type": "user_joined",
                    "user_id": sender_id,
                },
            )
        else:
            await websocket.send_text(
                json.dumps(
                    {
                        "type": "error",
                        "message": f"Unknown message type: {message_type}",
                    },
                ),
            )
    except Exception as e:
        logger.error(f"Error processing WebSocket message: {e}")
        await websocket.send_text(
            json.dumps(
                {
                    "type": "error",
                    "message": "Internal server error",
                },
            ),
        )


# REST endpoints (existing code)
@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Create a new conversation.

    Args:
        conversation_data: Conversation data
        current_user_id: Current user ID
        db: Database session

    Returns:
        ConversationResponse: Created conversation
    """
    try:
        conversation_service = ConversationService(db)
        conversation = await conversation_service.create_conversation(
            user_id=current_user_id,
            assistant_id=conversation_data.assistant_id,
            title=conversation_data.title,
        )

        return ConversationResponse(
            id=str(conversation.id),
            title=conversation.title,
            assistant_id=str(conversation.assistant_id),
            assistant_name=conversation.assistant.name,
            created_at=conversation.created_at.isoformat(),
            updated_at=conversation.updated_at.isoformat(),
            message_count=conversation.message_count,
        )

    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation",
        )


@router.get(
    "/conversations/{conversation_id}/messages", response_model=list[MessageResponse],
)
async def get_conversation_messages(
    conversation_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Get messages for a conversation.

    Args:
        conversation_id: Conversation ID
        current_user_id: Current user ID
        db: Database session

    Returns:
        List[MessageResponse]: List of messages
    """
    try:
        conversation_service = ConversationService(db)
        messages = await conversation_service.get_conversation_messages(conversation_id)

        return [
            MessageResponse(
                id=str(message.id),
                content=message.content,
                role=message.role,
                message_type=message.message_type,
                timestamp=message.created_at.isoformat(),
                metadata=message.metadata,
            )
            for message in messages
        ]

    except Exception as e:
        logger.error(f"Error getting conversation messages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get conversation messages",
        )


@router.post(
    "/conversations/{conversation_id}/messages", response_model=MessageResponse,
)
async def send_message(
    conversation_id: str,
    message_data: MessageCreate,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    use_rag: bool = Query(True, description="Use RAG for enhanced responses"),
    use_tools: bool = Query(True, description="Enable tool execution"),
    max_context_chunks: int = Query(5, description="Maximum context chunks for RAG"),
):
    """
    Send a message to a conversation with RAG and tool integration.

    Args:
        conversation_id: Conversation ID
        message_data: Message data
        current_user_id: Current user ID
        db: Database session
        use_rag: Whether to use RAG
        use_tools: Whether to enable tools
        max_context_chunks: Maximum context chunks

    Returns:
        MessageResponse: Created message with AI response
    """
    try:
        conversation_service = ConversationService(db)

        # Save user message
        user_message = await conversation_service.add_message(
            conversation_id=conversation_id,
            user_id=current_user_id,
            content=message_data.content,
            role="user",
            message_type=message_data.message_type,
        )

        # Get AI response with RAG and tools
        ai_response: AIResponse = await ai_service.get_response(
            conversation_id=conversation_id,
            user_message=message_data.content,
            user_id=current_user_id,
            db=db,
            use_rag=use_rag,
            use_tools=use_tools,
            max_context_chunks=max_context_chunks,
        )

        # Save AI response
        assistant_message = await conversation_service.add_message(
            conversation_id=conversation_id,
            user_id=current_user_id,
            content=ai_response.content,
            role="assistant",
            message_type=ai_response.message_type,
            metadata=ai_response.metadata,
        )

        # Index messages in Weaviate for future RAG
        try:
            from app.services.weaviate_service import weaviate_service

            weaviate_service.index_message(
                conversation_id=conversation_id,
                message_id=str(user_message.id),
                content=message_data.content,
                role="user",
                metadata={"user_id": current_user_id},
            )
            weaviate_service.index_message(
                conversation_id=conversation_id,
                message_id=str(assistant_message.id),
                content=ai_response.content,
                role="assistant",
                metadata={
                    "user_id": current_user_id,
                    "model_used": ai_response.metadata.get("model_used"),
                },
            )
        except Exception as e:
            logger.warning(f"Failed to index messages in Weaviate: {e}")

        return MessageResponse(
            id=str(assistant_message.id),
            content=assistant_message.content,
            role=assistant_message.role,
            message_type=assistant_message.message_type,
            timestamp=assistant_message.created_at.isoformat(),
            metadata={
                **(assistant_message.metadata or {}),
                "tool_calls": ai_response.tool_calls,
                "context_used": ai_response.context_used,
            },
        )

    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message",
        )
