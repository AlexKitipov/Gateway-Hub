from fastapi import HTTPException, status


class AppException(HTTPException):
    """HTTP exception carrying a stable application error code."""

    def __init__(
        self,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        detail: str = "Bad request",
        error_code: str = "BAD_REQUEST",
    ) -> None:
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code
