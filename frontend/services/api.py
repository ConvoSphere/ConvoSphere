"""
API service for frontend-backend communication.

This module provides a centralized API client for communicating with
the backend FastAPI server using real HTTP requests.
"""

import json
import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from urllib.parse import urljoin

try:
    import httpx
    from loguru import logger
except ImportError:
    # Fallback for development without dependencies
    httpx = None
    logger = None


@dataclass
class APIResponse:
    """API response wrapper."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    status_code: int = 200


class APIClient:
    """API client for backend communication."""
    
    def __init__(self, base_url: str = "http://backend:8000"):
        self.base_url = base_url.rstrip("/")
        self.token: Optional[str] = None
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        self.client: Optional[httpx.AsyncClient] = None
    
    def set_token(self, token: str):
        """Set authentication token."""
        self.token = token
        self.headers["Authorization"] = f"Bearer {token}"
    
    def clear_token(self):
        """Clear authentication token."""
        self.token = None
        if "Authorization" in self.headers:
            del self.headers["Authorization"]
    
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
        # Fallback to mock responses if httpx is not available
        if not httpx:
            return await self._mock_request(method, endpoint, data, params)
        
        try:
            url = urljoin(self.base_url, endpoint)
            
            # Create client if not exists
            if not self.client:
                self.client = httpx.AsyncClient(timeout=30.0)
            
            # Prepare headers
            headers = self.headers.copy()
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
            
            # Make request
            if logger:
                logger.debug(f"Making {method} request to {url}")
            
            response = await self.client.request(
                method=method,
                url=url,
                headers=headers,
                json=data if data else None,
                params=params if params else None
            )
            
            # Handle response
            if response.status_code < 400:
                try:
                    response_data = response.json() if response.content else None
                except json.JSONDecodeError:
                    response_data = response.text
                
                return APIResponse(
                    success=True,
                    data=response_data,
                    status_code=response.status_code
                )
            else:
                try:
                    error_data = response.json()
                    error_message = error_data.get("detail", response.text)
                except json.JSONDecodeError:
                    error_message = response.text
                
                if logger:
                    logger.error(f"API request failed: {response.status_code} - {error_message}")
                
                return APIResponse(
                    success=False,
                    error=error_message,
                    status_code=response.status_code
                )
                
        except httpx.RequestError as e:
            if logger:
                logger.error(f"Request error: {e}")
            return APIResponse(
                success=False,
                error=f"Network error: {str(e)}",
                status_code=0
            )
        except Exception as e:
            if logger:
                logger.error(f"Unexpected error: {e}")
            return APIResponse(
                success=False,
                error=f"Unexpected error: {str(e)}",
                status_code=0
            )
    
    async def _mock_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> APIResponse:
        """Mock request for development without dependencies."""
        await asyncio.sleep(0.1)  # Simulate network delay
        
        # Mock responses for development
        if method == "GET" and "health" in endpoint:
            return APIResponse(
                success=True,
                data={"status": "healthy", "version": "1.0.0"},
                status_code=200
            )
        
        if method == "POST" and "auth/login" in endpoint:
            return APIResponse(
                success=True,
                data={
                    "access_token": "mock_token_123",
                    "refresh_token": "mock_refresh_123",
                    "token_type": "bearer",
                    "expires_in": 1800
                },
                status_code=200
            )
        
        if method == "GET" and "assistants" in endpoint:
            return APIResponse(
                success=True,
                data=[
                    {
                        "id": "1",
                        "name": "General Assistant",
                        "description": "A helpful AI assistant",
                        "status": "active",
                        "model": "gpt-4"
                    },
                    {
                        "id": "2", 
                        "name": "Code Helper",
                        "description": "Specialized in programming",
                        "status": "active",
                        "model": "gpt-4"
                    }
                ],
                status_code=200
            )
        
        # Default response
        return APIResponse(
            success=True,
            data={"message": "Mock API call successful"},
            status_code=200
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