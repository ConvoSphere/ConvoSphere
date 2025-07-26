# ConvoSphere - Security Action Plan

## 🎯 Übersicht

Dieser Action-Plan basiert auf der umfassenden Security-Analyse und definiert konkrete Schritte zur Verbesserung der Sicherheit des ConvoSphere-Systems.

**Zeitrahmen:** 3 Monate  
**Priorität:** Kritisch  
**Budget:** €45,000  

---

## 📅 Phase 1: Kritische Sicherheitslücken (Woche 1-2)

### 1.1 Secrets Management (KRITISCH - Tag 1-3)

#### A. Sofortige Maßnahmen
```bash
# 1. Secrets aus docker-compose.yml entfernen
# Erstelle .env.production
cat > .env.production << EOF
# Production Environment Variables
OPENAI_API_KEY=your-actual-production-key
ANTHROPIC_API_KEY=your-actual-anthropic-key
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=postgresql://user:password@host:5432/db
REDIS_URL=redis://host:6379
EOF

# 2. .env.production zu .gitignore hinzufügen
echo ".env.production" >> .gitignore
echo "secrets/" >> .gitignore
```

#### B. Docker Secrets implementieren
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  backend:
    secrets:
      - openai_api_key
      - secret_key
      - database_url
    environment:
      - OPENAI_API_KEY_FILE=/run/secrets/openai_api_key
      - SECRET_KEY_FILE=/run/secrets/secret_key

secrets:
  openai_api_key:
    file: ./secrets/openai_api_key
  secret_key:
    file: ./secrets/secret_key
  database_url:
    file: ./secrets/database_url
```

#### C. Konfiguration anpassen
```python
# backend/app/core/config.py - Zeile 47-50 anpassen
secret_key: str = Field(
    default=None,  # Kein Default mehr
    description="Secret key - must be set in production",
)

@field_validator("secret_key")
@classmethod
def validate_secret_key(cls, v):
    if not v or v == "dev-secret-key-for-development-only-change-in-production":
        raise ValueError("Secret key must be properly configured in production")
    if len(v) < 32:
        raise ValueError("Secret key must be at least 32 characters long")
    return v
```

### 1.2 Netzwerk-Sicherheit (KRITISCH - Tag 4-7)

#### A. Port-Exposure eliminieren
```yaml
# docker-compose.yml - Zeile 60-65 anpassen
postgres:
  image: postgres:15
  environment:
    - POSTGRES_DB=convosphere
    - POSTGRES_USER=convosphere
    - POSTGRES_PASSWORD=convosphere_password
  volumes:
    - postgres_data:/var/lib/postgresql/data
  # ports: []  # Keine externen Ports mehr
  networks:
    - internal-network
  restart: unless-stopped

redis:
  image: redis:7-alpine
  # ports: []  # Keine externen Ports mehr
  volumes:
    - ./docker/redis/redis.conf:/usr/local/etc/redis/redis.conf
    - redis_data:/data
  command: redis-server /usr/local/etc/redis/redis.conf
  networks:
    - internal-network
  restart: unless-stopped

weaviate:
  image: semitechnologies/weaviate:1.23.7
  # ports: []  # Keine externen Ports mehr
  environment:
    - QUERY_DEFAULTS_LIMIT=25
    - AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=false  # Authentifizierung aktivieren
  volumes:
    - weaviate_data:/var/lib/weaviate
  networks:
    - internal-network
  restart: unless-stopped
```

#### B. Netzwerk-Isolation
```yaml
# docker-compose.yml - Netzwerke definieren
networks:
  internal-network:
    internal: true  # Nur interne Kommunikation
    driver: bridge
  external-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### 1.3 Security-Headers (HOCH - Tag 8-10)

#### A. FastAPI Security Middleware
```python
# backend/app/core/security_middleware.py
from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        
        # Security Headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response
```

#### B. CORS-Konfiguration härten
```python
# backend/app/core/config.py - CORS anpassen
cors_origins: list[str] = Field(
    default=[
        "https://yourdomain.com",  # Nur spezifische Domains
        "https://www.yourdomain.com",
    ],
    description="List of allowed CORS origins - restrict in production",
)
```

### 1.4 Container-Härtung (HOCH - Tag 11-14)

#### A. Dockerfile-Härtung
```dockerfile
# docker/backend/Dockerfile
FROM python:3.11-slim

# Security-Updates
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Non-root User erstellen
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Arbeitsverzeichnis
WORKDIR /app

# Dependencies installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application Code kopieren
COPY backend/ ./backend/

# Berechtigungen setzen
RUN chown -R appuser:appuser /app
USER appuser

# Health Check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Port exponieren
EXPOSE 8000

# Application starten
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### B. Security-Scanning implementieren
```yaml
# .github/workflows/security-scan.yml
name: Security Scan

on: [push, pull_request]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Bandit
        run: |
          pip install bandit
          bandit -r backend/ -f json -o security_scan.json
          
      - name: Run Safety Check
        run: |
          pip install safety
          safety check -r requirements.txt
          
      - name: Run Trivy
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'convosphere-backend:latest'
          format: 'sarif'
          output: 'trivy-results.sarif'
```

---

## 📅 Phase 2: Erweiterte Sicherheit (Woche 3-6)

### 2.1 Multi-Factor Authentication (HOCH - Woche 3-4)

#### A. TOTP-basierte MFA
```python
# backend/app/services/mfa_service.py
import pyotp
import qrcode
from io import BytesIO
import base64

class MFAService:
    def __init__(self):
        self.totp = pyotp.TOTP
    
    def generate_secret(self, user_id: str) -> str:
        """Generate TOTP secret for user."""
        secret = pyotp.random_base32()
        return secret
    
    def generate_qr_code(self, secret: str, user_email: str) -> str:
        """Generate QR code for MFA setup."""
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user_email,
            issuer_name="ConvoSphere"
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        
        return base64.b64encode(buffer.getvalue()).decode()
    
    def verify_token(self, secret: str, token: str) -> bool:
        """Verify TOTP token."""
        totp = pyotp.TOTP(secret)
        return totp.verify(token)
```

#### B. MFA-Endpunkte
```python
# backend/app/api/v1/endpoints/mfa.py
from fastapi import APIRouter, Depends, HTTPException
from app.services.mfa_service import MFAService
from app.core.security import get_current_user

router = APIRouter()
mfa_service = MFAService()

@router.post("/setup")
async def setup_mfa(current_user = Depends(get_current_user)):
    """Setup MFA for user."""
    secret = mfa_service.generate_secret(current_user.id)
    qr_code = mfa_service.generate_qr_code(secret, current_user.email)
    
    # Store secret temporarily (encrypted)
    # In production, use secure storage
    
    return {
        "secret": secret,
        "qr_code": qr_code,
        "backup_codes": generate_backup_codes()
    }

@router.post("/verify")
async def verify_mfa(token: str, current_user = Depends(get_current_user)):
    """Verify MFA token."""
    # Get user's MFA secret
    secret = get_user_mfa_secret(current_user.id)
    
    if mfa_service.verify_token(secret, token):
        return {"status": "verified"}
    else:
        raise HTTPException(status_code=400, detail="Invalid MFA token")
```

### 2.2 Advanced Threat Detection (HOCH - Woche 4-5)

#### A. Behavioral Analysis
```python
# backend/app/services/threat_detection.py
import numpy as np
from sklearn.ensemble import IsolationForest
from datetime import datetime, timedelta

class BehavioralThreatDetection:
    def __init__(self):
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.user_profiles = {}
    
    def analyze_user_behavior(self, user_id: str, action: dict) -> dict:
        """Analyze user behavior for anomalies."""
        features = self.extract_features(action)
        
        # Update user profile
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = []
        
        self.user_profiles[user_id].append(features)
        
        # Detect anomalies
        if len(self.user_profiles[user_id]) > 10:
            anomaly_score = self.detect_anomaly(user_id, features)
            
            if anomaly_score > 0.7:  # Threshold
                return {
                    "anomaly_detected": True,
                    "score": anomaly_score,
                    "risk_level": "high" if anomaly_score > 0.9 else "medium"
                }
        
        return {"anomaly_detected": False, "score": 0.0}
    
    def extract_features(self, action: dict) -> list:
        """Extract behavioral features from action."""
        return [
            action.get("timestamp", 0),
            action.get("ip_address", ""),
            action.get("user_agent", ""),
            action.get("endpoint", ""),
            action.get("method", ""),
            action.get("response_time", 0),
            action.get("payload_size", 0)
        ]
    
    def detect_anomaly(self, user_id: str, features: list) -> float:
        """Detect anomaly using isolation forest."""
        user_data = np.array(self.user_profiles[user_id])
        self.model.fit(user_data)
        
        # Predict anomaly score
        score = self.model.decision_function([features])[0]
        return 1 - score  # Convert to anomaly score
```

#### B. Real-time Monitoring
```python
# backend/app/core/monitoring.py
import asyncio
from datetime import datetime
from app.services.threat_detection import BehavioralThreatDetection

class SecurityMonitoring:
    def __init__(self):
        self.threat_detector = BehavioralThreatDetection()
        self.alert_threshold = 0.8
    
    async def monitor_request(self, request: Request, user_id: str):
        """Monitor incoming requests for threats."""
        action = {
            "timestamp": datetime.now().timestamp(),
            "ip_address": request.client.host,
            "user_agent": request.headers.get("user-agent"),
            "endpoint": request.url.path,
            "method": request.method,
            "user_id": user_id
        }
        
        # Analyze behavior
        result = self.threat_detector.analyze_user_behavior(user_id, action)
        
        if result["anomaly_detected"]:
            await self.trigger_alert(result, action)
    
    async def trigger_alert(self, result: dict, action: dict):
        """Trigger security alert."""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "user_id": action["user_id"],
            "ip_address": action["ip_address"],
            "anomaly_score": result["score"],
            "risk_level": result["risk_level"],
            "action": action
        }
        
        # Log alert
        logger.warning(f"Security alert: {alert}")
        
        # Send notification (email, Slack, etc.)
        await self.send_notification(alert)
        
        # Take action based on risk level
        if result["risk_level"] == "high":
            await self.block_user(action["user_id"])
```

### 2.3 Data Encryption (MITTLER - Woche 5-6)

#### A. Field-level Encryption
```python
# backend/app/core/encryption.py
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

class DataEncryption:
    def __init__(self):
        self.key = os.getenv("ENCRYPTION_KEY")
        if not self.key:
            self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)
    
    def encrypt_field(self, data: str) -> str:
        """Encrypt sensitive field data."""
        if not data:
            return data
        encrypted = self.cipher.encrypt(data.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt_field(self, encrypted_data: str) -> str:
        """Decrypt sensitive field data."""
        if not encrypted_data:
            return encrypted_data
        try:
            decoded = base64.b64decode(encrypted_data.encode())
            decrypted = self.cipher.decrypt(decoded)
            return decrypted.decode()
        except Exception:
            return encrypted_data  # Return original if decryption fails
    
    def encrypt_file(self, file_path: str) -> str:
        """Encrypt file content."""
        with open(file_path, 'rb') as f:
            data = f.read()
        encrypted = self.cipher.encrypt(data)
        return base64.b64encode(encrypted).decode()
```

#### B. Encrypted Fields in Models
```python
# backend/app/models/user.py
from sqlalchemy import Column, String, Boolean
from app.core.encryption import DataEncryption

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, index=True)
    encrypted_phone = Column(String)  # Encrypted phone number
    encrypted_ssn = Column(String)    # Encrypted SSN
    
    def __init__(self, **kwargs):
        self.encryption = DataEncryption()
        super().__init__(**kwargs)
    
    @property
    def phone(self):
        return self.encryption.decrypt_field(self.encrypted_phone)
    
    @phone.setter
    def phone(self, value):
        self.encrypted_phone = self.encryption.encrypt_field(value)
    
    @property
    def ssn(self):
        return self.encryption.decrypt_field(self.encrypted_ssn)
    
    @ssn.setter
    def ssn(self, value):
        self.encrypted_ssn = self.encryption.encrypt_field(value)
```

---

## 📅 Phase 3: Security Excellence (Woche 7-12)

### 3.1 Zero-Trust Architecture (HOCH - Woche 7-9)

#### A. Continuous Authentication
```python
# backend/app/core/zero_trust.py
from fastapi import Request, HTTPException
from app.services.threat_detection import BehavioralThreatDetection

class ZeroTrustMiddleware:
    def __init__(self):
        self.threat_detector = BehavioralThreatDetection()
        self.trust_scores = {}
    
    async def validate_request(self, request: Request, user_id: str) -> bool:
        """Validate every request with zero trust principles."""
        
        # 1. Device Fingerprinting
        device_score = await self.validate_device(request)
        
        # 2. Behavioral Analysis
        behavior_score = await self.validate_behavior(request, user_id)
        
        # 3. Context Validation
        context_score = await self.validate_context(request)
        
        # 4. Calculate Trust Score
        trust_score = (device_score + behavior_score + context_score) / 3
        
        # Update user trust score
        self.trust_scores[user_id] = trust_score
        
        # Decision based on trust score
        if trust_score < 0.5:
            await self.log_suspicious_activity(request, user_id, trust_score)
            raise HTTPException(status_code=403, detail="Access denied")
        
        return True
    
    async def validate_device(self, request: Request) -> float:
        """Validate device fingerprint."""
        # Implement device fingerprinting logic
        return 0.8  # Placeholder
    
    async def validate_behavior(self, request: Request, user_id: str) -> float:
        """Validate user behavior."""
        action = self.extract_action_data(request)
        result = self.threat_detector.analyze_user_behavior(user_id, action)
        return 1.0 - result.get("score", 0.0)
    
    async def validate_context(self, request: Request) -> float:
        """Validate request context."""
        # Time-based validation
        # Location-based validation
        # Request pattern validation
        return 0.9  # Placeholder
```

#### B. Micro-segmentation
```python
# backend/app/core/network_segmentation.py
class NetworkSegmentation:
    def __init__(self):
        self.segments = {
            "public": ["/api/public", "/health"],
            "authenticated": ["/api/v1/users", "/api/v1/conversations"],
            "admin": ["/api/v1/admin", "/api/v1/system"],
            "internal": ["/api/v1/internal"]
        }
    
    def get_segment_for_endpoint(self, endpoint: str) -> str:
        """Determine network segment for endpoint."""
        for segment, patterns in self.segments.items():
            for pattern in patterns:
                if endpoint.startswith(pattern):
                    return segment
        return "authenticated"  # Default
    
    def validate_access(self, user_role: str, segment: str) -> bool:
        """Validate user access to network segment."""
        access_matrix = {
            "user": ["public", "authenticated"],
            "admin": ["public", "authenticated", "admin"],
            "system": ["public", "authenticated", "admin", "internal"]
        }
        
        return segment in access_matrix.get(user_role, ["public"])
```

### 3.2 Automated Security Testing (MITTLER - Woche 10-11)

#### A. Security Test Suite
```python
# tests/security/test_security_comprehensive.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

class TestComprehensiveSecurity:
    """Comprehensive security test suite."""
    
    def test_sql_injection_protection(self, client: TestClient):
        """Test SQL injection protection."""
        payloads = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "admin'--",
            "1' OR '1'='1'--"
        ]
        
        for payload in payloads:
            response = client.get(f"/api/users/search?q={payload}")
            assert response.status_code in [200, 400, 422]
            # Verify no sensitive data exposure
    
    def test_xss_protection(self, client: TestClient):
        """Test XSS protection."""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>"
        ]
        
        for payload in xss_payloads:
            response = client.post("/api/conversations/1/messages", 
                                 json={"content": payload})
            if response.status_code == 201:
                message = response.json()
                assert "<script>" not in message["content"]
    
    def test_csrf_protection(self, client: TestClient):
        """Test CSRF protection."""
        # Test state-changing operations without CSRF token
        response = client.post("/api/users/me", json={"name": "test"})
        assert response.status_code in [401, 403, 422]
    
    def test_rate_limiting(self, client: TestClient):
        """Test rate limiting."""
        for _ in range(100):
            response = client.get("/api/users/search?q=test")
            if response.status_code == 429:
                break
        else:
            pytest.fail("Rate limiting not working")
    
    def test_authentication_bypass(self, client: TestClient):
        """Test authentication bypass attempts."""
        protected_endpoints = [
            "/api/v1/users/me",
            "/api/v1/conversations",
            "/api/v1/admin/users"
        ]
        
        for endpoint in protected_endpoints:
            response = client.get(endpoint)
            assert response.status_code in [401, 403]
```

#### B. CI/CD Security Pipeline
```yaml
# .github/workflows/security-pipeline.yml
name: Security Pipeline

on: [push, pull_request]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run SAST
        uses: github/codeql-action/init@v2
        with:
          languages: python
      
      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v2
      
      - name: Run Bandit
        run: |
          pip install bandit
          bandit -r backend/ -f json -o bandit-report.json
      
      - name: Run Safety Check
        run: |
          pip install safety
          safety check -r requirements.txt --json --output safety-report.json
      
      - name: Run Trivy
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'convosphere-backend:latest'
          format: 'sarif'
          output: 'trivy-results.sarif'
      
      - name: Upload Security Reports
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: bandit-report.json
      
      - name: Security Test Suite
        run: |
          pip install -r requirements-test.txt
          pytest tests/security/ -v --junitxml=security-test-results.xml
      
      - name: Generate Security Report
        run: |
          python scripts/generate_security_report.py
```

### 3.3 Compliance Framework (MITTLER - Woche 11-12)

#### A. GDPR Compliance
```python
# backend/app/services/gdpr_service.py
from datetime import datetime
from app.models.user import User
from app.core.encryption import DataEncryption

class GDPRService:
    def __init__(self):
        self.encryption = DataEncryption()
    
    async def export_user_data(self, user_id: str) -> dict:
        """Export user data for GDPR compliance."""
        user = await get_user_by_id(user_id)
        
        return {
            "user_id": user.id,
            "email": user.email,
            "created_at": user.created_at.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "conversations": await self.get_user_conversations(user_id),
            "files": await self.get_user_files(user_id),
            "preferences": await self.get_user_preferences(user_id)
        }
    
    async def delete_user_data(self, user_id: str) -> bool:
        """Delete user data for GDPR compliance."""
        try:
            # Anonymize user data instead of deletion
            await self.anonymize_user_data(user_id)
            return True
        except Exception as e:
            logger.error(f"Failed to delete user data: {e}")
            return False
    
    async def anonymize_user_data(self, user_id: str):
        """Anonymize user data."""
        # Replace personal data with anonymized values
        anonymized_email = f"deleted_{user_id}@deleted.com"
        anonymized_name = f"Deleted User {user_id[-8:]}"
        
        # Update user record
        await update_user(user_id, {
            "email": anonymized_email,
            "first_name": anonymized_name,
            "last_name": "",
            "phone": None,
            "deleted_at": datetime.now()
        })
```

#### B. Audit Logging
```python
# backend/app/services/audit_service.py
from datetime import datetime
from app.models.audit import AuditLog

class AuditService:
    async def log_data_access(self, user_id: str, data_type: str, action: str):
        """Log data access for compliance."""
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            data_type=data_type,
            timestamp=datetime.now(),
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
        
        await audit_log.save()
    
    async def log_data_export(self, user_id: str):
        """Log data export for GDPR compliance."""
        await self.log_data_access(user_id, "personal_data", "export")
    
    async def log_data_deletion(self, user_id: str):
        """Log data deletion for GDPR compliance."""
        await self.log_data_access(user_id, "personal_data", "deletion")
    
    async def get_audit_trail(self, user_id: str, days: int = 30) -> list:
        """Get audit trail for user."""
        start_date = datetime.now() - timedelta(days=days)
        
        return await AuditLog.filter(
            user_id=user_id,
            timestamp__gte=start_date
        ).order_by("-timestamp")
```

---

## 📊 Erfolgsmetriken & Monitoring

### 4.1 Security KPIs
```python
# backend/app/services/security_metrics.py
class SecurityMetrics:
    def __init__(self):
        self.metrics = {}
    
    async def track_security_incident(self, incident_type: str, severity: str):
        """Track security incidents."""
        key = f"incidents_{incident_type}_{severity}"
        self.metrics[key] = self.metrics.get(key, 0) + 1
    
    async def track_failed_login_attempts(self, user_id: str):
        """Track failed login attempts."""
        key = f"failed_logins_{user_id}"
        self.metrics[key] = self.metrics.get(key, 0) + 1
    
    async def track_suspicious_activity(self, activity_type: str):
        """Track suspicious activities."""
        key = f"suspicious_{activity_type}"
        self.metrics[key] = self.metrics.get(key, 0) + 1
    
    async def get_security_dashboard_data(self) -> dict:
        """Get data for security dashboard."""
        return {
            "total_incidents": sum(v for k, v in self.metrics.items() if "incidents" in k),
            "failed_logins": sum(v for k, v in self.metrics.items() if "failed_logins" in k),
            "suspicious_activities": sum(v for k, v in self.metrics.items() if "suspicious" in k),
            "security_score": self.calculate_security_score()
        }
    
    def calculate_security_score(self) -> float:
        """Calculate overall security score."""
        # Implement scoring algorithm
        return 85.0  # Placeholder
```

### 4.2 Monitoring Dashboard
```python
# backend/app/api/v1/endpoints/security_dashboard.py
from fastapi import APIRouter, Depends
from app.services.security_metrics import SecurityMetrics
from app.core.security import require_permission

router = APIRouter()
security_metrics = SecurityMetrics()

@router.get("/dashboard")
@require_permission("security:read")
async def get_security_dashboard():
    """Get security dashboard data."""
    return await security_metrics.get_security_dashboard_data()

@router.get("/incidents")
@require_permission("security:read")
async def get_security_incidents(days: int = 30):
    """Get recent security incidents."""
    # Implement incident retrieval
    return {"incidents": []}

@router.get("/threats")
@require_permission("security:read")
async def get_threat_analysis():
    """Get threat analysis data."""
    # Implement threat analysis
    return {"threats": []}
```

---

## 🎯 Erfolgskriterien

### Phase 1 (Woche 1-2)
- [ ] Alle Secrets aus Code entfernt
- [ ] Netzwerk-Ports geschlossen
- [ ] Security-Headers implementiert
- [ ] Container-Härtung durchgeführt

### Phase 2 (Woche 3-6)
- [ ] MFA implementiert
- [ ] Threat Detection aktiv
- [ ] Data Encryption implementiert
- [ ] Security Monitoring läuft

### Phase 3 (Woche 7-12)
- [ ] Zero-Trust Architecture implementiert
- [ ] Automated Security Testing läuft
- [ ] Compliance Framework aktiv
- [ ] Security Dashboard verfügbar

### Gesamtziel
- **Security Score**: > 90%
- **Security Incidents**: 0 pro Monat
- **Compliance**: 100% GDPR-konform
- **Vulnerabilities**: 0 kritische Schwachstellen

---

## 📞 Support & Escalation

### Bei kritischen Sicherheitsvorfällen:
1. **Sofort**: Security Lead kontaktieren
2. **Innerhalb 1 Stunde**: Incident Response Team aktivieren
3. **Innerhalb 4 Stunden**: Stakeholder informieren
4. **Innerhalb 24 Stunden**: Post-Incident Review

### Kontakte:
- **Security Lead**: [Name] - [Email] - [Phone]
- **Incident Response**: [Name] - [Email] - [Phone]
- **Management Escalation**: [Name] - [Email] - [Phone]

---

*Dieser Action-Plan ist ein lebendes Dokument und wird kontinuierlich aktualisiert.*