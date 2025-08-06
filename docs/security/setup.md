# 🔒 Security Setup Guide

This guide provides step-by-step instructions for securely setting up ConvoSphere in different environments.

## 🚨 Critical Security Requirements

### 1. Environment Variables
- **NEVER** commit `.env.prod` or any file containing real secrets to version control
- Use environment variables for all sensitive configuration
- Generate secure random values for all secrets

### 2. Secret Key Generation
Generate a secure secret key for production:
```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

### 3. Database Passwords
- Use strong, unique passwords for all database users
- Minimum 32 characters for production databases
- Never use default passwords

## 🛠️ Development Setup

### 1. Copy Environment Files
```bash
# Development
cp env.example .env

# Production (when ready)
cp env.prod.example .env.prod
```

### 2. Configure Development Environment
Edit `.env` and set:
```env
# Generate a secure secret key
SECRET_KEY=your-generated-secret-key-minimum-32-chars

# Database (use strong password even in development)
POSTGRES_PASSWORD=your-secure-dev-password

# AI Providers (optional for development)
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# CORS (development allows localhost)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost:8081
```

### 3. Start Development Environment
```bash
# Start services
docker-compose up -d postgres redis weaviate

# Run migrations
python backend/admin.py db migrate

# Create admin user (interactive)
python backend/admin.py user create-admin
```

## 🏭 Production Setup

### 1. Production Environment Configuration
Edit `.env.prod` with production values:
```env
# Application
ENVIRONMENT=production
DEBUG=false

# Security (CRITICAL)
SECRET_KEY=your-64-char-secret-key-generated-securely
POSTGRES_PASSWORD=your-very-secure-production-password

# CORS (only HTTPS origins)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Disable default user creation
CREATE_DEFAULT_ADMIN=false
CREATE_DEFAULT_ASSISTANT=false
```

### 2. Production Deployment
```bash
# Start production services
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
python backend/admin.py db migrate

# Create admin user securely
export ADMIN_EMAIL=admin@yourdomain.com
export ADMIN_USERNAME=admin
export ADMIN_PASSWORD=your-secure-admin-password
python backend/admin.py user create-secure
```

### 3. Security Verification
```bash
# Check configuration
python backend/admin.py config validate

# Test security endpoints
python backend/admin.py monitoring health
```

## 🔐 Security Features

### CSRF Protection
- Enabled by default in production
- Configurable via `CSRF_PROTECTION_ENABLED`
- Token expiration configurable via `CSRF_TOKEN_EXPIRE_MINUTES`

### CORS Configuration
- Environment-specific validation
- Production enforces HTTPS origins
- Wildcard origins disabled in production

### Rate Limiting
- API endpoint protection
- Configurable limits per endpoint
- IP-based and user-based limiting

### Password Security
- Bcrypt hashing with 12 rounds
- Strong password validation
- Password reset with rate limiting

## 🚨 Security Checklist

### Before Production Deployment
- [ ] All secrets moved to environment variables
- [ ] Strong secret key generated (64+ characters)
- [ ] Database passwords changed from defaults
- [ ] CORS origins restricted to production domains
- [ ] CSRF protection enabled
- [ ] Default user creation disabled
- [ ] HTTPS configured for all external access
- [ ] Firewall rules configured
- [ ] Database access restricted to application network
- [ ] Log monitoring configured

### Regular Security Maintenance
- [ ] Rotate secret keys quarterly
- [ ] Update dependencies monthly
- [ ] Review access logs weekly
- [ ] Test backup/restore procedures
- [ ] Verify SSL certificates
- [ ] Monitor for security advisories

## 🔧 Security Configuration

### Environment-Specific Settings

#### Development
```env
ENVIRONMENT=development
DEBUG=true
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
CSRF_PROTECTION_ENABLED=true
CREATE_DEFAULT_ADMIN=false  # Use admin CLI instead
```

#### Staging
```env
ENVIRONMENT=staging
DEBUG=false
CORS_ORIGINS=https://staging.yourdomain.com
CSRF_PROTECTION_ENABLED=true
CREATE_DEFAULT_ADMIN=false
```

#### Production
```env
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
CSRF_PROTECTION_ENABLED=true
CREATE_DEFAULT_ADMIN=false
```

### Security Headers
The application automatically sets security headers:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`
- `Content-Security-Policy: [configured]`
- `Referrer-Policy: strict-origin-when-cross-origin`

## 🚨 Emergency Procedures

### Compromised Secrets
1. **Immediate Actions:**
   - Rotate all API keys
   - Change database passwords
   - Generate new secret key
   - Review access logs

2. **Update Configuration:**
   ```bash
   # Update environment variables
   # Restart all services
   docker-compose -f docker-compose.prod.yml restart
   ```

### Database Compromise
1. **Isolate affected systems**
2. **Restore from secure backup**
3. **Rotate all credentials**
4. **Review access patterns**

## 📞 Security Support

For security issues:
1. **DO NOT** create public issues
2. Contact security team directly
3. Include detailed incident report
4. Preserve logs and evidence

## 🔍 Security Monitoring

### Log Monitoring
Monitor these log patterns:
- Failed authentication attempts
- Unusual API usage patterns
- Database connection errors
- File upload anomalies

### Health Checks
Regular security health checks:
```bash
# Check system health
python backend/admin.py monitoring health

# Validate configuration
python backend/admin.py config validate

# Test authentication
python backend/admin.py debug auth-flow
```

---

**Remember: Security is an ongoing process, not a one-time setup.**