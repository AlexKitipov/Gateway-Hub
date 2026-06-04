from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.link import Link
from app.models.user import User
from app.schemas.user import UserStatsResponse
from app.security import get_current_user
from app.utils.exceptions import AppException

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/stats", response_model=UserStatsResponse)
async def get_user_stats(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user statistics and plan info."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
            error_code="USER_NOT_FOUND",
        )

    total_links = db.query(func.count(Link.id)).filter(Link.user_id == user_id).scalar()
    total_clicks = (
        db.query(func.sum(Link.click_count)).filter(Link.user_id == user_id).scalar()
        or 0
    )

    month_start = datetime.utcnow().replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )
    links_this_month = (
        db.query(func.count(Link.id))
        .filter(
            Link.user_id == user_id,
            Link.created_at >= month_start,
        )
        .scalar()
    )

    return UserStatsResponse(
        total_links=total_links,
        total_clicks=total_clicks,
        links_this_month=links_this_month,
        is_premium=user.is_premium,
        premium_until=user.premium_until,
    )


@router.post("/upgrade")
async def upgrade_to_premium(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upgrade user to premium."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
            error_code="USER_NOT_FOUND",
        )

    if user.is_premium:
        raise AppException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already premium",
            error_code="ALREADY_PREMIUM",
        )

    user.is_premium = True
    user.premium_until = datetime.utcnow() + timedelta(days=365)
    db.commit()
    db.refresh(user)

    return {
        "success": True,
        "message": "Upgraded to premium",
        "premium_until": user.premium_until,
    }
