# SSO Setup Guide

## Overview

ConvoSphere supports comprehensive Single Sign-On (SSO) integration with multiple providers configured via environment variables.

## Supported Providers

- **Google OAuth2**: Gmail and Google Workspace users
- **Microsoft Azure AD**: Enterprise users
- **GitHub OAuth**: Developer accounts
- **SAML 2.0**: Enterprise SSO integration
- **OpenID Connect**: Modern identity providers

## Quick Setup

### 1. Environment Configuration

Add SSO variables to your `.env` file:

```bash
# Google OAuth2
SSO_GOOGLE_ENABLED=true
SSO_GOOGLE_CLIENT_ID=your-google-client-id
SSO_GOOGLE_CLIENT_SECRET=your-google-client-secret
SSO_GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/sso/callback/google

# Microsoft Azure AD
SSO_MICROSOFT_ENABLED=true
SSO_MICROSOFT_CLIENT_ID=your-microsoft-client-id
SSO_MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret
SSO_MICROSOFT_TENANT_ID=your-tenant-id

# GitHub OAuth
SSO_GITHUB_ENABLED=true
SSO_GITHUB_CLIENT_ID=your-github-client-id
SSO_GITHUB_CLIENT_SECRET=your-github-client-secret
SSO_GITHUB_REDIRECT_URI=http://localhost:8000/api/v1/auth/sso/callback/github
```

### 2. Provider Setup

#### Google OAuth2
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add redirect URI: `http://localhost:8000/api/v1/auth/sso/callback/google`

#### Microsoft Azure AD
1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to Azure Active Directory > App registrations
3. Create new registration
4. Add redirect URI: `http://localhost:8000/api/v1/auth/sso/callback/microsoft`

#### GitHub OAuth
1. Go to [GitHub Settings > Developer settings > OAuth Apps](https://github.com/settings/developers)
2. Create new OAuth App
3. Add redirect URI: `http://localhost:8000/api/v1/auth/sso/callback/github`

### 3. Testing

```bash
# Check SSO providers
curl http://localhost:8000/api/v1/auth/sso/providers

# Test specific provider
curl http://localhost:8000/api/v1/auth/sso/oauth/google/login
```

## API Endpoints

- `GET /api/v1/auth/sso/providers` - List available providers
- `GET /api/v1/auth/sso/providers/{provider}/config` - Get provider config (admin only)
- `GET /api/v1/auth/sso/oauth/{provider}/login` - Initiate OAuth flow
- `POST /api/v1/auth/sso/oauth/{provider}/callback` - OAuth callback

## Security Notes

- Client secrets are automatically hidden in API responses
- SSO configuration is loaded from environment variables only
- No runtime configuration changes allowed
- All SSO flows include CSRF protection