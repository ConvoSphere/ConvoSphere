"""
Chat API endpoints with hybrid mode support.

This module provides chat endpoints with integration to the hybrid mode
management system for structured responses and mode switching.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from loguru import logger
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.rate_limiting import rate_limit_chat
from backend.app.core.security import get_current_user_id
from backend.app.core.validation import (
    SecureChatMessageRequest,
    SecureConversationCreateRequest,
    SecurityValidationError,
    log_security_event,
)
from backend.app.schemas.hybrid_mode import ConversationMode
from backend.app.services.assistant_engine import assistant_engine
from backend.app.services.conversation_service import conversation_service

router = APIRouter()


class ChatMessageRequest(BaseModel):
    """Request model for chat messages with hybrid mode support."""

    message: str = Field(
        ..., min_length=1, max_length=10000, description="User message"
    )
    assistant_id: str | None = Field(None, description="Assistant ID")
    use_knowledge_base: bool = Field(
        default=True, description="Use knowledge base context"
    )
    use_tools: bool = Field(default=True, description="Enable tool usage")
    max_context_chunks: int = Field(
        default=5, ge=1, le=20, description="Maximum knowledge chunks"
    )
    temperature: float = Field(
        default=0.7, ge=0.0, le=2.0, description="AI temperature"
    )
    max_tokens: int | None = Field(None, ge=1, le=100000, description="Maximum tokens")
    model: str | None = Field(None, description="AI model to use")
    force_mode: ConversationMode | None = Field(
        None, description="Force specific conversation mode"
    )
    metadata: dict[str, Any] | None = Field(None, description="Additional metadata")


class ChatMessageResponse(BaseModel):
    """Response model for chat messages with structured output."""

    success: bool = Field(..., description="Whether the request was successful")
    content: str = Field(..., description="Assistant response content")
    conversation_id: str = Field(..., description="Conversation ID")
    message_id: str = Field(..., description="Message ID")
    model_used: str = Field(..., description="Model used for response")
    tokens_used: int = Field(..., description="Tokens used")
    processing_time: float = Field(..., description="Processing time in seconds")
    tool_calls: list[dict[str, Any]] = Field(
        default_factory=list, description="Tool calls made"
    )
    mode_decision: dict[str, Any] | None = Field(
        None, description="Mode decision information"
    )
    reasoning_process: list[dict[str, Any]] | None = Field(
        None, description="Reasoning process"
    )
    error_message: str | None = Field(None, description="Error message if failed")


class ConversationCreateRequest(BaseModel):
    """Request model for creating conversations."""

    title: str = Field(
        ..., min_length=1, max_length=500, description="Conversation title"
    )
    assistant_id: str | None = Field(None, description="Assistant ID")
    description: str | None = Field(None, description="Conversation description")


class ConversationListResponse(BaseModel):
    """Response model for conversation list."""

    conversations: list[dict[str, Any]] = Field(
        ..., description="List of conversations"
    )
    total: int = Field(..., description="Total number of conversations")
    page: int = Field(..., description="Current page")
    per_page: int = Field(..., description="Items per page")


@router.post("/conversations", response_model=dict[str, Any])
async def create_conversation(
    request: SecureConversationCreateRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Create a new conversation with hybrid mode support.

    Args:
        title: Conversation title
        assistant_id: Assistant ID
        description: Conversation description
        current_user_id: Current user ID
        db: Database session

    Returns:
        Dict: Created conversation data
    """
    try:
        conversation = conversation_service.create_conversation_simple(
            user_id=current_user_id,
            assistant_id=request.assistant_id,
            title=request.title,
            description=request.description,
        )
    except SecurityValidationError as e:
        log_security_event("validation_error", str(e), current_user_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Security validation failed: {str(e)}",
        )

        # Initialize hybrid mode for the new conversation
        from backend.app.services.hybrid_mode_manager import hybrid_mode_manager

        hybrid_mode_manager.initialize_conversation(
            conversation_id=str(conversation.id),
            user_id=current_user_id,
            initial_mode=ConversationMode.AUTO,
        )

        logger.info(f"Created conversation {conversation.id} with hybrid mode support")

        return {
            "id": str(conversation.id),
            "title": conversation.title,
            "description": conversation.description,
            "assistant_id": (
                str(conversation.assistant_id) if conversation.assistant_id else None
            ),
            "created_at": conversation.created_at.isoformat(),
            "hybrid_mode_initialized": True,
        }

    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create conversation: {str(e)}",
        )


@router.get("/conversations", response_model=ConversationListResponse)
async def get_conversations(
    page: int = Query(default=1, ge=1, description="Page number"),
    per_page: int = Query(default=20, ge=1, le=100, description="Items per page"),
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Get user conversations with hybrid mode status.

    Args:
        page: Page number
        per_page: Items per page
        current_user_id: Current user ID
        db: Database session

    Returns:
        ConversationListResponse: List of conversations with hybrid mode status
    """
    try:
        conversations = conversation_service.get_user_conversations_paginated(
            user_id=current_user_id,
            skip=(page - 1) * per_page,
            limit=per_page,
        )

        # Add hybrid mode status to each conversation
        from backend.app.services.hybrid_mode_manager import hybrid_mode_manager

        enhanced_conversations = []

        for conv in conversations:
            conv_data = {
                "id": str(conv.id),
                "title": conv.title,
                "description": conv.description,
                "assistant_id": str(conv.assistant_id) if conv.assistant_id else None,
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat(),
                "message_count": conv.message_count,
                "is_active": conv.is_active,
            }

            # Add hybrid mode status
            hybrid_state = hybrid_mode_manager.get_state(str(conv.id))
            if hybrid_state:
                conv_data["hybrid_mode"] = {
                    "current_mode": hybrid_state.current_mode.value,
                    "last_mode_change": hybrid_state.last_mode_change.isoformat(),
                    "auto_mode_enabled": hybrid_state.config.auto_mode_enabled,
                }
            else:
                conv_data["hybrid_mode"] = None

            enhanced_conversations.append(conv_data)

        total = len(conversations)

        return ConversationListResponse(
            conversations=enhanced_conversations,
            total=total,
            page=page,
            per_page=per_page,
        )

    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversations: {str(e)}",
        )


@router.post(
    "/conversations/{conversation_id}/messages", response_model=ChatMessageResponse
)
@rate_limit_chat
async def send_message(
    conversation_id: str,
    request: SecureChatMessageRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Send a message to a conversation with hybrid mode support.

    Args:
        conversation_id: Conversation ID
        request: Chat message request
        current_user_id: Current user ID
        db: Database session

    Returns:
        ChatMessageResponse: Response with structured output
    """
    try:
        # Verify conversation access
        conversation = conversation_service.get_conversation(
            conversation_id, current_user_id
        )
        if not conversation or str(conversation.user_id) != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found or access denied",
            )

        # Add user message to conversation
        user_message = conversation_service.add_message(
            conversation_id=conversation_id,
            user_id=current_user_id,
            content=request.message,
            role="user",
            metadata=request.metadata,
        )

        # Process message with hybrid mode support
        result = await assistant_engine.process_message(
            user_id=current_user_id,
            conversation_id=conversation_id,
            message=request.message,
            assistant_id=request.assistant_id,
            use_knowledge_base=request.use_knowledge_base,
            use_tools=request.use_tools,
            max_context_chunks=request.max_context_chunks,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            model=request.model,
            force_mode=request.force_mode,
            metadata=request.metadata,
        )

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.error_message or "Failed to process message",
            )

        # Extract structured response data
        mode_decision = None
        reasoning_process = None

        if result.structured_response:
            mode_decision = result.structured_response.mode_decision.dict()
            reasoning_process = [
                step.dict() for step in result.structured_response.reasoning_process
            ]

        return ChatMessageResponse(
            success=True,
            content=result.content,
            conversation_id=conversation_id,
            message_id=str(user_message.id),
            model_used=result.model_used,
            tokens_used=result.tokens_used,
            processing_time=result.processing_time,
            tool_calls=result.tool_calls,
            mode_decision=mode_decision,
            reasoning_process=reasoning_process,
        )

    except SecurityValidationError as e:
        log_security_event("validation_error", str(e), current_user_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Security validation failed: {str(e)}",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}",
        )


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: str,
    page: int = Query(default=1, ge=1, description="Page number"),
    per_page: int = Query(default=50, ge=1, le=200, description="Items per page"),
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Get conversation messages with hybrid mode metadata.

    Args:
        conversation_id: Conversation ID
        page: Page number
        per_page: Items per page
        current_user_id: Current user ID
        db: Database session

    Returns:
        List[Dict]: Messages with hybrid mode metadata
    """
    try:
        # Verify conversation access
        conversation = conversation_service.get_conversation(
            conversation_id, current_user_id
        )
        if not conversation or str(conversation.user_id) != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found or access denied",
            )

        messages = conversation_service.get_conversation_messages(
            conversation_id=conversation_id,
            skip=(page - 1) * per_page,
            limit=per_page,
        )

        # Enhance messages with hybrid mode metadata
        enhanced_messages = []
        for msg in messages:
            msg_data = {
                "id": str(msg.id),
                "content": msg.content,
                "role": msg.role.value,
                "message_type": msg.message_type.value,
                "created_at": msg.created_at.isoformat(),
                "tokens_used": msg.tokens_used,
                "model_used": msg.model_used,
            }

            # Add hybrid mode metadata if available
            if msg.message_metadata and msg.role.value == "assistant":
                if "mode_decision" in msg.message_metadata:
                    msg_data["mode_decision"] = msg.message_metadata["mode_decision"]
                if "reasoning_process" in msg.message_metadata:
                    msg_data["reasoning_process"] = msg.message_metadata[
                        "reasoning_process"
                    ]
                if "tool_calls" in msg.message_metadata:
                    msg_data["tool_calls"] = msg.message_metadata["tool_calls"]

            enhanced_messages.append(msg_data)

        return {
            "messages": enhanced_messages,
            "total": len(enhanced_messages),
            "page": page,
            "per_page": per_page,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation messages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversation messages: {str(e)}",
        )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Delete a conversation and clean up hybrid mode state.

    Args:
        conversation_id: Conversation ID
        current_user_id: Current user ID
        db: Database session

    Returns:
        Dict: Deletion result
    """
    try:
        # Verify conversation access
        conversation = conversation_service.get_conversation(
            conversation_id, current_user_id
        )
        if not conversation or str(conversation.user_id) != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found or access denied",
            )

        # Delete conversation
        conversation_service.delete_conversation(conversation_id, current_user_id)

        # Clean up hybrid mode state
        from backend.app.services.hybrid_mode_manager import hybrid_mode_manager

        hybrid_mode_manager.cleanup_conversation(conversation_id)

        logger.info(
            f"Deleted conversation {conversation_id} and cleaned up hybrid mode state"
        )

        return {"success": True, "message": "Conversation deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete conversation: {str(e)}",
        )


@router.get("/conversations/{conversation_id}/mode/status")
async def get_conversation_mode_status(
    conversation_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Get the current hybrid mode status for a conversation.

    Args:
        conversation_id: Conversation ID
        current_user_id: Current user ID
        db: Database session

    Returns:
        Dict: Hybrid mode status
    """
    try:
        # Verify conversation access
        conversation = conversation_service.get_conversation(
            conversation_id, current_user_id
        )
        if not conversation or str(conversation.user_id) != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found or access denied",
            )

        from backend.app.services.hybrid_mode_manager import hybrid_mode_manager

        state = hybrid_mode_manager.get_state(conversation_id)

        if not state:
            return {
                "hybrid_mode_initialized": False,
                "current_mode": None,
                "config": None,
            }

        return {
            "hybrid_mode_initialized": True,
            "current_mode": state.current_mode.value,
            "last_mode_change": state.last_mode_change.isoformat(),
            "config": {
                "auto_mode_enabled": state.config.auto_mode_enabled,
                "complexity_threshold": state.config.complexity_threshold,
                "confidence_threshold": state.config.confidence_threshold,
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation mode status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversation mode status: {str(e)}",
        )
