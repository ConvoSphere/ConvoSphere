# API Overview

This document provides an overview of the ConvoSphere API architecture and available endpoints.

## 🏗️ API Architecture

ConvoSphere uses a RESTful API built with FastAPI, providing:

- **RESTful Design**: Standard HTTP methods and status codes
- **OpenAPI Documentation**: Auto-generated API documentation
- **JWT Authentication**: Secure token-based authentication
- **Rate Limiting**: Protection against abuse
- **WebSocket Support**: Real-time communication

## 📋 API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - User logout
- `GET /auth/me` - Get current user info

### Conversations
- `GET /conversations` - List user conversations
- `POST /conversations` - Create new conversation
- `GET /conversations/{id}` - Get conversation details
- `PUT /conversations/{id}` - Update conversation
- `DELETE /conversations/{id}` - Delete conversation

### Messages
- `GET /conversations/{id}/messages` - Get conversation messages
- `POST /conversations/{id}/messages` - Send message
- `PUT /messages/{id}` - Update message
- `DELETE /messages/{id}` - Delete message

### Knowledge Base
- `GET /documents` - List user documents
- `POST /documents` - Upload document
- `GET /documents/{id}` - Get document details
- `DELETE /documents/{id}` - Delete document
- `POST /documents/search` - Search documents

### User Management
- `GET /users` - List users (admin only)
- `POST /users` - Create user (admin only)
- `GET /users/{id}` - Get user details
- `PUT /users/{id}` - Update user
- `DELETE /users/{id}` - Delete user (admin only)

### System
- `GET /health` - Health check
- `GET /metrics` - System metrics
- `GET /docs` - API documentation

## 🔐 Authentication

All API endpoints require authentication except `/auth/login` and `/health`.

### JWT Token Format
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Request Headers
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

## 📊 Response Format

### Success Response
```json
{
  "success": true,
  "data": {
    // Response data
  },
  "message": "Operation successful"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "error description"
    }
  }
}
```

## 🚀 Getting Started

### 1. Authentication
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'
```

### 2. Using the API
```bash
curl -X GET "http://localhost:8000/conversations" \
  -H "Authorization: Bearer <access_token>"
```

### 3. WebSocket Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/ws?token=<access_token>');
```

## 📚 Documentation

- **Interactive API Docs**: Visit `/docs` for Swagger UI
- **OpenAPI Schema**: Available at `/openapi.json`
- **Postman Collection**: Available in the project repository

## 🔧 Development

### Local Development
```bash
# Start the API server
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Testing
```bash
# Run API tests
pytest tests/api/ -v

# Run with coverage
pytest tests/api/ --cov=app --cov-report=html
```

## 📈 Monitoring

The API includes built-in monitoring:

- **Health Checks**: `/health` endpoint
- **Metrics**: Prometheus-compatible metrics at `/metrics`
- **Logging**: Structured logging for all requests
- **Tracing**: Distributed tracing support

## 🔒 Security

- **Rate Limiting**: Configurable per endpoint
- **Input Validation**: Automatic request validation
- **CORS**: Configurable cross-origin requests
- **Security Headers**: Automatic security header injection