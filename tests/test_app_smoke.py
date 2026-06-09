from fastapi.testclient import TestClient


def test_app_main_imports():
    import app.main

    assert app.main.app.title == "Gateway Hub"


def test_health_endpoint_returns_healthy_status():
    from app.main import app

    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "Gateway Hub"}


def test_auth_register_route_is_registered():
    from app.main import app

    registered_routes = {
        (route.path, method)
        for route in app.routes
        for method in getattr(route, "methods", set())
    }

    assert ("/api/v1/auth/register", "POST") in registered_routes
