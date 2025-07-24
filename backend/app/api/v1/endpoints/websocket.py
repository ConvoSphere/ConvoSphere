"""
WebSocket endpoints for real-time chat functionality.

This module provides WebSocket endpoints for real-time messaging,
typing indicators, chat state management, and knowledge base integration.
"""

import asyncio
import contextlib
import json
from datetime import datetime
from typing import Optional

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
from app.services.weaviate_service import weaviate_service
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

    async def send_knowledge_update(
        self, user_id: str, conversation_id: str, documents: list, search_query: str
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
        self, user_id: str, conversation_id: str, job_id: str, status: str, progress: int
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
                code=4002, reason="Conversation not found or access denied",
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
                    knowledge_context = message_data.get("data", {}).get("knowledgeContext")

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

                    # Generate AI response with knowledge base integration
                    try:
                        # Get conversation context
                        messages = conversation_service.get_messages(
                            conversation_id, limit=10,
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
                                filters=knowledge_context.get("filters", {})
                            )
                            
                            knowledge_documents = search_results.get("documents", [])
                            
                            # Send knowledge update to client
                            if knowledge_documents:
                                await manager.send_knowledge_update(
                                    str(user.id), conversation_id, knowledge_documents, search_query
                                )

                        # Generate AI response with RAG
                        ai_response = await ai_service.chat_completion_with_rag(
                            messages=messages,
                            user_id=str(user.id),
                            conversation_id=conversation_id,
                            use_knowledge_base=bool(knowledge_documents),
                            max_context_chunks=len(knowledge_documents),
                            model=str(conversation.assistant_id) if conversation.assistant_id else None,
                        )

                        if ai_response and ai_response.get("choices"):
                            response_content = ai_response["choices"][0]["message"]["content"]
                            
                            # Extract metadata from response
                            metadata = {}
                            if "usage" in ai_response:
                                metadata["tokens_used"] = ai_response["usage"].get("total_tokens", 0)
                            
                            # Add knowledge base metadata
                            if knowledge_documents:
                                metadata["contextChunks"] = len(knowledge_documents)
                                metadata["searchQuery"] = search_query

                            # Save AI response
                            ai_message = conversation_service.add_message(
                                conversation_id=conversation_id,
                                user_id=str(conversation.assistant_id),
                                content=response_content,
                                role="assistant",
                            )

                            # Broadcast AI response with knowledge context
                            ai_broadcast = json.dumps(
                                {
                                    "type": "message",
                                    "data": {
                                        "id": str(ai_message.id),
                                        "conversation_id": conversation_id,
                                        "user_id": str(conversation.assistant_id),
                                        "content": response_content,
                                        "role": "assistant",
                                        "timestamp": ai_message.timestamp.isoformat(),
                                        "messageType": "knowledge" if knowledge_documents else "text",
                                        "documents": knowledge_documents,
                                        "metadata": metadata,
                                    },
                                },
                            )

                            await manager.broadcast_to_conversation(
                                ai_broadcast, conversation_id,
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
                            error_message, str(user.id), conversation_id,
                        )

                elif message_type == "knowledge_search":
                    # Handle knowledge base search request
                    try:
                        search_query = message_data.get("data", {}).get("searchQuery", "")
                        filters = message_data.get("data", {}).get("knowledgeContext", {}).get("filters", {})
                        
                        if search_query.strip():
                            # Perform knowledge search
                            search_results = await knowledge_service.search_documents(
                                query=search_query,
                                user_id=str(user.id),
                                limit=10,
                                filters=filters
                            )
                            
                            documents = search_results.get("documents", [])
                            
                            # Send search results to client
                            await manager.send_knowledge_update(
                                str(user.id), conversation_id, documents, search_query
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
                    error_message, str(user.id), conversation_id,
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

        user_id = verify_token(token)
        if not user_id:
            return None

        # Get user from database
        return db.query(User).filter(User.id == user_id).first()

    except Exception as e:
        logger.error(f"WebSocket JWT validation error: {e}")
        return None
