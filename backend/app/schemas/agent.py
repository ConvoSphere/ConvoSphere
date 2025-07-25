"""
Pydantic v2 schemas for AI Agent framework.

This module provides comprehensive schemas for AI agent management
with full Pydantic v2 validation and type safety.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ToolCall(BaseModel):
    """Tool call schema for AI agent framework."""

    id: str = Field(..., description="Tool call ID")
    name: str = Field(..., min_length=1, max_length=200, description="Tool name")
    arguments: dict[str, Any] = Field(
        default_factory=dict,
        description="Tool arguments",
    )
    result: Any | None = Field(None, description="Tool execution result")
    error: str | None = Field(None, description="Tool execution error")
    status: str = Field(
        default="pending",
        pattern="^(pending|running|completed|failed)$",
        description="Tool execution status",
    )
    start_time: datetime | None = Field(None, description="Execution start time")
    end_time: datetime | None = Field(None, description="Execution end time")
    execution_time: float | None = Field(
        None,
        ge=0,
        description="Execution time in seconds",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate tool name."""
        if not v or not v.strip():
            raise ValueError("Tool name cannot be empty")
        return v.strip()

    @field_validator("arguments")
    @classmethod
    def validate_arguments(cls, v: dict[str, Any]) -> dict[str, Any]:
        """Validate tool arguments."""
        if not isinstance(v, dict):
            raise ValueError("Arguments must be a dictionary")
        return v

    @field_validator("execution_time")
    @classmethod
    def validate_execution_time(cls, v: float | None) -> float | None:
        """Validate execution time."""
        if v is not None and v < 0:
            raise ValueError("Execution time cannot be negative")
        return v

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        extra="forbid",
    )


class AgentConfig(BaseModel):
    """AI agent configuration schema."""

    name: str = Field(..., min_length=1, max_length=200, description="Agent name")
    description: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Agent description",
    )
    system_prompt: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="System prompt",
    )
    tools: list[str] = Field(
        default_factory=list,
        max_length=50,
        description="List of tool names",
    )
    model: str = Field(
        default="gpt-4",
        min_length=1,
        max_length=100,
        description="AI model to use",
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Model temperature",
    )
    max_tokens: int = Field(
        default=4096,
        ge=1,
        le=100000,
        description="Maximum tokens for response",
    )
    max_context_length: int = Field(
        default=8000,
        ge=1000,
        le=200000,
        description="Maximum context length",
    )
    personality: str | None = Field(
        None,
        max_length=5000,
        description="Agent personality description",
    )
    instructions: str | None = Field(
        None,
        max_length=10000,
        description="Additional instructions",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate agent name."""
        if not v or not v.strip():
            raise ValueError("Agent name cannot be empty")
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate agent description."""
        if not v or not v.strip():
            raise ValueError("Agent description cannot be empty")
        return v.strip()

    @field_validator("system_prompt")
    @classmethod
    def validate_system_prompt(cls, v: str) -> str:
        """Validate system prompt."""
        if not v or not v.strip():
            raise ValueError("System prompt cannot be empty")
        if len(v) > 10000:
            raise ValueError("System prompt too long (max 10000 characters)")
        return v.strip()

    @field_validator("tools")
    @classmethod
    def validate_tools(cls, v: list[str]) -> list[str]:
        """Validate tools list."""
        if len(v) > 50:
            raise ValueError("Maximum 50 tools allowed")
        # Remove duplicates and empty strings while preserving order
        seen = set()
        cleaned_tools = []
        for tool in v:
            if tool and tool.strip():
                clean_tool = tool.strip()
                if clean_tool not in seen:
                    seen.add(clean_tool)
                    cleaned_tools.append(clean_tool)
        return cleaned_tools

    @field_validator("personality")
    @classmethod
    def validate_personality(cls, v: str | None) -> str | None:
        """Validate personality description."""
        if v is not None and not v.strip():
            raise ValueError("Personality cannot be empty when provided")
        return v.strip() if v else None

    @field_validator("instructions")
    @classmethod
    def validate_instructions(cls, v: str | None) -> str | None:
        """Validate instructions."""
        if v is not None and not v.strip():
            raise ValueError("Instructions cannot be empty when provided")
        return v.strip() if v else None

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        extra="forbid",
    )


class AgentResponseSchema(BaseModel):
    """AI agent response schema."""

    content: str = Field(..., min_length=1, description="Response content")
    tool_calls: list[ToolCall] = Field(
        default_factory=list,
        description="Tool calls made by the agent",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Response metadata",
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Response confidence score",
    )
    model_used: str = Field(..., description="Model used for response")
    tokens_used: int = Field(..., ge=0, description="Tokens used")
    processing_time: float = Field(..., ge=0, description="Processing time in seconds")
    context_used: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Context information used",
    )

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate response content."""
        if not v or not v.strip():
            raise ValueError("Response content cannot be empty")
        return v.strip()

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        """Validate confidence score."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v

    @field_validator("tokens_used")
    @classmethod
    def validate_tokens_used(cls, v: int) -> int:
        """Validate tokens used."""
        if v < 0:
            raise ValueError("Tokens used cannot be negative")
        return v

    @field_validator("processing_time")
    @classmethod
    def validate_processing_time(cls, v: float) -> float:
        """Validate processing time."""
        if v < 0:
            raise ValueError("Processing time cannot be negative")
        return v

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        extra="forbid",
    )


class AgentState(BaseModel):
    """AI agent state schema."""

    agent_id: UUID = Field(..., description="Agent ID")
    conversation_id: UUID = Field(..., description="Conversation ID")
    current_step: int = Field(..., ge=0, description="Current processing step")
    total_steps: int = Field(..., ge=1, description="Total processing steps")
    status: str = Field(
        default="idle",
        pattern="^(idle|processing|waiting_for_tool|completed|failed)$",
        description="Agent status",
    )
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Agent context",
    )
    tool_calls: list[ToolCall] = Field(
        default_factory=list,
        description="Current tool calls",
    )
    last_activity: datetime = Field(..., description="Last activity timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    @field_validator("current_step")
    @classmethod
    def validate_current_step(cls, v: int) -> int:
        """Validate current step."""
        if v < 0:
            raise ValueError("Current step cannot be negative")
        return v

    @field_validator("total_steps")
    @classmethod
    def validate_total_steps(cls, v: int) -> int:
        """Validate total steps."""
        if v < 1:
            raise ValueError("Total steps must be at least 1")
        return v

    @field_validator("current_step")
    @classmethod
    def validate_step_range(cls, v: int, info) -> int:
        """Validate that current step is within total steps range."""
        if "total_steps" in info.data and v > info.data["total_steps"]:
            raise ValueError("Current step cannot exceed total steps")
        return v

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        extra="forbid",
    )


class AgentCreate(BaseModel):
    """Agent creation schema."""

    config: AgentConfig = Field(..., description="Agent configuration")
    user_id: UUID = Field(..., description="Owner user ID")
    is_public: bool = Field(default=False, description="Public visibility")
    is_template: bool = Field(default=False, description="Template flag")

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        extra="forbid",
    )


class AgentUpdate(BaseModel):
    """Agent update schema."""

    name: str | None = Field(
        None,
        min_length=1,
        max_length=200,
        description="Agent name",
    )
    description: str | None = Field(
        None,
        min_length=1,
        max_length=2000,
        description="Agent description",
    )
    system_prompt: str | None = Field(
        None,
        min_length=1,
        max_length=10000,
        description="System prompt",
    )
    tools: list[str] | None = Field(
        None,
        max_length=50,
        description="List of tool names",
    )
    model: str | None = Field(
        None,
        min_length=1,
        max_length=100,
        description="AI model to use",
    )
    temperature: float | None = Field(
        None,
        ge=0.0,
        le=2.0,
        description="Model temperature",
    )
    max_tokens: int | None = Field(
        None,
        ge=1,
        le=100000,
        description="Maximum tokens for response",
    )
    max_context_length: int | None = Field(
        None,
        ge=1000,
        le=200000,
        description="Maximum context length",
    )
    personality: str | None = Field(
        None,
        max_length=5000,
        description="Agent personality description",
    )
    instructions: str | None = Field(
        None,
        max_length=10000,
        description="Additional instructions",
    )
    is_public: bool | None = Field(None, description="Public visibility")
    is_template: bool | None = Field(None, description="Template flag")
    metadata: dict[str, Any] | None = Field(None, description="Additional metadata")

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        extra="forbid",
    )


class AgentResponse(BaseModel):
    """Agent response schema."""

    id: UUID = Field(..., description="Agent ID")
    config: AgentConfig = Field(..., description="Agent configuration")
    user_id: UUID = Field(..., description="Owner user ID")
    is_public: bool = Field(..., description="Public visibility")
    is_template: bool = Field(..., description="Template flag")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        extra="forbid",
    )


class AgentListResponse(BaseModel):
    """Agent list response schema."""

    agents: list[AgentResponse] = Field(..., description="List of agents")
    total: int = Field(..., ge=0, description="Total number of agents")
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
