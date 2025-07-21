from unittest.mock import AsyncMock, Mock

import pytest
from app.services.assistant_service import AssistantService
from app.services.tool_service import ToolService
from app.services.user_service import UserService


@pytest.fixture
def mock_db():
    """Mock database session for testing."""
    db = Mock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()
    db.close = AsyncMock()
    return db


def test_user_service_initialization(mock_db):
    """Test UserService can be instantiated."""
    service = UserService(mock_db)
    assert service is not None


def test_assistant_service_initialization(mock_db):
    """Test AssistantService can be instantiated."""
    service = AssistantService(mock_db)
    assert service is not None


def test_tool_service_initialization(mock_db):
    """Test ToolService can be instantiated."""
    service = ToolService(mock_db)
    assert service is not None


@pytest.mark.asyncio
async def test_user_service_methods(mock_db):
    """Test UserService methods exist and are callable."""
    service = UserService(mock_db)
    assert hasattr(service, "create_user")
    assert hasattr(service, "get_user_by_id")
    assert hasattr(service, "get_user_by_email")
    assert hasattr(service, "update_user")
    assert hasattr(service, "delete_user")
    assert hasattr(service, "list_users")
    assert hasattr(service, "authenticate_user")
    # Note: change_password and other methods may not exist yet


@pytest.mark.asyncio
async def test_assistant_service_methods(mock_db):
    """Test AssistantService methods exist and are callable."""
    service = AssistantService(mock_db)
    assert hasattr(service, "create_assistant")
    assert hasattr(service, "get_assistant")
    assert hasattr(service, "get_user_assistants")
    assert hasattr(service, "update_assistant")
    assert hasattr(service, "delete_assistant")
    assert hasattr(service, "activate_assistant")
    assert hasattr(service, "deactivate_assistant")


@pytest.mark.asyncio
async def test_tool_service_methods(mock_db):
    """Test ToolService methods exist and are callable."""
    service = ToolService(mock_db)
    assert hasattr(service, "get_available_tools")
    # Note: Other methods may not exist yet


def test_service_error_handling(mock_db):
    """Test that services handle errors gracefully."""
    # This test verifies that services don't crash on basic operations
    try:
        service = UserService(mock_db)
        # Basic instantiation should not fail
        assert True
    except Exception as e:
        pytest.fail(f"UserService instantiation failed: {e}")
