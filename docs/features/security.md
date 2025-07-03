# Security Features

## Overview

The AI Assistant Platform implements comprehensive security measures to protect user data, prevent abuse, and ensure secure operations across all components.

## Authentication

### JWT Token Management

The platform uses JSON Web Tokens (JWT) for stateless authentication with Redis-based blacklisting for enhanced security.

#### Token Structure

```python
# JWT token payload
{
    "sub": "user_id",
    "email": "user@example.com",
    "role": "user",
    "exp": 1640995200,  # Expiration timestamp
    "iat": 1640908800,  # Issued at timestamp
    "jti": "token_id"   # Unique token identifier
}
```

#### Token Configuration

```python
# Security settings
JWT_SECRET_KEY = "your-secure-secret-key"
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
```

#### Token Blacklisting

```python
class TokenBlacklist:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.prefix = "blacklisted_token:"
    
    async def blacklist_token(self, token_id: str, expires_in: int):
        """Add token to blacklist."""
        await self.redis.setex(
            f"{self.prefix}{token_id}",
            expires_in,
            "blacklisted"
        )
    
    async def is_blacklisted(self, token_id: str) -> bool:
        """Check if token is blacklisted."""
        return await self.redis.exists(f"{self.prefix}{token_id}")
```

### Password Security

#### Password Hashing

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)
```

#### Password Validation

```python
def validate_password_strength(password: str) -> bool:
    """Validate password strength requirements."""
    if len(password) < 8:
        return False
    
    # Check for uppercase, lowercase, digit, special char
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    return has_upper and has_lower and has_digit and has_special
```

## Authorization

### Role-Based Access Control (RBAC)

The platform implements a flexible role-based access control system.

#### User Roles

```python
class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"
    GUEST = "guest"

class Permission(str, Enum):
    # User management
    CREATE_USER = "create_user"
    READ_USER = "read_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"
    
    # Assistant management
    CREATE_ASSISTANT = "create_assistant"
    READ_ASSISTANT = "read_assistant"
    UPDATE_ASSISTANT = "update_assistant"
    DELETE_ASSISTANT = "delete_assistant"
    
    # System administration
    MANAGE_SYSTEM = "manage_system"
    VIEW_LOGS = "view_logs"
    MANAGE_TOOLS = "manage_tools"
```

#### Permission Mapping

```python
ROLE_PERMISSIONS = {
    UserRole.ADMIN: [
        Permission.CREATE_USER,
        Permission.READ_USER,
        Permission.UPDATE_USER,
        Permission.DELETE_USER,
        Permission.CREATE_ASSISTANT,
        Permission.READ_ASSISTANT,
        Permission.UPDATE_ASSISTANT,
        Permission.DELETE_ASSISTANT,
        Permission.MANAGE_SYSTEM,
        Permission.VIEW_LOGS,
        Permission.MANAGE_TOOLS
    ],
    UserRole.USER: [
        Permission.READ_USER,
        Permission.UPDATE_USER,
        Permission.CREATE_ASSISTANT,
        Permission.READ_ASSISTANT,
        Permission.UPDATE_ASSISTANT
    ],
    UserRole.MODERATOR: [
        Permission.READ_USER,
        Permission.UPDATE_USER,
        Permission.READ_ASSISTANT,
        Permission.UPDATE_ASSISTANT,
        Permission.VIEW_LOGS
    ],
    UserRole.GUEST: [
        Permission.READ_ASSISTANT
    ]
}
```

#### Permission Checking

```python
def check_permission(user_role: UserRole, required_permission: Permission) -> bool:
    """Check if user has required permission."""
    user_permissions = ROLE_PERMISSIONS.get(user_role, [])
    return required_permission in user_permissions

async def require_permission(permission: Permission):
    """Dependency for requiring specific permission."""
    async def permission_checker(current_user: User = Depends(get_current_user)):
        if not check_permission(current_user.role, permission):
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions"
            )
        return current_user
    return permission_checker
```

## Rate Limiting

### Redis-Based Rate Limiting

The platform implements sophisticated rate limiting using Redis to prevent abuse and ensure fair usage.

#### Rate Limiter Implementation

```python
class RateLimiter:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.default_limit = 100  # requests per minute
        self.default_window = 60  # seconds
    
    async def check_rate_limit(
        self,
        identifier: str,
        limit: int = None,
        window: int = None
    ) -> bool:
        """Check if request is within rate limit."""
        limit = limit or self.default_limit
        window = window or self.default_window
        
        current_time = int(time.time())
        window_start = current_time - window
        
        # Get current request count
        key = f"rate_limit:{identifier}:{window_start}"
        current_count = await self.redis.get(key)
        
        if current_count and int(current_count) >= limit:
            return False
        
        # Increment counter
        pipe = self.redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, window)
        await pipe.execute()
        
        return True
    
    async def get_remaining_requests(self, identifier: str) -> int:
        """Get remaining requests for user."""
        current_time = int(time.time())
        window_start = current_time - self.default_window
        key = f"rate_limit:{identifier}:{window_start}"
        
        current_count = await self.redis.get(key)
        return max(0, self.default_limit - int(current_count or 0))
```

#### Rate Limiting Middleware

```python
async def rate_limiter(request: Request):
    """Rate limiting middleware."""
    # Get user identifier (IP or user ID)
    if hasattr(request.state, 'user'):
        identifier = f"user:{request.state.user.id}"
    else:
        identifier = f"ip:{request.client.host}"
    
    # Check rate limit
    if not await rate_limiter.check_rate_limit(identifier):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded"
        )
    
    # Add remaining requests to response headers
    remaining = await rate_limiter.get_remaining_requests(identifier)
    request.state.remaining_requests = remaining
```

## Input Validation

### Pydantic Schemas

All user inputs are validated using Pydantic schemas to prevent injection attacks and ensure data integrity.

#### User Input Validation

```python
from pydantic import BaseModel, EmailStr, validator
import re

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    
    @validator('name')
    def validate_name(cls, v):
        if len(v) < 2 or len(v) > 50:
            raise ValueError('Name must be between 2 and 50 characters')
        if not re.match(r'^[a-zA-Z\s]+$', v):
            raise ValueError('Name can only contain letters and spaces')
        return v.strip()
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain digit')
        return v
```

#### SQL Injection Prevention

```python
# Use parameterized queries
async def get_user_by_email(email: str) -> Optional[User]:
    """Get user by email using parameterized query."""
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    return result.scalar_one_or_none()

# Avoid string concatenation
# BAD: f"SELECT * FROM users WHERE email = '{email}'"
# GOOD: Use ORM or parameterized queries
```

## Audit Logging

### Comprehensive Audit Trail

The platform maintains detailed audit logs for security monitoring and compliance.

#### Audit Event Types

```python
class AuditEventType(str, Enum):
    # Authentication events
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    
    # User management events
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    
    # Assistant events
    ASSISTANT_CREATED = "assistant_created"
    ASSISTANT_UPDATED = "assistant_updated"
    ASSISTANT_DELETED = "assistant_deleted"
    
    # System events
    CONFIGURATION_CHANGED = "configuration_changed"
    SECURITY_ALERT = "security_alert"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
```

#### Audit Logger

```python
class AuditLogger:
    def __init__(self, db_session):
        self.db = db_session
    
    async def log_event(
        self,
        event_type: AuditEventType,
        user_id: Optional[str],
        details: Dict[str, Any],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Log audit event."""
        audit_entry = AuditLog(
            event_type=event_type,
            user_id=user_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.utcnow()
        )
        
        self.db.add(audit_entry)
        await self.db.commit()
    
    async def log_security_event(
        self,
        event_type: AuditEventType,
        user_id: Optional[str],
        details: Dict[str, Any],
        severity: str = "medium"
    ):
        """Log security-related event."""
        details["severity"] = severity
        await self.log_event(event_type, user_id, details)
```

## Data Protection

### Encryption

#### Sensitive Data Encryption

```python
from cryptography.fernet import Fernet
import base64

class DataEncryption:
    def __init__(self, key: str):
        self.cipher = Fernet(key.encode())
    
    def encrypt(self, data: str) -> str:
        """Encrypt sensitive data."""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    def encrypt_field(self, model, field_name: str):
        """Encrypt field value before saving."""
        value = getattr(model, field_name)
        if value:
            setattr(model, field_name, self.encrypt(value))
    
    def decrypt_field(self, model, field_name: str):
        """Decrypt field value after loading."""
        value = getattr(model, field_name)
        if value:
            setattr(model, field_name, self.decrypt(value))
```

### Data Sanitization

#### Input Sanitization

```python
import html
import re

def sanitize_html(text: str) -> str:
    """Sanitize HTML content."""
    # Remove potentially dangerous HTML tags
    dangerous_tags = re.compile(r'<(script|iframe|object|embed|form).*?>.*?</\1>', re.IGNORECASE)
    text = dangerous_tags.sub('', text)
    
    # Escape remaining HTML
    return html.escape(text)

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage."""
    # Remove dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Limit length
    return filename[:255]

def sanitize_sql_input(text: str) -> str:
    """Sanitize input for SQL queries (use ORM instead)."""
    # This is a basic example - prefer using ORM
    return text.replace("'", "''").replace(";", "")
```

## Security Headers

### HTTP Security Headers

The platform sets appropriate security headers to protect against common web vulnerabilities.

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    
    return response
```

## Security Monitoring

### Real-time Security Monitoring

```python
class SecurityMonitor:
    def __init__(self):
        self.suspicious_patterns = [
            r"<script.*?>",
            r"javascript:",
            r"on\w+\s*=",
            r"union\s+select",
            r"drop\s+table"
        ]
    
    def detect_suspicious_activity(self, request: Request) -> bool:
        """Detect suspicious activity patterns."""
        # Check request path
        path = request.url.path.lower()
        if any(pattern in path for pattern in ["admin", "config", "backup"]):
            return True
        
        # Check request headers
        user_agent = request.headers.get("user-agent", "")
        if "sqlmap" in user_agent.lower() or "nikto" in user_agent.lower():
            return True
        
        # Check request body
        if request.method in ["POST", "PUT"]:
            body = request.body()
            if any(re.search(pattern, body, re.IGNORECASE) for pattern in self.suspicious_patterns):
                return True
        
        return False
    
    async def log_security_alert(self, request: Request, alert_type: str):
        """Log security alert."""
        await audit_logger.log_security_event(
            AuditEventType.SECURITY_ALERT,
            getattr(request.state, 'user_id', None),
            {
                "alert_type": alert_type,
                "ip_address": request.client.host,
                "user_agent": request.headers.get("user-agent"),
                "path": request.url.path,
                "method": request.method
            },
            severity="high"
        )
```

## Best Practices

### Security Checklist

1. **Authentication**
   - Use strong password requirements
   - Implement account lockout after failed attempts
   - Use secure session management
   - Implement multi-factor authentication (future)

2. **Authorization**
   - Follow principle of least privilege
   - Implement role-based access control
   - Validate permissions on every request
   - Use secure token management

3. **Data Protection**
   - Encrypt sensitive data at rest
   - Use HTTPS for all communications
   - Implement proper data sanitization
   - Follow data retention policies

4. **Monitoring**
   - Log all security events
   - Monitor for suspicious activity
   - Implement alerting for security incidents
   - Regular security audits

5. **Infrastructure**
   - Keep dependencies updated
   - Use secure configuration management
   - Implement network segmentation
   - Regular security assessments 