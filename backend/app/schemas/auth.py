"""
Authentication schemas for user login, registration, and SSO.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Any, Dict, Optional

from app.models.user import UserRole, AuthProvider


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserLogin(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1)


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=1, max_length=100)
    role: UserRole = UserRole.USER


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user_id: str
    username: str
    provider: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None


class SSOLoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1)
    provider: Optional[str] = None


class SSOProviderInfo(BaseModel):
    name: str
    type: str
    enabled: bool
    priority: int


class SSOConfig(BaseModel):
    provider_name: str
    provider_type: str
    enabled: bool
    priority: int
    config: Dict[str, Any]


class SSOUserSync(BaseModel):
    user_id: str
    provider: str
    sync_groups: bool = True
    sync_attributes: bool = True


class SSOHealthCheck(BaseModel):
    status: str
    providers: list
    timestamp: str
    error: Optional[str] = None


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


class ChangePassword(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: Optional[str] = None
    all_sessions: bool = False