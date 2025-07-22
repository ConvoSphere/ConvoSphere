# Frontend-Backend Communication Configuration

This document describes how to configure the communication between the frontend (React) and backend (FastAPI) components of the AI Assistant Platform.

## Overview

The platform supports both HTTP/REST API communication and WebSocket connections for real-time features. All communication endpoints are configurable through environment variables, making the system flexible for different deployment scenarios.

## Environment Variables

### Backend Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `BACKEND_URL` | `http://localhost:8000` | Backend URL for frontend communication |
| `WS_URL` | `ws://localhost:8000` | WebSocket URL for frontend communication |
| `FRONTEND_URL` | `http://localhost:5173` | Frontend URL for CORS configuration |
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:3000,http://localhost:8081` | Comma-separated list of allowed CORS origins |

### Frontend Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `/api` (proxy) | Backend API URL |
| `VITE_WS_URL` | `ws://localhost:8000` (dev) / `ws://${host}` (prod) | WebSocket URL |

## Configuration Scenarios

### 1. Local Development

```bash
# .env
BACKEND_URL=http://localhost:8000
WS_URL=ws://localhost:8000
FRONTEND_URL=http://localhost:5173
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Frontend uses Vite proxy for /api -> http://localhost:8000
VITE_API_URL=/api
VITE_WS_URL=ws://localhost:8000
```

### 2. Docker Compose

```yaml
# docker-compose.yml
services:
  backend:
    environment:
      - BACKEND_URL=http://backend:8000
      - WS_URL=ws://backend:8000
      - FRONTEND_URL=http://frontend:8080
      - CORS_ORIGINS=http://frontend:8080,http://localhost:8081
  
  frontend:
    environment:
      - VITE_API_URL=http://backend:8000
      - VITE_WS_URL=ws://backend:8000
```

### 3. Production Deployment

```bash
# .env
BACKEND_URL=https://api.yourdomain.com
WS_URL=wss://api.yourdomain.com
FRONTEND_URL=https://app.yourdomain.com
CORS_ORIGINS=https://app.yourdomain.com

# Frontend
VITE_API_URL=https://api.yourdomain.com
VITE_WS_URL=wss://api.yourdomain.com
```

## API Endpoints

### HTTP/REST API

The frontend communicates with the backend through these main endpoints:

- **Authentication**: `/api/v1/auth/*`
- **Users**: `/api/v1/users/*`
- **Conversations**: `/api/v1/conversations/*`
- **Chat**: `/api/v1/chat/*`
- **Tools**: `/api/v1/tools/*`
- **Assistants**: `/api/v1/assistants/*`
- **Knowledge**: `/api/v1/knowledge/*`
- **Health**: `/api/v1/health/*`

### WebSocket Endpoints

- **Chat**: `/api/v1/ws/chat` - Real-time chat functionality
- **Notifications**: `/api/v1/ws/notifications` - System notifications

## Frontend Configuration

The frontend uses a centralized configuration system in `src/config/index.ts`:

```typescript
export const config = {
  apiUrl: import.meta.env.VITE_API_URL || '/api',
  wsUrl: import.meta.env.VITE_WS_URL || 
    (import.meta.env.DEV ? 'ws://localhost:8000' : `ws://${window.location.host}`),
  
  wsEndpoints: {
    chat: '/api/v1/ws/chat',
    notifications: '/api/v1/ws/notifications',
  },
  
  apiEndpoints: {
    auth: '/api/v1/auth',
    users: '/api/v1/users',
    // ... other endpoints
  },
};
```

## CORS Configuration

The backend automatically configures CORS based on the `CORS_ORIGINS` environment variable. Multiple origins can be specified as a comma-separated list.

### Example CORS Configuration

```python
# Backend automatically handles CORS based on CORS_ORIGINS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,https://app.yourdomain.com
```

## WebSocket Authentication

WebSocket connections require authentication via JWT token passed as a query parameter:

```
ws://backend:8000/api/v1/ws/chat?token=<jwt_token>
```

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure `CORS_ORIGINS` includes your frontend URL
2. **WebSocket Connection Failed**: Check `WS_URL` and ensure the backend is accessible
3. **API Calls Failing**: Verify `VITE_API_URL` points to the correct backend
4. **Docker Network Issues**: Use service names (e.g., `backend:8000`) in Docker Compose

### Debug Mode

Enable debug mode to see detailed connection information:

```bash
VITE_ENABLE_DEBUG=true
```

### Health Checks

Use the health endpoint to verify backend connectivity:

```bash
curl http://backend:8000/api/v1/health
```

## Security Considerations

1. **HTTPS/WSS in Production**: Always use secure connections in production
2. **CORS Restrictions**: Limit CORS origins to trusted domains
3. **Token Validation**: WebSocket tokens are validated on the backend
4. **Rate Limiting**: API endpoints include rate limiting protection

## Migration Guide

### From Hardcoded URLs

If you're migrating from hardcoded URLs:

1. Set the appropriate environment variables
2. Update your `.env` file
3. Restart the services
4. Test the communication

### From Proxy-Only Configuration

If you're moving from Vite proxy to direct API calls:

1. Set `VITE_API_URL` to the full backend URL
2. Update CORS configuration
3. Test all API endpoints 