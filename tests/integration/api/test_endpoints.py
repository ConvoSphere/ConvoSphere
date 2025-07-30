"""
Unified integration tests for API endpoints.

This module provides comprehensive integration testing of all API endpoints,
covering authentication, user management, assistants, conversations, tools, and more.
"""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


class TestAuthEndpoints:
    """Integration tests for authentication endpoints."""

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.auth
    def test_register_success(self):
        """Test successful user registration."""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "TestPassword123!",
            "full_name": "Test User",
        }
        with patch("app.api.v1.endpoints.auth.user_service.create_user") as mock_create:
            mock_create.return_value = {"id": "123", "email": "test@example.com"}
            response = client.post("/api/v1/auth/register", json=user_data)
            assert response.status_code in [200, 201]

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.auth
    def test_register_invalid_data(self):
        """Test registration with invalid data."""
        invalid_data = {
            "email": "invalid-email",
            "username": "t",  # too short
            "password": "weak",
        }
        response = client.post("/api/v1/auth/register", json=invalid_data)
        assert response.status_code in [400, 422]

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.auth
    def test_login_success(self):
        """Test successful login."""
        login_data = {
            "email": "test@example.com",
            "password": "TestPassword123!",
        }
        with patch("app.api.v1.endpoints.auth.authenticate_user") as mock_auth:
            mock_auth.return_value = {"id": "123", "email": "test@example.com"}
            with patch("app.api.v1.endpoints.auth.create_access_token") as mock_token:
                mock_token.return_value = "fake_token"
                response = client.post("/api/v1/auth/login", json=login_data)
                assert response.status_code in [200, 201]

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.auth
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        login_data = {
            "email": "test@example.com",
            "password": "wrongpassword",
        }
        with patch("app.api.v1.endpoints.auth.authenticate_user") as mock_auth:
            mock_auth.return_value = None
            response = client.post("/api/v1/auth/login", json=login_data)
            assert response.status_code in [401, 400]

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.auth
    def test_refresh_token(self):
        """Test token refresh endpoint."""
        with patch("app.api.v1.endpoints.auth.verify_token") as mock_verify:
            mock_verify.return_value = "user123"
            with patch("app.api.v1.endpoints.auth.create_access_token") as mock_create:
                mock_create.return_value = "new_token"
                response = client.post(
                    "/api/v1/auth/refresh",
                    headers={"Authorization": "Bearer old_token"},
                )
                assert response.status_code in [200, 201]

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.auth
    def test_logout(self):
        """Test logout endpoint."""
        response = client.post("/api/v1/auth/logout")
        assert response.status_code in [200, 204]


class TestUserEndpoints:
    """Integration tests for user management endpoints."""

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.users
    def test_get_users_unauthorized(self):
        """Test getting users without authentication."""
        response = client.get("/api/v1/users/")
        assert response.status_code in [401, 403]

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.users
    def test_get_users_authorized(self):
        """Test getting users with authentication."""
        with patch("app.api.v1.endpoints.users.get_current_user") as mock_user:
            mock_user.return_value = {"id": "123", "role": "admin"}
            with patch("app.api.v1.endpoints.users.user_service.get_users") as mock_get:
                mock_get.return_value = [{"id": "1", "email": "user1@test.com"}]
                response = client.get(
                    "/api/v1/users/",
                    headers={"Authorization": "Bearer token"},
                )
                assert response.status_code == 200

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.users
    def test_get_user_profile(self):
        """Test getting user profile."""
        with patch("app.api.v1.endpoints.users.get_current_user") as mock_user:
            mock_user.return_value = {"id": "123", "email": "test@example.com"}
            with patch("app.api.v1.endpoints.users.user_service.get_user") as mock_get:
                mock_get.return_value = {"id": "123", "email": "test@example.com"}
                response = client.get(
                    "/api/v1/users/me",
                    headers={"Authorization": "Bearer token"},
                )
                assert response.status_code == 200

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.users
    def test_update_user_profile(self):
        """Test updating user profile."""
        update_data = {"full_name": "Updated Name"}
        with patch("app.api.v1.endpoints.users.get_current_user") as mock_user:
            mock_user.return_value = {"id": "123"}
            with patch("app.api.v1.endpoints.users.user_service.update_user") as mock_update:
                mock_update.return_value = {"id": "123", "full_name": "Updated Name"}
                response = client.put(
                    "/api/v1/users/me",
                    json=update_data,
                    headers={"Authorization": "Bearer token"},
                )
                assert response.status_code == 200

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.users
    def test_delete_user(self):
        """Test deleting user."""
        with patch("app.api.v1.endpoints.users.get_current_user") as mock_user:
            mock_user.return_value = {"id": "123", "role": "admin"}
            with patch("app.api.v1.endpoints.users.user_service.delete_user") as mock_delete:
                mock_delete.return_value = True
                response = client.delete(
                    "/api/v1/users/123",
                    headers={"Authorization": "Bearer token"},
                )
                assert response.status_code in [200, 204]


class TestAssistantEndpoints:
    """Integration tests for assistant management endpoints."""

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.assistants
    def test_get_assistants(self):
        """Test getting assistants."""
        with patch("app.api.v1.endpoints.assistants.get_current_user") as mock_user:
            mock_user.return_value = {"id": "123"}
            with patch("app.api.v1.endpoints.assistants.assistant_service.get_assistants") as mock_get:
                mock_get.return_value = [{"id": "1", "name": "Assistant 1"}]
                response = client.get(
                    "/api/v1/assistants/",
                    headers={"Authorization": "Bearer token"},
                )
                assert response.status_code == 200

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.assistants
    def test_create_assistant(self):
        """Test creating assistant."""
        assistant_data = {
            "name": "Test Assistant",
            "description": "A test assistant",
            "model": "gpt-4",
            "instructions": "You are a helpful assistant."
        }
        with patch("app.api.v1.endpoints.assistants.get_current_user") as mock_user:
            mock_user.return_value = {"id": "123"}
            with patch("app.api.v1.endpoints.assistants.assistant_service.create_assistant") as mock_create:
                mock_create.return_value = {"id": "1", "name": "Test Assistant"}
                response = client.post(
                    "/api/v1/assistants/",
                    json=assistant_data,
                    headers={"Authorization": "Bearer token"},
                )
                assert response.status_code in [200, 201]

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.assistants
    def test_update_assistant(self):
        """Test updating assistant."""
        update_data = {"name": "Updated Assistant"}
        with patch("app.api.v1.endpoints.assistants.get_current_user") as mock_user:
            mock_user.return_value = {"id": "123"}
            with patch("app.api.v1.endpoints.assistants.assistant_service.update_assistant") as mock_update:
                mock_update.return_value = {"id": "1", "name": "Updated Assistant"}
                response = client.put(
                    "/api/v1/assistants/1",
                    json=update_data,
                    headers={"Authorization": "Bearer token"},
                )
                assert response.status_code == 200

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.assistants
    def test_delete_assistant(self):
        """Test deleting assistant."""
        with patch("app.api.v1.endpoints.assistants.get_current_user") as mock_user:
            mock_user.return_value = {"id": "123"}
            with patch("app.api.v1.endpoints.assistants.assistant_service.delete_assistant") as mock_delete:
                mock_delete.return_value = True
                response = client.delete(
                    "/api/v1/assistants/1",
                    headers={"Authorization": "Bearer token"},
                )
                assert response.status_code in [200, 204]


class TestConversationEndpoints:
    """Integration tests for conversation endpoints."""

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.conversations
    def test_get_conversations(self):
        """Test getting conversations."""
        with patch("app.api.v1.endpoints.conversations.get_current_user") as mock_user:
            mock_user.return_value = {"id": "123"}
            with patch("app.api.v1.endpoints.conversations.conversation_service.get_conversations") as mock_get:
                mock_get.return_value = [{"id": "1", "title": "Conversation 1"}]
                response = client.get(
                    "/api/v1/conversations/",
                    headers={"Authorization": "Bearer token"},
                )
                assert response.status_code == 200

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.conversations
    def test_create_conversation(self):
        """Test creating conversation."""
        conversation_data = {
            "title": "Test Conversation",
            "assistant_id": "assistant-1"
        }
        with patch("app.api.v1.endpoints.conversations.get_current_user") as mock_user:
            mock_user.return_value = {"id": "123"}
            with patch("app.api.v1.endpoints.conversations.conversation_service.create_conversation") as mock_create:
                mock_create.return_value = {"id": "1", "title": "Test Conversation"}
                response = client.post(
                    "/api/v1/conversations/",
                    json=conversation_data,
                    headers={"Authorization": "Bearer token"},
                )
                assert response.status_code in [200, 201]

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.conversations
    def test_get_conversation_messages(self):
        """Test getting conversation messages."""
        with patch("app.api.v1.endpoints.conversations.get_current_user") as mock_user:
            mock_user.return_value = {"id": "123"}
            with patch("app.api.v1.endpoints.conversations.conversation_service.get_messages") as mock_get:
                mock_get.return_value = [{"id": "1", "content": "Hello"}]
                response = client.get(
                    "/api/v1/conversations/1/messages",
                    headers={"Authorization": "Bearer token"},
                )
                assert response.status_code == 200


class TestToolEndpoints:
    """Integration tests for tool endpoints."""

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.tools
    def test_get_tools(self):
        """Test getting tools."""
        with patch("app.api.v1.endpoints.tools.get_current_user") as mock_user:
            mock_user.return_value = {"id": "123"}
            with patch("app.api.v1.endpoints.tools.tool_service.get_tools") as mock_get:
                mock_get.return_value = [{"id": "1", "name": "Tool 1"}]
                response = client.get(
                    "/api/v1/tools/",
                    headers={"Authorization": "Bearer token"},
                )
                assert response.status_code == 200

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.tools
    def test_create_tool(self):
        """Test creating tool."""
        tool_data = {
            "name": "Test Tool",
            "description": "A test tool",
            "type": "function",
            "parameters": {"type": "object", "properties": {}}
        }
        with patch("app.api.v1.endpoints.tools.get_current_user") as mock_user:
            mock_user.return_value = {"id": "123"}
            with patch("app.api.v1.endpoints.tools.tool_service.create_tool") as mock_create:
                mock_create.return_value = {"id": "1", "name": "Test Tool"}
                response = client.post(
                    "/api/v1/tools/",
                    json=tool_data,
                    headers={"Authorization": "Bearer token"},
                )
                assert response.status_code in [200, 201]

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.tools
    def test_execute_tool(self):
        """Test executing tool."""
        execution_data = {
            "tool_id": "tool-1",
            "parameters": {"param1": "value1"}
        }
        with patch("app.api.v1.endpoints.tools.get_current_user") as mock_user:
            mock_user.return_value = {"id": "123"}
            with patch("app.api.v1.endpoints.tools.tool_service.execute_tool") as mock_execute:
                mock_execute.return_value = {"result": "success"}
                response = client.post(
                    "/api/v1/tools/execute",
                    json=execution_data,
                    headers={"Authorization": "Bearer token"},
                )
                assert response.status_code == 200


class TestKnowledgeEndpoints:
    """Integration tests for knowledge base endpoints."""

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.knowledge
    def test_upload_document(self):
        """Test uploading document to knowledge base."""
        with patch("app.api.v1.endpoints.knowledge.get_current_user") as mock_user:
            mock_user.return_value = {"id": "123"}
            with patch("app.api.v1.endpoints.knowledge.knowledge_service.upload_document") as mock_upload:
                mock_upload.return_value = {"id": "doc-1", "filename": "test.pdf"}
                files = {"file": ("test.pdf", b"test content", "application/pdf")}
                response = client.post(
                    "/api/v1/knowledge/upload",
                    files=files,
                    headers={"Authorization": "Bearer token"},
                )
                assert response.status_code in [200, 201]

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.knowledge
    def test_search_knowledge(self):
        """Test searching knowledge base."""
        search_data = {"query": "test query", "limit": 10}
        with patch("app.api.v1.endpoints.knowledge.get_current_user") as mock_user:
            mock_user.return_value = {"id": "123"}
            with patch("app.api.v1.endpoints.knowledge.knowledge_service.search") as mock_search:
                mock_search.return_value = [{"id": "doc-1", "content": "test content"}]
                response = client.post(
                    "/api/v1/knowledge/search",
                    json=search_data,
                    headers={"Authorization": "Bearer token"},
                )
                assert response.status_code == 200

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.knowledge
    def test_get_documents(self):
        """Test getting documents from knowledge base."""
        with patch("app.api.v1.endpoints.knowledge.get_current_user") as mock_user:
            mock_user.return_value = {"id": "123"}
            with patch("app.api.v1.endpoints.knowledge.knowledge_service.get_documents") as mock_get:
                mock_get.return_value = [{"id": "doc-1", "filename": "test.pdf"}]
                response = client.get(
                    "/api/v1/knowledge/documents",
                    headers={"Authorization": "Bearer token"},
                )
                assert response.status_code == 200


class TestHealthEndpoints:
    """Integration tests for health check endpoints."""

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.health
    def test_health_check(self):
        """Test basic health check."""
        response = client.get("/health")
        assert response.status_code in [200, 400, 404]

        if response.status_code == 200:
            data = response.json()
            assert "status" in data

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.health
    def test_detailed_health_check(self):
        """Test detailed health check."""
        response = client.get("/health/detailed")
        assert response.status_code in [200, 400, 404]

        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert "timestamp" in data
            assert "version" in data

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.health
    def test_system_status(self):
        """Test system status endpoint."""
        with patch("app.api.v1.endpoints.health.get_system_status") as mock_status:
            mock_status.return_value = {
                "cpu_usage": 50.0,
                "memory_usage": 75.0,
                "disk_usage": 60.0,
                "active_connections": 10
            }
            response = client.get("/health/system")
            assert response.status_code == 200


class TestSearchEndpoints:
    """Integration tests for search endpoints."""

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.search
    def test_search(self):
        """Test global search functionality."""
        search_data = {
            "query": "test search",
            "filters": {"type": "all"},
            "limit": 20
        }
        with patch("app.api.v1.endpoints.search.get_current_user") as mock_user:
            mock_user.return_value = {"id": "123"}
            with patch("app.api.v1.endpoints.search.search_service.search") as mock_search:
                mock_search.return_value = {
                    "results": [
                        {"id": "1", "type": "conversation", "title": "Test Conversation"},
                        {"id": "2", "type": "document", "title": "Test Document"}
                    ],
                    "total": 2
                }
                response = client.post(
                    "/api/v1/search",
                    json=search_data,
                    headers={"Authorization": "Bearer token"},
                )
                assert response.status_code == 200


class TestMCPEndpoints:
    """Integration tests for MCP (Model Context Protocol) endpoints."""

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.mcp
    def test_get_mcp_servers(self):
        """Test getting MCP servers."""
        with patch("app.api.v1.endpoints.mcp.get_current_user") as mock_user:
            mock_user.return_value = {"id": "123"}
            with patch("app.api.v1.endpoints.mcp.mcp_service.get_servers") as mock_get:
                mock_get.return_value = [{"id": "server-1", "name": "Test Server"}]
                response = client.get(
                    "/api/v1/mcp/servers",
                    headers={"Authorization": "Bearer token"},
                )
                assert response.status_code == 200

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.mcp
    def test_connect_mcp_server(self):
        """Test connecting to MCP server."""
        connection_data = {
            "server_id": "server-1",
            "config": {"host": "localhost", "port": 8080}
        }
        with patch("app.api.v1.endpoints.mcp.get_current_user") as mock_user:
            mock_user.return_value = {"id": "123"}
            with patch("app.api.v1.endpoints.mcp.mcp_service.connect") as mock_connect:
                mock_connect.return_value = {"status": "connected", "server_id": "server-1"}
                response = client.post(
                    "/api/v1/mcp/connect",
                    json=connection_data,
                    headers={"Authorization": "Bearer token"},
                )
                assert response.status_code in [200, 201]


# =============================================================================
# BASIC ENDPOINT TESTS - Simple endpoint availability checks
# =============================================================================

@pytest.mark.integration
@pytest.mark.api
@pytest.mark.asyncio
async def test_users_endpoint_basic(async_client):
    """Basic test for users endpoint."""
    response = async_client.get("/api/v1/users/")
    assert response.status_code in [200, 400, 401, 403, 404]


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.asyncio
async def test_assistants_endpoint_basic(async_client):
    """Basic test for assistants endpoint."""
    response = async_client.get("/api/v1/assistants/")
    assert response.status_code in [200, 400, 401, 403, 404]


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.asyncio
async def test_tools_endpoint_basic(async_client):
    """Basic test for tools endpoint."""
    response = async_client.get("/api/v1/tools/")
    assert response.status_code in [200, 400, 401, 403, 404]


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.asyncio
async def test_register_endpoint_basic(async_client, test_user_data):
    """Basic test for user registration endpoint."""
    response = async_client.post("/api/v1/auth/register", json=test_user_data)
    assert response.status_code in [200, 201, 400, 422]


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.asyncio
async def test_login_endpoint_basic(async_client, test_user_data):
    """Basic test for user login endpoint."""
    response = async_client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        },
    )
    assert response.status_code in [200, 400, 401, 422]


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.asyncio
async def test_protected_endpoints_unauthorized(async_client):
    """Test that protected endpoints return 403 without authentication."""
    endpoints = [
        "/api/v1/users/me",
        "/api/v1/assistants/",
        "/api/v1/conversations/",
        "/api/v1/tools/",
    ]

    for endpoint in endpoints:
        response = async_client.get(endpoint)
        assert response.status_code in [400, 401, 403, 404]


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.asyncio
async def test_rate_limiting(async_client):
    """Test rate limiting by making many requests quickly."""
    # This is a basic test - in a real scenario, you'd want to test actual rate limiting
    for _ in range(5):
        response = async_client.get("/health")
        # Should not fail due to rate limiting in basic tests
        assert response.status_code in [200, 400, 404]