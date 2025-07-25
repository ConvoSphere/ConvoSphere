"""
Hybrid Mode Management Schemas.

This module defines schemas for the hybrid chat/agent mode system
with structured output, agent memory, and reasoning capabilities.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class ConversationMode(str, Enum):
    """Conversation mode enumeration."""

    CHAT = "chat"
    AGENT = "agent"
    AUTO = "auto"


class ModeDecisionReason(str, Enum):
    """Reason for mode decision."""

    USER_REQUEST = "user_request"
    COMPLEXITY_HIGH = "complexity_high"
    TOOLS_AVAILABLE = "tools_available"
    CONTEXT_REQUIRES_AGENT = "context_requires_agent"
    SIMPLE_QUERY = "simple_query"
    CONFIDENCE_LOW = "confidence_low"
    CONTINUATION = "continuation"


class AgentMemory(BaseModel):
    """Agent memory for context retention."""

    conversation_id: UUID = Field(..., description="Conversation ID")
    user_id: UUID = Field(..., description="User ID")
    memory_type: str = Field(..., description="Type of memory (short_term, long_term)")
    content: Dict[str, Any] = Field(..., description="Memory content")
    importance: float = Field(default=0.5, ge=0.0, le=1.0, description="Memory importance")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")

    @field_validator("importance")
    @classmethod
    def validate_importance(cls, v: float) -> float:
        """Validate importance score."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Importance must be between 0.0 and 1.0")
        return v


class AgentReasoning(BaseModel):
    """Agent reasoning process and decision making."""

    reasoning_id: UUID = Field(..., description="Reasoning ID")
    conversation_id: UUID = Field(..., description="Conversation ID")
    step: int = Field(..., ge=1, description="Reasoning step number")
    thought: str = Field(..., min_length=1, description="Reasoning thought")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in reasoning")
    evidence: List[str] = Field(default_factory=list, description="Supporting evidence")
    conclusion: Optional[str] = Field(None, description="Reasoning conclusion")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        """Validate confidence score."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v


class ModeDecision(BaseModel):
    """Structured output for mode decision making."""

    conversation_id: UUID = Field(..., description="Conversation ID")
    user_message: str = Field(..., description="User message that triggered decision")
    current_mode: ConversationMode = Field(..., description="Current conversation mode")
    recommended_mode: ConversationMode = Field(..., description="Recommended next mode")
    reason: ModeDecisionReason = Field(..., description="Reason for mode decision")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in decision")
    complexity_score: float = Field(..., ge=0.0, le=1.0, description="Query complexity score")
    available_tools: List[str] = Field(default_factory=list, description="Available tools")
    context_relevance: float = Field(..., ge=0.0, le=1.0, description="Context relevance score")
    reasoning_steps: List[AgentReasoning] = Field(default_factory=list, description="Reasoning process")
    memory_context: List[AgentMemory] = Field(default_factory=list, description="Relevant memory context")
    timestamp: datetime = Field(default_factory=datetime.now, description="Decision timestamp")

    @field_validator("confidence", "complexity_score", "context_relevance")
    @classmethod
    def validate_scores(cls, v: float) -> float:
        """Validate score values."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Score must be between 0.0 and 1.0")
        return v


class HybridModeConfig(BaseModel):
    """Configuration for hybrid mode management."""

    auto_mode_enabled: bool = Field(default=True, description="Enable automatic mode switching")
    complexity_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Complexity threshold for agent mode")
    confidence_threshold: float = Field(default=0.8, ge=0.0, le=1.0, description="Confidence threshold for mode decisions")
    context_window_size: int = Field(default=10, ge=1, le=100, description="Context window size for memory")
    memory_retention_hours: int = Field(default=24, ge=1, le=168, description="Memory retention in hours")
    reasoning_steps_max: int = Field(default=5, ge=1, le=20, description="Maximum reasoning steps")
    tool_relevance_threshold: float = Field(default=0.6, ge=0.0, le=1.0, description="Tool relevance threshold")

    @field_validator("complexity_threshold", "confidence_threshold", "tool_relevance_threshold")
    @classmethod
    def validate_thresholds(cls, v: float) -> float:
        """Validate threshold values."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Threshold must be between 0.0 and 1.0")
        return v


class HybridModeState(BaseModel):
    """Current state of hybrid mode for a conversation."""

    conversation_id: UUID = Field(..., description="Conversation ID")
    user_id: UUID = Field(..., description="User ID")
    current_mode: ConversationMode = Field(..., description="Current mode")
    last_mode_change: datetime = Field(..., description="Last mode change timestamp")
    mode_history: List[Dict[str, Any]] = Field(default_factory=list, description="Mode change history")
    memory_context: List[AgentMemory] = Field(default_factory=list, description="Current memory context")
    reasoning_context: List[AgentReasoning] = Field(default_factory=list, description="Current reasoning context")
    config: HybridModeConfig = Field(..., description="Mode configuration")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")


class ModeChangeRequest(BaseModel):
    """Request to change conversation mode."""

    conversation_id: UUID = Field(..., description="Conversation ID")
    user_id: UUID = Field(..., description="User ID")
    target_mode: ConversationMode = Field(..., description="Target mode")
    reason: Optional[str] = Field(None, description="User-provided reason")
    force_change: bool = Field(default=False, description="Force mode change ignoring recommendations")


class ModeChangeResponse(BaseModel):
    """Response to mode change request."""

    success: bool = Field(..., description="Whether mode change was successful")
    previous_mode: ConversationMode = Field(..., description="Previous mode")
    new_mode: ConversationMode = Field(..., description="New mode")
    reason: str = Field(..., description="Reason for mode change")
    timestamp: datetime = Field(default_factory=datetime.now, description="Change timestamp")
    warnings: List[str] = Field(default_factory=list, description="Any warnings about the change")


class StructuredResponse(BaseModel):
    """Structured response with mode decision and reasoning."""

    content: str = Field(..., description="Response content")
    mode_decision: ModeDecision = Field(..., description="Mode decision information")
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list, description="Tool calls made")
    memory_updates: List[AgentMemory] = Field(default_factory=list, description="Memory updates")
    reasoning_process: List[AgentReasoning] = Field(default_factory=list, description="Reasoning process")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    model_used: str = Field(..., description="Model used for response")
    tokens_used: int = Field(..., ge=0, description="Tokens used")
    processing_time: float = Field(..., ge=0, description="Processing time in seconds")

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