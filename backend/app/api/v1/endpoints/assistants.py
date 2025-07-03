"""Assistants endpoints for assistant management."""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from loguru import logger

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.services.assistant_service import AssistantService
from app.models.assistant import AssistantStatus


# Pydantic models for request/response
class AssistantCreate(BaseModel):
    """Create assistant request model."""
    name: str = Field(..., min_length=1, max_length=200, description="Assistant name")
    system_prompt: str = Field(..., description="System prompt for the assistant")
    description: Optional[str] = Field(None, description="Assistant description")
    personality: Optional[str] = Field(None, description="Personality profile")
    instructions: Optional[str] = Field(None, description="Additional instructions")
    model: str = Field("gpt-4", description="AI model to use")
    temperature: str = Field("0.7", description="Model temperature")
    max_tokens: str = Field("4096", description="Maximum tokens")
    category: Optional[str] = Field(None, description="Assistant category")
    tags: List[str] = Field(default_factory=list, description="List of tags")
    is_public: bool = Field(False, description="Whether assistant is public")
    is_template: bool = Field(False, description="Whether assistant is a template")


class AssistantUpdate(BaseModel):
    """Update assistant request model."""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Assistant name")
    system_prompt: Optional[str] = Field(None, description="System prompt for the assistant")
    description: Optional[str] = Field(None, description="Assistant description")
    personality: Optional[str] = Field(None, description="Personality profile")
    instructions: Optional[str] = Field(None, description="Additional instructions")
    model: Optional[str] = Field(None, description="AI model to use")
    temperature: Optional[str] = Field(None, description="Model temperature")
    max_tokens: Optional[str] = Field(None, description="Maximum tokens")
    category: Optional[str] = Field(None, description="Assistant category")
    tags: Optional[List[str]] = Field(None, description="List of tags")
    is_public: Optional[bool] = Field(None, description="Whether assistant is public")
    is_template: Optional[bool] = Field(None, description="Whether assistant is a template")
    status: Optional[str] = Field(None, description="Assistant status")
    tools_enabled: Optional[bool] = Field(None, description="Whether tools are enabled")


class AssistantResponse(BaseModel):
    """Assistant response model."""
    id: str
    name: str
    description: Optional[str]
    version: str
    personality: Optional[str]
    system_prompt: str
    instructions: Optional[str]
    model: str
    temperature: str
    max_tokens: str
    status: str
    is_public: bool
    is_template: bool
    tools_config: List[Dict[str, Any]]
    tools_enabled: bool
    category: Optional[str]
    tags: List[str]
    metadata: Dict[str, Any]
    creator_id: str
    created_at: Optional[str]
    updated_at: Optional[str]
    tool_count: int
    is_active: bool

    class Config:
        from_attributes = True


class AssistantListResponse(BaseModel):
    """Assistant list response model."""
    assistants: List[AssistantResponse]
    total: int
    page: int
    size: int


class ToolAssignmentRequest(BaseModel):
    """Tool assignment request model."""
    tool_id: str = Field(..., description="Tool ID to assign")
    config: Optional[Dict[str, Any]] = Field(None, description="Tool configuration")


router = APIRouter()


@router.get("/", response_model=List[AssistantResponse])
async def get_assistants(
    status: Optional[str] = Query(None, description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    include_public: bool = Query(True, description="Include public assistants"),
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get all assistants for the current user with optional filtering.
    
    Args:
        status: Filter by assistant status
        category: Filter by assistant category
        include_public: Whether to include public assistants
        current_user_id: Current user ID
        db: Database session
        
    Returns:
        List[AssistantResponse]: List of assistants
    """
    try:
        assistant_service = AssistantService(db)
        
        # Parse status filter
        status_filter = None
        if status:
            try:
                status_filter = AssistantStatus(status)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status: {status}. Valid values: {[s.value for s in AssistantStatus]}"
                )
        
        # Get assistants
        assistants = assistant_service.get_user_assistants(
            user_id=current_user_id,
            include_public=include_public,
            status=status_filter
        )
        
        # Filter by category if specified
        if category:
            assistants = [a for a in assistants if a.category == category]
        
        # Convert to response models
        result = []
        for assistant in assistants:
            assistant_dict = assistant.to_dict()
            assistant_dict["tool_count"] = assistant.tool_count
            assistant_dict["is_active"] = assistant.is_active
            result.append(AssistantResponse(**assistant_dict))
        
        logger.info(f"Retrieved {len(result)} assistants for user {current_user_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting assistants: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve assistants"
        )


@router.get("/public", response_model=List[AssistantResponse])
async def get_public_assistants(
    category: Optional[str] = Query(None, description="Filter by category"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """
    Get public assistants.
    
    Args:
        category: Filter by assistant category
        tags: Filter by tags (comma-separated)
        limit: Maximum number of results
        db: Database session
        
    Returns:
        List[AssistantResponse]: List of public assistants
    """
    try:
        assistant_service = AssistantService(db)
        
        # Parse tags
        tag_list = None
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        
        # Get public assistants
        assistants = assistant_service.get_public_assistants(
            category=category,
            tags=tag_list,
            limit=limit
        )
        
        # Convert to response models
        result = []
        for assistant in assistants:
            assistant_dict = assistant.to_dict()
            assistant_dict["tool_count"] = assistant.tool_count
            assistant_dict["is_active"] = assistant.is_active
            result.append(AssistantResponse(**assistant_dict))
        
        logger.info(f"Retrieved {len(result)} public assistants")
        return result
        
    except Exception as e:
        logger.error(f"Error getting public assistants: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve public assistants"
        )


@router.get("/{assistant_id}", response_model=AssistantResponse)
async def get_assistant(
    assistant_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get assistant by ID.
    
    Args:
        assistant_id: Assistant ID
        current_user_id: Current user ID
        db: Database session
        
    Returns:
        AssistantResponse: Assistant information
        
    Raises:
        HTTPException: If assistant not found or access denied
    """
    try:
        assistant_service = AssistantService(db)
        assistant = assistant_service.get_assistant(assistant_id)
        
        if not assistant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assistant not found"
            )
        
        # Check if user has access to this assistant
        if assistant.creator_id != current_user_id and not assistant.is_public:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this assistant"
            )
        
        # Convert to response model
        assistant_dict = assistant.to_dict()
        assistant_dict["tool_count"] = assistant.tool_count
        assistant_dict["is_active"] = assistant.is_active
        
        logger.info(f"Retrieved assistant {assistant_id} for user {current_user_id}")
        return AssistantResponse(**assistant_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting assistant {assistant_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve assistant"
        )


@router.post("/", response_model=AssistantResponse)
async def create_assistant(
    assistant_data: AssistantCreate,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Create a new assistant.
    
    Args:
        assistant_data: Assistant creation data
        current_user_id: Current user ID
        db: Database session
        
    Returns:
        AssistantResponse: Created assistant information
        
    Raises:
        HTTPException: If validation fails or assistant creation fails
    """
    try:
        assistant_service = AssistantService(db)
        
        # Create assistant
        assistant = assistant_service.create_assistant(
            user_id=current_user_id,
            name=assistant_data.name,
            system_prompt=assistant_data.system_prompt,
            description=assistant_data.description,
            personality=assistant_data.personality,
            instructions=assistant_data.instructions,
            model=assistant_data.model,
            temperature=assistant_data.temperature,
            max_tokens=assistant_data.max_tokens,
            category=assistant_data.category,
            tags=assistant_data.tags,
            is_public=assistant_data.is_public,
            is_template=assistant_data.is_template
        )
        
        # Convert to response model
        assistant_dict = assistant.to_dict()
        assistant_dict["tool_count"] = assistant.tool_count
        assistant_dict["is_active"] = assistant.is_active
        
        logger.info(f"Created assistant by user {current_user_id}: {assistant.name}")
        return AssistantResponse(**assistant_dict)
        
    except ValueError as e:
        logger.warning(f"Validation error creating assistant: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating assistant: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create assistant"
        )


@router.put("/{assistant_id}", response_model=AssistantResponse)
async def update_assistant(
    assistant_id: str,
    assistant_data: AssistantUpdate,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Update an existing assistant.
    
    Args:
        assistant_id: Assistant ID
        assistant_data: Assistant update data
        current_user_id: Current user ID
        db: Database session
        
    Returns:
        AssistantResponse: Updated assistant information
        
    Raises:
        HTTPException: If assistant not found or update fails
    """
    try:
        assistant_service = AssistantService(db)
        
        # Convert Pydantic model to dict, excluding None values
        update_data = {k: v for k, v in assistant_data.dict().items() if v is not None}
        
        # Parse status if provided
        if "status" in update_data:
            try:
                update_data["status"] = AssistantStatus(update_data["status"])
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status: {update_data['status']}. Valid values: {[s.value for s in AssistantStatus]}"
                )
        
        # Update assistant
        assistant = assistant_service.update_assistant(assistant_id, current_user_id, **update_data)
        
        if not assistant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assistant not found or insufficient permissions"
            )
        
        # Convert to response model
        assistant_dict = assistant.to_dict()
        assistant_dict["tool_count"] = assistant.tool_count
        assistant_dict["is_active"] = assistant.is_active
        
        logger.info(f"Updated assistant {assistant_id} by user {current_user_id}")
        return AssistantResponse(**assistant_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating assistant {assistant_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update assistant"
        )


@router.delete("/{assistant_id}")
async def delete_assistant(
    assistant_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Delete an assistant.
    
    Args:
        assistant_id: Assistant ID
        current_user_id: Current user ID
        db: Database session
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: If assistant not found or deletion fails
    """
    try:
        assistant_service = AssistantService(db)
        success = assistant_service.delete_assistant(assistant_id, current_user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assistant not found or insufficient permissions"
            )
        
        logger.info(f"Deleted assistant {assistant_id} by user {current_user_id}")
        return {"message": "Assistant deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting assistant {assistant_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete assistant"
        )


@router.post("/{assistant_id}/activate", response_model=AssistantResponse)
async def activate_assistant(
    assistant_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Activate an assistant.
    
    Args:
        assistant_id: Assistant ID
        current_user_id: Current user ID
        db: Database session
        
    Returns:
        AssistantResponse: Activated assistant information
    """
    try:
        assistant_service = AssistantService(db)
        assistant = assistant_service.activate_assistant(assistant_id, current_user_id)
        
        if not assistant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assistant not found or insufficient permissions"
            )
        
        # Convert to response model
        assistant_dict = assistant.to_dict()
        assistant_dict["tool_count"] = assistant.tool_count
        assistant_dict["is_active"] = assistant.is_active
        
        logger.info(f"Activated assistant {assistant_id} by user {current_user_id}")
        return AssistantResponse(**assistant_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating assistant {assistant_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to activate assistant"
        )


@router.post("/{assistant_id}/deactivate", response_model=AssistantResponse)
async def deactivate_assistant(
    assistant_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Deactivate an assistant.
    
    Args:
        assistant_id: Assistant ID
        current_user_id: Current user ID
        db: Database session
        
    Returns:
        AssistantResponse: Deactivated assistant information
    """
    try:
        assistant_service = AssistantService(db)
        assistant = assistant_service.deactivate_assistant(assistant_id, current_user_id)
        
        if not assistant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assistant not found or insufficient permissions"
            )
        
        # Convert to response model
        assistant_dict = assistant.to_dict()
        assistant_dict["tool_count"] = assistant.tool_count
        assistant_dict["is_active"] = assistant.is_active
        
        logger.info(f"Deactivated assistant {assistant_id} by user {current_user_id}")
        return AssistantResponse(**assistant_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating assistant {assistant_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate assistant"
        )


@router.post("/{assistant_id}/tools", response_model=AssistantResponse)
async def add_tool_to_assistant(
    assistant_id: str,
    tool_data: ToolAssignmentRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Add a tool to an assistant.
    
    Args:
        assistant_id: Assistant ID
        tool_data: Tool assignment data
        current_user_id: Current user ID
        db: Database session
        
    Returns:
        AssistantResponse: Updated assistant information
    """
    try:
        assistant_service = AssistantService(db)
        assistant = assistant_service.add_tool_to_assistant(
            assistant_id=assistant_id,
            user_id=current_user_id,
            tool_id=tool_data.tool_id,
            config=tool_data.config
        )
        
        if not assistant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assistant not found or insufficient permissions"
            )
        
        # Convert to response model
        assistant_dict = assistant.to_dict()
        assistant_dict["tool_count"] = assistant.tool_count
        assistant_dict["is_active"] = assistant.is_active
        
        logger.info(f"Added tool {tool_data.tool_id} to assistant {assistant_id} by user {current_user_id}")
        return AssistantResponse(**assistant_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding tool to assistant {assistant_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add tool to assistant"
        )


@router.delete("/{assistant_id}/tools/{tool_id}", response_model=AssistantResponse)
async def remove_tool_from_assistant(
    assistant_id: str,
    tool_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Remove a tool from an assistant.
    
    Args:
        assistant_id: Assistant ID
        tool_id: Tool ID
        current_user_id: Current user ID
        db: Database session
        
    Returns:
        AssistantResponse: Updated assistant information
    """
    try:
        assistant_service = AssistantService(db)
        assistant = assistant_service.remove_tool_from_assistant(
            assistant_id=assistant_id,
            user_id=current_user_id,
            tool_id=tool_id
        )
        
        if not assistant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assistant or tool not found or insufficient permissions"
            )
        
        # Convert to response model
        assistant_dict = assistant.to_dict()
        assistant_dict["tool_count"] = assistant.tool_count
        assistant_dict["is_active"] = assistant.is_active
        
        logger.info(f"Removed tool {tool_id} from assistant {assistant_id} by user {current_user_id}")
        return AssistantResponse(**assistant_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing tool from assistant {assistant_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove tool from assistant"
        )


@router.get("/status/list")
async def get_assistant_statuses():
    """
    Get list of available assistant statuses.
    
    Returns:
        List[str]: List of assistant statuses
    """
    try:
        statuses = [status.value for status in AssistantStatus]
        return {"statuses": statuses}
        
    except Exception as e:
        logger.error(f"Error getting assistant statuses: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve assistant statuses"
        ) 