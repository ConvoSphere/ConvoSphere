# Code Style Guide

## Overview

This document outlines the coding standards and conventions used in the AI Assistant Platform project.

## Python Code Style

### General Principles

- **Readability**: Code should be self-documenting and easy to understand
- **Consistency**: Follow established patterns throughout the codebase
- **Simplicity**: Prefer simple, clear solutions over complex ones
- **Maintainability**: Write code that's easy to modify and extend

### PEP 8 Compliance

Follow PEP 8 standards with these specific guidelines:

#### Naming Conventions

```python
# Variables and functions: snake_case
user_name = "john"
def get_user_profile():
    pass

# Classes: PascalCase
class UserService:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRY_ATTEMPTS = 3
DEFAULT_TIMEOUT = 30

# Private methods: _leading_underscore
def _internal_helper():
    pass
```

#### Import Organization

```python
# Standard library imports
import os
import sys
from typing import Dict, List, Optional

# Third-party imports
from fastapi import FastAPI, Depends
from pydantic import BaseModel

# Local imports
from app.core.config import settings
from app.services.user_service import UserService
```

#### Line Length

- **Maximum**: 88 characters (Black formatter default)
- **Break long lines**: Use parentheses or backslashes appropriately

### Type Hints

Use type hints for all function parameters and return values:

```python
from typing import Dict, List, Optional, Union

def create_user(
    name: str,
    email: str,
    age: Optional[int] = None
) -> Dict[str, Union[str, int]]:
    """Create a new user."""
    pass

async def get_users(
    limit: int = 10,
    offset: int = 0
) -> List[Dict[str, str]]:
    """Get list of users."""
    pass
```

### Docstrings

Use Google-style docstrings for all public functions and classes:

```python
def process_user_data(user_data: Dict[str, Any]) -> bool:
    """Process user data and validate it.
    
    Args:
        user_data: Dictionary containing user information
        
    Returns:
        True if processing was successful, False otherwise
        
    Raises:
        ValueError: If user_data is invalid
        KeyError: If required fields are missing
    """
    pass
```

### Error Handling

Use specific exception types and provide meaningful error messages:

```python
def validate_email(email: str) -> bool:
    """Validate email format."""
    if not email or '@' not in email:
        raise ValueError("Invalid email format")
    
    if len(email) > 254:
        raise ValueError("Email too long")
    
    return True
```

## Frontend Code Style (NiceGUI)

### Component Organization

```python
# Use classes for complex components
class UserProfile:
    def __init__(self):
        self.name_input = None
        self.email_input = None
    
    def create(self):
        """Create the user profile component."""
        with ui.card():
            self.name_input = ui.input("Name")
            self.email_input = ui.input("Email")
```

### Event Handling

```python
# Use lambda for simple handlers
ui.button("Save", on_click=lambda: self.save_data())

# Use methods for complex handlers
ui.button("Process", on_click=self.process_data)

def process_data(self):
    """Handle data processing."""
    # Complex logic here
    pass
```

### State Management

```python
# Use class attributes for component state
class ChatInterface:
    def __init__(self):
        self.messages = []
        self.current_user = None
    
    def add_message(self, message: str):
        """Add message to chat."""
        self.messages.append(message)
        self.update_display()
```

## Database Models

### SQLAlchemy Models

```python
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.models.base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"
```

### Pydantic Schemas

```python
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True
```

## API Endpoints

### FastAPI Endpoints

```python
from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_user

router = APIRouter()

@router.get("/users/me")
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """Get current user profile."""
    return UserResponse.from_orm(current_user)

@router.post("/users")
async def create_user(
    user_data: UserCreate
) -> UserResponse:
    """Create a new user."""
    # Implementation here
    pass
```

## Configuration

### Environment Variables

```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "AI Assistant Platform"
    debug: bool = False
    database_url: str
    redis_url: str
    
    class Config:
        env_file = ".env"
```

## Testing

### Test Structure

```python
import pytest
from unittest.mock import Mock, patch

class TestUserService:
    """Test cases for UserService."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.user_service = UserService()
    
    def test_create_user_success(self):
        """Test successful user creation."""
        # Arrange
        user_data = {"name": "John", "email": "john@example.com"}
        
        # Act
        result = self.user_service.create_user(user_data)
        
        # Assert
        assert result.name == "John"
        assert result.email == "john@example.com"
    
    @patch('app.services.user_service.database')
    def test_create_user_database_error(self, mock_db):
        """Test user creation with database error."""
        # Arrange
        mock_db.save.side_effect = Exception("Database error")
        
        # Act & Assert
        with pytest.raises(Exception):
            self.user_service.create_user({})
```

## Security

### Input Validation

```python
from pydantic import validator

class UserCreate(BaseModel):
    email: str
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v
```

### Authentication

```python
from fastapi import Depends, HTTPException
from app.core.security import verify_token

async def get_current_user(
    token: str = Depends(verify_token)
) -> User:
    """Get current authenticated user."""
    if not token:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user
```

## Performance

### Database Queries

```python
# Use async/await for database operations
async def get_users_with_pagination(
    offset: int = 0,
    limit: int = 10
) -> List[User]:
    """Get users with pagination."""
    async with get_db() as db:
        users = await db.execute(
            select(User)
            .offset(offset)
            .limit(limit)
        )
        return users.scalars().all()
```

### Caching

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_configuration() -> Dict[str, Any]:
    """Get application configuration."""
    return load_config()
```

## Documentation

### Inline Comments

```python
# Use comments sparingly, prefer self-documenting code
def calculate_tax(income: float, rate: float) -> float:
    """Calculate tax based on income and rate."""
    # Apply progressive tax brackets
    if income <= 50000:
        return income * 0.15
    elif income <= 100000:
        return 7500 + (income - 50000) * 0.25
    else:
        return 20000 + (income - 100000) * 0.35
```

### README Files

Each module should have a README.md file explaining:

- Purpose and functionality
- Usage examples
- Dependencies
- Configuration options

## Tools and Automation

### Code Formatting

```bash
# Format code with Black
black .

# Sort imports with isort
isort .

# Check code style with flake8
flake8 .
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
```

## Best Practices

1. **DRY Principle**: Don't Repeat Yourself
2. **Single Responsibility**: Each function/class should have one purpose
3. **Fail Fast**: Validate inputs early and fail with clear error messages
4. **Logging**: Use appropriate log levels and include context
5. **Error Handling**: Handle errors gracefully and provide useful feedback
6. **Testing**: Write tests for all new functionality
7. **Documentation**: Keep documentation up to date with code changes 