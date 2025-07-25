"""
Advanced session manager with Redis backend.

This module provides comprehensive session management including
session storage, validation, security features, and multi-device support.
"""

import json
import logging
import secrets
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set
from uuid import UUID, uuid4

import redis
from fastapi import Request
from sqlalchemy.orm import Session as DBSession

from app.core.config import settings
from app.models.user import User
from app.utils.exceptions import SessionError, AuthenticationError

logger = logging.getLogger(__name__)


class SessionData:
    """Session data structure."""
    
    def __init__(
        self,
        session_id: str,
        user_id: str,
        username: str,
        created_at: datetime,
        expires_at: datetime,
        device_info: Dict[str, Any],
        ip_address: str,
        user_agent: str,
        is_active: bool = True,
        last_activity: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.session_id = session_id
        self.user_id = user_id
        self.username = username
        self.created_at = created_at
        self.expires_at = expires_at
        self.device_info = device_info
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.is_active = is_active
        self.last_activity = last_activity or created_at
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session data to dictionary."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "username": self.username,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "device_info": self.device_info,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "is_active": self.is_active,
            "last_activity": self.last_activity.isoformat(),
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionData":
        """Create session data from dictionary."""
        return cls(
            session_id=data["session_id"],
            user_id=data["user_id"],
            username=data["username"],
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]),
            device_info=data["device_info"],
            ip_address=data["ip_address"],
            user_agent=data["user_agent"],
            is_active=data["is_active"],
            last_activity=datetime.fromisoformat(data["last_activity"]),
            metadata=data.get("metadata", {}),
        )
    
    @property
    def is_expired(self) -> bool:
        """Check if session is expired."""
        return datetime.now() > self.expires_at
    
    @property
    def is_inactive(self) -> bool:
        """Check if session is inactive (no recent activity)."""
        if not self.last_activity:
            return True
        
        inactivity_threshold = timedelta(hours=settings.SESSION_INACTIVITY_HOURS)
        return datetime.now() - self.last_activity > inactivity_threshold


class DeviceInfo:
    """Device information extractor."""
    
    @staticmethod
    def extract_from_request(request: Request) -> Dict[str, Any]:
        """Extract device information from request."""
        user_agent = request.headers.get("user-agent", "")
        
        # Basic device detection
        device_info = {
            "user_agent": user_agent,
            "ip_address": request.client.host if request.client else "unknown",
            "platform": "unknown",
            "browser": "unknown",
            "device_type": "unknown",
        }
        
        # Simple user agent parsing
        ua_lower = user_agent.lower()
        
        # Platform detection
        if "windows" in ua_lower:
            device_info["platform"] = "windows"
        elif "mac" in ua_lower:
            device_info["platform"] = "macos"
        elif "linux" in ua_lower:
            device_info["platform"] = "linux"
        elif "android" in ua_lower:
            device_info["platform"] = "android"
        elif "ios" in ua_lower:
            device_info["platform"] = "ios"
        
        # Browser detection
        if "chrome" in ua_lower:
            device_info["browser"] = "chrome"
        elif "firefox" in ua_lower:
            device_info["browser"] = "firefox"
        elif "safari" in ua_lower:
            device_info["browser"] = "safari"
        elif "edge" in ua_lower:
            device_info["browser"] = "edge"
        
        # Device type detection
        if any(mobile in ua_lower for mobile in ["mobile", "android", "iphone", "ipad"]):
            device_info["device_type"] = "mobile"
        elif "tablet" in ua_lower:
            device_info["device_type"] = "tablet"
        else:
            device_info["device_type"] = "desktop"
        
        return device_info


class SessionManager:
    """Advanced session manager with Redis backend."""
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_SESSION_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True,
        )
        self.session_prefix = "session:"
        self.user_sessions_prefix = "user_sessions:"
        self.session_timeout = settings.SESSION_TIMEOUT_HOURS * 3600  # Convert to seconds
        self.max_sessions_per_user = settings.MAX_SESSIONS_PER_USER
    
    def create_session(
        self,
        user: User,
        request: Request,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SessionData:
        """Create a new session for user."""
        try:
            # Generate session ID
            session_id = str(uuid4())
            
            # Extract device information
            device_info = DeviceInfo.extract_from_request(request)
            
            # Set session expiration
            created_at = datetime.now()
            expires_at = created_at + timedelta(hours=settings.SESSION_TIMEOUT_HOURS)
            
            # Create session data
            session_data = SessionData(
                session_id=session_id,
                user_id=str(user.id),
                username=user.username,
                created_at=created_at,
                expires_at=expires_at,
                device_info=device_info,
                ip_address=device_info["ip_address"],
                user_agent=device_info["user_agent"],
                metadata=metadata or {},
            )
            
            # Store session in Redis
            self._store_session(session_data)
            
            # Add to user's session list
            self._add_user_session(str(user.id), session_id)
            
            # Enforce session limit
            self._enforce_session_limit(str(user.id))
            
            logger.info(f"Created session {session_id} for user {user.username}")
            return session_data
            
        except Exception as e:
            logger.error(f"Failed to create session: {str(e)}")
            raise SessionError(f"Failed to create session: {str(e)}")
    
    def validate_session(self, session_id: str, request: Request) -> Optional[SessionData]:
        """Validate session and return session data if valid."""
        try:
            # Get session from Redis
            session_data = self._get_session(session_id)
            if not session_data:
                return None
            
            # Check if session is expired
            if session_data.is_expired:
                self._remove_session(session_id)
                return None
            
            # Check if session is inactive
            if session_data.is_inactive:
                self._deactivate_session(session_id)
                return None
            
            # Check for session hijacking
            if self._detect_session_hijacking(session_data, request):
                self._deactivate_session(session_id)
                logger.warning(f"Session hijacking detected for session {session_id}")
                return None
            
            # Update last activity
            session_data.last_activity = datetime.now()
            self._update_session_activity(session_id, session_data.last_activity)
            
            return session_data
            
        except Exception as e:
            logger.error(f"Failed to validate session {session_id}: {str(e)}")
            return None
    
    def get_user_sessions(self, user_id: str) -> List[SessionData]:
        """Get all active sessions for a user."""
        try:
            session_ids = self._get_user_session_ids(user_id)
            sessions = []
            
            for session_id in session_ids:
                session_data = self._get_session(session_id)
                if session_data and session_data.is_active and not session_data.is_expired:
                    sessions.append(session_data)
            
            return sessions
            
        except Exception as e:
            logger.error(f"Failed to get user sessions: {str(e)}")
            return []
    
    def deactivate_session(self, session_id: str) -> bool:
        """Deactivate a specific session."""
        try:
            return self._deactivate_session(session_id)
        except Exception as e:
            logger.error(f"Failed to deactivate session {session_id}: {str(e)}")
            return False
    
    def deactivate_user_sessions(self, user_id: str, exclude_session_id: Optional[str] = None) -> int:
        """Deactivate all sessions for a user except the specified one."""
        try:
            session_ids = self._get_user_session_ids(user_id)
            deactivated_count = 0
            
            for session_id in session_ids:
                if session_id != exclude_session_id:
                    if self._deactivate_session(session_id):
                        deactivated_count += 1
            
            logger.info(f"Deactivated {deactivated_count} sessions for user {user_id}")
            return deactivated_count
            
        except Exception as e:
            logger.error(f"Failed to deactivate user sessions: {str(e)}")
            return 0
    
    def refresh_session(self, session_id: str) -> Optional[SessionData]:
        """Refresh session expiration."""
        try:
            session_data = self._get_session(session_id)
            if not session_data or not session_data.is_active:
                return None
            
            # Extend session expiration
            session_data.expires_at = datetime.now() + timedelta(hours=settings.SESSION_TIMEOUT_HOURS)
            session_data.last_activity = datetime.now()
            
            # Update session in Redis
            self._store_session(session_data)
            
            logger.info(f"Refreshed session {session_id}")
            return session_data
            
        except Exception as e:
            logger.error(f"Failed to refresh session {session_id}: {str(e)}")
            return None
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions."""
        try:
            # Get all session keys
            session_keys = self.redis_client.keys(f"{self.session_prefix}*")
            cleaned_count = 0
            
            for key in session_keys:
                session_id = key.replace(self.session_prefix, "")
                session_data = self._get_session(session_id)
                
                if session_data and session_data.is_expired:
                    if self._remove_session(session_id):
                        cleaned_count += 1
            
            logger.info(f"Cleaned up {cleaned_count} expired sessions")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired sessions: {str(e)}")
            return 0
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """Get session statistics."""
        try:
            total_sessions = len(self.redis_client.keys(f"{self.session_prefix}*"))
            total_users = len(self.redis_client.keys(f"{self.user_sessions_prefix}*"))
            
            # Get active sessions
            active_sessions = 0
            expired_sessions = 0
            
            session_keys = self.redis_client.keys(f"{self.session_prefix}*")
            for key in session_keys:
                session_id = key.replace(self.session_prefix, "")
                session_data = self._get_session(session_id)
                
                if session_data:
                    if session_data.is_expired:
                        expired_sessions += 1
                    elif session_data.is_active:
                        active_sessions += 1
            
            return {
                "total_sessions": total_sessions,
                "active_sessions": active_sessions,
                "expired_sessions": expired_sessions,
                "total_users_with_sessions": total_users,
                "timestamp": datetime.now().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Failed to get session statistics: {str(e)}")
            return {}
    
    # Private methods
    def _store_session(self, session_data: SessionData) -> bool:
        """Store session data in Redis."""
        try:
            key = f"{self.session_prefix}{session_data.session_id}"
            data = session_data.to_dict()
            
            # Store with expiration
            self.redis_client.setex(
                key,
                self.session_timeout,
                json.dumps(data)
            )
            
            return True
        except Exception as e:
            logger.error(f"Failed to store session: {str(e)}")
            return False
    
    def _get_session(self, session_id: str) -> Optional[SessionData]:
        """Get session data from Redis."""
        try:
            key = f"{self.session_prefix}{session_id}"
            data = self.redis_client.get(key)
            
            if not data:
                return None
            
            return SessionData.from_dict(json.loads(data))
            
        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {str(e)}")
            return None
    
    def _remove_session(self, session_id: str) -> bool:
        """Remove session from Redis."""
        try:
            key = f"{self.session_prefix}{session_id}"
            result = self.redis_client.delete(key)
            
            # Also remove from user's session list
            self._remove_user_session(session_id)
            
            return result > 0
            
        except Exception as e:
            logger.error(f"Failed to remove session {session_id}: {str(e)}")
            return False
    
    def _deactivate_session(self, session_id: str) -> bool:
        """Deactivate session (mark as inactive)."""
        try:
            session_data = self._get_session(session_id)
            if not session_data:
                return False
            
            session_data.is_active = False
            self._store_session(session_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to deactivate session {session_id}: {str(e)}")
            return False
    
    def _add_user_session(self, user_id: str, session_id: str) -> bool:
        """Add session to user's session list."""
        try:
            key = f"{self.user_sessions_prefix}{user_id}"
            self.redis_client.sadd(key, session_id)
            self.redis_client.expire(key, self.session_timeout)
            return True
        except Exception as e:
            logger.error(f"Failed to add user session: {str(e)}")
            return False
    
    def _remove_user_session(self, session_id: str) -> bool:
        """Remove session from user's session list."""
        try:
            # Find which user owns this session
            session_data = self._get_session(session_id)
            if not session_data:
                return False
            
            key = f"{self.user_sessions_prefix}{session_data.user_id}"
            self.redis_client.srem(key, session_id)
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove user session: {str(e)}")
            return False
    
    def _get_user_session_ids(self, user_id: str) -> Set[str]:
        """Get all session IDs for a user."""
        try:
            key = f"{self.user_sessions_prefix}{user_id}"
            session_ids = self.redis_client.smembers(key)
            return session_ids
        except Exception as e:
            logger.error(f"Failed to get user session IDs: {str(e)}")
            return set()
    
    def _enforce_session_limit(self, user_id: str) -> None:
        """Enforce maximum sessions per user."""
        try:
            session_ids = self._get_user_session_ids(user_id)
            
            if len(session_ids) > self.max_sessions_per_user:
                # Remove oldest sessions
                sessions_to_remove = []
                for session_id in session_ids:
                    session_data = self._get_session(session_id)
                    if session_data:
                        sessions_to_remove.append((session_data.created_at, session_id))
                
                # Sort by creation time and remove oldest
                sessions_to_remove.sort(key=lambda x: x[0])
                sessions_to_remove = sessions_to_remove[:-self.max_sessions_per_user]
                
                for _, session_id in sessions_to_remove:
                    self._remove_session(session_id)
                
                logger.info(f"Enforced session limit for user {user_id}, removed {len(sessions_to_remove)} sessions")
                
        except Exception as e:
            logger.error(f"Failed to enforce session limit: {str(e)}")
    
    def _update_session_activity(self, session_id: str, last_activity: datetime) -> bool:
        """Update session last activity."""
        try:
            session_data = self._get_session(session_id)
            if not session_data:
                return False
            
            session_data.last_activity = last_activity
            self._store_session(session_data)
            return True
            
        except Exception as e:
            logger.error(f"Failed to update session activity: {str(e)}")
            return False
    
    def _detect_session_hijacking(self, session_data: SessionData, request: Request) -> bool:
        """Detect potential session hijacking."""
        try:
            current_ip = request.client.host if request.client else "unknown"
            current_user_agent = request.headers.get("user-agent", "")
            
            # Check IP address change
            if session_data.ip_address != current_ip:
                # Allow for proxy/CDN scenarios
                if not self._is_safe_ip_change(session_data.ip_address, current_ip):
                    return True
            
            # Check user agent change
            if session_data.user_agent != current_user_agent:
                # Allow for minor user agent changes (browser updates)
                if not self._is_safe_user_agent_change(session_data.user_agent, current_user_agent):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to detect session hijacking: {str(e)}")
            return False
    
    def _is_safe_ip_change(self, original_ip: str, current_ip: str) -> bool:
        """Check if IP change is safe (e.g., due to proxy/CDN)."""
        # This is a simplified check - in production, you might want to:
        # 1. Check if IPs are from the same subnet
        # 2. Use geolocation to check if IPs are from the same region
        # 3. Check against known proxy/CDN IP ranges
        
        # For now, we'll be conservative and consider most IP changes suspicious
        return False
    
    def _is_safe_user_agent_change(self, original_ua: str, current_ua: str) -> bool:
        """Check if user agent change is safe."""
        # Allow minor changes like version updates
        original_parts = original_ua.split()
        current_parts = current_ua.split()
        
        # If major parts (browser, OS) are the same, consider it safe
        if len(original_parts) >= 2 and len(current_parts) >= 2:
            return original_parts[0] == current_parts[0] and original_parts[1] == current_parts[1]
        
        return False


# Global session manager instance
session_manager = SessionManager()


def get_session_manager() -> SessionManager:
    """Get global session manager instance."""
    return session_manager