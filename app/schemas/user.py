from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=255)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserResponse(UserBase):
    id: int
    is_premium: bool
    is_active: bool
    premium_until: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserStats(BaseModel):
    total_links: int
    total_clicks: int
    links_this_month: int
    is_premium: bool
    premium_until: Optional[datetime] = None
    links_limit: int
    links_remaining: int


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse
