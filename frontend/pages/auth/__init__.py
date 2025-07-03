"""
Authentication pages for the AI Assistant Platform.

This module provides login, registration, and user profile management.
"""

from .login import LoginPage
from .register import RegisterPage
from .profile import ProfilePage

__all__ = ["LoginPage", "RegisterPage", "ProfilePage"] 