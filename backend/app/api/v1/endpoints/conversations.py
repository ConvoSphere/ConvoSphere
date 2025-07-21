"""Conversations endpoints for conversation management (enterprise-ready)."""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import json
import os
from datetime import datetime

from ....core.database import get_db
from ....core.security import get_current_user, require_permission
from ....models.user import User
from ....schemas.conversation import (
    ConversationCreate, ConversationUpdate, ConversationResponse, ConversationListResponse,
    MessageCreate, MessageResponse
)
from ....services.conversation_service import ConversationService

router = APIRouter()

# Enhanced Chat Features Models
class MessageSearchRequest(BaseModel):
    """Message search request model."""
    query: str
    filters: Optional[Dict[str, Any]] = None
    limit: Optional[int] = 50
    offset: Optional[int] = 0

class MessageSearchResponse(BaseModel):
    """Message search response model."""
    messages: List[MessageResponse]
    total: int
    query: str

class ConversationExportRequest(BaseModel):
    """Conversation export request model."""
    format: str  # 'json', 'markdown', 'pdf', 'txt'
    include_metadata: bool = True
    include_attachments: bool = True

class ConversationExportResponse(BaseModel):
    """Conversation export response model."""
    download_url: str
    filename: str
    size: int
    expires_at: str

class ConversationContext(BaseModel):
    """Conversation context model."""
    conversation_id: str
    context_window: int
    relevant_documents: List[str]
    assistant_context: Dict[str, Any]
    user_preferences: Dict[str, Any]

class ConversationContextUpdate(BaseModel):
    """Conversation context update model."""
    context_window: Optional[int] = None
    relevant_documents: Optional[List[str]] = None
    assistant_context: Optional[Dict[str, Any]] = None
    user_preferences: Optional[Dict[str, Any]] = None

class MessageReactionCreate(BaseModel):
    """Message reaction create model."""
    emoji: str

class MessageReactionResponse(BaseModel):
    """Message reaction response model."""
    id: str
    emoji: str
    user_id: str
    created_at: str

# --- Conversation CRUD ---

@router.post("/", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation_data: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new conversation."""
    service = ConversationService(db)
    conv = service.create_conversation(
        user_id=str(conversation_data.user_id),
        assistant_id=str(conversation_data.assistant_id),
        title=conversation_data.title
    )
    return conv

@router.get("/", response_model=ConversationListResponse)
async def list_conversations(
    user_id: Optional[str] = Query(None),
    assistant_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None, description="Filter by status: active, archived, deleted"),
    tags: Optional[str] = Query(None, description="Comma-separated tags to filter by"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List conversations (paginated, filterable)."""
    service = ConversationService(db)
    # For now, only user_id filter is supported
    user_id = user_id or str(current_user.id)
    conversations = service.get_user_conversations(user_id)
    
    # Apply filters
    if assistant_id:
        conversations = [c for c in conversations if c.get("assistant_id") == assistant_id]
    if status:
        conversations = [c for c in conversations if c.get("status") == status]
    if tags:
        tag_list = [t.strip() for t in tags.split(',')]
        conversations = [c for c in conversations if any(tag in c.get("tags", []) for tag in tag_list)]
    
    total = len(conversations)
    start = (page - 1) * size
    end = start + size
    page_convs = conversations[start:end]
    return ConversationListResponse(
        conversations=page_convs,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )

@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a conversation by ID."""
    service = ConversationService(db)
    conv = service.get_conversation(conversation_id, str(current_user.id))
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv

@router.put("/{conversation_id}", response_model=ConversationResponse)
@require_permission("conversation:write")
async def update_conversation(
    conversation_id: str,
    update_data: ConversationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a conversation."""
    service = ConversationService(db)
    conv = service.get_conversation(conversation_id, str(current_user.id))
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Update conversation with new data
    updated_conv = service.update_conversation(
        conversation_id=conversation_id,
        user_id=str(current_user.id),
        update_data=update_data.dict(exclude_unset=True)
    )
    return updated_conv

@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_permission("conversation:delete")
async def delete_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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
    current_user: User = Depends(get_current_user)
):
    """Archive a conversation."""
    service = ConversationService(db)
    ok = service.archive_conversation(conversation_id, str(current_user.id))
    if not ok:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"message": "Conversation archived"}

# --- Enhanced Message Management ---

@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def list_messages(
    conversation_id: str,
    limit: Optional[int] = Query(50, ge=1, le=100),
    offset: Optional[int] = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List messages in a conversation with pagination."""
    service = ConversationService(db)
    # TODO: check access rights
    messages = service.get_conversation_messages(conversation_id, limit=limit, offset=offset)
    return messages

@router.post("/{conversation_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def add_message(
    conversation_id: str,
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a message to a conversation."""
    service = ConversationService(db)
    # TODO: check access rights
    return service.add_message(
        conversation_id=conversation_id,
        user_id=str(current_user.id),
        content=message_data.content,
        role=message_data.role,
        message_type=message_data.message_type,
        metadata=message_data.message_metadata
    )

# --- Message Search ---

@router.post("/{conversation_id}/messages/search", response_model=MessageSearchResponse)
async def search_messages(
    conversation_id: str,
    search_request: MessageSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Search messages in a conversation."""
    service = ConversationService(db)
    
    # Verify conversation access
    conv = service.get_conversation(conversation_id, str(current_user.id))
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Search messages
    messages, total = service.search_messages(
        conversation_id=conversation_id,
        query=search_request.query,
        filters=search_request.filters,
        limit=search_request.limit,
        offset=search_request.offset
    )
    
    return MessageSearchResponse(
        messages=messages,
        total=total,
        query=search_request.query
    )

# --- Message Deletion ---

@router.delete("/{conversation_id}/messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    conversation_id: str,
    message_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a message from a conversation."""
    service = ConversationService(db)
    
    # Verify conversation access
    conv = service.get_conversation(conversation_id, str(current_user.id))
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Delete message (only own messages)
    success = service.delete_message(
        conversation_id=conversation_id,
        message_id=message_id,
        user_id=str(current_user.id)
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Message not found or not authorized")

# --- Message Reactions ---

@router.post("/{conversation_id}/messages/{message_id}/reactions", response_model=MessageReactionResponse)
async def add_message_reaction(
    conversation_id: str,
    message_id: str,
    reaction_data: MessageReactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a reaction to a message."""
    service = ConversationService(db)
    
    # Verify conversation access
    conv = service.get_conversation(conversation_id, str(current_user.id))
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Add reaction
    reaction = service.add_message_reaction(
        conversation_id=conversation_id,
        message_id=message_id,
        user_id=str(current_user.id),
        emoji=reaction_data.emoji
    )
    
    if not reaction:
        raise HTTPException(status_code=400, detail="Failed to add reaction")
    
    return reaction

@router.delete("/{conversation_id}/messages/{message_id}/reactions/{reaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_message_reaction(
    conversation_id: str,
    message_id: str,
    reaction_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a reaction from a message."""
    service = ConversationService(db)
    
    # Verify conversation access
    conv = service.get_conversation(conversation_id, str(current_user.id))
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Remove reaction (only own reactions)
    success = service.remove_message_reaction(
        conversation_id=conversation_id,
        message_id=message_id,
        reaction_id=reaction_id,
        user_id=str(current_user.id)
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Reaction not found or not authorized")

# --- Conversation Export ---

@router.post("/{conversation_id}/export", response_model=ConversationExportResponse)
async def export_conversation(
    conversation_id: str,
    export_request: ConversationExportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export a conversation in various formats."""
    service = ConversationService(db)
    
    # Verify conversation access
    conv = service.get_conversation(conversation_id, str(current_user.id))
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Validate export format
    valid_formats = ['json', 'markdown', 'pdf', 'txt']
    if export_request.format not in valid_formats:
        raise HTTPException(status_code=400, detail=f"Invalid format. Must be one of: {valid_formats}")
    
    # Export conversation
    export_result = service.export_conversation(
        conversation_id=conversation_id,
        format=export_request.format,
        include_metadata=export_request.include_metadata,
        include_attachments=export_request.include_attachments
    )
    
    if not export_result:
        raise HTTPException(status_code=500, detail="Failed to export conversation")
    
    return export_result

@router.get("/{conversation_id}/export/download/{filename}")
async def download_export(
    conversation_id: str,
    filename: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Download an exported conversation file."""
    service = ConversationService(db)
    
    # Verify conversation access
    conv = service.get_conversation(conversation_id, str(current_user.id))
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Check if file exists
    file_path = os.path.join("exports", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Export file not found")
    
    # Verify filename belongs to this conversation
    if not filename.startswith(f"conversation_{conversation_id}_"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    )

# --- Conversation Context Management ---

@router.get("/{conversation_id}/context", response_model=ConversationContext)
async def get_conversation_context(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get conversation context."""
    service = ConversationService(db)
    
    # Verify conversation access
    conv = service.get_conversation(conversation_id, str(current_user.id))
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Get context
    context = service.get_conversation_context(conversation_id)
    if not context:
        # Return default context
        context = ConversationContext(
            conversation_id=conversation_id,
            context_window=50,
            relevant_documents=[],
            assistant_context={},
            user_preferences={}
        )
    
    return context

@router.put("/{conversation_id}/context", response_model=ConversationContext)
async def update_conversation_context(
    conversation_id: str,
    context_update: ConversationContextUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update conversation context."""
    service = ConversationService(db)
    
    # Verify conversation access
    conv = service.get_conversation(conversation_id, str(current_user.id))
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Update context
    updated_context = service.update_conversation_context(
        conversation_id=conversation_id,
        context_update=context_update.dict(exclude_unset=True)
    )
    
    if not updated_context:
        raise HTTPException(status_code=500, detail="Failed to update context")
    
    return updated_context 