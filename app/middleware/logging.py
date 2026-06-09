import json
import logging
import sys
import time
from datetime import datetime, timezone
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

_RESERVED_LOG_RECORD_ATTRS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
}


def _is_extra_log_attr(key: str) -> bool:
    return key not in _RESERVED_LOG_RECORD_ATTRS and not key.startswith("_")


class JsonLogFormatter(logging.Formatter):
    """Format log records as newline-delimited JSON for container logs."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        for key, value in record.__dict__.items():
            if _is_extra_log_attr(key):
                payload[key] = value

        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


def setup_logging(
    app_name: str,
    *,
    level: int = logging.INFO,
    log_file: str | None = None,
) -> logging.Logger:
    """Set up structured application logging.

    Logs are emitted to stdout by default so deployments can collect them
    from the process stream. A file handler is only added when ``log_file``
    is explicitly provided by the caller.
    """
    logger = logging.getLogger(app_name)
    logger.setLevel(level)
    logger.propagate = False

    formatter = JsonLogFormatter()

    logger.handlers.clear()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Emit one structured log event for every completed HTTP request."""

    def __init__(self, app, *, logger: logging.Logger):
        super().__init__(app)
        self.logger = logger

    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            self.logger.exception(
                "request_failed",
                extra={
                    "event": "http_request",
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": duration_ms,
                },
            )
            raise

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        self.logger.info(
            "request_completed",
            extra={
                "event": "http_request",
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )

        return response
