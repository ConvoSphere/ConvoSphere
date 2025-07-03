"""
Validation functions for the AI Assistant Platform frontend.

This module provides input validation functions used throughout
the frontend application.
"""

import re
from typing import Optional, Tuple, List, Dict, Any
from .constants import MAX_FILE_SIZE, SUPPORTED_FILE_TYPES
from datetime import datetime


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email:
        return False, "E-Mail-Adresse ist erforderlich"
    
    # Basic email format validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        return False, "Ungültiges E-Mail-Format"
    
    # Check for common issues
    if len(email) > 254:
        return False, "E-Mail-Adresse ist zu lang"
    
    if email.count('@') != 1:
        return False, "E-Mail-Adresse darf nur ein @-Zeichen enthalten"
    
    local_part, domain = email.split('@')
    
    if len(local_part) > 64:
        return False, "Lokaler Teil der E-Mail-Adresse ist zu lang"
    
    if len(domain) > 253:
        return False, "Domain-Teil der E-Mail-Adresse ist zu lang"
    
    return True, None


def validate_password(password: str) -> Tuple[bool, Optional[str]]:
    """
    Validate password strength.
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not password:
        return False, "Passwort ist erforderlich"
    
    if len(password) < 8:
        return False, "Passwort muss mindestens 8 Zeichen lang sein"
    
    if len(password) > 128:
        return False, "Passwort ist zu lang (maximal 128 Zeichen)"
    
    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False, "Passwort muss mindestens einen Großbuchstaben enthalten"
    
    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False, "Passwort muss mindestens einen Kleinbuchstaben enthalten"
    
    # Check for at least one digit
    if not re.search(r'\d', password):
        return False, "Passwort muss mindestens eine Zahl enthalten"
    
    # Check for at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Passwort muss mindestens ein Sonderzeichen enthalten"
    
    return True, None


def validate_username(username: str) -> Tuple[bool, Optional[str]]:
    """
    Validate username format.
    
    Args:
        username: Username to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not username:
        return False, "Benutzername ist erforderlich"
    
    if len(username) < 3:
        return False, "Benutzername muss mindestens 3 Zeichen lang sein"
    
    if len(username) > 30:
        return False, "Benutzername ist zu lang (maximal 30 Zeichen)"
    
    # Check for valid characters (alphanumeric, underscore, hyphen)
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, "Benutzername darf nur Buchstaben, Zahlen, Unterstriche und Bindestriche enthalten"
    
    # Check that username doesn't start or end with special characters
    if username.startswith('_') or username.startswith('-'):
        return False, "Benutzername darf nicht mit Unterstrichen oder Bindestrichen beginnen"
    
    if username.endswith('_') or username.endswith('-'):
        return False, "Benutzername darf nicht mit Unterstrichen oder Bindestrichen enden"
    
    # Check for consecutive special characters
    if re.search(r'[_-]{2,}', username):
        return False, "Benutzername darf keine aufeinanderfolgenden Unterstriche oder Bindestriche enthalten"
    
    return True, None


def validate_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url:
        return False, "URL ist erforderlich"
    
    # Basic URL pattern
    url_pattern = r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$'
    
    if not re.match(url_pattern, url):
        return False, "Ungültiges URL-Format"
    
    return True, None


def validate_file_size(file_size: int) -> Tuple[bool, Optional[str]]:
    """
    Validate file size.
    
    Args:
        file_size: File size in bytes
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if file_size <= 0:
        return False, "Datei ist leer"
    
    if file_size > MAX_FILE_SIZE:
        max_size_mb = MAX_FILE_SIZE / (1024 * 1024)
        return False, f"Datei ist zu groß (maximal {max_size_mb} MB)"
    
    return True, None


def validate_file_type(filename: str, allowed_types: Optional[List[str]] = None) -> Tuple[bool, Optional[str]]:
    """
    Validate file type.
    
    Args:
        filename: Filename to validate
        allowed_types: List of allowed file types (categories or extensions)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not filename:
        return False, "Dateiname ist erforderlich"
    
    # Extract file extension
    if '.' not in filename:
        return False, "Datei muss eine Erweiterung haben"
    
    extension = filename.rsplit('.', 1)[1].lower()
    
    # Use default allowed types if none specified
    if allowed_types is None:
        allowed_extensions = []
        for extensions in SUPPORTED_FILE_TYPES.values():
            allowed_extensions.extend([ext.lstrip('.') for ext in extensions])
    else:
        allowed_extensions = []
        for file_type in allowed_types:
            if file_type in SUPPORTED_FILE_TYPES:
                allowed_extensions.extend([ext.lstrip('.') for ext in SUPPORTED_FILE_TYPES[file_type]])
            else:
                # Assume it's a direct extension
                allowed_extensions.append(file_type.lstrip('.'))
    
    if extension not in allowed_extensions:
        return False, f"Dateityp .{extension} wird nicht unterstützt"
    
    return True, None


def validate_required_field(value: str, field_name: str) -> Tuple[bool, Optional[str]]:
    """
    Validate required field.
    
    Args:
        value: Field value
        field_name: Name of the field for error message
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not value or not value.strip():
        return False, f"{field_name} ist erforderlich"
    
    return True, None


def validate_text_length(text: str, min_length: int = 0, max_length: int = 1000, field_name: str = "Text") -> Tuple[bool, Optional[str]]:
    """
    Validate text length.
    
    Args:
        text: Text to validate
        min_length: Minimum length
        max_length: Maximum length
        field_name: Name of the field for error message
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not text:
        if min_length > 0:
            return False, f"{field_name} ist erforderlich"
        return True, None
    
    text_length = len(text.strip())
    
    if text_length < min_length:
        return False, f"{field_name} muss mindestens {min_length} Zeichen lang sein"
    
    if text_length > max_length:
        return False, f"{field_name} ist zu lang (maximal {max_length} Zeichen)"
    
    return True, None


def validate_numeric_range(value: int, min_value: int, max_value: int, field_name: str = "Wert") -> Tuple[bool, Optional[str]]:
    """
    Validate numeric value within range.
    
    Args:
        value: Numeric value
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        field_name: Name of the field for error message
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(value, (int, float)):
        return False, f"{field_name} muss eine Zahl sein"
    
    if value < min_value:
        return False, f"{field_name} muss mindestens {min_value} sein"
    
    if value > max_value:
        return False, f"{field_name} darf maximal {max_value} sein"
    
    return True, None


def validate_phone_number(phone: str) -> Tuple[bool, Optional[str]]:
    """
    Validate phone number format.
    
    Args:
        phone: Phone number to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not phone:
        return False, "Telefonnummer ist erforderlich"
    
    # Remove all non-digit characters for validation
    digits_only = re.sub(r'\D', '', phone)
    
    if len(digits_only) < 10:
        return False, "Telefonnummer ist zu kurz"
    
    if len(digits_only) > 15:
        return False, "Telefonnummer ist zu lang"
    
    return True, None


def validate_date_format(date_string: str, format_str: str = "%Y-%m-%d") -> Tuple[bool, Optional[str]]:
    """
    Validate date format.
    
    Args:
        date_string: Date string to validate
        format_str: Expected date format
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not date_string:
        return False, "Datum ist erforderlich"
    
    try:
        datetime.strptime(date_string, format_str)
        return True, None
    except ValueError:
        return False, f"Datum muss im Format {format_str} sein"


def validate_json_string(json_string: str) -> Tuple[bool, Optional[str]]:
    """
    Validate JSON string format.
    
    Args:
        json_string: JSON string to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not json_string:
        return False, "JSON-String ist erforderlich"
    
    try:
        import json
        json.loads(json_string)
        return True, None
    except json.JSONDecodeError as e:
        return False, f"Ungültiges JSON-Format: {str(e)}"


def validate_hex_color(color: str) -> Tuple[bool, Optional[str]]:
    """
    Validate hex color format.
    
    Args:
        color: Hex color to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not color:
        return False, "Farbe ist erforderlich"
    
    # Check for #RRGGBB or #RRGGBBAA format
    hex_pattern = r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{8})$'
    
    if not re.match(hex_pattern, color):
        return False, "Farbe muss im Hex-Format sein (#RRGGBB oder #RRGGBBAA)"
    
    return True, None


def validate_assistant_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate assistant creation/update data.
    
    Args:
        data: Assistant data to validate
        
    Returns:
        Dictionary with validation result
    """
    errors = []
    
    # Validate name
    if not data.get("name"):
        errors.append("Assistenten-Name ist erforderlich")
    elif len(data["name"]) < 2:
        errors.append("Assistenten-Name muss mindestens 2 Zeichen lang sein")
    elif len(data["name"]) > 100:
        errors.append("Assistenten-Name darf maximal 100 Zeichen lang sein")
    
    # Validate description
    if not data.get("description"):
        errors.append("Beschreibung ist erforderlich")
    elif len(data["description"]) < 10:
        errors.append("Beschreibung muss mindestens 10 Zeichen lang sein")
    elif len(data["description"]) > 500:
        errors.append("Beschreibung darf maximal 500 Zeichen lang sein")
    
    # Validate model
    valid_models = ["gpt-4", "gpt-3.5-turbo", "claude-3", "gemini-pro"]
    if data.get("model") not in valid_models:
        errors.append(f"Ungültiges Modell. Gültige Modelle: {', '.join(valid_models)}")
    
    # Validate temperature
    temperature = data.get("temperature", 0.7)
    if not isinstance(temperature, (int, float)) or temperature < 0 or temperature > 2:
        errors.append("Temperature muss zwischen 0 und 2 liegen")
    
    # Validate max_tokens
    max_tokens = data.get("max_tokens", 4096)
    if not isinstance(max_tokens, int) or max_tokens < 100 or max_tokens > 8000:
        errors.append("Max Tokens muss zwischen 100 und 8000 liegen")
    
    # Validate tools (if provided)
    if "tools" in data and not isinstance(data["tools"], list):
        errors.append("Tools muss eine Liste sein")
    
    # Validate status (if provided)
    if "status" in data and data["status"] not in ["active", "inactive"]:
        errors.append("Status muss 'active' oder 'inactive' sein")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def validate_conversation_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate conversation creation/update data.
    
    Args:
        data: Conversation data to validate
        
    Returns:
        Dictionary with validation result
    """
    errors = []
    
    # Validate assistant_id
    if not data.get("assistant_id"):
        errors.append("Assistant ID ist erforderlich")
    
    # Validate title (if provided)
    if "title" in data and data["title"]:
        if len(data["title"]) > 200:
            errors.append("Titel darf maximal 200 Zeichen lang sein")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def validate_message_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate message data.
    
    Args:
        data: Message data to validate
        
    Returns:
        Dictionary with validation result
    """
    errors = []
    
    # Validate content
    if not data.get("content"):
        errors.append("Nachrichteninhalt ist erforderlich")
    elif len(data["content"]) > 10000:
        errors.append("Nachrichteninhalt darf maximal 10000 Zeichen lang sein")
    
    # Validate conversation_id
    if not data.get("conversation_id"):
        errors.append("Konversations-ID ist erforderlich")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def validate_tool_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate tool data.
    
    Args:
        data: Tool data to validate
        
    Returns:
        Dictionary with validation result
    """
    errors = []
    
    # Validate name
    if not data.get("name"):
        errors.append("Tool-Name ist erforderlich")
    elif len(data["name"]) < 2:
        errors.append("Tool-Name muss mindestens 2 Zeichen lang sein")
    elif len(data["name"]) > 100:
        errors.append("Tool-Name darf maximal 100 Zeichen lang sein")
    
    # Validate description
    if not data.get("description"):
        errors.append("Tool-Beschreibung ist erforderlich")
    elif len(data["description"]) < 10:
        errors.append("Tool-Beschreibung muss mindestens 10 Zeichen lang sein")
    elif len(data["description"]) > 500:
        errors.append("Tool-Beschreibung darf maximal 500 Zeichen lang sein")
    
    # Validate category
    if "category" in data and data["category"]:
        if len(data["category"]) > 50:
            errors.append("Kategorie darf maximal 50 Zeichen lang sein")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def validate_knowledge_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate knowledge base data.
    
    Args:
        data: Knowledge data to validate
        
    Returns:
        Dictionary with validation result
    """
    errors = []
    
    # Validate title
    if not data.get("title"):
        errors.append("Titel ist erforderlich")
    elif len(data["title"]) < 2:
        errors.append("Titel muss mindestens 2 Zeichen lang sein")
    elif len(data["title"]) > 200:
        errors.append("Titel darf maximal 200 Zeichen lang sein")
    
    # Validate content
    if not data.get("content"):
        errors.append("Inhalt ist erforderlich")
    elif len(data["content"]) < 10:
        errors.append("Inhalt muss mindestens 10 Zeichen lang sein")
    
    # Validate category (if provided)
    if "category" in data and data["category"]:
        if len(data["category"]) > 50:
            errors.append("Kategorie darf maximal 50 Zeichen lang sein")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitize user input text.
    
    Args:
        text: Text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove null bytes and control characters
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    # Trim whitespace
    text = text.strip()
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length]
    
    return text


def validate_file_upload(filename: str, file_size: int, allowed_extensions: List[str] = None, max_size_mb: int = 10) -> Tuple[bool, str]:
    """
    Validate file upload.
    
    Args:
        filename: Name of the uploaded file
        file_size: Size of the file in bytes
        allowed_extensions: List of allowed file extensions
        max_size_mb: Maximum file size in MB
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not filename:
        return False, "Dateiname ist erforderlich"
    
    # Check file extension
    if allowed_extensions:
        file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
        if file_ext not in allowed_extensions:
            return False, f"Ungültiger Dateityp. Erlaubte Typen: {', '.join(allowed_extensions)}"
    
    # Check file size
    max_size_bytes = max_size_mb * 1024 * 1024
    if file_size > max_size_bytes:
        return False, f"Datei zu groß. Maximale Größe: {max_size_mb}MB"
    
    return True, ""


def validate_user_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate user profile data.
    
    Args:
        data: User data dictionary
        
    Returns:
        Validation result with valid flag and errors list
    """
    errors = []
    
    # Required fields
    required_fields = ["first_name", "last_name", "username", "email"]
    for field in required_fields:
        if not data.get(field):
            errors.append(f"{field} ist erforderlich")
    
    # Username validation
    if data.get("username"):
        username = data["username"]
        if len(username) < 3:
            errors.append("Benutzername muss mindestens 3 Zeichen lang sein")
        if len(username) > 30:
            errors.append("Benutzername darf maximal 30 Zeichen lang sein")
        if not re.match(r"^[a-zA-Z0-9_-]+$", username):
            errors.append("Benutzername darf nur Buchstaben, Zahlen, Unterstriche und Bindestriche enthalten")
    
    # Email validation
    if data.get("email"):
        email = data["email"]
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            errors.append("Ungültige E-Mail-Adresse")
    
    # Name validation
    if data.get("first_name"):
        first_name = data["first_name"]
        if len(first_name) < 2:
            errors.append("Vorname muss mindestens 2 Zeichen lang sein")
        if len(first_name) > 50:
            errors.append("Vorname darf maximal 50 Zeichen lang sein")
    
    if data.get("last_name"):
        last_name = data["last_name"]
        if len(last_name) < 2:
            errors.append("Nachname muss mindestens 2 Zeichen lang sein")
        if len(last_name) > 50:
            errors.append("Nachname darf maximal 50 Zeichen lang sein")
    
    # Bio validation
    if data.get("bio"):
        bio = data["bio"]
        if len(bio) > 500:
            errors.append("Bio darf maximal 500 Zeichen lang sein")
    
    # Website validation
    if data.get("website"):
        website = data["website"]
        if not re.match(r"^https?://.+", website):
            errors.append("Website muss mit http:// oder https:// beginnen")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def validate_password(password: str) -> Dict[str, Any]:
    """
    Validate password strength.
    
    Args:
        password: Password to validate
        
    Returns:
        Validation result with valid flag and errors list
    """
    errors = []
    
    if len(password) < 8:
        errors.append("Passwort muss mindestens 8 Zeichen lang sein")
    
    if len(password) > 128:
        errors.append("Passwort darf maximal 128 Zeichen lang sein")
    
    if not re.search(r"[a-z]", password):
        errors.append("Passwort muss mindestens einen Kleinbuchstaben enthalten")
    
    if not re.search(r"[A-Z]", password):
        errors.append("Passwort muss mindestens einen Großbuchstaben enthalten")
    
    if not re.search(r"\d", password):
        errors.append("Passwort muss mindestens eine Zahl enthalten")
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        errors.append("Passwort muss mindestens ein Sonderzeichen enthalten")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "strength": calculate_password_strength(password)
    }


def calculate_password_strength(password: str) -> str:
    """
    Calculate password strength.
    
    Args:
        password: Password to evaluate
        
    Returns:
        Password strength level
    """
    score = 0
    
    # Length
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if len(password) >= 16:
        score += 1
    
    # Character types
    if re.search(r"[a-z]", password):
        score += 1
    if re.search(r"[A-Z]", password):
        score += 1
    if re.search(r"\d", password):
        score += 1
    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        score += 1
    
    # Complexity
    if len(set(password)) >= len(password) * 0.8:
        score += 1
    
    if score <= 3:
        return "schwach"
    elif score <= 5:
        return "mittel"
    elif score <= 7:
        return "stark"
    else:
        return "sehr stark"


def validate_email(email: str) -> Dict[str, Any]:
    """
    Validate email address.
    
    Args:
        email: Email address to validate
        
    Returns:
        Validation result with valid flag and errors list
    """
    errors = []
    
    if not email:
        errors.append("E-Mail-Adresse ist erforderlich")
        return {"valid": False, "errors": errors}
    
    # Basic format check
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
        errors.append("Ungültige E-Mail-Adresse")
    
    # Length check
    if len(email) > 254:
        errors.append("E-Mail-Adresse ist zu lang")
    
    # Domain check
    if "@" in email:
        domain = email.split("@")[1]
        if len(domain) > 253:
            errors.append("Domain ist zu lang")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def validate_username(username: str) -> Dict[str, Any]:
    """
    Validate username.
    
    Args:
        username: Username to validate
        
    Returns:
        Validation result with valid flag and errors list
    """
    errors = []
    
    if not username:
        errors.append("Benutzername ist erforderlich")
        return {"valid": False, "errors": errors}
    
    if len(username) < 3:
        errors.append("Benutzername muss mindestens 3 Zeichen lang sein")
    
    if len(username) > 30:
        errors.append("Benutzername darf maximal 30 Zeichen lang sein")
    
    if not re.match(r"^[a-zA-Z0-9_-]+$", username):
        errors.append("Benutzername darf nur Buchstaben, Zahlen, Unterstriche und Bindestriche enthalten")
    
    # Check for reserved usernames
    reserved_usernames = [
        "admin", "administrator", "root", "system", "user", "guest",
        "test", "demo", "example", "support", "help", "info"
    ]
    if username.lower() in reserved_usernames:
        errors.append("Dieser Benutzername ist reserviert")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def validate_file_upload(filename: str, file_size: int, allowed_types: List[str], max_size: int) -> Dict[str, Any]:
    """
    Validate file upload.
    
    Args:
        filename: Name of the file
        file_size: Size of the file in bytes
        allowed_types: List of allowed file extensions
        max_size: Maximum file size in bytes
        
    Returns:
        Validation result with valid flag and errors list
    """
    errors = []
    
    # Check file size
    if file_size > max_size:
        max_size_mb = max_size / (1024 * 1024)
        errors.append(f"Datei ist zu groß. Maximale Größe: {max_size_mb:.1f} MB")
    
    # Check file extension
    if "." in filename:
        extension = filename.split(".")[-1].lower()
        if extension not in [ext.lower() for ext in allowed_types]:
            errors.append(f"Dateityp nicht erlaubt. Erlaubte Typen: {', '.join(allowed_types)}")
    else:
        errors.append("Datei hat keine Erweiterung")
    
    # Check filename
    if len(filename) > 255:
        errors.append("Dateiname ist zu lang")
    
    if not re.match(r"^[a-zA-Z0-9._-]+$", filename):
        errors.append("Dateiname enthält ungültige Zeichen")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def validate_url(url: str) -> Dict[str, Any]:
    """
    Validate URL.
    
    Args:
        url: URL to validate
        
    Returns:
        Validation result with valid flag and errors list
    """
    errors = []
    
    if not url:
        errors.append("URL ist erforderlich")
        return {"valid": False, "errors": errors}
    
    # Basic URL format check
    url_pattern = r"^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$"
    if not re.match(url_pattern, url):
        errors.append("Ungültige URL")
    
    # Length check
    if len(url) > 2048:
        errors.append("URL ist zu lang")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def validate_phone_number(phone: str) -> Dict[str, Any]:
    """
    Validate phone number.
    
    Args:
        phone: Phone number to validate
        
    Returns:
        Validation result with valid flag and errors list
    """
    errors = []
    
    if not phone:
        errors.append("Telefonnummer ist erforderlich")
        return {"valid": False, "errors": errors}
    
    # Remove common separators
    clean_phone = re.sub(r"[\s\-\(\)\+]", "", phone)
    
    # Check if it's all digits
    if not clean_phone.isdigit():
        errors.append("Telefonnummer darf nur Zahlen enthalten")
    
    # Check length (international format)
    if len(clean_phone) < 10 or len(clean_phone) > 15:
        errors.append("Telefonnummer muss zwischen 10 und 15 Ziffern haben")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def validate_date(date_str: str, format_str: str = "%Y-%m-%d") -> Dict[str, Any]:
    """
    Validate date string.
    
    Args:
        date_str: Date string to validate
        format_str: Expected date format
        
    Returns:
        Validation result with valid flag and errors list
    """
    errors = []
    
    if not date_str:
        errors.append("Datum ist erforderlich")
        return {"valid": False, "errors": errors}
    
    try:
        datetime.strptime(date_str, format_str)
    except ValueError:
        errors.append(f"Datum muss im Format {format_str} sein")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def validate_number(value: str, min_val: float = None, max_val: float = None) -> Dict[str, Any]:
    """
    Validate number input.
    
    Args:
        value: Number string to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        Validation result with valid flag and errors list
    """
    errors = []
    
    if not value:
        errors.append("Wert ist erforderlich")
        return {"valid": False, "errors": errors}
    
    try:
        num_value = float(value)
    except ValueError:
        errors.append("Wert muss eine Zahl sein")
        return {"valid": False, "errors": errors}
    
    if min_val is not None and num_value < min_val:
        errors.append(f"Wert muss mindestens {min_val} sein")
    
    if max_val is not None and num_value > max_val:
        errors.append(f"Wert darf maximal {max_val} sein")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "value": num_value
    }


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> Dict[str, Any]:
    """
    Validate required fields in a data dictionary.
    
    Args:
        data: Data dictionary to validate
        required_fields: List of required field names
        
    Returns:
        Validation result with valid flag and errors list
    """
    errors = []
    
    for field in required_fields:
        if not data.get(field):
            errors.append(f"{field} ist erforderlich")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def sanitize_input(input_str: str, max_length: int = 1000) -> str:
    """
    Sanitize user input.
    
    Args:
        input_str: Input string to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not input_str:
        return ""
    
    # Remove null bytes
    sanitized = input_str.replace("\x00", "")
    
    # Trim whitespace
    sanitized = sanitized.strip()
    
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


def validate_json_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate data against a JSON schema.
    
    Args:
        data: Data to validate
        schema: JSON schema definition
        
    Returns:
        Validation result with valid flag and errors list
    """
    errors = []
    
    # This is a simplified schema validation
    # In a real implementation, you might want to use a proper JSON schema library
    
    if "required" in schema:
        for field in schema["required"]:
            if field not in data or data[field] is None:
                errors.append(f"{field} ist erforderlich")
    
    if "properties" in schema:
        for field, field_schema in schema["properties"].items():
            if field in data:
                value = data[field]
                
                # Type validation
                if "type" in field_schema:
                    expected_type = field_schema["type"]
                    if expected_type == "string" and not isinstance(value, str):
                        errors.append(f"{field} muss ein String sein")
                    elif expected_type == "number" and not isinstance(value, (int, float)):
                        errors.append(f"{field} muss eine Zahl sein")
                    elif expected_type == "boolean" and not isinstance(value, bool):
                        errors.append(f"{field} muss ein Boolean sein")
                
                # Length validation for strings
                if isinstance(value, str) and "maxLength" in field_schema:
                    if len(value) > field_schema["maxLength"]:
                        errors.append(f"{field} ist zu lang")
                
                # Min/Max validation for numbers
                if isinstance(value, (int, float)):
                    if "minimum" in field_schema and value < field_schema["minimum"]:
                        errors.append(f"{field} ist zu klein")
                    if "maximum" in field_schema and value > field_schema["maximum"]:
                        errors.append(f"{field} ist zu groß")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def validate_document_data(data: dict) -> dict:
    """
    Validate document data for upload or update.
    Args:
        data: dict with document fields (filename, file_type, file_size, ...)
    Returns:
        dict: {"valid": bool, "errors": list[str]}
    """
    errors = []
    if not data.get("filename"):
        errors.append("Dateiname ist erforderlich.")
    if not data.get("file_type"):
        errors.append("Dateityp ist erforderlich.")
    if not isinstance(data.get("file_size"), int) or data.get("file_size", 0) <= 0:
        errors.append("Dateigröße muss größer als 0 sein.")
    if "description" in data and data["description"] and len(data["description"]) > 500:
        errors.append("Beschreibung darf maximal 500 Zeichen lang sein.")
    if "tags" in data and data["tags"] is not None and not isinstance(data["tags"], list):
        errors.append("Tags müssen eine Liste sein.")
    return {"valid": not errors, "errors": errors} 