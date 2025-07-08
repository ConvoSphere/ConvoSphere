# Conversations API

The Conversations API provides comprehensive conversation management capabilities including enhanced chat features like message search, export, context management, emoji reactions, and assistant switching.

## Base URL

```
/api/v1/conversations
```

## Authentication

All endpoints require authentication via JWT token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Endpoints

### Create Conversation

**POST** `/`

Create a new conversation with a specific assistant.

**Request Body:**
```json
{
  "user_id": "uuid",
  "assistant_id": "uuid",
  "title": "New Conversation"
}
```

**Response:**
```json
{
  "id": "uuid",
  "title": "New Conversation",
  "description": null,
  "user_id": "uuid",
  "assistant_id": "uuid",
  "is_active": true,
  "is_archived": false,
  "archived_at": null,
  "message_count": 0,
  "total_tokens": 0,
  "metadata": {},
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### List Conversations

**GET** `/`

Get a paginated list of conversations with optional filtering.

**Query Parameters:**
- `user_id` (optional): Filter by user ID
- `assistant_id` (optional): Filter by assistant ID
- `status` (optional): Filter by status (`active`, `archived`, `deleted`)
- `tags` (optional): Comma-separated tags to filter by
- `page` (default: 1): Page number
- `size` (default: 20, max: 100): Items per page

**Response:**
```json
{
  "conversations": [...],
  "total": 100,
  "page": 1,
  "size": 20,
  "pages": 5
}
```

### Get Conversation

**GET** `/{conversation_id}`

Get a specific conversation by ID.

**Response:**
```json
{
  "id": "uuid",
  "title": "Conversation Title",
  "description": "Description",
  "user_id": "uuid",
  "assistant_id": "uuid",
  "is_active": true,
  "is_archived": false,
  "archived_at": null,
  "message_count": 10,
  "total_tokens": 1500,
  "metadata": {},
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Update Conversation

**PUT** `/{conversation_id}`

Update conversation details.

**Request Body:**
```json
{
  "title": "Updated Title",
  "description": "Updated description",
  "metadata": {}
}
```

### Delete Conversation

**DELETE** `/{conversation_id}`

Delete a conversation permanently.

**Response:** 204 No Content

### Archive Conversation

**POST** `/{conversation_id}/archive`

Archive a conversation (soft delete).

**Response:**
```json
{
  "message": "Conversation archived"
}
```

## Message Management

### List Messages

**GET** `/{conversation_id}/messages`

Get messages in a conversation with pagination.

**Query Parameters:**
- `limit` (default: 50, max: 100): Maximum number of messages
- `offset` (default: 0): Number of messages to skip

**Response:**
```json
[
  {
    "id": "uuid",
    "content": "Message content",
    "role": "user",
    "message_type": "text",
    "conversation_id": "uuid",
    "tool_name": null,
    "tool_input": null,
    "tool_output": null,
    "tokens_used": 50,
    "model_used": "gpt-4",
    "metadata": {},
    "reactions": [],
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

### Add Message

**POST** `/{conversation_id}/messages`

Add a new message to the conversation.

**Request Body:**
```json
{
  "content": "Message content",
  "role": "user",
  "message_type": "text",
  "message_metadata": {}
}
```

## Enhanced Chat Features

### Message Search

**POST** `/{conversation_id}/messages/search`

Search messages within a conversation.

**Request Body:**
```json
{
  "query": "search term",
  "filters": {
    "role": "user",
    "message_type": "text",
    "date_from": "2024-01-01T00:00:00Z",
    "date_to": "2024-01-31T23:59:59Z"
  },
  "limit": 50,
  "offset": 0
}
```

**Response:**
```json
{
  "messages": [...],
  "total": 25,
  "query": "search term"
}
```

### Delete Message

**DELETE** `/{conversation_id}/messages/{message_id}`

Delete a message (only own messages).

**Response:** 204 No Content

### Message Reactions

#### Add Reaction

**POST** `/{conversation_id}/messages/{message_id}/reactions`

Add an emoji reaction to a message.

**Request Body:**
```json
{
  "emoji": "👍"
}
```

**Response:**
```json
{
  "id": "uuid",
  "emoji": "👍",
  "message_id": "uuid",
  "user_id": "uuid",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Remove Reaction

**DELETE** `/{conversation_id}/messages/{message_id}/reactions/{reaction_id}`

Remove an emoji reaction from a message.

**Response:** 204 No Content

### Conversation Export

**POST** `/{conversation_id}/export`

Export a conversation in various formats.

**Request Body:**
```json
{
  "format": "json",
  "include_metadata": true,
  "include_attachments": true
}
```

**Supported Formats:**
- `json`: Full conversation data in JSON format
- `markdown`: Formatted markdown with emojis and metadata
- `txt`: Plain text format
- `pdf`: PDF format (requires additional setup)

**Response:**
```json
{
  "download_url": "/api/v1/conversations/{conversation_id}/export/download/{filename}",
  "filename": "conversation_uuid_20240101_120000.json",
  "size": 1024,
  "expires_at": "2024-01-02T00:00:00Z"
}
```

#### Download Export

**GET** `/{conversation_id}/export/download/{filename}`

Download an exported conversation file.

**Response:** File download

### Conversation Context Management

#### Get Context

**GET** `/{conversation_id}/context`

Get conversation context information.

**Response:**
```json
{
  "conversation_id": "uuid",
  "context_window": 50,
  "relevant_documents": ["doc1", "doc2"],
  "assistant_context": {
    "model": "gpt-4",
    "temperature": 0.7
  },
  "user_preferences": {
    "language": "en",
    "style": "formal"
  }
}
```

#### Update Context

**PUT** `/{conversation_id}/context`

Update conversation context settings.

**Request Body:**
```json
{
  "context_window": 100,
  "relevant_documents": ["doc1", "doc2", "doc3"],
  "assistant_context": {
    "model": "gpt-4-turbo",
    "temperature": 0.5
  },
  "user_preferences": {
    "language": "de",
    "style": "casual"
  }
}
```

### Assistant Switching

#### Switch Assistant

**POST** `/{conversation_id}/switch-assistant`

Switch the active assistant for a conversation.

**Request Body:**
```json
{
  "assistant_id": "new-assistant-uuid",
  "preserve_context": true
}
```

**Response:**
```json
{
  "conversation_id": "uuid",
  "old_assistant_id": "old-assistant-uuid",
  "new_assistant_id": "new-assistant-uuid",
  "assistant_name": "New Assistant",
  "context_preserved": true,
  "message": "Switched to New Assistant assistant"
}
```

#### Get Current Assistant

**GET** `/{conversation_id}/assistant`

Get information about the current assistant.

**Response:**
```json
{
  "assistant_id": "uuid",
  "assistant_name": "Assistant Name",
  "assistant_description": "Assistant description",
  "assistant_avatar": "avatar-url",
  "assistant_capabilities": ["chat", "rag", "tools"]
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid format. Must be one of: json, markdown, pdf, txt"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Access denied"
}
```

### 404 Not Found
```json
{
  "detail": "Conversation not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Failed to export conversation"
}
```

## Data Models

### Conversation
```json
{
  "id": "uuid",
  "title": "string",
  "description": "string|null",
  "user_id": "uuid",
  "assistant_id": "uuid",
  "is_active": "boolean",
  "is_archived": "boolean",
  "archived_at": "datetime|null",
  "message_count": "integer",
  "total_tokens": "integer",
  "metadata": "object",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Message
```json
{
  "id": "uuid",
  "content": "string",
  "role": "user|assistant|system|tool",
  "message_type": "text|image|file|audio|video",
  "conversation_id": "uuid",
  "tool_name": "string|null",
  "tool_input": "object|null",
  "tool_output": "object|null",
  "tokens_used": "integer",
  "model_used": "string|null",
  "metadata": "object",
  "reactions": "array",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### MessageReaction
```json
{
  "id": "uuid",
  "emoji": "string",
  "message_id": "uuid",
  "user_id": "uuid",
  "created_at": "datetime"
}
```

## Rate Limiting

- **Message Search:** 100 requests per minute
- **Export:** 10 requests per minute
- **Reactions:** 200 requests per minute
- **Context Updates:** 50 requests per minute

## WebSocket Support

For real-time chat functionality, use the WebSocket endpoint:

```
/ws/{conversation_id}?token={jwt_token}
```

See the [WebSocket API documentation](websocket.md) for details. 