"""
Pydantic schemas for Conversation and Message management (enterprise-ready).
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from ..models.conversation import MessageRole, MessageType

# --- Message Schemas ---


class MessageBase(BaseModel):
    content: str = Field(..., description="Message content")
    role: MessageRole = Field(
        ..., description="Message role (user, assistant, system, tool)",
    )
    message_type: MessageType = Field(MessageType.TEXT, description="Message type")
    tool_name: str | None = Field(None, description="Tool name (if tool message)")
    tool_input: dict[str, Any] | None = Field(None, description="Tool input data")
    tool_output: dict[str, Any] | None = Field(None, description="Tool output data")
    tokens_used: int | None = Field(0, description="Tokens used")
    model_used: str | None = Field(None, description="Model used for this message")
    message_metadata: dict[str, Any] | None = Field(
        None, description="Additional metadata",
    )


class MessageCreate(MessageBase):
    pass


class MessageUpdate(BaseModel):
    content: str | None = None
    message_metadata: dict[str, Any] | None = None


class MessageResponse(MessageBase):
    id: UUID
    conversation_id: UUID
    created_at: datetime | None
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


# --- Conversation Schemas ---


class ConversationBase(BaseModel):
    title: str = Field(..., max_length=500, description="Conversation title")
    description: str | None = Field(None, description="Conversation description")
    conversation_metadata: dict[str, Any] | None = Field(
        None, description="Additional metadata",
    )
    tags: list[str] | None = Field(None, description="Tags for classification/search")
    access: str | None = Field(
        "private", description="Access level: private/team/public",
    )
    group_id: UUID | None = Field(
        None, description="Group/Team ID (for enterprise/multi-user)",
    )
    organization_id: UUID | None = Field(
        None, description="Organization ID (multi-tenancy)",
    )
    participants: list[UUID] | None = Field(
        None, description="Additional participant user IDs",
    )


class ConversationCreate(ConversationBase):
    user_id: UUID = Field(..., description="Owner user ID")
    assistant_id: UUID = Field(..., description="Assistant ID")


class ConversationUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    is_active: bool | None = None
    is_archived: bool | None = None
    conversation_metadata: dict[str, Any] | None = None
    tags: list[str] | None = None
    access: str | None = None
    group_id: UUID | None = None
    participants: list[UUID] | None = None


class ConversationResponse(ConversationBase):
    id: UUID
    user_id: UUID
    assistant_id: UUID
    is_active: bool
    is_archived: bool
    message_count: int
    total_tokens: int
    created_at: datetime | None
    updated_at: datetime | None
    messages: list[MessageResponse] | None = []

    model_config = ConfigDict(from_attributes=True)


class ConversationListResponse(BaseModel):
    conversations: list[ConversationResponse]
    total: int
    page: int
    size: int
    pages: int


class ConversationSearchParams(BaseModel):
    query: str | None = Field(None, description="Search query")
    user_id: UUID | None = None
    assistant_id: UUID | None = None
    group_id: UUID | None = None
    organization_id: UUID | None = None
    access: str | None = None
    is_active: bool | None = None
    is_archived: bool | None = None
    created_after: datetime | None = None
    created_before: datetime | None = None
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(20, ge=1, le=100, description="Page size")
