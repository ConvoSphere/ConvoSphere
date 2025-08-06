# Password Reset Integration Guide

## Overview

This guide provides comprehensive documentation for developers who want to integrate the password reset functionality into their applications or extend the existing implementation.

## Architecture Overview

### System Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Database      │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (PostgreSQL)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Email Service │    │   Token Service │    │   Audit Service │
│   (SMTP)        │    │   (Security)    │    │   (Logging)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Data Flow

1. **User requests password reset** → Frontend → Backend API
2. **Token generation** → Backend → Database
3. **Email sending** → Backend → Email Service
4. **User clicks reset link** → Frontend → Backend API
5. **Token validation** → Backend → Database
6. **Password reset** → Backend → Database
7. **Audit logging** → Backend → Audit Service

## Backend Integration

### API Endpoints

#### 1. Request Password Reset

```http
POST /api/v1/auth/forgot-password
Content-Type: application/json

{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "message": "If the email address exists, a password reset link has been sent.",
  "status": "success"
}
```

#### 2. Reset Password

```http
POST /api/v1/auth/reset-password
Content-Type: application/json

{
  "token": "valid-reset-token-123",
  "new_password": "NewSecurePassword123!"
}
```

**Response:**
```json
{
  "message": "Password reset successfully",
  "status": "success"
}
```

#### 3. Validate Reset Token

```http
POST /api/v1/auth/validate-reset-token
Content-Type: application/json

{
  "token": "valid-reset-token-123"
}
```

**Response:**
```json
{
  "valid": true,
  "message": "Token is valid"
}
```

#### 4. Generate CSRF Token

```http
GET /api/v1/auth/csrf-token
X-Session-ID: session-123
```

**Response:**
```json
{
  "csrf_token": "generated-csrf-token-123",
  "expires_in": 1800,
  "session_id": "session-123"
}
```

### Error Handling

#### HTTP Status Codes

| Code | Description | Example Response |
|------|-------------|------------------|
| 200 | Success | `{"status": "success", "message": "..."}` |
| 400 | Bad Request | `{"detail": "Invalid or expired token"}` |
| 429 | Rate Limited | `{"detail": "Too many requests"}` |
| 500 | Server Error | `{"detail": "Internal server error"}` |

#### Error Response Format

```json
{
  "detail": "Error message description",
  "error_code": "OPTIONAL_ERROR_CODE",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Rate Limiting

The API implements rate limiting to prevent abuse:

- **IP-based limit:** 5 requests per IP per hour
- **Email-based limit:** 3 requests per email per hour
- **Window:** 1 hour (3600 seconds)

When rate limited, the API returns:

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
  "detail": "Too many password reset requests. Please try again later.",
  "retry_after": 3600
}
```

## Frontend Integration

### React Components

#### ForgotPassword Component

```tsx
import React, { useState } from 'react';
import { forgotPassword } from '../services/auth';

const ForgotPassword: React.FC = () => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const result = await forgotPassword(email);
      if (result.success) {
        setSuccess(true);
      }
    } catch (error) {
      console.error('Password reset request failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Enter your email"
        required
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Sending...' : 'Send Reset Email'}
      </button>
    </form>
  );
};
```

#### ResetPassword Component

```tsx
import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { resetPassword, validateResetToken } from '../services/auth';

const ResetPassword: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [tokenValid, setTokenValid] = useState(false);
  
  const token = searchParams.get('token');

  useEffect(() => {
    const validateToken = async () => {
      if (token) {
        try {
          const result = await validateResetToken(token);
          setTokenValid(result.valid);
        } catch (error) {
          setTokenValid(false);
        }
      }
    };
    
    validateToken();
  }, [token]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      alert('Passwords do not match');
      return;
    }
    
    setLoading(true);
    try {
      const result = await resetPassword(token!, password);
      if (result.success) {
        // Redirect to login or show success message
      }
    } catch (error) {
      console.error('Password reset failed:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!tokenValid) {
    return <div>Invalid or expired token</div>;
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="New password"
        required
      />
      <input
        type="password"
        value={confirmPassword}
        onChange={(e) => setConfirmPassword(e.target.value)}
        placeholder="Confirm password"
        required
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Resetting...' : 'Reset Password'}
      </button>
    </form>
  );
};
```

### Auth Service Integration

```typescript
// services/auth.ts

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordResetConfirm {
  token: string;
  new_password: string;
}

export interface PasswordResetResponse {
  success: boolean;
  message: string;
}

export interface TokenValidationResponse {
  valid: boolean;
  message: string;
}

export async function forgotPassword(email: string): Promise<PasswordResetResponse> {
  const response = await fetch('/api/v1/auth/forgot-password', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email }),
  });

  if (response.status === 429) {
    throw new Error('Rate limit exceeded');
  }

  const data = await response.json();
  
  if (!response.ok) {
    throw new Error(data.detail || 'Password reset request failed');
  }

  return data;
}

export async function resetPassword(token: string, newPassword: string): Promise<PasswordResetResponse> {
  const response = await fetch('/api/v1/auth/reset-password', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      token,
      new_password: newPassword,
    }),
  });

  const data = await response.json();
  
  if (!response.ok) {
    throw new Error(data.detail || 'Password reset failed');
  }

  return data;
}

export async function validateResetToken(token: string): Promise<TokenValidationResponse> {
  const response = await fetch('/api/v1/auth/validate-reset-token', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ token }),
  });

  const data = await response.json();
  
  if (!response.ok) {
    throw new Error(data.detail || 'Token validation failed');
  }

  return data;
}

export async function getCsrfToken(sessionId?: string): Promise<{ csrf_token: string; expires_in: number }> {
  const headers: Record<string, string> = {};
  if (sessionId) {
    headers['X-Session-ID'] = sessionId;
  }

  const response = await fetch('/api/v1/auth/csrf-token', {
    method: 'GET',
    headers,
  });

  const data = await response.json();
  
  if (!response.ok) {
    throw new Error(data.detail || 'CSRF token generation failed');
  }

  return data;
}
```

## Database Schema

### User Table Extensions

```sql
-- Add password reset fields to users table
ALTER TABLE users ADD COLUMN password_reset_token VARCHAR(255);
ALTER TABLE users ADD COLUMN password_reset_expires_at TIMESTAMP WITH TIME ZONE;

-- Create index for performance
CREATE INDEX idx_users_password_reset_token ON users(password_reset_token);
```

### Audit Log Table

```sql
-- Extended audit log table for password reset events
CREATE TABLE extended_audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id VARCHAR(255) UNIQUE NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    event_category VARCHAR(50) NOT NULL,
    severity VARCHAR(20) DEFAULT 'info',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_id UUID REFERENCES users(id),
    ip_address VARCHAR(45),
    user_agent TEXT,
    context JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_audit_logs_event_type ON extended_audit_logs(event_type);
CREATE INDEX idx_audit_logs_timestamp ON extended_audit_logs(timestamp);
CREATE INDEX idx_audit_logs_user_id ON extended_audit_logs(user_id);
```

## Configuration

### Environment Variables

```bash
# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM_ADDRESS=noreply@yourdomain.com

# Password Reset Configuration
PASSWORD_RESET_TOKEN_EXPIRE_MINUTES=60
PASSWORD_RESET_BASE_URL=https://yourdomain.com

# Rate Limiting Configuration
PASSWORD_RESET_RATE_LIMIT_IP_MAX=5
PASSWORD_RESET_RATE_LIMIT_EMAIL_MAX=3
PASSWORD_RESET_RATE_LIMIT_WINDOW=3600

# CSRF Protection Configuration
CSRF_TOKEN_EXPIRE_MINUTES=30
CSRF_PROTECTION_ENABLED=true
```

### Email Templates

#### Password Reset Email Template

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Password Reset</title>
</head>
<body>
    <h2>Password Reset Request</h2>
    <p>You have requested to reset your password.</p>
    <p>Click the following link to reset your password:</p>
    <p><a href="{{ reset_url }}">Reset Password</a></p>
    <p>This link is valid for {{ expire_minutes }} minutes.</p>
    <p>If you did not request this, you can ignore this email.</p>
    <p>Best regards,<br>Your AI Assistant Platform Team</p>
</body>
</html>
```

#### Password Changed Notification Template

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Password Changed</title>
</head>
<body>
    <h2>Password Changed</h2>
    <p>Your password has been successfully changed.</p>
    <p>If you did not make this change, please contact support immediately.</p>
    <p>Best regards,<br>Your AI Assistant Platform Team</p>
</body>
</html>
```

## Security Implementation

### Token Generation

```python
import secrets
import string

def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))
```

### Password Validation

```python
import re

def validate_password_strength(password: str) -> tuple[bool, str]:
    """Validate password strength requirements."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    if not re.search(r'[@$!%*?&]', password):
        return False, "Password must contain at least one special character (@$!%*?&)"
    
    return True, "Password meets requirements"
```

### Rate Limiting Implementation

```python
import time
from typing import Dict, List

class RateLimiter:
    def __init__(self):
        self.requests: Dict[str, List[float]] = {}
    
    def is_allowed(self, identifier: str, max_requests: int, window: int) -> bool:
        """Check if request is allowed based on rate limiting rules."""
        current_time = time.time()
        window_start = current_time - window
        
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        # Clean old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if req_time > window_start
        ]
        
        # Check if limit exceeded
        if len(self.requests[identifier]) >= max_requests:
            return False
        
        # Add current request
        self.requests[identifier].append(current_time)
        return True
```

## Testing

### Unit Tests

```python
import pytest
from unittest.mock import Mock, patch
from your_app.services.auth_service import AuthService

class TestPasswordReset:
    @pytest.fixture
    def auth_service(self):
        return AuthService()
    
    def test_forgot_password_success(self, auth_service):
        """Test successful password reset request."""
        with patch('your_app.services.email_service.send_email') as mock_send:
            mock_send.return_value = True
            
            result = auth_service.request_password_reset("test@example.com")
            assert result is True
            mock_send.assert_called_once()
    
    def test_forgot_password_user_not_found(self, auth_service):
        """Test password reset request for non-existent user."""
        with pytest.raises(ValueError, match="User not found"):
            auth_service.request_password_reset("nonexistent@example.com")
    
    def test_reset_password_success(self, auth_service):
        """Test successful password reset."""
        # Setup test user with valid token
        user = create_test_user_with_token()
        
        result = auth_service.reset_password_with_token(
            user.password_reset_token,
            "NewPassword123!"
        )
        
        assert result is True
        assert user.password_reset_token is None  # Token should be cleared
```

### Integration Tests

```python
from fastapi.testclient import TestClient
from your_app.main import app

client = TestClient(app)

def test_password_reset_flow():
    """Test complete password reset flow."""
    # Step 1: Request password reset
    response = client.post("/api/v1/auth/forgot-password", json={
        "email": "test@example.com"
    })
    assert response.status_code == 200
    
    # Step 2: Get token from database (in real scenario, from email)
    token = get_reset_token_from_database("test@example.com")
    
    # Step 3: Validate token
    response = client.post("/api/v1/auth/validate-reset-token", json={
        "token": token
    })
    assert response.status_code == 200
    assert response.json()["valid"] is True
    
    # Step 4: Reset password
    response = client.post("/api/v1/auth/reset-password", json={
        "token": token,
        "new_password": "NewPassword123!"
    })
    assert response.status_code == 200
```

### E2E Tests

```typescript
// cypress/integration/password_reset.spec.ts

describe('Password Reset Flow', () => {
  it('should complete password reset successfully', () => {
    // Mock API responses
    cy.intercept('POST', '/api/v1/auth/forgot-password', {
      statusCode: 200,
      body: { message: 'Email sent', status: 'success' }
    }).as('forgotPassword');
    
    cy.intercept('POST', '/api/v1/auth/validate-reset-token', {
      statusCode: 200,
      body: { valid: true, message: 'Token is valid' }
    }).as('validateToken');
    
    cy.intercept('POST', '/api/v1/auth/reset-password', {
      statusCode: 200,
      body: { message: 'Password reset successfully', status: 'success' }
    }).as('resetPassword');
    
    // Test flow
    cy.visit('/forgot-password');
    cy.get('input[type="email"]').type('test@example.com');
    cy.get('button[type="submit"]').click();
    
    cy.wait('@forgotPassword');
    cy.contains('Check your email').should('be.visible');
    
    // Simulate clicking email link
    cy.visit('/reset-password?token=valid-token');
    cy.wait('@validateToken');
    
    cy.get('input[type="password"]').first().type('NewPassword123!');
    cy.get('input[type="password"]').last().type('NewPassword123!');
    cy.get('button[type="submit"]').click();
    
    cy.wait('@resetPassword');
    cy.contains('Password reset successfully').should('be.visible');
  });
});
```

## Deployment

### Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/dbname
      - SMTP_HOST=smtp.gmail.com
      - SMTP_PORT=587
      - SMTP_USER=${SMTP_USER}
      - SMTP_PASSWORD=${SMTP_PASSWORD}
    depends_on:
      - db
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=dbname
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Environment Setup

```bash
#!/bin/bash
# setup.sh

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up database
alembic upgrade head

# Run tests
pytest

# Start development server
uvicorn main:app --reload
```

## Monitoring and Logging

### Audit Logging

```python
import logging
from datetime import datetime

def log_password_reset_event(user_id: str, event_type: str, details: dict):
    """Log password reset events for audit purposes."""
    logger = logging.getLogger('audit')
    
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'user_id': user_id,
        'event_type': event_type,
        'details': details,
        'ip_address': get_client_ip(),
        'user_agent': get_user_agent()
    }
    
    logger.info(f"Password reset event: {log_entry}")
```

### Health Checks

```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/health/password-reset")
async def password_reset_health_check():
    """Health check for password reset functionality."""
    try:
        # Check database connection
        db_status = check_database_connection()
        
        # Check email service
        email_status = check_email_service()
        
        # Check rate limiting
        rate_limit_status = check_rate_limiting()
        
        return {
            "status": "healthy" if all([db_status, email_status, rate_limit_status]) else "unhealthy",
            "database": db_status,
            "email_service": email_status,
            "rate_limiting": rate_limit_status,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
```

## Troubleshooting

### Common Issues

#### 1. Email Not Sending

**Symptoms:**
- Users don't receive password reset emails
- SMTP errors in logs

**Solutions:**
- Check SMTP configuration
- Verify email credentials
- Check firewall settings
- Test email service connectivity

#### 2. Rate Limiting Issues

**Symptoms:**
- Users get rate limit errors unexpectedly
- Inconsistent rate limiting behavior

**Solutions:**
- Check rate limiting configuration
- Verify IP address detection
- Review rate limiting logs
- Adjust limits if necessary

#### 3. Token Validation Failures

**Symptoms:**
- Valid tokens are rejected
- Token expiration issues

**Solutions:**
- Check server time synchronization
- Verify token expiration configuration
- Review token generation logic
- Check database timezone settings

### Debug Mode

Enable debug mode for detailed logging:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Password reset specific logger
logger = logging.getLogger('password_reset')
logger.setLevel(logging.DEBUG)
```

### Performance Monitoring

```python
import time
from functools import wraps

def monitor_performance(func):
    """Decorator to monitor function performance."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        logger.info(f"{func.__name__} took {end_time - start_time:.2f} seconds")
        return result
    return wrapper

@monitor_performance
def request_password_reset(email: str) -> bool:
    # Implementation
    pass
```

## Best Practices

### Security Best Practices

1. **Always use HTTPS** for all API communications
2. **Implement rate limiting** to prevent abuse
3. **Use secure token generation** with cryptographically secure random numbers
4. **Validate all inputs** on both client and server
5. **Log security events** for audit purposes
6. **Implement CSRF protection** for sensitive operations
7. **Use secure password requirements** and validation

### Performance Best Practices

1. **Use database indexes** for token lookups
2. **Implement caching** for rate limiting
3. **Use background jobs** for email sending
4. **Optimize database queries** for audit logging
5. **Implement connection pooling** for database connections

### Code Quality Best Practices

1. **Write comprehensive tests** for all functionality
2. **Use type hints** for better code documentation
3. **Follow consistent error handling** patterns
4. **Implement proper logging** for debugging
5. **Use environment variables** for configuration
6. **Document all public APIs** and interfaces

## Support and Resources

### Documentation

- [API Documentation](../api/password_reset_api.md)
- [Security Documentation](../security/password_reset_security.md)
- [User Guide](../user_guide/password_reset_guide.md)

### Code Examples

- [Frontend Integration Examples](./examples/frontend/)
- [Backend Integration Examples](./examples/backend/)
- [Testing Examples](./examples/testing/)

### Community

- [GitHub Issues](https://github.com/your-repo/issues)
- [Discord Community](https://discord.gg/your-community)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/your-tag)

### Professional Support

- [Enterprise Support](mailto:enterprise@yourdomain.com)
- [Security Issues](mailto:security@yourdomain.com)
- [Feature Requests](mailto:features@yourdomain.com)