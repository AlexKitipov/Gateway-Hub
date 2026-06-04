from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.analytics import LinkAnalytics
from app.models.link import Link
from app.schemas.analytics import LinkAnalyticsResponse
from app.security import get_current_user
from app.utils.exceptions import AppException

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


@router.get("/{code}", response_model=LinkAnalyticsResponse)
async def get_link_analytics(
    code: str,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = Query(30, ge=1, le=365),
):
    """Get analytics for a specific link."""
    link = db.query(Link).filter(Link.code == code, Link.user_id == user_id).first()
    if not link:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found",
            error_code="LINK_NOT_FOUND",
        )

    since = datetime.utcnow() - timedelta(days=days)
    analytics = (
        db.query(LinkAnalytics)
        .filter(
            LinkAnalytics.link_id == link.id,
            LinkAnalytics.clicked_at >= since,
        )
        .all()
    )

    total_clicks = len(analytics)
    unique_ips = len({a.ip_address for a in analytics if a.ip_address})

    top_countries = []
    if analytics:
        country_counts = (
            db.query(LinkAnalytics.country, func.count(LinkAnalytics.id))
            .filter(
                LinkAnalytics.link_id == link.id,
                LinkAnalytics.clicked_at >= since,
                LinkAnalytics.country.isnot(None),
            )
            .group_by(LinkAnalytics.country)
            .order_by(func.count(LinkAnalytics.id).desc())
            .limit(10)
            .all()
        )
        top_countries = [(country, count) for country, count in country_counts]

    top_referrers = []
    if analytics:
        referrer_counts = (
            db.query(LinkAnalytics.referer, func.count(LinkAnalytics.id))
            .filter(
                LinkAnalytics.link_id == link.id,
                LinkAnalytics.clicked_at >= since,
                LinkAnalytics.referer.isnot(None),
            )
            .group_by(LinkAnalytics.referer)
            .order_by(func.count(LinkAnalytics.id).desc())
            .limit(10)
            .all()
        )
        top_referrers = [(referrer, count) for referrer, count in referrer_counts]

    clicks_by_date = []
    if analytics:
        date_counts = (
            db.query(func.date(LinkAnalytics.clicked_at), func.count(LinkAnalytics.id))
            .filter(
                LinkAnalytics.link_id == link.id,
                LinkAnalytics.clicked_at >= since,
            )
            .group_by(func.date(LinkAnalytics.clicked_at))
            .order_by(func.date(LinkAnalytics.clicked_at))
            .all()
        )
        clicks_by_date = [(str(day), count) for day, count in date_counts]

    clicks_by_hour = []
    if analytics:
        hour_counts = (
            db.query(
                func.extract("hour", LinkAnalytics.clicked_at),
                func.count(LinkAnalytics.id),
            )
            .filter(
                LinkAnalytics.link_id == link.id,
                LinkAnalytics.clicked_at >= since,
            )
            .group_by(func.extract("hour", LinkAnalytics.clicked_at))
            .order_by(func.extract("hour", LinkAnalytics.clicked_at))
            .all()
        )
        clicks_by_hour = [(int(hour), count) for hour, count in hour_counts]

    return LinkAnalyticsResponse(
        link_code=code,
        total_clicks=total_clicks,
        unique_ips=unique_ips,
        top_countries=top_countries,
        top_referrers=top_referrers,
        clicks_by_date=clicks_by_date,
        clicks_by_hour=clicks_by_hour,
    )
