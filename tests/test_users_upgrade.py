from fastapi.testclient import TestClient

from app.api.v1 import users
from app.config import settings
from app.main import app
from app.models.user import User


class FakeDb:
    def __init__(self):
        self.committed = False
        self.refreshed_user = None

    def commit(self):
        self.committed = True

    def refresh(self, user):
        self.refreshed_user = user


def _override_upgrade_dependencies(user: User, db: FakeDb):
    def override_get_current_user():
        return user

    def override_get_db():
        return db

    overrides = app.dependency_overrides
    overrides[users.get_current_user] = override_get_current_user
    overrides[users.get_db] = override_get_db


def test_mock_upgrade_is_blocked_in_production(monkeypatch):
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    monkeypatch.setattr(settings, "ENABLE_MOCK_BILLING", False)
    user = User(
        id=1,
        email="user@example.com",
        password_hash="hash",
        is_premium=False,
    )
    db = FakeDb()
    _override_upgrade_dependencies(user, db)

    try:
        response = TestClient(app).post("/api/v1/users/upgrade")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403
    assert response.json() == {
        "success": False,
        "error": {
            "code": "MOCK_BILLING_DISABLED",
            "message": (
                "Mock premium upgrades are disabled in production. "
                "Configure Stripe billing or set "
                "ENABLE_MOCK_BILLING=true only "
                "for controlled demos."
            ),
        },
    }
    assert user.is_premium is False
    assert db.committed is False


def test_mock_upgrade_can_be_enabled_in_production_demo(monkeypatch):
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    monkeypatch.setattr(settings, "ENABLE_MOCK_BILLING", True)
    user = User(
        id=1,
        email="user@example.com",
        password_hash="hash",
        is_premium=False,
    )
    db = FakeDb()
    _override_upgrade_dependencies(user, db)

    try:
        response = TestClient(app).post("/api/v1/users/upgrade")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["message"] == "Upgraded to premium"
    assert user.is_premium is True
    assert user.premium_until is not None
    assert db.committed is True
    assert db.refreshed_user is user
