"""
Authentication service for the frontend.

This module provides authentication state management and user session handling.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass
from nicegui import app


@dataclass
class User:
    """User data model."""
    id: str
    email: str
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None
    role: str = "user"
    is_active: bool = True
    is_verified: bool = False


class AuthService:
    """Authentication service for managing user sessions."""
    
    def __init__(self):
        self.current_user: Optional[User] = None
        self.token: Optional[str] = None
        self.is_authenticated: bool = False
    
    def login(self, token: str, user_data: Dict[str, Any]) -> None:
        """
        Login user with token and user data.
        
        Args:
            token: JWT access token
            user_data: User information
        """
        self.token = token
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
        
        # Store in app storage
        app.storage.user.update({
            "token": token,
            "user": user_data
        })
    
    def logout(self) -> None:
        """Logout current user."""
        self.token = None
        self.current_user = None
        self.is_authenticated = False
        
        # Clear app storage
        app.storage.user.clear()
    
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
                self.login(token, user_data)
                return True
            
            return False
        except Exception:
            return False


# Global auth service instance
auth_service = AuthService() 