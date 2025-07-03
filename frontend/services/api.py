"""
API service for frontend-backend communication.

This module provides a centralized API client for communicating with
the backend FastAPI server using real HTTP requests.
"""

import json
import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from .http_client import http_client


@dataclass
class APIResponse:
    """API response wrapper."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    status_code: int = 200


class APIClient:
    """API client for backend communication."""
    
    def __init__(self):
        """Initialize the API client."""
        self.client = http_client
    
    def set_token(self, token: str):
        """Set authentication token."""
        self.client.set_auth_token(token)
    
    def clear_token(self):
        """Clear authentication token."""
        self.client.clear_auth_token()
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> APIResponse:
        """
        Make HTTP request to backend.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request data
            params: Query parameters
            
        Returns:
            APIResponse: Response wrapper
        """
        try:
            if method == "GET":
                response_data = await self.client.get(endpoint, params=params)
            elif method == "POST":
                response_data = await self.client.post(endpoint, data=data)
            elif method == "PUT":
                response_data = await self.client.put(endpoint, data=data)
            elif method == "DELETE":
                response_data = await self.client.delete(endpoint)
            elif method == "PATCH":
                response_data = await self.client.patch(endpoint, data=data)
            else:
                return APIResponse(
                    success=False,
                    error=f"Unsupported HTTP method: {method}",
                    status_code=0
                )
            
            return APIResponse(
                success=True,
                data=response_data,
                status_code=200
            )
                
        except Exception as e:
            return APIResponse(
                success=False,
                error=f"Request failed: {str(e)}",
                status_code=0
            )
    
    # Authentication endpoints
    async def login(self, email: str, password: str) -> APIResponse:
        """Login user."""
        return await self._make_request("POST", "/api/v1/auth/login", {
            "email": email,
            "password": password
        })
    
    async def register(self, user_data: Dict[str, Any]) -> APIResponse:
        """Register new user."""
        return await self._make_request("POST", "/api/v1/auth/register", user_data)
    
    async def get_current_user(self) -> APIResponse:
        """Get current user profile."""
        return await self._make_request("GET", "/api/v1/auth/me")
    
    async def update_user_profile(self, user_data: Dict[str, Any]) -> APIResponse:
        """Update user profile."""
        return await self._make_request("PUT", "/api/v1/users/me/profile", user_data)
    
    async def logout(self) -> APIResponse:
        """Logout user."""
        return await self._make_request("POST", "/api/v1/auth/logout")
    
    # Assistant endpoints
    async def get_assistants(self) -> APIResponse:
        """Get all assistants."""
        return await self._make_request("GET", "/api/v1/assistants/")
    
    async def get_assistant(self, assistant_id: str) -> APIResponse:
        """Get specific assistant."""
        return await self._make_request("GET", f"/api/v1/assistants/{assistant_id}")
    
    async def create_assistant(self, assistant_data: Dict[str, Any]) -> APIResponse:
        """Create new assistant."""
        return await self._make_request("POST", "/api/v1/assistants/", assistant_data)
    
    async def update_assistant(self, assistant_id: str, assistant_data: Dict[str, Any]) -> APIResponse:
        """Update assistant."""
        return await self._make_request("PUT", f"/api/v1/assistants/{assistant_id}", assistant_data)
    
    async def delete_assistant(self, assistant_id: str) -> APIResponse:
        """Delete assistant."""
        return await self._make_request("DELETE", f"/api/v1/assistants/{assistant_id}")
    
    # Conversation endpoints
    async def get_conversations(self) -> APIResponse:
        """Get all conversations."""
        return await self._make_request("GET", "/api/v1/conversations/")
    
    async def create_conversation(self, assistant_id: str, title: Optional[str] = None) -> APIResponse:
        """Create new conversation."""
        data = {"assistant_id": assistant_id}
        if title:
            data["title"] = title
        return await self._make_request("POST", "/api/v1/conversations/", data)
    
    async def get_conversation_messages(self, conversation_id: str) -> APIResponse:
        """Get conversation messages."""
        return await self._make_request("GET", f"/api/v1/conversations/{conversation_id}/messages")
    
    async def send_message(self, conversation_id: str, content: str) -> APIResponse:
        """Send message to conversation."""
        return await self._make_request("POST", f"/api/v1/conversations/{conversation_id}/messages", {
            "content": content
        })
    
    # Tool endpoints
    async def get_tools(self) -> APIResponse:
        """Get all tools."""
        return await self._make_request("GET", "/api/v1/tools/")
    
    # Health check
    async def health_check(self) -> APIResponse:
        """Check API health."""
        return await self._make_request("GET", "/health")
    
    # MCP endpoints
    async def get_mcp_servers(self) -> APIResponse:
        """Get MCP servers."""
        return await self._make_request("GET", "/api/v1/mcp/servers")
    
    async def add_mcp_server(self, server_data: Dict[str, Any]) -> APIResponse:
        """Add MCP server."""
        return await self._make_request("POST", "/api/v1/mcp/servers", server_data)
    
    async def remove_mcp_server(self, server_id: str) -> APIResponse:
        """Remove MCP server."""
        return await self._make_request("DELETE", f"/api/v1/mcp/servers/{server_id}")
    
    async def get_mcp_tools(self) -> APIResponse:
        """Get MCP tools."""
        return await self._make_request("GET", "/api/v1/mcp/tools")
    
    async def get_mcp_tool(self, tool_id: str) -> APIResponse:
        """Get specific MCP tool."""
        return await self._make_request("GET", f"/api/v1/mcp/tools/{tool_id}")
    
    async def execute_mcp_tool(self, tool_id: str, arguments: Dict[str, Any]) -> APIResponse:
        """Execute MCP tool."""
        return await self._make_request("POST", f"/api/v1/mcp/tools/{tool_id}/execute", {
            "arguments": arguments
        })
    
    # Knowledge base endpoints
    async def get_documents(self, skip: int = 0, limit: int = 100) -> APIResponse:
        """Get documents."""
        return await self._make_request("GET", "/api/v1/knowledge/documents", params={
            "skip": skip,
            "limit": limit
        })
    
    async def get_document(self, document_id: str) -> APIResponse:
        """Get specific document."""
        return await self._make_request("GET", f"/api/v1/knowledge/documents/{document_id}")
    
    async def upload_document(self, file_data: Dict[str, Any], metadata: Dict[str, Any]) -> APIResponse:
        """Upload document."""
        return await self._make_request("POST", "/api/v1/knowledge/documents", {
            "file": file_data,
            "metadata": metadata
        })
    
    async def delete_document(self, document_id: str) -> APIResponse:
        """Delete document."""
        return await self._make_request("DELETE", f"/api/v1/knowledge/documents/{document_id}")
    
    async def download_document(self, document_id: str) -> APIResponse:
        """Download document."""
        return await self._make_request("GET", f"/api/v1/knowledge/documents/{document_id}/download")
    
    async def process_document(self, document_id: str) -> APIResponse:
        """Process document."""
        return await self._make_request("POST", f"/api/v1/knowledge/documents/{document_id}/process")
    
    # Search endpoints
    async def search_knowledge(self, query: str, limit: int = 10) -> APIResponse:
        """Search knowledge base."""
        return await self._make_request("GET", "/api/v1/search/knowledge", params={
            "query": query,
            "limit": limit
        })
    
    async def search_conversations(self, query: str, conversation_id: Optional[str] = None, limit: int = 10) -> APIResponse:
        """Search conversations."""
        params = {"query": query, "limit": limit}
        if conversation_id:
            params["conversation_id"] = conversation_id
        return await self._make_request("GET", "/api/v1/search/conversations", params=params)


# Global API client instance
api_client = APIClient() 