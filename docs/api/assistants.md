# Assistants API

## Overview

Assistant endpoints allow you to create, list, update, and delete AI assistants. Assistants can be filtered and configured with various options.

## Endpoints

### GET /assistants
List all assistants.

**Query Parameters:**
- `page`: Page number (default: 1)
- `size`: Page size (default: 20)
- `status`: Filter by status (active, inactive, draft)
- `category`: Filter by category

**Response:**
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
**Errors:**
- 401 Unauthorized: Invalid token

---

### POST /assistants
Create a new assistant.

**Request:**
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
**Response:**
```json
{
  "id": "uuid",
  "name": "My Assistant",
  "status": "active"
}
```
**Errors:**
- 400 Bad Request: Validation error
- 401 Unauthorized: Invalid token

---

### GET /assistants/{assistant_id}
Get details for a specific assistant.

**Response:**
```json
{
  "id": "uuid",
  "name": "My Assistant",
  "description": "A helpful AI assistant",
  "personality": "Friendly and professional",
  "status": "active",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```
**Errors:**
- 404 Not Found: Assistant does not exist

---

### PUT /assistants/{assistant_id}
Update an assistant.

**Request:**
```json
{
  "name": "Updated Name",
  "description": "Updated description"
}
```
**Response:**
```json
{
  "id": "uuid",
  "name": "Updated Name",
  "description": "Updated description"
}
```
**Errors:**
- 400 Bad Request: Validation error
- 404 Not Found: Assistant does not exist

---

### DELETE /assistants/{assistant_id}
Delete an assistant.

**Response:**
```json
{
  "message": "Assistant deleted successfully"
}
```
**Errors:**
- 404 Not Found: Assistant does not exist 