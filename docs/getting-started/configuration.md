# Configuration Guide

## Overview

This guide explains how to configure the AI Assistant Platform for different environments and use cases.

## Environment Variables

### Core Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `APP_NAME` | Application name | "AI Assistant Platform" | No |
| `DEBUG` | Debug mode | false | No |
| `ENVIRONMENT` | Environment (dev/prod) | "development" | No |
| `HOST` | Server host | "0.0.0.0" | No |
| `PORT` | Server port | 8000 | No |

### Database Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string | - | Yes |
| `DB_POOL_SIZE` | Connection pool size | 10 | No |
| `DB_MAX_OVERFLOW` | Max overflow connections | 20 | No |

### Redis Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `REDIS_URL` | Redis connection string | - | Yes |
| `REDIS_POOL_SIZE` | Redis pool size | 10 | No |

### Security Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SECRET_KEY` | Application secret key | - | Yes |
| `JWT_SECRET_KEY` | JWT signing key | - | Yes |
| `JWT_ALGORITHM` | JWT algorithm | "HS256" | No |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry | 30 | No |

### AI Provider Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API key | - | No |
| `ANTHROPIC_API_KEY` | Anthropic API key | - | No |
| `DEFAULT_AI_MODEL` | Default model | "gpt-4" | No |

## Configuration Files

### Environment File (.env)

```bash
# Core
APP_NAME=AI Assistant Platform
DEBUG=true
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/chatassistant
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

# Redis
REDIS_URL=redis://localhost:6379
REDIS_POOL_SIZE=10

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DEFAULT_AI_MODEL=gpt-4
```

### Production Configuration

```bash
# Core
APP_NAME=AI Assistant Platform
DEBUG=false
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=postgresql://prod_user:secure_pass@db.example.com:5432/chatassistant
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40

# Redis
REDIS_URL=redis://redis.example.com:6379
REDIS_POOL_SIZE=20

# Security
SECRET_KEY=very-long-secure-secret-key
JWT_SECRET_KEY=very-long-jwt-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# AI Providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DEFAULT_AI_MODEL=gpt-4
```

## Configuration Management

### Development Environment

```python
# config/development.py
from app.core.config import Settings

class DevelopmentSettings(Settings):
    debug: bool = True
    environment: str = "development"
    database_url: str = "postgresql://dev_user:dev_pass@localhost:5432/chatassistant_dev"
    redis_url: str = "redis://localhost:6379"
```

### Production Environment

```python
# config/production.py
from app.core.config import Settings

class ProductionSettings(Settings):
    debug: bool = False
    environment: str = "production"
    database_url: str = "postgresql://prod_user:secure_pass@db.example.com:5432/chatassistant"
    redis_url: str = "redis://redis.example.com:6379"
```

## Security Best Practices

### Secret Management

1. **Use Environment Variables**: Never hardcode secrets
2. **Rotate Keys Regularly**: Change secrets periodically
3. **Use Strong Keys**: Generate cryptographically secure keys
4. **Limit Access**: Restrict access to configuration files

### Key Generation

```bash
# Generate secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate JWT secret
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Database Configuration

### Connection Pooling

```python
# Optimize for your workload
DB_POOL_SIZE=20          # High traffic
DB_MAX_OVERFLOW=40       # Peak load handling
```

### SSL Configuration

```bash
# Enable SSL for production
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
```

## Redis Configuration

### Persistence

```bash
# Enable persistence for production
REDIS_URL=redis://localhost:6379/0
```

### Clustering

```bash
# Redis cluster configuration
REDIS_URL=redis://node1:6379,node2:6379,node3:6379
```

## Monitoring Configuration

### Health Checks

```python
# Custom health check endpoints
HEALTH_CHECK_INTERVAL=30
HEALTH_CHECK_TIMEOUT=5
```

### Logging

```python
# Logging configuration
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
LOG_FORMAT="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}"
```

## Performance Tuning

### Connection Limits

```bash
# Database connections
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40

# Redis connections
REDIS_POOL_SIZE=20
```

### Timeouts

```bash
# Request timeouts
REQUEST_TIMEOUT=30
DATABASE_TIMEOUT=10
REDIS_TIMEOUT=5
```

## Troubleshooting

### Common Configuration Issues

1. **Database Connection**: Check DATABASE_URL format
2. **Redis Connection**: Verify REDIS_URL and network access
3. **Secret Keys**: Ensure keys are properly set and secure
4. **Environment**: Verify ENVIRONMENT variable is set correctly

### Validation

```bash
# Validate configuration
python -c "from app.core.config import settings; print('Configuration valid')"
```

## Environment-Specific Settings

### Development

- Debug mode enabled
- Local database and Redis
- Detailed logging
- Hot reload enabled

### Staging

- Debug mode disabled
- Production-like database
- Performance monitoring
- Error tracking

### Production

- Debug mode disabled
- Production database
- Minimal logging
- Security hardening
- Load balancing 