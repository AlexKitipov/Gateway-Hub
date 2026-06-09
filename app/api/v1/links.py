from datetime import datetime

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import settings
from app.database.session import get_db
from app.dependencies import get_current_user
from app.models.link import Link
from app.models.user import User
from app.schemas.link import (
    LinkCreateRequest,
    LinkDeleteResponse,
    LinkListResponse,
    LinkResponse,
)
from app.utils.exceptions import AppException
from app.utils.short_code import generate_short_code, validate_custom_code

router = APIRouter(prefix="/api/v1/links", tags=["links"])


@router.get("/", response_model=LinkListResponse)
def get_user_links(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """Get all links for current user."""
    total = (
        db.query(func.count(Link.id)).filter(Link.user_id == current_user.id).scalar()
    )

    links = (
        db.query(Link)
        .filter(Link.user_id == current_user.id, Link.is_active.is_(True))
        .order_by(Link.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    link_responses = []
    for link in links:
        link_data = LinkResponse.model_validate(link)
        link_data.short_url = f"{settings.SHORT_URL_BASE}/{link.code}"
        link_responses.append(link_data)

    return LinkListResponse(total=total, limit=limit, offset=skip, links=link_responses)


@router.post(
    "/create", response_model=LinkResponse, status_code=status.HTTP_201_CREATED
)
def create_link(
    request: LinkCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new short link."""
    if not current_user.is_premium:
        month_start = datetime.utcnow().replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        links_this_month = (
            db.query(func.count(Link.id))
            .filter(
                Link.user_id == current_user.id,
                Link.created_at >= month_start,
            )
            .scalar()
        )

        if links_this_month >= settings.FREE_TIER_LINKS_PER_MONTH:
            raise AppException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Free tier limit reached "
                    f"({settings.FREE_TIER_LINKS_PER_MONTH} links/month)"
                ),
                error_code="LIMIT_EXCEEDED",
            )

    if request.custom_code:
        if not validate_custom_code(request.custom_code):
            raise AppException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid custom code format",
                error_code="INVALID_CODE",
            )

        existing = db.query(Link).filter(Link.code == request.custom_code).first()
        if existing:
            raise AppException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Custom code already taken",
                error_code="CODE_TAKEN",
            )
        code = request.custom_code
    else:
        code = generate_short_code(db)

    link = Link(
        user_id=current_user.id,
        code=code,
        target_url=str(request.target_url),
        title=request.title,
        description=request.description,
        expires_at=request.expires_at,
        created_at=datetime.utcnow(),
    )
    db.add(link)
    db.commit()
    db.refresh(link)

    response = LinkResponse.model_validate(link)
    response.short_url = f"{settings.SHORT_URL_BASE}/{link.code}"
    return response


@router.delete("/{code}", response_model=LinkDeleteResponse)
def delete_link(
    code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a short link."""
    link = (
        db.query(Link)
        .filter(Link.code == code, Link.user_id == current_user.id)
        .first()
    )
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
def get_link_details(
    code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get details of a specific link."""
    link = (
        db.query(Link)
        .filter(Link.code == code, Link.user_id == current_user.id)
        .first()
    )
    if not link:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found",
            error_code="LINK_NOT_FOUND",
        )

    response = LinkResponse.model_validate(link)
    response.short_url = f"{settings.SHORT_URL_BASE}/{link.code}"
    return response
