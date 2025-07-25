"""
Security hardening for SSO integration.

This module provides additional security measures and validations
for the SSO authentication flows.
"""

import hashlib
import secrets
import time
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse

from fastapi import HTTPException, Request, status
from loguru import logger


class SSOSecurityValidator:
    """Security validator for SSO operations."""

    def __init__(self):
        self.allowed_domains = set()
        self.rate_limit_cache = {}
        self.suspicious_patterns = [
            "javascript:",
            "data:",
            "vbscript:",
            "onload=",
            "onerror=",
            "onclick=",
            "<script",
            "eval(",
            "document.cookie",
        ]

    def validate_redirect_url(self, url: str, allowed_domains: list = None) -> bool:
        """
        Validate redirect URL for security.

        Args:
            url: URL to validate
            allowed_domains: List of allowed domains

        Returns:
            bool: True if URL is safe
        """
        try:
            parsed = urlparse(url)
            
            # Check for dangerous protocols
            if parsed.scheme not in ['http', 'https']:
                logger.warning(f"Dangerous redirect URL scheme: {parsed.scheme}")
                return False
            
            # Check for suspicious patterns
            url_lower = url.lower()
            for pattern in self.suspicious_patterns:
                if pattern in url_lower:
                    logger.warning(f"Suspicious pattern in redirect URL: {pattern}")
                    return False
            
            # Check domain if provided
            if allowed_domains:
                domain = parsed.netloc.lower()
                if not any(allowed_domain in domain for allowed_domain in allowed_domains):
                    logger.warning(f"Unauthorized redirect domain: {domain}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating redirect URL: {e}")
            return False

    def validate_sso_state(self, state: str, stored_state: str) -> bool:
        """
        Validate SSO state parameter for CSRF protection.

        Args:
            state: State from request
            stored_state: State from session

        Returns:
            bool: True if state is valid
        """
        if not state or not stored_state:
            logger.warning("Missing SSO state parameter")
            return False
        
        if state != stored_state:
            logger.warning("SSO state mismatch - possible CSRF attack")
            return False
        
        return True

    def generate_secure_state(self) -> str:
        """
        Generate secure state parameter for CSRF protection.

        Returns:
            str: Secure state token
        """
        return secrets.token_urlsafe(32)

    def validate_saml_response(self, saml_response: str) -> bool:
        """
        Validate SAML response for security issues.

        Args:
            saml_response: Base64 encoded SAML response

        Returns:
            bool: True if response is safe
        """
        try:
            # Check for suspicious patterns in decoded response
            import base64
            decoded = base64.b64decode(saml_response).decode('utf-8', errors='ignore')
            
            decoded_lower = decoded.lower()
            for pattern in self.suspicious_patterns:
                if pattern in decoded_lower:
                    logger.warning(f"Suspicious pattern in SAML response: {pattern}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating SAML response: {e}")
            return False

    def rate_limit_check(self, identifier: str, max_requests: int = 10, window: int = 60) -> bool:
        """
        Check rate limiting for SSO operations.

        Args:
            identifier: Unique identifier (IP, user ID, etc.)
            max_requests: Maximum requests allowed
            window: Time window in seconds

        Returns:
            bool: True if request is allowed
        """
        current_time = time.time()
        
        if identifier not in self.rate_limit_cache:
            self.rate_limit_cache[identifier] = []
        
        # Clean old entries
        self.rate_limit_cache[identifier] = [
            timestamp for timestamp in self.rate_limit_cache[identifier]
            if current_time - timestamp < window
        ]
        
        # Check if limit exceeded
        if len(self.rate_limit_cache[identifier]) >= max_requests:
            logger.warning(f"Rate limit exceeded for {identifier}")
            return False
        
        # Add current request
        self.rate_limit_cache[identifier].append(current_time)
        return True

    def validate_user_attributes(self, user_attributes: Dict) -> Tuple[bool, str]:
        """
        Validate user attributes from SSO providers.

        Args:
            user_attributes: User attributes from SSO provider

        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        # Check for required fields
        required_fields = ['email', 'external_id']
        for field in required_fields:
            if not user_attributes.get(field):
                return False, f"Missing required field: {field}"
        
        # Validate email format
        email = user_attributes.get('email', '')
        if not self._is_valid_email(email):
            return False, f"Invalid email format: {email}"
        
        # Check for suspicious content
        for key, value in user_attributes.items():
            if isinstance(value, str):
                value_lower = value.lower()
                for pattern in self.suspicious_patterns:
                    if pattern in value_lower:
                        return False, f"Suspicious content in {key}: {pattern}"
        
        return True, ""

    def _is_valid_email(self, email: str) -> bool:
        """Check if email format is valid."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def sanitize_user_data(self, user_data: Dict) -> Dict:
        """
        Sanitize user data from SSO providers.

        Args:
            user_data: Raw user data

        Returns:
            Dict: Sanitized user data
        """
        sanitized = {}
        
        for key, value in user_data.items():
            if isinstance(value, str):
                # Remove potentially dangerous characters
                sanitized_value = value.replace('<', '&lt;').replace('>', '&gt;')
                sanitized_value = sanitized_value.replace('"', '&quot;').replace("'", '&#x27;')
                sanitized[key] = sanitized_value
            else:
                sanitized[key] = value
        
        return sanitized

    def validate_provider_config(self, provider: str, config: Dict) -> bool:
        """
        Validate SSO provider configuration.

        Args:
            provider: Provider name
            config: Provider configuration

        Returns:
            bool: True if configuration is valid
        """
        required_fields = {
            'google': ['client_id', 'client_secret', 'redirect_uri'],
            'microsoft': ['client_id', 'client_secret', 'tenant_id', 'redirect_uri'],
            'github': ['client_id', 'client_secret', 'redirect_uri'],
            'saml': ['metadata_url', 'entity_id', 'acs_url']
        }
        
        if provider not in required_fields:
            logger.warning(f"Unknown SSO provider: {provider}")
            return False
        
        for field in required_fields[provider]:
            if not config.get(field):
                logger.warning(f"Missing required field for {provider}: {field}")
                return False
        
        return True


class SSOAuditLogger:
    """Audit logger for SSO security events."""

    def __init__(self):
        self.security_events = []

    def log_sso_event(self, event_type: str, user_id: str = None, 
                     provider: str = None, details: Dict = None, 
                     severity: str = "info", ip_address: str = None):
        """
        Log SSO security event.

        Args:
            event_type: Type of event
            user_id: User ID if available
            provider: SSO provider
            details: Additional details
            severity: Event severity
            ip_address: IP address
        """
        event = {
            'timestamp': time.time(),
            'event_type': event_type,
            'user_id': user_id,
            'provider': provider,
            'details': details or {},
            'severity': severity,
            'ip_address': ip_address
        }
        
        self.security_events.append(event)
        
        # Log to logger
        log_message = f"SSO Security Event: {event_type}"
        if user_id:
            log_message += f" (User: {user_id})"
        if provider:
            log_message += f" (Provider: {provider})"
        if ip_address:
            log_message += f" (IP: {ip_address})"
        
        if severity == "warning":
            logger.warning(log_message)
        elif severity == "error":
            logger.error(log_message)
        else:
            logger.info(log_message)

    def get_security_events(self, hours: int = 24) -> list:
        """
        Get security events from the last N hours.

        Args:
            hours: Number of hours to look back

        Returns:
            list: Security events
        """
        cutoff_time = time.time() - (hours * 3600)
        return [event for event in self.security_events if event['timestamp'] > cutoff_time]

    def get_suspicious_events(self, hours: int = 24) -> list:
        """
        Get suspicious security events.

        Args:
            hours: Number of hours to look back

        Returns:
            list: Suspicious events
        """
        events = self.get_security_events(hours)
        suspicious_types = [
            'csrf_attempt',
            'rate_limit_exceeded',
            'invalid_redirect',
            'suspicious_pattern',
            'authentication_failure'
        ]
        
        return [event for event in events if event['event_type'] in suspicious_types]


# Global instances
sso_security_validator = SSOSecurityValidator()
sso_audit_logger = SSOAuditLogger()


def get_client_ip(request: Request) -> str:
    """Get client IP address from request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def validate_sso_request(request: Request, provider: str) -> bool:
    """
    Validate SSO request for security.

    Args:
        request: FastAPI request
        provider: SSO provider

    Returns:
        bool: True if request is valid
    """
    client_ip = get_client_ip(request)
    
    # Rate limiting check
    if not sso_security_validator.rate_limit_check(client_ip):
        sso_audit_logger.log_sso_event(
            event_type="rate_limit_exceeded",
            provider=provider,
            severity="warning",
            ip_address=client_ip
        )
        return False
    
    # Check for suspicious headers
    suspicious_headers = [
        'X-Forwarded-Host',
        'X-Original-URL',
        'X-Rewrite-URL'
    ]
    
    for header in suspicious_headers:
        if header in request.headers:
            sso_audit_logger.log_sso_event(
                event_type="suspicious_header",
                provider=provider,
                details={'header': header, 'value': request.headers[header]},
                severity="warning",
                ip_address=client_ip
            )
            return False
    
    return True