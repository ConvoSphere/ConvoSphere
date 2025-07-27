"""
Consolidated test configuration and fixtures for AI Assistant Platform.
This file combines fixtures from both tests/conftest.py and backend/tests/conftest.py
"""

import asyncio
import os

# Update import paths for new test structure
import sys
import tempfile
from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from backend.app.core.database import get_db
from backend.app.models.base import Base
from backend.app.models.knowledge import Document
from backend.app.models.user import User

# Import the main application
from backend.main import app

# Test configuration - Using SQLite for fast tests, PostgreSQL for compatibility
import os

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", 
    "sqlite:///./test.db"
)
TEST_REDIS_URL = "redis://localhost:6380"
TEST_WEAVIATE_URL = "http://localhost:8081"

# Test data fixtures
TEST_USER_DATA = {
    "email": "test@example.com",
    "username": "testuser",
    "password": "testpassword123",
    "first_name": "Test",
    "last_name": "User",
    "role": "user",
}

TEST_ADMIN_DATA = {
    "email": "admin@example.com",
    "username": "admin",
    "password": "adminpassword123",
    "first_name": "Admin",
    "last_name": "User",
    "role": "admin",
}

TEST_ASSISTANT_DATA = {
    "name": "Test Assistant",
    "description": "A test assistant for testing purposes",
    "system_prompt": "You are a helpful test assistant.",
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 1000,
    "is_active": True,
}

TEST_CONVERSATION_DATA = {
    "title": "Test Conversation",
    "assistant_id": 1,
    "user_id": 1,
}

TEST_MESSAGE_DATA = {
    "content": "Hello, this is a test message",
    "role": "user",
    "conversation_id": 1,
}

TEST_DOCUMENT_DATA = {
    "title": "Test Document",
    "description": "A test document for testing",
    "file_path": "/tmp/test_document.pdf",
    "file_size": 1024,
    "file_type": "pdf",
}

TEST_TOOL_DATA = {
    "name": "Test Tool",
    "description": "A test tool for testing",
    "category": "search",
    "function_name": "test_function",
    "parameters": {
        "query": {"type": "string", "description": "Search query"},
    },
}


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_engine():
    """Create database engine for testing."""
    engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in TEST_DATABASE_URL else {}
)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def test_db_session_factory(test_engine):
    """Create database session factory for testing."""
    return sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def test_db_session(test_db_session_factory, test_engine):
    """Create a new database session for a test."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = test_db_session_factory(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def override_get_db(test_db_session):
    """Override the database dependency."""

    def _override_get_db():
        try:
            yield test_db_session
        finally:
            pass

    return _override_get_db


@pytest.fixture
def client(override_get_db):
    """Create a test client."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def async_client(override_get_db):
    """Create an async test client."""
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="session", autouse=True)
def setup_redis_mock():
    """Mock Redis for testing."""
    with patch("backend.app.core.redis_client.redis.Redis") as mock_redis:
        mock_redis_instance = MagicMock()
        mock_redis.return_value = mock_redis_instance
        yield mock_redis_instance


@pytest.fixture(scope="session", autouse=True)
def setup_weaviate_mock():
    """Mock Weaviate for testing."""
    with patch(
        "backend.app.services.weaviate_service.weaviate.Client"
    ) as mock_weaviate:
        mock_client = MagicMock()
        mock_weaviate.return_value = mock_client
        yield mock_client


@pytest.fixture
def test_user_headers(client, test_user_data):
    """Get headers for authenticated user."""
    response = client.post("/api/v1/auth/register", json=test_user_data)
    if response.status_code == 201:
        token = response.json().get("access_token")
        return {"Authorization": f"Bearer {token}"}
    return {}


@pytest.fixture
def test_admin_headers(client, test_admin_data):
    """Get headers for authenticated admin."""
    response = client.post("/api/v1/auth/register", json=test_admin_data)
    if response.status_code == 201:
        token = response.json().get("access_token")
        return {"Authorization": f"Bearer {token}"}
    return {}


@pytest.fixture
def test_user(test_db_session):
    """Create a test user."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password",
        first_name="Test",
        last_name="User",
    )
    test_db_session.add(user)
    test_db_session.commit()
    test_db_session.refresh(user)
    return user


@pytest.fixture
def test_admin(test_db_session):
    """Create a test admin user."""
    from backend.app.models.user import UserRole

    admin_user = User(
        email="admin@example.com",
        username="adminuser",
        hashed_password="hashed_password",
        first_name="Admin",
        last_name="User",
        role=UserRole.ADMIN,
    )
    test_db_session.add(admin_user)
    test_db_session.commit()
    test_db_session.refresh(admin_user)
    return admin_user


@pytest.fixture
def test_assistant(test_db_session, test_user):
    """Create a test assistant."""
    from backend.app.models.assistant import Assistant

    assistant = Assistant(
        name="Test Assistant",
        description="A test assistant",
        system_prompt="You are a helpful assistant.",
        model="gpt-4",
        temperature=0.7,
        max_tokens=1000,
        is_active=True,
        user_id=test_user.id,
    )
    test_db_session.add(assistant)
    test_db_session.commit()
    test_db_session.refresh(assistant)
    return assistant


@pytest.fixture
def test_conversation(test_db_session, test_user, test_assistant):
    """Create a test conversation."""
    from backend.app.models.conversation import Conversation

    conversation = Conversation(
        title="Test Conversation",
        user_id=test_user.id,
        assistant_id=test_assistant.id,
    )
    test_db_session.add(conversation)
    test_db_session.commit()
    test_db_session.refresh(conversation)
    return conversation


@pytest.fixture
def test_message(test_db_session, test_conversation):
    """Create a test message."""
    from backend.app.models.message import Message

    message = Message(
        content="Hello, this is a test message",
        role="user",
        conversation_id=test_conversation.id,
    )
    test_db_session.add(message)
    test_db_session.commit()
    test_db_session.refresh(message)
    return message


@pytest.fixture
def test_document(test_db_session, test_user):
    """Create a test document."""
    document = Document(
        title="Test Document",
        description="A test document",
        file_path="/tmp/test_document.pdf",
        file_size=1024,
        file_type="pdf",
        user_id=test_user.id,
    )
    test_db_session.add(document)
    test_db_session.commit()
    test_db_session.refresh(document)
    return document


@pytest.fixture
def test_tool(test_db_session):
    """Create a test tool."""
    from backend.app.models.tool import Tool

    tool = Tool(
        name="Test Tool",
        description="A test tool",
        category="search",
        function_name="test_function",
        parameters={
            "query": {"type": "string", "description": "Search query"},
        },
    )
    test_db_session.add(tool)
    test_db_session.commit()
    test_db_session.refresh(tool)
    return tool


@pytest.fixture
def temp_file():
    """Create a temporary file."""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"Test content")
        temp_file_path = f.name
    yield temp_file_path
    os.unlink(temp_file_path)


@pytest.fixture
def temp_pdf_file():
    """Create a temporary PDF file."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(b"%PDF-1.4\nTest PDF content")
        temp_file_path = f.name
    yield temp_file_path
    os.unlink(temp_file_path)


@pytest.fixture
def mock_llm_response():
    """Mock LLM response."""
    return {
        "choices": [
            {
                "message": {
                    "content": "This is a mock response from the LLM.",
                    "role": "assistant",
                }
            }
        ]
    }


@pytest.fixture
def mock_embedding_response():
    """Mock embedding response."""
    return {
        "data": [
            {
                "embedding": [0.1, 0.2, 0.3, 0.4, 0.5] * 100  # 500-dimensional vector
            }
        ]
    }


@pytest.fixture
def test_data():
    """General test data."""
    return {
        "users": [test_user_data, test_admin_data],
        "assistants": [test_assistant_data],
        "conversations": [test_conversation_data],
        "messages": [test_message_data],
        "documents": [test_document_data],
        "tools": [test_tool_data],
    }


@pytest.fixture
def performance_test_data():
    """Data for performance tests."""
    return {
        "large_text": "Lorem ipsum " * 1000,
        "many_users": [
            {"email": f"user{i}@example.com", "username": f"user{i}"}
            for i in range(100)
        ],
        "many_documents": [
            {"title": f"Doc {i}", "content": f"Content {i}"} for i in range(50)
        ],
    }


@pytest.fixture
def security_test_payloads():
    """Payloads for security tests."""
    return {
        "sql_injection": "'; DROP TABLE users; --",
        "xss": "<script>alert('XSS')</script>",
        "path_traversal": "../../../etc/passwd",
        "command_injection": "; rm -rf /",
    }


def create_test_file(content: str, extension: str = ".txt") -> str:
    """Create a test file with given content."""
    with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as f:
        f.write(content.encode())
        return f.name


def cleanup_test_file(file_path: str):
    """Clean up a test file."""
    if os.path.exists(file_path):
        os.unlink(file_path)
