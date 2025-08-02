"""
Shared test fixtures and configuration.

This module provides fixtures that can be used across all test modules.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator, Dict, Any

from backend.main import app
from backend.app.database import get_db
from backend.app.models.user import User, UserRole
from backend.app.models.conversation import Conversation
from backend.app.models.assistant import Assistant


# =============================================================================
# DATABASE FIXTURES
# =============================================================================

@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine."""
    # Use in-memory SQLite for testing
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )
    return engine


@pytest.fixture(scope="session")
def test_session_factory(test_engine):
    """Create test session factory."""
    return sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture
def db_session(test_session_factory) -> Generator[Session, None, None]:
    """Create a test database session."""
    session = test_session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def override_get_db(db_session):
    """Override the database dependency."""
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()


# =============================================================================
# CLIENT FIXTURES
# =============================================================================

@pytest.fixture
def client() -> TestClient:
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def async_client():
    """Create an async test client."""
    from httpx import AsyncClient
    return AsyncClient(app=app, base_url="http://test")


# =============================================================================
# USER FIXTURES
# =============================================================================

@pytest.fixture
def test_user_data() -> Dict[str, Any]:
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User",
        "display_name": "Test User",
        "bio": "Test bio",
        "phone": "+1234567890",
        "organization_id": "550e8400-e29b-41d4-a716-446655440000",
        "role": UserRole.USER,
        "is_active": True,
        "is_verified": False,
    }


@pytest.fixture
def test_user(test_user_data) -> User:
    """Create a test user."""
    user = User(
        id="user-123",
        email=test_user_data["email"],
        username=test_user_data["username"],
        hashed_password="hashed_password_123",
        first_name=test_user_data["first_name"],
        last_name=test_user_data["last_name"],
        display_name=test_user_data["display_name"],
        bio=test_user_data["bio"],
        phone=test_user_data["phone"],
        organization_id=test_user_data["organization_id"],
        role=test_user_data["role"],
        is_active=test_user_data["is_active"],
        is_verified=test_user_data["is_verified"],
    )
    return user


@pytest.fixture
def test_admin_user() -> User:
    """Create a test admin user."""
    admin = User(
        id="admin-123",
        email="admin@example.com",
        username="admin",
        hashed_password="hashed_password_123",
        first_name="Admin",
        last_name="User",
        display_name="Admin User",
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True,
        organization_id="550e8400-e29b-41d4-a716-446655440000",
    )
    return admin


@pytest.fixture
def test_user_headers(test_user) -> Dict[str, str]:
    """Create test user headers with authentication."""
    return {
        "Authorization": f"Bearer test_token_{test_user.id}",
        "Content-Type": "application/json"
    }


@pytest.fixture
def test_admin_headers(test_admin_user) -> Dict[str, str]:
    """Create test admin headers with authentication."""
    return {
        "Authorization": f"Bearer test_token_{test_admin_user.id}",
        "Content-Type": "application/json"
    }


# =============================================================================
# ASSISTANT FIXTURES
# =============================================================================

@pytest.fixture
def test_assistant() -> Assistant:
    """Create a test assistant."""
    assistant = Assistant(
        id="assistant-123",
        name="Test Assistant",
        description="A test assistant",
        model="gpt-4",
        instructions="You are a helpful assistant.",
        user_id="user-123",
        organization_id="550e8400-e29b-41d4-a716-446655440000",
        is_active=True,
    )
    return assistant


@pytest.fixture
def test_assistant_data() -> Dict[str, Any]:
    """Sample assistant data for testing."""
    return {
        "name": "Test Assistant",
        "description": "A test assistant",
        "model": "gpt-4",
        "instructions": "You are a helpful assistant.",
        "is_active": True,
    }


# =============================================================================
# CONVERSATION FIXTURES
# =============================================================================

@pytest.fixture
def test_conversation(test_user, test_assistant) -> Conversation:
    """Create a test conversation."""
    conversation = Conversation(
        id="conv-123",
        title="Test Conversation",
        user_id=test_user.id,
        assistant_id=test_assistant.id,
        organization_id="550e8400-e29b-41d4-a716-446655440000",
        is_active=True,
    )
    return conversation


@pytest.fixture
def test_conversation_data() -> Dict[str, Any]:
    """Sample conversation data for testing."""
    return {
        "title": "Test Conversation",
        "assistant_id": "assistant-123",
        "description": "A test conversation",
    }


# =============================================================================
# MOCK FIXTURES
# =============================================================================

@pytest.fixture
def mock_user_service():
    """Create a mock user service."""
    with patch('backend.app.services.user_service.UserService') as mock:
        service = mock.return_value
        service.get_user_by_id = Mock()
        service.get_user_by_email = Mock()
        service.get_user_by_username = Mock()
        service.create_user = Mock()
        service.update_user = Mock()
        service.delete_user = Mock()
        service.list_users = Mock()
        service.authenticate_user = Mock()
        service.update_password = Mock()
        service.verify_email = Mock()
        service.create_sso_user = Mock()
        service.get_user_stats = Mock()
        yield service


@pytest.fixture
def mock_conversation_service():
    """Create a mock conversation service."""
    with patch('backend.app.services.conversation_service.ConversationService') as mock:
        service = mock.return_value
        service.get_conversation = Mock()
        service.get_conversations = Mock()
        service.create_conversation = Mock()
        service.update_conversation = Mock()
        service.delete_conversation = Mock()
        service.get_conversation_messages = Mock()
        service.get_conversation_mode_status = Mock()
        yield service


@pytest.fixture
def mock_assistant_service():
    """Create a mock assistant service."""
    with patch('backend.app.services.assistant_service.AssistantService') as mock:
        service = mock.return_value
        service.get_assistant = Mock()
        service.get_assistants = Mock()
        service.create_assistant = Mock()
        service.update_assistant = Mock()
        service.delete_assistant = Mock()
        yield service


@pytest.fixture
def mock_assistant_engine():
    """Create a mock assistant engine."""
    with patch('backend.app.services.assistant_engine.AssistantEngine') as mock:
        engine = mock.return_value
        engine.process_message = Mock()
        engine.get_processing_status = Mock()
        engine.get_stats = Mock()
        yield engine


@pytest.fixture
def mock_auth():
    """Create a mock authentication dependency."""
    with patch('backend.app.api.dependencies.auth.get_current_user') as mock:
        mock.return_value = Mock(spec=User)
        yield mock


@pytest.fixture
def mock_auth_admin():
    """Create a mock admin authentication dependency."""
    with patch('backend.app.api.dependencies.auth.get_current_user') as mock:
        admin_user = Mock(spec=User)
        admin_user.role = UserRole.ADMIN
        mock.return_value = admin_user
        yield mock


# =============================================================================
# ASYNC FIXTURES
# =============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# =============================================================================
# UTILITY FIXTURES
# =============================================================================

@pytest.fixture
def sample_file_content() -> bytes:
    """Sample file content for testing file uploads."""
    return b"This is a test file content for testing file uploads."


@pytest.fixture
def sample_json_data() -> Dict[str, Any]:
    """Sample JSON data for testing."""
    return {
        "string_field": "test string",
        "number_field": 42,
        "boolean_field": True,
        "array_field": [1, 2, 3],
        "object_field": {"key": "value"}
    }


@pytest.fixture
def sample_error_response() -> Dict[str, Any]:
    """Sample error response for testing."""
    return {
        "error": "Test error",
        "message": "This is a test error message",
        "code": "TEST_ERROR",
        "details": {"field": "additional error details"}
    }


# =============================================================================
# TEST DATA FIXTURES
# =============================================================================

@pytest.fixture
def test_messages_data() -> list:
    """Sample messages data for testing."""
    return [
        {
            "id": "msg-1",
            "content": "Hello, how can you help me?",
            "role": "user",
            "conversation_id": "conv-123",
            "created_at": "2024-01-01T00:00:00Z"
        },
        {
            "id": "msg-2",
            "content": "I'm here to help you with any questions!",
            "role": "assistant",
            "conversation_id": "conv-123",
            "created_at": "2024-01-01T00:01:00Z"
        }
    ]


@pytest.fixture
def test_tools_data() -> list:
    """Sample tools data for testing."""
    return [
        {
            "id": "tool-1",
            "name": "Search Tool",
            "description": "Search for information",
            "type": "function",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                }
            }
        },
        {
            "id": "tool-2",
            "name": "Calculator",
            "description": "Perform calculations",
            "type": "function",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string"}
                }
            }
        }
    ]


@pytest.fixture
def test_knowledge_documents_data() -> list:
    """Sample knowledge documents data for testing."""
    return [
        {
            "id": "doc-1",
            "filename": "test_document.pdf",
            "title": "Test Document",
            "content": "This is test document content",
            "file_size": 1024,
            "file_type": "application/pdf",
            "uploaded_at": "2024-01-01T00:00:00Z"
        },
        {
            "id": "doc-2",
            "filename": "test_document.txt",
            "title": "Text Document",
            "content": "This is a text document",
            "file_size": 512,
            "file_type": "text/plain",
            "uploaded_at": "2024-01-01T01:00:00Z"
        }
    ]


# =============================================================================
# CLEANUP FIXTURES
# =============================================================================

@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Clean up after each test."""
    yield
    # Clear any overrides
    app.dependency_overrides.clear()
    
    # Clear any patches
    import unittest.mock
    unittest.mock.patch.stopall()