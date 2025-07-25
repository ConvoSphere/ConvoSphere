"""
Pydantic v2 schemas for Conversation and Message management (enterprise-ready).

This module provides comprehensive schemas for conversation and message management
with full Pydantic v2 validation and type safety.
"""

from datetime import UTC, datetime
from typing import Any
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
        description="Message content",
    )
    role: MessageRole = Field(
        ...,
        description="Message role (user, assistant, system, tool)",
    )
    message_type: MessageType = Field(
        MessageType.TEXT,
        description="Message type",
    )
    tool_name: str | None = Field(
        None,
        max_length=200,
        description="Tool name (if tool message)",
    )
    tool_input: dict[str, Any] | None = Field(
        None,
        description="Tool input data",
    )
    tool_output: dict[str, Any] | None = Field(
        None,
        description="Tool output data",
    )
    tokens_used: int | None = Field(
        0,
        ge=0,
        le=100000,
        description="Tokens used",
    )
    model_used: str | None = Field(
        None,
        max_length=100,
        description="Model used for this message",
    )
    message_metadata: dict[str, Any] | None = Field(
        None,
        description="Additional metadata",
    )

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate message content."""
        if not v or not v.strip():
            raise ValueError("Message content cannot be empty")
        return v.strip()

    @field_validator("tool_name")
    @classmethod
    def validate_tool_name(cls, v: str | None) -> str | None:
        """Validate tool name when provided."""
        if v is not None and not v.strip():
            raise ValueError("Tool name cannot be empty when provided")
        return v.strip() if v else None

    @field_validator("tokens_used")
    @classmethod
    def validate_tokens_used(cls, v: int | None) -> int | None:
        """Validate token usage."""
        if v is not None and v < 0:
            raise ValueError("Token usage cannot be negative")
        return v

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        extra="forbid",
    )


class MessageCreate(MessageBase):
    """Message creation schema with relaxed validation."""

    conversation_id: UUID = Field(..., description="Conversation ID")

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        extra="forbid",  # Forbid extra fields
    )


class MessageUpdate(BaseModel):
    content: str | None = None
    message_metadata: dict[str, Any] | None = None


class MessageResponse(MessageBase):
    """Message response schema with full validation."""

    id: UUID = Field(..., description="Message ID")
    conversation_id: UUID = Field(..., description="Conversation ID")
    created_at: datetime | None = Field(None, description="Creation timestamp")
    updated_at: datetime | None = Field(None, description="Last update timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        extra="forbid",
    )


# --- Conversation Schemas ---


class ConversationBase(BaseModel):
    """Base conversation schema with comprehensive validation."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Conversation title",
    )
    description: str | None = Field(
        None,
        max_length=2000,
        description="Conversation description",
    )
    conversation_metadata: dict[str, Any] | None = Field(
        None,
        description="Additional metadata",
    )
    tags: list[str] | None = Field(
        None,
        max_length=20,
        description="Tags for classification/search",
    )
    access: str | None = Field(
        "private",
        pattern="^(private|team|public)$",
        description="Access level: private/team/public",
    )
    group_id: UUID | None = Field(
        None,
        description="Group/Team ID (for enterprise/multi-user)",
    )
    organization_id: UUID | None = Field(
        None,
        description="Organization ID (multi-tenancy)",
    )
    participants: list[UUID] | None = Field(
        None,
        max_length=50,
        description="Additional participant user IDs",
    )

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate conversation title."""
        if not v or not v.strip():
            raise ValueError("Conversation title cannot be empty")
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        """Validate conversation description."""
        if v is not None and not v.strip():
            raise ValueError("Description cannot be empty when provided")
        return v.strip() if v else None

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str] | None) -> list[str] | None:
        """Validate conversation tags."""
        if v is not None:
            # Remove empty tags and duplicates while preserving order
            seen = set()
            cleaned_tags = []
            for tag in v:
                if tag and tag.strip():
                    clean_tag = tag.strip()
                    if clean_tag not in seen:
                        seen.add(clean_tag)
                        cleaned_tags.append(clean_tag)
            if len(cleaned_tags) > 20:
                raise ValueError("Maximum 20 tags allowed")
            return cleaned_tags
        return v

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        extra="forbid",
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
    created_at: datetime | None = Field(None, description="Creation timestamp")
    updated_at: datetime | None = Field(None, description="Last update timestamp")
    messages: list[MessageResponse] | None = Field(
        default_factory=list,
        description="List of messages",
    )

    @field_validator("message_count")
    @classmethod
    def validate_message_count(cls, v: int) -> int:
        """Validate message count."""
        if v < 0:
            raise ValueError("Message count cannot be negative")
        return v

    @field_validator("total_tokens")
    @classmethod
    def validate_total_tokens(cls, v: int) -> int:
        """Validate total tokens."""
        if v < 0:
            raise ValueError("Total tokens cannot be negative")
        return v

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        extra="forbid",
    )


class ConversationListResponse(BaseModel):
    """Conversation list response schema."""

    conversations: list[ConversationResponse] = Field(
        ...,
        description="List of conversations",
    )
    total: int = Field(..., ge=0, description="Total number of conversations")
    page: int = Field(..., ge=1, description="Current page number")
    size: int = Field(..., ge=1, le=100, description="Page size")
    pages: int = Field(..., ge=0, description="Total number of pages")

    @field_validator("total")
    @classmethod
    def validate_total(cls, v: int) -> int:
        """Validate total count."""
        if v < 0:
            raise ValueError("Total count cannot be negative")
        return v

    @field_validator("pages")
    @classmethod
    def validate_pages(cls, v: int) -> int:
        """Validate pages count."""
        if v < 0:
            raise ValueError("Pages count cannot be negative")
        return v

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        extra="forbid",
    )


class ConversationSearchParams(BaseModel):
    """Conversation search parameters schema."""

    query: str | None = Field(
        None,
        max_length=500,
        description="Search query",
    )
    user_id: UUID | None = Field(None, description="User ID filter")
    assistant_id: UUID | None = Field(None, description="Assistant ID filter")
    group_id: UUID | None = Field(None, description="Group ID filter")
    organization_id: UUID | None = Field(None, description="Organization ID filter")
    access: str | None = Field(
        None,
        pattern="^(private|team|public)$",
        description="Access level filter",
    )
    is_active: bool | None = Field(None, description="Active status filter")
    is_archived: bool | None = Field(None, description="Archived status filter")
    created_after: datetime | None = Field(None, description="Created after date")
    created_before: datetime | None = Field(None, description="Created before date")
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(20, ge=1, le=100, description="Page size")

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str | None) -> str | None:
        """Validate search query."""
        if v is not None and not v.strip():
            raise ValueError("Search query cannot be empty when provided")
        return v.strip() if v else None

    @field_validator("created_after", "created_before")
    @classmethod
    def validate_date_range(cls, v: datetime | None) -> datetime | None:
        """Validate date range."""
        if v is not None:
            # Make timezone-aware if it's naive
            if v.tzinfo is None:
                v = v.replace(tzinfo=UTC)
            # Compare with current time in the same timezone
            now = datetime.now(v.tzinfo)
            if v > now:
                raise ValueError("Date cannot be in the future")
        return v

    @field_validator("created_before")
    @classmethod
    def validate_date_order(cls, v: datetime | None, info) -> datetime | None:
        """Validate that created_before is after created_after."""
        if v is not None and "created_after" in info.data:
            created_after = info.data["created_after"]
            if created_after and v <= created_after:
                raise ValueError("created_before must be after created_after")
        return v

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        extra="forbid",
    )
