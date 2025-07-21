"""
API client for communicating with the backend API.

This module provides a high-level API client that wraps the HTTP client
and provides specific methods for each API endpoint.
"""

from typing import Any

from .http_client import http_client


class APIClient:
    """High-level API client for backend communication."""

    def __init__(self):
        """Initialize the API client."""
        self.client = http_client

    def set_auth_token(self, token: str):
        """Set authentication token."""
        self.client.set_auth_token(token)

    def clear_auth_token(self):
        """Clear authentication token."""
        self.client.clear_auth_token()

    # Authentication endpoints
    async def login(self, email: str, password: str) -> dict[str, Any]:
        """Login user."""
        data = {
            "username": email,
            "password": password,
        }
        return await self.client.post("/api/v1/auth/login", data=data)

    async def register(
        self, email: str, password: str, full_name: str,
    ) -> dict[str, Any]:
        """Register new user."""
        data = {
            "email": email,
            "password": password,
            "full_name": full_name,
        }
        return await self.client.post("/api/v1/auth/register", data=data)

    async def get_current_user(self) -> dict[str, Any]:
        """Get current user profile."""
        return await self.client.get("/api/v1/auth/me")

    async def refresh_token(self) -> dict[str, Any]:
        """Refresh authentication token."""
        return await self.client.post("/api/v1/auth/refresh")

    # User management
    async def get_users(self, skip: int = 0, limit: int = 100) -> dict[str, Any]:
        """Get users list."""
        params = {"skip": skip, "limit": limit}
        return await self.client.get("/api/v1/users", params=params)

    async def get_user(self, user_id: int) -> dict[str, Any]:
        """Get specific user."""
        return await self.client.get(f"/api/v1/users/{user_id}")

    async def update_user(self, user_id: int, data: dict[str, Any]) -> dict[str, Any]:
        """Update user."""
        return await self.client.put(f"/api/v1/users/{user_id}", data=data)

    async def delete_user(self, user_id: int) -> dict[str, Any]:
        """Delete user."""
        return await self.client.delete(f"/api/v1/users/{user_id}")

    # Conversations
    async def get_conversations(
        self, skip: int = 0, limit: int = 100,
    ) -> dict[str, Any]:
        """Get conversations list."""
        params = {"skip": skip, "limit": limit}
        return await self.client.get("/api/v1/conversations", params=params)

    async def get_conversation(self, conversation_id: int) -> dict[str, Any]:
        """Get specific conversation."""
        return await self.client.get(f"/api/v1/conversations/{conversation_id}")

    async def create_conversation(
        self, title: str, assistant_id: int | None = None,
    ) -> dict[str, Any]:
        """Create new conversation."""
        data = {"title": title}
        if assistant_id:
            data["assistant_id"] = str(assistant_id)
        return await self.client.post("/api/v1/conversations", data=data)

    async def update_conversation(
        self, conversation_id: int, data: dict[str, Any],
    ) -> dict[str, Any]:
        """Update conversation."""
        return await self.client.put(
            f"/api/v1/conversations/{conversation_id}", data=data,
        )

    async def delete_conversation(self, conversation_id: int) -> dict[str, Any]:
        """Delete conversation."""
        return await self.client.delete(f"/api/v1/conversations/{conversation_id}")

    # Messages
    async def get_messages(
        self, conversation_id: int, skip: int = 0, limit: int = 100,
    ) -> dict[str, Any]:
        """Get messages for conversation."""
        params = {"skip": skip, "limit": limit}
        return await self.client.get(
            f"/api/v1/conversations/{conversation_id}/messages", params=params,
        )

    async def send_message(
        self, conversation_id: int, content: str, role: str = "user",
    ) -> dict[str, Any]:
        """Send message to conversation."""
        data = {
            "content": content,
            "role": role,
        }
        return await self.client.post(
            f"/api/v1/conversations/{conversation_id}/messages", data=data,
        )

    # Assistants
    async def get_assistants(self, skip: int = 0, limit: int = 100) -> dict[str, Any]:
        """Get assistants list."""
        params = {"skip": skip, "limit": limit}
        return await self.client.get("/api/v1/assistants", params=params)

    async def get_assistant(self, assistant_id: int) -> dict[str, Any]:
        """Get specific assistant."""
        return await self.client.get(f"/api/v1/assistants/{assistant_id}")

    async def create_assistant(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create new assistant."""
        return await self.client.post("/api/v1/assistants", data=data)

    async def update_assistant(
        self, assistant_id: int, data: dict[str, Any],
    ) -> dict[str, Any]:
        """Update assistant."""
        return await self.client.put(f"/api/v1/assistants/{assistant_id}", data=data)

    async def delete_assistant(self, assistant_id: int) -> dict[str, Any]:
        """Delete assistant."""
        return await self.client.delete(f"/api/v1/assistants/{assistant_id}")

    # Tools
    async def get_tools(self, skip: int = 0, limit: int = 100) -> dict[str, Any]:
        """Get tools list."""
        params = {"skip": skip, "limit": limit}
        return await self.client.get("/api/v1/tools", params=params)

    async def get_tool(self, tool_id: int) -> dict[str, Any]:
        """Get specific tool."""
        return await self.client.get(f"/api/v1/tools/{tool_id}")

    async def create_tool(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create new tool."""
        return await self.client.post("/api/v1/tools", data=data)

    async def update_tool(self, tool_id: int, data: dict[str, Any]) -> dict[str, Any]:
        """Update tool."""
        return await self.client.put(f"/api/v1/tools/{tool_id}", data=data)

    async def delete_tool(self, tool_id: int) -> dict[str, Any]:
        """Delete tool."""
        return await self.client.delete(f"/api/v1/tools/{tool_id}")

    # Knowledge Base
    async def get_knowledge_documents(
        self, skip: int = 0, limit: int = 100,
    ) -> dict[str, Any]:
        """Get knowledge documents."""
        params = {"skip": skip, "limit": limit}
        return await self.client.get("/api/v1/knowledge", params=params)

    async def upload_document(
        self, file_data: bytes, filename: str, metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Upload document to knowledge base."""
        # This would need special handling for file uploads
        # For now, return a placeholder
        return {"message": "File upload not implemented yet"}

    async def search_knowledge(self, query: str, limit: int = 10) -> dict[str, Any]:
        """Search knowledge base."""
        params = {"q": query, "limit": limit}
        return await self.client.get("/api/v1/knowledge/search", params=params)

    # Health check
    async def health_check(self) -> dict[str, Any]:
        """Check API health."""
        return await self.client.get("/api/v1/health")


# Global API client instance
api_client = APIClient()
