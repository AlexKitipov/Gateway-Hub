from datetime import datetime, timedelta

from fastapi.testclient import TestClient

from app.api.v1 import redirect
from app.config import settings
from app.main import app
from app.models.analytics import LinkAnalytics
from app.models.link import Link
from app.models.user import User


class FakeQuery:
    def __init__(self, result):
        self.result = result

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self.result


class FakeDb:
    def __init__(self, link, user):
        self.link = link
        self.user = user
        self.added = []
        self.committed = False

    def query(self, model):
        if model is Link:
            return FakeQuery(self.link)
        if model is User:
            return FakeQuery(self.user)
        raise AssertionError(f"Unexpected query model: {model}")

    def add(self, instance):
        self.added.append(instance)

    def commit(self):
        self.committed = True


def _make_link(**overrides):
    values = {
        "id": 10,
        "user_id": 20,
        "code": "abc123",
        "target_url": "https://example.com/landing",
        "click_count": 0,
        "is_active": True,
        "expires_at": None,
    }
    values.update(overrides)
    return Link(**values)


def _make_user(**overrides):
    values = {
        "id": 20,
        "email": "user@example.com",
        "password_hash": "hash",
        "is_premium": False,
    }
    values.update(overrides)
    return User(**values)


def _override_redirect_db(db):
    def override_get_db():
        return db

    app.dependency_overrides[redirect.get_db] = override_get_db


def test_redirect_records_analytics_and_uses_temporary_redirect():
    link = _make_link()
    db = FakeDb(link=link, user=_make_user())
    _override_redirect_db(db)

    try:
        response = TestClient(app).get(
            "/r/abc123",
            headers={
                "user-agent": "pytest-agent",
                "referer": "https://ref.example",
            },
            follow_redirects=False,
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 302
    assert response.headers["location"] == "https://example.com/landing"
    assert link.click_count == 1
    assert db.committed is True
    assert len(db.added) == 1
    analytics = db.added[0]
    assert isinstance(analytics, LinkAnalytics)
    assert analytics.link_id == link.id
    assert analytics.user_agent == "pytest-agent"
    assert analytics.referer == "https://ref.example"


def test_redirect_blocks_free_click_limit_without_tracking(monkeypatch):
    monkeypatch.setattr(settings, "FREE_TIER_CLICKS_PER_LINK", 1)
    link = _make_link(click_count=1)
    db = FakeDb(link=link, user=_make_user(is_premium=False))
    _override_redirect_db(db)

    try:
        response = TestClient(app).get("/r/abc123", follow_redirects=False)
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "Click limit exceeded for this free link"
    )
    assert link.click_count == 1
    assert db.added == []
    assert db.committed is False


def test_redirect_inactive_link_returns_not_found_without_tracking():
    link = _make_link(is_active=False)
    db = FakeDb(link=link, user=_make_user())
    _override_redirect_db(db)

    try:
        response = TestClient(app).get("/r/abc123", follow_redirects=False)
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == "Link not found"
    assert link.click_count == 0
    assert db.added == []
    assert db.committed is False


def test_redirect_expired_link_returns_gone_without_tracking():
    link = _make_link(expires_at=datetime.utcnow() - timedelta(seconds=1))
    db = FakeDb(link=link, user=_make_user())
    _override_redirect_db(db)

    try:
        response = TestClient(app).get("/r/abc123", follow_redirects=False)
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 410
    assert response.json()["detail"] == "Link has expired"
    assert link.click_count == 0
    assert db.added == []
    assert db.committed is False
