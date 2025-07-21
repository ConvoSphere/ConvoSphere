"""
MCP (Model Context Protocol) API endpoints.

This module provides API endpoints for managing MCP servers and tools
through the web interface.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from loguru import logger

from app.core.database import get_db
from app.core.security import get_current_user_id, require_permission
from app.tools.mcp_tool import mcp_manager

router = APIRouter()


# Pydantic models
class MCPServerCreate(BaseModel):
    """Create MCP server request model."""
    server_id: str
    server_url: str
    server_name: Optional[str] = None


class MCPServerResponse(BaseModel):
    """MCP server response model."""
    server_id: str
    server_name: str
    server_url: str
    is_connected: bool
    tool_count: int
    resource_count: int


class MCPToolResponse(BaseModel):
    """MCP tool response model."""
    id: str
    name: str
    description: str
    category: str
    server_name: str
    parameters: List[Dict[str, Any]]


class MCPToolExecute(BaseModel):
    """Execute MCP tool request model."""
    arguments: Dict[str, Any]


@router.post("/servers", response_model=MCPServerResponse)
@require_permission("mcp:write")
async def add_mcp_server(
    server_data: MCPServerCreate,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Add and connect to an MCP server.
    
    Args:
        server_data: MCP server configuration
        current_user_id: Current user ID
        db: Database session
        
    Returns:
        MCPServerResponse: Server information
    """
    try:
        success = await mcp_manager.add_server(
            server_id=server_data.server_id,
            server_url=server_data.server_url,
            server_name=server_data.server_name
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to connect to MCP server"
            )
        
        # Get server information
        server = mcp_manager.servers.get(server_data.server_id)
        if not server:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Server not found after connection"
            )
        
        logger.info(f"MCP server added by user {current_user_id}: {server_data.server_id}")
        
        return MCPServerResponse(
            server_id=server_data.server_id,
            server_name=server.server_name,
            server_url=server.server_url,
            is_connected=server.is_connected,
            tool_count=len(server.tools),
            resource_count=len(server.resources)
        )
        
    except Exception as e:
        logger.error(f"Error adding MCP server: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add MCP server"
        )


@router.get("/servers", response_model=List[MCPServerResponse])
async def list_mcp_servers(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    List all connected MCP servers.
    
    Args:
        current_user_id: Current user ID
        db: Database session
        
    Returns:
        List[MCPServerResponse]: List of servers
    """
    try:
        servers = []
        
        for server_id, server in mcp_manager.servers.items():
            servers.append(MCPServerResponse(
                server_id=server_id,
                server_name=server.server_name,
                server_url=server.server_url,
                is_connected=server.is_connected,
                tool_count=len(server.tools),
                resource_count=len(server.resources)
            ))
        
        return servers
        
    except Exception as e:
        logger.error(f"Error listing MCP servers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list MCP servers"
        )


@router.delete("/servers/{server_id}")
@require_permission("mcp:write")
async def remove_mcp_server(
    server_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Remove MCP server connection.
    
    Args:
        server_id: Server identifier
        current_user_id: Current user ID
        db: Database session
        
    Returns:
        dict: Success message
    """
    try:
        success = await mcp_manager.remove_server(server_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="MCP server not found"
            )
        
        logger.info(f"MCP server removed by user {current_user_id}: {server_id}")
        
        return {"message": f"MCP server {server_id} removed successfully"}
        
    except Exception as e:
        logger.error(f"Error removing MCP server: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove MCP server"
        )


@router.get("/tools", response_model=List[MCPToolResponse])
async def list_mcp_tools(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    List all available MCP tools.
    
    Args:
        current_user_id: Current user ID
        db: Database session
        
    Returns:
        List[MCPToolResponse]: List of tools
    """
    try:
        tools_data = mcp_manager.get_all_tools()
        
        return [
            MCPToolResponse(
                id=tool["id"],
                name=tool["name"],
                description=tool["description"],
                category=tool["category"],
                server_name=tool["server_name"],
                parameters=tool["parameters"]
            )
            for tool in tools_data
        ]
        
    except Exception as e:
        logger.error(f"Error listing MCP tools: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list MCP tools"
        )


@router.get("/tools/{tool_id}", response_model=MCPToolResponse)
async def get_mcp_tool(
    tool_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get MCP tool information.
    
    Args:
        tool_id: Tool identifier
        current_user_id: Current user ID
        db: Database session
        
    Returns:
        MCPToolResponse: Tool information
    """
    try:
        tool = mcp_manager.get_tool(tool_id)
        
        if not tool:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="MCP tool not found"
            )
        
        return MCPToolResponse(
            id=tool_id,
            name=tool.name,
            description=tool.description,
            category=tool.category,
            server_name=tool.mcp_client.server_name,
            parameters=[param.dict() for param in tool.parameters]
        )
        
    except Exception as e:
        logger.error(f"Error getting MCP tool: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get MCP tool"
        )


@router.post("/tools/{tool_id}/execute")
@require_permission("mcp:write")
async def execute_mcp_tool(
    tool_id: str,
    execute_data: MCPToolExecute,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Execute an MCP tool.
    
    Args:
        tool_id: Tool identifier
        execute_data: Tool execution data
        current_user_id: Current user ID
        db: Database session
        
    Returns:
        dict: Tool execution result
    """
    try:
        result = await mcp_manager.execute_tool(tool_id, **execute_data.arguments)
        
        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.error
            )
        
        logger.info(f"MCP tool executed by user {current_user_id}: {tool_id}")
        
        return {
            "success": True,
            "data": result.data,
            "metadata": result.metadata
        }
        
    except Exception as e:
        logger.error(f"Error executing MCP tool: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute MCP tool"
        )


@router.get("/servers/{server_id}/resources")
async def list_server_resources(
    server_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    List resources from an MCP server.
    
    Args:
        server_id: Server identifier
        current_user_id: Current user ID
        db: Database session
        
    Returns:
        List[dict]: List of resources
    """
    try:
        server = mcp_manager.servers.get(server_id)
        
        if not server:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="MCP server not found"
            )
        
        return server.list_resources()
        
    except Exception as e:
        logger.error(f"Error listing server resources: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list server resources"
        )


@router.post("/servers/{server_id}/resources/{resource_uri}/read")
@require_permission("mcp:write")
async def read_server_resource(
    server_id: str,
    resource_uri: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Read a resource from an MCP server.
    
    Args:
        server_id: Server identifier
        resource_uri: Resource URI
        current_user_id: Current user ID
        db: Database session
        
    Returns:
        dict: Resource content
    """
    try:
        server = mcp_manager.servers.get(server_id)
        
        if not server:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="MCP server not found"
            )
        
        result = await server.read_resource(resource_uri)
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return result
        
    except Exception as e:
        logger.error(f"Error reading server resource: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to read server resource"
        ) 