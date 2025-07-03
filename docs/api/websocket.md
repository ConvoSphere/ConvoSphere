# WebSocket API

## Overview

The WebSocket API enables real-time communication for chat and notifications. Authentication is required via token.

## Connection

- **URL:** `ws://localhost:8000/api/v1/ws/{conversation_id}`
- **Protocol:** WebSocket
- **Authentication:** Pass the access token as a query parameter or in the initial message.
  - Example: `ws://localhost:8000/api/v1/ws/{conversation_id}?token=<access_token>`

## Events

### Client → Server
- **Send message:**
  ```json
  {
    "type": "message",
    "content": "Hello, assistant!"
  }
  ```
- **Typing indicator:**
  ```json
  {
    "type": "typing"
  }
  ```

### Server → Client
- **Receive message:**
  ```json
  {
    "type": "message",
    "sender": "assistant",
    "content": "Hello, how can I help you?",
    "timestamp": "2024-01-01T00:00:00Z"
  }
  ```
- **System notification:**
  ```json
  {
    "type": "system",
    "message": "User joined the conversation."
  }
  ```
- **Error:**
  ```json
  {
    "type": "error",
    "message": "Authentication failed."
  }
  ```

## Error Codes
- 4001: Authentication failed
- 4002: Conversation not found or access denied
- 4000: Connection error

## Usage Notes
- The connection will be closed if authentication fails or the conversation is not found.
- All messages must be sent as JSON objects. 