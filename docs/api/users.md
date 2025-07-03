# Users API

## Overview

User management endpoints allow you to retrieve, update, and manage user accounts. Some endpoints require admin privileges.

## Endpoints

### GET /users/me
Get the current user's profile.

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user",
  "created_at": "2024-01-01T00:00:00Z"
}
```
**Errors:**
- 401 Unauthorized: Invalid or missing token

---

### PUT /users/me
Update the current user's profile.

**Request:**
```json
{
  "name": "Jane Doe",
  "email": "new@example.com"
}
```
**Response:**
```json
{
  "id": "uuid",
  "email": "new@example.com",
  "name": "Jane Doe"
}
```
**Errors:**
- 400 Bad Request: Validation error
- 401 Unauthorized: Invalid token

---

### GET /users
List all users (admin only).

**Response:**
```json
{
  "items": [
    { "id": "uuid", "email": "user@example.com", "name": "John Doe", "role": "user" }
  ],
  "total": 1
}
```
**Errors:**
- 403 Forbidden: Admin privileges required

---

### GET /users/{user_id}
Get details for a specific user (admin only).

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user"
}
```
**Errors:**
- 404 Not Found: User does not exist
- 403 Forbidden: Admin privileges required

---

### PUT /users/{user_id}
Update a user (admin only).

**Request:**
```json
{
  "name": "Jane Doe",
  "email": "new@example.com",
  "role": "admin"
}
```
**Response:**
```json
{
  "id": "uuid",
  "email": "new@example.com",
  "name": "Jane Doe",
  "role": "admin"
}
```
**Errors:**
- 400 Bad Request: Validation error
- 404 Not Found: User does not exist
- 403 Forbidden: Admin privileges required

---

### DELETE /users/{user_id}
Delete a user (admin only).

**Response:**
```json
{
  "message": "User deleted successfully"
}
```
**Errors:**
- 404 Not Found: User does not exist
- 403 Forbidden: Admin privileges required 