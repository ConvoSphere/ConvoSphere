"""
Agent model for persisting AI agent configurations, including planning fields.
"""

import uuid
from typing import Any

from sqlalchemy import JSON, Boolean, Column, Float, String, Text
from sqlalchemy.dialects.postgresql import UUID

from .base import Base, TimestampMixin


class Agent(Base, TimestampMixin):
    """Persistent Agent configuration."""

    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Ownership/visibility
    user_id = Column(UUID(as_uuid=True), nullable=True)
    is_public = Column(Boolean, default=False, nullable=False)
    is_template = Column(Boolean, default=False, nullable=False)

    # Core config
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    system_prompt = Column(Text, nullable=False)
    tools = Column(JSON, default=list)
    model = Column(String(100), nullable=False, default="gpt-4")
    temperature = Column(Float, nullable=False, default=0.7)
    max_tokens = Column(String(50), nullable=True)
    max_context_length = Column(String(50), nullable=True)
    personality = Column(Text, nullable=True)
    instructions = Column(Text, nullable=True)
    metadata = Column(JSON, default=dict)

    # Planning
    planning_strategy = Column(
        String(50), nullable=False, default="none"
    )  # none|react|plan_execute|tree_of_thought
    max_planning_steps = Column(String(10), nullable=True)
    abort_criteria = Column(JSON, default=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "user_id": str(self.user_id) if self.user_id else None,
            "is_public": self.is_public,
            "is_template": self.is_template,
            "name": self.name,
            "description": self.description,
            "system_prompt": self.system_prompt,
            "tools": self.tools or [],
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "max_context_length": self.max_context_length,
            "personality": self.personality,
            "instructions": self.instructions,
            "metadata": self.metadata or {},
            "planning_strategy": self.planning_strategy,
            "max_planning_steps": self.max_planning_steps,
            "abort_criteria": self.abort_criteria or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }