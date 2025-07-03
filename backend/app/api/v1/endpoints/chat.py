"""
Chat API endpoints for real-time conversations.

This module provides WebSocket endpoints for real-time chat functionality
and REST endpoints for chat management.
"""

import json
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from sqlalchemy.orm import Session
from loguru import logger

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.services.conversation_service import ConversationService
from app.services.ai_service import AIService


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


@router.websocket("/ws/{conversation_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    conversation_id: str,
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time chat.
    
    Args:
        websocket: WebSocket connection
        conversation_id: Conversation ID
        db: Database session
    """
    await manager.connect(websocket, conversation_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process message
            await process_websocket_message(websocket, conversation_id, message_data, db)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, conversation_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, conversation_id)


async def process_websocket_message(
    websocket: WebSocket,
    conversation_id: str,
    message_data: Dict[str, Any],
    db: Session
):
    """
    Process incoming WebSocket message.
    
    Args:
        websocket: WebSocket connection
        conversation_id: Conversation ID
        message_data: Message data
        db: Database session
    """
    try:
        message_type = message_data.get("type")
        
        if message_type == "message":
            # Handle new message
            content = message_data.get("content", "")
            user_id = message_data.get("user_id")
            
            if not user_id:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "User ID required"
                }))
                return
            
            # Save user message
            conversation_service = ConversationService(db)
            user_message = await conversation_service.add_message(
                conversation_id=conversation_id,
                user_id=user_id,
                content=content,
                role="user"
            )
            
            # Send user message to all clients
            await manager.send_message(conversation_id, {
                "type": "message",
                "message": {
                    "id": str(user_message.id),
                    "content": user_message.content,
                    "role": user_message.role,
                    "message_type": user_message.message_type,
                    "timestamp": user_message.created_at.isoformat(),
                    "metadata": user_message.metadata
                }
            })
            
            # Get AI response
            ai_service = AIService()
            ai_response = await ai_service.get_response(
                conversation_id=conversation_id,
                user_message=content,
                db=db
            )
            
            # Save AI response
            assistant_message = await conversation_service.add_message(
                conversation_id=conversation_id,
                user_id=user_id,
                content=ai_response.content,
                role="assistant",
                message_type=ai_response.message_type,
                metadata=ai_response.metadata
            )
            
            # Send AI response to all clients
            await manager.send_message(conversation_id, {
                "type": "message",
                "message": {
                    "id": str(assistant_message.id),
                    "content": assistant_message.content,
                    "role": assistant_message.role,
                    "message_type": assistant_message.message_type,
                    "timestamp": assistant_message.created_at.isoformat(),
                    "metadata": assistant_message.metadata
                }
            })
            
        elif message_type == "typing":
            # Handle typing indicator
            user_id = message_data.get("user_id")
            is_typing = message_data.get("typing", False)
            
            await manager.send_message(conversation_id, {
                "type": "typing",
                "user_id": user_id,
                "typing": is_typing
            })
            
        elif message_type == "join":
            # Handle user joining conversation
            user_id = message_data.get("user_id")
            
            await manager.send_message(conversation_id, {
                "type": "user_joined",
                "user_id": user_id
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


# REST endpoints (existing code)
@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
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
            title=conversation_data.title
        )
        
        return ConversationResponse(
            id=str(conversation.id),
            title=conversation.title,
            assistant_id=str(conversation.assistant_id),
            assistant_name=conversation.assistant.name,
            created_at=conversation.created_at.isoformat(),
            updated_at=conversation.updated_at.isoformat(),
            message_count=conversation.message_count
        )
        
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation"
        )


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
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
                metadata=message.metadata
            )
            for message in messages
        ]
        
    except Exception as e:
        logger.error(f"Error getting conversation messages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get conversation messages"
        )


@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: str,
    message_data: MessageCreate,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Send a message to a conversation.
    
    Args:
        conversation_id: Conversation ID
        message_data: Message data
        current_user_id: Current user ID
        db: Database session
        
    Returns:
        MessageResponse: Created message
    """
    try:
        conversation_service = ConversationService(db)
        
        # Save user message
        user_message = await conversation_service.add_message(
            conversation_id=conversation_id,
            user_id=current_user_id,
            content=message_data.content,
            role="user",
            message_type=message_data.message_type
        )
        
        # Get AI response
        ai_service = AIService()
        ai_response = await ai_service.get_response(
            conversation_id=conversation_id,
            user_message=message_data.content,
            db=db
        )
        
        # Save AI response
        assistant_message = await conversation_service.add_message(
            conversation_id=conversation_id,
            user_id=current_user_id,
            content=ai_response.content,
            role="assistant",
            message_type=ai_response.message_type,
            metadata=ai_response.metadata
        )
        
        return MessageResponse(
            id=str(assistant_message.id),
            content=assistant_message.content,
            role=assistant_message.role,
            message_type=assistant_message.message_type,
            timestamp=assistant_message.created_at.isoformat(),
            metadata=assistant_message.metadata
        )
        
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message"
        ) 