"""
Chat endpoints for real-time conversations with AI assistants.

This module provides the chat API endpoints for sending messages to
AI assistants and receiving responses.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from sqlalchemy.orm import Session
from loguru import logger

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.services.conversation_service import ConversationService
from app.services.assistant_service import AssistantService
from app.services.ai_service import AIService
from app.models.conversation import MessageRole, MessageType

router = APIRouter()


# Pydantic models
class ChatMessage(BaseModel):
    """Chat message request model."""
    content: str
    message_type: MessageType = MessageType.TEXT
    metadata: Optional[dict] = None


class ChatResponse(BaseModel):
    """Chat response model."""
    message_id: str
    content: str
    role: str
    message_type: str
    timestamp: str
    tokens_used: Optional[int] = None
    model_used: Optional[str] = None


class ConversationCreate(BaseModel):
    """Create conversation request model."""
    assistant_id: str
    title: Optional[str] = None


@router.post("/conversations", response_model=dict)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Create a new conversation with an assistant.
    
    Args:
        conversation_data: Conversation creation data
        current_user_id: Current user ID
        db: Database session
        
    Returns:
        dict: Created conversation information
    """
    try:
        # Verify assistant exists and is accessible
        assistant_service = AssistantService(db)
        assistant = assistant_service.get_assistant(conversation_data.assistant_id)
        
        if not assistant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assistant not found"
            )
        
        if not assistant.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assistant is not active"
            )
        
        # Create conversation
        conversation_service = ConversationService(db)
        conversation = conversation_service.create_conversation(
            user_id=current_user_id,
            assistant_id=conversation_data.assistant_id,
            title=conversation_data.title or "New Conversation"
        )
        
        logger.info(f"Conversation created: {conversation['id']} by user {current_user_id}")
        
        return {
            "conversation_id": conversation["id"],
            "assistant_id": conversation_data.assistant_id,
            "title": conversation["title"],
            "created_at": conversation["created_at"]
        }
        
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation"
        )


@router.post("/conversations/{conversation_id}/messages", response_model=ChatResponse)
async def send_message(
    conversation_id: str,
    message: ChatMessage,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Send a message to an assistant in a conversation.
    
    Args:
        conversation_id: Conversation ID
        message: Message content
        current_user_id: Current user ID
        db: Database session
        
    Returns:
        ChatResponse: Assistant's response
    """
    try:
        conversation_service = ConversationService(db)
        assistant_service = AssistantService(db)
        ai_service = AIService()
        
        # Get conversation and verify ownership
        conversation = conversation_service.get_conversation(conversation_id, current_user_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Get assistant
        assistant = assistant_service.get_assistant(conversation["assistant_id"])
        if not assistant or not assistant.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assistant not available"
            )
        
        # Add user message to conversation
        user_message = conversation_service.add_message(
            conversation_id=conversation_id,
            user_id=current_user_id,
            content=message.content,
            role=MessageRole.USER,
            message_type=message.message_type,
            metadata=message.metadata
        )
        
        # Get conversation history for context
        history = conversation_service.get_conversation_history(conversation_id)
        
        # Generate assistant response
        assistant_config = {
            "model": assistant.model,
            "temperature": float(assistant.temperature),
            "max_tokens": int(assistant.max_tokens)
        }
        
        ai_response = await ai_service.generate_assistant_response(
            system_prompt=assistant.system_prompt,
            user_message=message.content,
            conversation_history=history,
            assistant_config=assistant_config
        )
        
        # Add assistant response to conversation
        assistant_message = conversation_service.add_message(
            conversation_id=conversation_id,
            user_id=None,  # Assistant message
            content=ai_response["content"],
            role=MessageRole.ASSISTANT,
            message_type=MessageType.TEXT,
            metadata={
                "model_used": ai_response["model"],
                "tokens_used": ai_response["usage"]["total_tokens"],
                "finish_reason": ai_response["finish_reason"]
            }
        )
        
        logger.info(f"Message sent in conversation {conversation_id} by user {current_user_id}")
        
        return ChatResponse(
            message_id=assistant_message["id"],
            content=ai_response["content"],
            role=MessageRole.ASSISTANT.value,
            message_type=MessageType.TEXT.value,
            timestamp=assistant_message["created_at"],
            tokens_used=ai_response["usage"]["total_tokens"],
            model_used=ai_response["model"]
        )
        
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message"
        )


@router.get("/conversations/{conversation_id}/messages", response_model=List[ChatResponse])
async def get_conversation_messages(
    conversation_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get all messages in a conversation.
    
    Args:
        conversation_id: Conversation ID
        current_user_id: Current user ID
        db: Database session
        
    Returns:
        List[ChatResponse]: List of messages
    """
    try:
        conversation_service = ConversationService(db)
        
        # Verify conversation ownership
        conversation = conversation_service.get_conversation(conversation_id, current_user_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Get messages
        messages = conversation_service.get_conversation_messages(conversation_id)
        
        return [
            ChatResponse(
                message_id=msg["id"],
                content=msg["content"],
                role=msg["role"],
                message_type=msg["message_type"],
                timestamp=msg["created_at"],
                tokens_used=msg.get("tokens_used"),
                model_used=msg.get("model_used")
            )
            for msg in messages
        ]
        
    except Exception as e:
        logger.error(f"Error getting conversation messages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get messages"
        )


@router.websocket("/ws/conversations/{conversation_id}")
async def websocket_chat(
    websocket: WebSocket,
    conversation_id: str,
    token: str
):
    """
    WebSocket endpoint for real-time chat.
    
    Args:
        websocket: WebSocket connection
        conversation_id: Conversation ID
        token: JWT token for authentication
    """
    # TODO: Implement WebSocket chat functionality
    await websocket.accept()
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            # Process message and generate response
            # TODO: Implement message processing
            
            # Send response back to client
            await websocket.send_text(f"Echo: {data}")
            
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close() 