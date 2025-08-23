"""Conversations endpoints for conversation management (enterprise-ready)."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.models.user import User
from backend.app.models.user import UserRole
from backend.app.schemas.conversation import (
    ConversationCreate,
    ConversationListResponse,
    ConversationResponse,
    ConversationUpdate,
    MessageCreate,
    MessageResponse,
)
from backend.app.services.conversation_service import ConversationService

router = APIRouter()


# API-specific request schema (without user_id)
class ConversationCreateRequest(BaseModel):
    """Create conversation request model for API."""

    assistant_id: str
    title: str | None = None
    description: str | None = None
    conversation_metadata: dict[str, Any] | None = None


# --- Conversation CRUD ---


@router.post(
    "/",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_conversation(
    conversation_data: ConversationCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new conversation."""
    service = ConversationService(db)

    # Create ConversationCreate object with user_id from authenticated user
    conversation_create = ConversationCreate(
        user_id=str(current_user.id),
        assistant_id=conversation_data.assistant_id,
        title=conversation_data.title or "New Conversation",
        description=conversation_data.description,
        conversation_metadata=conversation_data.conversation_metadata,
    )

    return service.create_conversation(conversation_create)


@router.get("/", response_model=ConversationListResponse)
async def list_conversations(
    user_id: str | None = Query(None),
    assistant_id: str | None = Query(None),
    mine: bool | None = Query(False, description="Only current user's conversations"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List conversations (paginated, filterable)."""
    service = ConversationService(db)
    # Default to current user's conversations
    # If mine=true, force current user; otherwise only allow other user_id for admins
    if mine:
        user_id = str(current_user.id)
    else:
        if user_id and user_id != str(current_user.id):
            if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        else:
            user_id = str(current_user.id)
    conversations = service.get_user_conversations(user_id)
    total = len(conversations)
    start = (page - 1) * size
    end = start + size
    page_convs = conversations[start:end]
    return ConversationListResponse(
        conversations=page_convs,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size,
    )


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a conversation by ID."""
    service = ConversationService(db)
    conv = service.get_conversation(conversation_id, str(current_user.id))
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: str,
    update_data: ConversationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a conversation."""
    service = ConversationService(db)
    conv = service.get_conversation(conversation_id, str(current_user.id))
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    # Check access rights
    if not service.has_conversation_access(conversation_id, str(current_user.id)):
        raise HTTPException(status_code=403, detail="Access denied")

    # Only allow update of title/description/metadata for now
    updated_conv = service.update_conversation(conversation_id, update_data.dict())
    if not updated_conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return updated_conv


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a conversation."""
    service = ConversationService(db)
    ok = service.delete_conversation(conversation_id, str(current_user.id))
    if not ok:
        raise HTTPException(status_code=404, detail="Conversation not found")


@router.post("/{conversation_id}/archive", status_code=status.HTTP_200_OK)
async def archive_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Archive a conversation."""
    service = ConversationService(db)
    ok = service.archive_conversation(conversation_id, str(current_user.id))
    if not ok:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"message": "Conversation archived"}


# --- Message Management ---


@router.get("/{conversation_id}/messages", response_model=list[MessageResponse])
async def list_messages(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all messages in a conversation."""
    service = ConversationService(db)
    # Check access rights
    if not service.has_conversation_access(conversation_id, str(current_user.id)):
        raise HTTPException(status_code=403, detail="Access denied")
    return service.get_conversation_messages(conversation_id)


@router.post(
    "/{conversation_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_message(
    conversation_id: str,
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a message to a conversation."""
    service = ConversationService(db)
    # Check access rights
    if not service.has_conversation_access(conversation_id, str(current_user.id)):
        raise HTTPException(status_code=403, detail="Access denied")
    # Create MessageCreate object with conversation_id
    from backend.app.schemas.conversation import MessageCreate as SchemaMessageCreate

    message_create = SchemaMessageCreate(
        conversation_id=conversation_id,
        content=message_data.content,
        role=message_data.role,
        message_type=message_data.message_type,
        message_metadata=message_data.message_metadata,
    )
    return service.add_message(message_create)
