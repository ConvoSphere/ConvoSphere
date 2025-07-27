"""
Enhanced security features for advanced RBAC.

This module provides advanced security features including session management,
rate limiting, IP whitelisting, and threat detection.
"""

import hashlib
import json
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from backend.app.core.redis_client import get_redis_client
from backend.app.models.user import User
from fastapi import HTTPException, Request, status
from loguru import logger


class SecurityEventType(str, Enum):
    """Security event types for threat detection."""

    SUSPICIOUS_LOGIN = "suspicious_login"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    IP_BLOCKED = "ip_blocked"
    ACCOUNT_LOCKED = "account_locked"
    PERMISSION_VIOLATION = "permission_violation"
    SESSION_HIJACKING = "session_hijacking"
    BRUTE_FORCE_ATTEMPT = "brute_force_attempt"
    ANOMALOUS_ACTIVITY = "anomalous_activity"


class ThreatLevel(str, Enum):
    """Threat levels for security events."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityEvent:
    """Security event data structure."""

    event_type: SecurityEventType
    user_id: str | None
    ip_address: str
    user_agent: str | None
    details: dict[str, Any]
    threat_level: ThreatLevel
    timestamp: datetime
    session_id: str | None = None


class SessionManager:
    """Advanced session management."""

    def __init__(self):
        self.redis = get_redis_client()
        self.session_prefix = "session:"
        self.session_timeout = 3600  # 1 hour

    def create_session(self, user_id: str, request: Request) -> str:
        """Create a new session."""
        session_id = self._generate_session_id(user_id, request)
        session_data = {
            "user_id": user_id,
            "ip_address": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent"),
            "created_at": datetime.now(UTC).isoformat(),
            "last_activity": datetime.now(UTC).isoformat(),
            "login_count": 1,
        }

        # Store session in Redis
        self.redis.setex(
            f"{self.session_prefix}{session_id}",
            self.session_timeout,
            json.dumps(session_data),
        )

        return session_id

    def validate_session(self, session_id: str, request: Request) -> bool:
        """Validate session and check for anomalies."""
        session_key = f"{self.session_prefix}{session_id}"
        session_data = self.redis.get(session_key)

        if not session_data:
            return False

        session = json.loads(session_data)
        current_ip = self._get_client_ip(request)
        current_user_agent = request.headers.get("user-agent")

        # Check for session hijacking
        if session["ip_address"] != current_ip:
            self._log_security_event(
                SecurityEvent(
                    event_type=SecurityEventType.SESSION_HIJACKING,
                    user_id=session["user_id"],
                    ip_address=current_ip,
                    user_agent=current_user_agent,
                    details={
                        "original_ip": session["ip_address"],
                        "new_ip": current_ip,
                        "session_id": session_id,
                    },
                    threat_level=ThreatLevel.HIGH,
                    timestamp=datetime.now(UTC),
                    session_id=session_id,
                ),
            )
            return False

        # Update last activity
        session["last_activity"] = datetime.now(UTC).isoformat()
        self.redis.setex(session_key, self.session_timeout, json.dumps(session))

        return True

    def _generate_session_id(self, user_id: str, request: Request) -> str:
        """Generate unique session ID."""
        data = f"{user_id}:{self._get_client_ip(request)}:{time.time()}"
        return hashlib.sha256(data.encode()).hexdigest()

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address."""
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"


class RateLimiter:
    """Advanced rate limiting with different strategies."""

    def __init__(self):
        self.redis = get_redis_client()
        self.rate_limit_prefix = "rate_limit:"

    def check_rate_limit(
        self,
        identifier: str,
        limit: int,
        window: int,
        request: Request,
    ) -> tuple[bool, dict[str, Any]]:
        """Check rate limit for given identifier."""
        key = f"{self.rate_limit_prefix}{identifier}"
        current_time = int(time.time())
        window_start = current_time - window

        # Get current requests in window
        requests = self.redis.zrangebyscore(key, window_start, current_time)

        if len(requests) >= limit:
            # Rate limit exceeded
            self._log_security_event(
                SecurityEvent(
                    event_type=SecurityEventType.RATE_LIMIT_EXCEEDED,
                    user_id=None,
                    ip_address=self._get_client_ip(request),
                    user_agent=request.headers.get("user-agent"),
                    details={
                        "identifier": identifier,
                        "limit": limit,
                        "window": window,
                        "current_requests": len(requests),
                    },
                    threat_level=ThreatLevel.MEDIUM,
                    timestamp=datetime.now(UTC),
                ),
            )

            return False, {
                "limit_exceeded": True,
                "limit": limit,
                "window": window,
                "retry_after": window,
            }

        # Add current request
        self.redis.zadd(key, {str(current_time): current_time})
        self.redis.expire(key, window)

        return True, {
            "limit_exceeded": False,
            "remaining": limit - len(requests) - 1,
            "reset_time": current_time + window,
        }

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address."""
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"


class IPWhitelistManager:
    """IP whitelist management."""

    def __init__(self):
        self.redis = get_redis_client()
        self.whitelist_prefix = "ip_whitelist:"
        self.blacklist_prefix = "ip_blacklist:"

    def is_ip_whitelisted(self, ip_address: str) -> bool:
        """Check if IP is whitelisted."""
        return self.redis.sismember(f"{self.whitelist_prefix}global", ip_address)

    def is_ip_blacklisted(self, ip_address: str) -> bool:
        """Check if IP is blacklisted."""
        return self.redis.sismember(f"{self.blacklist_prefix}global", ip_address)

    def add_to_whitelist(
        self,
        ip_address: str,
        organization_id: str | None = None,
    ) -> bool:
        """Add IP to whitelist."""
        key = f"{self.whitelist_prefix}{organization_id or 'global'}"
        return self.redis.sadd(key, ip_address) > 0

    def add_to_blacklist(
        self,
        ip_address: str,
        reason: str,
        duration: int = 3600,
    ) -> bool:
        """Add IP to blacklist with expiration."""
        key = f"{self.blacklist_prefix}global"
        self.redis.sadd(key, ip_address)

        # Set expiration for automatic removal
        self.redis.expire(key, duration)

        # Log the blacklist event
        self._log_security_event(
            SecurityEvent(
                event_type=SecurityEventType.IP_BLOCKED,
                user_id=None,
                ip_address=ip_address,
                user_agent=None,
                details={"reason": reason, "duration": duration},
                threat_level=ThreatLevel.HIGH,
                timestamp=datetime.now(UTC),
            ),
        )

        return True


class ThreatDetector:
    """Advanced threat detection system."""

    def __init__(self):
        self.redis = get_redis_client()
        self.threat_prefix = "threat:"
        self.anomaly_threshold = 5

    def detect_anomalies(
        self,
        user: User,
        request: Request,
        action: str,
    ) -> list[SecurityEvent]:
        """Detect security anomalies."""
        events = []

        # Check for unusual login patterns
        if action == "login":
            events.extend(self._detect_login_anomalies(user, request))

        # Check for permission violations
        events.extend(self._detect_permission_anomalies(user, request, action))

        # Check for behavioral anomalies
        events.extend(self._detect_behavioral_anomalies(user, request))

        return events

    def _detect_login_anomalies(
        self,
        user: User,
        request: Request,
    ) -> list[SecurityEvent]:
        """Detect unusual login patterns."""
        events = []
        ip_address = self._get_client_ip(request)

        # Check for login from new location
        user_login_history = self._get_user_login_history(user.id)
        if user_login_history and ip_address not in user_login_history.get("ips", []):
            events.append(
                SecurityEvent(
                    event_type=SecurityEventType.SUSPICIOUS_LOGIN,
                    user_id=str(user.id),
                    ip_address=ip_address,
                    user_agent=request.headers.get("user-agent"),
                    details={
                        "previous_ips": user_login_history.get("ips", []),
                        "new_ip": ip_address,
                    },
                    threat_level=ThreatLevel.MEDIUM,
                    timestamp=datetime.now(UTC),
                ),
            )

        # Check for rapid login attempts
        recent_logins = self._get_recent_logins(user.id)
        if len(recent_logins) > 3:  # More than 3 logins in short time
            events.append(
                SecurityEvent(
                    event_type=SecurityEventType.BRUTE_FORCE_ATTEMPT,
                    user_id=str(user.id),
                    ip_address=ip_address,
                    user_agent=request.headers.get("user-agent"),
                    details={"recent_logins": len(recent_logins)},
                    threat_level=ThreatLevel.HIGH,
                    timestamp=datetime.now(UTC),
                ),
            )

        return events

    def _detect_permission_anomalies(
        self,
        user: User,
        request: Request,
        action: str,
    ) -> list[SecurityEvent]:
        """Detect permission-related anomalies."""
        events = []

        # Check for privilege escalation attempts
        if action in ["role_update", "permission_grant"] and user.role not in [
            "admin",
            "super_admin",
        ]:
            events.append(
                SecurityEvent(
                    event_type=SecurityEventType.PERMISSION_VIOLATION,
                    user_id=str(user.id),
                    ip_address=self._get_client_ip(request),
                    user_agent=request.headers.get("user-agent"),
                    details={"action": action, "user_role": user.role},
                    threat_level=ThreatLevel.HIGH,
                    timestamp=datetime.now(UTC),
                ),
            )

        return events

    def _detect_behavioral_anomalies(
        self,
        user: User,
        request: Request,
    ) -> list[SecurityEvent]:
        """Detect behavioral anomalies."""
        events = []

        # Check for unusual activity patterns
        user_activity = self._get_user_activity_pattern(user.id)
        current_time = datetime.now(UTC)

        # Check for activity outside normal hours
        if user_activity and "normal_hours" in user_activity:
            hour = current_time.hour
            if hour < 6 or hour > 22:  # Outside 6 AM - 10 PM
                events.append(
                    SecurityEvent(
                        event_type=SecurityEventType.ANOMALOUS_ACTIVITY,
                        user_id=str(user.id),
                        ip_address=self._get_client_ip(request),
                        user_agent=request.headers.get("user-agent"),
                        details={
                            "hour": hour,
                            "normal_hours": user_activity["normal_hours"],
                        },
                        threat_level=ThreatLevel.LOW,
                        timestamp=current_time,
                    ),
                )

        return events

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address."""
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _get_user_login_history(self, user_id: str) -> dict[str, Any] | None:
        """Get user login history from cache."""
        data = self.redis.get(f"{self.threat_prefix}login_history:{user_id}")
        return json.loads(data) if data else None

    def _get_recent_logins(self, user_id: str) -> list[dict[str, Any]]:
        """Get recent login attempts."""
        data = self.redis.get(f"{self.threat_prefix}recent_logins:{user_id}")
        return json.loads(data) if data else []

    def _get_user_activity_pattern(self, user_id: str) -> dict[str, Any] | None:
        """Get user activity pattern."""
        data = self.redis.get(f"{self.threat_prefix}activity_pattern:{user_id}")
        return json.loads(data) if data else None


class SecurityManager:
    """Main security manager that coordinates all security features."""

    def __init__(self):
        self.session_manager = SessionManager()
        self.rate_limiter = RateLimiter()
        self.ip_manager = IPWhitelistManager()
        self.threat_detector = ThreatDetector()
        self.redis = get_redis_client()

    def authenticate_request(self, request: Request, user: User) -> bool:
        """Authenticate and validate request."""
        # Check IP whitelist/blacklist
        client_ip = self._get_client_ip(request)

        if self.ip_manager.is_ip_blacklisted(client_ip):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="IP address is blacklisted",
            )

        # Check rate limiting
        rate_limit_key = f"user:{user.id}:{request.url.path}"
        allowed, rate_info = self.rate_limiter.check_rate_limit(
            rate_limit_key,
            100,
            3600,
            request,  # 100 requests per hour
        )

        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Retry after {rate_info['retry_after']} seconds",
            )

        # Detect threats
        threats = self.threat_detector.detect_anomalies(user, request, "api_request")
        for threat in threats:
            self._log_security_event(threat)

            # Take action based on threat level
            if threat.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
                self._handle_high_threat(user, threat)

        return True

    def _handle_high_threat(self, user: User, threat: SecurityEvent):
        """Handle high-level threats."""
        if threat.event_type == SecurityEventType.BRUTE_FORCE_ATTEMPT:
            # Lock account temporarily
            self._lock_user_account(user.id, duration=1800)  # 30 minutes

        elif threat.event_type == SecurityEventType.SESSION_HIJACKING:
            # Invalidate all user sessions
            self._invalidate_user_sessions(user.id)

    def _lock_user_account(self, user_id: str, duration: int = 1800):
        """Lock user account temporarily."""
        lock_key = f"account_locked:{user_id}"
        self.redis.setex(lock_key, duration, "locked")

        self._log_security_event(
            SecurityEvent(
                event_type=SecurityEventType.ACCOUNT_LOCKED,
                user_id=user_id,
                ip_address="system",
                user_agent=None,
                details={"duration": duration, "reason": "security_threat"},
                threat_level=ThreatLevel.HIGH,
                timestamp=datetime.now(UTC),
            ),
        )

    def _invalidate_user_sessions(self, user_id: str):
        """Invalidate all user sessions."""
        session_pattern = "session:*"
        sessions = self.redis.keys(session_pattern)

        for session_key in sessions:
            session_data = self.redis.get(session_key)
            if session_data:
                session = json.loads(session_data)
                if session.get("user_id") == user_id:
                    self.redis.delete(session_key)

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address."""
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _log_security_event(self, event: SecurityEvent):
        """Log security event."""
        logger.warning(
            f"Security event: {event.event_type} - "
            f"User: {event.user_id}, IP: {event.ip_address}, "
            f"Threat Level: {event.threat_level}, Details: {event.details}",
        )

        # Store in Redis for analysis
        event_key = f"security_event:{event.user_id or 'anonymous'}:{int(time.time())}"
        self.redis.setex(event_key, 86400, json.dumps(event.__dict__))  # 24 hours
