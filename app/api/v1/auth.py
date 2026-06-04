from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.rate_limit import limiter
from app.models.user import User
from app.schemas.user import (
    AuthResponse,
    RefreshTokenRequest,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.security import create_token, hash_password, verify_password
from app.utils.exceptions import AppException

router = APIRouter()


@router.post("/register", response_model=AuthResponse)
@limiter.limit("3/minute")
async def register(
    request: Request, payload: UserRegisterRequest, db: Session = Depends(get_db)
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
    db.commit()
    db.refresh(user)

    access_token = create_token({"sub": user.id}, token_type="access")
    refresh_token = create_token({"sub": user.id}, token_type="refresh")

    return AuthResponse(
        user=UserResponse.model_validate(user),
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/login", response_model=AuthResponse)
@limiter.limit("5/minute")
async def login(
    request: Request, payload: UserLoginRequest, db: Session = Depends(get_db)
):
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

    access_token = create_token({"sub": user.id}, token_type="access")
    refresh_token = create_token({"sub": user.id}, token_type="refresh")

    return AuthResponse(
        user=UserResponse.model_validate(user),
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/logout")
async def logout():
    """Logout user (client-side token deletion)."""
    return {"message": "Logged out successfully"}


@router.post("/refresh", response_model=AuthResponse)
@limiter.limit("10/minute")
async def refresh_token(
    request: Request, payload: RefreshTokenRequest, db: Session = Depends(get_db)
):
    """Refresh access token using refresh token."""
    from app.security import verify_token

    payload_data = verify_token(payload.refresh_token, token_type="refresh")
    user_id = payload_data.get("sub")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
            error_code="USER_NOT_FOUND",
        )

    access_token = create_token({"sub": user.id}, token_type="access")
    new_refresh_token = create_token({"sub": user.id}, token_type="refresh")

    return AuthResponse(
        user=UserResponse.model_validate(user),
        access_token=access_token,
        refresh_token=new_refresh_token,
    )
