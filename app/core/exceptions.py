"""
Custom exception classes and FastAPI exception handlers.
"""
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse


class SabiTaxException(Exception):
    """Base exception for SabiTax application."""

    def __init__(
        self,
        message: str = "An error occurred",
        code: str = "INTERNAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(SabiTaxException):
    """Resource not found exception."""

    def __init__(
        self,
        message: str = "Resource not found",
        resource: str | None = None,
    ):
        super().__init__(
            message=message,
            code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource": resource} if resource else {},
        )


class UnauthorizedError(SabiTaxException):
    """Authentication required exception."""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            code="UNAUTHORIZED",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class ForbiddenError(SabiTaxException):
    """Permission denied exception."""

    def __init__(self, message: str = "Permission denied"):
        super().__init__(
            message=message,
            code="FORBIDDEN",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class BadRequestError(SabiTaxException):
    """Invalid request exception."""

    def __init__(
        self,
        message: str = "Invalid request",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            message=message,
            code="BAD_REQUEST",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class ConflictError(SabiTaxException):
    """Resource conflict exception."""

    def __init__(
        self,
        message: str = "Resource already exists",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            message=message,
            code="CONFLICT",
            status_code=status.HTTP_409_CONFLICT,
            details=details,
        )


class ValidationError(SabiTaxException):
    """Validation error exception."""

    def __init__(
        self,
        message: str = "Validation error",
        errors: list[dict[str, Any]] | None = None,
    ):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"errors": errors} if errors else {},
        )


class RateLimitError(SabiTaxException):
    """Rate limit exceeded exception."""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            message=message,
            code="RATE_LIMIT_EXCEEDED",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )


class ExternalServiceError(SabiTaxException):
    """External service error exception."""

    def __init__(
        self,
        message: str = "External service error",
        service: str | None = None,
    ):
        super().__init__(
            message=message,
            code="EXTERNAL_SERVICE_ERROR",
            status_code=status.HTTP_502_BAD_GATEWAY,
            details={"service": service} if service else {},
        )


async def sabitax_exception_handler(
    request: Request,
    exc: SabiTaxException,
) -> JSONResponse:
    """Handle SabiTax custom exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                **exc.details,
            }
        },
    )


async def http_exception_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    """Handle FastAPI HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "HTTP_ERROR",
                "message": exc.detail,
            }
        },
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Handle uncaught exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
            }
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers with the FastAPI app."""
    app.add_exception_handler(SabiTaxException, sabitax_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore[arg-type]
    # Uncomment for production to hide error details:
    # app.add_exception_handler(Exception, generic_exception_handler)
