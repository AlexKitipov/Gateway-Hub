from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime
from typing import Optional


class LinkCreate(BaseModel):
    target_url: HttpUrl
    title: Optional[str] = None
    description: Optional[str] = None
    custom_code: Optional[str] = Field(None, min_length=3, max_length=20)
    expires_at: Optional[datetime] = None


class LinkUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class LinkResponse(BaseModel):
    id: int
    code: str
    target_url: str
    title: Optional[str] = None
    description: Optional[str] = None
    click_count: int
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime] = None
    short_url: str

    class Config:
        from_attributes = True


class LinkListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    links: list[LinkResponse]
