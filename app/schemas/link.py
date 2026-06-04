from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class LinkCreate(BaseModel):
    target_url: HttpUrl
    title: Optional[str] = None
    description: Optional[str] = None
    custom_code: Optional[str] = Field(None, min_length=3, max_length=20)
    expires_at: Optional[datetime] = None


class LinkCreateRequest(LinkCreate):
    """Request body for creating a short link."""


class LinkUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class LinkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    target_url: str
    title: Optional[str] = None
    description: Optional[str] = None
    click_count: int
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime] = None
    short_url: str = ""


class LinkDeleteResponse(BaseModel):
    success: bool
    message: str


class LinkListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    links: list[LinkResponse]
