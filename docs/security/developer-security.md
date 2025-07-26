# Security Development Guide

This guide provides security best practices and guidelines for developers working on ConvoSphere.

## 🔒 Secure Development Principles

### Security-First Development

#### 1. Secure by Design
- **Security requirements** defined before development starts
- **Threat modeling** for all new features
- **Security reviews** integrated into development process
- **Secure coding standards** enforced through automated tools

#### 2. Defense in Depth
- **Multiple security layers** for critical functionality
- **Input validation** at every layer
- **Output encoding** to prevent injection attacks
- **Error handling** that doesn't leak sensitive information

#### 3. Principle of Least Privilege
- **Minimal permissions** for all components
- **Role-based access control** for all operations
- **Secure defaults** for all configurations
- **Regular permission reviews** and audits

## 🛡️ Secure Coding Practices

### Input Validation and Sanitization

#### 1. Input Validation
```python
# ✅ Good: Comprehensive input validation
from pydantic import BaseModel, validator, Field
from typing import Optional

class UserInput(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, regex=r'^[a-zA-Z0-9_]+$')
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    age: Optional[int] = Field(None, ge=0, le=120)
    
    @validator('username')
    def validate_username(cls, v):
        if v.lower() in ['admin', 'root', 'system']:
            raise ValueError('Username not allowed')
        return v

# ❌ Bad: No input validation
def create_user(username, email, age):
    # Direct use without validation
    user = User(username=username, email=email, age=age)
    return user
```

#### 2. SQL Injection Prevention
```python
# ✅ Good: Parameterized queries
from sqlalchemy.orm import Session
from sqlalchemy import text

def get_user_by_username(db: Session, username: str):
    query = text("SELECT * FROM users WHERE username = :username")
    result = db.execute(query, {"username": username})
    return result.fetchone()

# ❌ Bad: String concatenation (vulnerable to SQL injection)
def get_user_by_username_bad(db: Session, username: str):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    result = db.execute(query)
    return result.fetchone()
```

#### 3. XSS Prevention
```python
# ✅ Good: Output encoding
import html
from markupsafe import escape

def display_user_input(user_input: str):
    # Encode user input before displaying
    safe_input = html.escape(user_input)
    return f"<div>{safe_input}</div>"

# Using Jinja2 templates (automatic escaping)
def render_template(template, user_data):
    return template.render(
        username=escape(user_data.get('username', '')),
        message=escape(user_data.get('message', ''))
    )
```

### Authentication and Authorization

#### 1. Secure Authentication
```python
# ✅ Good: Secure password handling
import bcrypt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# ✅ Good: Secure JWT handling
from jose import JWTError, jwt
from datetime import datetime, timedelta

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

#### 2. Authorization Checks
```python
# ✅ Good: Comprehensive authorization
from functools import wraps
from fastapi import HTTPException, Depends

def require_permission(permission: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = kwargs.get('current_user')
            if not user or permission not in user.permissions:
                raise HTTPException(
                    status_code=403,
                    detail="Insufficient permissions"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Usage
@require_permission("read:users")
async def get_user_profile(user_id: str, current_user: User = Depends(get_current_user)):
    # Only users with read:users permission can access this
    pass
```

### Secure File Handling

#### 1. File Upload Security
```python
# ✅ Good: Secure file upload
import os
import magic
from fastapi import UploadFile, HTTPException

ALLOWED_MIME_TYPES = {
    'application/pdf',
    'text/plain',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

async def validate_file_upload(file: UploadFile):
    # Check file size
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")
    
    # Check file type
    content = await file.read(2048)  # Read first 2KB for MIME detection
    mime_type = magic.from_buffer(content, mime=True)
    
    if mime_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="File type not allowed")
    
    # Reset file pointer
    await file.seek(0)
    return file
```

#### 2. Secure File Storage
```python
# ✅ Good: Secure file storage
import os
import uuid
from pathlib import Path

def secure_file_storage(file: UploadFile, user_id: str) -> str:
    # Generate secure filename
    file_extension = Path(file.filename).suffix
    secure_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Create user-specific directory
    user_dir = Path(f"uploads/{user_id}")
    user_dir.mkdir(parents=True, exist_ok=True)
    
    # Set secure permissions
    file_path = user_dir / secure_filename
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    
    # Set restrictive permissions
    os.chmod(file_path, 0o600)
    
    return str(file_path)
```

## 🔍 Security Testing

### Automated Security Testing

#### 1. Security Test Suite
```python
# tests/security/test_authentication.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestAuthentication:
    def test_sql_injection_login(self):
        """Test SQL injection in login endpoint."""
        payloads = [
            "admin'--",
            "' OR '1'='1",
            "'; DROP TABLE users; --"
        ]
        
        for payload in payloads:
            response = client.post("/api/auth/login", data={
                "username": payload,
                "password": "password"
            })
            # Should not authenticate with SQL injection
            assert response.status_code == 401
    
    def test_xss_protection(self):
        """Test XSS protection in message content."""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>"
        ]
        
        for payload in xss_payloads:
            response = client.post("/api/conversations/1/messages", json={
                "content": payload
            })
            
            if response.status_code == 201:
                message = response.json()
                # Check if content was sanitized
                assert "<script>" not in message["content"]
                assert "javascript:" not in message["content"]
```

#### 2. Security Scanning
```bash
#!/bin/bash
# scripts/security_test.sh

echo "Running security tests..."

# Run security test suite
pytest tests/security/ -v --tb=short

# Run bandit security analysis
bandit -r backend/ -f json -o bandit_report.json

# Run safety check for dependencies
safety check -r requirements.txt --json --output safety_report.json

# Run OWASP ZAP scan (if available)
if command -v zap-baseline.py &> /dev/null; then
    zap-baseline.py -t http://localhost:8000 -J zap_report.json
fi

echo "Security tests completed. Check reports for issues."
```

### Manual Security Testing

#### 1. Penetration Testing Checklist
```markdown
# Security Testing Checklist

## Authentication & Authorization
- [ ] Test password complexity requirements
- [ ] Test account lockout mechanisms
- [ ] Test session timeout
- [ ] Test privilege escalation
- [ ] Test access control bypass

## Input Validation
- [ ] Test SQL injection vulnerabilities
- [ ] Test XSS vulnerabilities
- [ ] Test CSRF vulnerabilities
- [ ] Test file upload vulnerabilities
- [ ] Test path traversal attacks

## API Security
- [ ] Test rate limiting
- [ ] Test input validation
- [ ] Test error handling
- [ ] Test authentication bypass
- [ ] Test authorization bypass

## Infrastructure
- [ ] Test container security
- [ ] Test network security
- [ ] Test secrets management
- [ ] Test backup security
- [ ] Test logging and monitoring
```

## 🔧 Security Tools Integration

### Development Environment

#### 1. Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: [-r, backend/, -f, json, -o, bandit_report.json]
  
  - repo: https://github.com/pyupio/safety
    rev: 2.3.5
    hooks:
      - id: safety
        args: [check, -r, requirements.txt]
  
  - repo: https://github.com/PyCQA/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203,W503]
```

#### 2. IDE Security Plugins
```json
// .vscode/settings.json
{
    "python.linting.enabled": true,
    "python.linting.banditEnabled": true,
    "python.linting.flake8Enabled": true,
    "security.workspace.trust.enabled": true,
    "security.workspace.trust.untrustedFiles": "prompt"
}
```

### CI/CD Security

#### 1. GitHub Actions Security
```yaml
# .github/workflows/security.yml
name: Security Scan

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements-dev.txt
      
      - name: Run security tests
        run: |
          pytest tests/security/ -v
          bandit -r backend/ -f json
          safety check -r requirements.txt
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'convosphere-backend:latest'
          format: 'sarif'
          output: 'trivy-results.sarif'
      
      - name: Upload security reports
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: bandit_report.json
```

## 📚 Security Resources

### Learning Resources
- **OWASP Top 10**: Web application security risks
- **OWASP Cheat Sheet Series**: Security best practices
- **SANS Secure Coding**: Secure development guidelines
- **NIST Cybersecurity Framework**: Security standards

### Security Tools
- **Bandit**: Python security linting
- **Safety**: Dependency vulnerability scanning
- **Trivy**: Container vulnerability scanning
- **OWASP ZAP**: Web application security testing
- **SonarQube**: Code quality and security analysis

### Security Standards
- **ISO 27001**: Information security management
- **OWASP ASVS**: Application security verification standard
- **NIST SP 800-53**: Security and privacy controls
- **GDPR**: Data protection regulation

## 🚨 Security Incident Response

### Developer Responsibilities

#### 1. Incident Reporting
```python
# Security incident reporting
async def report_security_incident(
    incident_type: str,
    severity: str,
    description: str,
    affected_components: List[str]
):
    incident = {
        "type": incident_type,
        "severity": severity,
        "description": description,
        "components": affected_components,
        "timestamp": datetime.utcnow().isoformat(),
        "reporter": get_current_user_id()
    }
    
    # Log incident
    await log_security_event(incident)
    
    # Notify security team
    await notify_security_team(incident)
    
    return incident
```

#### 2. Vulnerability Disclosure
```python
# Vulnerability disclosure process
async def disclose_vulnerability(
    vulnerability_type: str,
    description: str,
    impact: str,
    reproduction_steps: List[str]
):
    disclosure = {
        "type": vulnerability_type,
        "description": description,
        "impact": impact,
        "steps": reproduction_steps,
        "status": "reported",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Create security advisory
    await create_security_advisory(disclosure)
    
    # Notify stakeholders
    await notify_stakeholders(disclosure)
    
    return disclosure
```

## 📞 Security Support

### Security Contacts
- **Security Team**: [security@yourdomain.com](mailto:security@yourdomain.com)
- **Code Review**: [code-review@yourdomain.com](mailto:code-review@yourdomain.com)
- **Security Training**: [training@yourdomain.com](mailto:training@yourdomain.com)

### Security Channels
- **Security Slack**: #security
- **Security Discord**: #security-discussions
- **Security Mailing List**: security@yourdomain.com

---

**Remember**: Security is everyone's responsibility. Write secure code, test thoroughly, and report security issues promptly.

**Last Updated**: {{ git_revision_date_localized }}