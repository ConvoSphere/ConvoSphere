# Configuration Guide

This comprehensive configuration guide covers all aspects of configuring the AI Assistant Platform, from basic environment setup to advanced production configurations.

## 📋 Table of Contents

- [Environment Configuration](#environment-configuration)
- [Database Configuration](#database-configuration)
- [Security Configuration](#security-configuration)
- [AI Provider Configuration](#ai-provider-configuration)
- [Performance Configuration](#performance-configuration)
- [Monitoring Configuration](#monitoring-configuration)
- [Deployment Configuration](#deployment-configuration)
- [Advanced Configuration](#advanced-configuration)

## 🔧 Environment Configuration

### Basic Environment Setup

Create a `.env` file in the backend directory with the following structure:

```env
# =============================================================================
# APPLICATION CONFIGURATION
# =============================================================================
APP_NAME=AI Assistant Platform
DEBUG=false
ENVIRONMENT=production
LOG_LEVEL=INFO
TIMEZONE=UTC

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
DATABASE_URL=postgresql://username:password@localhost:5432/chatassistant
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
DATABASE_POOL_TIMEOUT=30

# =============================================================================
# REDIS CONFIGURATION
# =============================================================================
REDIS_URL=redis://localhost:6379/0
REDIS_POOL_SIZE=10
REDIS_SOCKET_TIMEOUT=5
REDIS_SOCKET_CONNECT_TIMEOUT=5

# =============================================================================
# WEAVIATE CONFIGURATION
# =============================================================================
WEAVIATE_URL=http://localhost:8080
WEAVIATE_API_KEY=
WEAVIATE_BATCH_SIZE=100
WEAVIATE_BATCH_DYNAMIC=false

# =============================================================================
# SECURITY CONFIGURATION
# =============================================================================
SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
PASSWORD_MIN_LENGTH=8
PASSWORD_REQUIRE_UPPERCASE=true
PASSWORD_REQUIRE_LOWERCASE=true
PASSWORD_REQUIRE_DIGITS=true
PASSWORD_REQUIRE_SPECIAL_CHARS=true

# =============================================================================
# AI PROVIDER CONFIGURATION
# =============================================================================
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
LITELLM_MODEL=openai/gpt-4
LITELLM_MAX_TOKENS=4096
LITELLM_TEMPERATURE=0.7

# =============================================================================
# CORS AND NETWORK CONFIGURATION
# =============================================================================
CORS_ORIGINS=["http://localhost:3000", "https://your-domain.com"]
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
CORS_ALLOW_HEADERS=["*"]

# =============================================================================
# RATE LIMITING
# =============================================================================
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
RATE_LIMIT_BURST=10

# =============================================================================
# FILE UPLOAD CONFIGURATION
# =============================================================================
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_FILE_TYPES=pdf,doc,docx,txt,md
UPLOAD_DIR=uploads
ENABLE_FILE_COMPRESSION=true

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================
LOG_FORMAT=json
LOG_FILE=logs/app.log
LOG_MAX_SIZE=100MB
LOG_BACKUP_COUNT=5
LOG_LEVEL_ROOT=INFO
LOG_LEVEL_APP=DEBUG
```

### Environment-Specific Configurations

#### Development Environment
```env
DEBUG=true
LOG_LEVEL=DEBUG
ENVIRONMENT=development
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:3000"]
RATE_LIMIT_ENABLED=false
```

#### Staging Environment
```env
DEBUG=false
LOG_LEVEL=INFO
ENVIRONMENT=staging
CORS_ORIGINS=["https://staging.your-domain.com"]
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=50
```

#### Production Environment
```env
DEBUG=false
LOG_LEVEL=WARNING
ENVIRONMENT=production
CORS_ORIGINS=["https://your-domain.com"]
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
```

## 🗄️ Database Configuration

### PostgreSQL Configuration

#### Connection Pooling
```env
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
DATABASE_POOL_TIMEOUT=30
DATABASE_POOL_RECYCLE=3600
```

#### Performance Tuning
```sql
-- PostgreSQL configuration for production
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET work_mem = '4MB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;
```

#### Database Maintenance
```sql
-- Create indexes for better performance
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
CREATE INDEX CONCURRENTLY idx_conversations_user_id ON conversations(user_id);
CREATE INDEX CONCURRENTLY idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX CONCURRENTLY idx_messages_created_at ON messages(created_at);

-- Set up automatic vacuum
ALTER SYSTEM SET autovacuum = on;
ALTER SYSTEM SET autovacuum_max_workers = 3;
ALTER SYSTEM SET autovacuum_naptime = '1min';
```

### Redis Configuration

#### Basic Configuration
```env
REDIS_URL=redis://localhost:6379/0
REDIS_POOL_SIZE=10
REDIS_SOCKET_TIMEOUT=5
REDIS_SOCKET_CONNECT_TIMEOUT=5
REDIS_RETRY_ON_TIMEOUT=true
```

#### Advanced Redis Configuration
```conf
# redis.conf
maxmemory 512mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
appendonly yes
appendfsync everysec
tcp-keepalive 300
```

#### Redis Cluster Configuration
```env
# For Redis Cluster
REDIS_CLUSTER_MODE=true
REDIS_CLUSTER_NODES=redis://node1:6379,redis://node2:6379,redis://node3:6379
REDIS_CLUSTER_REQUIRE_FULL_COVERAGE=false
```

## 🔒 Security Configuration

### JWT Configuration
```env
SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Password Policy
```env
PASSWORD_MIN_LENGTH=8
PASSWORD_REQUIRE_UPPERCASE=true
PASSWORD_REQUIRE_LOWERCASE=true
PASSWORD_REQUIRE_DIGITS=true
PASSWORD_REQUIRE_SPECIAL_CHARS=true
PASSWORD_HISTORY_COUNT=5
PASSWORD_EXPIRY_DAYS=90
```

### CORS Configuration
```env
CORS_ORIGINS=["https://your-domain.com", "https://app.your-domain.com"]
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
CORS_ALLOW_HEADERS=["Authorization", "Content-Type", "X-Requested-With"]
CORS_EXPOSE_HEADERS=["X-Total-Count", "X-Page-Count"]
CORS_MAX_AGE=86400
```

### Rate Limiting
```env
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
RATE_LIMIT_BURST=10
RATE_LIMIT_STORAGE_URL=redis://localhost:6379/1
```

### SSL/TLS Configuration
```env
SSL_ENABLED=true
SSL_CERT_FILE=/path/to/certificate.crt
SSL_KEY_FILE=/path/to/private.key
SSL_CA_FILE=/path/to/ca-bundle.crt
FORCE_HTTPS=true
```

## 🤖 AI Provider Configuration

### OpenAI Configuration
```env
OPENAI_API_KEY=your-openai-api-key
OPENAI_ORGANIZATION=your-organization-id
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=4096
OPENAI_TEMPERATURE=0.7
OPENAI_TOP_P=1.0
OPENAI_FREQUENCY_PENALTY=0.0
OPENAI_PRESENCE_PENALTY=0.0
```

### Anthropic Configuration
```env
ANTHROPIC_API_KEY=your-anthropic-api-key
ANTHROPIC_MODEL=claude-3-sonnet-20240229
ANTHROPIC_MAX_TOKENS=4096
ANTHROPIC_TEMPERATURE=0.7
ANTHROPIC_TOP_P=1.0
ANTHROPIC_TOP_K=40
```

### LiteLLM Configuration
```env
LITELLM_MODEL=openai/gpt-4
LITELLM_MAX_TOKENS=4096
LITELLM_TEMPERATURE=0.7
LITELLM_TOP_P=1.0
LITELLM_FREQUENCY_PENALTY=0.0
LITELLM_PRESENCE_PENALTY=0.0
LITELLM_REQUEST_TIMEOUT=60
LITELLM_RETRY_ATTEMPTS=3
```

### Model Fallback Configuration
```env
MODEL_FALLBACK_ENABLED=true
PRIMARY_MODEL=openai/gpt-4
FALLBACK_MODELS=openai/gpt-3.5-turbo,anthropic/claude-3-haiku-20240307
FALLBACK_ON_ERROR=true
FALLBACK_ON_RATE_LIMIT=true
```

## ⚡ Performance Configuration

### Application Performance
```env
WORKER_PROCESSES=4
WORKER_CONNECTIONS=1000
MAX_REQUESTS=1000
MAX_REQUESTS_JITTER=50
TIMEOUT_KEEP_ALIVE=5
TIMEOUT_GRACEFUL_SHUTDOWN=30
```

### Database Performance
```env
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
DATABASE_POOL_TIMEOUT=30
DATABASE_POOL_RECYCLE=3600
DATABASE_ECHO=false
DATABASE_ECHO_POOL=false
```

### Cache Configuration
```env
CACHE_ENABLED=true
CACHE_TTL=3600
CACHE_MAX_SIZE=1000
CACHE_STORAGE_URL=redis://localhost:6379/2
CACHE_KEY_PREFIX=chatassistant:
```

### File Upload Performance
```env
MAX_FILE_SIZE=10485760  # 10MB
UPLOAD_CHUNK_SIZE=8192
ENABLE_FILE_COMPRESSION=true
COMPRESSION_LEVEL=6
UPLOAD_CONCURRENT_LIMIT=5
```

## 📊 Monitoring Configuration

### Health Check Configuration
```env
HEALTH_CHECK_ENABLED=true
HEALTH_CHECK_INTERVAL=30
HEALTH_CHECK_TIMEOUT=10
HEALTH_CHECK_RETRIES=3
```

### Metrics Configuration
```env
METRICS_ENABLED=true
METRICS_PORT=9090
METRICS_PATH=/metrics
PROMETHEUS_ENABLED=true
```

### Logging Configuration
```env
LOG_FORMAT=json
LOG_FILE=logs/app.log
LOG_MAX_SIZE=100MB
LOG_BACKUP_COUNT=5
LOG_LEVEL_ROOT=INFO
LOG_LEVEL_APP=DEBUG
LOG_LEVEL_SQL=WARNING
LOG_LEVEL_REDIS=WARNING
```

### Error Tracking
```env
SENTRY_DSN=your-sentry-dsn
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1
SENTRY_PROFILES_SAMPLE_RATE=0.1
```

## 🚀 Deployment Configuration

### Docker Configuration
```dockerfile
# Dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose Configuration
```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/chatassistant
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
      - weaviate

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: chatassistant
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  weaviate:
    image: semitechnologies/weaviate:1.22.4
    environment:
      QUERY_DEFAULTS_LIMIT: 25
      AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED: 'true'
      PERSISTENCE_DATA_PATH: '/var/lib/weaviate'
      DEFAULT_VECTORIZER_MODULE: 'none'
      ENABLE_MODULES: 'text2vec-openai,text2vec-cohere,text2vec-huggingface,ref2vec-centroid,generative-openai,qna-openai'
      CLUSTER_HOSTNAME: 'node1'

volumes:
  postgres_data:
  redis_data:
```

### Kubernetes Configuration
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chatassistant
spec:
  replicas: 3
  selector:
    matchLabels:
      app: chatassistant
  template:
    metadata:
      labels:
        app: chatassistant
    spec:
      containers:
      - name: chatassistant
        image: chatassistant:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: chatassistant-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: chatassistant-secrets
              key: redis-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

## 🔧 Advanced Configuration

### Custom Middleware Configuration
```python
# middleware_config.py
MIDDLEWARE_CONFIG = {
    "cors": {
        "allow_origins": ["https://your-domain.com"],
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["*"],
    },
    "rate_limit": {
        "enabled": True,
        "requests": 100,
        "window": 60,
    },
    "auth": {
        "jwt_secret": "your-secret",
        "algorithm": "HS256",
        "access_token_expire_minutes": 30,
    }
}
```

### Custom Logging Configuration
```python
# logging_config.py
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
        },
    },
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "formatter": "json",
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console", "file"],
            "level": "INFO",
        },
        "uvicorn": {
            "handlers": ["console", "file"],
            "level": "INFO",
        },
    },
}
```

### Environment-Specific Overrides
```python
# config_overrides.py
import os

def get_config_overrides():
    env = os.getenv("ENVIRONMENT", "development")
    
    if env == "development":
        return {
            "DEBUG": True,
            "LOG_LEVEL": "DEBUG",
            "CORS_ORIGINS": ["http://localhost:3000"],
        }
    elif env == "staging":
        return {
            "DEBUG": False,
            "LOG_LEVEL": "INFO",
            "CORS_ORIGINS": ["https://staging.your-domain.com"],
        }
    elif env == "production":
        return {
            "DEBUG": False,
            "LOG_LEVEL": "WARNING",
            "CORS_ORIGINS": ["https://your-domain.com"],
        }
    
    return {}
```

## 🔍 Configuration Validation

### Environment Validation Script
```python
# validate_config.py
import os
from typing import Dict, Any

def validate_required_vars() -> Dict[str, Any]:
    required_vars = [
        "DATABASE_URL",
        "REDIS_URL",
        "SECRET_KEY",
        "WEAVIATE_URL",
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {missing_vars}")
    
    return {var: os.getenv(var) for var in required_vars}

def validate_database_url(url: str) -> bool:
    return url.startswith("postgresql://")

def validate_redis_url(url: str) -> bool:
    return url.startswith("redis://")

if __name__ == "__main__":
    try:
        config = validate_required_vars()
        print("✅ Configuration validation passed")
    except ValueError as e:
        print(f"❌ Configuration validation failed: {e}")
        exit(1)
```

## 📚 Configuration Best Practices

### Security Best Practices
1. **Never commit secrets to version control**
2. **Use environment variables for sensitive data**
3. **Rotate secrets regularly**
4. **Use strong, unique passwords**
5. **Enable SSL/TLS in production**

### Performance Best Practices
1. **Use connection pooling for databases**
2. **Configure appropriate cache settings**
3. **Set up monitoring and alerting**
4. **Use load balancing for high availability**
5. **Optimize database queries and indexes**

### Deployment Best Practices
1. **Use containerization for consistency**
2. **Implement health checks**
3. **Set up proper logging**
4. **Configure backup strategies**
5. **Use infrastructure as code**

---

<div align="center">

**Ready to deploy your configuration?** [Deployment Guide →](../deployment/docker.md)

</div> 