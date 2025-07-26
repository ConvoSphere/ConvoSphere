"""
WebSocket endpoints for real-time chat functionality.

This module provides WebSocket endpoints for real-time messaging,
typing indicators, chat state management, and knowledge base integration.
"""

import asyncio
import contextlib
import json
from datetime import datetime

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

router = APIRouter()

from app.core.database import get_db

# get_current_user_ws is defined in this file
from app.models.conversation import Conversation
from app.models.user import User
from app.services.ai_service import AIService
from app.services.conversation_service import ConversationService
from app.services.knowledge_service import KnowledgeService
from loguru import logger


class ConnectionManager:
    """Manages WebSocket connections for real-time chat."""

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
        self.conversation_connections: dict[str, set[str]] = {}
        self.user_connections: dict[str, set[str]] = {}
        self.knowledge_search_connections: dict[str, set[str]] = {}

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
        self,
        message: str,
        user_id: str,
        conversation_id: str,
    ):
        """Send a message to a specific user in a conversation."""
        connection_id = f"{user_id}_{conversation_id}"
        if connection_id in self.active_connections:
            await self.active_connections[connection_id].send_text(message)

    async def broadcast_to_conversation(
        self,
        message: str,
        conversation_id: str,
        exclude_user: str | None = None,
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
        self,
        conversation_id: str,
        user_id: str,
        is_typing: bool,
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
            message,
            conversation_id,
            exclude_user=user_id,
        )

    async def send_knowledge_update(
        self,
        user_id: str,
        conversation_id: str,
        documents: list,
        search_query: str,
    ):
        """Send knowledge base search results to user."""
        message = json.dumps(
            {
                "type": "knowledge_update",
                "data": {
                    "documents": documents,
                    "searchQuery": search_query,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            },
        )
        await self.send_personal_message(message, user_id, conversation_id)

    async def send_processing_job_update(
        self,
        user_id: str,
        conversation_id: str,
        job_id: str,
        status: str,
        progress: int,
    ):
        """Send processing job status update to user."""
        message = json.dumps(
            {
                "type": "processing_job_update",
                "data": {
                    "processingJobId": job_id,
                    "status": status,
                    "progress": progress,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            },
        )
        await self.send_personal_message(message, user_id, conversation_id)


# Global connection manager
manager = ConnectionManager()


@router.websocket("/")
async def websocket_general_endpoint(
    websocket: WebSocket,
    token: str,
    db: Session = Depends(get_db),
):
    """General WebSocket endpoint for connection testing."""
    try:
        # Authenticate user
        user = await get_current_user_ws(token, db)
        if not user:
            await websocket.close(code=4001, reason="Authentication failed")
            return

        # Accept connection
        await websocket.accept()

        # Send connection confirmation
        await websocket.send_text(
            json.dumps(
                {
                    "type": "connection_established",
                    "data": {
                        "user_id": str(user.id),
                        "message": "Connected to general WebSocket",
                    },
                },
            ),
        )

        try:
            while True:
                # Keep connection alive
                data = await websocket.receive_text()
                message_data = json.loads(data)

                if message_data.get("type") == "ping":
                    await websocket.send_text(
                        json.dumps(
                            {
                                "type": "pong",
                                "data": {"timestamp": asyncio.get_event_loop().time()},
                            },
                        ),
                    )

        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for user {user.id}")

    except Exception as e:
        logger.error(f"General WebSocket error: {e}")
        with contextlib.suppress(Exception):
            await websocket.close(code=4000, reason=f"Connection error: {str(e)}")


@router.websocket("/{conversation_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    conversation_id: str,
    token: str,
    db: Session = Depends(get_db),
):
    """WebSocket endpoint for real-time chat with knowledge base integration."""
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
                code=4002,
                reason="Conversation not found or access denied",
            )
            return

        # Connect to WebSocket
        await manager.connect(websocket, str(user.id), conversation_id)

        # Initialize services
        conversation_service = ConversationService(db)
        ai_service = AIService()
        knowledge_service = KnowledgeService(db)

        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                message_data = json.loads(data)

                message_type = message_data.get("type")

                if message_type == "message":
                    # Handle new message with knowledge base integration
                    content = message_data.get("data", {}).get("content", "")
                    knowledge_context = message_data.get("data", {}).get(
                        "knowledgeContext",
                    )

                    if not content.strip():
                        continue

                    # Save message to database
                    from app.schemas.conversation import MessageCreate

                    message_data = MessageCreate(
                        conversation_id=conversation_id,
                        content=content,
                        role="user",
                    )
                    message_dict = conversation_service.add_message(message_data)

                    # Broadcast message to conversation
                    broadcast_message = json.dumps(
                        {
                            "type": "message",
                            "data": {
                                "id": str(message_dict["id"]),
                                "conversation_id": conversation_id,
                                "user_id": str(user.id),
                                "content": content,
                                "role": "user",
                                "timestamp": message_dict["created_at"],
                            },
                        },
                    )

                    await manager.broadcast_to_conversation(
                        broadcast_message,
                        conversation_id,
                    )

                    # Generate AI response with streaming
                    try:
                        # Get conversation context
                        messages = conversation_service.get_messages(
                            conversation_id,
                            limit=10,
                        )

                        # Prepare knowledge context for AI
                        knowledge_documents = []
                        if knowledge_context and knowledge_context.get("enabled"):
                            # Search knowledge base for relevant documents
                            search_query = knowledge_context.get("searchQuery", content)
                            max_chunks = knowledge_context.get("maxChunks", 5)

                            # Perform knowledge search
                            search_results = await knowledge_service.search_documents(
                                query=search_query,
                                user_id=str(user.id),
                                limit=max_chunks,
                                filters=knowledge_context.get("filters", {}),
                            )

                            knowledge_documents = search_results.get("documents", [])

                            # Send knowledge update to client
                            if knowledge_documents:
                                await manager.send_knowledge_update(
                                    str(user.id),
                                    conversation_id,
                                    knowledge_documents,
                                    search_query,
                                )

                        # Send typing indicator
                        await manager.send_typing_indicator(
                            conversation_id,
                            str(user.id),
                            True,
                        )

                        # Start streaming AI response
                        full_response_content = ""
                        message_id = None
                        metadata = {}

                        # Generate streaming AI response with RAG
                        async for chunk in ai_service.chat_completion_with_rag_stream(
                            messages=messages,
                            user_id=str(user.id),
                            conversation_id=conversation_id,
                            use_knowledge_base=bool(knowledge_documents),
                            max_context_chunks=len(knowledge_documents),
                            model=(
                                str(conversation.assistant_id)
                                if conversation.assistant_id
                                else None
                            ),
                        ):
                            if "error" in chunk:
                                # Handle error
                                error_message = json.dumps(
                                    {
                                        "type": "error",
                                        "data": {
                                            "message": "AI response generation failed",
                                            "error": chunk["error"],
                                        },
                                    },
                                )
                                await manager.send_personal_message(
                                    error_message,
                                    str(user.id),
                                    conversation_id,
                                )
                                break

                            # Extract content from chunk
                            if chunk.get("choices") and chunk["choices"][0].get("delta"):
                                delta = chunk["choices"][0]["delta"]
                                content_chunk = delta.get("content", "")

                                if content_chunk:
                                    full_response_content += content_chunk

                                    # Send streaming chunk to client
                                    stream_message = json.dumps(
                                        {
                                            "type": "stream_chunk",
                                            "data": {
                                                "conversation_id": conversation_id,
                                                "content": content_chunk,
                                                "is_partial": True,
                                            },
                                        },
                                    )
                                    await manager.send_personal_message(
                                        stream_message,
                                        str(user.id),
                                        conversation_id,
                                    )

                                # Check if response is complete
                                if chunk.get("choices") and chunk["choices"][0].get("finish_reason"):
                                    finish_reason = chunk["choices"][0]["finish_reason"]

                                    if finish_reason in ["stop", "length"]:
                                        # Response is complete, save to database
                                        from app.schemas.conversation import (
                                            MessageCreate,
                                        )

                                        ai_message_data = MessageCreate(
                                            conversation_id=conversation_id,
                                            content=full_response_content,
                                            role="assistant",
                                        )
                                        ai_message_dict = conversation_service.add_message(
                                            ai_message_data,
                                        )
                                        message_id = str(ai_message_dict["id"])

                                        # Extract metadata
                                        if "usage" in chunk:
                                            metadata["tokens_used"] = chunk["usage"].get(
                                                "total_tokens", 0
                                            )
                                        if "context_chunks" in chunk:
                                            metadata["contextChunks"] = chunk["context_count"]
                                            metadata["searchQuery"] = search_query

                                        # Send completion message
                                        completion_message = json.dumps(
                                            {
                                                "type": "stream_complete",
                                                "data": {
                                                    "id": message_id,
                                                    "conversation_id": conversation_id,
                                                    "user_id": str(conversation.assistant_id),
                                                    "content": full_response_content,
                                                    "role": "assistant",
                                                    "timestamp": ai_message_dict["created_at"],
                                                    "messageType": (
                                                        "knowledge"
                                                        if knowledge_documents
                                                        else "text"
                                                    ),
                                                    "documents": knowledge_documents,
                                                    "metadata": metadata,
                                                    "is_partial": False,
                                                },
                                            },
                                        )
                                        await manager.broadcast_to_conversation(
                                            completion_message,
                                            conversation_id,
                                        )
                                        break

                            # Stop typing indicator
                            await manager.send_typing_indicator(
                                conversation_id,
                                str(user.id),
                                False,
                            )

                    except Exception as e:
                        logger.error(f"AI response generation error: {e}")
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
                            error_message,
                            str(user.id),
                            conversation_id,
                        )

                elif message_type == "knowledge_search":
                    # Handle knowledge base search request
                    try:
                        search_query = message_data.get("data", {}).get(
                            "searchQuery",
                            "",
                        )
                        filters = (
                            message_data.get("data", {})
                            .get("knowledgeContext", {})
                            .get("filters", {})
                        )

                        if search_query.strip():
                            # Perform knowledge search
                            search_results = await knowledge_service.search_documents(
                                query=search_query,
                                user_id=str(user.id),
                                limit=10,
                                filters=filters,
                            )

                            documents = search_results.get("documents", [])

                            # Send search results to client
                            await manager.send_knowledge_update(
                                str(user.id),
                                conversation_id,
                                documents,
                                search_query,
                            )

                    except Exception as e:
                        logger.error(f"Knowledge search error: {e}")
                        error_message = json.dumps(
                            {
                                "type": "error",
                                "data": {
                                    "message": "Knowledge search failed",
                                    "error": str(e),
                                },
                            },
                        )
                        await manager.send_personal_message(
                            error_message,
                            str(user.id),
                            conversation_id,
                        )

                elif message_type == "typing":
                    # Handle typing indicator
                    is_typing = message_data.get("data", {}).get("is_typing", False)
                    await manager.send_typing_indicator(
                        conversation_id,
                        str(user.id),
                        is_typing,
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
                        pong_message,
                        str(user.id),
                        conversation_id,
                    )

        except WebSocketDisconnect:
            manager.disconnect(str(user.id), conversation_id)

        except Exception as e:
            logger.error(f"WebSocket error: {e}")
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
            with contextlib.suppress(Exception):
                await manager.send_personal_message(
                    error_message,
                    str(user.id),
                    conversation_id,
                )
            manager.disconnect(str(user.id), conversation_id)

    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        # Handle connection errors
        with contextlib.suppress(Exception):
            await websocket.close(code=4000, reason=f"Connection error: {str(e)}")


async def get_current_user_ws(token: str, db: Session) -> User | None:
    """Get current user from WebSocket token."""
    try:
        if not token:
            return None

        # Proper JWT validation for WebSocket
        from app.core.security import verify_token

        user_id = await verify_token(token)
        if not user_id:
            return None

        # Get user from database
        return db.query(User).filter(User.id == user_id).first()

    except Exception as e:
        logger.error(f"WebSocket JWT validation error: {e}")
        return None
