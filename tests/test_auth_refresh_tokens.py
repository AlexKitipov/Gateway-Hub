from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.v1 import auth
from app.config import settings
from app.database.base import Base
from app.main import app
from app.models import RefreshToken  # noqa: F401 - register metadata

SQLALCHEMY_DATABASE_URL = "sqlite://"


def _client_with_db():
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[auth.get_db] = override_get_db
    return TestClient(app), TestingSessionLocal


def _register(client: TestClient) -> dict:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "refresh@example.com",
            "password": "secure-password",
            "full_name": "Refresh User",
        },
    )
    assert response.status_code == 200
    return response.json()


def test_register_persists_hashed_refresh_token_id():
    client, SessionLocal = _client_with_db()

    auth_response = _register(client)
    refresh_payload = jwt.decode(
        auth_response["refresh_token"],
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )

    with SessionLocal() as db:
        stored_token = db.query(RefreshToken).one()
        assert stored_token.user_id == auth_response["user"]["id"]
        assert stored_token.token_id_hash != refresh_payload["jti"]
        assert len(stored_token.token_id_hash) == 64
        assert stored_token.revoked_at is None

    app.dependency_overrides.clear()


def test_refresh_rotates_and_reuse_revokes_token_family():
    client, SessionLocal = _client_with_db()
    auth_response = _register(client)
    original_refresh_token = auth_response["refresh_token"]

    refresh_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": original_refresh_token},
    )

    assert refresh_response.status_code == 200
    rotated_refresh_token = refresh_response.json()["refresh_token"]
    assert rotated_refresh_token != original_refresh_token

    with SessionLocal() as db:
        tokens = db.query(RefreshToken).order_by(RefreshToken.id).all()
        assert len(tokens) == 2
        assert tokens[0].revoked_at is not None
        assert tokens[0].replaced_by_token_id == tokens[1].id
        assert tokens[1].revoked_at is None
        assert tokens[0].family_id == tokens[1].family_id

    reuse_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": original_refresh_token},
    )

    assert reuse_response.status_code == 401
    with SessionLocal() as db:
        tokens = db.query(RefreshToken).order_by(RefreshToken.id).all()
        assert all(token.revoked_at is not None for token in tokens)
        assert tokens[0].reuse_detected_at is not None

    current_token_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": rotated_refresh_token},
    )
    assert current_token_response.status_code == 401

    app.dependency_overrides.clear()


def test_logout_revokes_refresh_token():
    client, SessionLocal = _client_with_db()
    auth_response = _register(client)
    refresh_token = auth_response["refresh_token"]

    logout_response = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token},
    )

    assert logout_response.status_code == 200
    assert logout_response.json() == {"message": "Logged out successfully"}

    with SessionLocal() as db:
        stored_token = db.query(RefreshToken).one()
        assert stored_token.revoked_at is not None

    refresh_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_response.status_code == 401

    app.dependency_overrides.clear()
