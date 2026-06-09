from datetime import datetime

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database.session import get_db
from app.models.analytics import LinkAnalytics
from app.models.link import Link
from app.models.user import User
from app.utils.exceptions import AppException

router = APIRouter(prefix="/r", tags=["redirect"])

REDIRECT_STATUS_CODE = status.HTTP_302_FOUND


def _get_redirectable_link(db: Session, code: str) -> Link:
    link = db.query(Link).filter(Link.code == code).first()
    now = datetime.utcnow()

    if not link or not link.is_active:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found",
            error_code="LINK_NOT_FOUND",
        )

    if link.expires_at and link.expires_at <= now:
        raise AppException(
            status_code=status.HTTP_410_GONE,
            detail="Link has expired",
            error_code="LINK_EXPIRED",
        )

    return link


def _enforce_click_limit(db: Session, link: Link) -> None:
    user = db.query(User).filter(User.id == link.user_id).first()
    if (
        user
        and not user.is_premium
        and link.click_count >= settings.FREE_TIER_CLICKS_PER_LINK
    ):
        raise AppException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Click limit exceeded for this free link",
            error_code="CLICK_LIMIT_EXCEEDED",
        )


def _record_click(db: Session, link: Link, request: Request) -> None:
    analytics = LinkAnalytics(
        link_id=link.id,
        user_agent=request.headers.get("user-agent"),
        referer=request.headers.get("referer"),
        ip_address=request.client.host if request.client else None,
    )

    link.click_count += 1
    db.add(analytics)
    db.commit()


@router.get("/{code}")
def redirect_to_target(
    code: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Redirect to target URL (public endpoint)."""
    link = _get_redirectable_link(db, code)
    _enforce_click_limit(db, link)
    _record_click(db, link, request)

    return RedirectResponse(
        url=link.target_url,
        status_code=REDIRECT_STATUS_CODE,
    )
