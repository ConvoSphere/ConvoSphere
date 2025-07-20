# API Overview

## Introduction

The AI Assistant Platform provides a RESTful API for managing assistants, conversations, tools, users, and more. All endpoints are versioned and require authentication unless otherwise noted.

- **Base URL (Development):** `http://localhost:8000/api/v1`
- **Base URL (Production):** `https://your-domain.com/api/v1`

## Authentication

All endpoints (except registration and login) require a valid JWT access token.

- **Login:** `POST /auth/login` (returns access and refresh tokens)
- **Header:**
  ```http
  Authorization: Bearer <access_token>
  ```
- **Token Refresh:** `POST /auth/refresh`

## Versioning

- All endpoints are prefixed with `/api/v1/`.
- Future versions will use `/api/v2/`, etc.

## Error Handling

- Errors are returned as JSON objects with HTTP status codes.
- Example:
  ```json
  {
    "detail": "Invalid credentials",
    "status_code": 401
  }
  ```
- Common error codes:
  - `400` Bad Request
  - `401` Unauthorized
  - `403` Forbidden
  - `404` Not Found
  - `409` Conflict
  - `422` Validation Error
  - `429` Too Many Requests (Rate Limiting)
  - `500` Internal Server Error

## Example Request

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password"
}
```

## Example Response

```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

---

**See also:**
- [Authentication](authentication.md)
- [Users](users.md)
- [Assistants](assistants.md)
- [Conversations](conversations.md)
- [Tools](tools.md)
- [MCP](mcp.md)
- [Knowledge Base](knowledge.md)
- [WebSocket](websocket.md)
- [Errors](errors.md) 