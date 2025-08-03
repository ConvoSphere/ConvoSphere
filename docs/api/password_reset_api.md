# Password Reset API Documentation

## Overview

The Password Reset API provides endpoints for secure password reset functionality. This API implements multiple security measures including rate limiting, CSRF protection, and comprehensive audit logging.

## Base URL

```
https://your-domain.com/api/v1/auth
```

## Authentication

Most password reset endpoints do not require authentication, as they are designed for users who cannot log in. However, some endpoints may require CSRF tokens for additional security.

## Endpoints

### 1. Request Password Reset

Initiates a password reset process by sending a reset email to the user.

**Endpoint:** `POST /forgot-password`

**Description:** Sends a password reset email if the user exists. For security reasons, this endpoint always returns success even if the email doesn't exist.

#### Request

```http
POST /api/v1/auth/forgot-password
Content-Type: application/json
```

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Parameters:**
- `email` (string, required): The email address of the user requesting password reset

#### Response

**Success Response (200 OK):**
```json
{
  "message": "If the email address exists, a password reset link has been sent.",
  "status": "success"
}
```

**Rate Limit Exceeded (429 Too Many Requests):**
```json
{
  "detail": "Too many password reset requests. Please try again later."
}
```

**Server Error (500 Internal Server Error):**
```json
{
  "detail": "An error occurred while processing your request"
}
```

#### Rate Limiting

- **IP-based limit:** 5 requests per IP address per hour
- **Email-based limit:** 3 requests per email address per hour
- **Window:** 1 hour (3600 seconds)

#### Example

```bash
curl -X POST "https://your-domain.com/api/v1/auth/forgot-password" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

### 2. Reset Password

Resets the user's password using a valid reset token.

**Endpoint:** `POST /reset-password`

**Description:** Resets the user's password using a valid token obtained from the password reset email.

#### Request

```http
POST /api/v1/auth/reset-password
Content-Type: application/json
```

**Request Body:**
```json
{
  "token": "valid-reset-token-123",
  "new_password": "NewSecurePassword123!"
}
```

**Parameters:**
- `token` (string, required): The password reset token from the email
- `new_password` (string, required): The new password (must meet security requirements)

**Password Requirements:**
- Minimum 8 characters
- Must contain at least one uppercase letter
- Must contain at least one lowercase letter
- Must contain at least one digit
- Must contain at least one special character (@$!%*?&)

#### Response

**Success Response (200 OK):**
```json
{
  "message": "Password reset successfully",
  "status": "success"
}
```

**Invalid Token (400 Bad Request):**
```json
{
  "detail": "Invalid or expired token"
}
```

**Weak Password (400 Bad Request):**
```json
{
  "detail": "Password does not meet security requirements"
}
```

**Server Error (500 Internal Server Error):**
```json
{
  "detail": "An error occurred while resetting your password"
}
```

#### Example

```bash
curl -X POST "https://your-domain.com/api/v1/auth/reset-password" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "valid-reset-token-123",
    "new_password": "NewSecurePassword123!"
  }'
```

### 3. Validate Reset Token

Validates a password reset token without resetting the password.

**Endpoint:** `POST /validate-reset-token`

**Description:** Checks if a password reset token is valid and not expired. This is useful for frontend validation before showing the password reset form.

#### Request

```http
POST /api/v1/auth/validate-reset-token
Content-Type: application/json
```

**Request Body:**
```json
{
  "token": "valid-reset-token-123"
}
```

**Parameters:**
- `token` (string, required): The password reset token to validate

#### Response

**Valid Token (200 OK):**
```json
{
  "valid": true,
  "message": "Token is valid"
}
```

**Invalid Token (200 OK):**
```json
{
  "valid": false,
  "message": "Token is invalid or expired"
}
```

**Server Error (500 Internal Server Error):**
```json
{
  "detail": "An error occurred while validating the token"
}
```

#### Example

```bash
curl -X POST "https://your-domain.com/api/v1/auth/validate-reset-token" \
  -H "Content-Type: application/json" \
  -d '{"token": "valid-reset-token-123"}'
```

### 4. Generate CSRF Token

Generates a CSRF token for form protection.

**Endpoint:** `GET /csrf-token`

**Description:** Generates a CSRF token that can be used to protect sensitive forms from cross-site request forgery attacks.

#### Request

```http
GET /api/v1/auth/csrf-token
```

**Optional Headers:**
- `X-Session-ID`: Custom session identifier for token binding

#### Response

**Success Response (200 OK):**
```json
{
  "csrf_token": "generated-csrf-token-123",
  "expires_in": 1800,
  "session_id": "session-123"
}
```

**Parameters:**
- `csrf_token` (string): The generated CSRF token
- `expires_in` (integer): Token expiration time in seconds (30 minutes)
- `session_id` (string): Session identifier for token binding

**Server Error (500 Internal Server Error):**
```json
{
  "detail": "An error occurred while generating CSRF token"
}
```

#### Example

```bash
curl -X GET "https://your-domain.com/api/v1/auth/csrf-token" \
  -H "X-Session-ID: session-123"
```

## Error Codes

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid input or token |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |

### Error Response Format

All error responses follow this format:

```json
{
  "detail": "Error message description"
}
```

## Security Features

### Rate Limiting

The API implements rate limiting to prevent abuse:

- **IP-based limiting:** 5 requests per IP per hour
- **Email-based limiting:** 3 requests per email per hour
- **Configurable limits:** All limits can be adjusted via environment variables

### CSRF Protection

CSRF tokens provide additional security:

- **Token generation:** 32-character cryptographically secure tokens
- **Expiration:** 30 minutes by default
- **Session binding:** Tokens can be bound to specific sessions
- **One-time use:** Tokens are consumed after validation

### Audit Logging

All password reset activities are logged:

- **Event types:** Request, completion, failure, token generation/validation
- **Logged data:** IP address, user agent, email, success/failure status
- **Compliance:** GDPR and security standard compliant logging

## Token Security

### Password Reset Tokens

- **Length:** 32 characters
- **Algorithm:** Cryptographically secure random generation
- **Expiration:** 60 minutes (configurable)
- **Storage:** Securely hashed in database
- **One-time use:** Tokens are cleared after password reset

### Token Validation

Tokens are validated for:
- **Existence:** Token exists in database
- **Expiration:** Token hasn't expired
- **User association:** Token belongs to valid user

## Email Security

### Email Content

- **No sensitive data:** Reset tokens are not included in email content
- **Secure links:** Reset URLs use HTTPS
- **Expiration notice:** Clear indication of token expiration time
- **Multi-language:** Support for multiple languages

### Email Delivery

- **SMTP over TLS:** Secure email transmission
- **Background processing:** Asynchronous email sending
- **Delivery confirmation:** Email service confirms successful delivery

## Configuration

### Environment Variables

```bash
# Password Reset Configuration
PASSWORD_RESET_TOKEN_EXPIRE_MINUTES=60
PASSWORD_RESET_BASE_URL=https://yourdomain.com

# Rate Limiting Configuration
PASSWORD_RESET_RATE_LIMIT_IP_MAX=5
PASSWORD_RESET_RATE_LIMIT_EMAIL_MAX=3
PASSWORD_RESET_RATE_LIMIT_WINDOW=3600

# CSRF Protection Configuration
CSRF_TOKEN_EXPIRE_MINUTES=30
CSRF_PROTECTION_ENABLED=true
```

## Best Practices

### Client Implementation

1. **Always validate tokens:** Use the validation endpoint before showing reset forms
2. **Handle rate limiting:** Implement proper error handling for 429 responses
3. **Use CSRF tokens:** Include CSRF tokens in sensitive form submissions
4. **Secure password requirements:** Enforce password requirements on the client side
5. **User feedback:** Provide clear feedback for all success and error states

### Security Considerations

1. **No information disclosure:** Don't reveal if an email exists in the system
2. **Secure token handling:** Never expose tokens in logs or error messages
3. **HTTPS only:** Always use HTTPS for all API communications
4. **Input validation:** Validate all inputs on both client and server
5. **Audit monitoring:** Monitor audit logs for suspicious activity

## Testing

### Test Scenarios

1. **Valid password reset flow**
2. **Invalid email addresses**
3. **Expired tokens**
4. **Rate limiting**
5. **Network errors**
6. **CSRF token validation**
7. **Password strength validation**

### Test Data

```json
{
  "valid_email": "test@example.com",
  "invalid_email": "invalid-email",
  "valid_token": "valid-reset-token-123",
  "expired_token": "expired-token-456",
  "weak_password": "123",
  "strong_password": "NewSecurePassword123!"
}
```

## Support

For API support and questions:

- **Documentation:** This document and related guides
- **Error logs:** Check server logs for detailed error information
- **Security issues:** Report security issues through proper channels
- **Feature requests:** Submit feature requests through the development team

## Changelog

### Version 1.0.0
- Initial implementation of password reset API
- Rate limiting and CSRF protection
- Comprehensive audit logging
- Multi-language email support