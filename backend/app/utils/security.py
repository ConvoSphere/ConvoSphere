"""Security utilities for the AI Assistant Platform."""

import re
import asyncio
import html
from typing import List
from fastapi import Request, HTTPException, status
from app.core.redis_client import get_redis

RATE_LIMIT = 100  # requests
RATE_PERIOD = 60  # seconds

async def rate_limiter(request: Request):
    """
    Simple Redis-based rate limiter (100 req/min per IP).
    Raises HTTP 429 if limit exceeded.
    """
    client_ip = request.client.host
    key = f"rate_limit:{client_ip}"
    redis = await get_redis()
    current = await redis.get(key)
    if current is None:
        await redis.set(key, 1, ex=RATE_PERIOD)
    else:
        current = int(current)
        if current >= RATE_LIMIT:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Try again later."
            )
        await redis.incr(key)

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


async def check_rate_limit(user_id: str, action: str, limit: int, window: int) -> bool:
    """
    Check if user has exceeded rate limit for an action using Redis.
    
    Args:
        user_id: User ID
        action: Action being performed
        limit: Maximum allowed actions
        window: Time window in seconds
    Returns:
        bool: True if within rate limit, False otherwise
    """
    redis = await get_redis()
    key = f"rate_limit:{user_id}:{action}"
    current = await redis.get(key)
    if current is None:
        await redis.set(key, 1, ex=window)
        return True
    else:
        current = int(current)
        if current >= limit:
            return False
        await redis.incr(key)
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