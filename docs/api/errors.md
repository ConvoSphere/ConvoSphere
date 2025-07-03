# API Error Reference

## Overview

This page lists all common error codes, their meaning, and example error responses for the API.

## Error Codes

| Code | Meaning                  | Typical Cause                        |
|------|--------------------------|--------------------------------------|
| 400  | Bad Request              | Invalid input, missing parameters    |
| 401  | Unauthorized             | Invalid or missing authentication    |
| 403  | Forbidden                | Insufficient permissions             |
| 404  | Not Found                | Resource does not exist              |
| 409  | Conflict                 | Duplicate resource, already exists   |
| 422  | Validation Error         | Input validation failed              |
| 429  | Too Many Requests        | Rate limit exceeded                  |
| 500  | Internal Server Error    | Unexpected server error              |

## Example Error Responses

### 400 Bad Request
```json
{
  "detail": "Missing required field: email",
  "status_code": 400
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid credentials",
  "status_code": 401
}
```

### 403 Forbidden
```json
{
  "detail": "Admin privileges required",
  "status_code": 403
}
```

### 404 Not Found
```json
{
  "detail": "User does not exist",
  "status_code": 404
}
```

### 409 Conflict
```json
{
  "detail": "Email already registered",
  "status_code": 409
}
```

### 422 Validation Error
```json
{
  "detail": [
    {"loc": ["body", "email"], "msg": "value is not a valid email address", "type": "value_error.email"}
  ],
  "status_code": 422
}
```

### 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded",
  "status_code": 429
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error",
  "status_code": 500
}
``` 