from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio

from backend.main import app


@pytest.fixture(scope="session", autouse=True)
def setup_redis():
    """Setup Redis for tests - disable Redis completely for tests."""
    # Create a mock Redis client with async methods
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    mock_redis.delete.return_value = True
    mock_redis.incr.return_value = 1
    mock_redis.ping.return_value = True

    # Mock the entire redis_client module
    with (
        patch("app.core.redis_client.redis_client", mock_redis),
        patch("app.core.redis_client.get_redis", return_value=mock_redis),
        patch("app.core.redis_client.init_redis", return_value=mock_redis),
        patch("app.core.redis_client.check_redis_connection", return_value=True),
        patch(
            "app.core.redis_client.get_redis_info",
            return_value={
                "status": "connected",
                "version": "7.0.0",
                "connected_clients": 1,
                "used_memory_human": "1.0M",
                "uptime_in_seconds": 3600,
                "keyspace_hits": 100,
                "keyspace_misses": 10,
            },
        ),
    ):
        yield


@pytest_asyncio.fixture
async def async_client():
    """Async client fixture for testing FastAPI endpoints."""
    from fastapi.testclient import TestClient
    client = TestClient(app)
    yield client


@pytest.fixture()
def test_user_data():
    """Test user data for authentication tests."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User",
    }


@pytest.fixture()
def test_assistant_data():
    """Test assistant data for assistant tests."""
    return {
        "name": "Test Assistant",
        "description": "A test assistant for testing",
        "system_prompt": "You are a helpful test assistant.",
        "model": "gpt-4",
        "temperature": "0.7",
    }


@pytest.fixture()
def test_tool_data():
    """Test tool data for tool tests."""
    return {
        "name": "Test Tool",
        "description": "A test tool for testing",
        "category": "search",
        "function_name": "test_function",
    }
