from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import settings
from app.database.session import get_db
from app.dependencies import get_current_user
from app.models.link import Link
from app.models.user import User
from app.schemas.user import UserStatsResponse
from app.utils.exceptions import AppException

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/stats", response_model=UserStatsResponse)
def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user statistics and plan info."""
    total_links = (
        db.query(func.count(Link.id)).filter(Link.user_id == current_user.id).scalar()
    )
    total_clicks = (
        db.query(func.sum(Link.click_count))
        .filter(Link.user_id == current_user.id)
        .scalar()
        or 0
    )

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

    return UserStatsResponse(
        total_links=total_links,
        total_clicks=total_clicks,
        links_this_month=links_this_month,
        is_premium=current_user.is_premium,
        premium_until=current_user.premium_until,
    )


def _mock_billing_enabled() -> bool:
    return settings.ENVIRONMENT.lower() != "production" or settings.ENABLE_MOCK_BILLING


@router.post("/upgrade")
def upgrade_to_premium(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upgrade user to premium using the development/demo mock billing flow."""
    if not _mock_billing_enabled():
        raise AppException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Mock premium upgrades are disabled in production. "
                "Configure Stripe billing or set ENABLE_MOCK_BILLING=true only "
                "for controlled demos."
            ),
            error_code="MOCK_BILLING_DISABLED",
        )

    if current_user.is_premium:
        raise AppException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already premium",
            error_code="ALREADY_PREMIUM",
        )

    current_user.is_premium = True
    current_user.premium_until = datetime.utcnow() + timedelta(days=365)
    db.commit()
    db.refresh(current_user)

    return {
        "success": True,
        "message": "Upgraded to premium",
        "premium_until": current_user.premium_until,
    }
