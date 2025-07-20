# Code Style Guide

This comprehensive code style guide ensures consistency and maintainability across the AI Assistant Platform codebase. All contributors should follow these guidelines to maintain high code quality.

## 📋 Table of Contents

- [Python Style Guidelines](#python-style-guidelines)
- [Naming Conventions](#naming-conventions)
- [Code Organization](#code-organization)
- [Documentation Standards](#documentation-standards)
- [Error Handling](#error-handling)
- [Testing Standards](#testing-standards)
- [Performance Guidelines](#performance-guidelines)
- [Security Guidelines](#security-guidelines)
- [Tools and Automation](#tools-and-automation)

## 🐍 Python Style Guidelines

### PEP 8 Compliance

We strictly follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some project-specific modifications.

#### Line Length
```python
# Maximum line length: 88 characters (Black default)
# Use parentheses for line continuation
long_function_name = (
    parameter_one,
    parameter_two,
    parameter_three
)

# For long strings, use parentheses
long_string = (
    "This is a very long string that needs to be "
    "broken across multiple lines for readability"
)
```

#### Indentation
```python
# Use 4 spaces for indentation (no tabs)
def function_name():
    if condition:
        do_something()
        if nested_condition:
            do_nested_thing()
```

#### Imports
```python
# Standard library imports first
import os
import sys
from typing import Dict, List, Optional

# Third-party imports
import fastapi
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Local application imports
from app.core.config import settings
from app.models.user import User
from app.services.user_service import UserService
```

#### Import Organization (isort)
```python
# isort configuration (.isort.cfg)
[settings]
profile = black
multi_line_output = 3
include_trailing_comma = True
force_grid_wrap = 0
use_parentheses = True
ensure_newline_before_comments = True
line_length = 88
```

### Type Hints

Use type hints for all function parameters, return values, and variables.

#### Basic Type Hints
```python
from typing import List, Dict, Optional, Union, Any

def get_user(user_id: str) -> Optional[User]:
    """Get user by ID."""
    pass

def create_users(users: List[UserCreate]) -> List[User]:
    """Create multiple users."""
    pass

def update_user_data(user_id: str, data: Dict[str, Any]) -> User:
    """Update user data."""
    pass
```

#### Complex Type Hints
```python
from typing import TypeVar, Generic, Callable
from pydantic import BaseModel

T = TypeVar('T')

class ServiceResponse(Generic[T]):
    """Generic service response wrapper."""
    data: T
    success: bool
    message: str

def process_with_callback(
    data: List[str],
    callback: Callable[[str], bool]
) -> List[str]:
    """Process data with a callback function."""
    return [item for item in data if callback(item)]
```

#### Type Aliases
```python
from typing import TypeAlias

# Define type aliases for complex types
UserDict: TypeAlias = Dict[str, Union[str, int, bool]]
ApiResponse: TypeAlias = Dict[str, Any]
```

## 🏷️ Naming Conventions

### Variables and Functions
```python
# Use snake_case for variables and functions
user_name = "john_doe"
first_name = "John"
last_name = "Doe"

def get_user_by_id(user_id: str) -> Optional[User]:
    pass

def create_new_user(user_data: UserCreate) -> User:
    pass

def is_user_active(user: User) -> bool:
    pass
```

### Classes
```python
# Use PascalCase for classes
class UserService:
    pass

class DatabaseConnection:
    pass

class ApiResponseHandler:
    pass
```

### Constants
```python
# Use UPPER_SNAKE_CASE for constants
MAX_RETRY_ATTEMPTS = 3
DEFAULT_TIMEOUT = 30
API_VERSION = "v1"
DATABASE_URL = "postgresql://localhost/chatassistant"
```

### Private Methods and Variables
```python
class UserService:
    def __init__(self):
        self._cache = {}  # Private variable
    
    def _validate_email(self, email: str) -> bool:
        """Private method for email validation."""
        pass
    
    def _get_cached_user(self, user_id: str) -> Optional[User]:
        """Private method for cache retrieval."""
        pass
```

### Database Models
```python
# Use singular form for model names
class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### API Endpoints
```python
# Use plural nouns for resource endpoints
@router.get("/users")  # ✅ Good
@router.get("/user")   # ❌ Avoid

@router.post("/users")  # ✅ Good
@router.post("/user")   # ❌ Avoid

# Use specific actions for non-CRUD operations
@router.post("/users/{user_id}/activate")
@router.post("/users/{user_id}/deactivate")
@router.post("/users/{user_id}/reset-password")
```

## 📁 Code Organization

### File Structure
```
app/
├── __init__.py
├── api/
│   ├── __init__.py
│   ├── deps.py              # Dependencies
│   ├── errors.py            # Error handlers
│   └── endpoints/
│       ├── __init__.py
│       ├── auth.py
│       ├── users.py
│       └── assistants.py
├── core/
│   ├── __init__.py
│   ├── config.py            # Configuration
│   ├── database.py          # Database setup
│   └── security.py          # Security utilities
├── models/
│   ├── __init__.py
│   ├── user.py
│   └── assistant.py
├── schemas/
│   ├── __init__.py
│   ├── user.py
│   └── assistant.py
├── services/
│   ├── __init__.py
│   ├── user_service.py
│   └── assistant_service.py
└── utils/
    ├── __init__.py
    ├── validators.py
    └── helpers.py
```

### Module Organization
```python
# Standard module structure
"""
User management module.

This module provides user-related functionality including creation,
authentication, and profile management.
"""

# Standard library imports
import logging
from typing import Optional, List
from datetime import datetime

# Third-party imports
from fastapi import HTTPException
from sqlalchemy.orm import Session

# Local imports
from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

# Module-level constants
logger = logging.getLogger(__name__)
MAX_USERS_PER_PAGE = 100

# Classes and functions
class UserService:
    """Service class for user operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        pass

# Module-level functions
def validate_email(email: str) -> bool:
    """Validate email format."""
    pass
```

### Function Organization
```python
class UserService:
    """Service class for user management operations."""
    
    def __init__(self, db: Session):
        """Initialize the service with database session."""
        self.db = db
    
    # Public methods first
    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user in the system."""
        self._validate_user_data(user_data)
        user = self._create_user_record(user_data)
        self._send_welcome_email(user)
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()
    
    # Private methods last
    def _validate_user_data(self, user_data: UserCreate) -> None:
        """Validate user creation data."""
        pass
    
    def _create_user_record(self, user_data: UserCreate) -> User:
        """Create user record in database."""
        pass
    
    def _send_welcome_email(self, user: User) -> None:
        """Send welcome email to new user."""
        pass
```

## 📚 Documentation Standards

### Docstring Format

We use Google-style docstrings for all public functions, classes, and modules.

#### Function Docstrings
```python
def create_user(
    user_data: UserCreate,
    send_welcome_email: bool = True
) -> User:
    """Create a new user in the system.
    
    This function creates a new user account with the provided data.
    It validates the input, creates the user record, and optionally
    sends a welcome email.
    
    Args:
        user_data: User creation data containing email, password, etc.
        send_welcome_email: Whether to send welcome email (default: True)
        
    Returns:
        User: The created user object with all fields populated
        
    Raises:
        ValueError: If user data is invalid or email already exists
        HTTPException: If database operation fails
        
    Example:
        >>> user_data = UserCreate(
        ...     email="user@example.com",
        ...     password="securepassword123"
        ... )
        >>> user = create_user(user_data)
        >>> print(user.email)
        user@example.com
    """
    pass
```

#### Class Docstrings
```python
class UserService:
    """Service class for user management operations.
    
    This class provides a high-level interface for user-related
    operations including creation, authentication, and profile
    management. It handles business logic and coordinates between
    different components of the system.
    
    Attributes:
        db: Database session for data operations
        cache: Redis cache for performance optimization
        
    Example:
        >>> service = UserService(db_session)
        >>> user = service.create_user(user_data)
        >>> users = service.get_users(page=1, size=10)
    """
    
    def __init__(self, db: Session, cache: Redis = None):
        """Initialize the UserService.
        
        Args:
            db: Database session for data operations
            cache: Optional Redis cache for performance
        """
        self.db = db
        self.cache = cache
```

#### Module Docstrings
```python
"""
User management module for the AI Assistant Platform.

This module provides comprehensive user management functionality
including user creation, authentication, profile management, and
role-based access control. It consists of models, services, and
API endpoints for user operations.

Classes:
    UserService: Main service class for user operations
    UserValidator: Utility class for user data validation
    
Functions:
    create_user: High-level function for user creation
    authenticate_user: User authentication function
    
Example:
    >>> from app.services.user_service import UserService
    >>> service = UserService(db_session)
    >>> user = service.create_user(user_data)
"""

# Module content...
```

### Inline Comments
```python
# Use inline comments sparingly and only when necessary
def calculate_user_score(user: User) -> float:
    """Calculate user activity score."""
    # Base score starts at 100
    score = 100.0
    
    # Deduct points for inactivity (more than 30 days)
    if user.last_active < datetime.now() - timedelta(days=30):
        score -= 20
    
    # Bonus points for verified email
    if user.email_verified:
        score += 10
    
    # Ensure score doesn't go below 0
    return max(0.0, score)
```

### API Documentation
```python
@router.post(
    "/users",
    response_model=UserResponse,
    status_code=201,
    summary="Create a new user",
    description="Create a new user account with the provided information.",
    responses={
        201: {
            "description": "User created successfully",
            "model": UserResponse
        },
        400: {
            "description": "Invalid input data",
            "model": ErrorResponse
        },
        409: {
            "description": "User already exists",
            "model": ErrorResponse
        }
    }
)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> UserResponse:
    """Create a new user account.
    
    This endpoint creates a new user account with the provided
    information. The user will receive a welcome email upon
    successful creation.
    
    Args:
        user_data: User creation data
        db: Database session dependency
        
    Returns:
        UserResponse: Created user information
        
    Raises:
        HTTPException: If user data is invalid or user already exists
    """
    pass
```

## ❌ Error Handling

### Exception Hierarchy
```python
# Custom exceptions
class ChatAssistantException(Exception):
    """Base exception for the application."""
    pass

class ValidationError(ChatAssistantException):
    """Raised when data validation fails."""
    pass

class AuthenticationError(ChatAssistantException):
    """Raised when authentication fails."""
    pass

class AuthorizationError(ChatAssistantException):
    """Raised when authorization fails."""
    pass

class DatabaseError(ChatAssistantException):
    """Raised when database operations fail."""
    pass
```

### Error Handling Patterns
```python
from fastapi import HTTPException
from app.core.exceptions import ValidationError, DatabaseError

def process_user_data(user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Process user data with comprehensive error handling."""
    try:
        # Validate input data
        if not user_id:
            raise ValidationError("User ID is required")
        
        # Process the data
        result = _process_data(user_id, data)
        
        return {
            "success": True,
            "data": result,
            "message": "Data processed successfully"
        }
        
    except ValidationError as e:
        logger.warning(f"Validation error for user {user_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
        
    except DatabaseError as e:
        logger.error(f"Database error for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Database operation failed")
        
    except Exception as e:
        logger.error(f"Unexpected error for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

### Logging
```python
import logging
from typing import Any

logger = logging.getLogger(__name__)

def log_function_call(func_name: str, **kwargs: Any) -> None:
    """Log function calls with parameters."""
    logger.info(f"Calling {func_name} with parameters: {kwargs}")

def log_error(error: Exception, context: str = "") -> None:
    """Log errors with context."""
    logger.error(f"Error in {context}: {str(error)}", exc_info=True)

# Usage in functions
def create_user(user_data: UserCreate) -> User:
    """Create a new user."""
    log_function_call("create_user", email=user_data.email)
    
    try:
        user = _create_user_record(user_data)
        logger.info(f"User created successfully: {user.id}")
        return user
    except Exception as e:
        log_error(e, "create_user")
        raise
```

## 🧪 Testing Standards

### Test Structure
```python
import pytest
from unittest.mock import Mock, patch
from app.services.user_service import UserService
from app.models.user import User

class TestUserService:
    """Test suite for UserService class."""
    
    @pytest.fixture
    def user_service(self, db_session):
        """Create UserService instance for testing."""
        return UserService(db_session)
    
    @pytest.fixture
    def sample_user_data(self):
        """Sample user data for testing."""
        return {
            "email": "test@example.com",
            "password": "securepassword123",
            "first_name": "Test",
            "last_name": "User"
        }
    
    def test_create_user_success(self, user_service, sample_user_data):
        """Test successful user creation."""
        # Arrange
        user_data = UserCreate(**sample_user_data)
        
        # Act
        user = user_service.create_user(user_data)
        
        # Assert
        assert user.email == sample_user_data["email"]
        assert user.first_name == sample_user_data["first_name"]
        assert user.last_name == sample_user_data["last_name"]
        assert user.is_active is True
    
    def test_create_user_duplicate_email(self, user_service, sample_user_data):
        """Test user creation with duplicate email."""
        # Arrange
        user_data = UserCreate(**sample_user_data)
        user_service.create_user(user_data)  # Create first user
        
        # Act & Assert
        with pytest.raises(ValueError, match="Email already exists"):
            user_service.create_user(user_data)
    
    @patch('app.services.user_service.send_email')
    def test_create_user_sends_welcome_email(
        self, 
        mock_send_email, 
        user_service, 
        sample_user_data
    ):
        """Test that welcome email is sent on user creation."""
        # Arrange
        user_data = UserCreate(**sample_user_data)
        
        # Act
        user = user_service.create_user(user_data)
        
        # Assert
        mock_send_email.assert_called_once_with(
            to_email=user.email,
            template="welcome",
            context={"user": user}
        )
```

### Test Naming
```python
# Use descriptive test names that explain the scenario
def test_create_user_with_valid_data_returns_user_object():
    pass

def test_create_user_with_invalid_email_raises_validation_error():
    pass

def test_create_user_with_existing_email_raises_conflict_error():
    pass

def test_get_user_by_id_returns_user_when_exists():
    pass

def test_get_user_by_id_returns_none_when_not_exists():
    pass
```

### Test Coverage
```python
# Aim for at least 90% test coverage
# Test both success and failure scenarios
# Test edge cases and boundary conditions

def test_user_age_calculation():
    """Test user age calculation with various birth dates."""
    # Test normal case
    user = User(birth_date=date(1990, 1, 1))
    assert user.age == 33  # Assuming current year is 2023
    
    # Test edge case - birthday today
    user = User(birth_date=date(1990, 12, 25))
    # Test logic for birthday today
    
    # Test edge case - future birth date
    user = User(birth_date=date(2030, 1, 1))
    assert user.age == 0
```

## ⚡ Performance Guidelines

### Database Optimization
```python
# Use appropriate indexes
class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)  # Index for lookups
    created_at = Column(DateTime, default=datetime.utcnow, index=True)  # Index for sorting

# Use select_from for complex queries
def get_active_users_with_assistants():
    """Get active users with their assistants using optimized query."""
    return (
        db.query(User)
        .select_from(User)
        .join(Assistant, User.id == Assistant.user_id)
        .filter(User.is_active == True)
        .options(joinedload(User.assistants))  # Eager loading
        .all()
    )

# Use pagination for large datasets
def get_users_paginated(page: int = 1, size: int = 20):
    """Get users with pagination."""
    offset = (page - 1) * size
    return (
        db.query(User)
        .offset(offset)
        .limit(size)
        .all()
    )
```

### Caching
```python
from functools import lru_cache
from app.core.cache import redis_cache

# Use LRU cache for expensive computations
@lru_cache(maxsize=128)
def calculate_user_score(user_id: str) -> float:
    """Calculate user score with caching."""
    # Expensive computation here
    pass

# Use Redis cache for distributed caching
def get_user_profile(user_id: str) -> Dict[str, Any]:
    """Get user profile with Redis caching."""
    cache_key = f"user_profile:{user_id}"
    
    # Try to get from cache first
    cached_data = redis_cache.get(cache_key)
    if cached_data:
        return cached_data
    
    # If not in cache, get from database
    user = get_user_from_db(user_id)
    profile_data = user.to_dict()
    
    # Store in cache for 1 hour
    redis_cache.setex(cache_key, 3600, profile_data)
    
    return profile_data
```

### Async/Await
```python
import asyncio
from typing import List

# Use async/await for I/O operations
async def get_multiple_users(user_ids: List[str]) -> List[User]:
    """Get multiple users concurrently."""
    tasks = [get_user_async(user_id) for user_id in user_ids]
    return await asyncio.gather(*tasks)

async def get_user_async(user_id: str) -> User:
    """Get user asynchronously."""
    # Simulate async database call
    await asyncio.sleep(0.1)
    return User(id=user_id, email=f"user{user_id}@example.com")

# Use async context managers
async def process_user_data(user_id: str):
    """Process user data with async context manager."""
    async with get_db_session() as db:
        user = await db.get(User, user_id)
        # Process user data
        await db.commit()
```

## 🔒 Security Guidelines

### Input Validation
```python
from pydantic import BaseModel, validator, EmailStr
import re

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain uppercase letter')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain lowercase letter')
        
        if not re.search(r'\d', v):
            raise ValueError('Password must contain digit')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain special character')
        
        return v
    
    @validator('first_name', 'last_name')
    def validate_name(cls, v):
        """Validate name fields."""
        if not v.strip():
            raise ValueError('Name cannot be empty')
        
        if len(v) > 50:
            raise ValueError('Name too long')
        
        if not re.match(r'^[a-zA-Z\s\-\.]+$', v):
            raise ValueError('Name contains invalid characters')
        
        return v.strip()
```

### SQL Injection Prevention
```python
# Use parameterized queries
def get_user_by_email(email: str) -> Optional[User]:
    """Get user by email using parameterized query."""
    return (
        db.query(User)
        .filter(User.email == email)  # Safe parameterized query
        .first()
    )

# Avoid string formatting for queries
def bad_get_user_by_email(email: str) -> Optional[User]:
    """BAD: Vulnerable to SQL injection."""
    query = f"SELECT * FROM users WHERE email = '{email}'"  # ❌ Dangerous
    return db.execute(query).first()

# Use ORM methods instead of raw SQL
def get_users_by_role(role: str) -> List[User]:
    """Get users by role using ORM."""
    return (
        db.query(User)
        .filter(User.role == role)
        .all()
    )
```

### Authentication and Authorization
```python
from fastapi import Depends, HTTPException, status
from app.core.auth import get_current_user, require_role

# Use dependency injection for authentication
@router.get("/users/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """Get current user information."""
    return UserResponse.from_orm(current_user)

# Use role-based access control
@router.get("/users")
@require_role("admin")
async def get_all_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[UserResponse]:
    """Get all users (admin only)."""
    users = db.query(User).all()
    return [UserResponse.from_orm(user) for user in users]

# Validate user ownership
@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> UserResponse:
    """Update user (owner or admin only)."""
    # Check if user is owner or admin
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user data
    for field, value in user_data.dict(exclude_unset=True).items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    return UserResponse.from_orm(user)
```

## 🛠️ Tools and Automation

### Pre-commit Configuration
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3
        args: [--line-length=88]

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: [--profile=black, --line-length=88]

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203,W503]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        args: [--ignore-missing-imports]

  - repo: https://github.com/pycqa/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: [-r, ., -f, json, -o, bandit-report.json]

  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
```

### Flake8 Configuration
```ini
# .flake8
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = 
    .git,
    __pycache__,
    .venv,
    venv,
    .env,
    migrations,
    alembic
per-file-ignores =
    __init__.py:F401
    tests/*:S101,S105,S106,S107
```

### MyPy Configuration
```ini
# mypy.ini
[mypy]
python_version = 3.13
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
disallow_untyped_decorators = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
warn_unreachable = True
strict_equality = True

[mypy.plugins.pydantic.*]
init_forbid_extra = True
init_typed = True
warn_required_dynamic_aliases = True
warn_untyped_fields = True
```

### IDE Configuration

#### VS Code Settings
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "python.testing.pytestArgs": [
        "tests"
    ]
}
```

#### PyCharm Configuration
```xml
<!-- .idea/codeStyles/Project.xml -->
<component name="ProjectCodeStyleConfiguration">
  <code_scheme name="Project" version="173">
    <PythonCodeStyleSettings>
      <option name="USE_SEMICOLON_AFTER_STATEMENTS" value="false" />
      <option name="USE_SPACE_AFTER_LAMBDA" value="true" />
      <option name="USE_SPACE_AROUND_OPERATORS" value="true" />
    </PythonCodeStyleSettings>
  </code_scheme>
</component>
```

---

<div align="center">

**Ready to write clean, maintainable code?** [Contributing Guide →](contributing.md)

</div> 