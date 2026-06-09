import secrets
from datetime import datetime, timedelta
from hashlib import sha256

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database.session import get_db
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.rate_limit import limiter
from app.schemas.user import (
    AuthResponse,
    LogoutRequest,
    RefreshTokenRequest,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.security import (
    create_token,
    hash_password,
    token_subject_as_user_id,
    verify_password,
    verify_token,
)
from app.utils.exceptions import AppException

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def _hash_refresh_token_id(token_id: str) -> str:
    return sha256(token_id.encode("utf-8")).hexdigest()


def _refresh_token_lifetime() -> timedelta:
    return timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)


def _issue_refresh_token(
    db: Session,
    user: User,
    parent: RefreshToken | None = None,
) -> tuple[str, RefreshToken]:
    token_id = secrets.token_urlsafe(32)
    family_id = parent.family_id if parent else secrets.token_hex(32)
    expires_delta = _refresh_token_lifetime()
    expires_at = datetime.utcnow() + expires_delta

    token = create_token(
        {"sub": user.id, "jti": token_id},
        expires_delta=expires_delta,
        token_type="refresh",
    )
    token_record = RefreshToken(
        user_id=user.id,
        token_id_hash=_hash_refresh_token_id(token_id),
        family_id=family_id,
        parent_token_id=parent.id if parent else None,
        expires_at=expires_at,
    )
    db.add(token_record)
    db.flush()
    return token, token_record


def _create_auth_response(db: Session, user: User) -> AuthResponse:
    access_token = create_token({"sub": user.id}, token_type="access")
    refresh_token, _ = _issue_refresh_token(db, user)
    db.commit()
    db.refresh(user)

    return AuthResponse(
        user=UserResponse.model_validate(user),
        access_token=access_token,
        refresh_token=refresh_token,
    )


def _get_refresh_token_id(payload_data: dict) -> str:
    token_id = payload_data.get("jti")
    if not isinstance(token_id, str) or not token_id:
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            error_code="INVALID_REFRESH_TOKEN",
        )
    return token_id


def _revoke_refresh_token_family(
    db: Session,
    family_id: str,
    now: datetime,
    reuse_detected_token: RefreshToken | None = None,
) -> None:
    active_family_tokens = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.family_id == family_id,
            RefreshToken.revoked_at.is_(None),
        )
        .all()
    )
    for token_record in active_family_tokens:
        token_record.revoked_at = now

    if reuse_detected_token and reuse_detected_token.reuse_detected_at is None:
        reuse_detected_token.reuse_detected_at = now


def _load_refresh_token_for_update(
    db: Session,
    refresh_token: str,
) -> tuple[dict, RefreshToken]:
    payload_data = verify_token(refresh_token, token_type="refresh")
    token_id = _get_refresh_token_id(payload_data)
    token_record = (
        db.query(RefreshToken)
        .filter(RefreshToken.token_id_hash == _hash_refresh_token_id(token_id))
        .first()
    )
    if not token_record:
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            error_code="INVALID_REFRESH_TOKEN",
        )
    return payload_data, token_record


def _ensure_refresh_token_is_active(db: Session, token_record: RefreshToken) -> None:
    now = datetime.utcnow()
    if (
        token_record.revoked_at is not None
        or token_record.replaced_by_token_id is not None
    ):
        _revoke_refresh_token_family(
            db,
            token_record.family_id,
            now,
            reuse_detected_token=token_record,
        )
        db.commit()
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token reuse detected",
            error_code="REFRESH_TOKEN_REUSE_DETECTED",
        )

    if token_record.expires_at <= now:
        token_record.revoked_at = now
        db.commit()
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            error_code="INVALID_OR_EXPIRED_REFRESH_TOKEN",
        )


@router.post("/register", response_model=AuthResponse)
@limiter.limit("3/minute")
def register(
    request: Request,
    payload: UserRegisterRequest,
    db: Session = Depends(get_db),
):
    """Register a new user."""
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise AppException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
            error_code="EMAIL_ALREADY_EXISTS",
        )

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        is_premium=False,
    )
    db.add(user)
    db.flush()

    return _create_auth_response(db, user)


@router.post("/login", response_model=AuthResponse)
@limiter.limit("5/minute")
def login(request: Request, payload: UserLoginRequest, db: Session = Depends(get_db)):
    """Login user."""
    user = db.query(User).filter(User.email == payload.email).first()

    if not user or not verify_password(payload.password, user.password_hash):
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            error_code="INVALID_CREDENTIALS",
        )

    if not user.is_active:
        raise AppException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
            error_code="ACCOUNT_DISABLED",
        )

    return _create_auth_response(db, user)


@router.post("/logout")
def logout(payload: LogoutRequest, db: Session = Depends(get_db)):
    """Revoke the supplied refresh token for logout."""
    _, token_record = _load_refresh_token_for_update(db, payload.refresh_token)

    if token_record.revoked_at is None:
        token_record.revoked_at = datetime.utcnow()
        db.commit()

    return {"message": "Logged out successfully"}


@router.post("/refresh", response_model=AuthResponse)
@limiter.limit("10/minute")
def refresh_token(
    request: Request,
    payload: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    """Rotate a persisted refresh token and return a new token pair."""
    payload_data, token_record = _load_refresh_token_for_update(
        db, payload.refresh_token
    )
    _ensure_refresh_token_is_active(db, token_record)
    user_id = token_subject_as_user_id(payload_data)

    if token_record.user_id != user_id:
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            error_code="INVALID_REFRESH_TOKEN",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive user",
            error_code="INVALID_OR_INACTIVE_USER",
        )

    access_token = create_token({"sub": user.id}, token_type="access")
    new_refresh_token, new_token_record = _issue_refresh_token(db, user, token_record)
    token_record.revoked_at = datetime.utcnow()
    token_record.replaced_by_token_id = new_token_record.id
    db.commit()
    db.refresh(user)

    return AuthResponse(
        user=UserResponse.model_validate(user),
        access_token=access_token,
        refresh_token=new_refresh_token,
    )
