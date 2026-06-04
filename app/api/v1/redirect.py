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


@router.get("/{code}")
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
