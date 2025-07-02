# API Documentation

## Overview

The AI Assistant Platform provides a comprehensive REST API for managing assistants, conversations, tools, and users.

## Base URL

- Development: `http://localhost:8000/api/v1`
- Production: `https://your-domain.com/api/v1`

## Authentication

All API endpoints require authentication using JWT tokens.

### Login

```http
POST /auth/login
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "password"
}
```

Response:
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 1800
}
```

### Using Tokens

Include the token in the Authorization header:

```http
Authorization: Bearer <access_token>
```

## Endpoints

### Authentication

#### POST /auth/login
Authenticate user and get access token.

#### POST /auth/refresh
Refresh access token using refresh token.

#### POST /auth/logout
Logout user and invalidate tokens.

#### POST /auth/register
Register new user account.

### Users

#### GET /users/me
Get current user profile.

#### PUT /users/me
Update current user profile.

#### GET /users
List all users (admin only).

#### GET /users/{user_id}
Get specific user details.

#### PUT /users/{user_id}
Update user (admin only).

#### DELETE /users/{user_id}
Delete user (admin only).

### Assistants

#### GET /assistants
List all assistants.

Query parameters:
- `page`: Page number (default: 1)
- `size`: Page size (default: 20)
- `status`: Filter by status (active, inactive, draft)
- `category`: Filter by category

Response:
```json
{
    "items": [
        {
            "id": "uuid",
            "name": "Assistant Name",
            "description": "Assistant description",
            "personality": "Friendly and helpful",
            "status": "active",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
    ],
    "total": 100,
    "page": 1,
    "size": 20,
    "pages": 5
}
```

#### POST /assistants
Create new assistant.

Request:
```json
{
    "name": "My Assistant",
    "description": "A helpful AI assistant",
    "personality": "Friendly and professional",
    "system_prompt": "You are a helpful assistant...",
    "tools": ["web_search", "file_upload"],
    "model": "gpt-4",
    "temperature": 0.7
}
```

#### GET /assistants/{assistant_id}
Get specific assistant details.

#### PUT /assistants/{assistant_id}
Update assistant.

#### DELETE /assistants/{assistant_id}
Delete assistant.

### Conversations

#### GET /conversations
List user conversations.

Query parameters:
- `page`: Page number (default: 1)
- `size`: Page size (default: 20)
- `assistant_id`: Filter by assistant

#### POST /conversations
Start new conversation.

Request:
```json
{
    "assistant_id": "uuid",
    "title": "Conversation Title",
    "initial_message": "Hello, how can you help me?"
}
```

#### GET /conversations/{conversation_id}
Get conversation details and messages.

#### POST /conversations/{conversation_id}/messages
Send message to conversation.

Request:
```json
{
    "content": "User message",
    "attachments": [
        {
            "type": "file",
            "url": "https://example.com/file.pdf"
        }
    ]
}
```

#### DELETE /conversations/{conversation_id}
Delete conversation.

### Tools

#### GET /tools
List available tools.

Response:
```json
{
    "items": [
        {
            "id": "web_search",
            "name": "Web Search",
            "description": "Search the web for information",
            "category": "search",
            "parameters": {
                "query": {
                    "type": "string",
                    "required": true,
                    "description": "Search query"
                }
            }
        }
    ]
}
```

#### GET /tools/{tool_id}
Get specific tool details.

#### POST /tools
Create custom tool (admin only).

### Health

#### GET /health
Basic health check.

#### GET /health/detailed
Detailed health check with component status.

## Error Handling

### Error Response Format

```json
{
    "detail": "Error message",
    "status_code": 400,
    "error_code": "VALIDATION_ERROR"
}
```

### Common Error Codes

- `400`: Bad Request - Invalid input
- `401`: Unauthorized - Authentication required
- `403`: Forbidden - Insufficient permissions
- `404`: Not Found - Resource not found
- `422`: Validation Error - Invalid data format
- `500`: Internal Server Error - Server error

### Rate Limiting

- API endpoints: 100 requests per minute
- Authentication endpoints: 10 requests per minute

## WebSocket Support

### Real-time Updates

Connect to WebSocket endpoint for real-time updates:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};
```

### Message Types

- `conversation_update`: New message in conversation
- `assistant_status`: Assistant status change
- `system_notification`: System notifications

## SDK Examples

### Python SDK

```python
from ai_assistant_sdk import AIAssistantClient

client = AIAssistantClient(
    base_url="http://localhost:8000/api/v1",
    api_key="your-api-key"
)

# List assistants
assistants = client.assistants.list()

# Start conversation
conversation = client.conversations.create(
    assistant_id="uuid",
    message="Hello!"
)
```

### JavaScript SDK

```javascript
import { AIAssistantClient } from '@ai-assistant/sdk';

const client = new AIAssistantClient({
    baseUrl: 'http://localhost:8000/api/v1',
    apiKey: 'your-api-key'
});

// List assistants
const assistants = await client.assistants.list();

// Start conversation
const conversation = await client.conversations.create({
    assistantId: 'uuid',
    message: 'Hello!'
});
```

## Pagination

All list endpoints support pagination:

```json
{
    "items": [...],
    "total": 100,
    "page": 1,
    "size": 20,
    "pages": 5,
    "has_next": true,
    "has_prev": false
}
```

## Filtering and Sorting

### Filtering

Use query parameters for filtering:

```
GET /assistants?status=active&category=general
```

### Sorting

Use `sort` parameter:

```
GET /assistants?sort=name:asc
GET /assistants?sort=created_at:desc
```

## File Upload

### Upload File

```http
POST /files/upload
Content-Type: multipart/form-data

file: <file_data>
```

### File Types Supported

- Images: PNG, JPG, GIF, WebP
- Documents: PDF, DOC, DOCX, TXT
- Data: CSV, JSON, XML
- Archives: ZIP, RAR

### File Size Limits

- Images: 10MB
- Documents: 50MB
- Data files: 100MB

## Webhooks

### Configure Webhook

```http
POST /webhooks
{
    "url": "https://your-domain.com/webhook",
    "events": ["conversation.created", "message.received"],
    "secret": "webhook-secret"
}
```

### Webhook Events

- `conversation.created`: New conversation started
- `conversation.updated`: Conversation updated
- `message.received`: New message received
- `assistant.status_changed`: Assistant status changed
- `user.created`: New user registered
- `user.updated`: User profile updated

### Webhook Payload

```json
{
    "event": "conversation.created",
    "timestamp": "2024-01-01T00:00:00Z",
    "data": {
        "conversation_id": "uuid",
        "assistant_id": "uuid",
        "user_id": "uuid"
    }
}
``` 