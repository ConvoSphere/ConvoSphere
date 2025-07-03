# Backend Architecture

## Overview

The backend of the AI Assistant Platform is built with FastAPI, providing a modern, high-performance API with automatic OpenAPI documentation, async support, and comprehensive type checking.

## Technology Stack

### Core Framework
- **FastAPI**: Modern, fast web framework for building APIs
- **Pydantic**: Data validation and settings management
- **SQLAlchemy**: ORM for database operations
- **Alembic**: Database migration management
- **Redis**: Caching and session storage
- **Weaviate**: Vector database for embeddings

### AI Integration
- **LiteLLM**: Unified interface for multiple AI providers
- **OpenAI**: GPT models integration
- **Anthropic**: Claude models integration
- **Local Models**: Ollama, LM Studio support

### Security & Authentication
- **JWT**: JSON Web Tokens for authentication
- **Passlib**: Password hashing with bcrypt
- **CORS**: Cross-origin resource sharing
- **Rate Limiting**: Redis-based request limiting

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── api.py
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── auth.py
│   │           ├── users.py
│   │           ├── assistants.py
│   │           ├── conversations.py
│   │           ├── tools.py
│   │           ├── mcp.py
│   │           ├── knowledge.py
│   │           ├── search.py
│   │           ├── websocket.py
│   │           └── health.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── security.py
│   │   ├── redis_client.py
│   │   ├── weaviate_client.py
│   │   └── i18n.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── assistant.py
│   │   ├── conversation.py
│   │   ├── tool.py
│   │   ├── knowledge.py
│   │   └── audit.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── conversation.py
│   │   └── knowledge.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_service.py
│   │   ├── assistant_service.py
│   │   ├── conversation_service.py
│   │   ├── tool_service.py
│   │   ├── user_service.py
│   │   ├── knowledge_service.py
│   │   ├── embedding_service.py
│   │   ├── weaviate_service.py
│   │   └── document_processor.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── mcp_tool.py
│   │   ├── file_tools.py
│   │   ├── search_tools.py
│   │   ├── api_tools.py
│   │   └── analysis_tools.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── exceptions.py
│   │   ├── helpers.py
│   │   ├── security.py
│   │   └── validators.py
│   └── translations/
│       ├── en.json
│       └── de.json
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_users.py
│   ├── test_assistants.py
│   ├── test_conversations.py
│   ├── test_tools.py
│   └── test_integration.py
├── main.py
├── requirements.txt
└── pytest.ini
```

## Application Entry Point

### Main Application Setup

```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from app.core.database import engine
from app.core.redis_client import redis_client
from app.core.weaviate_client import weaviate_client

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    # Initialize Redis connection
    await redis_client.connect()
    
    # Initialize Weaviate connection
    await weaviate_client.connect()
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    await redis_client.disconnect()
    await weaviate_client.disconnect()
```

## Configuration Management

### Environment Configuration

```python
# app/core/config.py
from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # Application settings
    PROJECT_NAME: str = "AI Assistant Platform"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Modern AI Assistant Platform"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: str
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Weaviate
    WEAVIATE_URL: str = "http://localhost:8080"
    WEAVIATE_API_KEY: Optional[str] = None
    
    # AI Providers
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    DEFAULT_AI_MODEL: str = "gpt-4"
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # File upload
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        env_file = ".env"

settings = Settings()
```

## Database Architecture

### SQLAlchemy Models

```python
# app/models/base.py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, String
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class BaseModel(Base):
    """Base model with common fields."""
    __abstract__ = True
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# app/models/user.py
from sqlalchemy import Column, String, Boolean, Enum
from app.models.base import BaseModel
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"

class User(BaseModel):
    __tablename__ = "users"
    
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
```

### Database Connection

```python
# app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    """Dependency to get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

## API Architecture

### Router Structure

```python
# app/api/v1/api.py
from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, users, assistants, conversations, 
    tools, mcp, knowledge, search, websocket, health
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(assistants.router, prefix="/assistants", tags=["assistants"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
api_router.include_router(tools.router, prefix="/tools", tags=["tools"])
api_router.include_router(mcp.router, prefix="/mcp", tags=["mcp"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(websocket.router, prefix="/ws", tags=["websocket"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
```

### Endpoint Example

```python
# app/api/v1/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services.user_service import UserService

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of users."""
    user_service = UserService(db)
    users = await user_service.get_users(skip=skip, limit=limit)
    return users

@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new user."""
    user_service = UserService(db)
    user = await user_service.create_user(user_data)
    return user

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information."""
    return current_user
```

## Service Layer

### Service Architecture

```python
# app/services/base_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy import select
from app.models.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)

class BaseService(Generic[ModelType]):
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get(self, id: str) -> Optional[ModelType]:
        """Get model by ID."""
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_multi(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get multiple models."""
        result = await self.db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return result.scalars().all()
    
    async def create(self, obj_in) -> ModelType:
        """Create new model."""
        db_obj = self.model(**obj_in.dict())
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def update(self, db_obj: ModelType, obj_in) -> ModelType:
        """Update model."""
        for field, value in obj_in.dict(exclude_unset=True).items():
            setattr(db_obj, field, value)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def delete(self, id: str) -> bool:
        """Delete model."""
        obj = await self.get(id)
        if obj:
            await self.db.delete(obj)
            await self.db.commit()
            return True
        return False

# app/services/user_service.py
from app.services.base_service import BaseService
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password, verify_password

class UserService(BaseService[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.model = User
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create new user with hashed password."""
        hashed_password = hash_password(user_data.password)
        user_dict = user_data.dict()
        user_dict["hashed_password"] = hashed_password
        del user_dict["password"]
        
        return await self.create(user_dict)
    
    async def authenticate(self, email: str, password: str) -> Optional[User]:
        """Authenticate user."""
        user = await self.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
```

## Middleware and Dependencies

### Authentication Middleware

```python
# app/core/security.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from app.core.config import settings
from app.models.user import User
from app.services.user_service import UserService

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user_service = UserService(db)
    user = await user_service.get(user_id)
    if user is None:
        raise credentials_exception
    
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
```

### Rate Limiting Middleware

```python
# app/middleware/rate_limiting.py
from fastapi import Request, HTTPException
from app.core.redis_client import redis_client
import time

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
    
    async def check_rate_limit(self, request: Request):
        """Check if request is within rate limit."""
        client_ip = request.client.host
        key = f"rate_limit:{client_ip}"
        
        # Get current request count
        current_count = await redis_client.get(key)
        if current_count and int(current_count) >= self.requests_per_minute:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded"
            )
        
        # Increment counter
        pipe = redis_client.pipeline()
        pipe.incr(key)
        pipe.expire(key, 60)  # 1 minute window
        await pipe.execute()

async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware."""
    rate_limiter = RateLimiter()
    await rate_limiter.check_rate_limit(request)
    
    response = await call_next(request)
    return response
```

## Error Handling

### Custom Exceptions

```python
# app/utils/exceptions.py
from fastapi import HTTPException, status

class UserNotFoundException(HTTPException):
    def __init__(self, user_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )

class AssistantNotFoundException(HTTPException):
    def __init__(self, assistant_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assistant with ID {assistant_id} not found"
        )

class InsufficientPermissionsException(HTTPException):
    def __init__(self, required_permission: str):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions. Required: {required_permission}"
        )

class ValidationException(HTTPException):
    def __init__(self, field: str, message: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error for {field}: {message}"
        )
```

### Global Exception Handler

```python
# app/main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.utils.exceptions import (
    UserNotFoundException, AssistantNotFoundException,
    InsufficientPermissionsException, ValidationException
)

@app.exception_handler(UserNotFoundException)
async def user_not_found_handler(request: Request, exc: UserNotFoundException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(AssistantNotFoundException)
async def assistant_not_found_handler(request: Request, exc: AssistantNotFoundException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(InsufficientPermissionsException)
async def insufficient_permissions_handler(request: Request, exc: InsufficientPermissionsException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(ValidationException)
async def validation_exception_handler(request: Request, exc: ValidationException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
```

## Testing Architecture

### Test Configuration

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db
from app.models.base import Base

# Test database
TEST_DATABASE_URL = "postgresql+asyncpg://test_user:test_pass@localhost/test_db"

@pytest.fixture
async def test_db():
    """Create test database."""
    engine = create_async_engine(TEST_DATABASE_URL)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    TestingSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with TestingSessionLocal() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def client(test_db):
    """Create test client."""
    def override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

@pytest.fixture
def test_user():
    """Create test user."""
    return {
        "email": "test@example.com",
        "name": "Test User",
        "password": "testpassword123"
    }
```

### Test Examples

```python
# tests/test_auth.py
import pytest
from fastapi import status

def test_register_user(client, test_user):
    """Test user registration."""
    response = client.post("/api/v1/auth/register", json=test_user)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == test_user["email"]
    assert data["name"] == test_user["name"]
    assert "password" not in data

def test_login_user(client, test_user):
    """Test user login."""
    # First register user
    client.post("/api/v1/auth/register", json=test_user)
    
    # Then login
    login_data = {
        "email": test_user["email"],
        "password": test_user["password"]
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data

def test_protected_route(client, test_user):
    """Test protected route access."""
    # Register and login
    client.post("/api/v1/auth/register", json=test_user)
    login_response = client.post("/api/v1/auth/login", data={
        "email": test_user["email"],
        "password": test_user["password"]
    })
    token = login_response.json()["access_token"]
    
    # Access protected route
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == status.HTTP_200_OK
```

## Performance Optimization

### Caching Strategy

```python
# app/core/cache.py
from app.core.redis_client import redis_client
import json
from typing import Any, Optional

class CacheManager:
    def __init__(self):
        self.redis = redis_client
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        value = await self.redis.get(key)
        if value:
            return json.loads(value)
        return None
    
    async def set(self, key: str, value: Any, expire: int = 3600):
        """Set value in cache."""
        await self.redis.setex(
            key,
            expire,
            json.dumps(value)
        )
    
    async def delete(self, key: str):
        """Delete value from cache."""
        await self.redis.delete(key)
    
    async def invalidate_pattern(self, pattern: str):
        """Invalidate all keys matching pattern."""
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)

# Usage in services
class AssistantService(BaseService[Assistant]):
    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.cache = CacheManager()
    
    async def get(self, id: str) -> Optional[Assistant]:
        """Get assistant with caching."""
        cache_key = f"assistant:{id}"
        
        # Try cache first
        cached = await self.cache.get(cache_key)
        if cached:
            return Assistant(**cached)
        
        # Get from database
        assistant = await super().get(id)
        if assistant:
            # Cache for 1 hour
            await self.cache.set(cache_key, assistant.dict(), 3600)
        
        return assistant
```

### Database Optimization

```python
# Database query optimization
class ConversationService(BaseService[Conversation]):
    async def get_user_conversations(
        self, 
        user_id: str, 
        skip: int = 0, 
        limit: int = 20
    ) -> List[Conversation]:
        """Get user conversations with optimized query."""
        query = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .offset(skip)
            .limit(limit)
            .options(
                selectinload(Conversation.messages),
                selectinload(Conversation.assistant)
            )
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()
```

## Monitoring and Logging

### Structured Logging

```python
# app/core/logging.py
import logging
import json
from datetime import datetime
from typing import Any, Dict

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def log_request(self, request: Request, response_time: float):
        """Log HTTP request."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "method": request.method,
            "url": str(request.url),
            "status_code": getattr(request, 'status_code', None),
            "response_time": response_time,
            "user_agent": request.headers.get("user-agent"),
            "ip_address": request.client.host
        }
        
        self.logger.info(json.dumps(log_data))
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """Log error with context."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {}
        }
        
        self.logger.error(json.dumps(log_data))

# Usage in middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests."""
    start_time = time.time()
    
    response = await call_next(request)
    
    response_time = time.time() - start_time
    logger = StructuredLogger("http")
    logger.log_request(request, response_time)
    
    return response
```

## Security Considerations

### Input Validation

```python
# app/utils/validators.py
from pydantic import validator
import re

def validate_email(email: str) -> str:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValueError("Invalid email format")
    return email.lower()

def validate_password_strength(password: str) -> str:
    """Validate password strength."""
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters")
    
    if not re.search(r'[A-Z]', password):
        raise ValueError("Password must contain uppercase letter")
    
    if not re.search(r'[a-z]', password):
        raise ValueError("Password must contain lowercase letter")
    
    if not re.search(r'\d', password):
        raise ValueError("Password must contain digit")
    
    return password

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage."""
    # Remove dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Limit length
    return filename[:255]
```

### SQL Injection Prevention

```python
# Always use parameterized queries
async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get user by email using parameterized query."""
    result = await db.execute(
        select(User).where(User.email == email)
    )
    return result.scalar_one_or_none()

# Never use string concatenation
# BAD: f"SELECT * FROM users WHERE email = '{email}'"
# GOOD: Use ORM or parameterized queries
```

## Deployment Considerations

### Environment Configuration

```python
# Production settings
class ProductionSettings(Settings):
    DEBUG: bool = False
    ALLOWED_HOSTS: List[str] = ["yourdomain.com"]
    
    # Use environment variables for secrets
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    REDIS_URL: str = os.getenv("REDIS_URL")
    
    # Security headers
    SECURE_COOKIES: bool = True
    HTTPS_ONLY: bool = True

# Development settings
class DevelopmentSettings(Settings):
    DEBUG: bool = True
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Local development
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost/dev_db"
    REDIS_URL: str = "redis://localhost:6379"
```

### Health Checks

```python
# app/api/v1/endpoints/health.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.redis_client import redis_client
from app.core.weaviate_client import weaviate_client

router = APIRouter()

@router.get("/")
async def health_check():
    """Basic health check."""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@router.get("/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """Detailed health check with dependencies."""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "dependencies": {}
    }
    
    # Check database
    try:
        await db.execute("SELECT 1")
        health_status["dependencies"]["database"] = "healthy"
    except Exception as e:
        health_status["dependencies"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check Redis
    try:
        await redis_client.ping()
        health_status["dependencies"]["redis"] = "healthy"
    except Exception as e:
        health_status["dependencies"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check Weaviate
    try:
        await weaviate_client.is_ready()
        health_status["dependencies"]["weaviate"] = "healthy"
    except Exception as e:
        health_status["dependencies"]["weaviate"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    return health_status
```

This backend architecture provides a solid foundation for the AI Assistant Platform with proper separation of concerns, security measures, and scalability considerations. 