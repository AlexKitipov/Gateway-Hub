from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=255)


class UserRegisterRequest(UserCreate):
    """Request body for registering a user."""


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserLoginRequest(UserLogin):
    """Request body for logging in a user."""


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_premium: bool
    is_active: bool
    premium_until: Optional[datetime] = None
    created_at: datetime


class UserStats(BaseModel):
    total_links: int
    total_clicks: int
    links_this_month: int
    is_premium: bool
    premium_until: Optional[datetime] = None
    links_limit: int
    links_remaining: int


class UserStatsResponse(BaseModel):
    total_links: int
    total_clicks: int
    links_this_month: int
    is_premium: bool
    premium_until: Optional[datetime] = None


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


TokenResponse = AuthResponse
