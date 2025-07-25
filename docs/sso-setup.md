# SSO (Single Sign-On) Integration Guide

## Übersicht

Das AI Assistant Platform unterstützt verschiedene SSO-Provider für die Authentifizierung:

- **Google OAuth2** - Für Google Workspace und persönliche Google-Konten
- **Microsoft OAuth2** - Für Azure AD und Microsoft 365
- **GitHub OAuth2** - Für GitHub-Konten
- **SAML** - Für Enterprise Identity Provider (geplant)
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
```

### 2. OAuth Provider konfigurieren

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
- `provider`: OAuth provider (google, microsoft, github)

**Response:** Redirect zur OAuth Provider Login-Seite

### SSO Callback

```http
GET /api/v1/auth/sso/callback/{provider}
```

**Parameter:**
- `provider`: OAuth provider (google, microsoft, github)
- `code`: Authorization code von OAuth Provider
- `state`: State parameter für CSRF-Schutz

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
- `provider`: OAuth provider (google, microsoft, github)

**Response:**
```json
{
  "message": "SSO account linked for google"
}
```

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

| OAuth Provider | Email | External ID | First Name | Last Name | Display Name | Avatar |
|----------------|-------|-------------|------------|-----------|--------------|--------|
| Google | ✅ | sub | given_name | family_name | name | picture |
| Microsoft | ✅ | sub | given_name | family_name | name | ❌ |
| GitHub | ✅ | id | name.split()[0] | name.split()[1:] | name | avatar_url |

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
```

## 📚 Weitere Ressourcen

- [OAuth 2.0 Specification](https://tools.ietf.org/html/rfc6749)
- [Google OAuth2 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Microsoft OAuth2 Documentation](https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow)
- [GitHub OAuth2 Documentation](https://docs.github.com/en/developers/apps/building-oauth-apps)

## 🤝 Support

Bei Problemen:

1. Überprüfen Sie die Logs
2. Testen Sie mit den Unit Tests
3. Überprüfen Sie die OAuth Provider Konfiguration
4. Erstellen Sie ein Issue im Repository