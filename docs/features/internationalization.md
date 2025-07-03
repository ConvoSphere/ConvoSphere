# Internationalization (i18n)

## Overview

The AI Assistant Platform supports multiple languages through a comprehensive internationalization system. Currently, English and German are supported, with the ability to easily add more languages.

## Features

### Language Detection
- **HTTP Headers**: Automatic detection via `Accept-Language` header
- **Query Parameters**: Manual language selection via `?lang=de`
- **Fallback**: Default to English if language not supported

### Translation Management
- **JSON-based**: Translations stored in JSON files
- **Hierarchical**: Organized by feature (auth, user, assistant, etc.)
- **Parameter Substitution**: Support for dynamic content in translations

### API Integration
- **Automatic Translation**: API responses translated based on detected language
- **Middleware**: FastAPI middleware for language detection
- **Headers**: Content-Language header added to responses

## Supported Languages

| Language | Code | Display Name |
|----------|------|--------------|
| English  | en   | English      |
| German   | de   | Deutsch      |

## Usage

### Setting Language

#### Via Query Parameter
```
GET /api/v1/assistants?lang=de
```

#### Via HTTP Header
```
Accept-Language: de-DE,de;q=0.9,en;q=0.8
```

### Translation Keys

Translations are organized by feature:

```json
{
  "auth": {
    "login_success": "Login successful",
    "login_failed": "Login failed"
  },
  "user": {
    "user_created": "User created successfully"
  },
  "assistant": {
    "assistant_created": "Assistant created successfully"
  }
}
```

### Parameter Substitution

Translations support dynamic content:

```json
{
  "validation": {
    "required_field": "{field} is required"
  }
}
```

Usage in code:
```python
t("validation.required_field", request, field="email")
# Result: "email is required"
```

## Implementation

### Backend

The i18n system is implemented in `backend/app/core/i18n.py`:

- **I18nManager**: Main translation management class
- **I18nMiddleware**: FastAPI middleware for language detection
- **Translation Files**: Located in `backend/app/translations/`

### Frontend

Frontend translations are stored in `frontend/i18n/`:

- **en.json**: English translations
- **de.json**: German translations

## Adding New Languages

1. **Create Translation File**:
   ```bash
   # Backend
   cp backend/app/translations/en.json backend/app/translations/fr.json
   
   # Frontend
   cp frontend/i18n/en.json frontend/i18n/fr.json
   ```

2. **Update Supported Languages**:
   ```python
   # In I18nManager.__init__()
   self.supported_languages = ["en", "de", "fr"]
   ```

3. **Add Display Name**:
   ```python
   def get_supported_languages(self) -> Dict[str, str]:
       return {
           "en": "English",
           "de": "Deutsch",
           "fr": "Français"
       }
   ```

## Translation Categories

### Common
General UI elements and actions (success, error, loading, etc.)

### Authentication
Login, registration, and authentication-related messages

### User Management
User profile, account management messages

### Assistants
Assistant creation, configuration, and management

### Conversations
Chat and conversation-related messages

### Knowledge Base
Document upload, processing, and search messages

### Tools
Tool execution and MCP-related messages

### Validation
Form validation and input error messages

### Errors
System error messages and status codes

### WebSocket
Real-time communication messages

### Health
Service health and status messages

## Best Practices

1. **Use Descriptive Keys**: Choose clear, hierarchical translation keys
2. **Parameter Substitution**: Use parameters for dynamic content
3. **Fallback Handling**: Always provide fallback to default language
4. **Consistent Naming**: Follow established naming conventions
5. **Context Awareness**: Consider cultural differences in translations

## Future Enhancements

- **RTL Support**: Right-to-left language support (Arabic, Hebrew)
- **Pluralization**: Advanced pluralization rules
- **Date/Time Formatting**: Locale-specific date and time formats
- **Number Formatting**: Locale-specific number formats
- **Currency Support**: Multi-currency display 