"""
Authentication pages for the AI Assistant Platform.

This module provides login, registration, and user profile management.
"""

from .login import LoginPage
from .profile import ProfilePage
from .register import RegisterPage

__all__ = ["LoginPage", "RegisterPage", "ProfilePage"]
