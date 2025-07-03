"""
Validation functions for the AI Assistant Platform frontend.

This module provides input validation functions used throughout
the frontend application.
"""

import re
from typing import Optional, Tuple, List
from .constants import MAX_FILE_SIZE, SUPPORTED_FILE_TYPES


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
        from datetime import datetime
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