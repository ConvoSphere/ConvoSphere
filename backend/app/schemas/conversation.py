"""
Pydantic v2 schemas for Conversation and Message management (enterprise-ready).

This module provides comprehensive schemas for conversation and message management
with full Pydantic v2 validation and type safety.
"""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..models.conversation import MessageRole, MessageType

# --- Message Schemas ---


class MessageBase(BaseModel):
    """Base message schema with comprehensive validation."""
    
    content: str = Field(
        ..., 
        min_length=1, 
        max_length=50000, 
        description="Message content"
    )
    role: MessageRole = Field(
        ..., 
        description="Message role (user, assistant, system, tool)"
    )
    message_type: MessageType = Field(
        MessageType.TEXT, 
        description="Message type"
    )
    tool_name: Optional[str] = Field(
        None, 
        max_length=200, 
        description="Tool name (if tool message)"
    )
    tool_input: Optional[dict[str, Any]] = Field(
        None, 
        description="Tool input data"
    )
    tool_output: Optional[dict[str, Any]] = Field(
        None, 
        description="Tool output data"
    )
    tokens_used: Optional[int] = Field(
        0, 
        ge=0, 
        le=100000, 
        description="Tokens used"
    )
    model_used: Optional[str] = Field(
        None, 
        max_length=100, 
        description="Model used for this message"
    )
    message_metadata: Optional[dict[str, Any]] = Field(
        None, 
        description="Additional metadata"
    )

    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate message content."""
        if not v or not v.strip():
            raise ValueError('Message content cannot be empty')
        return v.strip()

    @field_validator('tool_name')
    @classmethod
    def validate_tool_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate tool name when provided."""
        if v is not None and not v.strip():
            raise ValueError('Tool name cannot be empty when provided')
        return v.strip() if v else None

    @field_validator('tokens_used')
    @classmethod
    def validate_tokens_used(cls, v: Optional[int]) -> Optional[int]:
        """Validate token usage."""
        if v is not None and v < 0:
            raise ValueError('Token usage cannot be negative')
        return v

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        extra='forbid',
    )


class MessageCreate(MessageBase):
    pass


class MessageUpdate(BaseModel):
    content: str | None = None
    message_metadata: dict[str, Any] | None = None


class MessageResponse(MessageBase):
    """Message response schema with full validation."""
    
    id: UUID = Field(..., description="Message ID")
    conversation_id: UUID = Field(..., description="Conversation ID")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        extra='forbid',
    )


# --- Conversation Schemas ---


class ConversationBase(BaseModel):
    """Base conversation schema with comprehensive validation."""
    
    title: str = Field(
        ..., 
        min_length=1, 
        max_length=500, 
        description="Conversation title"
    )
    description: Optional[str] = Field(
        None, 
        max_length=2000, 
        description="Conversation description"
    )
    conversation_metadata: Optional[dict[str, Any]] = Field(
        None, 
        description="Additional metadata"
    )
    tags: Optional[list[str]] = Field(
        None, 
        max_length=20, 
        description="Tags for classification/search"
    )
    access: Optional[str] = Field(
        "private", 
        pattern="^(private|team|public)$",
        description="Access level: private/team/public"
    )
    group_id: Optional[UUID] = Field(
        None, 
        description="Group/Team ID (for enterprise/multi-user)"
    )
    organization_id: Optional[UUID] = Field(
        None, 
        description="Organization ID (multi-tenancy)"
    )
    participants: Optional[list[UUID]] = Field(
        None, 
        max_length=50, 
        description="Additional participant user IDs"
    )

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate conversation title."""
        if not v or not v.strip():
            raise ValueError('Conversation title cannot be empty')
        return v.strip()

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate conversation description."""
        if v is not None and not v.strip():
            raise ValueError('Description cannot be empty when provided')
        return v.strip() if v else None

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        """Validate conversation tags."""
        if v is not None:
            # Remove empty tags and duplicates
            cleaned_tags = list(set(tag.strip() for tag in v if tag and tag.strip()))
            if len(cleaned_tags) > 20:
                raise ValueError('Maximum 20 tags allowed')
            return cleaned_tags
        return v

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        extra='forbid',
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
    """Conversation response schema with full validation."""
    
    id: UUID = Field(..., description="Conversation ID")
    user_id: UUID = Field(..., description="Owner user ID")
    assistant_id: UUID = Field(..., description="Assistant ID")
    is_active: bool = Field(..., description="Active status")
    is_archived: bool = Field(..., description="Archived status")
    message_count: int = Field(..., ge=0, description="Number of messages")
    total_tokens: int = Field(..., ge=0, description="Total tokens used")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    messages: Optional[list[MessageResponse]] = Field(
        default_factory=list, 
        description="List of messages"
    )

    @field_validator('message_count')
    @classmethod
    def validate_message_count(cls, v: int) -> int:
        """Validate message count."""
        if v < 0:
            raise ValueError('Message count cannot be negative')
        return v

    @field_validator('total_tokens')
    @classmethod
    def validate_total_tokens(cls, v: int) -> int:
        """Validate total tokens."""
        if v < 0:
            raise ValueError('Total tokens cannot be negative')
        return v

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        extra='forbid',
    )


class ConversationListResponse(BaseModel):
    """Conversation list response schema."""
    
    conversations: list[ConversationResponse] = Field(
        ..., 
        description="List of conversations"
    )
    total: int = Field(..., ge=0, description="Total number of conversations")
    page: int = Field(..., ge=1, description="Current page number")
    size: int = Field(..., ge=1, le=100, description="Page size")
    pages: int = Field(..., ge=0, description="Total number of pages")

    @field_validator('total')
    @classmethod
    def validate_total(cls, v: int) -> int:
        """Validate total count."""
        if v < 0:
            raise ValueError('Total count cannot be negative')
        return v

    @field_validator('pages')
    @classmethod
    def validate_pages(cls, v: int) -> int:
        """Validate pages count."""
        if v < 0:
            raise ValueError('Pages count cannot be negative')
        return v

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        extra='forbid',
    )


class ConversationSearchParams(BaseModel):
    """Conversation search parameters schema."""
    
    query: Optional[str] = Field(
        None, 
        max_length=500, 
        description="Search query"
    )
    user_id: Optional[UUID] = Field(None, description="User ID filter")
    assistant_id: Optional[UUID] = Field(None, description="Assistant ID filter")
    group_id: Optional[UUID] = Field(None, description="Group ID filter")
    organization_id: Optional[UUID] = Field(None, description="Organization ID filter")
    access: Optional[str] = Field(
        None, 
        pattern="^(private|team|public)$",
        description="Access level filter"
    )
    is_active: Optional[bool] = Field(None, description="Active status filter")
    is_archived: Optional[bool] = Field(None, description="Archived status filter")
    created_after: Optional[datetime] = Field(None, description="Created after date")
    created_before: Optional[datetime] = Field(None, description="Created before date")
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(20, ge=1, le=100, description="Page size")

    @field_validator('query')
    @classmethod
    def validate_query(cls, v: Optional[str]) -> Optional[str]:
        """Validate search query."""
        if v is not None and not v.strip():
            raise ValueError('Search query cannot be empty when provided')
        return v.strip() if v else None

    @field_validator('created_after', 'created_before')
    @classmethod
    def validate_date_range(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Validate date range."""
        if v is not None and v > datetime.now():
            raise ValueError('Date cannot be in the future')
        return v

    @field_validator('created_before')
    @classmethod
    def validate_date_order(cls, v: Optional[datetime], info) -> Optional[datetime]:
        """Validate that created_before is after created_after."""
        if v is not None and 'created_after' in info.data:
            created_after = info.data['created_after']
            if created_after and v <= created_after:
                raise ValueError('created_before must be after created_after')
        return v

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        extra='forbid',
    )
