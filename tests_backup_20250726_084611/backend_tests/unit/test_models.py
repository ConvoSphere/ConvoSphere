from app.models.assistant import Assistant, AssistantStatus
from app.models.tool import Tool, ToolCategory
from app.models.user import User, UserRole, UserStatus


def test_user_model():
    """Test User model instantiation and attributes."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password_123",  # nosec # noqa: S106
        first_name="Test",
        last_name="User",
        role=UserRole.USER,
        status=UserStatus.ACTIVE,
    )

    assert user.email == "test@example.com"  # noqa: S101
    assert user.username == "testuser"  # noqa: S101
    assert user.first_name == "Test"  # noqa: S101
    assert user.last_name == "User"  # noqa: S101
    assert user.role == UserRole.USER  # noqa: S101
    assert user.status == UserStatus.ACTIVE  # noqa: S101
    assert user.is_active is True  # noqa: S101


def test_assistant_model():
    """Test Assistant model instantiation and attributes."""
    assistant = Assistant(
        name="Test Assistant",
        description="A test assistant",
        system_prompt="You are a helpful assistant.",
        creator_id="test_creator_id",
        model="gpt-4",
        temperature="0.7",
        status=AssistantStatus.DRAFT,
    )

    assert assistant.name == "Test Assistant"  # noqa: S101
    assert assistant.description == "A test assistant"  # noqa: S101
    assert assistant.system_prompt == "You are a helpful assistant."  # noqa: S101
    assert assistant.model == "gpt-4"  # noqa: S101
    assert assistant.temperature == "0.7"  # noqa: S101
    assert assistant.status == AssistantStatus.DRAFT  # noqa: S101


def test_tool_model():
    """Test Tool model instantiation and attributes."""
    tool = Tool(
        name="Test Tool",
        description="A test tool",
        category=ToolCategory.SEARCH,
        function_name="test_function",
        is_builtin=True,
        is_enabled=True,
    )

    assert tool.name == "Test Tool"  # noqa: S101
    assert tool.description == "A test tool"  # noqa: S101
    assert tool.category == ToolCategory.SEARCH  # noqa: S101
    assert tool.function_name == "test_function"  # noqa: S101
    assert tool.is_builtin is True  # noqa: S101
    assert tool.is_enabled is True  # noqa: S101


def test_user_role_enum():
    """Test UserRole enum values."""
    assert UserRole.ADMIN == "admin"  # noqa: S101
    assert UserRole.MANAGER == "manager"  # noqa: S101
    assert UserRole.USER == "user"  # noqa: S101
    assert UserRole.GUEST == "guest"  # noqa: S101


def test_assistant_status_enum():
    """Test AssistantStatus enum values."""
    assert AssistantStatus.ACTIVE == "active"  # noqa: S101
    assert AssistantStatus.INACTIVE == "inactive"  # noqa: S101
    assert AssistantStatus.DRAFT == "draft"  # noqa: S101
    assert AssistantStatus.MAINTENANCE == "maintenance"  # noqa: S101
