"""
Assistant tools API endpoints (add/remove tools).
"""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.services.assistant_service import AssistantService
from pydantic import BaseModel, Field

# ... Pydantic model ToolAssignmentRequest ...

router = APIRouter()

# Add tool to assistant
@router.post("/{assistant_id}/tools", response_model=Any)
async def add_tool_to_assistant(
    assistant_id: str,
    tool_data: ToolAssignmentRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    # ... existing code ...

# Remove tool from assistant
@router.delete("/{assistant_id}/tools/{tool_id}", response_model=Any)
async def remove_tool_from_assistant(
    assistant_id: str,
    tool_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    # ... existing code ...