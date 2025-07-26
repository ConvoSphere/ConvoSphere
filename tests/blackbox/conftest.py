"""
Blackbox test configuration and fixtures.

This module provides test configuration, fixtures, and utilities for
comprehensive blackbox testing of the AI Assistant Platform API.
"""

import json
import os
import tempfile
import uuid

import pytest
import requests
from requests import Response

# Test configuration
BASE_URL = "http://localhost:8000"
API_BASE_URL = f"{BASE_URL}/api/v1"
OPENAPI_URL = f"{BASE_URL}/openapi.json"

# Test user credentials
TEST_USER_CREDENTIALS = {
    "regular_user": {
        "email": "testuser@example.com",
        "username": "testuser",
        "password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User",
        "role": "user",
    },
    "admin_user": {
        "email": "admin@example.com",
        "username": "admin",
        "password": "AdminPassword123!",
        "first_name": "Admin",
        "last_name": "User",
        "role": "admin",
    },
    "manager_user": {
        "email": "manager@example.com",
        "username": "manager",
        "password": "ManagerPassword123!",
        "first_name": "Manager",
        "last_name": "User",
        "role": "manager",
    },
}

# Test data templates
TEST_ASSISTANT_DATA = {
    "name": "Test Assistant",
    "description": "A test assistant for blackbox testing",
    "system_prompt": "You are a helpful test assistant.",
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 1000,
    "is_active": True,
}

TEST_CONVERSATION_DATA = {
    "title": "Test Conversation",
    "assistant_id": None,  # Will be set dynamically
    "user_id": None,  # Will be set dynamically
}

TEST_MESSAGE_DATA = {
    "content": "Hello, this is a test message",
    "role": "user",
    "conversation_id": None,  # Will be set dynamically
}

TEST_DOCUMENT_DATA = {
    "title": "Test Document",
    "description": "A test document for blackbox testing",
    "file_path": None,  # Will be set dynamically
    "file_size": 1024,
    "file_type": "txt",
}

TEST_TOOL_DATA = {
    "name": "Test Tool",
    "description": "A test tool for blackbox testing",
    "category": "search",
    "function_name": "test_function",
    "parameters": {"query": {"type": "string", "description": "Search query"}},
}

# API endpoint categories for organized testing
API_ENDPOINTS = {
    "authentication": [
        "/auth/login",
        "/auth/logout",
        "/auth/refresh",
        "/auth/register",
        "/auth/me",
        "/auth/sso/providers",
        "/auth/sso/login/{provider}",
        "/auth/sso/callback/{provider}",
        "/auth/sso/link/{provider}",
        "/auth/sso/unlink/{provider}",
        "/auth/sso/metadata",
        "/auth/sso/bulk-sync/{provider}",
        "/auth/sso/provisioning/status/{user_id}",
    ],
    "users": [
        "/users/",
        "/users/me/profile",
        "/users/me/password",
        "/users/{user_id}",
        "/users/{user_id}/verify",
        "/users/search/email/{email}",
        "/users/search/username/{username}",
        "/users/bulk-update",
        "/users/groups",
        "/users/groups/assign",
        "/users/groups/{group_id}",
        "/users/sso",
        "/users/stats/overview",
        "/users/admin/system-status",
        "/users/admin/default-language",
        "/users/authenticate",
    ],
    "assistants": [
        "/assistants/",
        "/assistants/default",
        "/assistants/default/id",
        "/assistants/default/set",
        "/assistants/public",
        "/assistants/status/list",
        "/assistants/{assistant_id}",
        "/assistants/{assistant_id}/activate",
        "/assistants/{assistant_id}/deactivate",
        "/assistants/{assistant_id}/tools",
        "/assistants/{assistant_id}/tools/{tool_id}",
    ],
    "conversations": [
        "/conversations/",
        "/conversations/{conversation_id}",
        "/conversations/{conversation_id}/messages",
        "/conversations/{conversation_id}/archive",
    ],
    "chat": ["/chat/conversations", "/chat/conversations/{conversation_id}/messages"],
    "knowledge": [
        "/knowledge/documents",
        "/knowledge/documents/upload-advanced",
        "/knowledge/documents/{document_id}",
        "/knowledge/documents/{document_id}/download",
        "/knowledge/documents/{document_id}/process",
        "/knowledge/documents/{document_id}/reprocess",
        "/knowledge/search",
        "/knowledge/search/advanced",
        "/knowledge/search/history",
        "/knowledge/tags",
        "/knowledge/tags/search",
        "/knowledge/stats",
        "/knowledge/processing/jobs",
        "/knowledge/processing/engines",
        "/knowledge/processing/supported-formats",
    ],
    "tools": ["/tools/", "/tools/categories/list", "/tools/{tool_id}"],
    "ai": ["/ai/models", "/ai/providers", "/ai/health", "/ai/costs"],
    "rag": [
        "/rag/retrieve",
        "/rag/configs",
        "/rag/configs/{config_id}",
        "/rag/health",
        "/rag/metrics",
    ],
    "search": ["/search/conversation", "/search/knowledge"],
    "intelligence": [
        "/intelligence/analyze",
        "/intelligence/analytics/{conversation_id}",
        "/intelligence/sentiment",
        "/intelligence/sentiment/text",
        "/intelligence/metrics",
        "/intelligence/health",
    ],
    "mcp": [
        "/mcp/servers",
        "/mcp/servers/{server_id}",
        "/mcp/servers/{server_id}/resources",
        "/mcp/servers/{server_id}/resources/{resource_uri}/read",
        "/mcp/tools",
        "/mcp/tools/{tool_id}",
        "/mcp/tools/{tool_id}/execute",
    ],
    "health": [
        "/health/",
        "/health/database",
        "/health/redis",
        "/health/weaviate",
        "/health/detailed",
    ],
    "config": ["/config/", "/config"],
}


class APITestClient:
    """Client for making API requests with authentication and common utilities."""

    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.auth_tokens = {}
        self.current_user = None

    def set_auth_token(self, user_type: str, token: str):
        """Set authentication token for a user type."""
        self.auth_tokens[user_type] = token
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def get_auth_headers(self, user_type: str = None) -> dict[str, str]:
        """Get authentication headers for a user type."""
        headers = {"Content-Type": "application/json"}
        if user_type and user_type in self.auth_tokens:
            headers["Authorization"] = f"Bearer {self.auth_tokens[user_type]}"
        return headers

    def make_request(
        self,
        method: str,
        endpoint: str,
        data: dict = None,
        params: dict = None,
        headers: dict = None,
        user_type: str = None,
        files: dict = None,
    ) -> Response:
        """Make an HTTP request to the API."""
        url = f"{self.base_url}{endpoint}"
        request_headers = self.get_auth_headers(user_type)
        if headers:
            request_headers.update(headers)

        if files:
            # Remove Content-Type for file uploads
            request_headers.pop("Content-Type", None)

        return self.session.request(
            method=method,
            url=url,
            json=data,
            params=params,
            headers=request_headers,
            files=files,
        )

    def get(self, endpoint: str, **kwargs) -> Response:
        return self.make_request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> Response:
        return self.make_request("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs) -> Response:
        return self.make_request("PUT", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> Response:
        return self.make_request("DELETE", endpoint, **kwargs)

    def patch(self, endpoint: str, **kwargs) -> Response:
        return self.make_request("PATCH", endpoint, **kwargs)


class TestDataManager:
    """Manages test data creation, cleanup, and state."""

    def __init__(self):
        self.created_resources = {
            "users": [],
            "assistants": [],
            "conversations": [],
            "documents": [],
            "tools": [],
        }
        self.temp_files = []

    def create_temp_file(self, content: str, extension: str = ".txt") -> str:
        """Create a temporary file for testing."""
        temp_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=extension, delete=False, encoding="utf-8"
        )
        temp_file.write(content)
        temp_file.close()
        self.temp_files.append(temp_file.name)
        return temp_file.name

    def cleanup(self):
        """Clean up all created test resources."""
        # Clean up temporary files
        for file_path in self.temp_files:
            try:
                os.unlink(file_path)
            except OSError:
                pass
        self.temp_files.clear()

        # Reset created resources
        for resource_type in self.created_resources:
            self.created_resources[resource_type].clear()


class AssertionHelper:
    """Helper class for common API response assertions."""

    @staticmethod
    def assert_success_response(response: Response, expected_status: int = 200):
        """Assert that the response indicates success."""
        assert response.status_code == expected_status, (
            f"Expected status {expected_status}, got {response.status_code}. Response: {response.text}"
        )

    @staticmethod
    def assert_error_response(response: Response, expected_status: int = 400):
        """Assert that the response indicates an error."""
        assert response.status_code == expected_status, (
            f"Expected error status {expected_status}, got {response.status_code}. Response: {response.text}"
        )

    @staticmethod
    def assert_unauthorized(response: Response):
        """Assert that the response indicates unauthorized access."""
        assert response.status_code in [401, 403], (
            f"Expected unauthorized status (401/403), got {response.status_code}. Response: {response.text}"
        )

    @staticmethod
    def assert_not_found(response: Response):
        """Assert that the response indicates resource not found."""
        assert response.status_code == 404, (
            f"Expected not found status (404), got {response.status_code}. Response: {response.text}"
        )

    @staticmethod
    def assert_response_structure(data: Response | dict, required_fields: list[str]):
        """Assert that the response contains required fields."""
        # Handle both Response objects and dict objects
        if isinstance(data, Response):
            data = data.json()

        for field in required_fields:
            assert field in data, (
                f"Required field '{field}' not found in response: {data}"
            )

    @staticmethod
    def assert_list_response(response: Response, min_items: int = 0):
        """Assert that the response is a list with minimum items."""
        try:
            data = response.json()
        except json.JSONDecodeError:
            assert False, f"Response is not valid JSON: {response.text}"

        assert isinstance(data, list), f"Expected list response, got {type(data)}"
        assert len(data) >= min_items, (
            f"Expected at least {min_items} items, got {len(data)}"
        )


# Pytest fixtures
@pytest.fixture(scope="session")
def api_client() -> APITestClient:
    """Create API test client."""
    return APITestClient()


@pytest.fixture(scope="session")
def test_data_manager() -> TestDataManager:
    """Create test data manager."""
    return TestDataManager()


@pytest.fixture(scope="session")
def assertion_helper() -> AssertionHelper:
    """Create assertion helper."""
    return AssertionHelper()


@pytest.fixture(scope="session")
def openapi_spec() -> dict:
    """Load OpenAPI specification."""
    try:
        response = requests.get(OPENAPI_URL)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        pytest.skip(f"Could not load OpenAPI spec: {e}")


@pytest.fixture(scope="session")
def available_endpoints(openapi_spec) -> dict[str, list[str]]:
    """Get all available endpoints from OpenAPI spec."""
    if not openapi_spec:
        return API_ENDPOINTS

    paths = openapi_spec.get("paths", {})
    endpoints = {}

    for path, methods in paths.items():
        # Remove base path prefix
        if path.startswith("/api/v1"):
            path = path[7:]  # Remove "/api/v1"
        elif path.startswith("/api"):
            path = path[4:]  # Remove "/api"

        # Categorize endpoint
        for category, patterns in API_ENDPOINTS.items():
            for pattern in patterns:
                if path == pattern or path.startswith(
                    pattern.replace("{", "").replace("}", "")
                ):
                    if category not in endpoints:
                        endpoints[category] = []
                    if path not in endpoints[category]:
                        endpoints[category].append(path)
                    break

    return endpoints


@pytest.fixture(scope="function")
def authenticated_user(api_client, test_data_manager) -> tuple[str, dict]:
    """Create and authenticate a test user."""
    user_data = TEST_USER_CREDENTIALS["regular_user"].copy()

    # Generate unique email and username for each test
    unique_id = str(uuid.uuid4())[:8]
    user_data["email"] = f"testuser_{unique_id}@example.com"
    user_data["username"] = f"testuser_{unique_id}"

    # Register user
    response = api_client.post("/auth/register", data=user_data)
    if response.status_code != 201:
        # User might already exist, try to login
        response = api_client.post(
            "/auth/login",
            data={"email": user_data["email"], "password": user_data["password"]},
        )

    assert response.status_code in [200, 201], (
        f"Failed to create/authenticate user: {response.text}"
    )

    token_data = response.json()
    token = token_data.get("access_token")
    assert token, "No access token received"

    api_client.set_auth_token("regular_user", token)
    test_data_manager.created_resources["users"].append(user_data["email"])

    return token, user_data


@pytest.fixture(scope="function")
def authenticated_admin(api_client, test_data_manager) -> tuple[str, dict]:
    """Create and authenticate an admin user."""
    user_data = TEST_USER_CREDENTIALS["admin_user"].copy()

    # Generate unique email and username for each test
    unique_id = str(uuid.uuid4())[:8]
    user_data["email"] = f"admin_{unique_id}@example.com"
    user_data["username"] = f"admin_{unique_id}"

    # Register admin user
    response = api_client.post("/auth/register", data=user_data)
    if response.status_code != 201:
        # User might already exist, try to login
        response = api_client.post(
            "/auth/login",
            data={"email": user_data["email"], "password": user_data["password"]},
        )

    assert response.status_code in [200, 201], (
        f"Failed to create/authenticate admin: {response.text}"
    )

    token_data = response.json()
    token = token_data.get("access_token")
    assert token, "No access token received"

    api_client.set_auth_token("admin_user", token)
    test_data_manager.created_resources["users"].append(user_data["email"])

    return token, user_data


@pytest.fixture(scope="function")
def test_assistant(api_client, authenticated_user, test_data_manager) -> dict:
    """Create a test assistant."""
    assistant_data = TEST_ASSISTANT_DATA.copy()

    response = api_client.post("/assistants/", data=assistant_data)
    assert response.status_code == 200, f"Failed to create assistant: {response.text}"

    assistant = response.json()
    test_data_manager.created_resources["assistants"].append(assistant["id"])

    return assistant


@pytest.fixture(scope="function")
def test_conversation(
    api_client, authenticated_user, test_assistant, test_data_manager
) -> dict:
    """Create a test conversation."""
    conversation_data = TEST_CONVERSATION_DATA.copy()
    conversation_data["assistant_id"] = test_assistant["id"]

    response = api_client.post("/conversations/", data=conversation_data)
    assert response.status_code == 201, (
        f"Failed to create conversation: {response.text}"
    )

    conversation = response.json()
    test_data_manager.created_resources["conversations"].append(conversation["id"])

    return conversation


@pytest.fixture(scope="function")
def test_document(api_client, authenticated_user, test_data_manager) -> dict:
    """Create a test document."""
    # Create temporary file
    file_content = "This is a test document for blackbox testing."
    file_path = test_data_manager.create_temp_file(file_content, ".txt")

    # Upload document
    with open(file_path, "rb") as f:
        files = {"file": ("test_document.txt", f, "text/plain")}
        data = {
            "title": TEST_DOCUMENT_DATA["title"],
            "description": TEST_DOCUMENT_DATA["description"],
        }

        response = api_client.post("/knowledge/documents", data=data, files=files)
        assert response.status_code == 201, (
            f"Failed to upload document: {response.text}"
        )

    document = response.json()
    test_data_manager.created_resources["documents"].append(document["id"])

    return document


@pytest.fixture(autouse=True)
def cleanup_test_data(test_data_manager):
    """Clean up test data after each test."""
    yield
    test_data_manager.cleanup()


# Test configuration
def pytest_configure(config):
    """Configure pytest for blackbox testing."""
    config.addinivalue_line("markers", "blackbox: mark test as blackbox API test")
    config.addinivalue_line(
        "markers", "authentication: mark test as authentication test"
    )
    config.addinivalue_line("markers", "users: mark test as user management test")
    config.addinivalue_line(
        "markers", "assistants: mark test as assistant management test"
    )
    config.addinivalue_line("markers", "conversations: mark test as conversation test")
    config.addinivalue_line("markers", "knowledge: mark test as knowledge base test")
    config.addinivalue_line("markers", "tools: mark test as tools test")
    config.addinivalue_line("markers", "ai: mark test as AI service test")
    config.addinivalue_line("markers", "health: mark test as health check test")
    config.addinivalue_line("markers", "integration: mark test as integration test")
