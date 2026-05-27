from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class LinkCreateRequest(BaseModel):
    target_url: HttpUrl
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    custom_code: Optional[str] = Field(
        None,
        min_length=3,
        max_length=20,
        pattern=r"^[a-zA-Z0-9_-]+$",
    )


class LinkResponse(BaseModel):
    id: int
    code: str
    target_url: str
    title: Optional[str]
    description: Optional[str]
    click_count: int
    is_active: bool
    created_at: datetime
    short_url: str

    class Config:
        from_attributes = True


class LinkListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    links: list[LinkResponse]


class LinkDeleteResponse(BaseModel):
    success: bool
    message: str
