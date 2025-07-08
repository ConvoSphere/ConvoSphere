# Chat API

The Chat API provides real-time chat functionality through WebSocket connections and REST endpoints for message management and assistant switching.

## Base URL

```
/api/v1/chat
```

## Authentication

All endpoints require authentication via JWT token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## WebSocket Endpoints

### Real-time Chat

**WebSocket** `/ws/{conversation_id}`

Connect to a conversation for real-time messaging.

**Query Parameters:**
- `token` (optional): JWT token for authentication

**Connection:**
```javascript
const ws = new WebSocket(`ws://localhost:8000/api/v1/chat/ws/${conversationId}?token=${jwtToken}`);
```

**Connection Confirmation:**
```json
{
  "type": "connection_established",
  "data": {
    "conversation_id": "uuid",
    "message": "Connected to chat"
  }
}
```

### Message Types

#### Send Message
```json
{
  "type": "message",
  "content": "Hello, how can you help me?",
  "user_id": "uuid"
}
```

#### Typing Indicator
```json
{
  "type": "typing",
  "user_id": "uuid",
  "is_typing": true
}
```

#### Join Conversation
```json
{
  "type": "join",
  "user_id": "uuid",
  "username": "John Doe"
}
```

### Received Message Types

#### Message Received
```json
{
  "type": "message",
  "message": {
    "id": "uuid",
    "content": "I can help you with various tasks!",
    "role": "assistant",
    "message_type": "text",
    "timestamp": "2024-01-01T00:00:00Z",
    "metadata": {}
  }
}
```

#### Typing Indicator
```json
{
  "type": "typing",
  "user_id": "uuid",
  "is_typing": true
}
```

#### User Joined
```json
{
  "type": "user_joined",
  "user_id": "uuid",
  "username": "John Doe"
}
```

#### Error
```json
{
  "type": "error",
  "message": "User ID required"
}
```

## REST Endpoints

### Create Conversation

**POST** `/conversations`

Create a new conversation with a specific assistant.

**Request Body:**
```json
{
  "assistant_id": "uuid",
  "title": "New Conversation"
}
```

**Response:**
```json
{
  "id": "uuid",
  "title": "New Conversation",
  "assistant_id": "uuid",
  "assistant_name": "Assistant Name",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "message_count": 0
}
```

### Get Conversation Messages

**GET** `/conversations/{conversation_id}/messages`

Get all messages in a conversation.

**Response:**
```json
[
  {
    "id": "uuid",
    "content": "Hello!",
    "role": "user",
    "message_type": "text",
    "timestamp": "2024-01-01T00:00:00Z",
    "metadata": null
  },
  {
    "id": "uuid",
    "content": "Hi there! How can I help you?",
    "role": "assistant",
    "message_type": "text",
    "timestamp": "2024-01-01T00:00:01Z",
    "metadata": null
  }
]
```

### Send Message

**POST** `/conversations/{conversation_id}/messages`

Send a message to a conversation and get AI response.

**Request Body:**
```json
{
  "content": "What's the weather like?",
  "message_type": "text"
}
```

**Query Parameters:**
- `use_rag` (default: true): Use RAG for enhanced responses
- `use_tools` (default: true): Enable tool execution
- `max_context_chunks` (default: 5): Maximum context chunks for RAG

**Response:**
```json
{
  "id": "uuid",
  "content": "I don't have access to real-time weather data, but I can help you find weather information through available tools.",
  "role": "assistant",
  "message_type": "text",
  "timestamp": "2024-01-01T00:00:00Z",
  "metadata": {
    "model_used": "gpt-4",
    "tokens_used": 45,
    "context_used": true
  }
}
```

## Assistant Switching

### Switch Assistant

**POST** `/conversations/{conversation_id}/switch-assistant`

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

### Get Current Assistant

**GET** `/conversations/{conversation_id}/assistant`

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
  "detail": "Failed to switch assistant"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
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
  "detail": "Failed to send message"
}
```

## Data Models

### MessageCreate
```json
{
  "content": "string",
  "message_type": "text"
}
```

### MessageResponse
```json
{
  "id": "uuid",
  "content": "string",
  "role": "user|assistant|system|tool",
  "message_type": "text|image|file|audio|video",
  "timestamp": "datetime",
  "metadata": "object|null"
}
```

### ConversationCreate
```json
{
  "assistant_id": "uuid",
  "title": "string|null"
}
```

### ConversationResponse
```json
{
  "id": "uuid",
  "title": "string",
  "assistant_id": "uuid",
  "assistant_name": "string",
  "created_at": "datetime",
  "updated_at": "datetime",
  "message_count": "integer"
}
```

### AssistantSwitchRequest
```json
{
  "assistant_id": "uuid",
  "preserve_context": "boolean"
}
```

### AssistantSwitchResponse
```json
{
  "conversation_id": "uuid",
  "old_assistant_id": "uuid",
  "new_assistant_id": "uuid",
  "assistant_name": "string",
  "context_preserved": "boolean",
  "message": "string"
}
```

## WebSocket Event Handling

### JavaScript Example
```javascript
const ws = new WebSocket(`ws://localhost:8000/api/v1/chat/ws/${conversationId}?token=${jwtToken}`);

ws.onopen = function(event) {
  console.log('Connected to chat');
};

ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  
  switch(data.type) {
    case 'connection_established':
      console.log('Connection established:', data.data.message);
      break;
      
    case 'message':
      displayMessage(data.message);
      break;
      
    case 'typing':
      showTypingIndicator(data.user_id, data.is_typing);
      break;
      
    case 'user_joined':
      showUserJoined(data.user_id, data.username);
      break;
      
    case 'error':
      console.error('Error:', data.message);
      break;
  }
};

ws.onclose = function(event) {
  console.log('Disconnected from chat');
};

// Send a message
function sendMessage(content) {
  ws.send(JSON.stringify({
    type: 'message',
    content: content,
    user_id: currentUserId
  }));
}

// Send typing indicator
function sendTypingIndicator(isTyping) {
  ws.send(JSON.stringify({
    type: 'typing',
    user_id: currentUserId,
    is_typing: isTyping
  }));
}
```

## Rate Limiting

- **WebSocket connections:** 10 per user
- **Message sending:** 100 messages per minute
- **Assistant switching:** 10 switches per minute

## Best Practices

1. **Reconnection:** Implement automatic reconnection with exponential backoff
2. **Error Handling:** Always handle WebSocket errors and connection failures
3. **Typing Indicators:** Send typing indicators to improve user experience
4. **Message Validation:** Validate message content before sending
5. **Context Preservation:** Consider whether to preserve context when switching assistants

## Integration with Frontend

The Chat API is designed to work seamlessly with the React frontend. The frontend automatically handles:

- WebSocket connection management
- Message sending and receiving
- Typing indicators
- Assistant switching
- Error handling and reconnection

See the [Frontend Chat Component documentation](../frontend/chat.md) for implementation details. 