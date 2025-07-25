# SSO (Single Sign-On) Integration Guide

## Übersicht

Das AI Assistant Platform unterstützt verschiedene SSO-Provider für die Authentifizierung:

- **Google OAuth2** - Für Google Workspace und persönliche Google-Konten
- **Microsoft OAuth2** - Für Azure AD und Microsoft 365
- **GitHub OAuth2** - Für GitHub-Konten
- **SAML** - Für Enterprise Identity Provider
- **OIDC** - Für OpenID Connect Provider (geplant)

## 🚀 Schnellstart

### 1. Environment Variables konfigurieren

Fügen Sie die folgenden Variablen zu Ihrer `.env` Datei hinzu:

```bash
# Google OAuth2
SSO_GOOGLE_ENABLED=true
SSO_GOOGLE_CLIENT_ID=your-google-client-id
SSO_GOOGLE_CLIENT_SECRET=your-google-client-secret
SSO_GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/sso/callback/google

# Microsoft OAuth2
SSO_MICROSOFT_ENABLED=true
SSO_MICROSOFT_CLIENT_ID=your-microsoft-client-id
SSO_MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret
SSO_MICROSOFT_TENANT_ID=your-microsoft-tenant-id
SSO_MICROSOFT_REDIRECT_URI=http://localhost:8000/api/v1/auth/sso/callback/microsoft

# GitHub OAuth2
SSO_GITHUB_ENABLED=true
SSO_GITHUB_CLIENT_ID=your-github-client-id
SSO_GITHUB_CLIENT_SECRET=your-github-client-secret
SSO_GITHUB_REDIRECT_URI=http://localhost:8000/api/v1/auth/sso/callback/github

# SAML Configuration
SSO_SAML_ENABLED=true
SSO_SAML_METADATA_URL=https://idp.example.com/metadata
SSO_SAML_ENTITY_ID=http://localhost:8000
SSO_SAML_ACS_URL=http://localhost:8000/api/v1/auth/sso/callback/saml
SSO_SAML_CERT_FILE=/path/to/certificate.crt
SSO_SAML_KEY_FILE=/path/to/private.key
```

### 2. SSO Provider konfigurieren

#### Google OAuth2 Setup

1. Gehen Sie zur [Google Cloud Console](https://console.cloud.google.com/)
2. Erstellen Sie ein neues Projekt oder wählen Sie ein bestehendes
3. Aktivieren Sie die Google+ API
4. Gehen Sie zu "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
5. Wählen Sie "Web application"
6. Fügen Sie die Redirect URI hinzu: `http://localhost:8000/api/v1/auth/sso/callback/google`
7. Kopieren Sie Client ID und Client Secret

#### Microsoft OAuth2 Setup

1. Gehen Sie zum [Azure Portal](https://portal.azure.com/)
2. Navigieren Sie zu "Azure Active Directory" → "App registrations"
3. Klicken Sie auf "New registration"
4. Geben Sie einen Namen ein und wählen Sie "Accounts in this organizational directory only"
5. Gehen Sie zu "Authentication" → "Add a platform" → "Web"
6. Fügen Sie die Redirect URI hinzu: `http://localhost:8000/api/v1/auth/sso/callback/microsoft`
7. Gehen Sie zu "Certificates & secrets" und erstellen Sie ein neues Client Secret
8. Kopieren Sie Application (client) ID und Client Secret

#### GitHub OAuth2 Setup

1. Gehen Sie zu [GitHub Settings](https://github.com/settings/developers)
2. Klicken Sie auf "New OAuth App"
3. Füllen Sie die Felder aus:
   - Application name: AI Assistant Platform
   - Homepage URL: `http://localhost:8000`
   - Authorization callback URL: `http://localhost:8000/api/v1/auth/sso/callback/github`
4. Kopieren Sie Client ID und Client Secret

#### SAML Setup

1. **IdP Metadata URL konfigurieren**
   - Stellen Sie sicher, dass Ihr Identity Provider eine Metadata URL bereitstellt
   - Die URL sollte SAML 2.0 Metadata im XML-Format zurückgeben

2. **Certificate und Private Key (optional)**
   - Für Produktionsumgebungen sollten Sie ein gültiges SSL-Zertifikat verwenden
   - Für Tests werden automatisch temporäre Zertifikate erstellt

3. **SAML Metadata abrufen**
   ```bash
   curl http://localhost:8000/api/v1/auth/sso/metadata
   ```
   - Verwenden Sie diese Metadata in Ihrem Identity Provider

4. **IdP konfigurieren**
   - Entity ID: `http://localhost:8000`
   - ACS URL: `http://localhost:8000/api/v1/auth/sso/callback/saml`
   - Name ID Format: `urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress`

### 3. Backend starten

```bash
cd backend
python3 main.py
```

### 4. Frontend starten

```bash
cd frontend-react
npm install
npm run dev
```

## 🔧 API Endpoints

### SSO Provider Liste abrufen

```http
GET /api/v1/auth/sso/providers
```

**Response:**
```json
{
  "providers": [
    {
      "id": "google",
      "name": "Google",
      "type": "oauth2",
      "icon": "google",
      "login_url": "/api/v1/auth/sso/login/google"
    }
  ]
}
```

### SSO Login initiieren

```http
GET /api/v1/auth/sso/login/{provider}
```

**Parameter:**
- `provider`: SSO provider (google, microsoft, github, saml)

**Response:** Redirect zur OAuth Provider Login-Seite

### SSO Callback

```http
GET /api/v1/auth/sso/callback/{provider}
```

**Parameter:**
- `provider`: SSO provider (google, microsoft, github, saml)
- `code`: Authorization code von OAuth Provider (nur für OAuth2)
- `state`: State parameter für CSRF-Schutz (nur für OAuth2)
- `SAMLResponse`: Base64-encoded SAML response (nur für SAML)

**Response:**
```json
{
  "access_token": "jwt-access-token",
  "refresh_token": "jwt-refresh-token",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### SSO Account verknüpfen

```http
POST /api/v1/auth/sso/link/{provider}
Authorization: Bearer {access_token}
```

**Parameter:**
- `provider`: SSO provider (google, microsoft, github, saml)

**Response:**
```json
{
  "message": "SSO account linked for google"
}
```

### SAML Metadata

```http
GET /api/v1/auth/sso/metadata
```

**Response:** SAML 2.0 Metadata XML

**Verwendung:**
- Diese Metadata wird benötigt, um den Service Provider in Ihrem Identity Provider zu konfigurieren
- Die Metadata enthält alle notwendigen Endpoints und Zertifikate

## 🔐 Sicherheit

### CSRF Protection

Alle OAuth Flows verwenden State-Parameter für CSRF-Schutz.

### Token Management

- **Access Token**: 30 Minuten Gültigkeit (konfigurierbar)
- **Refresh Token**: 7 Tage Gültigkeit (konfigurierbar)
- **Token Blacklisting**: Unterstützt via Redis

### Audit Logging

Alle SSO-Events werden protokolliert:

```python
log_security_event(
    event_type="sso_login",
    user_id=user.id,
    description=f"User {user.email} logged in via SSO ({provider})",
    severity="info"
)
```

## 👥 User Provisioning

### Automatische User-Erstellung

Wenn ein User sich zum ersten Mal über SSO anmeldet:

1. User-Info wird vom OAuth Provider abgerufen
2. Username wird automatisch generiert (falls nicht vorhanden)
3. User wird mit `is_verified=True` erstellt
4. SSO-Attribute werden gespeichert

### User-Attribute Mapping

| SSO Provider | Email | External ID | First Name | Last Name | Display Name | Avatar |
|--------------|-------|-------------|------------|-----------|--------------|--------|
| Google | ✅ | sub | given_name | family_name | name | picture |
| Microsoft | ✅ | sub | given_name | family_name | name | ❌ |
| GitHub | ✅ | id | name.split()[0] | name.split()[1:] | name | avatar_url |
| SAML | ✅ | uid/userid/employeeID | givenName/firstName | sn/lastName/surname | displayName/cn/commonName | ❌ |

### Account Linking

Bestehende User können SSO-Accounts verknüpfen:

1. User meldet sich mit lokalen Credentials an
2. User klickt auf "Link SSO Account"
3. OAuth Flow wird initiiert
4. SSO-Account wird mit bestehendem User verknüpft

## 🧪 Testing

### Unit Tests

```bash
cd backend
python3 -m pytest tests/test_sso.py -v
python3 -m pytest tests/test_saml.py -v
```

### Performance Tests

```bash
cd backend
python3 -m pytest tests/test_sso_performance.py -v
```

### Security Tests

```bash
cd backend
python3 -m pytest tests/test_sso.py::TestSSOSecurity -v
```

### Integration Tests

```bash
cd backend
python3 -m pytest tests/test_sso_integration.py -v
```

### Manuelles Testing

1. Starten Sie Backend und Frontend
2. Gehen Sie zur Login-Seite
3. Klicken Sie auf SSO-Button
4. Authentifizieren Sie sich beim OAuth Provider
5. Überprüfen Sie, dass Sie eingeloggt sind

## 🚨 Troubleshooting

### Häufige Probleme

#### "SSO is not configured"

**Ursache:** OAuth Provider ist nicht aktiviert oder konfiguriert

**Lösung:**
1. Überprüfen Sie die Environment Variables
2. Stellen Sie sicher, dass Client ID und Secret korrekt sind
3. Überprüfen Sie die Redirect URIs

#### "OAuth authentication failed"

**Ursache:** Fehler beim OAuth Flow

**Lösung:**
1. Überprüfen Sie die OAuth Provider Konfiguration
2. Stellen Sie sicher, dass Redirect URIs korrekt sind
3. Überprüfen Sie die Client Secrets

#### "User not found"

**Ursache:** User wurde nicht korrekt erstellt

**Lösung:**
1. Überprüfen Sie die User Service Logs
2. Stellen Sie sicher, dass die Datenbank migriert ist
3. Überprüfen Sie die User-Attribute Mapping

### Debugging

Aktivieren Sie Debug-Logging:

```bash
LOG_LEVEL=DEBUG
```

### Logs überprüfen

```bash
tail -f logs/app.log | grep -i sso
```

## 🔄 Deployment

### Production Setup

1. **HTTPS verwenden**: Alle Redirect URIs müssen HTTPS verwenden
2. **Domain konfigurieren**: Aktualisieren Sie Redirect URIs für Ihre Domain
3. **Secrets sichern**: Verwenden Sie sichere Secret Management
4. **Monitoring**: Überwachen Sie SSO-Logins und Fehler
5. **Security Hardening**: Zusätzliche Sicherheitsmaßnahmen aktivieren
6. **Performance Monitoring**: SSO-Performance überwachen

### Environment Variables (Production)

```bash
# Google OAuth2
SSO_GOOGLE_ENABLED=true
SSO_GOOGLE_CLIENT_ID=your-production-client-id
SSO_GOOGLE_CLIENT_SECRET=your-production-client-secret
SSO_GOOGLE_REDIRECT_URI=https://yourdomain.com/api/v1/auth/sso/callback/google

# Microsoft OAuth2
SSO_MICROSOFT_ENABLED=true
SSO_MICROSOFT_CLIENT_ID=your-production-client-id
SSO_MICROSOFT_CLIENT_SECRET=your-production-client-secret
SSO_MICROSOFT_TENANT_ID=your-tenant-id
SSO_MICROSOFT_REDIRECT_URI=https://yourdomain.com/api/v1/auth/sso/callback/microsoft

# GitHub OAuth2
SSO_GITHUB_ENABLED=true
SSO_GITHUB_CLIENT_ID=your-production-client-id
SSO_GITHUB_CLIENT_SECRET=your-production-client-secret
SSO_GITHUB_REDIRECT_URI=https://yourdomain.com/api/v1/auth/sso/callback/github

# SAML Configuration
SSO_SAML_ENABLED=true
SSO_SAML_METADATA_URL=https://your-idp.com/metadata
SSO_SAML_ENTITY_ID=https://yourdomain.com
SSO_SAML_ACS_URL=https://yourdomain.com/api/v1/auth/sso/callback/saml
SSO_SAML_CERT_FILE=/path/to/production/certificate.crt
SSO_SAML_KEY_FILE=/path/to/production/private.key

# Security Settings
SECRET_KEY=your-super-secure-secret-key
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```

## 🔒 Security Features

### Security Hardening

Die SSO-Integration enthält umfassende Sicherheitsmaßnahmen:

#### Rate Limiting
- **IP-basierte Rate Limiting** für SSO-Endpoints
- **Konfigurierbare Limits** (Standard: 10 Requests/Minute)
- **Automatische Blockierung** bei Überschreitung

#### Input Validation
- **URL-Validierung** für Redirect-URLs
- **SAML Response Validierung** gegen XSS-Angriffe
- **User-Attribute Sanitization** vor Speicherung

#### CSRF Protection
- **State-Parameter Validierung** für OAuth2
- **Sichere State-Generierung** mit `secrets.token_urlsafe()`
- **Session-basierte Validierung**

#### Audit Logging
- **Detaillierte Security Events** für alle SSO-Operationen
- **IP-Adress Tracking** für verdächtige Aktivitäten
- **Suspicious Pattern Detection**

### Monitoring & Alerting

```python
# Security Events abrufen
from app.core.security_hardening import sso_audit_logger

# Alle Events der letzten 24 Stunden
events = sso_audit_logger.get_security_events(hours=24)

# Verdächtige Events
suspicious = sso_audit_logger.get_suspicious_events(hours=24)
```

## 📊 Performance Monitoring

### Performance Metrics

Die SSO-Integration überwacht folgende Metriken:

- **Response Times**: Durchschnittliche Antwortzeiten
- **Throughput**: Requests pro Sekunde
- **Error Rates**: Fehlerquoten pro Provider
- **Memory Usage**: Speicherverbrauch unter Last
- **Concurrency**: Gleichzeitige Verbindungen

### Load Testing

```bash
# Performance Tests ausführen
python3 -m pytest tests/test_sso_performance.py::TestSSOPerformance -v

# Load Tests ausführen
python3 -m pytest tests/test_sso_performance.py::TestSSOLoadTesting -v
```

## 🚀 Advanced Features

### Account Linking

Die SSO-Integration unterstützt das Verknüpfen lokaler Konten mit SSO-Providern:

#### Frontend Components

```typescript
// Account Linking UI
import { SSOAccountLinking } from '../components/SSOAccountLinking';

<SSOAccountLinking 
  onSuccess={() => console.log('Account linked!')}
  onError={(error) => console.error('Linking failed:', error)}
/>
```

#### Backend Endpoints

```bash
# Account verknüpfen
POST /api/v1/auth/sso/link/{provider}

# Account entkoppeln
GET /api/v1/auth/sso/unlink/{provider}
```

### Advanced User Provisioning

#### Group/Role Mapping

```python
# Automatische Rollen-Zuweisung basierend auf SSO-Gruppen
group_mappings = {
    'google': {
        'admin': ['admin', 'administrator', 'super_admin'],
        'manager': ['manager', 'team_lead', 'supervisor'],
        'user': ['user', 'member', 'employee']
    }
}
```

#### Conditional Provisioning

```python
# Bedingte Benutzer-Erstellung basierend auf Regeln
provisioning_rules = {
    'allowed_domains': ['example.com', 'company.com'],
    'blocked_domains': ['temp.com', 'test.com'],
    'auto_approve_domains': ['trusted-partner.com'],
    'require_approval_domains': ['external-vendor.com']
}
```

#### Bulk Operations

```python
# Massen-Synchronisation von Benutzern
user_list = [
    {'email': 'user1@example.com', 'external_id': 'user1'},
    {'email': 'user2@example.com', 'external_id': 'user2'}
]

results = await advanced_user_provisioning.bulk_sync_users(
    'google', user_list, db
)
```

### SSO Provider Management

#### Admin Interface

```typescript
// Provider Management UI
import { SSOProviderManagement } from '../components/SSOProviderManagement';

<SSOProviderManagement 
  onProviderUpdate={() => console.log('Provider updated!')}
/>
```

#### Provider Status

- **Active**: Provider ist konfiguriert und aktiv
- **Disabled**: Provider ist konfiguriert aber deaktiviert
- **Not Configured**: Provider ist nicht konfiguriert

### Advanced API Endpoints

```bash
# Benutzer-Provisioning Status abrufen
GET /api/v1/auth/sso/provisioning/status/{user_id}

# Massen-Synchronisation (Admin)
POST /api/v1/auth/sso/bulk-sync/{provider}
```

### Attribute Mapping

#### Google OAuth2
```python
{
    'email': 'email',
    'given_name': 'first_name',
    'family_name': 'last_name',
    'name': 'display_name',
    'picture': 'avatar_url',
    'hd': 'domain',
    'groups': 'groups'
}
```

#### Microsoft OAuth2
```python
{
    'email': 'email',
    'given_name': 'first_name',
    'surname': 'last_name',
    'display_name': 'display_name',
    'job_title': 'job_title',
    'department': 'department',
    'groups': 'groups'
}
```

#### SAML
```python
{
    'email': 'email',
    'givenName': 'first_name',
    'sn': 'last_name',
    'displayName': 'display_name',
    'department': 'department',
    'title': 'job_title',
    'memberOf': 'groups'
}
```

## 📚 Weitere Ressourcen

- [OAuth 2.0 Specification](https://tools.ietf.org/html/rfc6749)
- [SAML 2.0 Specification](http://docs.oasis-open.org/security/saml/Post2.0/sstc-saml-tech-overview-2.0.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Authlib Documentation](https://authlib.org/)
- [OWASP SSO Security Guidelines](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/06-Session_Management_Testing/10-Testing_Single_Sign-On)

## 🤝 Support

Bei Problemen:

1. Überprüfen Sie die Logs
2. Testen Sie mit den Unit Tests
3. Überprüfen Sie die OAuth Provider Konfiguration
4. Erstellen Sie ein Issue im Repository