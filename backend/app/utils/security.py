"""Security utilities for the AI Assistant Platform."""

import re
import html
from typing import List, Optional


def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent XSS attacks.
    
    Args:
        text: Input text to sanitize
        
    Returns:
        str: Sanitized text
    """
    # HTML escape
    sanitized = html.escape(text)
    # Remove script tags
    sanitized = re.sub(r'<script.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
    # Remove other potentially dangerous tags
    sanitized = re.sub(r'<(iframe|object|embed|form|input|textarea|select|button).*?>', '', sanitized, flags=re.IGNORECASE)
    
    return sanitized


def validate_permissions(user_permissions: List[str], required_permissions: List[str]) -> bool:
    """
    Validate if user has required permissions.
    
    Args:
        user_permissions: User's permissions
        required_permissions: Required permissions
        
    Returns:
        bool: True if user has all required permissions
    """
    return all(perm in user_permissions for perm in required_permissions)


def check_rate_limit(user_id: str, action: str, limit: int, window: int) -> bool:
    """
    Check if user has exceeded rate limit for an action.
    
    Args:
        user_id: User ID
        action: Action being performed
        limit: Maximum allowed actions
        window: Time window in seconds
        
    Returns:
        bool: True if within rate limit, False otherwise
    """
    # TODO: Implement rate limiting with Redis
    return True


def validate_api_key(api_key: str) -> bool:
    """
    Validate API key format.
    
    Args:
        api_key: API key to validate
        
    Returns:
        bool: True if valid format, False otherwise
    """
    # Basic validation - should be alphanumeric and at least 32 characters
    return bool(re.match(r'^[a-zA-Z0-9]{32,}$', api_key))


def generate_secure_token(length: int = 32) -> str:
    """
    Generate a secure random token.
    
    Args:
        length: Token length
        
    Returns:
        str: Secure token
    """
    import secrets
    import string
    
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length)) 