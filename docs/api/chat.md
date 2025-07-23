# Chat API

The Chat API provides endpoints for managing conversations and messages in the AI Chat Application.

## Overview

The Chat API enables real-time communication between users and AI assistants, supporting:

- Message creation and retrieval
- Conversation management
- Real-time streaming responses
- File attachments
- Message threading
- Conversation history

## Authentication

All chat endpoints require authentication. Include the JWT token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Endpoints

### Create Message

**POST** `/api/v1/chat/messages`

Create a new message in a conversation.

#### Request Body

```json
{
  "conversation_id": 123,
  "content": "Hello, how can you help me today?",
  "message_type": "user",
  "attachments": [
    {
      "file_id": "uuid-string",
      "file_name": "document.pdf",
      "file_type": "application/pdf"
    }
  ],
  "parent_message_id": null,
  "metadata": {
    "user_agent": "Mozilla/5.0...",
    "ip_address": "192.168.1.1"
  }
}
```

#### Response

```json
{
  "id": 456,
  "conversation_id": 123,
  "content": "Hello, how can you help me today?",
  "message_type": "user",
  "sender_id": 789,
  "sender_type": "user",
  "attachments": [
    {
      "id": "uuid-string",
      "file_name": "document.pdf",
      "file_type": "application/pdf",
      "file_size": 1024000,
      "url": "https://api.example.com/files/uuid-string"
    }
  ],
  "parent_message_id": null,
  "metadata": {
    "user_agent": "Mozilla/5.0...",
    "ip_address": "192.168.1.1"
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Get Message

**GET** `/api/v1/chat/messages/{message_id}`

Retrieve a specific message by ID.

#### Response

```json
{
  "id": 456,
  "conversation_id": 123,
  "content": "Hello, how can you help me today?",
  "message_type": "user",
  "sender_id": 789,
  "sender_type": "user",
  "attachments": [],
  "parent_message_id": null,
  "metadata": {},
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### List Messages

**GET** `/api/v1/chat/messages`

List messages with optional filtering and pagination.

#### Query Parameters

- `conversation_id` (optional): Filter by conversation ID
- `message_type` (optional): Filter by message type (`user`, `assistant`, `system`)
- `sender_id` (optional): Filter by sender ID
- `page` (optional): Page number (default: 1)
- `size` (optional): Page size (default: 20, max: 100)
- `sort_by` (optional): Sort field (`created_at`, `updated_at`)
- `sort_order` (optional): Sort order (`asc`, `desc`)

#### Response

```json
{
  "items": [
    {
      "id": 456,
      "conversation_id": 123,
      "content": "Hello, how can you help me today?",
      "message_type": "user",
      "sender_id": 789,
      "sender_type": "user",
      "attachments": [],
      "parent_message_id": null,
      "metadata": {},
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "page_info": {
    "page": 1,
    "size": 20,
    "total": 1,
    "pages": 1
  }
}
```

### Update Message

**PUT** `/api/v1/chat/messages/{message_id}`

Update an existing message (only for user messages).

#### Request Body

```json
{
  "content": "Updated message content",
  "metadata": {
    "edited": true,
    "edit_reason": "Typo correction"
  }
}
```

#### Response

```json
{
  "id": 456,
  "conversation_id": 123,
  "content": "Updated message content",
  "message_type": "user",
  "sender_id": 789,
  "sender_type": "user",
  "attachments": [],
  "parent_message_id": null,
  "metadata": {
    "edited": true,
    "edit_reason": "Typo correction"
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:35:00Z"
}
```

### Delete Message

**DELETE** `/api/v1/chat/messages/{message_id}`

Delete a message (only for user messages).

#### Response

- **204 No Content**: Message deleted successfully

### Stream Chat Response

**POST** `/api/v1/chat/stream`

Stream an AI response to a user message.

#### Request Body

```json
{
  "conversation_id": 123,
  "message_id": 456,
  "assistant_id": "gpt-4",
  "stream": true,
  "options": {
    "temperature": 0.7,
    "max_tokens": 1000,
    "top_p": 0.9
  }
}
```

#### Response (Server-Sent Events)

```
data: {"type": "start", "message_id": 789}

data: {"type": "content", "content": "Hello! I'm here to help you today. "}

data: {"type": "content", "content": "How can I assist you with your questions or tasks?"}

data: {"type": "end", "message_id": 789, "usage": {"prompt_tokens": 15, "completion_tokens": 20, "total_tokens": 35}}
```

### Create Conversation

**POST** `/api/v1/chat/conversations`

Create a new conversation.

#### Request Body

```json
{
  "title": "Project Discussion",
  "description": "Discussion about the new project requirements",
  "assistant_id": "gpt-4",
  "metadata": {
    "project_id": "proj-123",
    "category": "work"
  }
}
```

#### Response

```json
{
  "id": 123,
  "title": "Project Discussion",
  "description": "Discussion about the new project requirements",
  "user_id": 789,
  "assistant_id": "gpt-4",
  "status": "active",
  "message_count": 0,
  "metadata": {
    "project_id": "proj-123",
    "category": "work"
  },
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:00:00Z"
}
```

### Get Conversation

**GET** `/api/v1/chat/conversations/{conversation_id}`

Retrieve a specific conversation with its messages.

#### Query Parameters

- `include_messages` (optional): Include messages in response (default: false)
- `message_limit` (optional): Limit number of messages (default: 50)

#### Response

```json
{
  "id": 123,
  "title": "Project Discussion",
  "description": "Discussion about the new project requirements",
  "user_id": 789,
  "assistant_id": "gpt-4",
  "status": "active",
  "message_count": 5,
  "metadata": {
    "project_id": "proj-123",
    "category": "work"
  },
  "messages": [
    {
      "id": 456,
      "content": "Hello, how can you help me today?",
      "message_type": "user",
      "sender_id": 789,
      "sender_type": "user",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### List Conversations

**GET** `/api/v1/chat/conversations`

List user's conversations with pagination.

#### Query Parameters

- `status` (optional): Filter by status (`active`, `archived`, `deleted`)
- `assistant_id` (optional): Filter by assistant ID
- `page` (optional): Page number (default: 1)
- `size` (optional): Page size (default: 20, max: 100)
- `sort_by` (optional): Sort field (`created_at`, `updated_at`, `title`)
- `sort_order` (optional): Sort order (`asc`, `desc`)

#### Response

```json
{
  "items": [
    {
      "id": 123,
      "title": "Project Discussion",
      "description": "Discussion about the new project requirements",
      "user_id": 789,
      "assistant_id": "gpt-4",
      "status": "active",
      "message_count": 5,
      "metadata": {
        "project_id": "proj-123",
        "category": "work"
      },
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "page_info": {
    "page": 1,
    "size": 20,
    "total": 1,
    "pages": 1
  }
}
```

### Update Conversation

**PUT** `/api/v1/chat/conversations/{conversation_id}`

Update conversation details.

#### Request Body

```json
{
  "title": "Updated Project Discussion",
  "description": "Updated description",
  "status": "archived",
  "metadata": {
    "project_id": "proj-123",
    "category": "work",
    "priority": "high"
  }
}
```

#### Response

```json
{
  "id": 123,
  "title": "Updated Project Discussion",
  "description": "Updated description",
  "user_id": 789,
  "assistant_id": "gpt-4",
  "status": "archived",
  "message_count": 5,
  "metadata": {
    "project_id": "proj-123",
    "category": "work",
    "priority": "high"
  },
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:45:00Z"
}
```

### Delete Conversation

**DELETE** `/api/v1/chat/conversations/{conversation_id}`

Delete a conversation and all its messages.

#### Response

- **204 No Content**: Conversation deleted successfully

### Search Messages

**GET** `/api/v1/chat/search`

Search messages across conversations.

#### Query Parameters

- `q` (required): Search query
- `conversation_id` (optional): Limit search to specific conversation
- `message_type` (optional): Filter by message type
- `date_from` (optional): Search from date (ISO format)
- `date_to` (optional): Search to date (ISO format)
- `page` (optional): Page number (default: 1)
- `size` (optional): Page size (default: 20, max: 100)

#### Response

```json
{
  "items": [
    {
      "id": 456,
      "conversation_id": 123,
      "content": "Hello, how can you help me today?",
      "message_type": "user",
      "sender_id": 789,
      "sender_type": "user",
      "conversation_title": "Project Discussion",
      "created_at": "2024-01-15T10:30:00Z",
      "highlight": "Hello, how can you <em>help</em> me today?"
    }
  ],
  "page_info": {
    "page": 1,
    "size": 20,
    "total": 1,
    "pages": 1
  }
}
```

## WebSocket Endpoints

### Chat WebSocket

**WebSocket** `/api/v1/chat/ws`

Real-time chat connection for streaming responses and live updates.

#### Connection

```javascript
const ws = new WebSocket('wss://api.example.com/api/v1/chat/ws');

// Authenticate with token
ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'auth',
    token: 'your-jwt-token'
  }));
};
```

#### Message Types

**Send Message**
```json
{
  "type": "send_message",
  "data": {
    "conversation_id": 123,
    "content": "Hello, AI!",
    "message_type": "user"
  }
}
```

**Stream Response**
```json
{
  "type": "stream_response",
  "data": {
    "conversation_id": 123,
    "message_id": 456,
    "assistant_id": "gpt-4"
  }
}
```

**Typing Indicator**
```json
{
  "type": "typing",
  "data": {
    "conversation_id": 123,
    "is_typing": true
  }
}
```

#### Response Events

**Message Received**
```json
{
  "type": "message_received",
  "data": {
    "message": {
      "id": 456,
      "content": "Hello, AI!",
      "message_type": "user",
      "sender_id": 789,
      "created_at": "2024-01-15T10:30:00Z"
    }
  }
}
```

**Stream Content**
```json
{
  "type": "stream_content",
  "data": {
    "message_id": 789,
    "content": "Hello! I'm here to help you.",
    "is_complete": false
  }
}
```

**Stream Complete**
```json
{
  "type": "stream_complete",
  "data": {
    "message_id": 789,
    "usage": {
      "prompt_tokens": 15,
      "completion_tokens": 20,
      "total_tokens": 35
    }
  }
}
```

## Error Responses

### Common Error Codes

- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Missing or invalid authentication
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Validation error
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server error

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request data",
    "details": [
      {
        "field": "content",
        "message": "Content cannot be empty"
      }
    ]
  }
}
```

## Rate Limiting

Chat endpoints are rate-limited to prevent abuse:

- **Message Creation**: 100 requests per minute per user
- **Streaming**: 10 concurrent streams per user
- **Search**: 50 requests per minute per user

Rate limit headers are included in responses:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248600
```

## Pagination

List endpoints support pagination with the following parameters:

- `page`: Page number (1-based)
- `size`: Items per page (1-100)
- `sort_by`: Sort field
- `sort_order`: Sort direction (`asc` or `desc`)

Pagination metadata is included in responses:

```json
{
  "page_info": {
    "page": 1,
    "size": 20,
    "total": 100,
    "pages": 5
  }
}
```

## File Attachments

Messages can include file attachments. Files must be uploaded separately using the File Upload API before being referenced in messages.

### Attachment Format

```json
{
  "attachments": [
    {
      "file_id": "uuid-string",
      "file_name": "document.pdf",
      "file_type": "application/pdf",
      "file_size": 1024000
    }
  ]
}
```

## Metadata

Messages and conversations support custom metadata for extensibility:

```json
{
  "metadata": {
    "user_agent": "Mozilla/5.0...",
    "ip_address": "192.168.1.1",
    "session_id": "session-123",
    "custom_field": "custom_value"
  }
}
```

## Examples

### Complete Chat Flow

1. **Create Conversation**
```bash
curl -X POST "https://api.example.com/api/v1/chat/conversations" \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Help Session",
    "assistant_id": "gpt-4"
  }'
```

2. **Send Message**
```bash
curl -X POST "https://api.example.com/api/v1/chat/messages" \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": 123,
    "content": "What is the capital of France?",
    "message_type": "user"
  }'
```

3. **Stream Response**
```bash
curl -X POST "https://api.example.com/api/v1/chat/stream" \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": 123,
    "message_id": 456,
    "assistant_id": "gpt-4",
    "stream": true
  }'
```

### WebSocket Example

```javascript
const ws = new WebSocket('wss://api.example.com/api/v1/chat/ws');

ws.onopen = () => {
  // Authenticate
  ws.send(JSON.stringify({
    type: 'auth',
    token: 'your-jwt-token'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch (data.type) {
    case 'message_received':
      console.log('New message:', data.data.message);
      break;
    case 'stream_content':
      console.log('Stream content:', data.data.content);
      break;
    case 'stream_complete':
      console.log('Stream complete:', data.data.usage);
      break;
  }
};

// Send a message
ws.send(JSON.stringify({
  type: 'send_message',
  data: {
    conversation_id: 123,
    content: 'Hello, AI!',
    message_type: 'user'
  }
}));
```