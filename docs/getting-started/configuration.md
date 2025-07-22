# Configuration Guide

This guide covers all configuration options for the AI Chat Application, including environment variables, database settings, AI provider configuration, and security settings.

## Environment Configuration

### Core Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# =============================================================================
# APPLICATION CONFIGURATION
# =============================================================================
DEBUG=true
ENVIRONMENT=development
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
DATABASE_URL=postgresql://user:password@localhost:5432/ai_chat_db
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
DATABASE_POOL_TIMEOUT=30

# =============================================================================
# REDIS CONFIGURATION
# =============================================================================
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=
REDIS_DB=0

# =============================================================================
# SECURITY CONFIGURATION
# =============================================================================
SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
PASSWORD_MIN_LENGTH=8
PASSWORD_REQUIRE_SPECIAL_CHARS=true

# =============================================================================
# CORS CONFIGURATION
# =============================================================================
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
CORS_ALLOW_HEADERS=["*"]

# =============================================================================
# AI PROVIDER CONFIGURATION
# =============================================================================
DEFAULT_AI_PROVIDER=openai
OPENAI_API_KEY=your-openai-api-key
OPENAI_ORGANIZATION=your-openai-org-id
ANTHROPIC_API_KEY=your-anthropic-api-key
GOOGLE_AI_API_KEY=your-google-ai-api-key
COHERE_API_KEY=your-cohere-api-key

# =============================================================================
# MODEL CONFIGURATION
# =============================================================================
DEFAULT_MODEL=gpt-4
FALLBACK_MODEL=gpt-3.5-turbo
MAX_TOKENS=4096
TEMPERATURE=0.7
TOP_P=1.0
FREQUENCY_PENALTY=0.0
PRESENCE_PENALTY=0.0

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
ALLOWED_FILE_TYPES=pdf,doc,docx,txt,md,csv,json
UPLOAD_DIR=uploads
ENABLE_FILE_PROCESSING=true

# =============================================================================
# EMAIL CONFIGURATION
# =============================================================================
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_TLS=true
FROM_EMAIL=noreply@yourdomain.com

# =============================================================================
# MONITORING AND LOGGING
# =============================================================================
ENABLE_METRICS=true
METRICS_PORT=9090
LOG_FORMAT=json
LOG_FILE=logs/app.log
SENTRY_DSN=your-sentry-dsn
```

## Database Configuration

### PostgreSQL Settings

#### Development Configuration

```sql
-- Create database and user
CREATE DATABASE ai_chat_db;
CREATE USER ai_chat_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE ai_chat_db TO ai_chat_user;
ALTER USER ai_chat_user CREATEDB;

-- Set up extensions
\c ai_chat_db
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
```

#### Production Configuration

```sql
-- Optimize for production
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET work_mem = '4MB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;

-- Reload configuration
SELECT pg_reload_conf();
```

### Redis Configuration

#### Development Configuration

```bash
# Edit Redis configuration
sudo nano /etc/redis/redis.conf

# Basic settings
bind 127.0.0.1
port 6379
databases 16
save 900 1
save 300 10
save 60 10000
```

#### Production Configuration

```bash
# Production Redis settings
maxmemory 512mb
maxmemory-policy allkeys-lru
appendonly yes
appendfsync everysec
tcp-keepalive 300
timeout 0
tcp-backlog 511
```

## AI Provider Configuration

### OpenAI Configuration

```python
# OpenAI settings
OPENAI_CONFIG = {
    "api_key": os.getenv("OPENAI_API_KEY"),
    "organization": os.getenv("OPENAI_ORGANIZATION"),
    "default_model": "gpt-4",
    "fallback_model": "gpt-3.5-turbo",
    "max_tokens": 4096,
    "temperature": 0.7,
    "timeout": 30,
    "retry_attempts": 3
}
```

### Anthropic Configuration

```python
# Anthropic settings
ANTHROPIC_CONFIG = {
    "api_key": os.getenv("ANTHROPIC_API_KEY"),
    "default_model": "claude-3-sonnet-20240229",
    "max_tokens": 4096,
    "temperature": 0.7,
    "timeout": 30,
    "retry_attempts": 3
}
```

### Model Selection Strategy

```python
# Model selection configuration
MODEL_SELECTION = {
    "strategy": "cost_optimized",  # or "performance_optimized"
    "budget_limit": 0.10,  # $0.10 per request
    "performance_threshold": 0.8,
    "fallback_chain": [
        "gpt-4",
        "gpt-3.5-turbo",
        "claude-3-haiku-20240307"
    ]
}
```

## Security Configuration

### JWT Configuration

```python
# JWT settings
JWT_CONFIG = {
    "secret_key": os.getenv("JWT_SECRET_KEY"),
    "algorithm": "HS256",
    "access_token_expire_minutes": 30,
    "refresh_token_expire_days": 7,
    "token_type": "Bearer"
}
```

### Password Policy

```python
# Password requirements
PASSWORD_POLICY = {
    "min_length": 8,
    "require_uppercase": True,
    "require_lowercase": True,
    "require_digits": True,
    "require_special_chars": True,
    "max_length": 128,
    "prevent_common_passwords": True
}
```

### Rate Limiting

```python
# Rate limiting configuration
RATE_LIMIT_CONFIG = {
    "enabled": True,
    "requests_per_minute": 100,
    "burst_limit": 10,
    "storage": "redis",
    "key_prefix": "rate_limit:"
}
```

## File Upload Configuration

### File Processing Settings

```python
# File upload configuration
FILE_UPLOAD_CONFIG = {
    "max_size": 10 * 1024 * 1024,  # 10MB
    "allowed_types": [
        "application/pdf",
        "text/plain",
        "text/markdown",
        "application/json",
        "text/csv"
    ],
    "storage_backend": "local",  # or "s3", "gcs"
    "process_files": True,
    "extract_text": True,
    "create_embeddings": True
}
```

### S3 Configuration (Optional)

```env
# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name
S3_ENDPOINT_URL=https://s3.amazonaws.com
```

## Email Configuration

### SMTP Settings

```python
# Email configuration
EMAIL_CONFIG = {
    "smtp_host": os.getenv("SMTP_HOST"),
    "smtp_port": int(os.getenv("SMTP_PORT", 587)),
    "smtp_username": os.getenv("SMTP_USERNAME"),
    "smtp_password": os.getenv("SMTP_PASSWORD"),
    "smtp_tls": os.getenv("SMTP_TLS", "true").lower() == "true",
    "from_email": os.getenv("FROM_EMAIL"),
    "from_name": "AI Chat Application"
}
```

## Monitoring Configuration

### Logging Configuration

```python
# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter"
        }
    },
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "formatter": "json"
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json"
        }
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO"
    }
}
```

### Metrics Configuration

```python
# Metrics configuration
METRICS_CONFIG = {
    "enabled": True,
    "port": 9090,
    "endpoint": "/metrics",
    "collectors": [
        "request_count",
        "request_duration",
        "error_count",
        "active_connections"
    ]
}
```

## Environment-Specific Configurations

### Development Environment

```env
# Development settings
DEBUG=true
LOG_LEVEL=DEBUG
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
ENABLE_METRICS=false
RATE_LIMIT_ENABLED=false
```

### Staging Environment

```env
# Staging settings
DEBUG=false
LOG_LEVEL=INFO
CORS_ORIGINS=["https://staging.yourdomain.com"]
ENABLE_METRICS=true
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=50
```

### Production Environment

```env
# Production settings
DEBUG=false
LOG_LEVEL=WARNING
CORS_ORIGINS=["https://yourdomain.com"]
ENABLE_METRICS=true
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
SENTRY_DSN=your-sentry-dsn
```

## Configuration Validation

### Environment Validation Script

```python
# config_validator.py
import os
from typing import Dict, List

def validate_environment() -> Dict[str, List[str]]:
    """Validate environment configuration."""
    errors = []
    warnings = []
    
    # Required variables
    required_vars = [
        "DATABASE_URL",
        "REDIS_URL",
        "SECRET_KEY",
        "JWT_SECRET_KEY"
    ]
    
    for var in required_vars:
        if not os.getenv(var):
            errors.append(f"Missing required environment variable: {var}")
    
    # Optional but recommended
    recommended_vars = [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY"
    ]
    
    for var in recommended_vars:
        if not os.getenv(var):
            warnings.append(f"Missing recommended environment variable: {var}")
    
    return {"errors": errors, "warnings": warnings}

if __name__ == "__main__":
    result = validate_environment()
    
    if result["errors"]:
        print("❌ Configuration errors:")
        for error in result["errors"]:
            print(f"  - {error}")
        exit(1)
    
    if result["warnings"]:
        print("⚠️  Configuration warnings:")
        for warning in result["warnings"]:
            print(f"  - {warning}")
    
    print("✅ Configuration validation passed!")
```

## Configuration Management

### Using Configuration Classes

```python
# config.py
from pydantic import BaseSettings, validator
from typing import List, Optional

class Settings(BaseSettings):
    # Application
    debug: bool = False
    environment: str = "development"
    log_level: str = "INFO"
    
    # Database
    database_url: str
    
    # Redis
    redis_url: str
    
    # Security
    secret_key: str
    jwt_secret_key: str
    
    # AI Providers
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    @validator("secret_key")
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters")
        return v
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### Environment-Specific Configuration Files

```bash
# Create environment-specific configs
cp .env .env.development
cp .env .env.staging
cp .env .env.production

# Use appropriate config based on environment
export ENVIRONMENT=production
export CONFIG_FILE=.env.production
```

## Best Practices

### Security Best Practices

1. **Never commit secrets to version control**
2. **Use strong, unique secret keys**
3. **Rotate API keys regularly**
4. **Use environment-specific configurations**
5. **Enable HTTPS in production**

### Performance Best Practices

1. **Optimize database connection pools**
2. **Configure Redis for your workload**
3. **Set appropriate rate limits**
4. **Monitor resource usage**
5. **Use caching strategies**

### Monitoring Best Practices

1. **Enable structured logging**
2. **Set up metrics collection**
3. **Configure error tracking**
4. **Monitor API response times**
5. **Set up alerting for critical issues**

## Troubleshooting Configuration Issues

### Common Configuration Problems

1. **Database Connection Issues**
   - Check connection string format
   - Verify database credentials
   - Ensure database is running

2. **Redis Connection Issues**
   - Verify Redis is running
   - Check connection URL format
   - Test with redis-cli

3. **AI Provider Issues**
   - Verify API keys are valid
   - Check API quotas and limits
   - Test API endpoints directly

4. **Security Issues**
   - Ensure secret keys are strong
   - Check CORS configuration
   - Verify JWT settings

### Configuration Testing

```bash
# Test configuration
python -c "
from config import settings
print('Configuration loaded successfully')
print(f'Environment: {settings.environment}')
print(f'Debug mode: {settings.debug}')
"
```

## Next Steps

After configuring your application:

1. **Test the configuration** using the validation script
2. **Start the application** and verify all services are working
3. **Monitor logs** for any configuration-related issues
4. **Set up monitoring** to track application performance
5. **Document your configuration** for team members

For more detailed information about specific configuration areas, see:

- [Database Configuration](../architecture/database.md)
- [Security Configuration](../architecture/security.md)
- [AI Provider Setup](../features/ai-integration.md)
- [Deployment Configuration](../deployment/production.md) 