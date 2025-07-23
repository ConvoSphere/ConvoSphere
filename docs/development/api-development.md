# API Development Guide

This guide covers the development practices and patterns for the AI Chat Application API.

## Architecture Overview

The API follows a layered architecture pattern:

```
┌─────────────────┐
│   API Routes    │  ← FastAPI route handlers
├─────────────────┤
│   Services      │  ← Business logic layer
├─────────────────┤
│   Models        │  ← Data models and schemas
├─────────────────┤
│   Database      │  ← SQLAlchemy ORM
└─────────────────┘
```

## Project Structure

```
app/
├── api/              # API route handlers
│   ├── v1/          # API version 1
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── chat.py
│   │   └── ...
│   └── deps.py      # Dependencies
├── core/            # Core configuration
│   ├── config.py
│   ├── security.py
│   └── ...
├── models/          # Database models
├── schemas/         # Pydantic schemas
├── services/        # Business logic
└── main.py         # FastAPI application
```

## Creating New API Endpoints

### 1. Define the Schema

First, create a Pydantic schema for request/response models:

```python
# app/schemas/user.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

### 2. Create the Service

Implement business logic in a service class:

```python
# app/services/user_service.py
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()

    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user information"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None

        update_data = user_data.dict(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

        for field, value in update_data.items():
            setattr(user, field, value)

        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user_id: int) -> bool:
        """Delete a user"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False

        self.db.delete(user)
        self.db.commit()
        return True

    def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """List users with pagination"""
        return self.db.query(User).offset(skip).limit(limit).all()
```

### 3. Create the API Route

Implement the API endpoint:

```python
# app/api/v1/users.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services.user_service import UserService

router = APIRouter()

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(deps.get_db)
):
    """Create a new user"""
    user_service = UserService(db)
    
    # Check if user already exists
    existing_user = user_service.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user = user_service.create_user(user_data)
    return user

@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(deps.get_db)
):
    """Get user by ID"""
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Update user information"""
    # Only allow users to update their own profile or admins
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user_service = UserService(db)
    user = user_service.update_user(user_id, user_data)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Delete a user"""
    # Only allow users to delete their own account or admins
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user_service = UserService(db)
    success = user_service.delete_user(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

@router.get("/", response_model=List[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """List users (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user_service = UserService(db)
    users = user_service.list_users(skip=skip, limit=limit)
    return users
```

### 4. Register the Router

Add the router to the main API:

```python
# app/api/v1/__init__.py
from fastapi import APIRouter
from app.api.v1 import auth, users, chat, conversations

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
```

## Error Handling

### Custom Exceptions

```python
# app/core/exceptions.py
from fastapi import HTTPException, status

class UserNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

class InsufficientPermissionsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )

class ValidationException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )
```

### Global Exception Handler

```python
# app/core/exception_handlers.py
from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from app.core.exceptions import UserNotFoundException

async def integrity_error_handler(request: Request, exc: IntegrityError):
    """Handle database integrity errors"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Data integrity error occurred"}
    )

async def user_not_found_handler(request: Request, exc: UserNotFoundException):
    """Handle user not found errors"""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc.detail)}
    )
```

## Authentication & Authorization

### Dependencies

```python
# app/api/deps.py
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import ALGORITHM
from app.database import SessionLocal
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

def get_db() -> Generator:
    """Database dependency"""
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current admin user"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
```

## Validation

### Custom Validators

```python
# app/core/validators.py
from typing import Any
from pydantic import validator
import re

def validate_password_strength(password: str) -> str:
    """Validate password strength"""
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain at least one uppercase letter")
    
    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain at least one lowercase letter")
    
    if not re.search(r"\d", password):
        raise ValueError("Password must contain at least one digit")
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise ValueError("Password must contain at least one special character")
    
    return password

def validate_email_format(email: str) -> str:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValueError("Invalid email format")
    return email
```

### Using Validators in Schemas

```python
# app/schemas/user.py
from pydantic import BaseModel, validator
from app.core.validators import validate_password_strength, validate_email_format

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str

    @validator('email')
    def validate_email(cls, v):
        return validate_email_format(v)

    @validator('password')
    def validate_password(cls, v):
        return validate_password_strength(v)
```

## Pagination

### Pagination Utilities

```python
# app/core/pagination.py
from typing import TypeVar, Generic, List, Optional
from pydantic import BaseModel
from fastapi import Query

T = TypeVar('T')

class PageInfo(BaseModel):
    page: int
    size: int
    total: int
    pages: int

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    page_info: PageInfo

def get_pagination_params(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size")
) -> tuple[int, int]:
    """Get pagination parameters"""
    return page, size

def create_paginated_response(
    items: List[T],
    total: int,
    page: int,
    size: int
) -> PaginatedResponse[T]:
    """Create paginated response"""
    pages = (total + size - 1) // size
    
    page_info = PageInfo(
        page=page,
        size=size,
        total=total,
        pages=pages
    )
    
    return PaginatedResponse(items=items, page_info=page_info)
```

## Rate Limiting

### Rate Limiter Implementation

```python
# app/core/rate_limiter.py
import time
from typing import Dict, Tuple
from fastapi import HTTPException, status
from app.core.config import settings

class RateLimiter:
    def __init__(self):
        self.requests: Dict[str, list] = {}
    
    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """Check if request is allowed"""
        now = time.time()
        
        if key not in self.requests:
            self.requests[key] = []
        
        # Remove old requests outside the window
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if now - req_time < window_seconds
        ]
        
        # Check if we're under the limit
        if len(self.requests[key]) >= max_requests:
            return False
        
        # Add current request
        self.requests[key].append(now)
        return True

rate_limiter = RateLimiter()

def check_rate_limit(
    key: str,
    max_requests: int = 100,
    window_seconds: int = 3600
):
    """Rate limiting dependency"""
    if not rate_limiter.is_allowed(key, max_requests, window_seconds):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )
```

## Testing API Endpoints

### Test Examples

```python
# tests/test_api_users.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.models.user import User
from app.core.security import create_access_token

client = TestClient(app)

class TestUserAPI:
    def test_create_user(self, db_session: Session):
        """Test user creation endpoint"""
        user_data = {
            "email": "test@example.com",
            "password": "SecurePass123!",
            "full_name": "Test User"
        }
        
        response = client.post("/api/v1/users/", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["full_name"] == user_data["full_name"]
        assert "password" not in data

    def test_get_user_unauthorized(self, db_session: Session):
        """Test getting user without authentication"""
        response = client.get("/api/v1/users/1")
        assert response.status_code == 401

    def test_get_user_authorized(self, db_session: Session):
        """Test getting user with authentication"""
        # Create a user
        user = User(
            email="test@example.com",
            full_name="Test User",
            hashed_password="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        
        # Create access token
        token = create_access_token(data={"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get(f"/api/v1/users/{user.id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == user.email
```

## Best Practices

1. **Separation of Concerns**: Keep business logic in services, not in route handlers
2. **Input Validation**: Always validate input data using Pydantic schemas
3. **Error Handling**: Use consistent error responses and proper HTTP status codes
4. **Authentication**: Implement proper authentication and authorization
5. **Rate Limiting**: Protect your API from abuse
6. **Documentation**: Use docstrings and FastAPI's automatic documentation
7. **Testing**: Write comprehensive tests for all endpoints
8. **Logging**: Log important events and errors
9. **Security**: Follow security best practices (HTTPS, input sanitization, etc.)
10. **Performance**: Use async operations where appropriate and implement caching

## API Versioning

### Version Strategy

```python
# app/api/v1/__init__.py
from fastapi import APIRouter

v1_router = APIRouter()

# Include all v1 routes
v1_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
v1_router.include_router(users.router, prefix="/users", tags=["users"])

# app/main.py
from app.api.v1 import v1_router

app.include_router(v1_router, prefix="/api/v1")
```

This structure allows for easy versioning when breaking changes are needed.