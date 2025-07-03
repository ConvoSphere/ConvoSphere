# Conversations API

## Overview

Conversation endpoints allow you to start, manage, and interact with conversations with assistants. Messages, attachments, and conversation history are supported.

## Endpoints

### GET /conversations
List user conversations.

**Query Parameters:**
- `page`: Page number (default: 1)
- `size`: Page size (default: 20)
- `assistant_id`: Filter by assistant

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "title": "Conversation Title",
      "assistant_id": "uuid",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 10,
  "page": 1,
  "size": 20,
  "pages": 1
}
```
**Errors:**
- 401 Unauthorized: Invalid token

---

### POST /conversations
Start a new conversation.

**Request:**
```json
{
  "assistant_id": "uuid",
  "title": "Conversation Title",
  "initial_message": "Hello, how can you help me?"
}
```
**Response:**
```json
{
  "id": "uuid",
  "title": "Conversation Title",
  "assistant_id": "uuid",
  "created_at": "2024-01-01T00:00:00Z"
}
```
**Errors:**
- 400 Bad Request: Validation error
- 401 Unauthorized: Invalid token

---

### GET /conversations/{conversation_id}
Get conversation details and messages.

**Response:**
```json
{
  "id": "uuid",
  "title": "Conversation Title",
  "assistant_id": "uuid",
  "messages": [
    {
      "id": "uuid",
      "sender": "user",
      "content": "Hello, how can you help me?",
      "timestamp": "2024-01-01T00:00:00Z"
    }
  ]
}
```
**Errors:**
- 404 Not Found: Conversation does not exist

---

### POST /conversations/{conversation_id}/messages
Send a message to a conversation.

**Request:**
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
**Response:**
```json
{
  "id": "uuid",
  "sender": "user",
  "content": "User message",
  "timestamp": "2024-01-01T00:00:00Z"
}
```
**Errors:**
- 400 Bad Request: Validation error
- 404 Not Found: Conversation does not exist

---

### DELETE /conversations/{conversation_id}
Delete a conversation.

**Response:**
```json
{
  "message": "Conversation deleted successfully"
}
```
**Errors:**
- 404 Not Found: Conversation does not exist 