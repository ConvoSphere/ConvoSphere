"""
Security middleware for FastAPI application.

This module provides comprehensive security headers and middleware
for protecting the ConvoSphere application.
"""

import time

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from backend.app.core.config import get_settings
from backend.app.core.security import verify_token


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers to all responses."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Add security headers to response."""
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate response time
        process_time = time.time() - start_time

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )
        response.headers["Content-Security-Policy"] = self._get_csp_header()
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=(), payment=(), usb=()"
        )
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
        response.headers["X-Download-Options"] = "noopen"
        response.headers["X-DNS-Prefetch-Control"] = "off"

        # Optional modern isolation headers (safe defaults)
        response.headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
        response.headers.setdefault("Cross-Origin-Embedder-Policy", "require-corp")

        # Add performance headers
        response.headers["X-Response-Time"] = f"{process_time:.4f}"

        # Log security events
        await self._log_security_event(request, response, process_time)

        return response

    def _get_csp_header(self) -> str:
        """Get Content Security Policy header (hardened, environment-aware)."""
        settings = get_settings()
        # Allow connections only to self and configured backend/ws endpoints
        backend_http = settings.backend_url
        backend_ws = settings.ws_url
        # Fonts and styles (Ant Design) may require inline styles; keep style 'unsafe-inline'
        return (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            f"connect-src 'self' {backend_http} {backend_ws}; "
            "worker-src 'self' blob:; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "upgrade-insecure-requests;"
        )

    async def _log_security_event(
        self, request: Request, response: Response, process_time: float
    ):
        """Log security-relevant events."""
        # Log suspicious requests
        if response.status_code >= 400:
            logger.warning(
                f"Security event: {request.method} {request.url.path} "
                f"returned {response.status_code} from {request.client.host}"
            )

        # Log slow requests
        if process_time > 5.0:
            logger.warning(
                f"Slow request: {request.method} {request.url.path} "
                f"took {process_time:.2f}s from {request.client.host}"
            )


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting requests with different limits per endpoint."""

    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts = {}

        # Different rate limits for different endpoints
        self.endpoint_limits = {
            "/api/v1/auth/login": 20,
            "/api/v1/auth/register": 10,
            "/api/v1/auth/refresh": 60,
            "/api/v1/auth/sso/providers": 200,
            "/api/v1/chat": 120,
            "/api/v1/knowledge": 80,
            "/api/v1/tools": 60,
            "/api/v1/assistants": 60,
        }

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Apply rate limiting to requests (deprecated in favor of Redis-based limiter)."""
        client_ip = self._get_client_ip(request)
        current_time = int(time.time() / 60)

        # Get user ID if authenticated
        user_id = await self._get_user_id(request)
        identifier = user_id if user_id else client_ip

        # Clean old entries
        self._cleanup_old_entries(current_time)

        # Get rate limit for this endpoint
        rate_limit = self._get_rate_limit_for_endpoint(request.url.path)

        # Check rate limit
        if not self._check_rate_limit(identifier, current_time, rate_limit):
            logger.warning(
                f"Rate limit exceeded for {identifier} on {request.url.path}"
            )
            return Response(
                content="Rate limit exceeded",
                status_code=429,
                headers={"Retry-After": "60"},
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(rate_limit)
        response.headers["X-RateLimit-Remaining"] = str(
            self._get_remaining_requests(identifier, current_time, rate_limit)
        )

        return response

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host

    async def _get_user_id(self, request: Request) -> str | None:
        """Get user ID from JWT token if authenticated using unified verifier."""
        try:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                subject = await verify_token(token)
                return subject
        except Exception:
            pass
        return None

    def _get_rate_limit_for_endpoint(self, path: str) -> int:
        """Get rate limit for specific endpoint."""
        for endpoint, limit in self.endpoint_limits.items():
            if path.startswith(endpoint):
                return limit
        return self.requests_per_minute

    def _check_rate_limit(
        self, identifier: str, current_time: int, rate_limit: int
    ) -> bool:
        """Check if request is within rate limit."""
        key = f"{identifier}:{current_time}"
        count = self.request_counts.get(key, 0)

        if count >= rate_limit:
            return False

        self.request_counts[key] = count + 1
        return True

    def _get_remaining_requests(
        self, identifier: str, current_time: int, rate_limit: int
    ) -> int:
        """Get remaining requests for client."""
        key = f"{identifier}:{current_time}"
        count = self.request_counts.get(key, 0)
        return max(0, rate_limit - count)

    def _cleanup_old_entries(self, current_time: int):
        """Clean up old rate limit entries."""
        keys_to_remove = [
            key
            for key in self.request_counts
            if int(key.split(":")[1]) < current_time - 1
        ]
        for key in keys_to_remove:
            del self.request_counts[key]


class SecurityValidationMiddleware(BaseHTTPMiddleware):
    """Middleware for security validation."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Validate request for security issues."""

        # Check for suspicious headers
        if self._has_suspicious_headers(request):
            logger.warning(f"Suspicious headers from {request.client.host}")
            return Response(content="Invalid request", status_code=400)

        # Check for suspicious user agents
        if self._has_suspicious_user_agent(request):
            logger.warning(f"Suspicious user agent from {request.client.host}")
            return Response(content="Invalid request", status_code=400)

        # Check for path traversal attempts
        if self._has_path_traversal(request):
            logger.warning(f"Path traversal attempt from {request.client.host}")
            return Response(content="Invalid request", status_code=400)

        # Process request
        return await call_next(request)

    def _has_suspicious_headers(self, request: Request) -> bool:
        """Check for suspicious headers."""
        suspicious_headers = ["X-Forwarded-Host", "X-Original-URL", "X-Rewrite-URL"]

        return any(header in request.headers for header in suspicious_headers)

    def _has_suspicious_user_agent(self, request: Request) -> bool:
        """Check for suspicious user agents."""
        user_agent = request.headers.get("user-agent", "").lower()

        suspicious_patterns = [
            "sqlmap",
            "nikto",
            "nmap",
            "scanner",
            "bot",
            "crawler",
            "spider",
        ]

        return any(pattern in user_agent for pattern in suspicious_patterns)

    def _has_path_traversal(self, request: Request) -> bool:
        """Check for path traversal attempts."""
        path = request.url.path.lower()

        suspicious_patterns = [
            "..",
            "~",
            "/etc/",
            "/proc/",
            "/sys/",
            "/dev/",
            "cmd",
            "exec",
            "system",
        ]

        return any(pattern in path for pattern in suspicious_patterns)


def setup_security_middleware(app):
    """Setup all security middleware for the application."""

    # Add security headers middleware
    app.add_middleware(SecurityHeadersMiddleware)

    # NOTE: The in-memory RateLimitMiddleware is intentionally not added here to
    # avoid inconsistent behavior in multi-instance deployments. Prefer the
    # Redis-backed limiter from backend.app.core.rate_limiting applied at the
    # endpoint level.

    # Add security validation middleware
    app.add_middleware(SecurityValidationMiddleware)

    logger.info("Security middleware configured successfully")
