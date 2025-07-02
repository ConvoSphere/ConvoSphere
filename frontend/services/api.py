"""
API service for frontend-backend communication.

This module provides a centralized API client for communicating with
the backend FastAPI server.
"""

import json
import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from urllib.parse import urljoin


@dataclass
class APIResponse:
    """API response wrapper."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    status_code: int = 200


class APIClient:
    """API client for backend communication."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.token: Optional[str] = None
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
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
        try:
            url = urljoin(self.base_url, endpoint)
            
            # Prepare request
            request_data = {
                "method": method,
                "url": url,
                "headers": self.headers.copy()
            }
            
            if data:
                request_data["data"] = json.dumps(data)
            
            if params:
                request_data["params"] = params
            
            # Make request (simulated for now)
            # In a real implementation, this would use aiohttp or httpx
            await asyncio.sleep(0.1)  # Simulate network delay
            
            # Simulate response
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
            
            # Knowledge base mock responses
            if method == "GET" and "knowledge/documents" in endpoint:
                return APIResponse(
                    success=True,
                    data=[
                        {
                            "id": "1",
                            "title": "API Documentation",
                            "description": "Complete API reference",
                            "file_name": "api_docs.pdf",
                            "file_size": 1024000,
                            "file_type": "application/pdf",
                            "status": "processed",
                            "created_at": "2024-01-15T10:30:00Z",
                            "updated_at": "2024-01-15T10:35:00Z",
                            "tags": ["api", "documentation"],
                            "chunk_count": 45
                        },
                        {
                            "id": "2",
                            "title": "User Guide",
                            "description": "User manual and tutorials",
                            "file_name": "user_guide.md",
                            "file_size": 256000,
                            "file_type": "text/markdown",
                            "status": "processed",
                            "created_at": "2024-01-14T14:20:00Z",
                            "updated_at": "2024-01-14T14:25:00Z",
                            "tags": ["guide", "tutorial"],
                            "chunk_count": 23
                        }
                    ],
                    status_code=200
                )
            
            if method == "GET" and "knowledge/search" in endpoint:
                return APIResponse(
                    success=True,
                    data=[
                        {
                            "id": "1",
                            "content": "This is a relevant search result about the query.",
                            "score": 0.85,
                            "document_id": "1",
                            "chunk_id": "chunk_1"
                        },
                        {
                            "id": "2",
                            "content": "Another relevant result with lower score.",
                            "score": 0.72,
                            "document_id": "2",
                            "chunk_id": "chunk_5"
                        }
                    ],
                    status_code=200
                )
            
            if method == "GET" and "search/conversations" in endpoint:
                return APIResponse(
                    success=True,
                    data=[
                        {
                            "id": "1",
                            "content": "Previous conversation about similar topic.",
                            "score": 0.78,
                            "conversation_id": "conv_1",
                            "message_id": "msg_5"
                        }
                    ],
                    status_code=200
                )
            
            # Default response
            return APIResponse(
                success=True,
                data={"message": "API call successful"},
                status_code=200
            )
            
        except Exception as e:
            return APIResponse(
                success=False,
                error=str(e),
                status_code=500
            )
    
    # Authentication endpoints
    async def login(self, email: str, password: str) -> APIResponse:
        """Login user."""
        return await self._make_request(
            "POST",
            "/api/v1/auth/login",
            data={"email": email, "password": password}
        )
    
    async def register(self, user_data: Dict[str, Any]) -> APIResponse:
        """Register new user."""
        return await self._make_request(
            "POST",
            "/api/v1/auth/register",
            data=user_data
        )
    
    async def get_current_user(self) -> APIResponse:
        """Get current user information."""
        return await self._make_request("GET", "/api/v1/auth/me")
    
    async def logout(self) -> APIResponse:
        """Logout user."""
        return await self._make_request("POST", "/api/v1/auth/logout")
    
    # Assistant endpoints
    async def get_assistants(self) -> APIResponse:
        """Get all assistants."""
        return await self._make_request("GET", "/api/v1/assistants")
    
    async def get_assistant(self, assistant_id: str) -> APIResponse:
        """Get assistant by ID."""
        return await self._make_request("GET", f"/api/v1/assistants/{assistant_id}")
    
    async def create_assistant(self, assistant_data: Dict[str, Any]) -> APIResponse:
        """Create new assistant."""
        return await self._make_request(
            "POST",
            "/api/v1/assistants",
            data=assistant_data
        )
    
    async def update_assistant(self, assistant_id: str, assistant_data: Dict[str, Any]) -> APIResponse:
        """Update assistant."""
        return await self._make_request(
            "PUT",
            f"/api/v1/assistants/{assistant_id}",
            data=assistant_data
        )
    
    async def delete_assistant(self, assistant_id: str) -> APIResponse:
        """Delete assistant."""
        return await self._make_request("DELETE", f"/api/v1/assistants/{assistant_id}")
    
    # Conversation endpoints
    async def get_conversations(self) -> APIResponse:
        """Get user conversations."""
        return await self._make_request("GET", "/api/v1/conversations")
    
    async def create_conversation(self, assistant_id: str, title: Optional[str] = None) -> APIResponse:
        """Create new conversation."""
        return await self._make_request(
            "POST",
            "/api/v1/chat/conversations",
            data={"assistant_id": assistant_id, "title": title}
        )
    
    async def get_conversation_messages(self, conversation_id: str) -> APIResponse:
        """Get conversation messages."""
        return await self._make_request(
            "GET",
            f"/api/v1/chat/conversations/{conversation_id}/messages"
        )
    
    async def send_message(self, conversation_id: str, content: str) -> APIResponse:
        """Send message to assistant."""
        return await self._make_request(
            "POST",
            f"/api/v1/chat/conversations/{conversation_id}/messages",
            data={"content": content, "message_type": "text"}
        )
    
    # Tool endpoints
    async def get_tools(self) -> APIResponse:
        """Get available tools."""
        return await self._make_request("GET", "/api/v1/tools")
    
    # Health check
    async def health_check(self) -> APIResponse:
        """Check API health."""
        return await self._make_request("GET", "/api/v1/health")
    
    # MCP API methods
    async def get_mcp_servers(self) -> APIResponse:
        """Get MCP servers."""
        return await self._make_request("GET", "/api/v1/mcp/servers")
    
    async def add_mcp_server(self, server_data: Dict[str, Any]) -> APIResponse:
        """Add MCP server."""
        return await self._make_request("POST", "/api/v1/mcp/servers", data=server_data)
    
    async def remove_mcp_server(self, server_id: str) -> APIResponse:
        """Remove MCP server."""
        return await self._make_request("DELETE", f"/api/v1/mcp/servers/{server_id}")
    
    async def get_mcp_tools(self) -> APIResponse:
        """Get MCP tools."""
        return await self._make_request("GET", "/api/v1/mcp/tools")
    
    async def get_mcp_tool(self, tool_id: str) -> APIResponse:
        """Get MCP tool."""
        return await self._make_request("GET", f"/api/v1/mcp/tools/{tool_id}")
    
    async def execute_mcp_tool(self, tool_id: str, arguments: Dict[str, Any]) -> APIResponse:
        """Execute MCP tool."""
        return await self._make_request(
            "POST",
            f"/api/v1/mcp/tools/{tool_id}/execute",
            data={"arguments": arguments}
        )
    
    # Knowledge base endpoints
    async def get_documents(self, skip: int = 0, limit: int = 100) -> APIResponse:
        """Get documents from knowledge base."""
        return await self._make_request(
            "GET",
            "/api/v1/knowledge/documents",
            params={"skip": skip, "limit": limit}
        )
    
    async def get_document(self, document_id: str) -> APIResponse:
        """Get document by ID."""
        return await self._make_request("GET", f"/api/v1/knowledge/documents/{document_id}")
    
    async def upload_document(self, file_data: Dict[str, Any], metadata: Dict[str, Any]) -> APIResponse:
        """Upload document to knowledge base."""
        return await self._make_request(
            "POST",
            "/api/v1/knowledge/documents/upload",
            data={"file": file_data, "metadata": metadata}
        )
    
    async def delete_document(self, document_id: str) -> APIResponse:
        """Delete document from knowledge base."""
        return await self._make_request("DELETE", f"/api/v1/knowledge/documents/{document_id}")
    
    async def download_document(self, document_id: str) -> APIResponse:
        """Download document."""
        return await self._make_request("GET", f"/api/v1/knowledge/documents/{document_id}/download")
    
    async def process_document(self, document_id: str) -> APIResponse:
        """Process document for embedding."""
        return await self._make_request(
            "POST",
            f"/api/v1/knowledge/documents/{document_id}/process"
        )
    
    async def search_knowledge(self, query: str, limit: int = 10) -> APIResponse:
        """Search knowledge base."""
        return await self._make_request(
            "GET",
            "/api/v1/knowledge/search",
            params={"query": query, "limit": limit}
        )
    
    async def search_conversations(self, query: str, conversation_id: Optional[str] = None, limit: int = 10) -> APIResponse:
        """Search conversations semantically."""
        params = {"query": query, "limit": limit}
        if conversation_id:
            params["conversation_id"] = conversation_id
        return await self._make_request(
            "GET",
            "/api/v1/search/conversations",
            params=params
        )


# Global API client instance
api_client = APIClient() 