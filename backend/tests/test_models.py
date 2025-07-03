import pytest
from app.models.user import User, UserRole, UserStatus
from app.models.assistant import Assistant, AssistantStatus
from app.models.tool import Tool, ToolCategory

def test_user_model():
    """Test User model instantiation and attributes."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password_123",
        first_name="Test",
        last_name="User",
        role=UserRole.USER,
        status=UserStatus.ACTIVE
    )
    
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.first_name == "Test"
    assert user.last_name == "User"
    assert user.role == UserRole.USER
    assert user.status == UserStatus.ACTIVE
    assert user.is_active is True

def test_assistant_model():
    """Test Assistant model instantiation and attributes."""
    assistant = Assistant(
        name="Test Assistant",
        description="A test assistant",
        system_prompt="You are a helpful assistant.",
        creator_id="test_creator_id",
        model="gpt-4",
        temperature="0.7",
        status=AssistantStatus.DRAFT
    )
    
    assert assistant.name == "Test Assistant"
    assert assistant.description == "A test assistant"
    assert assistant.system_prompt == "You are a helpful assistant."
    assert assistant.model == "gpt-4"
    assert assistant.temperature == "0.7"
    assert assistant.status == AssistantStatus.DRAFT

def test_tool_model():
    """Test Tool model instantiation and attributes."""
    tool = Tool(
        name="Test Tool",
        description="A test tool",
        category=ToolCategory.SEARCH,
        function_name="test_function",
        is_builtin=True,
        is_enabled=True
    )
    
    assert tool.name == "Test Tool"
    assert tool.description == "A test tool"
    assert tool.category == ToolCategory.SEARCH
    assert tool.function_name == "test_function"
    assert tool.is_builtin is True
    assert tool.is_enabled is True

def test_user_role_enum():
    """Test UserRole enum values."""
    assert UserRole.ADMIN == "admin"
    assert UserRole.MANAGER == "manager"
    assert UserRole.USER == "user"
    assert UserRole.GUEST == "guest"

def test_assistant_status_enum():
    """Test AssistantStatus enum values."""
    assert AssistantStatus.ACTIVE == "active"
    assert AssistantStatus.INACTIVE == "inactive"
    assert AssistantStatus.DRAFT == "draft"
    assert AssistantStatus.MAINTENANCE == "maintenance" 