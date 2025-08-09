"""
Common Pydantic models for authentication endpoints.

This module contains shared models used across all authentication endpoints.
"""

from pydantic import BaseModel, EmailStr


class UserLogin(BaseModel):
    """User login credentials."""

    email: EmailStr | None = None
    username: str | None = None
    password: str


class UserRegister(BaseModel):
    """User registration data."""

    email: EmailStr
    username: str
    password: str
    first_name: str | None = None
    last_name: str | None = None


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""

    refresh_token: str


class TokenResponse(BaseModel):
    """Token response."""

    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class UserResponse(BaseModel):
    """User response."""

    id: str
    email: str
    username: str
    first_name: str | None
    last_name: str | None
    display_name: str | None
    role: str
    is_active: bool
    is_verified: bool


class PasswordResetRequest(BaseModel):
    """Password reset request."""

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation."""

    token: str
    new_password: str
