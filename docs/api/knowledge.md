# Knowledge Base API

## Overview

Knowledge Base endpoints allow you to upload, manage, and search documents for use by assistants.

## Endpoints

### POST /knowledge/documents
Upload a new document.

**Request:**
Multipart/form-data with file upload.

**Response:**
```json
{
  "id": "uuid",
  "name": "document.pdf",
  "status": "processing"
}
```
**Errors:**
- 400 Bad Request: Invalid file or format

---

### GET /knowledge/documents
List all uploaded documents.

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "document.pdf",
      "status": "ready",
      "uploaded_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

### GET /knowledge/documents/{document_id}
Get details for a specific document.

**Response:**
```json
{
  "id": "uuid",
  "name": "document.pdf",
  "status": "ready",
  "uploaded_at": "2024-01-01T00:00:00Z",
  "size": 123456
}
```
**Errors:**
- 404 Not Found: Document does not exist

---

### DELETE /knowledge/documents/{document_id}
Delete a document.

**Response:**
```json
{
  "message": "Document deleted successfully"
}
```
**Errors:**
- 404 Not Found: Document does not exist

---

### GET /knowledge/search
Search the knowledge base.

**Query Parameters:**
- `query`: Search string
- `limit`: Max results (default: 10)

**Response:**
```json
{
  "results": [
    {
      "document_id": "uuid",
      "snippet": "...text...",
      "score": 0.98
    }
  ]
}
```
**Errors:**
- 400 Bad Request: Missing or invalid query 