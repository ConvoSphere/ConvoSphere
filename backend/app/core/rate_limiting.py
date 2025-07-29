"""
Rate limiting utilities for API endpoints.

This module provides rate limiting functionality using Redis
to prevent abuse and ensure fair usage of the API.
"""

import time
from typing import Optional, Callable
from functools import wraps
from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse
import redis.asyncio as redis
from backend.app.core.config import get_settings
from backend.app.core.redis_client import get_redis
from loguru import logger



class RateLimiter:
    """Rate limiter using Redis for distributed rate limiting."""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.settings = get_settings()
    
    async def is_rate_limited(
        self,
        key: str,
        max_requests: int,
        window_seconds: int,
        identifier: Optional[str] = None
    ) -> tuple[bool, dict]:
        """
        Check if request is rate limited.
        
        Args:
            key: Rate limit key (e.g., 'upload', 'search')
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
            identifier: Optional identifier (e.g., user_id, ip)
            
        Returns:
            Tuple of (is_limited, rate_limit_info)
        """
        try:
            # Create rate limit key
            rate_key = f"rate_limit:{key}:{identifier}" if identifier else f"rate_limit:{key}"
            
            # Get current timestamp
            current_time = int(time.time())
            window_start = current_time - window_seconds
            
            # Use Redis pipeline for atomic operations
            pipe = self.redis.pipeline()
            
            # Remove old entries outside the window
            pipe.zremrangebyscore(rate_key, 0, window_start)
            
            # Count current requests in window
            pipe.zcard(rate_key)
            
            # Add current request
            pipe.zadd(rate_key, {str(current_time): current_time})
            
            # Set expiry on the key
            pipe.expire(rate_key, window_seconds)
            
            # Execute pipeline
            results = await pipe.execute()
            
            current_requests = results[1]  # zcard result
            
            # Check if rate limited
            is_limited = current_requests >= max_requests
            
            # Calculate remaining requests and reset time
            remaining_requests = max(0, max_requests - current_requests)
            reset_time = current_time + window_seconds
            
            rate_limit_info = {
                "limited": is_limited,
                "current_requests": current_requests,
                "max_requests": max_requests,
                "remaining_requests": remaining_requests,
                "reset_time": reset_time,
                "window_seconds": window_seconds
            }
            
            return is_limited, rate_limit_info
            
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # On error, allow the request but log it
            return False, {
                "limited": False,
                "error": "Rate limiting temporarily unavailable"
            }
    
    async def get_rate_limit_info(
        self,
        key: str,
        identifier: Optional[str] = None
    ) -> dict:
        """Get current rate limit information."""
        try:
            rate_key = f"rate_limit:{key}:{identifier}" if identifier else f"rate_limit:{key}"
            current_time = int(time.time())
            
            # Get all requests in current window
            requests = await self.redis.zrangebyscore(
                rate_key, 
                current_time - 3600,  # Last hour
                current_time
            )
            
            return {
                "current_requests": len(requests),
                "window_seconds": 3600,
                "reset_time": current_time + 3600
            }
            
        except Exception as e:
            logger.error(f"Error getting rate limit info: {e}")
            return {"error": "Unable to get rate limit info"}


# Global rate limiter instance
_rate_limiter: Optional[RateLimiter] = None

async def get_rate_limiter() -> RateLimiter:
    """Get or create rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        redis_client = await get_redis()
        _rate_limiter = RateLimiter(redis_client)
    return _rate_limiter


def rate_limit(
    max_requests: int = 100,
    window_seconds: int = 60,
    key_prefix: str = "default",
    identifier_func: Optional[Callable[[Request], str]] = None
):
    """
    Rate limiting decorator for FastAPI endpoints.
    
    Args:
        max_requests: Maximum requests allowed in window
        window_seconds: Time window in seconds
        key_prefix: Prefix for rate limit key
        identifier_func: Function to extract identifier from request
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, request: Request, **kwargs):
            try:
                # Get rate limiter
                limiter = await get_rate_limiter()
                
                # Determine identifier (user_id, ip, etc.)
                identifier = None
                if identifier_func:
                    identifier = identifier_func(request)
                else:
                    # Default to IP address
                    identifier = request.client.host
                
                # Check rate limit
                is_limited, rate_info = await limiter.is_rate_limited(
                    key_prefix,
                    max_requests,
                    window_seconds,
                    identifier
                )
                
                if is_limited:
                    # Return rate limit error
                    return JSONResponse(
                        status_code=429,
                        content={
                            "error": "Rate limit exceeded",
                            "message": f"Too many requests. Try again in {rate_info['window_seconds']} seconds.",
                            "rate_limit_info": rate_info
                        },
                        headers={
                            "X-RateLimit-Limit": str(max_requests),
                            "X-RateLimit-Remaining": str(rate_info["remaining_requests"]),
                            "X-RateLimit-Reset": str(rate_info["reset_time"]),
                            "Retry-After": str(rate_info["window_seconds"])
                        }
                    )
                
                # Add rate limit headers to response
                response = await func(*args, request=request, **kwargs)
                
                if hasattr(response, 'headers'):
                    response.headers["X-RateLimit-Limit"] = str(max_requests)
                    response.headers["X-RateLimit-Remaining"] = str(rate_info["remaining_requests"])
                    response.headers["X-RateLimit-Reset"] = str(rate_info["reset_time"])
                
                return response
                
            except Exception as e:
                logger.error(f"Rate limiting error in {func.__name__}: {e}")
                # On error, allow the request
                return await func(*args, request=request, **kwargs)
        
        return wrapper
    return decorator


# Predefined rate limit configurations
RATE_LIMITS = {
    "upload": {
        "max_requests": 10,
        "window_seconds": 60,
        "key_prefix": "upload"
    },
    "search": {
        "max_requests": 100,
        "window_seconds": 60,
        "key_prefix": "search"
    },
    "chat": {
        "max_requests": 50,
        "window_seconds": 60,
        "key_prefix": "chat"
    },
    "api": {
        "max_requests": 1000,
        "window_seconds": 60,
        "key_prefix": "api"
    },
    "auth": {
        "max_requests": 5,
        "window_seconds": 300,  # 5 minutes
        "key_prefix": "auth"
    }
}


def get_user_identifier(request: Request) -> str:
    """Extract user identifier from request."""
    # Try to get user_id from request state or headers
    user_id = getattr(request.state, 'user_id', None)
    if user_id:
        return f"user:{user_id}"
    
    # Fallback to IP address
    return request.client.host


def get_ip_identifier(request: Request) -> str:
    """Extract IP address from request."""
    return request.client.host


# Convenience decorators
def rate_limit_upload(func):
    """Rate limit for upload endpoints."""
    config = RATE_LIMITS["upload"]
    return rate_limit(
        max_requests=config["max_requests"],
        window_seconds=config["window_seconds"],
        key_prefix=config["key_prefix"],
        identifier_func=get_user_identifier
    )(func)


def rate_limit_search(func):
    """Rate limit for search endpoints."""
    config = RATE_LIMITS["search"]
    return rate_limit(
        max_requests=config["max_requests"],
        window_seconds=config["window_seconds"],
        key_prefix=config["key_prefix"],
        identifier_func=get_user_identifier
    )(func)


def rate_limit_chat(func):
    """Rate limit for chat endpoints."""
    config = RATE_LIMITS["chat"]
    return rate_limit(
        max_requests=config["max_requests"],
        window_seconds=config["window_seconds"],
        key_prefix=config["key_prefix"],
        identifier_func=get_user_identifier
    )(func)


def rate_limit_auth(func):
    """Rate limit for authentication endpoints."""
    config = RATE_LIMITS["auth"]
    return rate_limit(
        max_requests=config["max_requests"],
        window_seconds=config["window_seconds"],
        key_prefix=config["key_prefix"],
        identifier_func=get_ip_identifier
    )(func)