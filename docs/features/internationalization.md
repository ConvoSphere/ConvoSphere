# Internationalization (i18n) Features

## Overview

The ChatAssistant platform provides comprehensive internationalization support with state-of-the-art features for handling multiple languages, including non-Latin scripts and right-to-left (RTL) languages.

## Supported Languages

The platform currently supports the following languages:

| Language | Code | Native Name | Direction | Status |
|----------|------|-------------|-----------|--------|
| English | `en` | English | LTR | ✅ Complete |
| German | `de` | Deutsch | LTR | ✅ Complete |
| French | `fr` | Français | LTR | ✅ Complete |
| Spanish | `es` | Español | LTR | ✅ Complete |
| Arabic | `ar` | العربية | RTL | ✅ Complete |
| Japanese | `ja` | 日本語 | LTR | ✅ Complete |

### Language Features

- **UTF-8 Encoding**: All translations use UTF-8 encoding for proper character support
- **RTL Support**: Arabic language includes full right-to-left text direction support
- **Native Names**: Each language displays its name in its native script
- **Fallback System**: Automatic fallback to English if translation is missing

## Backend Implementation

### Core Components

#### I18nManager

The main internationalization manager handles:

- Language detection from HTTP headers and query parameters
- Translation loading and caching
- RTL language detection
- Fallback translation handling

```python
from app.core.i18n import i18n_manager

# Get supported languages
languages = i18n_manager.get_supported_languages()

# Check if language is RTL
is_rtl = i18n_manager.is_rtl('ar')  # True for Arabic

# Translate text
translation = i18n_manager.translate('common.success', 'ar')  # نجح
```

#### I18nMiddleware

FastAPI middleware that automatically:

- Detects the user's preferred language
- Sets language context for each request
- Adds language headers to responses
- Handles RTL direction detection

### API Endpoints

#### GET `/api/v1/i18n/languages`

Returns list of supported languages with metadata:

```json
[
  {
    "code": "en",
    "name": "English",
    "native_name": "English",
    "direction": "ltr"
  },
  {
    "code": "ar",
    "name": "Arabic",
    "native_name": "العربية",
    "direction": "rtl"
  }
]
```

#### GET `/api/v1/i18n/current`

Returns current language information for the request:

```json
{
  "language": "ar",
  "is_rtl": true,
  "info": {
    "code": "ar",
    "name": "Arabic",
    "native_name": "العربية",
    "direction": "rtl"
  }
}
```

#### GET `/api/v1/i18n/translations`

Retrieves translations for the current language:

```bash
# Get all translations
GET /api/v1/i18n/translations

# Get specific namespace
GET /api/v1/i18n/translations?namespace=auth

# Get specific keys
GET /api/v1/i18n/translations?keys=common.success,common.error
```

#### POST `/api/v1/i18n/translate`

Translates specific text to target language:

```json
{
  "text": "common.success",
  "target_language": "ar"
}
```

Response:
```json
{
  "original": "common.success",
  "translated": "نجح",
  "language": "ar",
  "is_rtl": true
}
```

#### GET `/api/v1/i18n/health`

Health check for the i18n system:

```json
{
  "status": "healthy",
  "supported_languages": 6,
  "loaded_languages": 6,
  "default_language": "en",
  "rtl_languages": ["ar"]
}
```

## Language Detection

The system detects the user's preferred language in the following order:

1. **Query Parameter**: `?lang=ar`
2. **Accept-Language Header**: `Accept-Language: ar-SA,ar;q=0.9,en;q=0.8`
3. **User Preference**: From user profile (future feature)
4. **Default Language**: English (`en`)

### Example Usage

```bash
# Set language via query parameter
curl "https://api.chatassistant.com/api/v1/conversations?lang=ar"

# Set language via header
curl -H "Accept-Language: ar-SA,ar;q=0.9" \
     "https://api.chatassistant.com/api/v1/conversations"
```

## Translation Structure

Translations are organized in JSON files with nested structure:

```json
{
  "common": {
    "success": "نجح",
    "error": "خطأ",
    "loading": "جاري التحميل..."
  },
  "auth": {
    "login_success": "تم تسجيل الدخول بنجاح",
    "login_failed": "فشل تسجيل الدخول"
  }
}
```

### Translation Keys

Use dot notation for nested keys:

```python
# Access nested translation
translation = i18n_manager.translate('auth.login_success', 'ar')
```

## RTL Language Support

### Arabic Language Features

- **Text Direction**: Right-to-left (RTL) text flow
- **Character Support**: Full Arabic Unicode character support
- **Number Formatting**: Arabic numerals and formatting
- **Date Formatting**: Arabic calendar and date formats

### Frontend Integration

For RTL languages, the frontend should:

1. Set `dir="rtl"` on HTML elements
2. Use CSS `direction: rtl` for text containers
3. Mirror layout elements (navigation, buttons, etc.)
4. Handle bidirectional text properly

```css
/* RTL support in CSS */
[dir="rtl"] .container {
  direction: rtl;
  text-align: right;
}

[dir="rtl"] .button {
  margin-left: 0;
  margin-right: 10px;
}
```

## Adding New Languages

### 1. Create Translation File

Create a new JSON file in `backend/app/translations/`:

```json
// backend/app/translations/zh.json
{
  "common": {
    "success": "成功",
    "error": "错误"
  }
}
```

### 2. Update Configuration

Add the language to the supported languages list in `backend/app/core/config.py`:

```python
supported_languages: List[str] = Field(
    default=["en", "de", "fr", "es", "ar", "ja", "zh"], 
    description="Supported languages"
)
```

### 3. Add Language Metadata

Update the language info in `backend/app/core/i18n.py`:

```python
self.language_info = {
    # ... existing languages ...
    "zh": LanguageInfo("zh", "Chinese", "中文", "ltr"),
}
```

### 4. Test the Implementation

```python
# Test new language
translation = i18n_manager.translate('common.success', 'zh')
print(translation)  # 成功
```

## Best Practices

### Translation Guidelines

1. **Use Descriptive Keys**: Use hierarchical keys like `auth.login_success`
2. **Maintain Consistency**: Keep translation keys consistent across languages
3. **Handle Parameters**: Use string formatting for dynamic content
4. **Test RTL**: Verify RTL languages display correctly
5. **Cultural Sensitivity**: Consider cultural differences in translations

### Performance Considerations

1. **Caching**: Translations are loaded once and cached in memory
2. **Lazy Loading**: Only load translations for supported languages
3. **Fallback Chain**: Efficient fallback to default language
4. **Memory Usage**: Monitor memory usage with many languages

### Security Considerations

1. **Input Validation**: Validate language codes to prevent injection
2. **File Access**: Secure access to translation files
3. **Admin Controls**: Restrict translation reload to administrators
4. **Audit Logging**: Log translation changes for compliance

## Future Enhancements

### Planned Features

1. **User Language Preferences**: Store user language preference in database
2. **Dynamic Translation Loading**: Load translations on-demand
3. **Translation Management UI**: Web interface for managing translations
4. **Machine Translation Integration**: Automatic translation suggestions
5. **Pluralization Support**: Handle plural forms correctly
6. **Date/Time Localization**: Proper date and time formatting per locale
7. **Number Formatting**: Localized number and currency formatting

### Additional Languages

Potential additions:
- Russian (`ru`)
- Portuguese (`pt`)
- Italian (`it`)
- Korean (`ko`)
- Hindi (`hi`)
- Turkish (`tr`)

## Troubleshooting

### Common Issues

1. **Missing Translations**: Check if translation file exists and is valid JSON
2. **Encoding Issues**: Ensure all files use UTF-8 encoding
3. **RTL Display Problems**: Verify CSS and HTML direction attributes
4. **Language Detection**: Check Accept-Language header format

### Debug Commands

```python
# Check loaded languages
python -c "from app.core.i18n import i18n_manager; print(i18n_manager.translations.keys())"

# Test specific translation
python -c "from app.core.i18n import i18n_manager; print(i18n_manager.translate('common.success', 'ar'))"

# Check RTL support
python -c "from app.core.i18n import i18n_manager; print(i18n_manager.is_rtl('ar'))"
```

## API Documentation

For complete API documentation, see the interactive Swagger UI at:
`https://api.chatassistant.com/docs`

The i18n endpoints are available under the "internationalization" tag. 