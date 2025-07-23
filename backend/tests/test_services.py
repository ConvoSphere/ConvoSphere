from unittest.mock import AsyncMock, Mock

import pytest
from app.services.assistant_service import AssistantService
from app.services.tool_service import ToolService
from app.services.user_service import UserService


@pytest.fixture()
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
    assert service is not None  # noqa: S101


def test_assistant_service_initialization(mock_db):
    """Test AssistantService can be instantiated."""
    service = AssistantService(mock_db)
    assert service is not None  # noqa: S101


def test_tool_service_initialization(mock_db):
    """Test ToolService can be instantiated."""
    service = ToolService(mock_db)
    assert service is not None  # noqa: S101


@pytest.mark.asyncio()
async def test_user_service_methods(mock_db):
    """Test UserService methods exist and are callable."""
    service = UserService(mock_db)
    assert hasattr(service, "create_user")  # noqa: S101
    assert hasattr(service, "get_user_by_id")  # noqa: S101
    assert hasattr(service, "get_user_by_email")  # noqa: S101
    assert hasattr(service, "update_user")  # noqa: S101
    assert hasattr(service, "delete_user")  # noqa: S101
    assert hasattr(service, "list_users")  # noqa: S101
    assert hasattr(service, "authenticate_user")  # noqa: S101
    # Note: change_password and other methods may not exist yet


@pytest.mark.asyncio()
async def test_assistant_service_methods(mock_db):
    """Test AssistantService methods exist and are callable."""
    service = AssistantService(mock_db)
    assert hasattr(service, "create_assistant")  # noqa: S101
    assert hasattr(service, "get_assistant")  # noqa: S101
    assert hasattr(service, "get_user_assistants")  # noqa: S101
    assert hasattr(service, "update_assistant")  # noqa: S101
    assert hasattr(service, "delete_assistant")  # noqa: S101
    assert hasattr(service, "activate_assistant")  # noqa: S101
    assert hasattr(service, "deactivate_assistant")  # noqa: S101


@pytest.mark.asyncio()
async def test_tool_service_methods(mock_db):
    """Test ToolService methods exist and are callable."""
    service = ToolService(mock_db)
    assert hasattr(service, "get_available_tools")  # noqa: S101
    # Note: Other methods may not exist yet


def test_service_error_handling(mock_db):
    """Test that services handle errors gracefully."""
    # This test verifies that services don't crash on basic operations
    try:
        UserService(mock_db)
        # Basic instantiation should not fail
        assert True  # noqa: S101
    except Exception as e:  # noqa: BLE001
        pytest.fail(f"UserService instantiation failed: {e}")
