"""
Assistant management API endpoints (CRUD, activate, deactivate, status).
"""

from uuid import UUID

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user_id
from backend.app.models.assistant import AssistantStatus
from backend.app.services.assistant_service import AssistantService
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy.orm import Session


# Pydantic models
class AssistantCreate(BaseModel):
    """Model for creating a new assistant."""

    name: str = Field(..., min_length=1, max_length=200, description="Assistant name")
    description: str | None = Field(None, description="Assistant description")
    personality: str | None = Field(None, description="Assistant personality")
    system_prompt: str = Field(..., min_length=1, description="System prompt")
    instructions: str | None = Field(None, description="Additional instructions")
    model: str = Field(default="gpt-4", description="AI model to use")
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Temperature setting",
    )
    max_tokens: int = Field(default=4096, ge=1, description="Maximum tokens")
    is_public: bool = Field(default=False, description="Whether assistant is public")
    category: str | None = Field(None, description="Assistant category")
    tags: list[str] = Field(default_factory=list, description="Assistant tags")
    tools_config: list[dict] = Field(
        default_factory=list,
        description="Tool configurations",
    )


class AssistantUpdate(BaseModel):
    """Model for updating an assistant."""

    name: str | None = Field(
        None,
        min_length=1,
        max_length=200,
        description="Assistant name",
    )
    description: str | None = Field(None, description="Assistant description")
    personality: str | None = Field(None, description="Assistant personality")
    system_prompt: str | None = Field(None, min_length=1, description="System prompt")
    instructions: str | None = Field(None, description="Additional instructions")
    model: str | None = Field(None, description="AI model to use")
    temperature: float | None = Field(
        None,
        ge=0.0,
        le=2.0,
        description="Temperature setting",
    )
    max_tokens: int | None = Field(None, ge=1, description="Maximum tokens")
    is_public: bool | None = Field(None, description="Whether assistant is public")
    category: str | None = Field(None, description="Assistant category")
    tags: list[str] | None = Field(None, description="Assistant tags")
    tools_config: list[dict] | None = Field(None, description="Tool configurations")


class AssistantResponse(BaseModel):
    """Model for assistant response."""

    id: UUID
    name: str
    description: str | None
    personality: str | None
    system_prompt: str
    instructions: str | None
    model: str
    temperature: float
    max_tokens: int
    status: str
    is_public: bool
    is_template: bool
    category: str | None
    tags: list[str]
    tools_config: list[dict]
    tools_enabled: bool
    creator_id: UUID
    version: str

    model_config = ConfigDict(from_attributes=True)


router = APIRouter()


# Get all assistants
@router.get("/", response_model=list[AssistantResponse])
def get_assistants(
    status: str | None = Query(None, description="Filter by status"),
    category: str | None = Query(None, description="Filter by category"),
    include_public: bool = Query(True, description="Include public assistants"),
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Get all assistants for the current user (optionally including public)."""
    service = AssistantService(db)
    return service.get_user_assistants(current_user_id, include_public=include_public)


# Get public assistants
@router.get("/public", response_model=list[AssistantResponse])
async def get_public_assistants(
    category: str | None = Query(None, description="Filter by category"),
    tags: str | None = Query(None, description="Filter by tags (comma-separated)"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    db: Session = Depends(get_db),
):
    """Get public assistants."""
    service = AssistantService(db)
    return await service.get_public_assistants(
        category=category,
        tags=tags,
        limit=limit,
    )


# Get assistant statuses
@router.get("/status/list")
async def get_assistant_statuses():
    """Get all available assistant statuses."""
    return [status.value for status in AssistantStatus]


@router.get("/default", response_model=AssistantResponse)
async def get_default_assistant(
    db: Session = Depends(get_db),
):
    """Get the default assistant."""
    service = AssistantService(db)
    assistant = service.get_default_assistant()
    if not assistant:
        raise HTTPException(status_code=404, detail="No default assistant found")
    return assistant


@router.get("/default/id")
async def get_default_assistant_id(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Get the default assistant ID for the current user."""
    service = AssistantService(db)
    default_assistant_id = service.get_user_default_assistant_id(current_user_id)
    if not default_assistant_id:
        raise HTTPException(
            status_code=404, detail="No default assistant configured for user"
        )
    return {"assistant_id": default_assistant_id}


class DefaultAssistantRequest(BaseModel):
    """Request model for setting default assistant."""

    assistant_id: str = Field(..., description="Assistant ID to set as default")

    @field_validator("assistant_id")
    @classmethod
    def validate_assistant_id(cls, v: str) -> str:
        """Validate that assistant_id is a valid UUID."""
        try:
            UUID(v)
            return v
        except ValueError:
            raise ValueError("assistant_id must be a valid UUID")


@router.post("/default/set")
async def set_default_assistant(
    request: DefaultAssistantRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Set the default assistant for the current user."""
    service = AssistantService(db)
    success = service.set_user_default_assistant(current_user_id, request.assistant_id)
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Failed to set default assistant. Assistant may not exist or you may not have access.",
        )
    return {"message": "Default assistant set successfully"}


# Get assistant by ID
@router.get("/{assistant_id}", response_model=AssistantResponse)
def get_assistant(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    assistant_id: str = Path(
        ...,
        description="Assistant ID",
        pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    ),
):
    """Get assistant by ID."""
    service = AssistantService(db)
    return service.get_assistant(assistant_id, current_user_id)


# Create assistant
@router.post("/", response_model=AssistantResponse)
def create_assistant(
    assistant_data: AssistantCreate,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Create a new assistant."""
    service = AssistantService(db)
    return service.create_assistant(assistant_data, current_user_id)


# Update assistant
@router.put("/{assistant_id}", response_model=AssistantResponse)
def update_assistant(
    assistant_data: AssistantUpdate,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    assistant_id: str = Path(
        ...,
        description="Assistant ID",
        pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    ),
):
    """Update an assistant."""
    service = AssistantService(db)
    return service.update_assistant(assistant_id, assistant_data, current_user_id)


# Delete assistant
@router.delete("/{assistant_id}")
def delete_assistant(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    assistant_id: str = Path(
        ...,
        description="Assistant ID",
        pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    ),
):
    """Delete an assistant."""
    service = AssistantService(db)
    service.delete_assistant(assistant_id, current_user_id)
    return {"message": "Assistant deleted successfully"}


# Activate assistant
@router.post("/{assistant_id}/activate", response_model=AssistantResponse)
def activate_assistant(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    assistant_id: str = Path(
        ...,
        description="Assistant ID",
        pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    ),
):
    """Activate an assistant."""
    service = AssistantService(db)
    return service.activate_assistant(assistant_id, current_user_id)


# Deactivate assistant
@router.post("/{assistant_id}/deactivate", response_model=AssistantResponse)
def deactivate_assistant(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    assistant_id: str = Path(
        ...,
        description="Assistant ID",
        pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    ),
):
    """Deactivate an assistant."""
    service = AssistantService(db)
    return service.deactivate_assistant(assistant_id, current_user_id)
