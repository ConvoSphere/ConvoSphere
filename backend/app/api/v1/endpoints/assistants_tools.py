"""
Assistant tools API endpoints (add/remove tools).
"""

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user_id
from backend.app.services.assistant_service import AssistantService


# Pydantic model
class ToolAssignmentRequest(BaseModel):
    """Model for assigning a tool to an assistant."""

    tool_id: str = Field(..., description="Tool ID to assign")
    config: dict | None = Field(None, description="Tool configuration")


router = APIRouter()


# Add tool to assistant
@router.post("/{assistant_id}/tools", response_model=Any)
async def add_tool_to_assistant(
    assistant_id: str,
    tool_data: ToolAssignmentRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Add a tool to an assistant."""
    service = AssistantService(db)
    return await service.add_tool_to_assistant(
        assistant_id,
        tool_data.tool_id,
        tool_data.config,
        current_user_id,
    )


# Remove tool from assistant
@router.delete("/{assistant_id}/tools/{tool_id}", response_model=Any)
async def remove_tool_from_assistant(
    assistant_id: str,
    tool_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Remove a tool from an assistant."""
    service = AssistantService(db)
    return await service.remove_tool_from_assistant(
        assistant_id,
        tool_id,
        current_user_id,
    )
