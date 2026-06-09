from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.schemas.user import (
    AuthResponse,
    LogoutRequest,
    RefreshTokenRequest,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)


def test_user_register_request_accepts_valid_payload():
    payload = UserRegisterRequest(
        email="new-user@example.com",
        password="secure-password",
        full_name="New User",
    )

    assert payload.email == "new-user@example.com"
    assert payload.password == "secure-password"
    assert payload.full_name == "New User"


def test_user_register_request_rejects_invalid_email_and_short_password():
    with pytest.raises(ValidationError) as exc_info:
        UserRegisterRequest(email="not-an-email", password="short")

    errors = {tuple(error["loc"]): error["type"] for error in exc_info.value.errors()}
    assert errors[("email",)] == "value_error"
    assert errors[("password",)] == "string_too_short"


def test_user_login_request_requires_valid_email():
    with pytest.raises(ValidationError) as exc_info:
        UserLoginRequest(email="invalid", password="password")

    assert exc_info.value.errors()[0]["loc"] == ("email",)


def test_refresh_token_request_requires_token_value():
    payload = RefreshTokenRequest(refresh_token="refresh-token")

    assert payload.refresh_token == "refresh-token"


def test_logout_request_requires_token_value():
    payload = LogoutRequest(refresh_token="refresh-token")

    assert payload.refresh_token == "refresh-token"


def test_auth_response_serializes_user_payload():
    user = UserResponse(
        id=1,
        email="user@example.com",
        full_name="User Example",
        is_premium=False,
        is_active=True,
        premium_until=None,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )

    response = AuthResponse(
        access_token="access-token",
        refresh_token="refresh-token",
        user=user,
    )

    assert response.token_type == "bearer"
    assert response.user.email == "user@example.com"
