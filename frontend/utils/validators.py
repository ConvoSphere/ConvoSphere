"""
Validators for input validation and data sanitization.

This module provides comprehensive validation and sanitization
functions for user inputs and data processing.
"""

import html
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from .constants import MAX_FILE_SIZE, SUPPORTED_FILE_TYPES


class ValidationType(Enum):
    """Validation types."""

    REQUIRED = "required"
    EMAIL = "email"
    PASSWORD = "password"
    LENGTH = "length"
    PATTERN = "pattern"
    RANGE = "range"
    CUSTOM = "custom"


@dataclass
class ValidationRule:
    """Validation rule definition."""

    type: ValidationType
    message: str
    params: dict[str, Any] = None

    def __post_init__(self):
        if self.params is None:
            self.params = {}


@dataclass
class ValidationResult:
    """Validation result."""

    valid: bool
    errors: list[str] = None
    sanitized_value: Any = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class Validator:
    """Input validation and sanitization."""

    def __init__(self):
        """Initialize validator."""
        # Common patterns
        self.patterns = {
            "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            "password": r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$",
            "username": r"^[a-zA-Z0-9_-]{3,20}$",
            "phone": r"^\+?[\d\s\-\(\)]{10,}$",
            "url": r"^https?://[^\s/$.?#].[^\s]*$",
            "date": r"^\d{4}-\d{2}-\d{2}$",
            "time": r"^\d{2}:\d{2}(:\d{2})?$",
            "datetime": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})?$",
        }

        # Default validation rules
        self.default_rules = {
            "email": [
                ValidationRule(ValidationType.REQUIRED, "Email is required"),
                ValidationRule(ValidationType.EMAIL, "Invalid email format"),
            ],
            "password": [
                ValidationRule(ValidationType.REQUIRED, "Password is required"),
                ValidationRule(
                    ValidationType.PASSWORD,
                    "Password must be at least 8 characters with uppercase, lowercase, number, and special character",
                ),
            ],
            "username": [
                ValidationRule(ValidationType.REQUIRED, "Username is required"),
                ValidationRule(
                    ValidationType.PATTERN,
                    "Username must be 3-20 characters, letters, numbers, underscore, or dash",
                    {"pattern": "username"},
                ),
            ],
        }

    def validate(
        self,
        value: Any,
        rules: list[ValidationRule],
        field_name: str = "field",
    ) -> ValidationResult:
        """
        Validate a value against a list of rules.

        Args:
            value: Value to validate
            rules: List of validation rules
            field_name: Name of the field being validated

        Returns:
            ValidationResult with validation status and errors
        """
        result = ValidationResult(valid=True)
        sanitized_value = value

        for rule in rules:
            validation_result = self._apply_rule(value, rule, field_name)

            if not validation_result["valid"]:
                result.valid = False
                result.errors.append(validation_result["message"])

            if validation_result.get("sanitized_value") is not None:
                sanitized_value = validation_result["sanitized_value"]

        result.sanitized_value = sanitized_value
        return result

    def _apply_rule(
        self,
        value: Any,
        rule: ValidationRule,
        field_name: str,
    ) -> dict[str, Any]:
        """Apply a single validation rule."""
        if rule.type == ValidationType.REQUIRED:
            return self._validate_required(value, rule, field_name)
        if rule.type == ValidationType.EMAIL:
            return self._validate_email(value, rule, field_name)
        if rule.type == ValidationType.PASSWORD:
            return self._validate_password(value, rule, field_name)
        if rule.type == ValidationType.LENGTH:
            return self._validate_length(value, rule, field_name)
        if rule.type == ValidationType.PATTERN:
            return self._validate_pattern(value, rule, field_name)
        if rule.type == ValidationType.RANGE:
            return self._validate_range(value, rule, field_name)
        if rule.type == ValidationType.CUSTOM:
            return self._validate_custom(value, rule, field_name)
        return {"valid": True, "message": ""}

    def _validate_required(
        self, value: Any, rule: ValidationRule, field_name: str,
    ) -> dict[str, Any]:
        """Validate required field."""
        if value is None or (isinstance(value, str) and not value.strip()):
            return {
                "valid": False,
                "message": rule.message or f"{field_name} is required",
            }
        return {"valid": True}

    def _validate_email(
        self, value: Any, rule: ValidationRule, field_name: str,
    ) -> dict[str, Any]:
        """Validate email format."""
        if not value:
            return {"valid": True}

        if not re.match(self.patterns["email"], str(value)):
            return {
                "valid": False,
                "message": rule.message or f"Invalid email format for {field_name}",
            }

        return {
            "valid": True,
            "sanitized_value": str(value).lower().strip(),
        }

    def _validate_password(
        self, value: Any, rule: ValidationRule, field_name: str,
    ) -> dict[str, Any]:
        """Validate password strength."""
        if not value:
            return {"valid": True}

        password = str(value)

        # Check minimum length
        if len(password) < 8:
            return {
                "valid": False,
                "message": rule.message
                or f"{field_name} must be at least 8 characters long",
            }

        # Check for required character types
        if not re.search(r"[a-z]", password):
            return {
                "valid": False,
                "message": rule.message
                or f"{field_name} must contain at least one lowercase letter",
            }

        if not re.search(r"[A-Z]", password):
            return {
                "valid": False,
                "message": rule.message
                or f"{field_name} must contain at least one uppercase letter",
            }

        if not re.search(r"\d", password):
            return {
                "valid": False,
                "message": rule.message
                or f"{field_name} must contain at least one number",
            }

        if not re.search(r"[@$!%*?&]", password):
            return {
                "valid": False,
                "message": rule.message
                or f"{field_name} must contain at least one special character (@$!%*?&)",
            }

        return {"valid": True}

    def _validate_length(
        self, value: Any, rule: ValidationRule, field_name: str,
    ) -> dict[str, Any]:
        """Validate string length."""
        if not value:
            return {"valid": True}

        value_str = str(value)
        min_length = rule.params.get("min")
        max_length = rule.params.get("max")

        if min_length and len(value_str) < min_length:
            return {
                "valid": False,
                "message": rule.message
                or f"{field_name} must be at least {min_length} characters long",
            }

        if max_length and len(value_str) > max_length:
            return {
                "valid": False,
                "message": rule.message
                or f"{field_name} must be no more than {max_length} characters long",
            }

        return {"valid": True}

    def _validate_pattern(
        self, value: Any, rule: ValidationRule, field_name: str,
    ) -> dict[str, Any]:
        """Validate against regex pattern."""
        if not value:
            return {"valid": True}

        pattern_name = rule.params.get("pattern")
        custom_pattern = rule.params.get("custom_pattern")

        if pattern_name and pattern_name in self.patterns:
            pattern = self.patterns[pattern_name]
        elif custom_pattern:
            pattern = custom_pattern
        else:
            return {"valid": True}

        if not re.match(pattern, str(value)):
            return {
                "valid": False,
                "message": rule.message or f"Invalid format for {field_name}",
            }

        return {"valid": True}

    def _validate_range(
        self, value: Any, rule: ValidationRule, field_name: str,
    ) -> dict[str, Any]:
        """Validate numeric range."""
        if value is None:
            return {"valid": True}

        try:
            num_value = float(value)
        except (ValueError, TypeError):
            return {
                "valid": False,
                "message": rule.message or f"{field_name} must be a number",
            }

        min_val = rule.params.get("min")
        max_val = rule.params.get("max")

        if min_val is not None and num_value < min_val:
            return {
                "valid": False,
                "message": rule.message or f"{field_name} must be at least {min_val}",
            }

        if max_val is not None and num_value > max_val:
            return {
                "valid": False,
                "message": rule.message
                or f"{field_name} must be no more than {max_val}",
            }

        return {"valid": True}

    def _validate_custom(
        self, value: Any, rule: ValidationRule, field_name: str,
    ) -> dict[str, Any]:
        """Validate using custom function."""
        custom_func = rule.params.get("function")
        if not custom_func or not callable(custom_func):
            return {"valid": True}

        try:
            result = custom_func(value)
            if isinstance(result, bool):
                return {
                    "valid": result,
                    "message": rule.message or f"Invalid {field_name}",
                }
            if isinstance(result, dict):
                return result
            return {"valid": True}
        except Exception as e:
            return {
                "valid": False,
                "message": f"Validation error for {field_name}: {str(e)}",
            }

    # Convenience methods for common validations
    def validate_email(self, email: str) -> ValidationResult:
        """Validate email address."""
        return self.validate(email, self.default_rules["email"], "email")

    def validate_password(self, password: str) -> ValidationResult:
        """Validate password strength."""
        return self.validate(password, self.default_rules["password"], "password")

    def validate_username(self, username: str) -> ValidationResult:
        """Validate username."""
        return self.validate(username, self.default_rules["username"], "username")

    def validate_form_data(
        self, data: dict[str, Any], schema: dict[str, list[ValidationRule]],
    ) -> dict[str, ValidationResult]:
        """Validate form data against schema."""
        results = {}

        for field_name, rules in schema.items():
            value = data.get(field_name)
            results[field_name] = self.validate(value, rules, field_name)

        return results

    # Sanitization methods
    def sanitize_string(self, value: str, max_length: int | None = None) -> str:
        """Sanitize string input."""
        if not value:
            return ""

        # Convert to string and strip whitespace
        sanitized = str(value).strip()

        # HTML escape
        sanitized = html.escape(sanitized)

        # Limit length
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[:max_length]

        return sanitized

    def sanitize_email(self, email: str) -> str:
        """Sanitize email address."""
        if not email:
            return ""

        # Convert to lowercase and strip whitespace
        sanitized = str(email).lower().strip()

        # Basic email validation
        if re.match(self.patterns["email"], sanitized):
            return sanitized

        return ""

    def sanitize_html(
        self, html_content: str, allowed_tags: list[str] | None = None,
    ) -> str:
        """Sanitize HTML content."""
        if not html_content:
            return ""

        # For now, just escape all HTML
        # In a real implementation, you might use a library like bleach
        return html.escape(html_content)

    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename."""
        if not filename:
            return ""

        # Remove or replace dangerous characters
        sanitized = re.sub(r'[<>:"/\\|?*]', "_", str(filename))

        # Remove leading/trailing dots and spaces
        sanitized = sanitized.strip(". ")

        # Limit length
        if len(sanitized) > 255:
            name, ext = (
                sanitized.rsplit(".", 1) if "." in sanitized else (sanitized, "")
            )
            sanitized = name[: 255 - len(ext) - 1] + ("." + ext if ext else "")

        return sanitized


# Global validator instance
validator = Validator()


# Convenience functions
def validate_email(email: str) -> ValidationResult:
    """Validate email address."""
    return validator.validate_email(email)


def validate_password(password: str) -> ValidationResult:
    """Validate password strength."""
    return validator.validate_password(password)


def validate_username(username: str) -> ValidationResult:
    """Validate username."""
    return validator.validate_username(username)


def sanitize_string(value: str, max_length: int | None = None) -> str:
    """Sanitize string input."""
    return validator.sanitize_string(value, max_length)


def sanitize_email(email: str) -> str:
    """Sanitize email address."""
    return validator.sanitize_email(email)


def validate_file_size(file_size: int) -> tuple[bool, str | None]:
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


def validate_file_type(
    filename: str, allowed_types: list[str] | None = None,
) -> tuple[bool, str | None]:
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
    if "." not in filename:
        return False, "Datei muss eine Erweiterung haben"

    extension = filename.rsplit(".", 1)[1].lower()

    # Use default allowed types if none specified
    if allowed_types is None:
        allowed_extensions = []
        for extensions in SUPPORTED_FILE_TYPES.values():
            allowed_extensions.extend([ext.lstrip(".") for ext in extensions])
    else:
        allowed_extensions = []
        for file_type in allowed_types:
            if file_type in SUPPORTED_FILE_TYPES:
                allowed_extensions.extend(
                    [ext.lstrip(".") for ext in SUPPORTED_FILE_TYPES[file_type]],
                )
            else:
                # Assume it's a direct extension
                allowed_extensions.append(file_type.lstrip("."))

    if extension not in allowed_extensions:
        return False, f"Dateityp .{extension} wird nicht unterstützt"

    return True, None


def validate_required_field(value: str, field_name: str) -> tuple[bool, str | None]:
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


def validate_text_length(
    text: str, min_length: int = 0, max_length: int = 1000, field_name: str = "Text",
) -> tuple[bool, str | None]:
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


def validate_numeric_range(
    value: int, min_value: int, max_value: int, field_name: str = "Wert",
) -> tuple[bool, str | None]:
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


def validate_phone_number(phone: str) -> tuple[bool, str | None]:
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
    digits_only = re.sub(r"\D", "", phone)

    if len(digits_only) < 10:
        return False, "Telefonnummer ist zu kurz"

    if len(digits_only) > 15:
        return False, "Telefonnummer ist zu lang"

    return True, None


def validate_date_format(
    date_string: str, format_str: str = "%Y-%m-%d",
) -> tuple[bool, str | None]:
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


def validate_json_string(json_string: str) -> tuple[bool, str | None]:
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


def validate_hex_color(color: str) -> tuple[bool, str | None]:
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
    hex_pattern = r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{8})$"

    if not re.match(hex_pattern, color):
        return False, "Farbe muss im Hex-Format sein (#RRGGBB oder #RRGGBBAA)"

    return True, None


def validate_assistant_data(data: dict[str, Any]) -> dict[str, Any]:
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
        "errors": errors,
    }


def validate_conversation_data(data: dict[str, Any]) -> dict[str, Any]:
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
        "errors": errors,
    }


def validate_message_data(data: dict[str, Any]) -> dict[str, Any]:
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
        "errors": errors,
    }


def validate_tool_data(data: dict[str, Any]) -> dict[str, Any]:
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
        "errors": errors,
    }


def validate_knowledge_data(data: dict[str, Any]) -> dict[str, Any]:
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
        "errors": errors,
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
    text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)

    # Trim whitespace
    text = text.strip()

    # Limit length
    if len(text) > max_length:
        text = text[:max_length]

    return text


def validate_file_upload(
    filename: str,
    file_size: int,
    allowed_extensions: list[str] = None,
    max_size_mb: int = 10,
) -> tuple[bool, str]:
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
        file_ext = filename.lower().split(".")[-1] if "." in filename else ""
        if file_ext not in allowed_extensions:
            return (
                False,
                f"Ungültiger Dateityp. Erlaubte Typen: {', '.join(allowed_extensions)}",
            )

    # Check file size
    max_size_bytes = max_size_mb * 1024 * 1024
    if file_size > max_size_bytes:
        return False, f"Datei zu groß. Maximale Größe: {max_size_mb}MB"

    return True, ""


def validate_user_data(data: dict[str, Any]) -> dict[str, Any]:
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
            errors.append(
                "Benutzername darf nur Buchstaben, Zahlen, Unterstriche und Bindestriche enthalten",
            )

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
        "errors": errors,
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
    if score <= 5:
        return "mittel"
    if score <= 7:
        return "stark"
    return "sehr stark"


def validate_url(url: str) -> dict[str, Any]:
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
        "errors": errors,
    }


def validate_phone_number(phone: str) -> dict[str, Any]:
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
        "errors": errors,
    }


def validate_date(date_str: str, format_str: str = "%Y-%m-%d") -> dict[str, Any]:
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
        "errors": errors,
    }


def validate_number(
    value: str, min_val: float = None, max_val: float = None,
) -> dict[str, Any]:
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
        "value": num_value,
    }


def validate_required_fields(
    data: dict[str, Any], required_fields: list[str],
) -> dict[str, Any]:
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
        "errors": errors,
    }


def validate_json_schema(
    data: dict[str, Any], schema: dict[str, Any],
) -> dict[str, Any]:
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
                    elif expected_type == "number" and not isinstance(
                        value, (int, float),
                    ):
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
        "errors": errors,
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
    if (
        "tags" in data
        and data["tags"] is not None
        and not isinstance(data["tags"], list)
    ):
        errors.append("Tags müssen eine Liste sein.")
    return {"valid": not errors, "errors": errors}
