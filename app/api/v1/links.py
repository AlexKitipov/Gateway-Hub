from datetime import datetime

from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import settings
from app.database.session import get_db
from app.models.analytics import LinkAnalytics
from app.models.link import Link
from app.models.user import User
from app.schemas.link import (
    LinkCreateRequest,
    LinkDeleteResponse,
    LinkListResponse,
    LinkResponse,
)
from app.security import get_current_user
from app.utils.exceptions import AppException
from app.utils.short_code import generate_short_code

router = APIRouter()


@router.get("/", response_model=LinkListResponse)
async def get_user_links(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """Get all links for current user."""
    total = db.query(func.count(Link.id)).filter(Link.user_id == user_id).scalar()

    links = (
        db.query(Link)
        .filter(Link.user_id == user_id, Link.is_active.is_(True))
        .order_by(Link.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    link_responses = []
    for link in links:
        link_data = LinkResponse.from_orm(link)
        link_data.short_url = f"{settings.SHORT_URL_BASE}/{link.code}"
        link_responses.append(link_data)

    return LinkListResponse(total=total, limit=limit, offset=skip, links=link_responses)


@router.post("/create", response_model=LinkResponse, status_code=status.HTTP_201_CREATED)
async def create_link(
    request: LinkCreateRequest,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new short link."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
            error_code="USER_NOT_FOUND",
        )

    if not user.is_premium:
        month_start = datetime.utcnow().replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        links_this_month = db.query(func.count(Link.id)).filter(
            Link.user_id == user_id,
            Link.created_at >= month_start,
        ).scalar()

        if links_this_month >= settings.FREE_TIER_LINKS_PER_MONTH:
            raise AppException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Free tier limit reached ({settings.FREE_TIER_LINKS_PER_MONTH} links/month)",
                error_code="LIMIT_EXCEEDED",
            )

    if request.custom_code:
        existing = db.query(Link).filter(Link.code == request.custom_code).first()
        if existing:
            raise AppException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Custom code already taken",
                error_code="CODE_TAKEN",
            )
        code = request.custom_code
    else:
        code = await generate_short_code(db)

    link = Link(
        user_id=user_id,
        code=code,
        target_url=str(request.target_url),
        title=request.title,
        description=request.description,
        created_at=datetime.utcnow(),
    )
    db.add(link)
    db.commit()
    db.refresh(link)

    response = LinkResponse.from_orm(link)
    response.short_url = f"{settings.SHORT_URL_BASE}/{link.code}"
    return response


@router.delete("/{code}", response_model=LinkDeleteResponse)
async def delete_link(
    code: str,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a short link."""
    link = db.query(Link).filter(Link.code == code, Link.user_id == user_id).first()
    if not link:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found",
            error_code="LINK_NOT_FOUND",
        )

    link.is_active = False
    db.commit()

    return LinkDeleteResponse(success=True, message="Link deleted successfully")


@router.get("/{code}", response_model=LinkResponse)
async def get_link_details(
    code: str,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get details of a specific link."""
    link = db.query(Link).filter(Link.code == code, Link.user_id == user_id).first()
    if not link:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found",
            error_code="LINK_NOT_FOUND",
        )

    response = LinkResponse.from_orm(link)
    response.short_url = f"{settings.SHORT_URL_BASE}/{link.code}"
    return response


@router.get("/r/{code}")
async def redirect_to_target(
    code: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Redirect to target URL (public endpoint)."""
    link = db.query(Link).filter(Link.code == code, Link.is_active.is_(True)).first()
    if not link:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found",
            error_code="LINK_NOT_FOUND",
        )

    user = db.query(User).filter(User.id == link.user_id).first()
    if not user.is_premium and link.click_count >= settings.FREE_TIER_CLICKS_PER_LINK:
        raise AppException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Click limit exceeded for this free link",
            error_code="CLICK_LIMIT_EXCEEDED",
        )

    analytics = LinkAnalytics(
        link_id=link.id,
        user_agent=request.headers.get("user-agent"),
        referer=request.headers.get("referer"),
        ip_address=request.client.host if request.client else None,
    )

    link.click_count += 1
    db.add(analytics)
    db.commit()

    return RedirectResponse(
        url=link.target_url,
        status_code=status.HTTP_301_MOVED_PERMANENTLY,
    )
