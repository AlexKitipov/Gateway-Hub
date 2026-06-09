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


def test_app_exception_handler_preserves_error_code():
    from fastapi import status

    from app.main import app
    from app.utils.exceptions import AppException

    app_exception_route_exists = any(
        route.path == "/__test__/app-exception" for route in app.routes
    )
    if not app_exception_route_exists:

        @app.get("/__test__/app-exception")
        async def app_exception_test_route():
            raise AppException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Custom client error",
                error_code="CUSTOM_CLIENT_ERROR",
            )

    client = TestClient(app)

    response = client.get("/__test__/app-exception")

    assert response.status_code == 409
    assert response.json() == {
        "success": False,
        "error": {
            "code": "CUSTOM_CLIENT_ERROR",
            "message": "Custom client error",
        },
    }


def test_validation_error_handler_returns_standard_error_shape():
    from app.main import app

    if not any(route.path == "/__test__/validation" for route in app.routes):

        @app.get("/__test__/validation")
        async def validation_test_route(limit: int):
            return {"limit": limit}

    client = TestClient(app)

    response = client.get(
        "/__test__/validation",
        params={"limit": "not-an-int"},
    )

    assert response.status_code == 422
    payload = response.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "VALIDATION_ERROR"
    assert payload["error"]["message"] == "Request validation failed"
    assert payload["error"]["details"][0]["loc"] == ["query", "limit"]


def test_setup_logging_emits_json_to_stdout_without_file_handler(capsys):
    import json
    import logging

    from app.middleware.logging import setup_logging

    logger = setup_logging("test-json-logger")

    assert not any(
        isinstance(handler, logging.FileHandler) for handler in logger.handlers
    )

    logger.info(
        "structured_event",
        extra={"event": "test_event", "status_code": 200},
    )

    payload = json.loads(capsys.readouterr().out)
    assert payload["logger"] == "test-json-logger"
    assert payload["level"] == "INFO"
    assert payload["message"] == "structured_event"
    assert payload["event"] == "test_event"
    assert payload["status_code"] == 200
