"""
Chat API endpoints for real-time conversations.

This module provides WebSocket endpoints for real-time chat functionality
and REST endpoints for chat management.
"""

import json
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from loguru import logger

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.services.conversation_service import ConversationService
from app.services.ai_service import AIService, ai_service, AIResponse
from app.services.assistant_engine import AssistantEngine
from app.services.assistant_service import AssistantService
from app.services.tool_service import tool_service


router = APIRouter()


# WebSocket connection manager
class ConnectionManager:
    """Manage WebSocket connections for real-time chat."""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
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
    
    async def send_message(self, conversation_id: str, message: Dict[str, Any]):
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
    metadata: Optional[Dict[str, Any]] = None


class ConversationCreate(BaseModel):
    """Create conversation request model."""
    assistant_id: str
    title: Optional[str] = None


class ConversationResponse(BaseModel):
    """Conversation response model."""
    id: str
    title: str
    assistant_id: str
    assistant_name: str
    created_at: str
    updated_at: str
    message_count: int


class AssistantSwitchRequest(BaseModel):
    """Assistant switch request model."""
    assistant_id: str
    preserve_context: bool = True


class AssistantSwitchResponse(BaseModel):
    """Assistant switch response model."""
    conversation_id: str
    old_assistant_id: str
    new_assistant_id: str
    assistant_name: str
    context_preserved: bool
    message: str


@router.websocket("/ws/{conversation_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    conversation_id: str,
    token: str = Query(None, description="Optional JWT token for authentication"),
    db: Session = Depends(get_db)
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
        # TODO: Implementiere echte JWT-Validierung
        # Hier: Dummy-Validierung für Entwicklung
        user_id = str(token) if token != "mock_token_123" else ""
    
    await manager.connect(websocket, conversation_id)
    # Sende Connection-Confirmation
    await websocket.send_text(json.dumps({
        "type": "connection_established",
        "data": {
            "conversation_id": conversation_id,
            "message": "Connected to chat"
        }
    }))
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            await process_websocket_message(websocket, conversation_id, message_data, db, user_id)
    except WebSocketDisconnect:
        manager.disconnect(websocket, conversation_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, conversation_id)


async def process_websocket_message(
    websocket: WebSocket,
    conversation_id: str,
    message_data: Dict[str, Any],
    db: Session,
    user_id: str = ""
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
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "User ID required"
                }))
                return
            conversation_service = ConversationService(db)
            assistant_service = AssistantService(db)
            
            # Create assistant engine
            assistant_engine = AssistantEngine(
                ai_service=ai_service,
                assistant_service=assistant_service,
                conversation_service=conversation_service,
                tool_service=tool_service
            )
            
            # Get conversation to find assistant_id
            conversation = await conversation_service.get_conversation(conversation_id, sender_id)
            if not conversation:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Conversation not found"
                }))
                return
            
            assistant_id = str(conversation.assistant_id) if conversation.assistant_id else "default"
            
            # Add user message
            user_message = await conversation_service.add_message(
                conversation_id=conversation_id,
                user_id=sender_id,
                content=content,
                role="user"
            )
            
            await manager.send_message(conversation_id, {
                "type": "message",
                "message": {
                    "id": str(user_message.id),
                    "content": user_message.content,
                    "role": user_message.role,
                    "message_type": getattr(user_message, 'message_type', 'text'),
                    "timestamp": user_message.created_at.isoformat() if hasattr(user_message, 'created_at') else "",
                    "metadata": getattr(user_message, 'metadata', None)
                }
            })
            
            # Process message with assistant engine
            ai_response: AIResponse = await assistant_engine.process_message(
                message=content,
                conversation_id=conversation_id,
                assistant_id=assistant_id,
                user_id=sender_id,
                use_rag=True,
                use_tools=True
            )
            
            # Add assistant message
            assistant_message = await conversation_service.add_message(
                conversation_id=conversation_id,
                user_id=sender_id,
                content=ai_response.content,
                role="assistant",
                message_type="text",
                metadata=ai_response.metadata
            )
            await manager.send_message(conversation_id, {
                "type": "message",
                "message": {
                    "id": str(assistant_message.id),
                    "content": assistant_message.content,
                    "role": assistant_message.role,
                    "message_type": getattr(assistant_message, 'message_type', 'text'),
                    "timestamp": assistant_message.created_at.isoformat() if hasattr(assistant_message, 'created_at') else "",
                    "metadata": getattr(assistant_message, 'metadata', None)
                }
            })
        elif message_type == "typing":
            # Broadcast typing indicator
            await manager.send_message(conversation_id, {
                "type": "typing",
                "user_id": message_data.get("user_id", ""),
                "is_typing": message_data.get("is_typing", False)
            })
        elif message_type == "join":
            # User joined the conversation
            await manager.send_message(conversation_id, {
                "type": "user_joined",
                "user_id": message_data.get("user_id", ""),
                "username": message_data.get("username", "Unknown")
            })
        else:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": f"Unknown message type: {message_type}"
            }))
    except Exception as e:
        logger.error(f"Error processing WebSocket message: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": "Internal server error"
        }))


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Create a new conversation."""
    conversation_service = ConversationService(db)
    
    # Validate assistant exists
    # TODO: Add assistant validation
    
    conversation = await conversation_service.create_conversation(
        user_id=current_user_id,
        assistant_id=conversation_data.assistant_id,
        title=conversation_data.title
    )
    
    return ConversationResponse(
        id=str(conversation.id),
        title=conversation.title,
        assistant_id=str(conversation.assistant_id),
        assistant_name=conversation.assistant_name,
        created_at=conversation.created_at.isoformat(),
        updated_at=conversation.updated_at.isoformat(),
        message_count=conversation.message_count
    )


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get all messages in a conversation."""
    conversation_service = ConversationService(db)
    
    # Verify conversation access
    conversation = await conversation_service.get_conversation(conversation_id, current_user_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = await conversation_service.get_conversation_messages(conversation_id)
    
    return [
        MessageResponse(
            id=str(message.id),
            content=message.content,
            role=message.role,
            message_type=getattr(message, 'message_type', 'text'),
            timestamp=message.created_at.isoformat(),
            metadata=getattr(message, 'metadata', None)
        )
        for message in messages
    ]


@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: str,
    message_data: MessageCreate,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    use_rag: bool = Query(True, description="Use RAG for enhanced responses"),
    use_tools: bool = Query(True, description="Enable tool execution"),
    max_context_chunks: int = Query(5, description="Maximum context chunks for RAG")
):
    """Send a message to a conversation."""
    conversation_service = ConversationService(db)
    
    # Verify conversation access
    conversation = await conversation_service.get_conversation(conversation_id, current_user_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Add user message
    user_message = await conversation_service.add_message(
        conversation_id=conversation_id,
        user_id=current_user_id,
        content=message_data.content,
        role="user",
        message_type=message_data.message_type
    )
    
                # Get conversation to find assistant_id
            conversation = await conversation_service.get_conversation(conversation_id, current_user_id)
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
            
            assistant_id = str(conversation.assistant_id) if conversation.assistant_id else "default"
            
            # Create assistant engine
            assistant_service = AssistantService(db)
            assistant_engine = AssistantEngine(
                ai_service=ai_service,
                assistant_service=assistant_service,
                conversation_service=conversation_service,
                tool_service=tool_service
            )
            
            # Get AI response using assistant engine
            ai_response: AIResponse = await assistant_engine.process_message(
                message=message_data.content,
                conversation_id=conversation_id,
                assistant_id=assistant_id,
                user_id=current_user_id,
                use_rag=use_rag,
                use_tools=use_tools
            )
    
    # Add assistant message
    assistant_message = await conversation_service.add_message(
        conversation_id=conversation_id,
        user_id=current_user_id,
        content=ai_response.content,
        role="assistant",
        message_type="text",
        metadata=ai_response.metadata
    )
    
    return MessageResponse(
        id=str(assistant_message.id),
        content=assistant_message.content,
        role=assistant_message.role,
        message_type=getattr(assistant_message, 'message_type', 'text'),
        timestamp=assistant_message.created_at.isoformat(),
        metadata=getattr(assistant_message, 'metadata', None)
    )


# --- Assistant Switching ---

@router.post("/conversations/{conversation_id}/switch-assistant", response_model=AssistantSwitchResponse)
async def switch_conversation_assistant(
    conversation_id: str,
    switch_request: AssistantSwitchRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Switch the active assistant for a conversation."""
    conversation_service = ConversationService(db)
    
    # Verify conversation access
    conversation = await conversation_service.get_conversation(conversation_id, current_user_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Validate new assistant exists
    # TODO: Add assistant validation
    
    # Switch assistant
    switch_result = await conversation_service.switch_assistant(
        conversation_id=conversation_id,
        new_assistant_id=switch_request.assistant_id,
        preserve_context=switch_request.preserve_context,
        user_id=current_user_id
    )
    
    if not switch_result:
        raise HTTPException(status_code=400, detail="Failed to switch assistant")
    
    return AssistantSwitchResponse(
        conversation_id=conversation_id,
        old_assistant_id=str(conversation.assistant_id),
        new_assistant_id=switch_request.assistant_id,
        assistant_name=switch_result.get("assistant_name", "Unknown"),
        context_preserved=switch_request.preserve_context,
        message=f"Switched to {switch_result.get('assistant_name', 'Unknown')} assistant"
    )


@router.get("/conversations/{conversation_id}/assistant", response_model=Dict[str, Any])
async def get_conversation_assistant(
    conversation_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get the current assistant for a conversation."""
    conversation_service = ConversationService(db)
    
    # Verify conversation access
    conversation = await conversation_service.get_conversation(conversation_id, current_user_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Get assistant details
    assistant = await conversation_service.get_conversation_assistant(conversation_id)
    
    return {
        "assistant_id": str(assistant.get("id")),
        "assistant_name": assistant.get("name", "Unknown"),
        "assistant_description": assistant.get("description", ""),
        "assistant_avatar": assistant.get("avatar", ""),
        "assistant_capabilities": assistant.get("capabilities", [])
    } 