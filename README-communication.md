# Frontend-Backend Communication Configuration

This document provides a quick overview of the new robust and configurable frontend-backend communication system.

## 🚀 Quick Start

### 1. Local Development

```bash
# Copy the example environment file
cp env.local.example .env.local

# Start the services
make docker-up

# Test the communication
make test-communication
```

### 2. Docker Compose

```bash
# The docker-compose.yml is already configured with the new variables
docker-compose up -d

# Test the communication
make test-communication
```

## 🔧 Configuration

### Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `BACKEND_URL` | Backend API URL | `http://localhost:8000` |
| `WS_URL` | WebSocket URL | `ws://localhost:8000` |
| `FRONTEND_URL` | Frontend URL for CORS | `http://localhost:5173` |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:5173,http://localhost:3000,http://localhost:8081` |
| `VITE_API_URL` | Frontend API URL | `/api` (proxy) |
| `VITE_WS_URL` | Frontend WebSocket URL | `ws://localhost:8000` |

### Configuration Scenarios

#### Local Development
```bash
BACKEND_URL=http://localhost:8000
WS_URL=ws://localhost:8000
VITE_API_URL=/api  # Uses Vite proxy
VITE_WS_URL=ws://localhost:8000
```

#### Docker Compose
```bash
BACKEND_URL=http://backend:8000
WS_URL=ws://backend:8000
VITE_API_URL=http://backend:8000
VITE_WS_URL=ws://backend:8000
```

#### Production
```bash
BACKEND_URL=https://api.yourdomain.com
WS_URL=wss://api.yourdomain.com
VITE_API_URL=https://api.yourdomain.com
VITE_WS_URL=wss://api.yourdomain.com
```

## 🧪 Testing

### Manual Testing

```bash
# Test the communication configuration
make test-communication

# Or run the script directly
./scripts/test-communication.sh
```

### What the Test Checks

1. **Environment Variables**: Validates that all required variables are set
2. **Backend Health**: Checks if the backend is accessible
3. **API Endpoints**: Tests key API endpoints
4. **WebSocket Connection**: Verifies WebSocket connectivity
5. **CORS Configuration**: Checks CORS headers
6. **Docker Compose**: Validates Docker configuration

## 📁 File Structure

```
├── backend/app/core/config.py          # Backend configuration
├── frontend-react/src/config/index.ts  # Frontend configuration
├── frontend-react/src/services/api.ts  # API service
├── frontend-react/src/services/chat.ts # WebSocket service
├── docker-compose.yml                  # Docker configuration
├── env.example                         # Environment variables example
├── env.local.example                   # Local development example
├── scripts/test-communication.sh       # Test script
└── docs/configuration/frontend-backend-communication.md # Full documentation
```

## 🔄 Migration from Old Configuration

### Before (Hardcoded)
```typescript
// Old WebSocket configuration
const wsUrl = process.env.NODE_ENV === 'development'
  ? `ws://localhost:8000/api/v1/ws/chat?token=${token}`
  : `ws://${window.location.host}/api/v1/ws/chat?token=${token}`;
```

### After (Configurable)
```typescript
// New WebSocket configuration
import config from '../config';
const wsUrl = `${config.wsUrl}${config.wsEndpoints.chat}?token=${token}`;
```

## 🛠️ Troubleshooting

### Common Issues

1. **CORS Errors**
   ```bash
   # Check CORS configuration
   curl -H "Origin: http://localhost:5173" -I http://localhost:8000/api/v1/health
   ```

2. **WebSocket Connection Failed**
   ```bash
   # Test WebSocket endpoint
   websocat ws://localhost:8000/api/v1/ws/chat
   ```

3. **API Calls Failing**
   ```bash
   # Check API endpoint
   curl http://localhost:8000/api/v1/health
   ```

### Debug Mode

Enable debug mode to see detailed connection information:

```bash
VITE_ENABLE_DEBUG=true
```

## 📚 Documentation

For detailed documentation, see:
- [Full Configuration Guide](docs/configuration/frontend-backend-communication.md)
- [API Documentation](docs/api/overview.md)
- [Docker Deployment](docs/deployment/docker.md)

## 🤝 Contributing

When making changes to the communication configuration:

1. Update the environment variables in `env.example`
2. Test with `make test-communication`
3. Update the documentation
4. Test in different environments (local, Docker, production)

## 🔒 Security

- Always use HTTPS/WSS in production
- Limit CORS origins to trusted domains
- Validate WebSocket tokens on the backend
- Use environment variables for sensitive configuration 