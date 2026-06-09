from datetime import timedelta

import pytest
from fastapi import HTTPException

from app.security import create_token, token_subject_as_user_id, verify_token
from app.utils.security import create_access_token, create_refresh_token


def test_create_token_normalizes_subject_to_string():
    token = create_token({"sub": 42}, expires_delta=timedelta(minutes=5))

    payload = verify_token(token)

    assert payload["sub"] == "42"
    assert token_subject_as_user_id(payload) == 42


def test_refresh_token_requires_refresh_type():
    refresh = create_token({"sub": 42}, token_type="refresh")

    payload = verify_token(refresh, token_type="refresh")

    assert payload["sub"] == "42"


def test_verify_token_rejects_wrong_token_type():
    access = create_token({"sub": 42}, token_type="access")

    with pytest.raises(HTTPException) as exc_info:
        verify_token(access, token_type="refresh")

    assert exc_info.value.status_code == 401


def test_token_subject_as_user_id_rejects_non_integer_subject():
    with pytest.raises(HTTPException) as exc_info:
        token_subject_as_user_id({"sub": "not-an-int"})

    assert exc_info.value.status_code == 401


def test_utils_security_delegates_to_canonical_token_helpers():
    access_payload = verify_token(create_access_token({"sub": 5}))
    refresh_payload = verify_token(
        create_refresh_token({"sub": 6}), token_type="refresh"
    )

    assert access_payload["sub"] == "5"
    assert refresh_payload["sub"] == "6"
