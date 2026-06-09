from datetime import datetime, timedelta
from typing import Any, Optional

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def _token_expiration(token_type: str, expires_delta: Optional[timedelta]) -> datetime:
    if expires_delta:
        return datetime.utcnow() + expires_delta

    if token_type == "access":
        return datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    if token_type == "refresh":
        return datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Unsupported token type",
    )


def create_token(
    data: dict[str, Any],
    expires_delta: Optional[timedelta] = None,
    token_type: str = "access",
) -> str:
    """Create a JWT with a string subject claim."""
    to_encode = data.copy()
    if "sub" in to_encode and to_encode["sub"] is not None:
        to_encode["sub"] = str(to_encode["sub"])

    to_encode.update(
        {
            "exp": _token_expiration(token_type, expires_delta),
            "type": token_type,
        }
    )
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def verify_token(token: str, token_type: str = "access") -> dict[str, Any]:
    """Verify a JWT and return its decoded payload."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        if payload.get("type") != token_type:
            raise JWTError("Invalid token type")

        if payload.get("sub") is None:
            raise JWTError("Missing token subject")

        return payload
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def token_subject_as_user_id(payload: dict[str, Any]) -> int:
    """Parse the token subject into a user id at the auth boundary."""
    subject = payload.get("sub")
    try:
        user_id = int(subject)
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    if user_id < 1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id
