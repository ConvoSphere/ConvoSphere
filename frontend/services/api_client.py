"""
API client for handling HTTP requests to the backend.

This module provides a centralized API client with request/response
handling, authentication, and error management.
"""

import json
import asyncio
from typing import Optional, Dict, Any, List
from nicegui import ui


class APIClient:
    """Centralized API client for backend communication."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL for the API
        """
        self.base_url = base_url.rstrip('/')
        self.session_token: Optional[str] = None
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def set_auth_token(self, token: str):
        """Set authentication token."""
        self.session_token = token
        self.headers["Authorization"] = f"Bearer {token}"
    
    def clear_auth_token(self):
        """Clear authentication token."""
        self.session_token = None
        if "Authorization" in self.headers:
            del self.headers["Authorization"]
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            data: Request data
            params: Query parameters
            
        Returns:
            Dict containing response data
            
        Raises:
            Exception: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            # Prepare request data
            request_data = None
            if data:
                request_data = json.dumps(data)
            
            # Make request (simplified for NiceGUI)
            # In a real implementation, you would use aiohttp or httpx
            response = await self._simulate_request(method, url, request_data, params)
            
            return response
            
        except Exception as e:
            raise Exception(f"API request failed: {str(e)}")
    
    async def _simulate_request(
        self,
        method: str,
        url: str,
        data: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Simulate API request for development.
        
        In production, replace this with actual HTTP client.
        """
        # Simulate network delay
        await asyncio.sleep(0.1)
        
        # Mock responses for development
        if method == "POST" and "/auth/login" in url:
            if data and "test@example.com" in data and "password123" in data:
                return {
                    "success": True,
                    "access_token": "mock_token_123",
                    "token_type": "bearer",
                    "user": {
                        "id": 1,
                        "email": "test@example.com",
                        "username": "testuser",
                        "first_name": "Test",
                        "last_name": "User"
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "Invalid credentials"
                }
        
        elif method == "POST" and "/auth/register" in url:
            return {
                "success": True,
                "message": "User registered successfully"
            }
        
        elif method == "GET" and "/users/me" in url:
            return {
                "success": True,
                "user": {
                    "id": 1,
                    "email": "test@example.com",
                    "username": "testuser",
                    "first_name": "Test",
                    "last_name": "User"
                }
            }
        
        else:
            return {
                "success": True,
                "data": f"Mock response for {method} {url}"
            }
    
    # Authentication endpoints
    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login user."""
        data = {
            "username": email,
            "password": password
        }
        return await self._make_request("POST", "/auth/login", data)
    
    async def register(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register new user."""
        return await self._make_request("POST", "/auth/register", user_data)
    
    async def logout(self) -> Dict[str, Any]:
        """Logout user."""
        response = await self._make_request("POST", "/auth/logout")
        self.clear_auth_token()
        return response
    
    async def get_current_user(self) -> Dict[str, Any]:
        """Get current user information."""
        return await self._make_request("GET", "/users/me")
    
    # User management endpoints
    async def get_users(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get list of users."""
        return await self._make_request("GET", "/users", params=params)
    
    async def get_user(self, user_id: int) -> Dict[str, Any]:
        """Get user by ID."""
        return await self._make_request("GET", f"/users/{user_id}")
    
    async def update_user(self, user_id: int, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user."""
        return await self._make_request("PUT", f"/users/{user_id}", user_data)
    
    async def delete_user(self, user_id: int) -> Dict[str, Any]:
        """Delete user."""
        return await self._make_request("DELETE", f"/users/{user_id}")
    
    # Assistant endpoints
    async def get_assistants(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get list of assistants."""
        return await self._make_request("GET", "/assistants", params=params)
    
    async def get_assistant(self, assistant_id: int) -> Dict[str, Any]:
        """Get assistant by ID."""
        return await self._make_request("GET", f"/assistants/{assistant_id}")
    
    async def create_assistant(self, assistant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new assistant."""
        return await self._make_request("POST", "/assistants", assistant_data)
    
    async def update_assistant(self, assistant_id: int, assistant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update assistant."""
        return await self._make_request("PUT", f"/assistants/{assistant_id}", assistant_data)
    
    async def delete_assistant(self, assistant_id: int) -> Dict[str, Any]:
        """Delete assistant."""
        return await self._make_request("DELETE", f"/assistants/{assistant_id}")
    
    # Conversation endpoints
    async def get_conversations(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get list of conversations."""
        return await self._make_request("GET", "/conversations", params=params)
    
    async def get_conversation(self, conversation_id: int) -> Dict[str, Any]:
        """Get conversation by ID."""
        return await self._make_request("GET", f"/conversations/{conversation_id}")
    
    async def create_conversation(self, conversation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new conversation."""
        return await self._make_request("POST", "/conversations", conversation_data)
    
    async def update_conversation(self, conversation_id: int, conversation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update conversation."""
        return await self._make_request("PUT", f"/conversations/{conversation_id}", conversation_data)
    
    async def delete_conversation(self, conversation_id: int) -> Dict[str, Any]:
        """Delete conversation."""
        return await self._make_request("DELETE", f"/conversations/{conversation_id}")
    
    # Chat endpoints
    async def send_message(self, conversation_id: int, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send message to conversation."""
        return await self._make_request("POST", f"/conversations/{conversation_id}/messages", message_data)
    
    async def get_messages(self, conversation_id: int, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get messages for conversation."""
        return await self._make_request("GET", f"/conversations/{conversation_id}/messages", params=params)
    
    # Tool endpoints
    async def get_tools(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get list of tools."""
        return await self._make_request("GET", "/tools", params=params)
    
    async def get_tool(self, tool_id: int) -> Dict[str, Any]:
        """Get tool by ID."""
        return await self._make_request("GET", f"/tools/{tool_id}")
    
    async def create_tool(self, tool_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new tool."""
        return await self._make_request("POST", "/tools", tool_data)
    
    async def update_tool(self, tool_id: int, tool_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update tool."""
        return await self._make_request("PUT", f"/tools/{tool_id}", tool_data)
    
    async def delete_tool(self, tool_id: int) -> Dict[str, Any]:
        """Delete tool."""
        return await self._make_request("DELETE", f"/tools/{tool_id}")
    
    # Knowledge base endpoints
    async def get_knowledge_documents(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get list of knowledge documents."""
        return await self._make_request("GET", "/knowledge", params=params)
    
    async def upload_document(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Upload knowledge document."""
        return await self._make_request("POST", "/knowledge/upload", file_data)
    
    async def delete_document(self, document_id: int) -> Dict[str, Any]:
        """Delete knowledge document."""
        return await self._make_request("DELETE", f"/knowledge/{document_id}")
    
    # Health check
    async def health_check(self) -> Dict[str, Any]:
        """Check API health."""
        return await self._make_request("GET", "/health")


# Global API client instance
api_client = APIClient() 