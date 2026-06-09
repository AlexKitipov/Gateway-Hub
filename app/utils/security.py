"""Compatibility exports for the canonical app.security module."""

from datetime import timedelta
from typing import Any, Optional

from app.security import (
    create_token,
    hash_password,
    token_subject_as_user_id,
    verify_password,
    verify_token,
)


def create_access_token(
    data: dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    return create_token(data, expires_delta=expires_delta, token_type="access")


def create_refresh_token(data: dict[str, Any]) -> str:
    return create_token(data, token_type="refresh")


__all__ = [
    "create_access_token",
    "create_refresh_token",
    "create_token",
    "hash_password",
    "token_subject_as_user_id",
    "verify_password",
    "verify_token",
]
