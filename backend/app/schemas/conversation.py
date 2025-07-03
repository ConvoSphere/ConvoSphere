"""
Pydantic schemas for Conversation and Message management (enterprise-ready).
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

from ..models.conversation import MessageRole, MessageType

# --- Message Schemas ---

class MessageBase(BaseModel):
    content: str = Field(..., description="Message content")
    role: MessageRole = Field(..., description="Message role (user, assistant, system, tool)")
    message_type: MessageType = Field(MessageType.TEXT, description="Message type")
    tool_name: Optional[str] = Field(None, description="Tool name (if tool message)")
    tool_input: Optional[Dict[str, Any]] = Field(None, description="Tool input data")
    tool_output: Optional[Dict[str, Any]] = Field(None, description="Tool output data")
    tokens_used: Optional[int] = Field(0, description="Tokens used")
    model_used: Optional[str] = Field(None, description="Model used for this message")
    message_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class MessageCreate(MessageBase):
    pass

class MessageUpdate(BaseModel):
    content: Optional[str] = None
    message_metadata: Optional[Dict[str, Any]] = None

class MessageResponse(MessageBase):
    id: UUID
    conversation_id: UUID
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# --- Conversation Schemas ---

class ConversationBase(BaseModel):
    title: str = Field(..., max_length=500, description="Conversation title")
    description: Optional[str] = Field(None, description="Conversation description")
    conversation_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    tags: Optional[List[str]] = Field(None, description="Tags for classification/search")
    access: Optional[str] = Field("private", description="Access level: private/team/public")
    group_id: Optional[UUID] = Field(None, description="Group/Team ID (for enterprise/multi-user)")
    organization_id: Optional[UUID] = Field(None, description="Organization ID (multi-tenancy)")
    participants: Optional[List[UUID]] = Field(None, description="Additional participant user IDs")

class ConversationCreate(ConversationBase):
    user_id: UUID = Field(..., description="Owner user ID")
    assistant_id: UUID = Field(..., description="Assistant ID")

class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    is_archived: Optional[bool] = None
    conversation_metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    access: Optional[str] = None
    group_id: Optional[UUID] = None
    participants: Optional[List[UUID]] = None

class ConversationResponse(ConversationBase):
    id: UUID
    user_id: UUID
    assistant_id: UUID
    is_active: bool
    is_archived: bool
    message_count: int
    total_tokens: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    messages: Optional[List[MessageResponse]] = []

    class Config:
        from_attributes = True

class ConversationListResponse(BaseModel):
    conversations: List[ConversationResponse]
    total: int
    page: int
    size: int
    pages: int

class ConversationSearchParams(BaseModel):
    query: Optional[str] = Field(None, description="Search query")
    user_id: Optional[UUID] = None
    assistant_id: Optional[UUID] = None
    group_id: Optional[UUID] = None
    organization_id: Optional[UUID] = None
    access: Optional[str] = None
    is_active: Optional[bool] = None
    is_archived: Optional[bool] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(20, ge=1, le=100, description="Page size") 