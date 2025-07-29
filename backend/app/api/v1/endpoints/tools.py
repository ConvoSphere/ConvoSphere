"""Tools endpoints for tool management."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from loguru import logger
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user_id
from backend.app.models.tool import ToolCategory
from backend.app.services.tool_service import ToolService


# Pydantic models for request/response
class ToolCreate(BaseModel):
    """Create tool request model."""

    name: str = Field(..., min_length=1, max_length=200, description="Tool name")
    description: str | None = Field(None, description="Tool description")
    version: str = Field("0.1.0-beta", description="Tool version")
    category: str = Field(..., description="Tool category")
    function_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Unique function name",
    )
    parameters_schema: dict[str, Any] | None = Field(
        None,
        description="JSON Schema for parameters",
    )
    implementation_path: str | None = Field(None, description="Path to implementation")
    is_builtin: bool = Field(False, description="Whether tool is builtin")
    is_enabled: bool = Field(True, description="Whether tool is enabled")
    requires_auth: bool = Field(
        False,
        description="Whether tool requires authentication",
    )
    required_permissions: list[str] = Field(
        default_factory=list,
        description="Required permissions",
    )
    rate_limit: str | None = Field(None, description="Rate limiting configuration")
    tags: list[str] = Field(default_factory=list, description="Tool tags")
    tool_metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata",
    )


class ToolUpdate(BaseModel):
    """Update tool request model."""

    name: str | None = Field(
        None,
        min_length=1,
        max_length=200,
        description="Tool name",
    )
    description: str | None = Field(None, description="Tool description")
    version: str | None = Field(None, description="Tool version")
    category: str | None = Field(None, description="Tool category")
    parameters_schema: dict[str, Any] | None = Field(
        None,
        description="JSON Schema for parameters",
    )
    implementation_path: str | None = Field(None, description="Path to implementation")
    is_enabled: bool | None = Field(None, description="Whether tool is enabled")
    requires_auth: bool | None = Field(
        None,
        description="Whether tool requires authentication",
    )
    required_permissions: list[str] | None = Field(
        None,
        description="Required permissions",
    )
    rate_limit: str | None = Field(None, description="Rate limiting configuration")
    tags: list[str] | None = Field(None, description="Tool tags")
    tool_metadata: dict[str, Any] | None = Field(
        None,
        description="Additional metadata",
    )


class ToolResponse(BaseModel):
    """Tool response model."""

    id: str
    name: str
    description: str | None
    version: str
    category: str
    function_name: str
    parameters_schema: dict[str, Any] | None
    implementation_path: str | None
    is_builtin: bool
    is_enabled: bool
    requires_auth: bool
    required_permissions: list[str]
    rate_limit: str | None
    tags: list[str]
    metadata: dict[str, Any]
    creator_id: str | None
    created_at: str | None
    updated_at: str | None
    can_use: bool

    model_config = ConfigDict(from_attributes=True)


class ToolListResponse(BaseModel):
    """Tool list response model."""

    tools: list[ToolResponse]
    total: int
    page: int
    size: int


router = APIRouter()


@router.get("/", response_model=list[ToolResponse])
async def get_tools(
    category: str | None = Query(None, description="Filter by tool category"),
    search: str | None = Query(None, description="Search in tool name and description"),
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Get all available tools with optional filtering.

    Args:
        category: Filter by tool category
        search: Search query for tool name and description
        current_user_id: Current user ID
        db: Database session

    Returns:
        List[ToolResponse]: List of available tools
    """
    try:
        tool_service = ToolService(db)

        if search:
            tools = tool_service.search_tools(search, current_user_id)
        elif category:
            tools = tool_service.get_tools_by_category(category, current_user_id)
        else:
            tools = tool_service.get_available_tools(current_user_id)

        # Convert to response models
        result = []
        for tool_data in tools:
            result.append(ToolResponse(**tool_data))

        logger.info(f"Retrieved {len(result)} tools for user {current_user_id}")
        return result

    except Exception as e:
        logger.error(f"Error getting tools: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve tools",
        )


@router.get("/{tool_id}", response_model=ToolResponse)
async def get_tool(
    tool_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Get tool by ID.

    Args:
        tool_id: Tool ID
        current_user_id: Current user ID
        db: Database session

    Returns:
        ToolResponse: Tool information

    Raises:
        HTTPException: If tool not found
    """
    try:
        tool_service = ToolService(db)
        tool_data = tool_service.get_tool_by_id(tool_id, current_user_id)

        if not tool_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tool not found",
            )

        logger.info(f"Retrieved tool {tool_id} for user {current_user_id}")
        return ToolResponse(**tool_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tool {tool_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve tool",
        )


@router.post("/", response_model=ToolResponse)
async def create_tool(
    tool_data: ToolCreate,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Create a new tool.

    Args:
        tool_data: Tool creation data
        current_user_id: Current user ID
        db: Database session

    Returns:
        ToolResponse: Created tool information

    Raises:
        HTTPException: If validation fails or tool creation fails
    """
    try:
        tool_service = ToolService(db)

        # Convert Pydantic model to dict
        tool_dict = tool_data.dict()

        # Create tool
        created_tool = tool_service.create_tool(tool_dict, current_user_id)

        if not created_tool:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create tool",
            )

        logger.info(f"Created tool by user {current_user_id}: {created_tool['name']}")
        return ToolResponse(**created_tool)

    except ValueError as e:
        logger.warning(f"Validation error creating tool: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error creating tool: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create tool",
        )


@router.put("/{tool_id}", response_model=ToolResponse)
async def update_tool(
    tool_id: str,
    tool_data: ToolUpdate,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Update an existing tool.

    Args:
        tool_id: Tool ID
        tool_data: Tool update data
        current_user_id: Current user ID
        db: Database session

    Returns:
        ToolResponse: Updated tool information

    Raises:
        HTTPException: If tool not found or update fails
    """
    try:
        tool_service = ToolService(db)

        # Convert Pydantic model to dict, excluding None values
        tool_dict = {k: v for k, v in tool_data.dict().items() if v is not None}

        # Update tool
        updated_tool = tool_service.update_tool(tool_id, tool_dict, current_user_id)

        if not updated_tool:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tool not found or insufficient permissions",
            )

        logger.info(f"Updated tool {tool_id} by user {current_user_id}")
        return ToolResponse(**updated_tool)

    except ValueError as e:
        logger.warning(f"Validation error updating tool: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating tool {tool_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update tool",
        )


@router.delete("/{tool_id}")
async def delete_tool(
    tool_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Delete a tool.

    Args:
        tool_id: Tool ID
        current_user_id: Current user ID
        db: Database session

    Returns:
        dict: Success message

    Raises:
        HTTPException: If tool not found or deletion fails
    """
    try:
        tool_service = ToolService(db)
        success = tool_service.delete_tool(tool_id, current_user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tool not found or insufficient permissions",
            )

        logger.info(f"Deleted tool {tool_id} by user {current_user_id}")
        return {"message": "Tool deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting tool {tool_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete tool",
        )


@router.get("/categories/list")
async def get_tool_categories():
    """
    Get list of available tool categories.

    Returns:
        List[str]: List of tool categories
    """
    try:
        categories = [category.value for category in ToolCategory]
        return {"categories": categories}

    except Exception as e:
        logger.error(f"Error getting tool categories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve tool categories",
        )
