# Authentication API

## Overview

Authentication is required for most API endpoints. The platform uses JWT tokens for stateless authentication. Obtain tokens via login and include them in the `Authorization` header for all requests.

## Endpoints

### POST /auth/login
Authenticate user and receive access/refresh tokens.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password"
}
```
**Response:**
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "expires_in": 1800
}
```
**Errors:**
- 401 Unauthorized: Invalid credentials

---

### POST /auth/refresh
Refresh the access token using a valid refresh token.

**Request:**
```json
{
  "refresh_token": "..."
}
```
**Response:**
```json
{
  "access_token": "...",
  "token_type": "bearer",
  "expires_in": 1800
}
```
**Errors:**
- 401 Unauthorized: Invalid or expired refresh token

---

### POST /auth/logout
Invalidate the current access and refresh tokens.

**Request:**
```json
{
  "refresh_token": "..."
}
```
**Response:**
```json
{
  "message": "Logged out successfully"
}
```
**Errors:**
- 401 Unauthorized: Invalid token

---

### POST /auth/register
Register a new user account.

**Request:**
```json
{
  "name": "John Doe",
  "email": "user@example.com",
  "password": "password"
}
```
**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "John Doe"
}
```
**Errors:**
- 400 Bad Request: Validation error
- 409 Conflict: Email already registered

---

## Usage Notes
- Include the access token in the `Authorization` header for all protected endpoints:
  ```http
  Authorization: Bearer <access_token>
  ```
- Tokens expire after a set time (default: 30 minutes).
- Use the refresh token to obtain a new access token before expiry.
- Logout will invalidate both tokens. 