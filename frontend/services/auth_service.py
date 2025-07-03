"""
Authentication service for the AI Assistant Platform.

This module provides authentication functionality including login,
registration, and token management.
"""

import asyncio
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from nicegui import app

from .api import api_client


@dataclass
class User:
    """User data model."""
    id: str
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None
    role: str = "user"
    is_active: bool = True
    is_verified: bool = False
    created_at: Optional[datetime] = None


@dataclass
class AuthToken:
    """Authentication token data model."""
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    expires_at: datetime


class AuthService:
    """Authentication service."""
    
    def __init__(self):
        """Initialize the authentication service."""
        self.current_user: Optional[User] = None
        self.token: Optional[AuthToken] = None
        self.is_authenticated = False
    
    async def login(self, email: str, password: str) -> bool:
        """
        Login user with email and password.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            response = await api_client.login(email, password)
            
            if response.success and response.data:
                # Extract token data
                token_data = response.data
                self.token = AuthToken(
                    access_token=token_data["access_token"],
                    refresh_token=token_data["refresh_token"],
                    token_type=token_data["token_type"],
                    expires_in=token_data["expires_in"],
                    expires_at=datetime.now() + timedelta(seconds=token_data["expires_in"])
                )
                
                # Set token in API client
                api_client.set_token(self.token.access_token)
                
                # Get user data
                await self.get_current_user()
                
                self.is_authenticated = True
                
                # Store in app storage
                app.storage.user.update({
                    "token": self.token.access_token,
                    "user": {
                        "id": self.current_user.id,
                        "email": self.current_user.email,
                        "username": self.current_user.username,
                        "first_name": self.current_user.first_name,
                        "last_name": self.current_user.last_name,
                        "role": self.current_user.role,
                        "is_active": self.current_user.is_active,
                        "is_verified": self.current_user.is_verified
                    }
                })
                
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Login error: {e}")
            return False
    
    async def register(self, user_data: Dict[str, Any]) -> bool:
        """
        Register new user.
        
        Args:
            user_data: User registration data
            
        Returns:
            bool: True if registration successful, False otherwise
        """
        try:
            response = await api_client.register(user_data)
            return response.success
        except Exception as e:
            print(f"Registration error: {e}")
            return False
    
    async def get_current_user(self) -> Optional[User]:
        """
        Get current authenticated user.
        
        Returns:
            User: Current user data or None if not authenticated
        """
        try:
            response = await api_client.get_current_user()
            
            if response.success and response.data:
                user_data = response.data
                self.current_user = User(
                    id=user_data["id"],
                    username=user_data["username"],
                    email=user_data["email"],
                    first_name=user_data.get("first_name"),
                    last_name=user_data.get("last_name"),
                    display_name=user_data.get("display_name"),
                    role=user_data.get("role", "user"),
                    is_active=user_data.get("is_active", True),
                    is_verified=user_data.get("is_verified", False),
                    created_at=datetime.fromisoformat(user_data["created_at"]) if user_data.get("created_at") else None
                )
                return self.current_user
            else:
                return None
                
        except Exception as e:
            print(f"Get current user error: {e}")
            return None
    
    async def logout(self) -> bool:
        """
        Logout current user.
        
        Returns:
            bool: True if logout successful, False otherwise
        """
        try:
            response = await api_client.logout()
            
            # Clear local state regardless of API response
            self.current_user = None
            self.token = None
            self.is_authenticated = False
            api_client.clear_token()
            
            # Clear app storage
            app.storage.user.clear()
            
            return response.success
        except Exception as e:
            print(f"Logout error: {e}")
            # Clear local state even if API call fails
            self.current_user = None
            self.token = None
            self.is_authenticated = False
            api_client.clear_token()
            app.storage.user.clear()
            return True
    
    def is_token_expired(self) -> bool:
        """
        Check if current token is expired.
        
        Returns:
            bool: True if token is expired, False otherwise
        """
        if not self.token:
            return True
        
        return datetime.now() >= self.token.expires_at
    
    async def refresh_token(self) -> bool:
        """
        Refresh authentication token.
        
        Returns:
            bool: True if refresh successful, False otherwise
        """
        if not self.token:
            return False
        
        try:
            # TODO: Implement refresh token endpoint
            # response = await api_client.refresh_token(self.token.refresh_token)
            
            # For now, just return False to force re-login
            return False
                
        except Exception as e:
            print(f"Token refresh error: {e}")
            return False
    
    def get_user_display_name(self) -> str:
        """
        Get user display name.
        
        Returns:
            str: User display name
        """
        if not self.current_user:
            return "Guest"
        
        if self.current_user.display_name:
            return self.current_user.display_name
        
        if self.current_user.first_name and self.current_user.last_name:
            return f"{self.current_user.first_name} {self.current_user.last_name}"
        
        return self.current_user.username
    
    def has_role(self, role: str) -> bool:
        """
        Check if user has specific role.
        
        Args:
            role: Role to check
            
        Returns:
            bool: True if user has role
        """
        if not self.current_user:
            return False
        
        return self.current_user.role == role
    
    def is_admin(self) -> bool:
        """
        Check if user is admin.
        
        Returns:
            bool: True if user is admin
        """
        return self.has_role("admin")
    
    def load_from_storage(self) -> bool:
        """
        Load authentication state from storage.
        
        Returns:
            bool: True if loaded successfully
        """
        try:
            user_data = app.storage.user.get("user")
            token = app.storage.user.get("token")
            
            if user_data and token:
                # Set token in API client
                api_client.set_token(token)
                
                # Create user object
                self.current_user = User(
                    id=user_data["id"],
                    email=user_data["email"],
                    username=user_data["username"],
                    first_name=user_data.get("first_name"),
                    last_name=user_data.get("last_name"),
                    display_name=user_data.get("display_name"),
                    role=user_data["role"],
                    is_active=user_data["is_active"],
                    is_verified=user_data["is_verified"]
                )
                
                self.is_authenticated = True
                return True
            
            return False
        except Exception:
            return False


# Global auth service instance
auth_service = AuthService() 