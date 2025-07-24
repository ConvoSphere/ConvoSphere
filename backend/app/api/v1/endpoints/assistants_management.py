"""
Assistant management API endpoints (CRUD, activate, deactivate, status).
"""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.assistant import AssistantStatus
from app.services.assistant_service import AssistantService
from pydantic import BaseModel, Field

# ... Pydantic models (AssistantCreate, AssistantUpdate, AssistantResponse, AssistantListResponse) ...

router = APIRouter()

# Get all assistants
@router.get("/", response_model=list[AssistantResponse])
async def get_assistants(
    status: str | None = Query(None, description="Filter by status"),
    category: str | None = Query(None, description="Filter by category"),
    include_public: bool = Query(True, description="Include public assistants"),
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    # ... existing code ...

# Get public assistants
@router.get("/public", response_model=list[AssistantResponse])
async def get_public_assistants(
    category: str | None = Query(None, description="Filter by category"),
    tags: str | None = Query(None, description="Filter by tags (comma-separated)"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    db: Session = Depends(get_db),
):
    # ... existing code ...

# Get assistant by ID
@router.get("/{assistant_id}", response_model=AssistantResponse)
async def get_assistant(
    assistant_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    # ... existing code ...

# Create assistant
@router.post("/", response_model=AssistantResponse)
async def create_assistant(
    assistant_data: AssistantCreate,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    # ... existing code ...

# Update assistant
@router.put("/{assistant_id}", response_model=AssistantResponse)
async def update_assistant(
    assistant_id: str,
    assistant_data: AssistantUpdate,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    # ... existing code ...

# Delete assistant
@router.delete("/{assistant_id}")
async def delete_assistant(
    assistant_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    # ... existing code ...

# Activate assistant
@router.post("/{assistant_id}/activate", response_model=AssistantResponse)
async def activate_assistant(
    assistant_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    # ... existing code ...

# Deactivate assistant
@router.post("/{assistant_id}/deactivate", response_model=AssistantResponse)
async def deactivate_assistant(
    assistant_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    # ... existing code ...

# Get assistant statuses
@router.get("/status/list")
async def get_assistant_statuses():
    # ... existing code ...