from collections import Counter, defaultdict
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.analytics import LinkAnalytics
from app.models.link import Link

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


@router.get("/{code}")
def get_link_analytics(
    code: str,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    cutoff = datetime.utcnow() - timedelta(days=days)

    link = db.query(Link).filter(Link.code == code).first()
    if link is None:
        raise HTTPException(status_code=404, detail="Link not found")

    analytics_rows = (
        db.query(LinkAnalytics)
        .filter(
            LinkAnalytics.link_id == link.id,
            LinkAnalytics.clicked_at >= cutoff,
        )
        .all()
    )

    countries = Counter((a.country or "--") for a in analytics_rows)
    referrers = Counter((a.referer or "Direct") for a in analytics_rows)
    user_agents = Counter((a.user_agent or "Unknown") for a in analytics_rows)

    by_date: dict[str, int] = defaultdict(int)
    by_hour: dict[int, int] = defaultdict(int)
    unique_ips = set()

    for row in analytics_rows:
        by_date[row.clicked_at.date().isoformat()] += 1
        by_hour[row.clicked_at.hour] += 1
        if row.ip_address:
            unique_ips.add(row.ip_address)

    return {
        "success": True,
        "analytics": {
            "link_code": code,
            "total_clicks": len(analytics_rows),
            "unique_ips": len(unique_ips),
            "top_countries": countries.most_common(10),
            "top_referrers": referrers.most_common(10),
            "top_user_agents": user_agents.most_common(10),
            "clicks_by_date": sorted(by_date.items()),
            "clicks_by_hour": sorted(by_hour.items()),
        },
    }
