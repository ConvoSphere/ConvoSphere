# Authentication

The AI Assistant Platform uses JWT (JSON Web Tokens) for authentication and authorization. This document covers all aspects of authentication, from user registration to token management.

## 📋 Table of Contents

- [Overview](#overview)
- [Authentication Flow](#authentication-flow)
- [User Registration](#user-registration)
- [User Login](#user-login)
- [Token Management](#token-management)
- [Password Management](#password-management)
- [Role-Based Access Control](#role-based-access-control)
- [Security Best Practices](#security-best-practices)
- [Error Handling](#error-handling)

## 🔐 Overview

The platform implements a secure authentication system with the following features:

- **JWT-based authentication** with access and refresh tokens
- **Role-based access control** (Admin, User, Guest)
- **Password security** with bcrypt hashing
- **Rate limiting** on authentication endpoints
- **Token blacklisting** for secure logout
- **Audit logging** for security events

### Authentication Endpoints

| Endpoint | Method | Description | Authentication Required |
|----------|--------|-------------|------------------------|
| `/api/v1/auth/register` | POST | Register new user | No |
| `/api/v1/auth/login` | POST | User login | No |
| `/api/v1/auth/logout` | POST | User logout | Yes |
| `/api/v1/auth/refresh` | POST | Refresh access token | Yes |
| `/api/v1/auth/me` | GET | Get current user info | Yes |
| `/api/v1/auth/change-password` | POST | Change password | Yes |
| `/api/v1/auth/forgot-password` | POST | Request password reset | No |
| `/api/v1/auth/reset-password` | POST | Reset password | No |

## 🔄 Authentication Flow

### 1. User Registration
```mermaid
sequenceDiagram
    participant C as Client
    participant A as API
    participant D as Database
    
    C->>A: POST /auth/register
    A->>A: Validate input
    A->>D: Check if user exists
    A->>A: Hash password
    A->>D: Create user
    A->>C: Return user data
```

### 2. User Login
```mermaid
sequenceDiagram
    participant C as Client
    participant A as API
    participant D as Database
    participant R as Redis
    
    C->>A: POST /auth/login
    A->>A: Validate credentials
    A->>D: Get user by email
    A->>A: Verify password
    A->>A: Generate tokens
    A->>R: Store refresh token
    A->>C: Return tokens
```

### 3. API Request with Token
```mermaid
sequenceDiagram
    participant C as Client
    participant A as API
    participant R as Redis
    
    C->>A: Request with Bearer token
    A->>A: Validate JWT token
    A->>R: Check if token is blacklisted
    A->>A: Extract user info
    A->>A: Process request
    A->>C: Return response
```

## 👤 User Registration

### Register a New User

**Endpoint:** `POST /api/v1/auth/register`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe",
  "role": "user"
}
```

**Response (201 Created):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "user",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### Registration Validation Rules

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `email` | string | Yes | Valid email format, unique |
| `password` | string | Yes | Min 8 chars, complexity rules |
| `first_name` | string | No | Max 50 characters |
| `last_name` | string | No | Max 50 characters |
| `role` | string | No | Default: "user" |

### Password Requirements

- **Minimum length**: 8 characters
- **Must contain**: At least one uppercase letter
- **Must contain**: At least one lowercase letter
- **Must contain**: At least one digit
- **Must contain**: At least one special character

## 🔑 User Login

### Login with Credentials

**Endpoint:** `POST /api/v1/auth/login`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "user",
    "is_active": true
  }
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

### Login with Remember Me

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "remember_me": true
}
```

When `remember_me` is true, the refresh token will have a longer expiration time (7 days instead of 1 day).

## 🎫 Token Management

### Using Access Tokens

Include the access token in the Authorization header for authenticated requests:

```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Token Structure

**Access Token Payload:**
```json
{
  "sub": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "role": "user",
  "exp": 1705312200,
  "iat": 1705310400,
  "type": "access"
}
```

**Refresh Token Payload:**
```json
{
  "sub": "123e4567-e89b-12d3-a456-426614174000",
  "jti": "refresh_token_id",
  "exp": 1705915200,
  "iat": 1705310400,
  "type": "refresh"
}
```

### Refresh Access Token

**Endpoint:** `POST /api/v1/auth/refresh`

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer current_access_token" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

### Logout

**Endpoint:** `POST /api/v1/auth/logout`

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**
```json
{
  "message": "Successfully logged out"
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/logout" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer access_token" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

## 🔒 Password Management

### Change Password

**Endpoint:** `POST /api/v1/auth/change-password`

**Request Body:**
```json
{
  "current_password": "oldpassword123",
  "new_password": "newsecurepassword456"
}
```

**Response (200 OK):**
```json
{
  "message": "Password changed successfully"
}
```

### Forgot Password

**Endpoint:** `POST /api/v1/auth/forgot-password`

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response (200 OK):**
```json
{
  "message": "Password reset email sent"
}
```

### Reset Password

**Endpoint:** `POST /api/v1/auth/reset-password`

**Request Body:**
```json
{
  "token": "reset_token_from_email",
  "new_password": "newsecurepassword456"
}
```

**Response (200 OK):**
```json
{
  "message": "Password reset successfully"
}
```

## 👥 Role-Based Access Control

### User Roles

The platform supports three user roles:

| Role | Description | Permissions |
|------|-------------|-------------|
| **Admin** | System administrator | Full access to all features |
| **User** | Regular user | Access to personal data and features |
| **Guest** | Limited access user | Read-only access to public features |

### Role Permissions

#### Admin Permissions
- ✅ Full access to all endpoints
- ✅ User management (create, read, update, delete)
- ✅ System configuration
- ✅ Audit logs access
- ✅ Database management

#### User Permissions
- ✅ Personal profile management
- ✅ Create and manage assistants
- ✅ Access to conversations
- ✅ Upload and manage documents
- ✅ Use tools and integrations

#### Guest Permissions
- ✅ Read public information
- ✅ View public assistants
- ✅ Limited API access

### Checking User Role

```python
# In your API endpoint
from app.core.auth import get_current_user
from app.models.user import User

@router.get("/admin-only")
async def admin_only_endpoint(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return {"message": "Admin access granted"}
```

### Role-Based Endpoint Protection

```python
from app.core.auth import require_role

@router.get("/users")
@require_role("admin")
async def get_all_users():
    return {"users": [...]}

@router.get("/my-profile")
@require_role(["user", "admin"])
async def get_my_profile():
    return {"profile": {...}}
```

## 🛡️ Security Best Practices

### Token Security

1. **Store tokens securely**
   - Access tokens: Memory only (not localStorage)
   - Refresh tokens: HttpOnly cookies or secure storage

2. **Token expiration**
   - Access tokens: 30 minutes
   - Refresh tokens: 1 day (7 days with remember_me)

3. **Token rotation**
   - Refresh tokens are rotated on each use
   - Old refresh tokens are invalidated

### Password Security

1. **Password hashing**
   - Uses bcrypt with salt rounds
   - Configurable cost factor

2. **Password validation**
   - Minimum length and complexity requirements
   - Password history checking
   - Common password blocking

3. **Account lockout**
   - Failed login attempts tracking
   - Temporary account lockout
   - Progressive delays

### API Security

1. **Rate limiting**
   - Authentication endpoints: 5 requests per minute
   - General API: 100 requests per minute
   - Configurable per endpoint

2. **Input validation**
   - All inputs are validated and sanitized
   - SQL injection protection
   - XSS protection

3. **Audit logging**
   - All authentication events logged
   - Failed login attempts tracked
   - Security event monitoring

## ❌ Error Handling

### Common Authentication Errors

| Status Code | Error Code | Description |
|-------------|------------|-------------|
| `400` | `INVALID_CREDENTIALS` | Invalid email or password |
| `400` | `EMAIL_ALREADY_EXISTS` | Email already registered |
| `400` | `WEAK_PASSWORD` | Password doesn't meet requirements |
| `401` | `INVALID_TOKEN` | Invalid or expired token |
| `401` | `TOKEN_EXPIRED` | Access token has expired |
| `401` | `TOKEN_BLACKLISTED` | Token has been revoked |
| `403` | `INSUFFICIENT_PERMISSIONS` | User lacks required permissions |
| `429` | `RATE_LIMIT_EXCEEDED` | Too many requests |

### Error Response Format

```json
{
  "detail": "Invalid credentials",
  "error_code": "INVALID_CREDENTIALS",
  "status_code": 400,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Handling Token Expiration

```javascript
// Client-side token refresh example
async function makeAuthenticatedRequest(url, options = {}) {
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${getAccessToken()}`
      }
    });
    
    if (response.status === 401) {
      // Token expired, try to refresh
      const refreshed = await refreshToken();
      if (refreshed) {
        // Retry the original request
        return makeAuthenticatedRequest(url, options);
      } else {
        // Redirect to login
        window.location.href = '/login';
      }
    }
    
    return response;
  } catch (error) {
    console.error('Request failed:', error);
    throw error;
  }
}
```

## 📝 Examples

### Complete Authentication Flow

```javascript
// 1. Register a new user
const registerResponse = await fetch('/api/v1/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'securepassword123',
    first_name: 'John',
    last_name: 'Doe'
  })
});

// 2. Login to get tokens
const loginResponse = await fetch('/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'securepassword123'
  })
});

const { access_token, refresh_token } = await loginResponse.json();

// 3. Make authenticated requests
const userResponse = await fetch('/api/v1/auth/me', {
  headers: {
    'Authorization': `Bearer ${access_token}`
  }
});

// 4. Refresh token when needed
const refreshResponse = await fetch('/api/v1/auth/refresh', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ refresh_token })
});

// 5. Logout
await fetch('/api/v1/auth/logout', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ refresh_token })
});
```

### Python Client Example

```python
import requests

class ChatAssistantClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.access_token = None
        self.refresh_token = None
    
    def register(self, email, password, first_name=None, last_name=None):
        response = requests.post(f"{self.base_url}/api/v1/auth/register", json={
            "email": email,
            "password": password,
            "first_name": first_name,
            "last_name": last_name
        })
        return response.json()
    
    def login(self, email, password, remember_me=False):
        response = requests.post(f"{self.base_url}/api/v1/auth/login", json={
            "email": email,
            "password": password,
            "remember_me": remember_me
        })
        data = response.json()
        self.access_token = data["access_token"]
        self.refresh_token = data["refresh_token"]
        return data
    
    def get_headers(self):
        return {"Authorization": f"Bearer {self.access_token}"}
    
    def get_me(self):
        response = requests.get(
            f"{self.base_url}/api/v1/auth/me",
            headers=self.get_headers()
        )
        return response.json()
    
    def logout(self):
        response = requests.post(
            f"{self.base_url}/api/v1/auth/logout",
            headers=self.get_headers(),
            json={"refresh_token": self.refresh_token}
        )
        self.access_token = None
        self.refresh_token = None
        return response.json()

# Usage
client = ChatAssistantClient()
client.register("user@example.com", "password123")
client.login("user@example.com", "password123")
user_info = client.get_me()
client.logout()
```

---

<div align="center">

**Ready to implement authentication?** [API Reference →](overview.md)

</div> 

## 🚀 SSO (Single Sign-On) Integration

The platform supports SSO via OIDC, SAML, and OAuth2 (Google, Microsoft, etc.).

### SSO Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/sso/login/{provider}` | GET | Redirect to SSO provider |
| `/api/v1/auth/sso/callback/{provider}` | GET | Handle SSO callback and user provisioning |
| `/api/v1/auth/sso/link/{provider}` | POST | Link SSO account to existing user |

### SSO Flow
1. User clicks SSO login button (e.g. "Login with Google").
2. User is redirected to the provider and authenticates.
3. Provider redirects back to `/sso/callback/{provider}`.
4. User is provisioned (JIT) or eingeloggt.
5. Optional: Account-Linking, falls E-Mail schon existiert.

### SSO Provider Configuration
- Configure client ID, secret, redirect URIs in the deployment config.
- Supported providers: Google, Microsoft, SAML, OIDC, etc.
- Attribute mapping: SSO attributes (email, name, roles) are mapped to user fields.

### Account Linking
- Existing users can link SSO accounts via `/sso/link/{provider}`.
- SSO events are audit-logged.

---

## 🏢 Erweiterte RBAC

- Hierarchische Rollen: Super Admin, Admin, Manager, User, Guest
- Gruppenbasierte Rechte und Bereichs-Admins
- Feingranulare Rechteverwaltung (z.B. auf Ressourcenebene)
- Admin-API und UI für Rollen, Rechte, Gruppen
- Delegierte Administration: Bereichs-/Team-Admins können User in ihrem Bereich verwalten
- Alle Änderungen werden audit-logged 