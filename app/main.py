import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import analytics, auth, links, redirect, users
from app.config import settings
from app.middleware.logging import RequestLoggingMiddleware, setup_logging
from app.utils.exceptions import AppException

logger = setup_logging(
    settings.APP_NAME,
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
)

app = FastAPI(title=settings.APP_NAME, version="1.0.0")

app.add_middleware(RequestLoggingMiddleware, logger=logger)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Versioned API routers
app.include_router(auth.router)
app.include_router(links.router)
app.include_router(analytics.router)
app.include_router(users.router)

# Public short-link redirect router
app.include_router(redirect.router)


def _error_response(
    *,
    status_code: int,
    error_code: str,
    message: str,
    details: object | None = None,
) -> JSONResponse:
    error: dict[str, object] = {
        "code": error_code,
        "message": message,
    }
    if details is not None:
        error["details"] = details

    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": error,
        },
    )


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    logger.warning(
        "app_exception",
        extra={
            "event": "app_exception",
            "method": request.method,
            "path": request.url.path,
            "status_code": exc.status_code,
            "error_code": exc.error_code,
        },
    )
    return _error_response(
        status_code=exc.status_code,
        error_code=exc.error_code,
        message=str(exc.detail),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    logger.warning(
        "validation_error",
        extra={
            "event": "validation_error",
            "method": request.method,
            "path": request.url.path,
            "status_code": 422,
            "error_code": "VALIDATION_ERROR",
        },
    )
    return _error_response(
        status_code=422,
        error_code="VALIDATION_ERROR",
        message="Request validation failed",
        details=jsonable_encoder(exc.errors()),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(
        "http_exception",
        extra={
            "event": "http_exception",
            "method": request.method,
            "path": request.url.path,
            "status_code": exc.status_code,
            "error_code": f"HTTP_{exc.status_code}",
        },
    )
    return _error_response(
        status_code=exc.status_code,
        error_code=f"HTTP_{exc.status_code}",
        message=str(exc.detail),
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(
        "unhandled_exception",
        extra={
            "event": "unhandled_exception",
            "method": request.method,
            "path": request.url.path,
            "status_code": 500,
            "error_code": "INTERNAL_SERVER_ERROR",
        },
    )
    return _error_response(
        status_code=500,
        error_code="INTERNAL_SERVER_ERROR",
        message="An unexpected error occurred",
    )


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": settings.APP_NAME}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
